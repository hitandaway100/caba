# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from defines import Defines


class Handler(RaidEventBaseHandler):
    """レイドイベントヘルプ依頼一覧.
    """
    
    CONTENT_NUM_MAX_PER_PAGE = 5
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
        
        model_mgr = self.getModelMgr()
        
        # 開催中判定.
        cur_eventmaster = self.getCurrentRaidEvent()
        mid = cur_eventmaster.id
        
        # イベントTopのURL.
        url = UrlMaker.raidevent_top(mid)
        self.html_param['url_raidevent_top'] = self.makeAppLinkUrl(url)
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        offset = page * Handler.CONTENT_NUM_MAX_PER_PAGE
        limit = Handler.CONTENT_NUM_MAX_PER_PAGE
        
        # 救援要請.
        func = self.putRaidHelpList(do_execute=False, limit=limit, offset=offset)
        
        helpnum = BackendApi.get_raidhelp_num(model_mgr, uid, using=settings.DB_READONLY)
        self.putPagenation(UrlMaker.raidevent_helplist(), page, helpnum, Handler.CONTENT_NUM_MAX_PER_PAGE)
        
        if helpnum < 1 and self.request.get(Defines.URLQUERY_FLAG) == '_mypage':
            self.html_param['from_mypage'] = True
        
        if func:
            self.execute_api()
            func()
        
        self.writeHtml(cur_eventmaster, 'helplist')
    

def main(request):
    return Handler.run(request)
