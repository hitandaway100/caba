# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.raideventtest import RaidEventApiTest

class ApiTest(RaidEventApiTest):
    """レイドイベントスカウトTOP.
    """
    
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # レイドイベントを準備.
        self.setUpRaidEvent(self.__player0, dedicated_stage_max=5, is_open=True)
        
        # オープニングとタイムボーナスを閲覧済みにする.
        eventflagrecord = self.create_dummy(DummyType.RAID_EVENT_FLAGS, self.eventmaster.id, self.__player0.id, tbvtime=self.raidevent_config.starttime)
        self.__eventflagrecord = eventflagrecord
        
        # イベントスコア.
        eventscore = self.create_dummy(DummyType.RAID_EVENT_SCORE, self.eventmaster.id, self.__player0.id, destroy=1)
        self.__eventscore = eventscore
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        keys = (
            'raidevent',
            'scout',
            'player',
            'flag_skip',
            'is_all_open',
            'is_all_cleared',
            'url_raidevent_top',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
