# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import settings_sub
import os
from platinumegg.lib.forms import UploadFileForm
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.lib.movie import MovieUtil
from platinumegg.app.cabaret.models.Memories import MoviePlayList, PcMoviePlayList
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.media import Media
from StringIO import StringIO
from zipfile import ZipFile
from platinumegg.lib.pljson import Json
import settings_sub_props
import urllib


class Handler(AdminHandler):
    """動画の管理.
    アップロード.
        ファイル.
    一覧.
        名前.
        videoタグ表示.
    """
    def process(self):
        
        if self.request.method == 'POST':
            proc = self.request.get('_proc')
            
            table = {
                'upload' : self.__proc_upload,
                'listget' : self.__proc_listget,
                'package' : self.__proc_package,
                'packagepc' : self.__proc_package_pc,
                'update' : self.__proc_update,
                'updatepc' : self.__proc_update_pc,
            }
            f = table.get(proc)
            if f:
                f()
        if not self.response.isEnd:
            self.__proc_list()
    
    def __proc_list(self):
        """ファイル一覧.
        """
        dirpath = settings_sub.MEDIA_DOC_ROOT
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        
        model_mgr = self.getModelMgr()
        masterlist = BackendApi.get_movieplaylist_all(model_mgr, using=settings.DB_READONLY)
        masterdict = dict([(master.filename, master) for master in masterlist])
        pcmasterlist = BackendApi.get_pcmovieplaylist_all(model_mgr, using=settings.DB_READONLY)
        pcmasterdict = dict([(master.filename, master) for master in pcmasterlist])
        
        another_env_movies = {}
        another_env_pcmovies = {}
        downloadable = False
        if settings_sub.MEDIA_DOWNLOAD_FROM is not None:
            # 動画ダウンロード元.
            url = settings_sub.MEDIA_DOWNLOAD_FROM + 'cabaret/mgr' + UrlMaker.movie_edit()
            headers = {"Content-type": "application/x-www-form-urlencoded",}
            body = urllib.urlencode({'_proc':'listget'})
            jsonobj = {}
            response_data = None
            try:
                response = self.osa_util.httpopen(url, body, 'POST', headers)
                response_data = response.read()
                jsonobj = Json.decode(response_data)
                downloadable = True
            except:
                if response_data:
                    raise CabaretError(response_data)
                raise
            
            for data in jsonobj.get('result', {}).get('movielist', []):
                name = data['filename']
                if 'is_pc' in data and data['is_pc']:
                    another_env_pcmovies[name] = data
                else:
                    another_env_movies[name] = data
        
        def makeList(masterlist, masterdict, another_env_movies):
            movielist = []
            for master in masterlist:
                data = another_env_movies.get(master.filename)
                is_pc = isinstance(master, PcMoviePlayList)
                if is_pc:
                    thumbUrl = self.makeAppLinkUrlMedia(Media.movie_pc_thumbnail(master.filename))
                else:
                    thumbUrl = self.makeAppLinkUrlMedia(Media.movie_thumbnail(master.filename))
                movielist.append({
                    'id' : master.id,
                    'name' : master.name,
                    'filename' : master.filename,
                    'data' : getattr(master, 'data', ''),
                    'is_old' : data and (master.edittime < data['utime']),
                    'thumbUrl' : thumbUrl,
                    'is_pc' : is_pc,
                    'stgonly' : False,
                })
            
            for filename in list(set(another_env_movies.keys()) - set(masterdict.keys())):
                data = another_env_movies.get(filename)
                movielist.append({
                    'id' : data['id'],
                    'name' : data['name'],
                    'filename' : filename,
                    'data' : '',
                    'is_old' : True,
                    'thumbUrl' : data['thumbUrl'],
                    'is_pc' : data.get('is_pc'),
                    'stgonly' : True,
                })
            return movielist
        
        movielist = makeList(masterlist, masterdict, another_env_movies)
        movielist.extend(makeList(pcmasterlist, pcmasterdict, another_env_pcmovies))
        movielist.sort(key=lambda x: x['id'])
        
        self.html_param['downloadable'] = downloadable
        
        self.html_param['movielist'] = movielist
        
        self.html_param['uploadform'] = UploadFileForm()
        
        self.html_param['url_self'] = self.makeAppLinkUrlAdmin(UrlMaker.movie_edit())
        
        # HTML書き出し.
        self.writeAppHtml('movie')
    
    def __proc_upload_sp(self, basefilepath, filename, movname, outdir, mediaroot_dir):
        """ファイルをアップロード(SP).
        """
        tsfilename = u'stream.ts'
        segment_list_name = u'%s.m3u8' % movname
        flvfilename = u'stream.flv'
        
        # キャプチャ.
        sec = int(self.request.get('_sec') or 0)
        errlog = MovieUtil.make_capture_image(basefilepath, 'thumbnail.png', sec, 1, '140x80', workdir=outdir)
        if errlog:
            self.putAlertToHtmlParam(u'キャプチャの作成に失敗しました<br />Log:%s' % errlog, AlertCode.ERROR)
            return
        
        options = {
            '-s' : '320x180',
            '-aspect' : '16:9',
            '-vb' : '350k',
            '-ab' : '64k',
            '-ac' : '2',
            '-ar' : '44100',
            '-r' : '24',
            '-g' : '24',
            '-coder': '0',
            '-bf' : '0',
            '-qmin' : '10',
            '-vprofile' : 'baseline',
        }
        # mp4 -> flv.
        errlog = MovieUtil.to_flv(basefilepath, flvfilename, vcodec='libx264', acodec='aac -strict experimental', workdir=outdir, **options)
        if errlog:
            self.putAlertToHtmlParam(u'flvへのコンバートに失敗しました<br />Log:%s' % errlog, AlertCode.ERROR)
            return
        
        options = {
            '-s' : '320x180',
            '-aspect' : '16:9',
            '-vb' : '500k',
            '-ab' : '128k',
            '-ac' : '2',
            '-r' : '30',
            '-g' : '30',
            '-force_key_frames' : "00:00:10",
        }
        # mp4 -> mpeg2-ts.
        errlog = MovieUtil.to_mpeg2ts(basefilepath, tsfilename, vcodec='libx264', acodec='aac -strict experimental', workdir=outdir, **options)
        if errlog:
            self.putAlertToHtmlParam(u'mpeg2へのコンバートに失敗しました<br />Log:%s' % errlog, AlertCode.ERROR)
            return
        
        # プレイリスト作成.
        ts_inputname = '%s/%s' % (movname, tsfilename)
        ts_outputformat = '%s/%s.ts' % (movname, 'stream%04d')
        tscrypt_outputformat = '%s/%s.ts' % (movname, 'crstream%04d')
        options = {
            '-s' : '320x180',
            '-aspect' : '16:9',
            '-vcodec' : 'copy',
            '-acodec' : 'copy',
            '-ar' : '44100',
            '-qmin' : '10',
        }
        errlog = MovieUtil.segment(ts_inputname, segment_list_name, ts_outputformat, segment_format='mpegts', segment_list_type='m3u8', segment_time='10', workdir=mediaroot_dir, **options)
        if errlog:
            self.putAlertToHtmlParam(u'プレイリスト作成に失敗しました<br />Log:%s' % errlog, AlertCode.ERROR)
            return
        
        # 暗号化.
        hexkey = OSAUtil.makeRandomHexString(length=32)
        errlog = MovieUtil.crypt(hexkey, ts_outputformat, tscrypt_outputformat, flag_delete_inputfile=True, workdir=mediaroot_dir)
        if errlog:
            self.putAlertToHtmlParam(u'動画ファイルの暗号化に失敗しました<br />Log:%s' % errlog, AlertCode.ERROR)
            return
        
        # m3u8をロード.
        m3u8_file = None
        playlist_lines = None
        try:
            m3u8_file = open('%s/%s' % (mediaroot_dir, segment_list_name), 'r')
            playlist_lines = m3u8_file.readlines()
        finally:
            if m3u8_file:
                m3u8_file.close()
                m3u8_file = None
        if playlist_lines is None:
            self.putAlertToHtmlParam(u'プレイリストの登録に失敗しました', AlertCode.ERROR)
            return
        
        # プレイリストに鍵取得URLをつける.
        arr = []
        flag_url_add = False
        for line in playlist_lines:
            s = line.rstrip('\n').rstrip('\r')
            if not flag_url_add and line.startswith('#EXTINF'):
                diff = len(line) - len(s)
                postfix = ''
                if 0 < diff:
                    postfix = line[-diff:]
                url = self.makeAppLinkWebGrobalUrl(UrlMaker.movie_keyget('{masterid}'))
                arr.append('#EXT-X-KEY:METHOD=AES-128,URI="%s"%s' % (url, postfix))
                flag_url_add = True
            elif s[-3:] == '.ts':
                arr.append(line.replace('stream', 'crstream'))
                continue
            arr.append(line)
        playlist_data_format = ''.join(arr)
        
        # マスターデータに設定.
        name = self.request.get('_name') or movname
        m3u8_name = movname
        filepath = '%s/%s' % (mediaroot_dir, segment_list_name)
        model_mgr = db_util.run_in_transaction(Handler.tr_write, name, m3u8_name, filepath, playlist_data_format, hexkey)
        model_mgr.write_end()
        
        # とり直しておく.
        model_mgr.get_mastermodel_all(MoviePlayList, fetch_deleted=True, using=settings.DB_DEFAULT, reflesh=True)
        
        self.putAlertToHtmlParam(u'アップロード完了:元ファイル=%s, プレイリスト=%s' % (filename, movname), AlertCode.SUCCESS)
    
    def __proc_upload_pc(self, basefilepath, filename, movname, outdir, mediaroot_dir):
        """ファイルをアップロード(PC).
        """
        # キャプチャ.
        sec = int(self.request.get('_sec') or 0)
        errlog = MovieUtil.make_capture_image(basefilepath, 'pcthumbnail.png', sec, 1, '140x80', workdir=outdir)
        if errlog:
            self.putAlertToHtmlParam(u'キャプチャの作成に失敗しました<br />Log:%s' % errlog, AlertCode.ERROR)
            return
        
        mp4filename = u'%s.mp4' % movname
        options = {
            '-s' : '640x480',
            '-aspect' : '16:9',
            '-vb' : '500k',
            '-ab' : '128k',
            '-ac' : '2',
            '-ar' : '48k',
            '-r' : '30',
            '-g' : '30',
            '-qmin' : '10',
            '-vprofile' : 'main',
        }
        # mp4 -> mp4.
        errlog = MovieUtil.to_mp4(basefilepath, mp4filename, vcodec='libx264', acodec='aac -strict experimental', workdir=mediaroot_dir, **options)
        if errlog:
            self.putAlertToHtmlParam(u'mp4へのコンバートに失敗しました<br />Log:%s' % errlog, AlertCode.ERROR)
            return
        
        # 他のサーバに配布.
        
        # マスターデータに設定.
        name = self.request.get('_name') or movname
        filepath = '%s/%s' % (mediaroot_dir, mp4filename)
        weblist = self.getMediaWebList()
        model_mgr = db_util.run_in_transaction(Handler.tr_write_pc, name, movname, filepath, weblist)
        model_mgr.write_end()
        
        # とり直しておく.
        model_mgr.get_mastermodel_all(PcMoviePlayList, fetch_deleted=True, using=settings.DB_DEFAULT, reflesh=True)
        
        self.putAlertToHtmlParam(u'アップロード完了:元ファイル=%s, プレイリスト=%s' % (filename, movname), AlertCode.SUCCESS)
    
    def __proc_upload(self):
        """ファイルをアップロード.
        """
        request_files = self.request.files
        form = UploadFileForm(self.request.body, request_files)
        fixture = None
        if form.is_valid():
            fixture = request_files['data_file']
        
        if not fixture:
            self.putAlertToHtmlParam(u'動画が選択されていません', AlertCode.ERROR)
            return
        
        # 元のファイル.
        basefilepath = fixture.temporary_file_path()
        filename = fixture.name
        
        # 拡張子をチェック.
        movname, ext = os.path.splitext(filename)
        if ext != '.mp4':
            self.putAlertToHtmlParam(u'非対応の動画形式です. %s' % ext, AlertCode.ERROR)
            return
        
        movname = movname.replace('.', '_').replace('-', '')
        mediaroot_dir = settings_sub.MEDIA_DOC_ROOT
        outdir = '%s/%s' % (mediaroot_dir, movname)
        
        # 保存先のディレクトリを作成.
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        
        if int(self.request.get('_platform') or 0) == 0:
            # SP
            self.__proc_upload_sp(basefilepath, filename, movname, outdir, mediaroot_dir)
        else:
            # PC
            self.__proc_upload_pc(basefilepath, filename, movname, outdir, mediaroot_dir)
    
    def __proc_listget(self):
        """動画一覧.
        """
        dirpath = settings_sub.MEDIA_DOC_ROOT
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        
        model_mgr = self.getModelMgr()
        masterlist = BackendApi.get_movieplaylist_all(model_mgr, using=settings.DB_READONLY)
        pcmasterlist = BackendApi.get_pcmovieplaylist_all(model_mgr, using=settings.DB_READONLY)
        
        movielist = []
        for master in masterlist:
            thumbUrl = self.makeAppLinkUrlMedia(Media.movie_thumbnail(master.filename))
            movielist.append({
                'id' : master.id,
                'name' : master.name,
                'filename' : master.filename,
                'thumbUrl' : thumbUrl,
                'utime' : master.edittime,
                'is_pc' : False,
            })
        for master in pcmasterlist:
            thumbUrl = self.makeAppLinkUrlMedia(Media.movie_pc_thumbnail(master.filename))
            movielist.append({
                'id' : master.id,
                'name' : master.name,
                'filename' : master.filename,
                'thumbUrl' : thumbUrl,
                'utime' : master.edittime,
                'is_pc' : True,
            })
        self.json_result_param['movielist'] = movielist
        self.writeAppJson()
    
    def __proc_package(self):
        """動画パッケージ.
        """
        zf = None
        zipdata = None
        try:
            name = self.request.get('_name')
            master = MoviePlayList.getValues(filters={'filename':name})
            
            io = StringIO()
            zf = ZipFile(io, 'w')
            
            # マスターデータ.
            dic = {}
            columnnames = MoviePlayList.get_column_names()
            for columnname in columnnames:
                dic[columnname] = getattr(master, columnname)
            zf.writestr('master.json', Json.encode(dic))
            
            def getData(filepath):
                f = None
                try:
                    f = open(filepath, 'r')
                    data = f.read()
                    f.close()
                    f = None
                except:
                    if f:
                        f.close()
                        f = None
                    raise
                return data
            
            # 動画ファイル.
            dirpath = os.path.join(settings_sub.MEDIA_DOC_ROOT, master.filename)
            for name in os.listdir(dirpath):
                filepath = os.path.join(dirpath, name)
                data = getData(filepath)
                zf.writestr(name, data)
            
            filename = Media.movie_m3u8(master.filename)
            zf.writestr(filename, getData(os.path.join(settings_sub.MEDIA_DOC_ROOT, filename)))
            
            err = zf.testzip()
            if err:
                raise CabaretError(err)
            
            zf.close()
            
            io.seek(0)
            zipdata = io.read()
            
            zf = None
        except:
            if zf:
                zf.close()
                zf = None
            if settings_sub.IS_LOCAL:
                raise
            self.response.set_status(500)
            self.response.end()
            return
        
        f = open(os.path.join(settings_sub.TMP_DOC_ROOT, 'abc.zip'), 'w')
        f.write(zipdata)
        f.close()
        
        if zipdata:
            self.osa_util.write_zip(zipdata, 'movie')
        else:
            self.response.set_status(404)
            self.response.end()
            return
    
    def __proc_package_pc(self):
        """動画パッケージ(PC).
        """
        zf = None
        zipdata = None
        try:
            name = self.request.get('_name')
            master = PcMoviePlayList.getValues(filters={'filename':name})
            
            io = StringIO()
            zf = ZipFile(io, 'w')
            
            # マスターデータ.
            dic = {}
            columnnames = PcMoviePlayList.get_column_names()
            for columnname in columnnames:
                dic[columnname] = getattr(master, columnname)
            zf.writestr('master.json', Json.encode(dic))
            
            def getData(filepath):
                f = None
                try:
                    f = open(filepath, 'r')
                    data = f.read()
                    f.close()
                    f = None
                except:
                    if f:
                        f.close()
                        f = None
                    raise
                return data
            
            # サムネイル画像.
            dirpath = settings_sub.MEDIA_DOC_ROOT
            name = Media.movie_pc_thumbnail(master.filename)
            filepath = os.path.join(dirpath, name)
            data = getData(filepath)
            zf.writestr(name, data)
            
            # 動画ファイル.
            filename = Media.movie_mp4(master.filename)
            zf.writestr(filename, getData(os.path.join(settings_sub.MEDIA_DOC_ROOT, filename)))
            
            err = zf.testzip()
            if err:
                raise CabaretError(err)
            
            zf.close()
            
            io.seek(0)
            zipdata = io.read()
            
            zf = None
        except:
            if zf:
                zf.close()
                zf = None
            if settings_sub.IS_LOCAL:
                raise
            self.response.set_status(500)
            raise
        
        f = open(os.path.join(settings_sub.TMP_DOC_ROOT, 'abc.zip'), 'w')
        f.write(zipdata)
        f.close()
        
        if zipdata:
            self.osa_util.write_zip(zipdata, 'movie')
        else:
            self.response.set_status(404)
            self.response.end()
            return
    
    def __proc_update(self):
        """動画更新.
        本番環境のみ.
        ステージングから指定した動画を受け取って各メディアサーバに配付する.
        """
        if not settings_sub.IS_LOCAL and settings_sub_props.ENVIRONMENT_TYPE != settings_sub_props.EnvironmentType.MANAGER:
            self.response.set_status(404)
            return
        zf = None
        try:
            # ダウンロードするマスターデータ.
            try:
                filename = self.request.get('_name')
            except:
                self.response.set_status(400)
                return
            
            # ダウンロード元.
            url = settings_sub.MEDIA_DOWNLOAD_FROM + 'cabaret/mgr/movie/'
            headers = {"Content-type": "application/x-www-form-urlencoded",}
            body = urllib.urlencode({
                '_name' : filename,
                '_proc' : 'package',
            })
            
            try:
                response = self.osa_util.httpopen(url, body, 'POST', headers)
                data = response.read()
            except:
                raise
            
            def writeFile(filepath, data):
                f = None
                try:
                    f = open(filepath, 'w')
                    f.write(data)
                    f.close()
                    f = None
                except:
                    if f:
                        f.close()
                        f = None
                    raise
            
            io = StringIO(data)
            zf = ZipFile(io, 'r')
            
            # 動画ファイル.
            namelist = zf.namelist()[:]
            
            # マスターデータ.
            jsonfile = zf.open('master.json')
            obj_master = Json.decode(jsonfile.read())
            namelist.remove('master.json')
            
            master = MoviePlayList.getValues(filters={'filename':filename})
            if master:
                obj_master['id'] = master.id
            mid = obj_master['id']
            
            # プレイリスト.
            m3u8filename = Media.movie_m3u8(filename)
            m3u8file = zf.open(m3u8filename)
            m3u8lines = []
            for line in m3u8file.readlines():
                s = line.rstrip('\n').rstrip('\r')
                if line.startswith('#EXT-X-KEY:METHOD=AES-128'):
                    diff = len(line) - len(s)
                    postfix = ''
                    if 0 < diff:
                        postfix = line[-diff:]
                    url = self.makeAppLinkWebGrobalUrl(UrlMaker.movie_keyget(mid))
                    line = '#EXT-X-KEY:METHOD=AES-128,URI="%s"%s' % (url, postfix)
                m3u8lines.append(line)
            m3u8data = ''.join(m3u8lines)
            writeFile(os.path.join(settings_sub.MEDIA_DOC_ROOT, m3u8filename), m3u8data)
            namelist.remove(m3u8filename)
            
            # その他動画ファイル.
            dirpath = os.path.join(settings_sub.MEDIA_DOC_ROOT, filename)
            if not os.path.exists(dirpath):
                os.mkdir(dirpath)
            
            for name in namelist:
                outname = name
                if name == 'stream.ts':
                    if settings_sub.IS_LOCAL:
                        outname = filename + name
                    else:
                        continue
                filepath = os.path.join(dirpath, outname)
                data = zf.open(name).read()
                writeFile(filepath, data)
            zf.close()
            zf = None
            
            # マスターデータ書き込み.
            # 上書き.
            def tr(data):
                model_mgr = ModelRequestMgr()
                
                def forUpdate(model, inserted):
                    for k,v in data.items():
                        setattr(model, k, v)
                model_mgr.add_forupdate_task(MoviePlayList, mid, forUpdate)
                model_mgr.write_all()
                return model_mgr
            tmp = db_util.run_in_transaction(tr, obj_master)
            tmp.write_end()
            
            # 配布.
            weblist = self.getMediaWebList()
            if weblist:
                errlog = MovieUtil.distribute(filename, weblist, settings_sub.SERVER_PASS)
                if errlog:
                    raise CabaretError(errlog)
            
            # とり直しておく.
            model_mgr = self.getModelMgr()
            model_mgr.get_mastermodel_all(MoviePlayList, fetch_deleted=True, using=settings.DB_DEFAULT, reflesh=True)
        except:
            if zf:
                zf.close()
                zf = None
            raise
        
        self.putAlertToHtmlParam(u'動画を更新しました:name=%s' % filename, AlertCode.SUCCESS)
    
    def __proc_update_pc(self):
        """動画更新(PC).
        本番環境のみ.
        ステージングから指定した動画を受け取って本番Wowzaサーバに配付する.
        サムネイル画像は各メディアサーバに配付する.
        """
        if not settings_sub.IS_LOCAL and settings_sub_props.ENVIRONMENT_TYPE != settings_sub_props.EnvironmentType.MANAGER:
            self.response.set_status(404)
            return
        zf = None
        try:
            # ダウンロードするマスターデータ.
            try:
                filename = self.request.get('_name')
            except:
                self.response.set_status(400)
                return
            
            # ダウンロード元.
            url = settings_sub.MEDIA_DOWNLOAD_FROM + 'cabaret/mgr/movie/'
            headers = {"Content-type": "application/x-www-form-urlencoded",}
            body = urllib.urlencode({
                '_name' : filename,
                '_proc' : 'packagepc',
            })
            
            try:
                response = self.osa_util.httpopen(url, body, 'POST', headers)
                data = response.read()
            except:
                raise
            
            def writeFile(filepath, data):
                f = None
                try:
                    f = open(filepath, 'w')
                    f.write(data)
                    f.close()
                    f = None
                except:
                    if f:
                        f.close()
                        f = None
                    raise
            
            io = StringIO(data)
            zf = ZipFile(io, 'r')
            
            # 動画ファイル.
            namelist = zf.namelist()[:]
            
            # マスターデータ.
            jsonfile = zf.open('master.json')
            obj_master = Json.decode(jsonfile.read())
            namelist.remove('master.json')
            
            master = PcMoviePlayList.getValues(filters={'filename':filename})
            if master:
                obj_master['id'] = master.id
            mid = obj_master['id']
            
            mediadir = os.path.join(settings_sub.MEDIA_DOC_ROOT, filename)
            if not os.path.exists(mediadir):
                os.mkdir(mediadir)
            
            # 動画ファイル.
            mp4filename = Media.movie_mp4(filename)
            mp4data = zf.open(mp4filename).read()
            filepath = os.path.join(settings_sub.MEDIA_DOC_ROOT, mp4filename)
            writeFile(filepath, mp4data)
            namelist.remove(mp4filename)
            
            # サムネイル画像.
            dirpath = settings_sub.MEDIA_DOC_ROOT
            if not os.path.exists(dirpath):
                os.mkdir(dirpath)
            
            name = Media.movie_pc_thumbnail(filename)
            filepath = os.path.join(dirpath, name)
            data = zf.open(name).read()
            writeFile(filepath, data)
            zf.close()
            zf = None
            
            # マスターデータ書き込み.
            # 上書き.
            def tr(data):
                model_mgr = ModelRequestMgr()
                
                def forUpdate(model, inserted):
                    for k,v in data.items():
                        setattr(model, k, v)
                model_mgr.add_forupdate_task(PcMoviePlayList, mid, forUpdate)
                model_mgr.write_all()
                return model_mgr
            tmp = db_util.run_in_transaction(tr, obj_master)
            tmp.write_end()
            
            # 配布.
            weblist = self.getMediaWebList()
            if weblist:
                # TODO
                errlog = MovieUtil.distribute_pc(filename, weblist, settings_sub.SERVER_PASS)
                if errlog:
                    raise CabaretError(errlog)
            
            # 本番環境ではステージングと同じ動画を見るので配付する必要がない.
            if settings_sub.IS_DEV:
                errlog = MovieUtil.distribute_wowza(filename)
                if errlog:
                    raise CabaretError(errlog)
            
            # とり直しておく.
            model_mgr = self.getModelMgr()
            model_mgr.get_mastermodel_all(PcMoviePlayList, fetch_deleted=True, using=settings.DB_DEFAULT, reflesh=True)
        except:
            if zf:
                zf.close()
                zf = None
            raise
        
        self.putAlertToHtmlParam(u'動画を更新しました:name=%s' % filename, AlertCode.SUCCESS)
    
    @staticmethod
    def tr_write(name, m3u8_name, filepath, playlist_data_format, hexkey, edittime=None):
        """マスターデータ書き込み.
        """
        model_mgr = ModelRequestMgr()
        exists_masterdata = MoviePlayList.getValues(['id'], filters={'filename':m3u8_name})
        if exists_masterdata:
            master = MoviePlayList.getByKeyForUpdate(exists_masterdata.id)
        else:
            master = MoviePlayList()
            master.filename = m3u8_name
        
        master.name = name
        master.data = hexkey
        master.edittime = edittime or OSAUtil.get_now()
        model_mgr.set_save(master)
        
        model_mgr.write_all()
        
        # m3u8を上書き.
        playlist_data = playlist_data_format.format(masterid=master.id)
        f = None
        try:
            f = open(filepath, 'w')
            f.write(playlist_data)
            f.close()
            f = None
        except:
            if f:
                f.close()
            raise
        
        if settings_sub_props.ENVIRONMENT_TYPE != settings_sub_props.EnvironmentType.MANAGER:
            weblist = Handler.getMediaWebList()
            if weblist:
                errlog = MovieUtil.distribute(master.filename, weblist, settings_sub.SERVER_PASS)
                if errlog:
                    raise CabaretError(errlog)
        
        return model_mgr
    
    @staticmethod
    def tr_write_pc(name, mp4_name, filepath, weblist, edittime=None):
        """マスターデータ書き込み（PC用）.
        """
        model_mgr = ModelRequestMgr()
        exists_masterdata = PcMoviePlayList.getValues(['id'], filters = {'filename':mp4_name})
        if exists_masterdata:
            master = PcMoviePlayList.getByKeyForUpdate(exists_masterdata.id)
        else:
            master = PcMoviePlayList()
            master.filename = mp4_name
        
        master.name = name
        master.edittime = edittime or OSAUtil.get_now()
        model_mgr.set_save(master)
        
        model_mgr.write_all()
        
        if settings_sub_props.ENVIRONMENT_TYPE != settings_sub_props.EnvironmentType.MANAGER:
            errlog = MovieUtil.distribute_wowza(master.filename)
            if errlog:
                raise CabaretError(errlog)
            if weblist:
                errlog = MovieUtil.distribute_pc(master.filename, weblist, settings_sub.SERVER_PASS)
                if errlog:
                    raise CabaretError(errlog)
        
        return model_mgr
    
    def makeAppLinkWebGrobalUrl(self, url):
        # httpsの方がいいかも.
        if settings_sub.IS_LOCAL:
            url_cgi = 'http://%s/sp' % settings_sub.MEDIA_GLOBAL_HOST
        else:
            url_cgi = 'http://%s/%s/sp' % (settings_sub.MEDIA_GLOBAL_HOST, settings_sub.APP_NAME)
        return OSAUtil.addQuery(url_cgi + url, OSAUtil.KEY_APP_ID, self.osa_util.appparam.app_id)
    
    @staticmethod
    def getMediaWebList():
        """配付するメディアサーバ一覧
        """
        if settings_sub.MEDIA_WEBLIST_FILE is None or not os.path.exists(settings_sub.MEDIA_WEBLIST_FILE):
            return None
        
        f = None
        try:
            f = open(settings_sub.MEDIA_WEBLIST_FILE)
            weblist = f.readlines()
            f.close()
            f = None
        except:
            if f:
                f.close()
            raise
        arr = []
        for web in weblist:
            s = web.rstrip('\n').rstrip('\r')
            if s:
                arr.append(s)
        return arr
    
def main(request):
    return Handler.run(request)
