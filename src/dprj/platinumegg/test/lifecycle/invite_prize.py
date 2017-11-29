# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Invite import InviteData
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """ライフサイクル(招待報酬あり).
    """
    KEY_EVENT_TYPE = u'eventtype'
    KEY_ID = u'id'
    KEY_INVITE_FROM_ID = u'invite_from_id'
    
    def setUp(self):
        # 招待したプレイヤー.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        # 招待されたプレイヤー.
        self.__player1 = self.create_dummy(DummyType.PLAYER)
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100)
        # マスターデータ.
        prizes = {'normal':[
            [2, [prize.id]],
        ],
        'repeat':[{
            'min' : 1,
            'prize' : [prize.id],
        }]}
        cur_invitemaster = BackendApi.get_current_invitemaster(ModelRequestMgr())
        self.__invitemaster = self.create_dummy(DummyType.INVITE_MASTER, prizes=prizes, mid=cur_invitemaster.id if cur_invitemaster else None)
        
        # 招待レコード.
        self.__invite = self.create_dummy(DummyType.INVITE, self.__player0.id, self.__invitemaster.id, cnt=1)
        
        # 処理前のプレゼント数.
        self.__present_num = BackendApi.get_present_num(self.__player0.id)
    
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
        elif invitedata.state != Defines.InviteState.ACCEPT:
            raise AppTestError(u'招待の状態が正しくない.%s' % invitedata.state)
        
        model_mgr = ModelRequestMgr()
        invite = BackendApi.get_invite(model_mgr, self.__player0.id, self.__invitemaster.id)
        if invite is None:
            raise AppTestError(u'招待数のレコードが保存されていない')
        elif invite.cnt != (self.__invite.cnt+1):
            raise AppTestError(u'招待数が正しくない.%s' % invite.cnt)
        
        present_num = BackendApi.get_present_num(self.__player0.id)
        if present_num != (self.__present_num + 2):
            raise AppTestError(u'プレゼント数が正しくない.%s vs %s' % (present_num, (self.__present_num + 2)))
