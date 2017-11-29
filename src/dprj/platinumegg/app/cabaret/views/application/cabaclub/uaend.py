# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines

class Handler(CabaClubHandler):
    """キャバクラ対策完了.
    """
    def process(self):
        # 現在時刻.
        self.__now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # 店舗のマスターデータ.
        args = self.getUrlArgs('/cabaclubuaend/')
        mid = args.getInt(0)
        master = None
        if mid:
            master = BackendApi.get_cabaretclub_store_master(model_mgr, mid, using=settings.DB_READONLY)
        if master is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubtop()))
            return
        # イベント情報.
        eventmaster_id = self.request.get(Defines.URLQUERY_ID)
        eventmaster = None
        if eventmaster_id and eventmaster_id.isdigit():
            eventmaster_id = int(eventmaster_id)
            eventmaster = BackendApi.get_cabaretclub_event_master(model_mgr, eventmaster_id, using=settings.DB_READONLY)
        if eventmaster is None:
            # 存在しないイベント.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubstore(mid)))
            return
        obj_cabaclubstoreeventmaster = Objects.cabaclubstoreeventmaster(self, eventmaster)
        # ユーザ情報.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # スコア情報.
        scoredata = BackendApi.get_cabaretclub_scoreplayerdata(model_mgr, uid, using=settings.DB_READONLY)
        obj_cabaclub_management_info = Objects.cabaclub_management_info(self, scoredata)
        # HTML書き込み.
        self.html_param.update(
            cabaclubstoreeventmaster = obj_cabaclubstoreeventmaster,
            cabaclub_management_info = obj_cabaclub_management_info,
            url_store = self.makeAppLinkUrl(UrlMaker.cabaclubstore(mid)),
        )
        self.writeAppHtml('cabaclub/uaend')
    

def main(request):
    return Handler.run(request)
