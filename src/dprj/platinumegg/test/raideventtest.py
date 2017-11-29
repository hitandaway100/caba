# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.scout import ScoutDropItemData,\
    ScoutHappeningData
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
import datetime

class RaidEventApiTest(ApiTestBase):
    """レイドイベント.
    """
    
    def setUpRaidEvent(self, player, dedicated_stage_max=0, is_open=True):
        model_mgr = ModelRequestMgr()
        now = OSAUtil.get_now()
        
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
        happeningmaster = self.create_dummy(DummyType.HAPPENING_MASTER, raidmaster.id, execution=0, items=items)
        self.__happeningmaster = happeningmaster
        
        # レイドイベント.
        data = ScoutHappeningData.create(happeningmaster.id, 10000)
        happenings = [data.get_dict()]
        destroyprizes = [
            [1, [prize.id]],
        ]
        eventmaster = self.create_dummy(DummyType.RAID_EVENT_MASTER, raidtable=happenings, destroyprizes=destroyprizes, flag_dedicated_stage=0 < dedicated_stage_max)
        self.__eventmaster = eventmaster
        
        # イベント用レイド設定.
        raideventraidmaster = self.create_dummy(DummyType.RAID_EVENT_RAID_MASTER, self.eventmaster.id, self.raidmaster.id)
        self.__raideventraidmaster = raideventraidmaster
        
        # イベント用ステージ作成.
        stageparams = self.getStageParams() or {}
        stagelist = []
        for stagenumber in xrange(1, dedicated_stage_max+1):
            stagelist.append(self.create_dummy(DummyType.RAID_EVENT_SCOUT_STAGE_MASTER, self.eventmaster.id, stagenumber, prizes=[prize.id], **stageparams))
        self.__stagelist = stagelist
        
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
        if is_open:
            starttime = now
            endtime = now + datetime.timedelta(days=1)
        else:
            starttime = now - datetime.timedelta(days=1)
            endtime = now
        config = BackendApi.update_raideventconfig(self.eventmaster.id, starttime, endtime, timebonus_time=timebonus_time)
        self.raidevent_config = config
    
    @property
    def eventmaster(self):
        return self.__eventmaster
    
    @property
    def happeningmaster(self):
        return self.__happeningmaster
    
    @property
    def raidmaster(self):
        return self.__raidmaster
    
    @property
    def raideventraidmaster(self):
        return self.__raideventraidmaster
    
    @property
    def stagelist(self):
        return self.__stagelist
    
    def getStageParams(self):
        """ステージ情報作成.
        """
        return None
    
    def getStageByNumber(self, number):
        number = max(number, 1)
        return self.__stagelist[number - 1] if number <= len(self.__stagelist) else None
    
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
