# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Card import Deck
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerDeck

class ApiTest(ApiTestBase):
    """デッキ設定.
    """
    
    AUTO = False
    
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
            card = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
            if not ApiTest.AUTO or len(arr) == 0:
                arr.append(card.id)
        deck.set_from_array(arr)
        deck.save()
        self.__deck = deck
        
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        self.__card = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
        
        for _ in xrange(20):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            self.create_dummy(DummyType.CARD, self.__player, cardmaster)
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return '/%d' % int(ApiTest.AUTO)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_INDEX : 1,
            Defines.URLQUERY_CARD : self.__card.id,
        }
        return params
    
    def check(self):
        
        deck = Deck.getByKey(self.__player.id)
        
        if ApiTest.AUTO:
            if len(deck.to_array()) != Defines.DECK_CARD_NUM_MAX:
                raise AppTestError(u'デッキ設定されていない')
        else:
#            if deck.member1 == self.__deck.member1 or deck.member1 != self.__deck.member2:
#                raise AppTestError(u'デッキ設定されていない')
            if deck.member1 != self.__card.id:
                raise AppTestError(u'デッキ設定されていない')
