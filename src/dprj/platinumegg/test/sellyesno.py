# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Card import Deck
from defines import Defines

class ApiTest(ApiTestBase):
    """売却確認.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        self.__sell_card_idlist = []
        
        # デッキ.
        deck = Deck(id=self.__player.id)
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        deck.leader = self.create_dummy(DummyType.CARD, self.__player, cardmaster).id
#        self.__sell_card_idlist.append(deck.leader)
        
        for i in xrange(9):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            setattr(deck, 'mamber%d' % i, self.create_dummy(DummyType.CARD, self.__player, cardmaster).id)
#            self.__sell_card_idlist.append(getattr(deck, 'mamber%d' % i))
        
        for i in xrange(10):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            card = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
#            card.protection = True
#            card.save()
            self.__sell_card_idlist.append(card.id)
        
        deck.save()
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        for i in xrange(len(self.__sell_card_idlist)):
            params['%s%s' % (Defines.URLQUERY_CARD, i)] = self.__sell_card_idlist[i]
        return params
    
    def check(self):
        keys = (
            'cardlist',
            'sellprice',
            'gold_pre',
            'gold_post',
            'flag_include_rare',
            'flag_include_hkincr_already',
            'url_selldo',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
