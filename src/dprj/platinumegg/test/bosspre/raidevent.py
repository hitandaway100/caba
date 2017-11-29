# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.app.cabaret.models.Card import Deck
from platinumegg.test.raideventtest import RaidEventApiTest

class ApiTest(RaidEventApiTest):
    """ボス戦確認.
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # デッキ.
        deck = Deck(id=self.__player0.id)
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        
        arr = []
        for _ in xrange(Defines.DECK_CARD_NUM_MAX - 3):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            arr.append(self.create_dummy(DummyType.CARD, self.__player0, cardmaster).id)
        deck.set_from_array(arr)
        deck.save()
        
        self.setUpRaidEvent(self.__player0, dedicated_stage_max=5, is_open=True)
        
        # 進行情報.
        self.__playdata = self.create_dummy(DummyType.RAID_EVENT_SCOUT_PLAY_DATA, self.__player0.id, self.eventmaster.id, stage=1, cleared=1, progress=1)
    
    def getStageParams(self):
        """ステージ情報作成.
        """
        # ボス.
        self.__boss = self.create_dummy(DummyType.BOSS_MASTER)
        
        # すぐに終わるようにする.
        stageparams = {
            'boss' : self.__boss.id,
            'execution' : 1,
        }
        return stageparams
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        stagemaster = self.getStageByNumber(self.__playdata.stage)
        return '/{}/'.format(stagemaster.id)
    
    def get_frompagedata(self):
        stagemaster = self.getStageByNumber(self.__playdata.stage)
        return Defines.FromPages.RAIDEVENTSCOUT, stagemaster.id
    
    def check(self):
        keys = (
            'boss',
            'cardlist',
            'power_total',
            'cost_total',
            'url_bossbattle',
        )
        for k in keys:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない' % k)
