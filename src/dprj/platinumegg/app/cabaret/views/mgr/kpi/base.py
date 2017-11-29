# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import os
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import settings_sub

class KpiHandler(AdminHandler):
    """KPIダウンロードページ.
    """
    
    #================================
    # 各ページのパラメータ.
    def getKpiName(self):
        """Kpiターゲット名.
        """
        raise NotImplementedError()
    
    def getTitle(self):
        """タイトル.
        """
        raise NotImplementedError()
    
    #================================
    
    def process(self):
        args = self.getUrlArgs(self.getUrl())
        ope = args.get(0)
        self.__filename = args.get(1)
        
        table = {
            'download' : self.__proc_download,
            'delete' : self.__proc_delete,
        }
        table.get(ope, self.__proc_list)()
    
    def __proc_list(self):
        """csvを一覧表示.
        """
        dirpath = self.getCSVDirPath()
        
        filelist = []
        def add(filename):
            filelist.append({
                'filename' : filename,
                'url_download' : self.makeAppLinkUrlAdmin(self.makeDownloadLinkUrl(filename)),
                'url_delete' : self.makeAppLinkUrlAdmin(self.makeDeleteLinkUrl(filename)),
            })
        
        if os.path.exists(dirpath):
            for filename in os.listdir(dirpath):
                if filename[-4:] == '.csv':
                    add(filename)
        filelist.sort(key=lambda x:x['filename'], reverse=True)
        self.html_param['filelist'] = filelist
        
        self.html_param['page_title'] = self.getTitle()
        
        self.html_param['filedata_table'] = self.makeFileDataTable(dirpath, filelist)
        
        self.html_param['optional_form'] = self.getOptionalForm()
        
        self.writeAppHtml('kpi')
    
    def getOptionalForm(self):
        return None
    
    def makeFileDataTable(self, dirpath, filelist):
        return None
    
    def __proc_download(self):
        """csvをダウンロード.
        """
        filepath = self.__get_target_filepath()
        if filepath is None:
            self.response.set_status(404)
            self.response.send()
            return
        
        csv_data = None
        f = None
        try:
            f = open(filepath, 'rb')
            csv_data = f.read()
            f.close()
        except:
            if f:
                f.close()
            raise
        
        self.osa_util.write_csv_data(csv_data, self.__filename)
    
    def __proc_delete(self):
        """csvを削除.
        """
        filepath = self.__get_target_filepath()
        if filepath is None:
            url = self.setAlert(self.makeListLinkUrl(), u'ファイルが見つかりませんでした.%s' % self.__filename, alert_code=AlertCode.ERROR)
            self.appRedirect(self.makeAppLinkUrlAdmin(url))
            return
        
        os.remove(filepath)
        
        if os.path.exists(filepath):
            url = self.setAlert(self.makeListLinkUrl(), u'ファイルの削除に失敗しました.%s' % self.__filename, alert_code=AlertCode.ERROR)
        else:
            url = self.setAlert(self.makeListLinkUrl(), u'ファイルを削除しました.%s' % self.__filename, alert_code=AlertCode.SUCCESS)
        self.appRedirect(self.makeAppLinkUrlAdmin(url))
    
    def __get_target_filepath(self):
        """対象のファイルのパス.
        """
        if self.__filename and self.__filename[-4:] == '.csv':
            dirpath = self.getCSVDirPath()
            filepath = os.path.join(dirpath, self.__filename)
            if os.path.exists(filepath):
                return filepath
        return None
    
    def getCSVDirPath(self):
        """csvファイルが配置されているディレクトリのパス.
        """
        return os.path.join(settings_sub.KPI_ROOT, self.getKpiName())
    
    def getUrl(self):
        """このページのURL.
        """
        return UrlMaker.mgr_kpi(self.getKpiName())
    
    def makeListLinkUrl(self):
        """一覧ページURL.
        """
        return UrlMaker.mgr_kpi(self.getKpiName(), 'list')
    
    def makeDownloadLinkUrl(self, filename):
        """ダウンロードURL.
        """
        return UrlMaker.mgr_kpi(self.getKpiName(), 'download', filename)
    
    def makeDeleteLinkUrl(self, filename):
        """ファイル削除URL.
        """
        return UrlMaker.mgr_kpi(self.getKpiName(), 'delete', filename)

