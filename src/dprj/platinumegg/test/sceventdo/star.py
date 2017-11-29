# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.test.util.scoutevent import ScoutEventTestUtil
from defines import Defines

class ApiTest(ApiTestBase):
    """スカウトイベント実行(逢引ラブタイム発生).
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
        
        # Player.
        self.__player0 = self.__scoutevent_util.create_player()
        
        # とりあえずステージを１つ追加.
        self.__scoutevent_util.add_stages_by_maxnumber(1)
        
        # イベント発生中設定.
        self.__scoutevent_util.set_scoutevent_open()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        playdata = self.__scoutevent_util.get_scoutplaydata(self.__player0.id)
        return '/{}/{}'.format(self.__scoutevent_util.get_stage(1).id, playdata.confirmkey)
    
    def check(self):
        eventmaster = self.__scoutevent_util.eventmaster
        stagemaster = self.__scoutevent_util.get_stage(1)
        playdata_pre = self.__scoutevent_util.get_scoutplaydata(self.__player0.id)
        
        # リダイレクト先.
        redirect_url = self.response.get('redirect_url')
        if redirect_url is None or redirect_url.find('/sceventanim/{}/{}'.format(stagemaster.id, playdata_pre.confirmkey)) == -1:
            raise AppTestError(u'リダイレクト先が正しくありません')
        
        model_mgr = ModelRequestMgr()
        # 実行結果.
        playdata = BackendApi.get_event_playdata(model_mgr, eventmaster.id, self.__player0.id)
        if playdata.alreadykey != playdata_pre.confirmkey:
            raise AppTestError(u'重複確認キーが正しくない')
        elif BackendApi.find_scout_event(playdata, Defines.ScoutEventType.LOVETIME_STAR) is None:
            raise AppTestError(u'星獲得の結果が設定されていない')
        
        star_diff = playdata.star - playdata_pre.star
        if not (stagemaster.lovetime_star_min <= star_diff <= stagemaster.lovetime_star_max):
            raise AppTestError(u'星の獲得数が正しくありません')
    
    def finish(self):
        self.__scoutevent_util.set_scoutevent_close()
