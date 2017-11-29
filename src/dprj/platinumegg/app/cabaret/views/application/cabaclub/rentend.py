# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines

class Handler(CabaClubHandler):
    """キャバクラ経営店舗レンタル完了.
    """
    def process(self):
        # 現在時刻.
        self.__now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # 店舗のマスターデータ.
        args = self.getUrlArgs('/cabaclubrentend/')
        mid = args.getInt(0)
        master = None
        if mid:
            master = BackendApi.get_cabaretclub_store_master(model_mgr, mid, using=settings.DB_READONLY)
        if master is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubtop()))
            return
        # 借りる日数.
        days = self.request.get(Defines.URLQUERY_DAYS)
        days = int(days) if days and days.isdigit() else 0
        # HTML書き込み.
        self.html_param.update(
            url_store = self.makeAppLinkUrl(UrlMaker.cabaclubstore(mid)),
        )
        self.writeAppHtml('cabaclub/rentend')
    

def main(request):
    return Handler.run(request)
