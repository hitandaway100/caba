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
        for effect in Defines.ItemEffect.NAMES.keys():
            self.__itemmaster = self.create_dummy(DummyType.ITEM_MASTER, mid=effect)
            self.create_dummy(DummyType.ITEM, self.__player, self.__itemmaster, rnum=1, vnum=1)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_NUMBER:1,
        }
    
    def get_urlargs(self):
        return '/%s' % (self.__itemmaster.id)
    
    def check(self):
        keys = (
            'item',
            'url_use',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
