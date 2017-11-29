# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerFriend
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """仲間Top.
    """
    STATE = Defines.FriendState.SEND
    
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        model = self.__player0.getModel(PlayerFriend)
        model.friendlimit = 30
        model.save()
        
        def addRequest(v_player, o_player):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_friendrequest(model_mgr, v_player, o_player)
            model_mgr.write_all()
            model_mgr.write_end()
        
        def addFriend(v_player, o_player):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_friend(model_mgr, v_player.id, o_player.id)
            model_mgr.write_all()
            model_mgr.write_end()
        
        for _ in xrange(model.friendlimit):
            player = self.create_dummy(DummyType.PLAYER)
            if ApiTest.STATE == Defines.FriendState.ACCEPT:
                addRequest(self.__player0, player)
                addFriend(player, self.__player0)
            elif ApiTest.STATE == Defines.FriendState.SEND:
                addRequest(self.__player0, player)
            elif ApiTest.STATE == Defines.FriendState.RECEIVE:
                addRequest(player, self.__player0)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
            Defines.URLQUERY_STATE : ApiTest.STATE,
            Defines.URLQUERY_PAGE : 1,
        }
    
    def check(self):
        keys = (
            'friendnum',
            'friendnummax',
            'url_friendsearch',
            'url_friendrequest_auto',
            'playerlist',
            'url_page_next',
            'url_page_prev',
            'url_friendlist',
            'url_requestlist',
            'url_receivelist',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
