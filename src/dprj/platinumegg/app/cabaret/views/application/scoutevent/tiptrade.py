# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler
from platinumegg.app.cabaret.models.Player import PlayerRequest


class Handler(ScoutHandler):
    """スカウトイベントチップ交換ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRequest]
    
    def process(self):
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=using)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        mid = eventmaster.id
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 短冊情報.
        obj_tanzakulist = BackendApi.put_scoutevent_tanzakudata(self, uid)
        if not obj_tanzakulist:
            # 短冊が無いイベント.
            url = UrlMaker.scoutevent_top()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # 所持チップ数.
        scorerecord = BackendApi.get_scoutevent_scorerecord(model_mgr, mid, uid, using=settings.DB_READONLY)
        self.html_param['scouteventscore'] = Objects.scoutevent_score(scorerecord)
        
        # トピック.
        self.putEventTopic(mid)
        
        # このページのURL.
        url = UrlMaker.scouteventtiptradedo(v_player.req_confirmkey)
        self.html_param['url_do'] = self.makeAppLinkUrl(url)
        
        self.writeScoutEventHTML('tip_trade', eventmaster)

def main(request):
    return Handler.run(request)
