# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings


class Handler(RaidEventBaseHandler):
    """大ボス演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        cur_eventmaster = self.getCurrentRaidEvent()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 閲覧フラグを立てる.
        if BackendApi.check_raidevent_lead_bigboss(model_mgr, uid, cur_eventmaster.id, using=settings.DB_READONLY):
            flagrecord = BackendApi.update_raideventunwillingflagrecord(cur_eventmaster.id, uid, OSAUtil.get_now())
            model_mgr.set_got_models([flagrecord])
        
        # 演出のパラメータ.
        effectpath = 'raidevent/event_boss_ec2/effect.html'
        params = {
            'backUrl' : self.makeAppLinkUrl(UrlMaker.raidevent_explain(cur_eventmaster.id)),
            'pre' : self.url_static_img + 'event/raidevent/%s/effect/' % cur_eventmaster.codename
        }
        self.appRedirectToEffect(effectpath, params)
    

def main(request):
    return Handler.run(request)
