# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Card import Deck, Card, CardDeleted
from defines import Defines
import urllib
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """異動実行.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        self.__sell_card_idlist = []
        
        # デッキ.
        deck = Deck(id=self.__player.id)
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        deck.leader = self.create_dummy(DummyType.CARD, self.__player, cardmaster).id
        
        for i in xrange(9):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            setattr(deck, 'mamber%d' % i, self.create_dummy(DummyType.CARD, self.__player, cardmaster).id)
        
        stocknums = {}
        for i in xrange(10):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER, rare=Defines.Rarity.TRANSFER[0])
            card = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
            self.__sell_card_idlist.append(card.id)
            stocknums[cardmaster.id] = stocknums.get(cardmaster.id, 0) + 1
        
        self.__stocknums = stocknums
        
        deck.save()
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_CARD : ','.join([str(cid) for cid in self.__sell_card_idlist]),
        }
        return params
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return '/%s/' % urllib.quote(self.__player.req_confirmkey, '')
    
    def check(self):
        keys = (
            Defines.URLQUERY_CARD_NUM,
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        cardlist = Card.getByKey(self.__sell_card_idlist)
        if len(cardlist):
            raise AppTestError(u'カードが消えていない')
        
        del_cardlist = CardDeleted.getByKey(self.__sell_card_idlist)
        if len(del_cardlist) < 1:
            raise AppTestError(u'消えたカードが保存されていない')
        
        stocknum_models = BackendApi.get_cardstocks(ModelRequestMgr(), self.__player.id, self.__stocknums.keys())
        for k,v in self.__stocknums.items():
            model = stocknum_models.get(k)
            if model is None:
                raise AppTestError(u'ストックのモデルが作られていない')
            elif v != model.num:
                raise AppTestError(u'ストック数が正しくない')
