# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerFriend
from defines import Defines
from platinumegg.app.cabaret.models.Friend import Friend

class ApiTest(ApiTestBase):
    """仲間申請書き込み.
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
    
    def get_urlargs(self):
        return '/do'
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
            Defines.URLQUERY_USERID : self.__str_playeridlist,
        }
    
    def check(self):
        keys = (
            Defines.URLQUERY_USERID,
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        fid_set = set([int(fid) for fid in self.response[Defines.URLQUERY_USERID].split(',')])
        if len(set(self.__playeridlist) & fid_set) != len(set(self.__playeridlist)) or len(fid_set) != len(self.__playeridlist):
            raise AppTestError(u'ちゃんと送信されていない')
        
        uid = self.__player0.id
        for fid in self.__playeridlist:
            for _uid, _fid, _state in ((uid, fid, Defines.FriendState.SEND), (fid, uid, Defines.FriendState.RECEIVE)):
                model = Friend.getByKey(Friend.makeID(_uid, _fid))
                if model is None or model.state != _state:
                    raise AppTestError(u'レコードが作成されていない')
