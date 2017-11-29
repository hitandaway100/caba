# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError, ApiTestBase
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.scout import ScoutDropItemData,\
    ScoutHappeningData
from defines import Defines

class ApiTest(ApiTestBase):
    """レイドイベントレシピ一覧.
    """
    def setUp(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # アイテム.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER)
        data = ScoutDropItemData.create(Defines.ItemType.ITEM, itemmaster.id, filters={'ptype':Defines.CharacterType.TYPE_001}, rate=10000)
        items = [data.get_dropitem_dict()]
        
        # 素材.
        materialidlist = []
        materialnumlist = []
        for _ in xrange(Defines.RAIDEVENT_MATERIAL_KIND_MAX):
            materialmaster = self.create_dummy(DummyType.RAID_EVENT_MATERIAL_MASTER)
            materialidlist.append(materialmaster.id)
            materialnumlist.append(100)
        
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
        destroyprizes = [
            [1, [prize.id]],
        ]
        scenario = self.create_dummy(DummyType.EVENT_SCENARIO_MASTER)
        eventmaster = self.create_dummy(DummyType.RAID_EVENT_MASTER, raidtable=happenings, destroyprizes=destroyprizes, op=scenario.number, ed=scenario.number, materiallist=materialidlist)
        self.__eventmaster = eventmaster
        
        # レシピ.
        recipemaster = self.create_dummy(DummyType.RAID_EVENT_RECIPE_MASTER, eventmaster.id, material_num_list=materialnumlist)
        self.__recipemaster = recipemaster
        
        # 素材の所持数.
        materialdata = self.create_dummy(DummyType.RAID_EVENT_MATERIAL_DATA, self.__player0.id, eventmaster.id, materialnumlist)
        self.__materialdata = materialdata
        
        # イベント用レイド設定.
        raideventraidmaster = self.create_dummy(DummyType.RAID_EVENT_RAID_MASTER, self.__eventmaster.id, self.__raidmaster.id)
        self.__raideventraidmaster = raideventraidmaster
        
        # イベント終了設定.
        config = BackendApi.get_current_raideventconfig(model_mgr)
        self.__preconfig_mid = config.mid
        self.__preconfig_starttime = config.starttime
        self.__preconfig_endtime = config.endtime
        self.__preconfig_ticket_endtime = config.ticket_endtime
        config = BackendApi.update_raideventconfig(self.__eventmaster.id, OSAUtil.get_datetime_min(), OSAUtil.get_datetime_min(), ticket_endtime=OSAUtil.get_datetime_max())
        
        # オープニングとタイムボーナスを閲覧済みにする.
        eventflagrecord = self.create_dummy(DummyType.RAID_EVENT_FLAGS, self.__eventmaster.id, self.__player0.id, tbvtime=config.starttime)
        self.__eventflagrecord = eventflagrecord
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        keys = (
            'recipelist',
            'is_cardnum_max',
            'url_raidevent_top',
            'raidevent_materials',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
    
    def finish(self):
        model_mgr = ModelRequestMgr()
        config = BackendApi.get_current_raideventconfig(model_mgr)
        config.mid = self.__preconfig_mid
        config.starttime = self.__preconfig_starttime
        config.endtime = self.__preconfig_endtime
        config.ticket_endtime = self.__preconfig_ticket_endtime
        model_mgr.set_save(config)
        model_mgr.write_all()
        model_mgr.write_end()
