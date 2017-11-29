# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler
from platinumegg.app.cabaret.models.Player import PlayerRequest
import settings_sub


class Handler(ScoutHandler):
    """スカウトイベントチップ交換ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRequest]
    
    def process(self):
        args = self.getUrlArgs('/sceventtiptraderesult/')
        tanzaku_number = args.getInt(0)
        tanzaku_num = args.getInt(1)
        
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=using)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        mid = eventmaster.id
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # イベント情報.
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
        self.html_param['scoutevent'] = Objects.scouteventmaster(self, eventmaster, config)
        
        # 短冊情報.
        tanzakumaster = BackendApi.get_scoutevent_tanzakumaster(model_mgr, mid, tanzaku_number, using=settings.DB_READONLY)
        if tanzakumaster is None:
            if settings_sub.IS_DEV:
                raise CabaretError(u'存在しない短冊です', CabaretError.Code.ILLEGAL_ARGS)
            url = UrlMaker.scouteventtiptrade()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        self.html_param['scoutevent_tanzaku'] = Objects.scoutevent_tanzaku(self, tanzakumaster, None)
        
        # 所持チップ数.
        scorerecord = BackendApi.get_scoutevent_scorerecord(model_mgr, mid, uid, using=settings.DB_READONLY)
        self.html_param['scouteventscore'] = Objects.scoutevent_score(scorerecord)
        
        # 投入した短冊数.
        self.html_param['tanzaku_num'] = tanzaku_num
        
        # トピック.
        self.putEventTopic(mid)
        
        self.writeScoutEventHTML('tip_trade_complete', eventmaster)

def main(request):
    return Handler.run(request)
