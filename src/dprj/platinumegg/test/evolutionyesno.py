# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerDeck
from defines import Defines

class ApiTest(ApiTestBase):
    """進化合成素材選択.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__player.cardlimititem = 100
        self.__player.getModel(PlayerDeck).save()
        
        # カード.
        cardmaster = self.create_dummy(DummyType.CARD_MASTER, rare=Defines.Rarity.RARE)
        evolcardmaster = self.create_dummy(DummyType.CARD_MASTER, rare=Defines.Rarity.RARE, album=cardmaster.id, hklevel=2)
        self.__basecard = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
        self.__materialcard = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
        self.__evolcardmaster = evolcardmaster
        
        for _ in xrange(10):
            self.create_dummy(DummyType.CARD, self.__player, cardmaster)
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return '/%d' % self.__basecard.id
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_CARD:self.__materialcard.id,
        }
        return params
    
    def check(self):
        keys = (
            'player',
            'basecard',
            'materialcard',
            'cost',
            'cost_over',
            'url_do',
            'cardnum',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
