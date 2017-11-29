# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.pc.base import PcTestBase
from defines import Defines

class ApiTest(PcTestBase):
    """エリア一覧.
    """
    
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # ボス.
        boss = self.create_dummy(DummyType.BOSS_MASTER)
        
        # エリア.
        area = self.create_dummy(DummyType.AREA_MASTER, bossid=boss.id)
        self.__area = area
        
        # スカウト.
        for _ in xrange(5):
            scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area)
            self.create_dummy(DummyType.SCOUT_PLAY_DATA, self.__player0.id, scout.id, scout.execution)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
            Defines.URLQUERY_AREA:self.__area.id,
        }
    
    def check(self):
        self.checkResponseStatus()
        
        keys = (
            'area',
            'scoutlist',
            'boss',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
    
