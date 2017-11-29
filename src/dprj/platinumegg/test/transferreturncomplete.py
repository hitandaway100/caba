# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines

class ApiTest(ApiTestBase):
    """呼び戻す完了.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        self.__cardmaster = self.create_dummy(DummyType.CARD_MASTER, rare=Defines.Rarity.TRANSFER[0])
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return '/%s/%s/' % (self.__cardmaster.id, 10)
    
    def check(self):
        keys = (
            'url_albumdetail',
            'cardmaster',
            'cardnum',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
