# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerFriend
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """仲間検索.
    """
    
    def setUp(self):
        def saveLogin(player):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_updatelogintime(model_mgr, player, False)
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
        keys = (
            'friendnum',
            'friendnummax',
            'playerlist',
            'url_reload',
            'LevelGroup',
            Defines.URLQUERY_LEVELGROUP,
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
