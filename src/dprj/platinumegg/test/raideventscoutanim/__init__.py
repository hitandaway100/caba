# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.raideventtest import RaidEventApiTest
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerGold
from platinumegg.app.cabaret.models.raidevent.RaidEventScout import RaidEventScoutPlayData
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi

class RaidEventScoutAnimApiTest(RaidEventApiTest):
    """レイドイベントスカウト演出.
    """
    
    def setUp(self):
        # Player.
        self.__player0 = self.createPlayer()
        
        # レイドイベントを準備.
        self.setUpRaidEvent(self.__player0, dedicated_stage_max=self.get_dedicated_stage_max(), is_open=True)
        
        # オープニングとタイムボーナスを閲覧済みにする.
        eventflagrecord = self.create_dummy(DummyType.RAID_EVENT_FLAGS, self.eventmaster.id, self.player.id, tbvtime=self.raidevent_config.starttime)
        self.__eventflagrecord = eventflagrecord
        
        # イベントスコア.
        eventscore = self.create_dummy(DummyType.RAID_EVENT_SCORE, self.eventmaster.id, self.__player0.id, destroy=1)
        self.__eventscore = eventscore
        
        # 進行情報.
        self.__playdata = self.createPlayData()
        
        self.executeScout()
    
    def executeScout(self):
        stagemaster = self.getStageByNumber(self.__playdata.stage)
        model_mgr = ModelRequestMgr()
        BackendApi.tr_do_raidevent_scout(model_mgr, self.eventmaster, self.__player0, stagemaster, self.__playdata.confirmkey, False)
        model_mgr.write_all()
        model_mgr.write_end()
    
    @property
    def player(self):
        return self.__player0
    
    @property
    def eventplaydata(self):
        return self.__playdata
    
    def get_dedicated_stage_max(self):
        return 5
    
    def createPlayer(self):
        """プレイヤー情報作成.
        """
        return self.create_dummy(DummyType.PLAYER)
    
    def createPlayData(self):
        return self.create_dummy(DummyType.RAID_EVENT_SCOUT_PLAY_DATA, self.player.id, self.eventmaster.id)
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        stagemaster = self.getStageByNumber(self.eventplaydata.stage)
        return u'/{}/{}'.format(stagemaster.id, self.eventplaydata.confirmkey)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.player.dmmid,
        }
    
    def check(self):
        keys = (
            'dataBody',
            'dataUrl',
            'topUrl',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
