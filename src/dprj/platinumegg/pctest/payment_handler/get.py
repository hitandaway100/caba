# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.test.dummy_factory import DummyType
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines

class ApiTest(ApiTestBase):
    """PC版決済確定.
    """
    
    @classmethod
    def makeRequestUrl(cls, api):
        return "/pc/%s" % api
    
    def setUp(self):
        # ダミーデータを設定する
        # payment-id
        self.payment_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_APP_ID : '402286',
            'payment_id' : self.payment_id,
        }
    
    def check(self):
        if 'response_code' not in self.response:
            raise AppTestError(u'response_codeが無い.')
        if 'payment_id' not in self.response:
            raise AppTestError(u'payment_idが無い.')
        elif self.response['response_code'] != 'OK':
            raise AppTestError(u'response_codeがOKでない.%s' % self.response['response_code'])
        elif self.response['payment_id'] != self.payment_id:
            raise AppTestError(u'payment_idが不一致.%s' % self.response['payment_id'])
