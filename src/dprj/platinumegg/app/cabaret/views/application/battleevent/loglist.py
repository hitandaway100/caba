# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from defines import Defines

class Handler(BattleEventBaseHandler):
    """バトルイベントバトル履歴一覧.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        eventmaster = None
        if config.mid:
            eventmaster = BackendApi.get_battleevent_master(model_mgr, config.mid, using=settings.DB_READONLY)
        if eventmaster is None:
            self.redirectToTop()
            return
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
        
        nummax = BackendApi.get_battleevent_battlelog_num(model_mgr, uid, using=settings.DB_READONLY)
        
        offset = page * Defines.GAMELOG_PAGE_CONTENT_NUM
        loglist = BackendApi.get_battleevent_battlelog_list(model_mgr, uid, Defines.GAMELOG_PAGE_CONTENT_NUM, offset, using=settings.DB_READONLY)
        
        infolist = BackendApi.make_battleevent_battleloginfo(self, loglist)
        self.html_param['battleloglist'] = infolist
        
        self.putPagenation(UrlMaker.battleevent_loglist(), page, nummax, Defines.GAMELOG_PAGE_CONTENT_NUM)
        
        self.putEventTopic(eventmaster.id)
        
        if eventmaster.is_goukon:
            self.writeAppHtml('gcevent/battlelog')
        else:
            self.writeAppHtml('btevent/battlelog')

def main(request):
    return Handler.run(request)
