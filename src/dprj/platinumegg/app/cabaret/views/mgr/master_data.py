# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import settings_sub
import os
from zipfile import ZipFile, BadZipfile
from platinumegg.app.cabaret.util.master_data import MasterData
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from StringIO import StringIO
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.forms import UploadFileForm
from platinumegg.lib.pljson import Json
import urllib
import datetime

class Handler(AdminHandler):
    """マスターデータ.
    ステージング
        マスターデータのスナップショットを幾つか保存
            マスターデータのJson.
            作成時間.
            ファイル名
                master_%06d.zip
            削除ボタン
        マスターデータ一覧表示
        保存ボタン
    本番
        ステージングのマスターデータ一覧表示
            更新ボタン
        最新版のzipはローカルにおいておく.
        現在のファイルを表示
    """
    
    def process(self):
        if settings_sub.IS_LOCAL:
#             self.__proc_dev()
            self.__proc_release()
        elif settings_sub.IS_DEV:
            self.__proc_dev()
        else:
            self.__proc_release()
    
    def __proc_dev(self):
        """開発・ステージング環境.
        """
        args = self.getUrlArgs('/master_data/')
        proc = args.get(0)
        table = {
            'package' : self.__proc_package,
            'delete' : self.__proc_delete,
            'save' : self.__proc_save,
            'download' : self.__proc_download,
            'upload' : self.__proc_upload,
            'listget' : self.__proc_listget,
        }
        f = table.get(proc)
        if f:
            f()
            if self.response.isEnd:
                return
        
        filenamelist = self.getZipFileNameList()
        
        arr = []
        
        url_download_base = UrlMaker.master_data('package')
        url_delete_base = UrlMaker.master_data('delete')
        for filename in filenamelist:
            str_ctime = self.zipfile(filename, lambda zf : zf.open('createtime.txt').read())
            arr.append({
                'name' : filename,
                'ctime' : str_ctime,
                'url_delete' : self.makeAppLinkUrlAdmin(OSAUtil.addQuery(url_delete_base, '_name', filename)),
                'url_download' : self.makeAppLinkUrlAdmin(OSAUtil.addQuery(url_download_base, '_name', filename)),
            })
        self.html_param['zipfilelist'] = arr
        
        self.html_param['form'] = UploadFileForm()
        self.html_param['url_save'] = self.makeAppLinkUrlAdmin(UrlMaker.master_data('save'))
        self.html_param['url_download'] = self.makeAppLinkUrlAdmin(UrlMaker.master_data('download'))
        self.html_param['url_upload'] = self.makeAppLinkUrlAdmin(UrlMaker.master_data('upload'))
        
        self.writeAppHtml('masterdata/dev')
    
    def __proc_release(self):
        """本番環境.
        """
        args = self.getUrlArgs('/master_data/')
        proc = args.get(0)
        table = {
            'package' : self.__proc_package,
            'download' : self.__proc_download,
            'update' : self.__proc_update,
        }
        f = table.get(proc)
        if f:
            f()
            if self.response.isEnd:
                return
        
        url = settings_sub.MASTER_DOWNLOAD_FROM + 'cabaret/mgr' + UrlMaker.master_data('listget')
        jsonobj = {}
        try:
            response = self.osa_util.httpopen(url, None, 'GET', {})
            jsonobj = Json.decode(response.read())
        except:
            raise
        
        # 現在のマスターデータ.
        def callback(zf):
            data = None
            if zf:
                filenamepath = os.path.join(self.getDirectoryPath(), 'stg_filename.txt')
                if os.path.exists(filenamepath):
                    try:
                        f = open(filenamepath)
                        name = f.read()
                        f.close()
                    except:
                        if f:
                            f.close()
                        raise
                else:
                    name = u'不明'
                data = {
                    'name' : name,
                    'ctime' : zf.open('createtime.txt').read(),
                    'url_download' : self.makeAppLinkUrlAdmin(OSAUtil.addQuery(UrlMaker.master_data('package'), '_name', 'current_master.zip')),
                }
            return data
        self.html_param['cur_zipfile'] = self.zipfile('current_master.zip', callback)
        
        ziplist = jsonobj.get('result', {}).get('zipfilelist', [])
        arr = []
        for zipfile_obj in ziplist:
            name = zipfile_obj['name']
            ctime = zipfile_obj['ctime']
            arr.append({
                'name' : name,
                'ctime' : ctime,
            })
        
        self.html_param['zipfilelist'] = arr
        
        self.html_param['url_update'] = self.makeAppLinkUrlAdmin(UrlMaker.master_data('update'))
        self.html_param['url_download'] = self.makeAppLinkUrlAdmin(UrlMaker.master_data('download'))
        
        self.writeAppHtml('masterdata/release')
    
    def __proc_download(self):
        """マスターデータダウンロード.
        """
        jsonstr = MasterData.to_json()
        now = OSAUtil.get_now()
        self.osa_util.write_json_data(jsonstr, 'masterdata_%s.json' % now.strftime("%Y%m%d%H%M%S"))
    
    def __proc_upload(self):
        """マスターデータアップロード.
        """
        request_files = self.request.files
        form = UploadFileForm(self.request.body, request_files)
        if not form.is_valid():
            self.putAlertToHtmlParam(u'うまく受け取れませんでした', alert_code=AlertCode.ERROR)
            return
        
        jsonstr = request_files['data_file'].read()
        MasterData.update_from_json(jsonstr)
        
        self.putAlertToHtmlParam(u'マスターデータをアップロードしました')
    
    def __proc_save(self):
        """マスターデータを保存.
        """
        
        # マスターの番号を更新.
        def tr():
            model_mgr = ModelRequestMgr()
            appconfig = BackendApi.get_appconfig(model_mgr, using=settings.DB_DEFAULT)
            appconfig.master += 1
            model_mgr.set_save(appconfig)
            model_mgr.write_all()
            return model_mgr, appconfig
        model_mgr, appconfig = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        
        dirpath = self.getDirectoryPath()
        filename = self.makeZipFileName(appconfig.master)
        filepath = os.path.join(dirpath, filename)
        
        io = StringIO()
        zf = ZipFile(io, 'w')
        
        # マスターデータ.
        jsondata = MasterData.to_json()
        zf.writestr('master.json', jsondata)
        
        # 現在時刻.
        now = datetime.datetime.now()
        str_now = now.strftime('%Y/%m/%d %H:%M:%S')
        zf.writestr('createtime.txt', str_now)
        
        zf.close()
        io.seek(0)
        zipdata = io.read()
        
        f = None
        try:
            f = open(filepath, 'w')
            f.write(zipdata)
            f.close()
        except:
            if f:
                f.close()
            raise
        
        self.putAlertToHtmlParam(u'マスターデータを保存しました.file=%s' % filepath, AlertCode.SUCCESS)
    
    def __proc_delete(self):
        """マスターデータを削除.
        """
        filename = self.request.get('_name')
        dirpath = self.getDirectoryPath()
        filepath = os.path.join(dirpath, filename)
        if not os.path.exists(filepath):
            self.putAlertToHtmlParam(u'マスターデータが見つかりませんでした.file=%s' % filepath, AlertCode.ERROR)
            return
        
        try:
            os.remove(filepath)
        except:
            self.putAlertToHtmlParam(u'マスターデータｗｐ削除できませんでした.file=%s' % filepath, AlertCode.ERROR)
            return
        
        self.putAlertToHtmlParam(u'マスターデータを削除しました.file=%s' % filepath, AlertCode.SUCCESS)
    
    def __proc_listget(self):
        """ファイル一覧を取得.
        """
        filenamelist = self.getZipFileNameList()
        
        arr = []
        
        for filename in filenamelist:
            str_ctime = self.zipfile(filename, lambda zf : zf.open('createtime.txt').read())
            arr.append({
                'name' : filename,
                'ctime' : str_ctime,
            })
        self.json_result_param['zipfilelist'] = arr
        
        self.writeAppJson()
    
    def __proc_package(self):
        """ファイルを取得.
        """
        filename = self.request.get('_name')
        dirpath = self.getDirectoryPath()
        filepath = os.path.join(dirpath, filename)
        if not os.path.exists(filepath):
            self.response.set_status(404)
            self.response.end()
            return
        
        f = None
        try:
            f = open(filepath, 'r')
            data = f.read()
            f.close()
        except:
            if f:
                f.close()
            self.response.set_status(500)
            self.response.end()
            return
        
        self.osa_util.write_zip(data, filename[:-4])
    
    def __proc_update(self):
        """マスターデータを落として更新.
        """
        filename = self.request.get('_name')
        
        url = settings_sub.MASTER_DOWNLOAD_FROM + 'cabaret/mgr' + UrlMaker.master_data('package')
        headers = {"Content-type": "application/x-www-form-urlencoded",}
        body = urllib.urlencode({'_name': filename})
        try:
            response = self.osa_util.httpopen(url, body, 'POST', headers)
            data = response.read()
        except:
            raise
        
        datadict = {}
        io = StringIO(data)
        zf = ZipFile(io, 'r')
        for name in zf.namelist():
            datadict[name] = zf.open(name).read()
        zf.close()
        
        filepath = os.path.join(self.getDirectoryPath(), 'current_master.zip')
        filenamepath = os.path.join(self.getDirectoryPath(), 'stg_filename.txt')
        
        zipdata = data
        
        jsonstr = datadict['master.json']
        MasterData.update_from_json(jsonstr)
        
        f = None
        try:
            f = open(filepath, 'w')
            f.write(zipdata)
            f.close()
            
            f = open(filenamepath, 'w')
            f.write(filename)
            f.close()
        except:
            if f:
                f.close()
            self.putAlertToHtmlParam(u'マスターデータを更新しましたが、zipファイルの保存に失敗しました.file=%s' % filepath, AlertCode.WARNING)
            return
        
        self.putAlertToHtmlParam(u'マスターデータを更新しました.', AlertCode.SUCCESS)
    
    def getZipFileNameList(self):
        """ファイル名一覧.
        """
        dirpath = self.getDirectoryPath()
        filenamelist = [name for name in os.listdir(dirpath) if name[-4:] == '.zip']
        filenamelist.sort(reverse=True)
        return filenamelist
    
    def zipfile(self, filename, work):
        """zipファイル.
        """
        dirpath = self.getDirectoryPath()
        filepath = os.path.join(dirpath, filename)
        if not os.path.exists(filepath):
            return work(None)
        
        zf = None
        response = None
        try:
            zf = ZipFile(filepath, 'r')
            response = work(zf)
            zf.close()
            zf = None
        except BadZipfile:
            zf = None
        except:
            if zf:
                zf.close()
                zf = None
            raise
        return response
    
    def getDirectoryPath(self):
        if not os.path.exists(settings_sub.TMP_DOC_ROOT):
            os.mkdir(settings_sub.TMP_DOC_ROOT)
        
        dirpath = os.path.join(settings_sub.TMP_DOC_ROOT, 'masterdata')
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        return dirpath
    
    def makeZipFileName(self, number, ext=True):
        if ext:
            return 'master_%08d.zip' % number
        else:
            return 'master_%08d' % number
    
def main(request):
    return Handler.run(request)
