# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker

class Handler(CabaClubHandler):
    """キャバクラ経営店舗解約確認.
    """
    def process(self):
        # 現在時刻.
        self.__now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # 店舗のマスターデータ.
        args = self.getUrlArgs('/cabaclubcancelyesno/')
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
            # 既に解約済み.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubstore(mid)))
            return
        # 店舗マスター.
        obj_cabaclubstoremaster = Objects.cabaclubstoremaster(self, master)
        # 書き込みのURL.
        url_write = UrlMaker.cabaclubcanceldo(mid)
        # HTML書き込み.
        self.html_param.update(
            cabaclubstoremaster = obj_cabaclubstoremaster,
            url_write = self.makeAppLinkUrl(url_write),
        )
        self.writeAppHtml('cabaclub/cancelyesno')
    

def main(request):
    return Handler.run(request)
