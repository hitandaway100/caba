# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerFriend
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Friend import Friend

class ApiTest(ApiTestBase):
    """仲間から外す書き込み.
    """
    
    def setUp(self):
        def createPlayer():
            player = self.create_dummy(DummyType.PLAYER)
            model = player.getModel(PlayerFriend)
            model.friendlimit = 30
            model.save()
            return player
        
        # Player.
        self.__player0 = createPlayer()
        self.__player1 = createPlayer()
        
        def addRequest(v_player, o_player):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_friendrequest(model_mgr, v_player, o_player)
            model_mgr.write_all()
            model_mgr.write_end()
        def addFriend(v_player, o_player):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_friend(model_mgr, o_player.id, v_player.id)
            model_mgr.write_all()
            model_mgr.write_end()
        addRequest(self.__player0, self.__player1)
        addFriend(self.__player0, self.__player1)
        
    
    def get_urlargs(self):
        return '/do/%s' % self.__player1.id
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        uid = self.__player0.id
        fid = self.__player1.id
        for _uid, _fid in ((uid, fid), (fid, uid)):
            model = Friend.getByKey(Friend.makeID(_uid, _fid))
            if model is not None:
                raise AppTestError(u'レコードが残っている')
