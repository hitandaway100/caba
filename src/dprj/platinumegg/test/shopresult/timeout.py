# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.lib.platform.api.objects import PaymentData
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """ショップ購入結果(期限切れ).
    """
    def setUp(self):
        
        self.__buy_num = 2
        
        # アイテム.
        item = self.create_dummy(DummyType.ITEM_MASTER)
        self.__item = item
        
        # 商品.
        self.__shopitem = self.create_dummy(DummyType.SHOP_ITEM_MASTER, Defines.ItemType.ITEM, item.id, 1)
        
        # プレイヤー.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        # アイテム所持数.
        self.__itemnum = self.create_dummy(DummyType.ITEM, self.__player, self.__item, rnum=0)
        
        # 購入情報.
        self.create_dummy(DummyType.SHOP_ITEM_BUY_DATA, self.__player.id, self.__shopitem.id)
        
        # 課金レコード.
        self.__payment_entry = self.create_dummy(DummyType.SHOP_PAYMENT_ENTRY, self.__player.id, self.__shopitem.id, self.__buy_num, PaymentData.Status.START)
        
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            'paymentId' : self.__payment_entry.id,
            Defines.URLQUERY_STATE : PaymentData.Status.TIMEOUT,
        }
    
    def get_urlargs(self):
        return '/%s' % (self.__shopitem.id)
    
    def check(self):
        model_mgr = ModelRequestMgr()
        entry = BackendApi.get_shoppaymententry(model_mgr, self.__payment_entry.id)
        if entry is None:
            raise AppTestError(u'課金レコードが作成されていない')
        elif entry.state != PaymentData.Status.TIMEOUT:
            raise AppTestError(u'課金ステータスが異常です.status=%s' % entry.state)
