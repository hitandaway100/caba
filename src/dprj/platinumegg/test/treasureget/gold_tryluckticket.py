# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.test.treasureget import TreasureGetApiTestBase

class ApiTest(TreasureGetApiTestBase):
    """宝箱開封(金の宝箱 運試しチケット).
    """
    @classmethod
    def get_treasure_type(cls):
        return Defines.TreasureType.GOLD
    @classmethod
    def get_treasure_itemtype(cls):
        return Defines.ItemType.TRYLUCKTICKET
    

