# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.app.cabaret.models.Card import Deck
from platinumegg.app.cabaret.util.api import BackendApi
import urllib
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """ボス戦アニメーション.
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
            card = self.create_dummy(DummyType.CARD, self.__player0, cardmaster)
            arr.append(card.id)
        deck.set_from_array(arr)
        deck.save()
        
        # ボス.
        boss = self.create_dummy(DummyType.BOSS_MASTER)
        boss.hp = 5
        boss.defense = 1
        boss.save()
        
        # 報酬.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER)
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, gachapt=10, item=itemmaster, card=cardmaster)
        
        # エリア.
        area = self.create_dummy(DummyType.AREA_MASTER, bossid=boss.id)
        area.prizes = [prize.id]
        area.save()
        
        # スカウト.
        for _ in xrange(5):
            scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area)
            self.create_dummy(DummyType.SCOUT_PLAY_DATA, self.__player0.id, scout.id, scout.execution)
        
        self.__area = area
        
        bosshp, animdata = BackendApi.bossbattle(BackendApi.get_cards(arr), boss)
        
        model_mgr = ModelRequestMgr()
        if bosshp < 1:
            BackendApi.tr_area_clear(model_mgr, self.__player0, area)
        BackendApi.tr_save_bossresult(model_mgr, self.__player0.id, area, boss, animdata, self.__player0.req_confirmkey)
        model_mgr.write_all()
        model_mgr.write_end()
        self.__battlekey = self.__player0.req_confirmkey
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        return '/%d/%s' % (self.__area.id, urllib.quote(self.__battlekey, ''))
    
    def check(self):
        arr = (
            'backUrl',
            'winFlag',
            'playerMax',
            'activePlayer',
            'bossGauge',
            'bossImage',
            'image1',
            'image2',
            'image3',
            'image4',
            'image5',
            'image6',
            'image7',
#            'image8',
#            'image9',
#            'image10',
        )
        for k in arr:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない' % k)
