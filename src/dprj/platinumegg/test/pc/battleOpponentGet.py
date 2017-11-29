# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.pc.base import PcTestBase

class ApiTest(PcTestBase):
    """バトル対戦相手取得.
    """
    
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__o_player = self.create_dummy(DummyType.PLAYER)
        
        self.__rankmaster = self.create_dummy(DummyType.BATTLE_RANK_MASTER)
        self.__battleplayer = self.create_dummy(DummyType.BATTLE_PLAYER, self.__player.id, rank=self.__rankmaster.id, oid=self.__o_player.id)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        
        self.checkResponseStatus()
        
        keys = (
            'player',
            'opponent_change_restnum',
            'battlekey',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
