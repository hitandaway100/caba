# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.test.cabaclubtestpage import CabaclubTest

class ApiTest(CabaclubTest):
    """キャバクラ店舗配置キャスト選択(変更).
    """
    
    def setUp(self):
        ua_type = Defines.CabaClubEventUAType.LIVEN_UP
        # ユーザーを用意.
        self.__player = self.create_dummy(DummyType.PLAYER)
        # 店舗を用意.
        cabaclub_dummy = self.setUpCabaclub(self.__player)
        self.__cabaclub_dummy = cabaclub_dummy
        self.__storemaster = cabaclub_dummy.stores[ua_type]
        # キャストを配置しておく.
        self.create_dummy(DummyType.CABA_CLUB_CAST_PLAYER_DATA, self.__player.id, self.__storemaster.id, cabaclub_dummy.cardlist[1:])
        self.__cardid = cabaclub_dummy.cardlist[0].id
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%d/%d' % (self.__storemaster.id, self.__cardid)
    
    def check(self):
        arr = (
            'current_card',
            'cardlist',
            'url_store',
            'cardlist',
            'ctype_items',
            'sort_items',
            Defines.URLQUERY_CTYPE,
            Defines.URLQUERY_SORTBY,
            Defines.URLQUERY_PAGE,
        )
        for k in arr:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない' % k)
        obj_card = self.response['current_card']
        if not obj_card or obj_card['id'] != self.__cardid:
            raise AppTestError(u'cardが想定外')
