# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.test.pc.treasureOpen import PcTreasureGetApiTestBase

class ApiTest(PcTreasureGetApiTestBase):
    """宝箱開封(金の宝箱 引抜Pt).
    """
    @classmethod
    def get_treasure_type(cls):
        return Defines.TreasureType.GOLD
    @classmethod
    def get_treasure_itemtype(cls):
        return Defines.ItemType.GACHA_PT
    

