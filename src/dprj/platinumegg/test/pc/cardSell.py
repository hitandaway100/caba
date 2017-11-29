# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.pc.base import PcTestBase
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerGold
from platinumegg.app.cabaret.models.Card import Card, CardDeleted

class ApiTest(PcTestBase):
    """カード売却.
    """
    
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__gold_pre = self.__player.gold
        
        self.__sell_card_idlist = []
        
        for _ in xrange(10):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            card = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
            self.__sell_card_idlist.append(card.id)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_CARD : ','.join([str(cid) for cid in self.__sell_card_idlist]),
        }
        return params
    
    def check(self):
        self.checkResponseStatus()
        
        keys = (
            'player',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
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
    
