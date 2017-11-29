# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Card import Deck
from defines import Defines

class ApiTest(ApiTestBase):
    """デッキ編成.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        # デッキ.
        deck = Deck(id=self.__player.id)
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        
        arr = []
        for _ in xrange(Defines.DECK_CARD_NUM_MAX - 3):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            arr.append(self.create_dummy(DummyType.CARD, self.__player, cardmaster).id)
        deck.set_from_array(arr)
        deck.save()
        
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        self.__card0 = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_CARD : self.__card0.id,
        }
        return params
    
    def check(self):
        keys = (
            'url_addmember',
            'leader',
            'memberlist',
            'cost',
            'capacity',
            'power_total',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
