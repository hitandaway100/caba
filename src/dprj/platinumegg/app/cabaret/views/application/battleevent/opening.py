# -*- coding: utf-8 -*-
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler


class Handler(BattleEventBaseHandler):
    """バトルイベントオープニング演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        cur_eventmaster = self.getCurrentBattleEvent()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # OP閲覧フラグを立てる.
        if BackendApi.check_battleevent_lead_opening(model_mgr, uid, cur_eventmaster.id, using=settings.DB_READONLY):
            flagrecord = BackendApi.update_battleevent_flagrecord(cur_eventmaster.id, uid, OSAUtil.get_now())
            model_mgr.set_got_models([flagrecord])
            # ここで一度とっておく.
            BackendApi.get_battleeventpresent_pointdata(model_mgr, uid, cur_eventmaster.id)
        
        url = UrlMaker.battleevent_explain(cur_eventmaster.id)
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
