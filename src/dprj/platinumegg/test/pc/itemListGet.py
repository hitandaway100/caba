# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.test.pc.base import PcTestBase

class ApiTest(PcTestBase):
    """アイテム.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        for effect in Defines.ItemEffect.NAMES.keys():
            itemmaster = self.create_dummy(DummyType.ITEM_MASTER, mid=effect)
            self.create_dummy(DummyType.ITEM, self.__player, itemmaster)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def check(self):
        self.checkResponseStatus()
        
        keys = (
            'item_list',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
