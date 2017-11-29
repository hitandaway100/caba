# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines

class ApiTest(ApiTestBase):
    """カード売却完了.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_CARD_NUM:1,
            Defines.URLQUERY_GOLDPRE:2,
            Defines.URLQUERY_GOLDADD:3,
            Defines.URLQUERY_GOLD:5,
            Defines.URLQUERY_CABAKING:5,
            Defines.URLQUERY_CABAKINGPRE:1,
        }
    
    def check(self):
        keys = (
            Defines.URLQUERY_CARD_NUM,
            Defines.URLQUERY_GOLDPRE,
            Defines.URLQUERY_GOLDADD,
            Defines.URLQUERY_GOLD,
            Defines.URLQUERY_CABAKING,
            Defines.URLQUERY_CABAKINGPRE,
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
