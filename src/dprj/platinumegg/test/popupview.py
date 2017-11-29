# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.redisdb import PopupViewTime, PopupResetTime

class ApiTest(ApiTestBase):
    """ポップアップ閲覧.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        # バナー.
        eventbanner = self.create_dummy(DummyType.EVENT_BANNER_MASTER)
        
        # ポップアップ.
        popup = self.create_dummy(DummyType.POPUP_MASTER, banner=eventbanner)
        self.__popup = popup
    
    def get_urlargs(self):
        return '/%d' % self.__popup.id
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def check(self):
        print self.response
        # 閲覧フラグ.
        resettime_model = PopupResetTime.get()
        model = PopupViewTime.get(self.__player.id)
        if not self.__popup.id in model.get_viewed_midlist(resettime_model.rtime):
            raise AppTestError(u'閲覧フラグが立っていない')
        elif not self.response['result'].get('popupbanner', None):
            raise AppTestError(u'ポップアップの情報がない')
