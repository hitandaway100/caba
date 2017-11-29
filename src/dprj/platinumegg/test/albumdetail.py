# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType

class ApiTest(ApiTestBase):
    """カード詳細.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        self.create_dummy(DummyType.MEMORIES_MASTER, id=self.__cardmaster.id)
        self.create_dummy(DummyType.CARD, self.__player, self.__cardmaster)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def get_urlargs(self):
        return '/%s' % int(self.__cardmaster.albumhklevel >> 32)
    
    def check(self):
        keys = (
            'card',
            'memories_list',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
