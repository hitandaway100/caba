# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines


class Handler(ScoutHandler):
    """スカウトイベントランキングページ.
    """
    
    CONTENT_NUM_MAX_PER_PAGE = 10
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        args = self.getUrlArgs('/sceventranking/')
        str_eventid = str(args.get(0))
        view_myrank = args.get(1) == '1'
        
        model_mgr = self.getModelMgr()
        eventmaster = None
        mid = None
        if str_eventid.isdigit():
            mid = int(str_eventid)
            eventmaster = BackendApi.get_scouteventmaster(model_mgr, mid, using=settings.DB_READONLY)
        
        if eventmaster is None:
            raise CabaretError(u'閲覧できないイベントです', CabaretError.Code.ILLEGAL_ARGS)
        
        # 開催中判定.
        cur_eventmaster = self.getCurrentScoutEvent(quiet=True)
        if cur_eventmaster and cur_eventmaster.id == mid:
            is_opened = True
        else:
            is_opened = False
        self.html_param['is_opened'] = is_opened
        
        self.putEventTopic(mid, 'ranking')
        
        # イベント情報.
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
        obj_scouteventmaster = Objects.scouteventmaster(self, eventmaster, config)
        self.html_param['scoutevent'] = obj_scouteventmaster
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 初心者判定.
        is_beginer = BackendApi.check_scoutevent_beginer(model_mgr, uid, eventmaster, config=config, using=settings.DB_READONLY)
        self.html_param['is_beginer'] = is_beginer
        
        # ランキング.
        view_beginer = self.request.get(Defines.URLQUERY_BEGINER) == "1"
        if view_beginer and not is_beginer:
            view_myrank = False
        
        url_scoutevent_ranking = UrlMaker.scoutevent_ranking(mid, False)
        url_scoutevent_myrank = UrlMaker.scoutevent_ranking(mid, True)
        self.putRanking(uid, mid, view_myrank, url_scoutevent_ranking, url_scoutevent_myrank, view_beginer=view_beginer)
        
        self.writeScoutEventHTML('ranking', eventmaster)
    

def main(request):
    return Handler.run(request)
