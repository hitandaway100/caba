# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.test.dummy_factory import DummyType
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
from defines import Defines
from platinumegg.app.cabaret.models.SerialCampaign import SerialCode,\
    SerialCount

class ApiTest(ApiTestBase):
    """シリアルコード入力ページ(入力成功).
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, gachapt=10)
        
        # シリアルマスター.
        self.__serialmaster = self.create_dummy(DummyType.SERIAL_CAMPAIGN_MASTER, prizes=[prize.id], limit_pp=1)
        
        # シリアルコード.
        self.__serialcode = self.create_dummy(DummyType.SERIAL_CODE, self.__serialmaster.id)
        
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
        
        if (self.__present_num+2) != BackendApi.get_present_num(self.__player.id):
            raise AppTestError(u'プレゼントの配布数が想定外です')
        
        serialcode = SerialCode.getByKey(self.__serialcode.id)
        if serialcode.uid != self.__player.id:
            raise AppTestError(u'入力したユーザーが保存されていない')
        
        serialcount = SerialCount.getByKey(SerialCount.makeID(self.__player.id, self.__serialmaster.id))
        if serialcount is None or serialcount.cnt != 1:
            raise AppTestError(u'シリアルコード入力回数が保存されていない')
