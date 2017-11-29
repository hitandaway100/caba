# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines

class ApiTest(ApiTestBase):
    """ショップTop.
    """
    def setUp(self):
        # アイテム.
        item = self.create_dummy(DummyType.ITEM_MASTER)
        
        # 商品.
        shopitem = self.create_dummy(DummyType.SHOP_ITEM_MASTER, Defines.ItemType.ITEM, item.id, 1)
        self.__shopitem = shopitem
        
        # プレイヤー.
        self.__player = self.create_dummy(DummyType.PLAYER)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def check(self):
        keys = (
            'player',
            'shopitemlist',
            'num_key',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
