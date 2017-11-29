# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError, ApiTestBase
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.scout import ScoutHappeningData
from defines import Defines
import urllib
from platinumegg.app.cabaret.util.url_maker import UrlMaker

class ApiTest(ApiTestBase):
    """レイドイベントレシピ交換の書き込み.
    """
    def setUp(self):
        model_mgr = ModelRequestMgr()
        
        trade_num = 8
        recipe_material_num = 10
        self.__trade_num = trade_num
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # アイテム.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER)
        self.__itemmaster = itemmaster
        
        # アイテムの所持数.
        item = self.create_dummy(DummyType.ITEM, self.__player0, itemmaster)
        self.__item = item
        
        # 素材.
        materialidlist = []
        materialnumlist = []
        for _ in xrange(Defines.RAIDEVENT_MATERIAL_KIND_MAX):
            materialmaster = self.create_dummy(DummyType.RAID_EVENT_MATERIAL_MASTER)
            materialidlist.append(materialmaster.id)
            materialnumlist.append(recipe_material_num)
        
        # レイドマスター.
        raidmaster = self.create_dummy(DummyType.RAID_MASTER, hp=1, prizes=[], helpprizes=[], cabaretking=100, demiworld=10)
        self.__raidmaster = raidmaster
        
        # ハプニング.
        happeningmaster = self.create_dummy(DummyType.HAPPENING_MASTER, raidmaster.id, items=[])
        self.__happeningmaster = happeningmaster
        
        # レイドイベント.
        data = ScoutHappeningData.create(happeningmaster.id, 10000)
        happenings = [data.get_dict()]
        destroyprizes = []
        scenario = self.create_dummy(DummyType.EVENT_SCENARIO_MASTER)
        eventmaster = self.create_dummy(DummyType.RAID_EVENT_MASTER, raidtable=happenings, destroyprizes=destroyprizes, op=scenario.number, ed=scenario.number, materiallist=materialidlist)
        self.__eventmaster = eventmaster
        
        # レシピ.
        itype = Defines.ItemType.ITEM
        itemid = self.__itemmaster.id
        itemnum = 1
        recipemaster = self.create_dummy(DummyType.RAID_EVENT_RECIPE_MASTER, eventmaster.id, itype=itype, itemid=itemid, itemnum=itemnum, stock=trade_num, material_num_list=materialnumlist)
        self.__recipemaster = recipemaster
        
        # 交換回数.
        mixdata = self.create_dummy(DummyType.RAID_EVENT_MIX_DATA, self.__player0.id, recipemaster, 0)
        self.__mixdata = mixdata
        
        # 素材の所持数.
        materialdata = self.create_dummy(DummyType.RAID_EVENT_MATERIAL_DATA, self.__player0.id, eventmaster.id, [materialnum * trade_num for materialnum in materialnumlist])
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
            '_num' : self.__trade_num,
        }
    
    def get_urlargs(self):
        return '/%s/%s' % (self.__recipemaster.id, urllib.quote(self.__player0.req_confirmkey, ''))
    
    def check(self):
        redirect_url = self.response.get('redirect_url', None)
        if not redirect_url:
            raise AppTestError(u'リダイレクト先が設定されていない')
        elif redirect_url.find(UrlMaker.raidevent_recipe_complete(self.__recipemaster.id)) == -1:
            raise AppTestError(u'リダイレクト先が正しくない')
        
        model_mgr = ModelRequestMgr()
        # 素材数.
        materialdata = BackendApi.get_raidevent_materialdata(model_mgr, self.__player0.id)
        if materialdata is None:
            raise AppTestError(u'素材情報が見つからない')
        elif 0 < sum([0 if materialdata.getMaterialNum(self.__eventmaster.id, i)==0 else 1 for i in xrange(Defines.RAIDEVENT_MATERIAL_KIND_MAX)]):
            raise AppTestError(u'素材数が想定外')
        
        # 交換回数.
        mixdata = BackendApi.get_raidevent_mixdata(model_mgr, self.__player0.id, self.__recipemaster.id)
        if mixdata is None:
            raise AppTestError(u'交換回数情報が見つからない')
        elif mixdata.getCount(self.__eventmaster.id) != (self.__mixdata.getCount(self.__eventmaster.id) + self.__trade_num):
            raise AppTestError(u'交換回数が想定外')
        
        # アイテム.
        itemnum = BackendApi.get_item_nums(model_mgr, self.__player0.id, [self.__itemmaster.id]).get(self.__itemmaster.id, None)
        if itemnum != (self.__item.num + self.__recipemaster.itemnum * self.__trade_num):
            raise AppTestError(u'アイテムの所持数が想定外 %s vs %s' % (itemnum, (self.__item.num + self.__recipemaster.itemnum)))
    
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
