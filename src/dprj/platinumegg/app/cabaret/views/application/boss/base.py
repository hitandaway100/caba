# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
import settings
from defines import Defines
from platinumegg.app.cabaret.util.url_maker import UrlMaker


class BossHandler(AppHandler):
    """ボス戦のハンドラ.
    """
    def preprocess(self):
        # どれ向けのボスなのかを決めてしまう.
        frompagename = self.getFromPageName()
        if not frompagename in (Defines.FromPages.SCOUTEVENT, Defines.FromPages.RAIDEVENTSCOUT,
                                Defines.FromPages.PRODUCEEVENT, Defines.FromPages.PRODUCEEVENTSCOUT):
            frompagename = Defines.FromPages.SCOUT
        self.__frompagename = frompagename
    
    def callFunctionByFromPage(self, functionname, *args, **kwargs):
        """どこから来たのかを見て関数呼び出し.
        """
        f = getattr(self, '{}_{}'.format(functionname, self.__frompagename.upper()))
        return f(*args, **kwargs)
    
    def setAreaID(self, areaid):
        """エリアIDを設定.
        """
        self.__areaid = areaid
        self.__areamaster = None
        self.__bossmaster = None
    
    def getAreaMaster(self):
        """エリアを取得.
        """
        if self.__areamaster is None:
            self.__areamaster = self.callFunctionByFromPage('_getAreaMaster', self.__areaid)
        return self.__areamaster
    
    def getBossMaster(self):
        """ボスを取得.
        """
        if self.__bossmaster is None:
            model_mgr = self.getModelMgr()
            area = self.getAreaMaster()
            boss = BackendApi.get_boss(model_mgr, area.boss, using=settings.DB_READONLY)
            self.__bossmaster = boss
        return self.__bossmaster
    
    def getAreaPlayData(self, using=settings.DB_READONLY):
        """エリアプレイ情報.
        """
        return self.callFunctionByFromPage('_getAreaPlayData', using)
    
    def makeAreaObj(self, areamaster, playdata=None):
        """エリア情報作成.
        """
        return self.callFunctionByFromPage('_makeAreaObj', areamaster, playdata=None)
    
    def makeBossObj(self, bossmaster, hp=None):
        """ボス情報作成.
        """
        return Objects.boss(self, bossmaster, hp)
    
    def checkBossBattleAble(self, model_mgr, using=settings.DB_READONLY):
        """エリアのボスと戦えるかを確認.
        """
        return self.callFunctionByFromPage('_checkBossBattleAble', model_mgr, using)
    
    def getDeck(self):
        """デッキ取得.
        """
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        deck = BackendApi.get_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
        return deck
    
    def getDeckLeader(self):
        """デッキのカード取得.
        """
        model_mgr = self.getModelMgr()
        deck = self.getDeck()
        cardlist = BackendApi.get_cards([deck.leader], model_mgr, using=settings.DB_READONLY)
        return cardlist[0]
    
    def getDeckCardList(self):
        """デッキのカード取得.
        """
        model_mgr = self.getModelMgr()
        deck = self.getDeck()
        cardidlist = deck.to_array()
        cardlist = BackendApi.get_cards(cardidlist, model_mgr, using=settings.DB_READONLY)
        return cardlist
    
    def getPowerTotal(self):
        """デッキの総接客力.
        """
        cardlist = self.getDeckCardList()
        power_total = 0
        for card in cardlist:
            power_total += card.power
        return power_total
    
    def putDeckInfoParams(self):
        # デッキのカード.
        cardlist = self.getDeckCardList()
        obj_cardlist = []
        cost_total = 0
        power_total = 0
        for card in cardlist:
            obj_card = Objects.card(self, card)
            power_total += obj_card['power']
            cost_total += card.master.cost
            obj_cardlist.append(obj_card)
        self.html_param['cardlist'] = obj_cardlist
        self.html_param['cost_total'] = cost_total
        self.html_param['power_total'] = power_total
    
    #===================================================================
    # 通常のスカウト.
    def _getAreaMaster_SCOUT(self, areaid):
        model_mgr = self.getModelMgr()
        area = BackendApi.get_area(model_mgr, areaid, using=settings.DB_READONLY)
        return area
    
    def _getAreaPlayData_SCOUT(self, using):
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        area = self.getAreaMaster()
        return BackendApi.get_areaplaydata(model_mgr, v_player.id, [area.id], using=using)
    
    def _checkBossBattleAble_SCOUT(self, model_mgr, using):
        v_player = self.getViewerPlayer()
        
        area = self.getAreaMaster()
        if area is None:
            return False
        
        # エリアクリア済みだと戦えない.
        playdata = BackendApi.get_areaplaydata(model_mgr, v_player.id, [area.id], using=using).get(area.id, None)
        if playdata:
            return False
        
        # エリアのスカウトを全てクリアしていないといけない.
        if not BackendApi.check_areascout_allcleared(model_mgr, v_player.id, area.id, using=using):
            return False
            
        return True
    
    def _makeAreaObj_SCOUT(self, areamaster, playdata=None):
        return Objects.area(self, areamaster, playdata)
    
    def redirectToScoutTop_SCOUT(self):
        url = UrlMaker.scout()
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    #===================================================================
    # スカウトイベント.
    def _getAreaMaster_SCOUTEVENT(self, areaid):
        model_mgr = self.getModelMgr()
        stage = BackendApi.get_event_stage(model_mgr, areaid, using=settings.DB_READONLY)
        return stage
    
    def _getAreaPlayData_SCOUTEVENT(self, using):
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        area = self.getAreaMaster()
        return BackendApi.get_event_playdata(model_mgr, area.eventid, v_player.id, using=using)
    
    def _checkBossBattleAble_SCOUTEVENT(self, model_mgr, using):
        v_player = self.getViewerPlayer()
        
        stage = self.getAreaMaster()
        if stage is None:
            return False
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=using)
        if eventmaster is None:
            return False
        playdata = BackendApi.get_event_playdata(model_mgr, eventmaster.id, v_player.id, using)
        if playdata is None:
            return False
        
        return BackendApi.check_event_boss_playable(playdata, stage)
    
    def _makeAreaObj_SCOUTEVENT(self, areamaster, playdata=None):
        return Objects.scoutevent_stage(self, areamaster, playdata)
    
    def redirectToScoutTop_SCOUTEVENT(self):
        url = UrlMaker.scoutevent_top()
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    #===================================================================
    # レイドイベント.
    def _getAreaMaster_RAIDEVENTSCOUT(self, areaid):
        model_mgr = self.getModelMgr()
        stage = BackendApi.get_raidevent_stagemaster(model_mgr, areaid, using=settings.DB_READONLY)
        return stage
    
    def _getAreaPlayData_RAIDEVENTSCOUT(self, using):
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        area = self.getAreaMaster()
        return BackendApi.get_raideventstage_playdata(model_mgr, area.eventid, v_player.id, using=using)
    
    def _checkBossBattleAble_RAIDEVENTSCOUT(self, model_mgr, using):
        v_player = self.getViewerPlayer()
        
        stage = self.getAreaMaster()
        if stage is None:
            return False
        eventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=using)
        if eventmaster is None:
            return False
        playdata = BackendApi.get_raideventstage_playdata(model_mgr, eventmaster.id, v_player.id, using)
        if playdata is None:
            return False
        
        return BackendApi.check_event_boss_playable(playdata, stage)
    
    def _makeAreaObj_RAIDEVENTSCOUT(self, areamaster, playdata=None):
        v_player = self.getViewerPlayer()
        if playdata:
            stagenumber = playdata.stage
            progress = playdata.progress
            confirmkey = playdata.req_confirmkey
        else:
            stagenumber = areamaster.stage
            progress = 0
            confirmkey = ''
        return Objects.raidevent_stage(self, v_player, stagenumber, areamaster, progress, confirmkey)
    
    def redirectToScoutTop_RAIDEVENTSCOUT(self):
        url = UrlMaker.raidevent_top()
        self.appRedirect(self.makeAppLinkUrlRedirect(url))

    # ===================================================================
    # プロデュースイベント.
    def _getAreaMaster_PRODUCEEVENT(self, areaid):
        """単純に_getAreaMaster_PRODUCEEVENTSCOUTを呼ぶ
        """
        return self._getAreaMaster_PRODUCEEVENTSCOUT(areaid)

    def _getAreaMaster_PRODUCEEVENTSCOUT(self, areaid):
        model_mgr = self.getModelMgr()
        stage = BackendApi.get_produceevent_stagemaster(model_mgr, areaid, using=settings.DB_READONLY)
        return stage

    def _getAreaPlayData_PRODUCEEVENT(self, using):
        return self._getAreaPlayData_PRODUCEEVENTSCOUT(using)

    def _getAreaPlayData_PRODUCEEVENTSCOUT(self, using):
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        area = self.getAreaMaster()
        return BackendApi.get_produceeventstage_playdata(model_mgr, area.eventid, v_player.id, using=using)

    def _checkBossBattleAble_PRODUCEEVENT(self, model_mgr, using):
        return self._checkBossBattleAble_PRODUCEEVENTSCOUT(model_mgr, using)

    def _checkBossBattleAble_PRODUCEEVENTSCOUT(self, model_mgr, using):
        v_player = self.getViewerPlayer()

        stage = self.getAreaMaster()
        if stage is None:
            return False
        eventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=using)
        if eventmaster is None:
            return False
        playdata = BackendApi.get_produceeventstage_playdata(model_mgr, eventmaster.id, v_player.id, using)
        if playdata is None:
            return False

        return BackendApi.check_event_boss_playable(playdata, stage)

    def _makeAreaObj_PRODUCEEVENT(self, areamaster, playdata=None):
        return self._makeAreaObj_PRODUCEEVENTSCOUT(areamaster, playdata)

    def _makeAreaObj_PRODUCEEVENTSCOUT(self, areamaster, playdata=None):
        v_player = self.getViewerPlayer()
        if playdata:
            stagenumber = playdata.stage
            progress = playdata.progress
            confirmkey = playdata.req_confirmkey
        else:
            stagenumber = areamaster.stage
            progress = 0
            confirmkey = ''
        return Objects.produceevent_stage(self, v_player, stagenumber, areamaster, progress, confirmkey)

    def redirectToScoutTop_PRODUCEEVENT(self):
        return self.redirectToScoutTop_PRODUCEEVENTSCOUT()

    def redirectToScoutTop_PRODUCEEVENTSCOUT(self):
        url = UrlMaker.produceevent_top()
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
