# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines

class ApiTest(ApiTestBase):
    """エリアマップ.
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # ボス.
        boss = self.create_dummy(DummyType.BOSS_MASTER)
        
        # エリア.
        for _ in xrange(Defines.SCOUTAREAMAP_CONTENTNUM_PER_PAGE + 1):
            area = self.create_dummy(DummyType.AREA_MASTER, bossid=boss.id)
            # スカウト.
            for __ in xrange(3):
                scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area)
                self.create_dummy(DummyType.SCOUT_PLAY_DATA, self.__player0.id, scout.id, scout.execution)
            self.create_dummy(DummyType.AREA_PLAY_DATA, self.__player0.id, area.id)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        keys = (
            'area',
            'arealist',
            'area_scout_dict',
            'url_page_next',
            'cur_page',
            'page_max',
        )
        for k in keys:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない' % k)
