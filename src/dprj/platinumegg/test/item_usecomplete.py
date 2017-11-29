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
            self.__item = self.create_dummy(DummyType.ITEM, self.__player, self.__itemmaster)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def get_urlargs(self):
        num = self.__item.rnum + self.__item.vnum
        return '/%s/%s/%s/%s/%s/%s' % (self.__itemmaster.id, 0, num, num, 0, 10)
    
    def check(self):
        keys = (
            'mid',
            'is_duplicate',
            'is_not_enough',
            'before_num',
            'after_num',
            'difference_value',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
