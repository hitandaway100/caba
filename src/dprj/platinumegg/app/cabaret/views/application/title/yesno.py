# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
import datetime
from platinumegg.app.cabaret.util.url_maker import UrlMaker

class Handler(CabaClubHandler):
    """称号交換確認.
    """
    def process(self):
        # 現在時刻.
        now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # 交換する称号.
        args = self.getUrlArgs('/titleyesno/')
        mid = args.getInt(0)
        master = BackendApi.get_title_master(model_mgr, mid, using=settings.DB_READONLY) if mid else None
        if master is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.titletop()))
            return
        # ユーザ情報.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # 経営情報.
        scoredata = BackendApi.get_cabaretclub_scoreplayerdata(model_mgr, uid, using=settings.DB_DEFAULT)
        obj_cabaclub_management_info = Objects.cabaclub_management_info(self, scoredata)
        # 現在の称号.
        title_playerdata = BackendApi.get_title_playerdata(model_mgr, uid, using=settings.DB_DEFAULT)
        current_title_id = title_playerdata.title if title_playerdata else 0
        if current_title_id == master.id and now < (title_playerdata.stime + datetime.timedelta(days=master.days)):
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.titletop()))
            return
        obj_title = Objects.title(self, master, title_playerdata)
        # HTML書き込み.
        self.html_param.update(
            cabaclub_management_info = obj_cabaclub_management_info,
            title = obj_title,
            url_write = self.makeAppLinkUrl(UrlMaker.titledo(mid)),
            url_title = self.makeAppLinkUrl(UrlMaker.titletop()),
        )
        self.writeAppHtml('title/yesno')

def main(request):
    return Handler.run(request)
