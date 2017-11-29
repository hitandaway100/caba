# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Happening import Happening
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi

class ApiTest(ApiTestBase):
    """ハプニング諦める書き込み.
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # アイテム.
        item = self.create_dummy(DummyType.ITEM_MASTER)
        
        # レイド.
        raidmaster = self.create_dummy(DummyType.RAID_MASTER)
        
        # ハプニング.
        happeningmaster = self.create_dummy(DummyType.HAPPENING_MASTER, raidmaster.id)
        self.__happeningmaster = happeningmaster
        
        # ハプニング情報.
        happening = self.create_dummy(DummyType.HAPPENING, self.__player0.id, self.__happeningmaster.id)
        happening.gold = 10
        happening.addDropItem(Defines.ItemType.ITEM, item.id)
        happening.save()
        self.__happening = happening
        
        self.__present_num = BackendApi.get_present_idlist(self.__player0.id)
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/do'
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        # 進行情報があるかを確認.
        playdata = Happening.getByKey(self.__happening.id)
        if playdata is None or not playdata.is_canceled():
            raise AppTestError(u'進行情報が保存されていない')
        
        # 報酬.
#        if self.__present_num == BackendApi.get_present_idlist(self.__player0.id):
#            raise AppTestError(u'報酬が付与されていない')
