# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType

class ApiTest(ApiTestBase):
    """バトルTOP(2回目以降のアクセス).
    """
    
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__rankmaster = self.create_dummy(DummyType.BATTLE_RANK_MASTER)
        self.__battleplayer = self.create_dummy(DummyType.BATTLE_PLAYER, self.__player.id, rank=self.__rankmaster.id, lpvtime=OSAUtil.get_now())
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        keys = (
            'player',
            'battleplayer',
            'url_battlepre',
            'url_bprecover',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
