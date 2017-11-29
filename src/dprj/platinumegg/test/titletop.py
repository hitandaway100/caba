# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType

class ApiTest(ApiTestBase):
    """称号Top.
    """
    
    def setUp(self):
        self.__now = OSAUtil.get_now()
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        # 名誉ポイント.
        self.create_dummy(DummyType.CABA_CLUB_SCORE_PLAYER_DATA, uid=self.__player.id, point=200)
        # 称号一覧.
        titlemaster_list = [self.create_dummy(DummyType.TITLE_MASTER, cost=100) for _ in xrange(5)]
        # 称号情報.
        self.create_dummy(DummyType.TITLE_PLAYER_DATA, uid=self.__player.id, title=titlemaster_list[0].id)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        keys = (
            'cabaclub_management_info',
            'titlemaster_list',
            'title',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
