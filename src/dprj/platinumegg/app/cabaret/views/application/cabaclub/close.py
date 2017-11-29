# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError

class Handler(CabaClubHandler):
    """キャバクラ経営店舗閉店.
    """
    def process(self):
        # 現在時刻.
        self.__now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # 店舗のマスターデータ.
        args = self.getUrlArgs('/cabaclubclose/')
        mid = args.getInt(0)
        master = None
        if mid:
            master = BackendApi.get_cabaretclub_store_master(model_mgr, mid, using=settings.DB_READONLY)
        if master is None:
            # 存在しない.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubtop()))
            return
        mid = master.id
        # ユーザ情報.
        v_player = self.getViewerPlayer()
        uid = v_player.id
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
        # 店舗に戻る.
        self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubstore(mid)))
    
    def tr_write(self, uid, cabaclubstoremaster, now):
        """店舗閉店書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_cabaclubstore_close(model_mgr, uid, cabaclubstoremaster, now)
        model_mgr.write_all()
        model_mgr.write_end()
    

def main(request):
    return Handler.run(request)