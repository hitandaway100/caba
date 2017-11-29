# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.util.scoutevent import ScoutEventTestUtil
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi

class ApiTest(ApiTestBase):
    """スカウトイベントチップ交換ページ.
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
        self.__tanzakumaster = self.__scoutevent_util.create_tanzakumaster(0, [prize.id], 1, tip_rate=2)
        
        # Player.
        self.__player0 = self.__scoutevent_util.create_player()
        self.__tanzakudata = self.__scoutevent_util.create_tanzakudata(self.__player0.id, tanzaku_nums={self.__tanzakumaster.number:10})
        
        # とりあえずステージを１つ追加.
        self.__scoutevent_util.add_stages_by_maxnumber(1)
        
        # イベント発生中設定.
        self.__scoutevent_util.set_scoutevent_open()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_args(self):
        return {
            Defines.URLQUERY_ID:self.__tanzakumaster.number,
            Defines.URLQUERY_NUMBER:self.__tanzakudata.get_tanzaku(self.__tanzakumaster.number),
        }
    
    def get_urlargs(self):
        return '/{}'.format(self.__player0.req_confirmkey)
    
    def check(self):
        keys = (
            'redirect_url',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        tanzakudata = BackendApi.get_scoutevent_tanzakucastdata(ModelRequestMgr(), self.__player0.id, self.__scoutevent_util.eventmaster.id)
        if tanzakudata.get_tanzaku(self.__tanzakumaster.number) != 0:
            raise AppTestError(u'残り短冊数が正しくない')
        
        scorerecord = BackendApi.get_scoutevent_scorerecord(ModelRequestMgr(), self.__scoutevent_util.eventmaster.id, self.__player0.id)
        tip_add = self.__tanzakumaster.tip_rate * self.__tanzakudata.get_tanzaku(self.__tanzakumaster.number)
        if scorerecord.tip != tip_add:
            raise AppTestError(u'チップ数が正しくない')
    
    def finish(self):
        self.__scoutevent_util.set_scoutevent_close()
