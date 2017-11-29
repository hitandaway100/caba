# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.test.pc.base import PcTestBase

class ApiTest(PcTestBase):
    """宝箱一覧.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER, Defines.ItemEffect.ACTION_ALL_RECOVERY)
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        
        TREASURETYPE_TABLE = {
            Defines.TreasureType.GOLD : (DummyType.TREASURE_GOLD_MASTER, DummyType.TREASURE_GOLD),
            Defines.TreasureType.SILVER : (DummyType.TREASURE_SILVER_MASTER, DummyType.TREASURE_SILVER),
            Defines.TreasureType.BRONZE : (DummyType.TREASURE_BRONZE_MASTER, DummyType.TREASURE_BRONZE),
        }
        # 宝箱のマスター.
        MASTER_TABLE = (
            # (itype, ivalue1, ivalue2).
            (Defines.ItemType.GOLD, 0, 1),
            (Defines.ItemType.GACHA_PT, 0, 1),
            (Defines.ItemType.ITEM, itemmaster.id, 1),
            (Defines.ItemType.CARD, cardmaster.id, 1),
            (Defines.ItemType.GACHATICKET, 0, 1),
            (Defines.ItemType.TRYLUCKTICKET, 0, 1),
            (Defines.ItemType.MEMORIESTICKET, 0, 1),
        )
        
        for treasure_type in Defines.TreasureType.NAMES.keys():
            dummy_type_master, dummy_type_model = TREASURETYPE_TABLE[treasure_type]
            for itype, ivalue1, ivalue2 in MASTER_TABLE:
                treasuremaster = self.create_dummy(dummy_type_master, itype, ivalue1, ivalue2)
                self.create_dummy(dummy_type_model, self.__player.id, treasuremaster.id)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_CTYPE:Defines.TreasureType.GOLD,
        }
    
    def check(self):
        self.checkResponseStatus()
        
        keys = (
            'overlimit',
            'is_openable',
            'treasure_name',
            'treasure_nums',
            'treasurelist',
            'treasure_item_list',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
