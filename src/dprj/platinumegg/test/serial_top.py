# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.test.dummy_factory import DummyType
from platinumegg.lib.opensocial.util import OSAUtil

class ApiTest(ApiTestBase):
    """シリアルコード入力キャンペーンTOP.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, gachapt=10)
        
        # シリアルマスター.
        self.__serialmaster = self.create_dummy(DummyType.SERIAL_CAMPAIGN_MASTER, prizes=[prize.id])
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%s' % self.__serialmaster.id
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def check(self):
        keys = (
            'serialcampaign',
            'is_open',
            'url_input',
            'prize',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
