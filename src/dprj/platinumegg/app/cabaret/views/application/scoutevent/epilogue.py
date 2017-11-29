# -*- coding: utf-8 -*-
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler


class Handler(ScoutHandler):
    """スカウトイベントエンディング演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        now = OSAUtil.get_now()
        
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
        cur_eventmaster = None
        if config.mid and config.endtime < now:
            cur_eventmaster = BackendApi.get_scouteventmaster(model_mgr, config.mid, using=settings.DB_READONLY)
        
        if cur_eventmaster is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # EP閲覧フラグを立てる.
        if BackendApi.check_scoutevent_lead_epilogue(model_mgr, uid, cur_eventmaster.id, using=settings.DB_READONLY):
            flagrecord = BackendApi.update_scouteventflagrecord(cur_eventmaster.id, uid, epvtime=now)
            model_mgr.set_got_models([flagrecord])
        
        url = UrlMaker.scoutevent_top(cur_eventmaster.id)
        if cur_eventmaster.ed:
            # 演出のパラメータ.
            effectpath = UrlMaker.event_scenario()
            dataUrl = self.makeAppLinkUrlEffectParamGet('eventscenario/%d/last%s' % (cur_eventmaster.ed, url))
            self.appRedirectToEffect2(effectpath, dataUrl)
        else:
            # 演出なし.
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
    

def main(request):
    return Handler.run(request)
