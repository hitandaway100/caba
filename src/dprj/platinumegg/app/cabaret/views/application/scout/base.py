# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings


class ScoutHandler(AppHandler):
    """スカウトのハンドラ.
    """
    def makeScoutObj(self, scoutmaster, scoutplaydata):
        """スカウト情報作成.
        """
        v_player = self.getViewerPlayer()
        progress = scoutplaydata.progress if scoutplaydata else 0
        dropitems = BackendApi.get_dropitemobj_list(self, v_player, scoutmaster, using=settings.DB_READONLY)
        obj_scout = Objects.scout(self, v_player, scoutmaster, progress, dropitems)
        return obj_scout
