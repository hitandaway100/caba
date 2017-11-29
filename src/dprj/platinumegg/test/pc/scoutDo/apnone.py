# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerGold,\
    PlayerDeck
from platinumegg.app.cabaret.models.Scout import ScoutPlayData
from defines import Defines
from platinumegg.test.pc.base import PcTestBase

class ApiTest(PcTestBase):
    """スカウト実行(体力不足).
    """
    
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # ボス.
        boss = self.create_dummy(DummyType.BOSS_MASTER)
        # エリア.
        area = self.create_dummy(DummyType.AREA_MASTER, bossid=boss.id)
        
        # スカウト.
        scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area, execution=100, apcost=100)
        self.__scout = scout
        for _ in xrange(5):
            scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area, opencondition=scout.id)
        
        # 経験値情報.
        for i in xrange(Defines.BIGINNER_PLAYERLEVEL):
            self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, i+1, exp=i+1)
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, Defines.BIGINNER_PLAYERLEVEL+1, exp=999)
        self.__player0.level = Defines.BIGINNER_PLAYERLEVEL
        self.__player0.exp = Defines.BIGINNER_PLAYERLEVEL
        self.__player0.getModel(PlayerExp).save()
        
        self.__player0.gold = 0
        self.__player0.getModel(PlayerGold).save()
        
        self.__player0.cardlimititem = 100
        self.__player0.getModel(PlayerDeck).save()
        
        # 途中まで進んでいるかもしれないので消しておく.
        playdata = ScoutPlayData.getByKey(ScoutPlayData.makeID(self.__player0.id, self.__scout.id))
        if playdata:
            playdata.delete()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
            Defines.URLQUERY_SCOUT:self.__scout.id,
        }
    
    def check(self):
        self.checkResponseStatus()
        
        # 進行情報があるかを確認.
        playdata = ScoutPlayData.getByKey(ScoutPlayData.makeID(self.__player0.id, self.__scout.id))
        if playdata is None:
            raise AppTestError(u'進行情報が保存されていない')
        
        # 報酬.
        resultlist = playdata.result.get('result', None)
        if resultlist is None:
            raise AppTestError(u'結果が設定されていない')
        
        for result in resultlist:
            self.__player0.exp += result['exp_add']
            self.__player0.gold += result['gold_add']
        
        # お金確認.
        playergold = PlayerGold.getByKey(playdata.uid)
        if playergold.gold != self.__player0.gold:
            raise AppTestError(u'お金が正しくない')
        
        # 経験値.
        playerexp = PlayerExp.getByKey(playdata.uid)
        if playerexp.exp != self.__player0.exp:
            raise AppTestError(u'お金が正しくない')
        
        # イベント設定されているか.
        eventlist = playdata.result.get('event', None)
        if not eventlist:
            raise AppTestError(u'イベントが設定されていない')
        
        # 体力不足のイベントが設定されているか.
        targetevent = None
        for event in eventlist:
            if event.get_type() == Defines.ScoutEventType.AP_NONE:
                targetevent = event
        if targetevent is None:
            raise AppTestError(u'体力不足イベントが設定されていない')
