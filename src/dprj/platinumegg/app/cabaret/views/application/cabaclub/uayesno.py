# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines

class Handler(CabaClubHandler):
    """キャバクラ対策確認.
    """
    def process(self):
        # 現在時刻.
        self.__now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # 店舗のマスターデータ.
        args = self.getUrlArgs('/cabaclubuayesno/')
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
        # 店舗情報.
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
        elif eventmaster.ua_type == Defines.CabaClubEventUAType.NONE:
            # ユーザアクションのないイベント.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubstore(mid)))
            return
        # スコア情報.
        scoredata = BackendApi.get_cabaretclub_scoreplayerdata(model_mgr, uid, using=settings.DB_READONLY)
        obj_cabaclub_management_info = Objects.cabaclub_management_info(self, scoredata)
        # イベント情報.
        obj_cabaclubstoreeventmaster = Objects.cabaclubstoreeventmaster(self, eventmaster)
        # HTML書き込み.
        self.html_param.update(
            cabaclubstoreeventmaster = obj_cabaclubstoreeventmaster,
            cabaclub_management_info = obj_cabaclub_management_info,
            url_store = self.makeAppLinkUrl(UrlMaker.cabaclubstore(mid)),
            url_write = self.makeAppLinkUrl(UrlMaker.cabaclubuado(mid)),
        )
        self.writeAppHtml('cabaclub/uayesno')
    

def main(request):
    return Handler.run(request)
