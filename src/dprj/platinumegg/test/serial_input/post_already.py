# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.test.dummy_factory import DummyType
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
from defines import Defines

class ApiTest(ApiTestBase):
    """シリアルコード入力ページ(既に使用済み).
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, gachapt=10)
        
        # シリアルマスター.
        self.__serialmaster = self.create_dummy(DummyType.SERIAL_CAMPAIGN_MASTER, prizes=[prize.id], limit_pp=1)
        
        # シリアルコード.
        self.__serialcode = self.create_dummy(DummyType.SERIAL_CODE, self.__serialmaster.id, uid=self.__player.id)
        
        # プレゼント数.
        self.__present_num = BackendApi.get_present_num(self.__player.id)
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%s' % self.__serialmaster.id
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_SERIALCODE : self.__serialcode.serial,
        }
    
    def check(self):
        keys = (
            'url_input',
            'message',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        if self.__present_num != BackendApi.get_present_num(self.__player.id):
            raise AppTestError(u'プレゼントが配布されています')
