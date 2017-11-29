# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """あいさつ完了.
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        self.__player1 = self.create_dummy(DummyType.PLAYER)
        
        model_mgr = ModelRequestMgr()
        BackendApi.tr_greet(model_mgr, self.__player0.id, self.__player1.id, False)
        model_mgr.write_all()
        model_mgr.write_end()
        
        self.__logid = BackendApi.get_greetlog_last(model_mgr, self.__player0.id, self.__player1.id).id
    
    def get_urlargs(self):
        return '/%s/%s/%s/%s/%s' % (self.__player1.id, CabaretError.Code.OK, 0, Defines.GREET_GACHA_PT, self.__logid)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        keys = (
            'is_duplicate',
            'is_overlimit',
            'gacha_pt_pre',
            'gacha_pt_post',
            'gacha_pt_add',
            'url_profile',
            'person',
        )
        for k in keys:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない' % k)
