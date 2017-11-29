# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.test.cabaclubtestpage import CabaclubTest

class ApiTest(CabaclubTest):
    """キャバクラ経営店舗レンタル完了.
    """
    
    def setUp(self):
        ua_type = Defines.CabaClubEventUAType.LIVEN_UP
        # ユーザーを用意.
        self.__player = self.create_dummy(DummyType.PLAYER)
        # 店舗を用意.
        cabaclub_dummy = self.setUpCabaclub(self.__player)
        self.__cabaclub_dummy = cabaclub_dummy
        self.__storemaster = cabaclub_dummy.stores[ua_type]
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_DAYS : self.__storemaster.days_0,
        }
        return params
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%d' % self.__storemaster.id
    
    def check(self):
        arr = (
            'url_store',
        )
        for k in arr:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない' % k)

