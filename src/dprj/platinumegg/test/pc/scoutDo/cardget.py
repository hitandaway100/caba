# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerGold,\
    PlayerDeck
from platinumegg.app.cabaret.models.Scout import ScoutPlayData
from defines import Defines
from platinumegg.app.cabaret.util.scout import ScoutDropItemData
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.test.pc.base import PcTestBase

class ApiTest(PcTestBase):
    """スカウト実行(カード獲得).
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # ボス.
        boss = self.create_dummy(DummyType.BOSS_MASTER)
        # エリア.
        area = self.create_dummy(DummyType.AREA_MASTER, bossid=boss.id)
        
        # カード.
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        data = ScoutDropItemData.create(Defines.ItemType.CARD, cardmaster.id, filters={'ptype':Defines.CharacterType.TYPE_001}, rate=10000)
        dropitems = [data.get_dropitem_dict()]
        self.__cardmaster = cardmaster
        
        # スカウト.
        scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area, execution=100, dropitems=dropitems)
        self.__scout = scout
        for _ in xrange(5):
            scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area, opencondition=scout.id)
        
        # 経験値情報.
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 1, exp=0)
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 2, exp=999)
        self.__player0.level = 1
        self.__player0.exp = 0
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
        elif playdata.progress == 0:
            raise AppTestError(u'進行度が進んでいない')
        
        # 報酬.
        resultlist = playdata.result.get('result', None)
        if not resultlist:
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
        
        # カード獲得のイベントが設定されているか.
        targetevent = BackendApi.find_scout_event(playdata, Defines.ScoutEventType.GET_CARD)
        if targetevent is None:
            raise AppTestError(u'カード獲得イベントが設定されていない')
        elif targetevent.card != self.__cardmaster.id:
            raise AppTestError(u'カード獲得イベントに正しくカードが設定されていない.%d vs %d' % (targetevent.card, self.__cardmaster.id))
        elif targetevent.is_received:
            raise AppTestError(u'カード受取判定済になってしまっている')
