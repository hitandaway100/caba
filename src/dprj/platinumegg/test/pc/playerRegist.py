# -*- coding: utf-8 -*-
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.pc.base import PcTestBase
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.base import AppTestError
from platinumegg.app.cabaret.models.Player import PlayerRegist
from platinumegg.test.dummy_factory import DummyType

class ApiTest(PcTestBase):
    """ユーザー登録.
    """
    CHARACTER_TYPE = Defines.CharacterType.TYPE_002
    
    def setUp(self):
        self.__player = self.create_dummy(DummyType.PLAYER, regist=False)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_CTYPE:ApiTest.CHARACTER_TYPE,
        }
        return params
    
    def check(self):
        self.checkResponseStatus()
        
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_players(None, [self.__player.id], [PlayerRegist], model_mgr=model_mgr)[0]
        if player.ptype != ApiTest.CHARACTER_TYPE:
            raise AppTestError(u'タイプが正しくない')
