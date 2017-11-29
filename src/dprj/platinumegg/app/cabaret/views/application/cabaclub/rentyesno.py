# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines

class Handler(CabaClubHandler):
    """キャバクラ経営店舗レンタル確認.
    """
    def process(self):
        # 現在時刻.
        self.__now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # 店舗のマスターデータ.
        args = self.getUrlArgs('/cabaclubrentyesno/')
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
        # 店舗情報.
        storeset = BackendApi.get_cabaretclub_storeset(model_mgr, uid, mid, using=settings.DB_READONLY)
        if storeset and (storeset.is_alive(self.__now) or storeset.get_rental_cost(days) is None):
            # 既に借り入れ済み.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubstore(mid)))
            return
        # スコア情報.
        scoredata = BackendApi.get_cabaretclub_scoreplayerdata(model_mgr, uid, using=settings.DB_READONLY)
        obj_cabaclub_management_info = Objects.cabaclub_management_info(self, scoredata)
        # 店舗マスター.
        obj_cabaclubstoremaster = Objects.cabaclubstoremaster(self, master)
        # 書き込みのURL.
        url_write = UrlMaker.cabaclubrentdo(mid)
        url_write = OSAUtil.addQuery(url_write, Defines.URLQUERY_DAYS, days)
        # HTML書き込み.
        self.html_param.update(
            cabaclub_management_info = obj_cabaclub_management_info,
            cabaclubstoremaster = obj_cabaclubstoremaster,
            url_write = self.makeAppLinkUrl(url_write),
            days = days,
        )
        self.writeAppHtml('cabaclub/rentyesno')
    

def main(request):
    return Handler.run(request)
