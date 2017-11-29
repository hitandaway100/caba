# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.test.dummy_factory import DummyType
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines

class ApiTest(ApiTestBase):
    """PC版決済確認.
    """
    
    @classmethod
    def makeRequestUrl(cls, api):
        return "/pc/%s" % api
    
    def setUp(self):
        # ダミーデータを設定する
        # アイテム.
        item = self.create_dummy(DummyType.ITEM_MASTER)
        
        # 商品.
        shopitem = self.create_dummy(DummyType.SHOP_ITEM_MASTER, Defines.ItemType.ITEM, item.id, 1)
        self.shopitem = shopitem
        
        # payment-id
        self.payment_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    
    def get_args(self):
        """APIに送る引数.
        """
        return {
            'ITEMS' : [
                {
                    'PRICE' : self.shopitem.price,
                    'NAME' : self.shopitem.name,
                    'SKU_ID' : self.shopitem.id,
                    'DESCRIPTION' : self.shopitem.text,
                    'COUNT' : 1,
                    'IMAGE_URL' : self.shopitem.thumb,
                }
            ],
            'PAYMENT_TYPE' : 'payment',
            'PAYMENT_ID' : self.payment_id,
            'ORDERER_TIME' : 1284547429317,
        }
    
    def get_query_params(self):
        return {OSAUtil.KEY_APP_ID : '402286'}
    
    def check(self):
        if 'response_code' not in self.response:
            raise AppTestError(u'response_codeが無い.')
        elif self.response['response_code'] != 'OK':
            raise AppTestError(u'response_codeがOKでない.%s' % self.response['response_code'])
