# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.pc.base import PcTestBase
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Player import PlayerFriend
from defines import Defines
from platinumegg.app.cabaret.models.Friend import Friend

class ApiTest(PcTestBase):
    """フレンド申請承認.
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
        addRequest(self.__player1, self.__player0)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
            Defines.URLQUERY_ID : self.__player1.id,
            Defines.URLQUERY_ACCEPT : 1,
        }
        return params
    
    def check(self):
        self.checkResponseStatus()
        
        uid = self.__player0.id
        fid = self.__player1.id
        for _uid, _fid in ((uid, fid), (fid, uid)):
            model = Friend.getByKey(Friend.makeID(_uid, _fid))
            if model is None or model.state != Defines.FriendState.ACCEPT:
                raise AppTestError(u'フレンドになっていない')
