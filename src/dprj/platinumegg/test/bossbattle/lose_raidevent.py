# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.app.cabaret.models.Card import Deck
from platinumegg.test.raideventtest import RaidEventApiTest
import urllib
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi

class ApiTest(RaidEventApiTest):
    """ボス戦(バトル敗北).
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
        
        self.__stagemaster = self.getStageByNumber(self.__playdata.stage)
    
    def getStageParams(self):
        """ステージ情報作成.
        """
        # ボス.
        self.__boss = self.create_dummy(DummyType.BOSS_MASTER)
        self.__boss.hp = 100000
        self.__boss.defense = 10000
        self.__boss.save()
        
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
        return '/{}/{}/'.format(self.__stagemaster.id, urllib.quote(self.__player0.req_confirmkey, ''))
    
    def get_frompagedata(self):
        return Defines.FromPages.RAIDEVENTSCOUT, self.__stagemaster.id
    
    def check(self):
        result = BackendApi.get_bossresult(ModelRequestMgr(), self.__player0.id, self.__stagemaster.id)
        if result is None:
            raise AppTestError(u'結果が保存されていない')
