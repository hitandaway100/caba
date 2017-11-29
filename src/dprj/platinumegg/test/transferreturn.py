# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
import urllib
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Player import PlayerDeck

class ApiTest(ApiTestBase):
    """異動実行.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        playerdeck = self.__player.getModel(PlayerDeck)
        playerdeck.cardlimititem = 100
        playerdeck.save()
        
        # 異動数.
        cardmaster = self.create_dummy(DummyType.CARD_MASTER, rare=Defines.Rarity.TRANSFER[0])
        self.__card_stock = self.create_dummy(DummyType.CARD_STOCK, self.__player.id, cardmaster.album, 10)
        
        # 移動前のカード数.
        self.__card_num = BackendApi.get_cardnum(self.__player.id)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_NUMBER : self.__card_stock.num,
        }
        return params
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return '/%d/%s' % (self.__card_stock.mid, urllib.quote(self.__player.req_confirmkey, ''))
    
    def check(self):
        card_num = BackendApi.get_cardnum(self.__player.id)
        if (self.__card_num + self.__card_stock.num) != card_num:
            raise AppTestError(u'カードが増えていない')
        
        stocknum_model = BackendApi.get_cardstock(ModelRequestMgr(), self.__player.id, self.__card_stock.mid)
        if stocknum_model is None:
            raise AppTestError(u'ストックのモデルが消えている')
        elif stocknum_model.num != 0:
            raise AppTestError(u'ストックのモデルのストック数が正しく保存されていない')
