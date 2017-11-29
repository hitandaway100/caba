# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.pc.base import PcTestBase
from defines import Defines

class ApiTest(PcTestBase):
    """プレイヤー情報.
    """
    
    def setUp(self):
        uidlist = []
        
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        uidlist.append(self.__player.id)
        
        for _ in xrange(5):
            uidlist.append(self.create_dummy(DummyType.PLAYER).id)
        self.__uidlist = uidlist
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_ID:','.join([str(uid) for uid in self.__uidlist]),
        }
        return params
    
    def check(self):
        self.checkResponseStatus()
        
        keys = (
            'playerlist',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
    
