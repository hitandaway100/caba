# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.redisdb import CabaClubRecentlyViewedTime

class Handler(CabaClubHandler):
    """キャバクラ店舗イベント発生演出.
    """
    def process(self):
        # 現在時刻.
        self.__now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # 店舗のマスターデータ.
        args = self.getUrlArgs('/cabaclubeventanim/')
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
        if eventmaster is None:
            # イベントが発生していない.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubstore(mid)))
            return
        # 閲覧時間の更新.
        CabaClubRecentlyViewedTime.create(uid, mid, self.__now).save()
        # 演出用パラメータ.
        params = dict(
            backUrl = self.makeAppLinkUrl(UrlMaker.cabaclubstore(mid)),
        )
        # 仮.
        self.appRedirectToEffect('cb_system/warning/effect.html', params)

def main(request):
    return Handler.run(request)
