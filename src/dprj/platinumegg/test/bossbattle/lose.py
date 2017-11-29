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
    """ボス戦書き込み(敗北).
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
        boss.hp = 100000
        boss.defense = 10000
        boss.save()
        
        # エリア.
        area = self.create_dummy(DummyType.AREA_MASTER, bossid=boss.id)
        
        # スカウト.
        for _ in xrange(5):
            scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area)
            self.create_dummy(DummyType.SCOUT_PLAY_DATA, self.__player0.id, scout.id, scout.execution)
        
        self.__area = area
        self.__battlekey = self.__player0.req_confirmkey
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        return '/%d/%s' % (self.__area.id, urllib.quote(self.__battlekey, ''))
    
    def check(self):
        result = BackendApi.get_bossresult(ModelRequestMgr(), self.__player0.id, self.__area.id)
        if result is None:
            raise AppTestError(u'結果が保存されていない')
