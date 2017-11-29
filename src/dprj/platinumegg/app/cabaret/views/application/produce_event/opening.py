# -*- coding: utf-8 -*-
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.views.application.produce_event.base import ProduceEventBaseHandler


class Handler(ProduceEventBaseHandler):
    """プロデュースイベントオープニング演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_produce_event_config(model_mgr, using=settings.DB_READONLY)
        cur_eventmaster = config.get_produce_event_master(model_mgr, using=settings.DB_READONLY)
        uid = self.getViewerPlayer().id
        
        # OP閲覧フラグを立てる.
        flagrecord = self.getCurrentProduceFlagRecord()
        if BackendApi.check_produceevent_lead_opening(model_mgr, uid, cur_eventmaster.id):
            if flagrecord is None or not (config.starttime <= flagrecord.opvtime < config.endtime):
                flagrecord = BackendApi.update_produceevenflagrecord(config.mid, uid, opvtime=OSAUtil.get_now())
            model_mgr.set_got_models([flagrecord])
        
        url = UrlMaker.produceevent_explain(cur_eventmaster.id)
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
