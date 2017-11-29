# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from defines import Defines

class Handler(BattleEventBaseHandler):
    """バトルイベントランキング.
    """
    
    CONTENT_NUM_MAX_PER_PAGE = 10
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        args = self.getUrlArgs('/battleeventranking/')
        eventid = args.getInt(0)
        view_myrank = args.getInt(1) == 1
        
        model_mgr = self.getModelMgr()
        eventmaster = None
        if eventid:
            eventmaster = BackendApi.get_battleevent_master(model_mgr, eventid, using=settings.DB_READONLY)
        
        if eventmaster is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'引数がおかしい')
            self.redirectToTop()
            return
        
        # 開催中判定.
        cur_eventmaster = self.getCurrentBattleEvent(quiet=True)
        if cur_eventmaster and cur_eventmaster.id == eventid:
            is_opened = True
            if not self.checkBattleEventUser(do_check_battle_open=False, do_check_regist=False, do_check_emergency=False):
                return
        else:
            is_opened = False
        self.html_param['is_opened'] = is_opened
        
        # イベント情報.
        self.html_param['battleevent'] = Objects.battleevent(self, eventmaster)
        
        self.putEventTopic(eventid, 'ranking')
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        url_battleevent_ranking = UrlMaker.battleevent_ranking(eventid, False)
        url_battleevent_myrank = UrlMaker.battleevent_ranking(eventid, True)
        
        # 初心者判定.
        is_beginer = BackendApi.check_battleevent_beginer(model_mgr, uid, eventmaster, using=settings.DB_READONLY)
        self.html_param['is_beginer'] = is_beginer
        
        # ランキング.
        view_beginer = self.request.get(Defines.URLQUERY_BEGINER) == "1"
        if view_beginer and not is_beginer:
            view_myrank = False
        self.putRanking(uid, eventid, view_myrank, url_battleevent_ranking, url_battleevent_myrank, view_beginer=view_beginer)
        
        if eventmaster.is_goukon:
            self.writeAppHtml('gcevent/ranking')
        else:
            self.writeAppHtml('btevent/ranking')

def main(request):
    return Handler.run(request)
