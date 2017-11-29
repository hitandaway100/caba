# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import urllib
from platinumegg.app.cabaret.views.application.boss.base import BossHandler
from platinumegg.app.cabaret.models.EventScout import EventScoutStageMaster


class Handler(BossHandler):
    """ボス戦後のシナリオ閲覧.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        self.__swf_params = {}
        
        args = self.getUrlArgs('/bossscenarioanim/')
        try:
            stageid = int(args.get(0))
            battlekey = urllib.unquote(args.get(1))[:32]
            self.setAreaID(stageid)
        except:
            raise CabaretError(u'引数が不正です', CabaretError.Code.ILLEGAL_ARGS)
        
        stagemaster = self.getAreaMaster()
        if not isinstance(stagemaster, EventScoutStageMaster) or stagemaster.bossscenario < 1:
            # イベントじゃないとダメです.
            self.appRedirect(UrlMaker.bossresult(stageid, battlekey))
            return
        
        eventmaster = self.callFunctionByFromPage('getEventMaster')
        if eventmaster is None or stagemaster.eventid != eventmaster.id:
            self.callFunctionByFromPage('redirectToScoutTop')
            return
        
        # 演出のパラメータ.
        url = UrlMaker.bossresult(stageid, battlekey)
        effectpath = UrlMaker.event_scenario()
        dataUrl = self.makeAppLinkUrlEffectParamGet('eventscenario/{}/normal{}'.format(stagemaster.bossscenario, url))
        dataUrl = self.addFromPageToUrlQuery(dataUrl)
        self.appRedirectToEffect2(effectpath, dataUrl)
    
    #=======================================================
    # スカウトイベント.
    def getEventMaster_SCOUTEVENT(self):
        """イベントのマスターデータを取得.
        """
        model_mgr = self.getModelMgr()
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY)
        return eventmaster
    
    #=======================================================
    # レイドイベント.
    def getEventMaster_RAIDEVENTSCOUT(self):
        """イベントのマスターデータを取得.
        """
        model_mgr = self.getModelMgr()
        eventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
        return eventmaster

    #=======================================================
    # プロデュースイベント
    def getEventMaster_PRODUCEEVENT(self):
        return self.getEventMaster_PRODUCEEVENTSCOUT()

    def getEventMaster_PRODUCEEVENTSCOUT(self):
        """イベントのマスターデータを取得
        """
        model_mgr = self.getModelMgr()
        eventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=settings.DB_READONLY)
        return eventmaster

def main(request):
    return Handler.run(request)
