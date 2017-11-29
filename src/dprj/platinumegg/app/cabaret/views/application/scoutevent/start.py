# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler


class Handler(ScoutHandler):
    """スカウトイベント開始踏み台ページ.
    適切な判定を行って次のページへリダイレクトさせる.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        # OP閲覧判定.
        current_event = self.getCurrentScoutEvent()
        if current_event is not None:
            # イベント開催中.
            model_mgr = self.getModelMgr()
            config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
            flagrecord = self.getScoutEventFlagRecord()
            if flagrecord is None or not (config.starttime <= flagrecord.opvtime < config.endtime):
                # OPを見ていない.
                url = UrlMaker.scoutevent_opening()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        
        # 通常はマイページへ遷移.
        url = UrlMaker.mypage()
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    

def main(request):
    return Handler.run(request)
