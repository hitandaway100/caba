# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
import datetime

class ApiTest(ApiTestBase):
    """スカウトイベントオープニング.
    """
    def setUp(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # イベントマスター.
        scenario = self.create_dummy(DummyType.EVENT_SCENARIO_MASTER)
        eventmaster = self.create_dummy(DummyType.SCOUT_EVENT_MASTER, op=scenario.number, ed=scenario.number)
        self.__eventmaster = eventmaster
        
        # イベント発生中設定.
        config = BackendApi.get_current_scouteventconfig(model_mgr)
        self.__preconfig_mid = config.mid
        self.__preconfig_starttime = config.starttime
        self.__preconfig_endtime = config.endtime
        now = OSAUtil.get_now()
        BackendApi.update_scouteventconfig(self.__eventmaster.id, now, now + datetime.timedelta(days=1))
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        url = self.response.get('redirect_url')
        if not url:
            raise AppTestError(u'リダイレクト先が設定されていない')
        elif url.find('eventscenario') == -1:
            raise AppTestError(u'演出に遷移していない')
        
        model_mgr = ModelRequestMgr()
        config = BackendApi.get_current_scouteventconfig(model_mgr)
        flagrecord = BackendApi.get_scoutevent_flagrecord(model_mgr, self.__eventmaster.id, self.__player0.id)
        if flagrecord is None or not (config.starttime <= flagrecord.opvtime < config.endtime):
            raise AppTestError(u'演出の閲覧時間が更新されていない')
    
    def finish(self):
        model_mgr = ModelRequestMgr()
        config = BackendApi.get_current_scouteventconfig(model_mgr)
        config.mid = self.__preconfig_mid
        config.starttime = self.__preconfig_starttime
        config.endtime = self.__preconfig_endtime
        model_mgr.set_save(config)
        model_mgr.write_all()
        model_mgr.write_end()
