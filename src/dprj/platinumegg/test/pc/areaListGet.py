# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.pc.base import PcTestBase
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(PcTestBase):
    """エリア一覧.
    """
    
    def setUp(self):
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        # ボス.
        boss = self.create_dummy(DummyType.BOSS_MASTER)
        
        self.__pre_arealist = BackendApi.get_playable_area_all(ModelRequestMgr(), self.__player.id)
        
        preareaid = 0
        for _ in xrange(10):
            # エリア.
            area = self.create_dummy(DummyType.AREA_MASTER, bossid=boss.id, opencondition=preareaid)
            preareaid = area.id
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        self.checkResponseStatus()
        
        keys = (
            'arealist',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        if len(self.resultbody['arealist']) != (len(self.__pre_arealist) + 1):
            raise AppTestError(u'エリア数が想定外, pre=%s vs post=%s' % ([area.id for area in self.__pre_arealist], [area['id'] for area in self.resultbody['arealist']]))
    
