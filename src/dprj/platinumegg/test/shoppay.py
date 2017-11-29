# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.lib.platform.api.objects import PaymentData

class ApiTest(ApiTestBase):
    """ショップ購入(ユーザー確認済みの状態にする).
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
        
        # 購入情報.
        self.create_dummy(DummyType.SHOP_ITEM_BUY_DATA, self.__player.id, self.__shopitem.id)
        
        # 課金レコード.
        self.__payment_entry = self.create_dummy(DummyType.SHOP_PAYMENT_ENTRY, self.__player.id, self.__shopitem.id, self.__buy_num, PaymentData.Status.CREATE)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID : self.__player.dmmid,
            'paymentId' : self.__payment_entry.id,
        }
    
    def check(self):
        model_mgr = ModelRequestMgr()
        paymentId = self.response.get('paymentId', None)
        if self.__payment_entry.id != paymentId:
            raise AppTestError(u'paymentIdが違う. %s vs %s' % (self.__payment_entry.id, paymentId))
        
        entry = BackendApi.get_shoppaymententry(model_mgr, paymentId)
        if entry is None:
            raise AppTestError(u'課金レコードが作成されていない')
        elif entry.state != PaymentData.Status.START:
            raise AppTestError(u'課金ステータスが異常です.status=%s' % entry.state)
