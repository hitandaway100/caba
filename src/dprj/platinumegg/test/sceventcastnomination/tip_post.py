# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.util.scoutevent import ScoutEventTestUtil
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """スカウトイベントチップ投入書き込み.
    """
    def setUp(self):
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, gachapt=10)
        
        # イベントマスター.
        pointprizes = [
            [1, [prize.id]],
        ]
        event_args = dict(pointprizes=pointprizes, lovetime_star=10, lovetime_timelimit=3600)
        eventstage_args = dict(execution=1000, lovetime_star_min=1)
        self.__scoutevent_util = ScoutEventTestUtil(self, event_args, eventstage_args)
        
        # 短冊.
        self.__tanzakumaster = self.__scoutevent_util.create_tanzakumaster(0, [prize.id], 1)
        
        # Player.
        self.__player0 = self.__scoutevent_util.create_player(score_args=dict(tip=10))
        self.__tanzakudata = self.__scoutevent_util.create_tanzakudata(self.__player0.id, current_cast=self.__tanzakumaster.number)
        
        # とりあえずステージを１つ追加.
        self.__scoutevent_util.add_stages_by_maxnumber(1)
        
        # イベント発生中設定.
        self.__scoutevent_util.set_scoutevent_open()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_args(self):
        scorerecord = self.__scoutevent_util.get_scorerecord(self.__player0.id)
        return {
            Defines.URLQUERY_NUMBER:scorerecord.tip,
        }
    
    def check(self):
        keys = (
            'redirect_url',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        scorerecord_pre = self.__scoutevent_util.get_scorerecord(self.__player0.id)
        scorerecord = BackendApi.get_scoutevent_scorerecord(ModelRequestMgr(), self.__scoutevent_util.eventmaster.id, self.__player0.id)
        
        tanzakudata = BackendApi.get_scoutevent_tanzakucastdata(ModelRequestMgr(), self.__player0.id, self.__scoutevent_util.eventmaster.id)
        if tanzakudata.current_cast != -1:
            raise AppTestError(u'現在の指名キャストが解除されていない')
        elif scorerecord.tip != 0:
            raise AppTestError(u'チップの残り枚数が正しくない')
        elif tanzakudata.get_tip(self.__tanzakumaster.number) != scorerecord_pre.tip:
            raise AppTestError(u'投入後のチップ数が正しくない')
    
    def finish(self):
        self.__scoutevent_util.set_scoutevent_close()
