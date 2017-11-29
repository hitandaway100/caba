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
from platinumegg.app.cabaret.models.Card import EvolutionData

class ApiTest(ApiTestBase):
    """進化合成実行.
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
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return '/%d/%s' % (self.__basecard.id, urllib.quote(self.__requestkey, ''))
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_CARD:self.__materialcard.id,
        }
        return params
    
    def check(self):
        model_mgr = ModelRequestMgr()
        
        playerrequest = PlayerRequest.getByKey(self.__player.id)
        evolutiondata = EvolutionData.getByKey(self.__player.id)
        basecard = BackendApi.get_cards([self.__basecard.id], model_mgr)[0]
        
        # 結果が保存されているか.
        if evolutiondata is None or playerrequest.req_alreadykey != self.__requestkey:
            raise AppTestError(u'結果が保存されていない')
        # 結果が正しいか.
        for att in ('mid', 'exp', 'level', 'skilllevel', 'takeover'):
            if getattr(evolutiondata, att) != getattr(self.__basecard, att):
                raise AppTestError(u'合成前の状態が正しくない')
        
        # 進化しているか.
        if basecard.card.mid != self.__evolcardmaster.id:
            raise AppTestError(u'進化していない')
        elif basecard.card.level != 1 or 0 < basecard.card.exp:
            raise AppTestError(u'経験値が残っている')
        
        # お金が減っているか.
        playergold = PlayerGold.getByKey(self.__player.id)
        if playergold.gold != 0:
            raise AppTestError(u'お金が正しくない')
        
        materialid = self.__materialcard.id
        # 素材が消えているか.
        materiallist = BackendApi.get_cards([materialid], model_mgr, deleted=False)
        if materiallist:
            raise AppTestError(u'素材が消えていない')
        
        # 消えた素材が保存されているか.
        materiallist = BackendApi.get_cards([materialid], model_mgr, deleted=True)
        if len(materiallist) != 1:
            raise AppTestError(u'削除済みデータが作られていない')
