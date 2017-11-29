# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
import datetime

class ApiTest(ApiTestBase):
    """スカウトイベントランキングページ.
    """
    def setUp(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # イベントマスター.
        eventmaster = self.create_dummy(DummyType.SCOUT_EVENT_MASTER)
        self.__eventmaster = eventmaster
        
        now = OSAUtil.get_now()
        
        # OPを閲覧済みに.
        flagrecord = self.create_dummy(DummyType.SCOUT_EVENT_FLAGS, self.__player0.id, self.__eventmaster.id, now)
        self.__flagrecord = flagrecord
        
        # イベント発生中設定.
        config = BackendApi.get_current_scouteventconfig(model_mgr)
        self.__preconfig_mid = config.mid
        self.__preconfig_starttime = config.starttime
        self.__preconfig_endtime = config.endtime
        BackendApi.update_scouteventconfig(self.__eventmaster.id, now, now + datetime.timedelta(days=1))
        
        PLAYER_NUM = 20
        # スコア設定.
        score = 10000000
        rankdata = []
        model_mgr = ModelRequestMgr()
        for _ in xrange(PLAYER_NUM):
            player = self.create_dummy(DummyType.PLAYER)
            BackendApi.tr_add_scoutevent_score(model_mgr, self.__eventmaster, player.id, score)
            rankdata.insert(0, (player.id, score))
            score *= 2
        model_mgr.write_all()
        model_mgr.write_end()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        return '/%s' % self.__eventmaster.id
    
    def check(self):
        keys = (
            'is_opened',
            'url_scoutevent_top',
            'url_scoutevent_explain',
            'is_view_myrank',
            'url_scoutevent_ranking',
            'url_scoutevent_myrank',
            'url_page_next',
            'cur_page',
            'page_max',
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
