# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import settings_sub
import os
from platinumegg.lib.forms import UploadFileForm
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.lib.movie import MovieUtil
from platinumegg.app.cabaret.models.Memories import VoicePlayList
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
    """音声の管理.
    アップロード.
        ファイル.
    一覧.
        名前.
        voiceタグ表示.
    """
    def process(self):
        
        if self.request.method == 'POST':
            proc = self.request.get('_proc')
            
            table = {
                'upload' : self.__proc_upload,
                'listget' : self.__proc_listget,
                'package' : self.__proc_package,
                'update' : self.__proc_update,
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
        masterlist = BackendApi.get_voiceplaylist_all(model_mgr, using=settings.DB_READONLY)
        masterdict = dict([(master.filename, master) for master in masterlist])
        
        another_env_voices = {}
        downloadable = False
        if settings_sub.MEDIA_DOWNLOAD_FROM is not None:
            # 音声ダウンロード元.
            url = settings_sub.MEDIA_DOWNLOAD_FROM + 'cabaret/mgr' + UrlMaker.voice_edit()
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
            
            for data in jsonobj.get('result', {}).get('voicelist', []):
                name = data['filename']
                another_env_voices[name] = data
        
        voicelist = []
        for master in masterlist:
            data = another_env_voices.get(master.filename)
            voicelist.append({
                'type' : type,
                'id' : master.id,
                'name' : master.name,
                'filename' : master.filename,
                'is_old' : data and (master.edittime < data['utime']),
                'stgonly' : False,
            })
        for filename in list(set(another_env_voices.keys()) - set(masterdict.keys())):
            data = another_env_voices[filename]
            voicelist.append({
                'type' : data['type'],
                'id' : data['id'],
                'name' : data['name'],
                'filename' : filename,
                'is_old' : True,
                'stgonly' : True,
            })
        voicelist.sort(key=lambda x: x['id'])
        
        self.html_param['downloadable'] = downloadable
        
        self.html_param['voicelist'] = voicelist
        
        self.html_param['uploadform'] = UploadFileForm()
        
        self.html_param['url_self'] = self.makeAppLinkUrlAdmin(UrlMaker.voice_edit())
        
        # HTML書き出し.
        self.writeAppHtml('voice')
    
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
        outdir = '%s/voice/%s' % (mediaroot_dir, movname)
        
        # 保存先のディレクトリを作成.
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        
        filenameaac = u'voice.m4a'
        filenameogg = u'voice.ogg'
        
        options = {
            '-ac' : '2',
            '-ab' : '64k',
            '-ar' : '44100',
        }
        # mp4 -> aac.
        errlog = MovieUtil.to_aac(basefilepath, filenameaac, acodec='aac -strict experimental', workdir=outdir, **options)
        if errlog:
            self.putAlertToHtmlParam(u'aacへのコンバートに失敗しました<br />Log:%s' % errlog, AlertCode.ERROR)
            return
        
        options = {
            '-ac' : '2',
            '-ab' : '64k',
            '-ar' : '44100',
        }
        # mp4 -> ogg.
        errlog = MovieUtil.to_ogg(basefilepath, filenameogg, acodec='libvorbis', workdir=outdir, **options)
        if errlog:
            self.putAlertToHtmlParam(u'oggへのコンバートに失敗しました<br />Log:%s' % errlog, AlertCode.ERROR)
            return
        
        # マスターデータに設定.
        name = self.request.get('_name') or movname
        m3u8_name = movname
        model_mgr = db_util.run_in_transaction(Handler.tr_write, name, m3u8_name)
        model_mgr.write_end()
        
        # とり直しておく.
        model_mgr.get_mastermodel_all(VoicePlayList, fetch_deleted=True, using=settings.DB_DEFAULT, reflesh=True)
        
        self.putAlertToHtmlParam(u'アップロード完了:元ファイル=%s, プレイリスト=%s' % (filename, movname), AlertCode.SUCCESS)
    
    def __proc_listget(self):
        """動画一覧.
        """
        dirpath = settings_sub.MEDIA_DOC_ROOT
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        dirpath = os.path.join(dirpath, 'voice')
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        
        model_mgr = self.getModelMgr()
        masterlist = BackendApi.get_voiceplaylist_all(model_mgr, using=settings.DB_READONLY)
        
        voicelist = []
        for master in masterlist:
            voicelist.append({
                'id' : master.id,
                'name' : master.name,
                'filename' : master.filename,
                'utime' : master.edittime,
            })
        self.json_result_param['voicelist'] = voicelist
        self.writeAppJson()
    
    def __proc_package(self):
        """動画パッケージ.
        """
        zf = None
        zipdata = None
        try:
            name = self.request.get('_name')
            master = VoicePlayList.getValues(filters={'filename':name})
            
            io = StringIO()
            zf = ZipFile(io, 'w')
            
            # マスターデータ.
            dic = {}
            columnnames = VoicePlayList.get_column_names()
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
            self.osa_util.write_zip(zipdata, 'voice')
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
            url = settings_sub.MEDIA_DOWNLOAD_FROM + 'cabaret/mgr/voice/'
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
            
            master = VoicePlayList.getValues(filters={'filename':filename})
            if master:
                obj_master['id'] = master.id
            mid = obj_master['id']
            
            # その他動画ファイル.
            dirpath = os.path.join(settings_sub.MEDIA_DOC_ROOT, filename)
            if not os.path.exists(dirpath):
                os.mkdir(dirpath)
            
            for name in namelist:
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
                model_mgr.add_forupdate_task(VoicePlayList, mid, forUpdate)
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
            model_mgr.get_mastermodel_all(VoicePlayList, fetch_deleted=True, using=settings.DB_DEFAULT, reflesh=True)
        except:
            if zf:
                zf.close()
                zf = None
            raise
        
        self.putAlertToHtmlParam(u'動画を更新しました:name=%s' % filename, AlertCode.SUCCESS)
    
    @staticmethod
    def tr_write(name, m3u8_name, edittime=None):
        """マスターデータ書き込み.
        """
        model_mgr = ModelRequestMgr()
        exists_masterdata = VoicePlayList.getValues(['id'], filters = {'filename':m3u8_name})
        if exists_masterdata:
            master = VoicePlayList.getByKeyForUpdate(exists_masterdata.id)
        else:
            master = VoicePlayList()
            master.filename = m3u8_name
        
        master.name = name
        master.data = ''
        master.edittime = edittime or OSAUtil.get_now()
        model_mgr.set_save(master)
        
        model_mgr.write_all()
        
        if settings_sub_props.ENVIRONMENT_TYPE != settings_sub_props.EnvironmentType.MANAGER:
            weblist = Handler.getMediaWebList()
            if weblist:
                errlog = MovieUtil.distribute(master.filename, weblist, settings_sub.SERVER_PASS)
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
