# -*- coding: utf-8 -*-
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.views.application.produce_event.base import ProduceEventBaseHandler


class Handler(ProduceEventBaseHandler):
    """プロデュースイベントエンディング演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_produce_event_config(model_mgr, using=settings.DB_READONLY)
        
        if config.mid == 0 or not config.is_open_epilogue(OSAUtil.get_now()):
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return
        
        produce_event_master = config.get_produce_event_master(model_mgr)
        if produce_event_master is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return
        
        uid = self.getViewerPlayer().id
        if BackendApi.check_produceevent_lead_epilogue(model_mgr, uid, produce_event_master.id):
            flagrecord = BackendApi.update_produceevenflagrecord(produce_event_master.id, uid, epvtime=OSAUtil.get_now())
            model_mgr.set_got_models([flagrecord])
        
        url = UrlMaker.produceevent_top(produce_event_master.id)
        if produce_event_master.ed:
            # 演出のパラメータ.
            effectpath = UrlMaker.event_scenario()
            dataUrl = self.makeAppLinkUrlEffectParamGet('eventscenario/%d/last%s' % (produce_event_master.ed, url))
            self.appRedirectToEffect2(effectpath, dataUrl)
        else:
            # 演出なし.
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
    

def main(request):
    return Handler.run(request)
