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
    """レイドイベント討伐報酬受け取り演出.
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
        self.__prize = prize
        
        # レイドマスター.
        raidmaster = self.create_dummy(DummyType.RAID_MASTER, hp=1, prizes=[prize.id], helpprizes=[prize.id], cabaretking=100, demiworld=10)
        self.__raidmaster = raidmaster
        
        # ハプニング.
        happeningmaster = self.create_dummy(DummyType.HAPPENING_MASTER, raidmaster.id, items=items)
        self.__happeningmaster = happeningmaster
        
        # レイドイベント.
        data = ScoutHappeningData.create(happeningmaster.id, 10000)
        happenings = [data.get_dict()]
        destroyprizes = [
            [1, [prize.id]],
        ]
        eventmaster = self.create_dummy(DummyType.RAID_EVENT_MASTER, raidtable=happenings, destroyprizes=destroyprizes)
        self.__eventmaster = eventmaster
        
        # イベント用レイド設定.
        raideventraidmaster = self.create_dummy(DummyType.RAID_EVENT_RAID_MASTER, self.__eventmaster.id, self.__raidmaster.id)
        self.__raideventraidmaster = raideventraidmaster
        
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
        config = BackendApi.update_raideventconfig(self.__eventmaster.id, now, now + datetime.timedelta(days=1), timebonus_time=timebonus_time)
        
        # オープニングとタイムボーナスを閲覧済みにする.
        eventflagrecord = self.create_dummy(DummyType.RAID_EVENT_FLAGS, self.__eventmaster.id, self.__player0.id, tbvtime=config.starttime)
        self.__eventflagrecord = eventflagrecord
        
        # イベントスコア.
        eventscore = self.create_dummy(DummyType.RAID_EVENT_SCORE, self.__eventmaster.id, self.__player0.id, destroy=1)
        self.__eventscore = eventscore
        
        # ハプニング情報.
        happening = self.create_dummy(DummyType.HAPPENING, self.__player0.id, self.__happeningmaster.id,  progress=happeningmaster.execution, eventid=self.__eventmaster.id)
        self.__happening = happening
        
        # レイド.
        raidboss = self.create_dummy(DummyType.RAID, self.__player0, happeningmaster, happening)
        raidboss.addDamageRecord(self.__player0.id, 1)
        raidboss.refrectDamageRecord()
        raidboss.raid.save()
        self.__raid = raidboss
        
        # 報酬受取り.
        model_mgr = ModelRequestMgr()
        BackendApi.tr_receive_raidevent_destroyprize(model_mgr, self.__player0.id, self.__eventmaster, self.__player0.req_confirmkey)
        model_mgr.write_all()
        model_mgr.write_end()
    
    def get_urlargs(self):
        return '/anim/%d' % self.__eventmaster.id
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        keys = (
            'backUrl',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        url = self.response.get('redirect_url')
        if not url:
            raise AppTestError(u'リダイレクト先が設定されていない')
        elif url.find('/levelup/effect_dev.html') == -1:
            raise AppTestError(u'演出に遷移していない')
    
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
