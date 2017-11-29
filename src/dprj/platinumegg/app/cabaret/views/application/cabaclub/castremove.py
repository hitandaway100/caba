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
    """キャバクラ経営キャスト配置削除.
    """
    def process(self):
        # 現在時刻.
        self.__now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # ユーザ情報.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # 店舗のマスターデータ.
        args = self.getUrlArgs('/cabaclubcastremove/')
        mid = args.getInt(0)
        master = None
        if mid:
            master = BackendApi.get_cabaretclub_store_master(model_mgr, mid, using=settings.DB_READONLY)
        if master is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubtop()))
            return
        mid = master.id
        # 削除するID.
        cardid = args.getInt(1)
        card = None
        if cardid:
            cardlist = BackendApi.get_cards([cardid], model_mgr, using=settings.DB_READONLY)
            if cardlist:
                card = cardlist[0]
        if card is None or card.card.uid != uid:
            # カードの指定おかしい.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubstore(mid)))
            return
        # 書き込み.
        try:
            db_util.run_in_transaction(self.tr_write, uid, master, self.__now, cardid)
        except CabaretError, err:
            if err.code in CabaretError.Code.ALREADY_RECEIVED:
                pass
            elif err.code == CabaretError.Code.ILLEGAL_ARGS:
                self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubstore(mid)))
                return
            else:
                raise
        # 書き込み結果のURL.
        url = UrlMaker.cabaclubstore(mid)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def tr_write(self, uid, cabaclubstoremaster, now, cardid):
        """キャスト削除書き込み
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_cabaclubstore_change_cast(model_mgr, uid, cabaclubstoremaster, now, cardid)
        model_mgr.write_all()
        model_mgr.write_end()
    

def main(request):
    return Handler.run(request)
