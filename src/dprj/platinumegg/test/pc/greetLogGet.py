# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.pc.base import PcTestBase
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi

class ApiTest(PcTestBase):
    """あいさつ履歴.
    """
    
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        uid = self.__player.id
        
        for _ in xrange(16):
            o_player = self.create_dummy(DummyType.PLAYER)
            oid = o_player.id
            model_mgr = ModelRequestMgr()
            BackendApi.tr_greet(model_mgr, oid, uid, False)
            model_mgr.write_all()
            model_mgr.write_end()
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        self.checkResponseStatus()
        
        keys = (
            'greetlog_list',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
    
