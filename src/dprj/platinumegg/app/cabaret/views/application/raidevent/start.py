# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.happening import HappeningUtil


class Handler(RaidEventBaseHandler):
    """レイドイベント開始ページ.
    適切な判定を行って次のページへリダイレクトさせる.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        # OP閲覧判定.
        current_event = self.getCurrentRaidEvent()
        if current_event is None:
            # 通常はマイページへ遷移.
            url = UrlMaker.mypage()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        flagrecord = self.getCurrentRaidFlagRecord()
        if flagrecord is None or not (config.starttime <= flagrecord.opvtime < config.endtime):
            # OPを見ていない.
            url = UrlMaker.raidevent_opening()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        mid = flagrecord.mid
        
        # タイムボーナス演出閲覧判定.
#        now = OSAUtil.get_now()
#        stime, etime = BackendApi.get_raidevent_timebonus_time(model_mgr, using=settings.DB_READONLY, now=now)
#        if stime is None or etime is None:
#            pass
#        elif not (stime <= flagrecord.tbvtime < etime):
#            # タイムボーナス演出を見ていない.
#            url = UrlMaker.raidevent_timebonus()
#            self.appRedirect(self.makeAppLinkUrlRedirect(url))
#            return
        
        # 未確認結果判定.
        cur_happening = self.getHappening()
        if cur_happening:
            eventid = HappeningUtil.get_raideventid(cur_happening.happening.event)
            if eventid == mid:
                if (cur_happening.happening.is_cleared() or cur_happening.happening.is_missed_and_not_end()):
                    # 未確認の結果がある.
                    url = UrlMaker.raidresultanim(cur_happening.id)
                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
                    return
        
        # 通常はマイページへ遷移.
        url = UrlMaker.mypage()
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    

def main(request):
    return Handler.run(request)
