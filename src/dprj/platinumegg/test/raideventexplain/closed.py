# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.scout import ScoutDropItemData,\
    ScoutHappeningData
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
import datetime

class ApiTest(ApiTestBase):
    """レイドイベント説明(終了済イベント).
    """
    def setUp(self):
        model_mgr = ModelRequestMgr()
        now = OSAUtil.get_now()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # アイテム.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER)
        data = ScoutDropItemData.create(Defines.ItemType.ITEM, itemmaster.id, filters={'ptype':Defines.CharacterType.TYPE_001}, rate=10000)
        items = [data.get_dropitem_dict()]
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, gachapt=10, item=itemmaster)
        
        # レイドマスター.
        raidmaster = self.create_dummy(DummyType.RAID_MASTER, hp=1, prizes=[prize.id], helpprizes=[prize.id], cabaretking=100, demiworld=10)
        self.__raidmaster = raidmaster
        
        # ハプニング.
        happeningmaster = self.create_dummy(DummyType.HAPPENING_MASTER, raidmaster.id, items=items)
        self.__happeningmaster = happeningmaster
        
        # レイドイベント.
        data = ScoutHappeningData.create(happeningmaster.id, 10000)
        happenings = [data.get_dict()]
        eventmaster = self.create_dummy(DummyType.RAID_EVENT_MASTER, raidtable=happenings)
        self.__eventmaster = eventmaster
        
        # イベント発生中設定.
        config = BackendApi.get_current_raideventconfig(model_mgr)
        self.__preconfig_mid = config.mid
        self.__preconfig_starttime = config.starttime
        self.__preconfig_endtime = config.endtime
        self.__preconfig_timebonus = config.timebonus_time
        timebonus_time = [{
            'stime' : now,
            'etime' : now + datetime.timedelta(days=1),
        }]
        now = OSAUtil.get_now()
        BackendApi.update_raideventconfig(self.__eventmaster.id, now - datetime.timedelta(days=1), now - datetime.timedelta(days=1), timebonus_time=timebonus_time)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        return '/%s/' % (self.__eventmaster.id)
    
    def check(self):
        keys = (
            'is_opened',
            'url_raidevent_top',
            'url_raidevent_ranking',
            'url_explain_detail',
            'url_explain_prizes',
            'url_explain_faq',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        if self.response.get('is_opened'):
            raise AppTestError(u'イベントが発生してしまっている')
    
    def finish(self):
        model_mgr = ModelRequestMgr()
        config = BackendApi.get_current_raideventconfig(model_mgr)
        config.mid = self.__preconfig_mid
        config.starttime = self.__preconfig_starttime
        config.endtime = self.__preconfig_endtime
        config.timebonus_time = self.__preconfig_timebonus
        model_mgr.set_save(config)
        model_mgr.write_all()
        model_mgr.write_end()
