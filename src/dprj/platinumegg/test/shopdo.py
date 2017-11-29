# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.app.cabaret.models.PaymentEntry import ShopPaymentEntry
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.lib.platform.api.objects import PaymentData

class ApiTest(ApiTestBase):
    """ショップ購入実行.
    """
    def setUp(self):
        # アイテム.
        item = self.create_dummy(DummyType.ITEM_MASTER)
        self.__item = item
        
        # 商品.
        self.__shopitem = self.create_dummy(DummyType.SHOP_ITEM_MASTER, Defines.ItemType.ITEM, item.id, 1)
        
        # プレイヤー.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        # 購入情報.
        self.create_dummy(DummyType.SHOP_ITEM_BUY_DATA, self.__player.id, self.__shopitem.id)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID : self.__player.dmmid,
            Defines.URLQUERY_NUMBER : 2,
        }
    
    def get_urlargs(self):
        return '/%d' % self.__shopitem.id
    
    def check(self):
        model_mgr = ModelRequestMgr()
        paymentId = self.response.get('paymentId', None)
        entry = BackendApi.get_shoppaymententry(model_mgr, paymentId)
        if entry is None:
            raise AppTestError(u'課金レコードが作成されていない')
        elif entry.state != PaymentData.Status.CREATE:
            raise AppTestError(u'課金ステータスが異常です.status=%s' % entry.state)
        self.__paymentId = paymentId
    
    def finish(self):
        # チェック後にやりたいこと.
        entry = ShopPaymentEntry.getByKey(self.__paymentId)
        if entry:
            model_mgr = ModelRequestMgr()
            model_mgr.set_delete(entry)
            model_mgr.write_all()
            model_mgr.write_end()
