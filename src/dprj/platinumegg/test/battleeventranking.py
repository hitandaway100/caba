# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase

class ApiTest(BattleEventApiTestBase):
    """バトルイベントランキング.
    """
    def setUp2(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # イベントマスター.
        eventmaster = self.setUpEvent(model_mgr=model_mgr)
        self.__eventmaster = eventmaster
        
        rankmaster = self.createRankMaster(1)
        
        self.setOpeningViewTime(self.__player0.id)
        
        PLAYER_NUM = 20
        # スコア設定.
        score = 10000000
        rankdata = []
        model_mgr = ModelRequestMgr()
        for _ in xrange(PLAYER_NUM):
            player = self.create_dummy(DummyType.PLAYER)
            BackendApi.tr_add_battleevent_battlepoint(model_mgr, self.__eventmaster, player.id, rankmaster, score, OSAUtil.get_now())
            rankdata.insert(0, (player.id, score))
            score *= 2
        model_mgr.write_all()
        model_mgr.write_end()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%d' % self.__eventmaster.id
    
    def check(self):
        keys = (
            'is_opened',
            'url_battleevent_top',
            'url_battleevent_explain',
            'is_view_myrank',
            'url_battleevent_ranking',
            'url_battleevent_myrank',
            'url_page_next',
            'cur_page',
            'page_max',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
