# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
import datetime

class ApiTest(ApiTestBase):
    """スカウトイベントTOP.
    """
    
    def setUp(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, gachapt=10)
        
        # イベントマスター.
        pointprizes = [
            [1, [prize.id]],
        ]
        eventmaster = self.create_dummy(DummyType.SCOUT_EVENT_MASTER, pointprizes=pointprizes)
        self.__eventmaster = eventmaster
        
        # ステージマスター.
        stagemaster = self.create_dummy(DummyType.SCOUT_EVENT_STAGE_MASTER, eventid=eventmaster.id, stage=1)
        self.__stagemaster = stagemaster
        
        # OPを閲覧済みに.
        now = OSAUtil.get_now()
        flagrecord = self.create_dummy(DummyType.SCOUT_EVENT_FLAGS, self.__player0.id, self.__eventmaster.id, now)
        self.__flagrecord = flagrecord
        
        # イベント発生中設定.
        config = BackendApi.get_current_scouteventconfig(model_mgr)
        self.__preconfig_mid = config.mid
        self.__preconfig_starttime = config.starttime
        self.__preconfig_endtime = config.endtime
        BackendApi.update_scouteventconfig(self.__eventmaster.id, now, now + datetime.timedelta(days=1))
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        return '/%s' % self.__eventmaster.id
    
    def check(self):
        keys = (
            'scoutevent',
            'scouteventstage',
            'scouteventfever',
            'scouteventdata',
            'url_scoutevent_explain',
            'url_scoutevent_ranking',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
    
    def finish(self):
        model_mgr = ModelRequestMgr()
        config = BackendApi.get_current_scouteventconfig(model_mgr)
        config.mid = self.__preconfig_mid
        config.starttime = self.__preconfig_starttime
        config.endtime = self.__preconfig_endtime
        model_mgr.set_save(config)
        model_mgr.write_all()
        model_mgr.write_end()
