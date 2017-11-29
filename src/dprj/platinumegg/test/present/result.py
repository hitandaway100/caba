# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Present import Present, PresentReceived
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerDeck
from platinumegg.app.cabaret.util.api import BackendApi

class ApiTest(ApiTestBase):
    """プレゼント受け取り.
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        playerdeck = self.__player0.getModel(PlayerDeck)
        playerdeck.cardlimititem = 50
        playerdeck.save()
        
        presentlist = []
        
        # アイテム.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER, Defines.ItemEffect.ACTION_ALL_RECOVERY)
        present = Present.createByItem(0, self.__player0.id, itemmaster)
        presentlist.append(present)
        
        # カード.
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        present = Present.createByCard(0, self.__player0.id, cardmaster)
        presentlist.append(present)
        
        # お金.
        present = Present.createByGold(0, self.__player0.id, 100)
        presentlist.append(present)
        
        # チケット.
        present = Present.createByTicket(0, self.__player0.id, 100)
        presentlist.append(present)
        
        # ガチャポイント.
        present = Present.createByGachaPt(0, self.__player0.id, 100)
        presentlist.append(present)
        
        # プレゼント受け取りレコード作成.
        presentidlist = []
        for present in presentlist:
            present.save()
            PresentReceived.createByPresent(present).save()
            presentidlist.append(present.id)
            present.delete()
        
        self.__cardnum = BackendApi.get_cardnum(self.__player0.id)
        self.__presentidlist = presentidlist
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
            Defines.URLQUERY_ID : ','.join([str(pid) for pid in self.__presentidlist])
        }
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/result'
    
    def check(self):
        arr = (
            'presentlist',
            'overlimit',
        )
        for k in arr:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない' % k)
