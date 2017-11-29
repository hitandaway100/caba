# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerFriend, PlayerExp
from defines import Defines
from platinumegg.app.cabaret.models.Friend import Friend
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """仲間申請書き込み.
    """
    
    def setUp(self):
        def createPlayer():
            player = self.create_dummy(DummyType.PLAYER)
            
            model_mgr = ModelRequestMgr()
            model = player.getModel(PlayerFriend)
            model.friendlimit = 30
            model_mgr.set_save(model)
            model = player.getModel(PlayerExp)
            model.level = 1
            model_mgr.set_save(model)
            BackendApi.tr_updatelogintime(model_mgr, player, False)
            model_mgr.write_all()
            model_mgr.write_end()
            
            return player
        # Player.
        self.__player0 = createPlayer()
        self.__playeridlist = [createPlayer().id for _ in xrange(10)]
    
    def get_urlargs(self):
        return '/auto'
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        keys = (
            Defines.URLQUERY_USERID,
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
