# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Card import Deck, Card, CardDeleted
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerGold

class ApiTest(ApiTestBase):
    """売却実行.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__gold_pre = self.__player.gold
        
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
            Defines.URLQUERY_CARD : ','.join([str(cid) for cid in self.__sell_card_idlist]),
        }
        return params
    
    def check(self):
        keys = (
            Defines.URLQUERY_CARD_NUM,
            Defines.URLQUERY_GOLD,
            Defines.URLQUERY_GOLDADD,
            Defines.URLQUERY_GOLDPRE,
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        playergold = PlayerGold.getByKey(self.__player.id)
        if playergold is None or playergold.gold <= self.__gold_pre:
            raise AppTestError(u'所持金が増えていない')
        
        cardlist = Card.getByKey(self.__sell_card_idlist)
        if len(cardlist):
            raise AppTestError(u'カードが消えていない')
        
        del_cardlist = CardDeleted.getByKey(self.__sell_card_idlist)
        if len(del_cardlist) < 1:
            raise AppTestError(u'消えたカードが保存されていない')
