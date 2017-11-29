# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings


class Handler(RaidEventBaseHandler):
    """イベントレイドオープニング演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        cur_eventmaster = self.getCurrentRaidEvent()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # OP閲覧フラグを立てる.
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        flagrecord = self.getCurrentRaidFlagRecord()
        if flagrecord is None or not (config.starttime <= flagrecord.opvtime < config.endtime):
            flagrecord = BackendApi.update_raideventflagrecord(model_mgr, cur_eventmaster.id, uid, OSAUtil.get_now())
            model_mgr.set_got_models([flagrecord])
        
        if BackendApi.check_raidevent_lead_bigboss(model_mgr, uid, cur_eventmaster.id, using=settings.DB_READONLY):
            url = UrlMaker.raidevent_bigboss()
        else:
            url = UrlMaker.raidevent_explain(cur_eventmaster.id)
        
        if cur_eventmaster.op:
            # 演出のパラメータ.
            effectpath = UrlMaker.event_scenario()
            dataUrl = self.makeAppLinkUrlEffectParamGet('eventscenario/%d/normal%s' % (cur_eventmaster.op, url))
            self.appRedirectToEffect2(effectpath, dataUrl)
        else:
            # 演出なし.
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
    

def main(request):
    return Handler.run(request)
