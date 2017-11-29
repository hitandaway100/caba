# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Card import Deck
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerDeck

class ApiTest(ApiTestBase):
    """デッキメンバー選択.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__player.deckcapacitylv = 999
        self.__player.getModel(PlayerDeck).save()
        
        # デッキ.
        deck = Deck(id=self.__player.id)
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        
        arr = []
        for _ in xrange(Defines.DECK_CARD_NUM_MAX - 3):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            arr.append(self.create_dummy(DummyType.CARD, self.__player, cardmaster).id)
        deck.set_from_array(arr)
        deck.save()
        self.__deck = deck
        
        for _ in xrange(20):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            self.create_dummy(DummyType.CARD, self.__player, cardmaster)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_INDEX : 1,
        }
        return params
    
    def check(self):
        keys = (
            'cardlist',
            'ctype_items',
            'sort_items',
            'url_page_next',
            'current_card',
            Defines.URLQUERY_CTYPE,
            Defines.URLQUERY_SORTBY,
            Defines.URLQUERY_PAGE,
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        current_card = self.response.get('current_card')
        if current_card['id'] != self.__deck.member1:
            raise AppTestError(u'current_cardが違う')
