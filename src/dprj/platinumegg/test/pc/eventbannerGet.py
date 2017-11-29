# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.pc.base import PcTestBase

class ApiTest(PcTestBase):
    """イベントバナー.
    """
    
    def setUp(self):
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        # お知らせ.
        for _ in range(20):
            self.create_dummy(DummyType.EVENT_BANNER_MASTER)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        self.checkResponseStatus()
        
        keys = (
            'eventbanners',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
    
