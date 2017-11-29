# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi

class ApiTest(ApiTestBase):
    """対戦相手更新(更新して残り回数を減らす).
    """
    
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__o_player = self.create_dummy(DummyType.PLAYER)
        for _ in xrange(10):
            self.create_dummy(DummyType.PLAYER)
        rank = self.create_dummy(DummyType.BATTLE_RANK_MASTER)
        self.__battleplayer = self.create_dummy(DummyType.BATTLE_PLAYER, self.__player.id, rank.id, oid=self.__o_player.id, rankopplist=[self.__o_player.id])
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return '/%d' % (self.__battleplayer.change_cnt+1)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
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
