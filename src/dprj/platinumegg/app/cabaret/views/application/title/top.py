# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
import datetime

class Handler(CabaClubHandler):
    """称号Top.
    """
    def process(self):
        # 現在時刻.
        now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # ユーザ情報.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # 経営情報.
        scoredata = BackendApi.get_cabaretclub_scoreplayerdata(model_mgr, uid, using=settings.DB_READONLY)
        obj_cabaclub_management_info = Objects.cabaclub_management_info(self, scoredata)
        # 現在の称号.
        title_playerdata = BackendApi.get_title_playerdata(model_mgr, uid, using=settings.DB_READONLY)
        current_title_id = title_playerdata.title if title_playerdata else 0
        obj_title = None
        # 称号一覧.
        titlemaster_list = BackendApi.get_title_master_all(model_mgr, using=settings.DB_READONLY)
        obj_titlemaster_list = []
        for titlemaster in titlemaster_list:
            if current_title_id == titlemaster.id and now < (title_playerdata.stime + datetime.timedelta(days=titlemaster.days)):
                obj_title = Objects.title(self, titlemaster, title_playerdata)
            obj_titlemaster_list.append(Objects.titlemaster(self, titlemaster))
        # HTML書き込み.
        self.html_param.update(
            cabaclub_management_info = obj_cabaclub_management_info,
            titlemaster_list = obj_titlemaster_list,
            title = obj_title,
        )
        self.writeAppHtml('title/top')

def main(request):
    return Handler.run(request)
