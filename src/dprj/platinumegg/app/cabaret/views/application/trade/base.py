# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
import settings
from platinumegg.app.cabaret.util.present import PresentSet


class TradeBaseHandler(AppHandler):
    """秘宝交換ベース.
    """
    
    def makeobj(self, trademaster, playerdata=None):
        # model_mgr.
        model_mgr = self.getModelMgr()
        
        v_player = self.getViewerPlayer()
        
        presentlist = BackendApi.create_present(model_mgr, 0, v_player.id, trademaster.itype, trademaster.itemid, trademaster.itemnum, do_set_save=False)
        presentset = PresentSet.presentToPresentSet(model_mgr, [presentlist[0]], using=settings.DB_READONLY)[0]
        
        obj_trade = Objects.trade(self, trademaster, presentset)
        if playerdata is not None:
            trade_cnt = BackendApi.get_trade_cnt(model_mgr, trademaster, playerdata, using=settings.DB_READONLY)
            obj_trade['trade_cnt'] = trade_cnt
        
        return obj_trade
    
    def getCurrentEventMaster(self):
        model_mgr = self.getModelMgr()
        return BackendApi.get_current_ticket_raideventmaster(model_mgr, using=settings.DB_READONLY)
    
    def putRaidEventParams(self, eventmaster=None):
        """レイドイベント用の交換パラメータ.
        """
        model_mgr = self.getModelMgr()
        if eventmaster is None:
            eventmaster = self.getCurrentEventMaster()
        
        if eventmaster:
            v_player = self.getViewerPlayer()
            uid = v_player.id
            
            # イベント情報.
            config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
            self.html_param['raidevent'] = Objects.raidevent(self, eventmaster, config)
            
            # スコア.
            scorerecord = BackendApi.get_raidevent_scorerecord(model_mgr, eventmaster.id, uid, using=settings.DB_READONLY)
            rank = BackendApi.get_raidevent_rank(eventmaster.id, uid)
            self.html_param['raideventscore'] = Objects.raidevent_score(eventmaster, scorerecord, rank)
            
        return eventmaster
    
    
