# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.pc.base import PcTestBase
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(PcTestBase):
    """バトル対戦相手取得.
    """
    
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__o_player = self.create_dummy(DummyType.PLAYER)
        for _ in xrange(10):
            self.create_dummy(DummyType.PLAYER)
        rank = self.create_dummy(DummyType.BATTLE_RANK_MASTER)
        self.__battleplayer = self.create_dummy(DummyType.BATTLE_PLAYER, self.__player.id, rank.id, oid=self.__o_player.id, rankopplist=[self.__o_player.id])
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_NUMBER:self.__battleplayer.change_cnt+1,
        }
        return params
    
    def check(self):
        self.checkResponseStatus()
        
        model_mgr = ModelRequestMgr()
        battleplayer = BackendApi.get_battleplayer(model_mgr, self.__player.id)
        if battleplayer is None:
            raise AppTestError(u'BattlePlayerが保存されていない')
        elif battleplayer.opponent == 0:
            raise AppTestError(u'対戦相手が設定されていない')
        elif self.__battleplayer.opponent == battleplayer.opponent:
            raise AppTestError(u'対戦相手が変わってない')
        elif battleplayer.change_cnt != 1:
            raise AppTestError(u'変更回数が増えていない')
        elif not battleplayer.opponent in battleplayer.rankopplist:
            raise AppTestError(u'対戦相手がrankopplistに登録されていない')
