# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerDeck, PlayerGold
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """強化合成演出.
    """
    def setUp(self):
        model_mgr = ModelRequestMgr()
        
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__player.cardlimititem = 100
        self.__player.getModel(PlayerDeck).save()
        
        # カード.
        cardmaster = self.create_dummy(DummyType.CARD_MASTER, maxlevel=10)
        basecard = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
        self.__basecard = BackendApi.get_cards([basecard.id], model_mgr)[0]
        
        materialcardidlist = []
        for _ in xrange(10):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER, cost=10, basematerialexp=100)
            materialcardidlist.append(self.create_dummy(DummyType.CARD, self.__player, cardmaster).id)
        self.__materialcardlist = BackendApi.get_cards(materialcardidlist, model_mgr)
        
        self.__player.gold = BackendApi.calc_composition_cost(self.__basecard, self.__materialcardlist)
        self.__player.getModel(PlayerGold).save()
        
        self.__compositiondata = BackendApi.get_compositiondata(model_mgr, self.__player.id)
        self.__requestkey = self.__player.req_confirmkey
        
        exp = BackendApi.calc_composition_exp(self.__basecard, self.__materialcardlist, is_great_success=False)
        exp_great = BackendApi.calc_composition_exp(self.__basecard, self.__materialcardlist, is_great_success=True)
        
        self.create_dummy(DummyType.CARD_LEVEL_EXP_MASTER, 1, 0)
        self.create_dummy(DummyType.CARD_LEVEL_EXP_MASTER, 2, exp)
        self.create_dummy(DummyType.CARD_LEVEL_EXP_MASTER, 3, exp_great)
        
        BackendApi.get_compositiondata(model_mgr, self.__player.id)
        BackendApi.tr_composition_do(model_mgr, self.__player.id, self.__basecard.id, materialcardidlist, self.__requestkey)
        model_mgr.write_all()
        model_mgr.write_end()
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        pass
