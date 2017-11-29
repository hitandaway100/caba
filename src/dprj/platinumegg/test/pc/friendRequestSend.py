# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.pc.base import PcTestBase
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerFriend
from platinumegg.app.cabaret.models.Friend import Friend

class ApiTest(PcTestBase):
    """フレンド申請送信.
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
        self.__playeridlist = [createPlayer().id for _ in xrange(Defines.FRIEND_PAGE_CONTENT_NUM)]
        self.__str_playeridlist = ','.join([str(fid) for fid in self.__playeridlist])
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
            Defines.URLQUERY_USERID : self.__str_playeridlist,
        }
        return params
    
    def check(self):
        self.checkResponseStatus()
        
        uid = self.__player0.id
        for fid in self.__playeridlist:
            for _uid, _fid, _state in ((uid, fid, Defines.FriendState.SEND), (fid, uid, Defines.FriendState.RECEIVE)):
                model = Friend.getByKey(Friend.makeID(_uid, _fid))
                if model is None or model.state != _state:
                    raise AppTestError(u'レコードが作成されていない')
