# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerDeck, PlayerGold,\
    PlayerRequest
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import urllib
from platinumegg.app.cabaret.models.Card import CompositionData
from platinumegg.app.cabaret.models.CardLevelExp import CardLevelExpMster

class ApiTest(ApiTestBase):
    """強化合成実行.
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
        tmp = self.create_dummy(DummyType.CARD_LEVEL_EXP_MASTER, 3, exp_great)
        
        level_min = tmp.level
        exp_min = tmp.exp
        for levelexp in model_mgr.get_mastermodel_all(CardLevelExpMster, order_by='level', fetch_deleted=True):
            if levelexp.level <= level_min:
                continue
            elif exp_min < levelexp.exp:
                break
            exp_min += 1
            levelexp.exp = exp_min
            levelexp.save()
        model_mgr.get_mastermodel_all(CardLevelExpMster, order_by='level', fetch_deleted=True, reflesh=True)
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return '/%d/%s' % (self.__basecard.id, urllib.quote(self.__requestkey, ''))
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_CARD:','.join([str(card.id) for card in self.__materialcardlist]),
        }
        return params
    
    def check(self):
        model_mgr = ModelRequestMgr()
        
        playerrequest = PlayerRequest.getByKey(self.__player.id)
        compositiondata = CompositionData.getByKey(self.__player.id)
        basecard = BackendApi.get_cards([self.__basecard.id], model_mgr)[0]
        
        # 結果が保存されているか.
        if compositiondata is None or playerrequest.req_alreadykey != self.__requestkey:
            raise AppTestError(u'結果が保存されていない')
        # 結果が正しいか.
        for att in ('mid', 'exp', 'level', 'skilllevel', 'takeover'):
            if getattr(compositiondata, att) != getattr(self.__basecard.card, att):
                raise AppTestError(u'合成前の状態が正しくない')
        
        # お金が減っているか.
        playergold = PlayerGold.getByKey(self.__player.id)
        if playergold.gold != 0:
            raise AppTestError(u'お金が正しくない')
        
        # 経験値が正しいか.
        exp = compositiondata.result_exp
        if (basecard.card.exp - self.__basecard.card.exp) != exp:
            raise AppTestError(u'経験値が正しくない')
        
        # レベルが正しいか.
        if compositiondata.result_flag_great_success:
            if compositiondata.result_lvup != 2 or basecard.card.level != 3:
                raise AppTestError(u'レベルが正しくない[大成功]')
        else:
            if compositiondata.result_lvup != 1 or basecard.card.level != 2:
                raise AppTestError(u'レベルが正しくない[成功]')
        
        materialidlist = [materialcard.id for materialcard in self.__materialcardlist]
        # 素材が消えているか.
        materiallist = BackendApi.get_cards(materialidlist, model_mgr, deleted=False)
        if materiallist:
            raise AppTestError(u'素材が消えていない')
        
        # 消えた素材が保存されているか.
        materiallist = BackendApi.get_cards(materialidlist, model_mgr, deleted=True)
        if len(materiallist) != len(materialidlist):
            raise AppTestError(u'削除済みデータが作られていない')
