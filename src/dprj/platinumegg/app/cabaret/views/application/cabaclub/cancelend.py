# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker

class Handler(CabaClubHandler):
    """キャバクラ経営店舗解約完了.
    """
    def process(self):
        # 現在時刻.
        self.__now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # 店舗のマスターデータ.
        args = self.getUrlArgs('/cabaclubcancelend/')
        mid = args.getInt(0)
        master = None
        if mid:
            master = BackendApi.get_cabaretclub_store_master(model_mgr, mid, using=settings.DB_READONLY)
        if master is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubtop()))
            return
        self.writeAppHtml('cabaclub/cancelend')
    

def main(request):
    return Handler.run(request)
