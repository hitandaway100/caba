# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.test.treasureget import TreasureGetApiTestBase

class ApiTest(TreasureGetApiTestBase):
    """宝箱開封(銀の宝箱 カード).
    """
    @classmethod
    def get_treasure_type(cls):
        return Defines.TreasureType.SILVER
    @classmethod
    def get_treasure_itemtype(cls):
        return Defines.ItemType.CARD
    

