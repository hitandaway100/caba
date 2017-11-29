# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Invite import InviteData
from defines import Defines

class ApiTest(ApiTestBase):
    """ライフサイクル(招待).
    """
    KEY_EVENT_TYPE = u'eventtype'
    KEY_ID = u'id'
    KEY_INVITE_FROM_ID = u'invite_from_id'
    
    def setUp(self):
        # 招待したプレイヤー.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        # 招待されたプレイヤー.
        self.__player1 = self.create_dummy(DummyType.PLAYER, regist=False, tutoend=False)
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/addapp'
    
    def get_query_params(self):
        return {
            'id' : self.__player1.dmmid,
            'invite_from_id' : self.__player0.dmmid,
            'eventtype' : 'event.addapp',
        }
    
    def check(self):
        invitedata = InviteData.getByKey(self.__player1.dmmid)
        if invitedata is None:
            raise AppTestError(u'招待レコードが作成されていない')
        elif invitedata.fid != self.__player0.id:
            raise AppTestError(u'招待してくれたIDが正しくない.%s vs %s' % (invitedata.fid, self.__player0.id))
        elif invitedata.state != Defines.InviteState.RECEIVE:
            raise AppTestError(u'招待の状態が正しくない.%s' % invitedata.state)
