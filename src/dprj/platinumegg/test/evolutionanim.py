# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerDeck, PlayerGold
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """進化合成演出.
    """
    def setUp(self):
        model_mgr = ModelRequestMgr()
        
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__player.cardlimititem = 100
        self.__player.getModel(PlayerDeck).save()
        
        # カード.
        cardmaster = self.create_dummy(DummyType.CARD_MASTER, rare=Defines.Rarity.RARE)
        evolcardmaster = self.create_dummy(DummyType.CARD_MASTER, rare=Defines.Rarity.RARE, album=cardmaster.id, hklevel=2, evolcost=1000)
        self.__basecard = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
        self.__materialcard = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
        self.__evolcardmaster = evolcardmaster
        
        for _ in xrange(10):
            self.create_dummy(DummyType.CARD, self.__player, cardmaster)
        
        self.__player.gold = evolcardmaster.evolcost
        self.__player.getModel(PlayerGold).save()
        
        self.__evolutiondata = BackendApi.get_evolutiondata(model_mgr, self.__player.id)
        self.__requestkey = self.__player.req_confirmkey
        
        BackendApi.tr_evolution_do(model_mgr, self.__player, self.__basecard.id, self.__materialcard.id, self.__requestkey)
        model_mgr.write_all()
        model_mgr.write_end()
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return '/%d' % self.__basecard.id
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        keys = (
            'card1',
            'card2',
            'mixCard',
            'startText',
            'endText',
            'backUrl',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
