# -*- coding: utf-8 -*-
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler


class Handler(BattleEventBaseHandler):
    """バトルイベント中押し演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        now = OSAUtil.get_now()
        
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        cur_eventmaster = None
        if config.mid and now < config.endtime:
            cur_eventmaster = BackendApi.get_battleevent_master(model_mgr, config.mid, using=settings.DB_READONLY)
        
        if cur_eventmaster is None or not cur_eventmaster.is_goukon:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 閲覧フラグを立てる.
        if BackendApi.check_battleevent_lead_scenario(model_mgr, uid, config.mid, using=settings.DB_READONLY):
            flagrecord = BackendApi.update_battleevent_flagrecord(cur_eventmaster.id, uid, scvtime=now)
            model_mgr.set_got_models([flagrecord])
        
        # 演出のパラメータ.
        effectpath = '%s/event_nakaoshi/effect.html' % cur_eventmaster.effectname
        params = {
            'backUrl' : self.makeAppLinkUrl(UrlMaker.battleevent_top(cur_eventmaster.id)),
            'pre' : self.url_static + 'effect/sp/v2/%s/data/' % cur_eventmaster.effectname,
            'logo_img' : 'scenario/event_logo.png',
            'logo_w_img' : 'scenario/event_logo_w.png',
        }
        self.appRedirectToEffect(effectpath, params)
    

def main(request):
    return Handler.run(request)
