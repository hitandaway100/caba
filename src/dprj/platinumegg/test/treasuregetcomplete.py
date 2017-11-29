# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines

class ApiTest(ApiTestBase):
    """アイテム.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        # Item関連
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER, mid=Defines.ItemEffect.ACTION_ALL_RECOVERY)
        self.__treasuremaster =  self.create_dummy(DummyType.TREASURE_GOLD_MASTER, Defines.ItemType.ITEM, itemmaster.id, 10)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def get_urlargs(self):
        return '/%d/%d' % (Defines.TreasureType.GOLD, self.__treasuremaster.id)
    
    def check(self):
        keys = (
            'treasurekey',
            'treasure_get_data_list',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
