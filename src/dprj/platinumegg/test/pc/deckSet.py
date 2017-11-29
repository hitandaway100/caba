# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.pc.base import PcTestBase
from platinumegg.app.cabaret.models.Player import PlayerDeck
from platinumegg.app.cabaret.models.Card import Deck
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(PcTestBase):
    """デッキ設定.
    """
    
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__player.deckcapacitylv = 999
        self.__player.getModel(PlayerDeck).save()
        
        cardidlist = []
        for _ in xrange(Defines.DECK_CARD_NUM_MAX):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            cardidlist.append(self.create_dummy(DummyType.CARD, self.__player, cardmaster).id)
        self.__cardidlist = cardidlist
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_CARD : ','.join([str(cardid) for cardid in self.__cardidlist]),
        }
        return params
    
    def check(self):
        self.checkResponseStatus()
        
        deck = BackendApi.get_deck(self.__player.id)
        deck_cardidlist = deck.to_array()
        
        for i in xrange(len(self.__cardidlist)):
            if self.__cardidlist[i] != deck_cardidlist[i]:
                raise AppTestError(u'デッキ内容が違う')
    
