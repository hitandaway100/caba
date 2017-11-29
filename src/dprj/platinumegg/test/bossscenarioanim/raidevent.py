# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.app.cabaret.models.Card import Deck
from platinumegg.test.raideventtest import RaidEventApiTest
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import urllib

class ApiTest(RaidEventApiTest):
    """ボス戦勝利後のシナリオ演出.
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        self.__boss = self.create_dummy(DummyType.BOSS_MASTER)
        self.__boss.hp = 1
        self.__boss.save()
        
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
        
        # ボス.
        bosshp, animdata = BackendApi.bossbattle(BackendApi.get_cards(arr), self.__boss)
        
        model_mgr = ModelRequestMgr()
        if bosshp < 1:
            BackendApi.tr_raidevent_stage_clear(model_mgr, self.eventmaster, self.__player0, self.__stagemaster)
        BackendApi.tr_save_bossresult(model_mgr, self.__player0.id, self.__stagemaster, self.__boss, animdata, self.__player0.req_confirmkey)
        model_mgr.write_all()
        model_mgr.write_end()
    
    def getStageParams(self):
        """ステージ情報作成.
        """
        # 報酬.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER)
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, gachapt=10, item=itemmaster, card=cardmaster)
        
        # すぐに終わるようにする.
        stageparams = {
            'boss' : self.__boss.id,
            'execution' : 1,
            'bossprizes' : [prize.id],
            'bossscenario' : 1,
        }
        return stageparams
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        return '/{}/{}/'.format(self.__stagemaster.id, urllib.quote(self.__player0.req_confirmkey, ''))
    
    def get_frompagedata(self):
        stagemaster = self.getStageByNumber(self.__playdata.stage)
        return Defines.FromPages.RAIDEVENTSCOUT, stagemaster.id
    
    def check(self):
        arr = (
            'redirect_url',
        )
        for k in arr:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない' % k)
        
        redirect_url = self.response['redirect_url']
        if redirect_url.find('event_scenario4/effect2') == -1:
            raise AppTestError(u'リダイレクト先が正しくない')
