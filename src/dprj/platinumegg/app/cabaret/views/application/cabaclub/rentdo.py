# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util import db_util

class Handler(CabaClubHandler):
    """キャバクラ経営店舗レンタル書き込み.
    """
    def process(self):
        # 現在時刻.
        self.__now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # 店舗のマスターデータ.
        args = self.getUrlArgs('/cabaclubrentdo/')
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
        # ユーザ情報.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # 書き込み.
        try:
            db_util.run_in_transaction(self.tr_write, uid, master, days, self.__now)
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            elif err.code == CabaretError.Code.ILLEGAL_ARGS:
                self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubstore(mid)))
                return
            else:
                raise
        # 書き込み結果のURL.
        url = UrlMaker.cabaclubrentend(mid)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_DAYS, days)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def tr_write(self, uid, cabaclubstoremaster, days, now):
        """借り入れ書き込み
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_cabaclub_store_rent(model_mgr, uid, cabaclubstoremaster, days, now)
        model_mgr.write_all()
        model_mgr.write_end()
    

def main(request):
    return Handler.run(request)
