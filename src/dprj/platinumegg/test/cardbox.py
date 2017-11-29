# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines

class ApiTest(ApiTestBase):
    """カードBOX.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        for _ in xrange(20):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            self.create_dummy(DummyType.CARD, self.__player, cardmaster)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def check(self):
        keys = (
            'cardlist',
            'ctype_items',
            'sort_items',
            'url_page_next',
            'url_protect',
            'url_sell',
            Defines.URLQUERY_CTYPE,
            Defines.URLQUERY_SORTBY,
            Defines.URLQUERY_PAGE,
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
