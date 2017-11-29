# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.app.cabaret.models.Card import Deck

class ApiTest(ApiTestBase):
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
        
        # ボス.
        boss = self.create_dummy(DummyType.BOSS_MASTER)
        
        # エリア.
        area = self.create_dummy(DummyType.AREA_MASTER, bossid=boss.id)
        
        # スカウト.
        for _ in xrange(5):
            scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area)
            self.create_dummy(DummyType.SCOUT_PLAY_DATA, self.__player0.id, scout.id, scout.execution)
        
        self.__area = area
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        return '/%d' % self.__area.id
    
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
