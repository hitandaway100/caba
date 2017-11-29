# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.promotion import PromotionSettings

class ApiTest(ApiTestBase):
    """クロスプロモーション達成条件取得.
    """
    
    def setUp(self):
        self.create_dummy(DummyType.PROMOTION_CONFIG_KOIHIME)
        
        NUM = 8
        masterlist = []
        for i in xrange(NUM):
            masterlist.append(self.create_dummy(DummyType.PROMOTION_REQUIREMENT_MASTER_KOIHIME, condition_value=(i+1)))
        self.__masterlist = masterlist
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return '/%s/%s' % (PromotionSettings.Apps.KOIHIME, ','.join([str(master.id) for master in self.__masterlist]))
    
    def check(self):
        
        for master in self.__masterlist:
            text = self.response.get(str(master.id))
            if text != master.text:
                raise AppTestError(u'テキストが一致しません:%s vs %s' % (text, master.text))
