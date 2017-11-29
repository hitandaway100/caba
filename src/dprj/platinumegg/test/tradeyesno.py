# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines

class ApiTest(ApiTestBase):
    """宝箱一覧.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__trade = self.create_dummy(DummyType.TRADE_MASTER, Defines.ItemType.TRYLUCKTICKET, 0, 1, 1, 1)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def get_urlargs(self):
        return '/%d' % (self.__trade.id)
    
    def check(self):
        keys = (
            'tradedata',
            'url_trade',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
