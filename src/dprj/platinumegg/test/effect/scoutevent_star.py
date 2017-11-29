# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.util.scoutevent import ScoutEventTestUtil

class ApiTest(ApiTestBase):
    """スカウトイベントスカウト演出(星獲得)パラメータ.
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
        
        # スカウト実行.
        self.__scoutevent_util.execute_scout(self.__player0.id)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        playdata = self.__scoutevent_util.get_scoutplaydata(self.__player0.id)
        return '/scoutevent/{}/{}'.format(self.__scoutevent_util.get_stage(1).id, playdata.confirmkey)
    
    def check(self):
        keys = (
            'eventKind',
            'eventText',
            'scoutNum',
            'backImage',
            'charText',
            'cgText',
            'expText',
            'progressGauge',
            'hpGauge',
            'expGauge',
            'backUrl',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        stagemaster = self.__scoutevent_util.get_stage(1)
        playdata = self.__scoutevent_util.get_scoutplaydata(self.__player0.id)
        if self.response['backUrl'].find('/sceventresult/{}/{}'.format(stagemaster.id, playdata.confirmkey)) == -1:
            raise AppTestError(u'現在のパネル番号が違う')
    
    def finish(self):
        self.__scoutevent_util.set_scoutevent_close()
