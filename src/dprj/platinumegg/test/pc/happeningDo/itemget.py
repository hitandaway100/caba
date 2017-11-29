# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerGold,\
    PlayerHappening
from defines import Defines
from platinumegg.app.cabaret.util.scout import ScoutDropItemData
from platinumegg.test.pc.base import PcTestBase
from platinumegg.app.cabaret.models.Happening import Happening

class ApiTest(PcTestBase):
    """ハプニング実行(アイテム獲得).
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        items = []
        
        # アイテム.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER)
        data = ScoutDropItemData.create(Defines.ItemType.ITEM, itemmaster.id, filters={'ptype':Defines.CharacterType.TYPE_001}, rate=10000)
        items.append(data.get_dropitem_dict())
        self.__itemmaster = itemmaster
        
        # レイド.
        raidmaster = self.create_dummy(DummyType.RAID_MASTER)
        
        # ハプニング.
        happeningmaster = self.create_dummy(DummyType.HAPPENING_MASTER, raidmaster.id, items=items)
        self.__happeningmaster = happeningmaster
        
        # ハプニング情報.
        happening = self.create_dummy(DummyType.HAPPENING, self.__player0.id, self.__happeningmaster.id)
        self.__happening = happening
        
        # 経験値情報.
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 1, exp=0)
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 2, exp=999)
        self.__player0.level = 1
        self.__player0.exp = 0
        self.__player0.getModel(PlayerExp).save()
        
        self.__player0.gold = 0
        self.__player0.getModel(PlayerGold).save()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        self.checkResponseStatus()
        
        # 進行情報があるかを確認.
        happening = Happening.getByKey(self.__happening.id)
        playerhappening = PlayerHappening.getByKey(self.__player0.id)
        
        if happening is None or happening.progress == 0:
            raise AppTestError(u'進行情報が保存されていない')
        
        # 報酬.
        resultlist = playerhappening.happening_result.get('result', None)
        if resultlist is None:
            raise AppTestError(u'結果が設定されていない')
        
        gold_add = 0
        for result in resultlist:
            self.__player0.exp += result['exp_add']
            gold_add += result['gold_add']
        
        # お金確認.
        if happening.gold != gold_add:
            raise AppTestError(u'お金が正しくない')
        
        # 経験値.
        playerexp = PlayerExp.getByKey(self.__player0.id)
        if playerexp.exp != self.__player0.exp:
            raise AppTestError(u'お金が正しくない')
        
        # イベント設定されているか.
        eventlist = playerhappening.happening_result.get('event', None)
        if not eventlist:
            raise AppTestError(u'イベントが設定されていない')
        
        # アイテム獲得のイベントが設定されているか.
        targetevent = None
        for event in eventlist:
            if event.get_type() == Defines.ScoutEventType.GET_ITEM:
                targetevent = event
        if targetevent is None:
            raise AppTestError(u'アイテム獲得が設定されていない')
        elif targetevent.item != self.__itemmaster.id:
            raise AppTestError(u'イベントのアイテムIDが正しくない')
        
        # 報酬リストにアイテムが入っているか.
        if not happening.idDropped(Defines.ItemType.ITEM, self.__itemmaster.id):
            raise AppTestError(u'報酬リストにアイテムが設定されていない')
