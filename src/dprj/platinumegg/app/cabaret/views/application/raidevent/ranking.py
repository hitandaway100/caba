# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines


class Handler(RaidEventBaseHandler):
    """レイドイベントランキングページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        args = self.getUrlArgs('/raideventranking/')
        str_eventid = str(args.get(0))
        view_myrank = args.get(1) == '1'
        
        model_mgr = self.getModelMgr()
        eventmaster = None
        mid = None
        if str_eventid.isdigit():
            mid = int(str_eventid)
            eventmaster = BackendApi.get_raideventmaster(model_mgr, mid, using=settings.DB_READONLY)
        
        if eventmaster is None:
            raise CabaretError(u'閲覧できないイベントです', CabaretError.Code.ILLEGAL_ARGS)
        
        # 開催中判定.
        cur_eventmaster = self.getCurrentRaidEvent(quiet=True)
        if cur_eventmaster and cur_eventmaster.id == mid:
            is_opened = True
        else:
            is_opened = False
        self.html_param['is_opened'] = is_opened
        
        self.putEventTopic(mid, 'ranking')
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 初心者フラグ.
        is_beginer = BackendApi.check_raidevent_beginer(model_mgr, uid, eventmaster, using=settings.DB_READONLY)
        self.html_param['is_beginer'] = is_beginer
        
        # ランキング.
        view_beginer = self.request.get(Defines.URLQUERY_BEGINER) == "1"
        if view_beginer and not is_beginer:
            view_myrank = False
        self.putRanking(uid, mid, view_myrank, UrlMaker.raidevent_ranking(mid, False), UrlMaker.raidevent_ranking(mid, True), view_beginer)
        
        self.writeHtml(eventmaster, 'ranking')

def main(request):
    return Handler.run(request)
