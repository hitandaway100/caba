# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker


class Handler(AppHandler):
    """シリアルコードキャンペーンTopページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        args = self.getUrlArgs('/serial_top/')
        
        # マスター.
        mid = args.getInt(0)
        master = None
        if mid:
            master = BackendApi.get_serialcampaign_master(model_mgr, mid, using=settings.DB_READONLY)
        if master is None:
            # 存在しないキャンペーン.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return
        
        # マスターデータ情報.
        self.html_param['serialcampaign'] = Objects.serialcampaign(self, master)
        
        # 報酬.
        prizelist = BackendApi.get_prizelist(model_mgr, master.prizes, using=settings.DB_READONLY)
        self.html_param['prize'] = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
        
        # 開催中か.
        self.html_param['is_open'] = BackendApi.check_schedule(model_mgr, master.schedule, using=settings.DB_READONLY)
        
        # 入力ページのURL.
        url = UrlMaker.serial_input(mid)
        self.html_param['url_input'] = self.makeAppLinkUrl(url)
        
        self.writeAppHtml('serialcode/serialtop')

def main(request):
    return Handler.run(request)
