# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.test.pc.treasureOpen import PcTreasureGetApiTestBase

class ApiTest(PcTreasureGetApiTestBase):
    """宝箱開封(銀の宝箱 思い出チケット).
    """
    @classmethod
    def get_treasure_type(cls):
        return Defines.TreasureType.SILVER
    @classmethod
    def get_treasure_itemtype(cls):
        return Defines.ItemType.MEMORIESTICKET
    

