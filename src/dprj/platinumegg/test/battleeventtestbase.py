# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from defines import Defines
from platinumegg.app.cabaret.models.Card import Deck
from platinumegg.app.cabaret.models.Player import PlayerDeck
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.redisbattleevent import BattleEventRevengeSet

class BattleEventApiTestBase(ApiTestBase):
    """バトルイベントテストのベース.
    """
    
    def setUp(self):
        self.__preconfig_mid = None
        self.__preconfig_starttime = None
        self.__preconfig_endtime = None
        self.__preconfig_ependtime = None
        self.__eventmaster = None
        self.__eventrankmasters = {}
        self.setUp2()
        
    def setUp2(self):
        pass
    
    def setUpEvent(self, eventmaster_kwargs=None, model_mgr=None, is_open=True, opening=True):
        
        # シナリオ.
        scenario = self.create_dummy(DummyType.EVENT_SCENARIO_MASTER)
        
        # イベントマスター.
        eventmaster_kwargs = eventmaster_kwargs or {}
        eventmaster_kwargs.update(op=scenario.number, ed=scenario.number)
        eventmaster = self.create_dummy(DummyType.BATTLE_EVENT_MASTER, **eventmaster_kwargs)
        self.__eventmaster = eventmaster
        
        # イベント発生中設定.
        model_mgr = model_mgr or ModelRequestMgr()
        
        if is_open:
            stime = OSAUtil.get_datetime_min()
            etime = OSAUtil.get_datetime_max()
        else:
            stime = OSAUtil.get_datetime_min()
            etime = stime
        
        config = BackendApi.get_current_battleeventconfig(model_mgr)
        self.__preconfig_mid = config.mid
        self.__preconfig_starttime = config.starttime
        self.__preconfig_endtime = config.endtime
        self.__preconfig_ependtime = config.epilogue_endtime
        BackendApi.update_battleeventconfig(eventmaster.id, stime, etime, OSAUtil.get_datetime_max())
        
        return eventmaster
    
    def setOpeningViewTime(self, uid, opvtime=None):
        BackendApi.update_battleevent_flagrecord(self.__eventmaster.id, uid, opvtime=opvtime or OSAUtil.get_now())
    
    def setLoginBonusReceived(self, uid):
        try:
            model_mgr = ModelRequestMgr()
            BackendApi.tr_battleevent_receive_loginbonus(model_mgr, self.__eventmaster, uid, OSAUtil.get_now())
            model_mgr.write_all()
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
    
    def createRankMaster(self, rank=1, params=None):
        master = self.__eventrankmasters.get(rank)
        if master is None:
            params = params or {}
            master = self.__eventrankmasters[rank] = self.create_dummy(DummyType.BATTLE_EVENT_RANK_MASTER, self.__eventmaster.id, rank, **params)
        return master
    
    def joinRank(self, uid):
        model_mgr = ModelRequestMgr()
        config = BackendApi.get_current_battleeventconfig(model_mgr)
        BackendApi.tr_battleevent_regist_group_for_user(model_mgr, config, self.__eventmaster, uid, 1, self.__eventrankmasters.values())
        model_mgr.write_all()
        model_mgr.write_end()
    
    def addRankLog(self, rankrecord, rankmaster, cdate):
        return self.create_dummy(DummyType.BATTLE_EVENT_GROUP_LOG, rankrecord, rankmaster.rank, cdate=cdate)
    
    def createRevenge(self, uid, oid):
        model_mgr = ModelRequestMgr()
        ins = BackendApi.tr_update_battleevent_revenge(model_mgr, uid, oid)
        model_mgr.write_all()
        model_mgr.write_end()
        
        redisdb = BattleEventRevengeSet.getDB()
        redisdb.delete(BattleEventRevengeSet.makeKey(uid))
        
        return ins
    
    def makePlayer(self, power):
        player = self.create_dummy(DummyType.PLAYER)
        player.deckcapacitylv = 999
        player.getModel(PlayerDeck).save()
        
        # デッキ.
        deck = Deck(id=player.id)
        
        arr = []
        for _ in xrange(Defines.DECK_CARD_NUM_MAX - 3):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER, basepower=power, maxpower=power)
            card = self.create_dummy(DummyType.CARD, player, cardmaster)
            arr.append(card.id)
        deck.set_from_array(arr)
        deck.save()
        
        return player
    
    def makePresentMaster(self, eventid, number, point=1, special_conditions=None, rate=1):
        """贈り物マスター作成.
        """
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100)
        
        # 中身.
        content = self.create_dummy(DummyType.BATTLE_EVENT_PRESENT_CONTENT_MASTER, prizes=[prize.id])
        
        # 贈り物.
        contents = [[content.id,1]]
        master = self.create_dummy(DummyType.BATTLE_EVENT_PRESENT_MASTER, eventid=eventid, number=number, contents=contents, point=point, rate=rate, special_conditions=special_conditions)
        
        return master
    
    def makePresentData(self, uid, eventid, point=0, cur_presentmaster=None, prev_presentmaster=None):
        """贈り物獲得ポイント情報.
        """
        currentnum = cur_presentmaster.number if cur_presentmaster else 0
        currentcontent = cur_presentmaster.contents[0][0] if cur_presentmaster and cur_presentmaster.contents else 0
        prenum = prev_presentmaster.number if prev_presentmaster else 0
        precontent = prev_presentmaster.contents[0][0] if prev_presentmaster and prev_presentmaster.contents else 0
        model = self.create_dummy(DummyType.BATTLE_EVENT_PRESENT_DATA, uid, eventid, point=point, currentnum=currentnum, currentcontent=currentcontent, prenum=prenum, precontent=precontent)
        return model
    
    def makePresentCount(self, presentmaster, uid, cnt=0):
        """贈り物出現回数.
        """
        model = self.create_dummy(DummyType.BATTLE_EVENT_PRESENT_COUNTS, uid, presentmaster.number, cnt=cnt)
        return model
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def finish(self):
        if self.__preconfig_mid is not None:
            BackendApi.update_battleeventconfig(self.__preconfig_mid, self.__preconfig_starttime, self.__preconfig_endtime, self.__preconfig_ependtime)
