# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Present import Present, PresentReceived
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerGold, PlayerGachaPt,\
    PlayerDeck
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """プレゼント受け取り.
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        playerdeck = self.__player0.getModel(PlayerDeck)
        playerdeck.cardlimititem = 50
        playerdeck.save()
        
        presentidlist = []
        
        # アイテム.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER, Defines.ItemEffect.ACTION_ALL_RECOVERY)
        present = Present.createByItem(0, self.__player0.id, itemmaster)
        present.save()
        presentidlist.append(present.id)
        
        # カード.
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        present = Present.createByCard(0, self.__player0.id, cardmaster)
        present.save()
        presentidlist.append(present.id)
        
        # お金.
        present = Present.createByGold(0, self.__player0.id, 100)
        present.save()
        presentidlist.append(present.id)
        
        # チケット.
        present = Present.createByTicket(0, self.__player0.id, 100)
        present.save()
        presentidlist.append(present.id)
        
        # ガチャポイント.
        present = Present.createByGachaPt(0, self.__player0.id, 100)
        present.save()
        presentidlist.append(present.id)
        
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
        return u'/do'
    
    def check(self):
        if Present.getByKey(self.__presentidlist):
            raise AppTestError(u'プレゼントが残っている')
        elif len(PresentReceived.getByKey(self.__presentidlist)) != len(self.__presentidlist):
            raise AppTestError(u'受取済みプレゼントが設定されていない')
        
        uid = self.__player0.id
        
        # お金.
        playergold = PlayerGold.getByKey(uid)
        if playergold.gold != (self.__player0.gold + 100):
            raise AppTestError(u'お金をうまく受け取れていない')
        
        # 引抜ポイントと引抜チケット.
        playergachapt = PlayerGachaPt.getByKey(uid)
        if playergachapt.gachapt != (self.__player0.gachapt + 100):
            raise AppTestError(u'引抜ポイントをうまく受け取れていない')
        elif playergachapt.tryluckticket != (self.__player0.tryluckticket + 100):
            raise AppTestError(u'引抜チケットをうまく受け取れていない')
        
        # アイテム.
        itemnum = BackendApi.get_item_nums(ModelRequestMgr(), self.__player0.id, [Defines.ItemEffect.ACTION_ALL_RECOVERY]).get(Defines.ItemEffect.ACTION_ALL_RECOVERY, 0)
        if itemnum != 1:
            raise AppTestError(u'アイテムをうまく受け取れていない')
        
        # カード.
        cardnum = BackendApi.get_cardnum(self.__player0.id)
        if (self.__cardnum + 1) != cardnum:
            raise AppTestError(u'カードをうまく受け取れていない')
