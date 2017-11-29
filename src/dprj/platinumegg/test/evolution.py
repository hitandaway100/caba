# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerDeck
from defines import Defines

class ApiTest(ApiTestBase):
    """進化合成ベース選択.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__player.cardlimititem = 100
        self.__player.getModel(PlayerDeck).save()
        
        # カード.
        cardmaster = self.create_dummy(DummyType.CARD_MASTER, rare=Defines.Rarity.RARE)
        self.__basecard = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
        self.__materialcard = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
        
        for _ in xrange(10):
            self.create_dummy(DummyType.CARD, self.__player, cardmaster)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        keys = (
            'player',
            'cardnum',
            'cardlist',
            'ctype_items',
            'sort_items',
            'url_page_next',
            Defines.URLQUERY_CTYPE,
            Defines.URLQUERY_SORTBY,
            Defines.URLQUERY_PAGE,
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
