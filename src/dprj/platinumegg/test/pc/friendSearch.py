# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.pc.base import PcTestBase
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Player import PlayerFriend

class ApiTest(PcTestBase):
    """フレンド候補検索.
    """
    def setUp(self):
        def saveLogin(player):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_updatelogintime(model_mgr, player, True)
            model_mgr.write_all()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        model = self.__player0.getModel(PlayerFriend)
        model.friendlimit = 30
        model.save()
        saveLogin(self.__player0)
        
        def addRequest(v_player, o_player):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_friendrequest(model_mgr, v_player, o_player)
            model_mgr.write_all()
            model_mgr.write_end()
        
        for _ in xrange(10):
            player = self.create_dummy(DummyType.PLAYER)
            addRequest(self.__player0, player)
            saveLogin(player)
        
        for _ in xrange(10):
            player = self.create_dummy(DummyType.PLAYER)
            saveLogin(player)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        self.checkResponseStatus()
        
        keys = (
            'playerlist',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
    
