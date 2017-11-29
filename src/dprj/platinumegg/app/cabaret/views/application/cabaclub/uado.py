# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util import db_util
from defines import Defines

class Handler(CabaClubHandler):
    """キャバクラ対策書き込み.
    """
    def process(self):
        # 現在時刻.
        self.__now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # 店舗のマスターデータ.
        args = self.getUrlArgs('/cabaclubuado/')
        mid = args.getInt(0)
        master = None
        if mid:
            master = BackendApi.get_cabaretclub_store_master(model_mgr, mid, using=settings.DB_READONLY)
        if master is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubtop()))
            return
        # ユーザ情報.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # 書き込み前店舗情報.
        storeset = BackendApi.get_cabaretclub_storeset(model_mgr, uid, mid, using=settings.DB_READONLY)
        if storeset is None or not storeset.is_alive(self.__now):
            # 店舗を借りていない.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubstore(mid)))
            return
        eventmaster = storeset.get_current_eventmaster(self.__now)
        if eventmaster is None or storeset.playerdata.ua_flag:
            # イベントが発生していない.もしくはユーザアクションを実行済み.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubstore(mid)))
            return
        # 書き込み.
        try:
            db_util.run_in_transaction(self.tr_write, uid, master, self.__now)
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            elif err.code == CabaretError.Code.ILLEGAL_ARGS:
                self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubstore(mid)))
                return
            else:
                raise
        # 書き込み結果のURL.
        url = UrlMaker.cabaclubuaend(mid)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_ID, eventmaster.id)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def tr_write(self, uid, cabaclubstoremaster, now):
        """対策書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_cabaclubstore_useraction(model_mgr, uid, cabaclubstoremaster, now)
        model_mgr.write_all()
        model_mgr.write_end()

def main(request):
    return Handler.run(request)
