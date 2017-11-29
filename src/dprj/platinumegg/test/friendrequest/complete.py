# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerFriend
from defines import Defines

class ApiTest(ApiTestBase):
    """仲間申請完了.
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
        self.__str_playeridlist = ','.join([str(createPlayer().id) for _ in xrange(Defines.FRIEND_PAGE_CONTENT_NUM)])
    
    def get_urlargs(self):
        return '/complete'
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
            Defines.URLQUERY_USERID : self.__str_playeridlist,
        }
    
    def check(self):
        keys = (
            'playerlist',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
