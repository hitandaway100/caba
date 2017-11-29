# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.scout import ScoutDropItemData,\
    ScoutHappeningData
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import datetime

class ApiTest(ApiTestBase):
    """レイド攻撃(救援で倒した).
    """
    def setUp(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER, friendlimit=100)
        
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
        
        # イベント用レイド設定.
        raideventraidmaster = self.create_dummy(DummyType.RAID_EVENT_RAID_MASTER, self.__eventmaster.id, self.__raidmaster.id)
        self.__raideventraidmaster = raideventraidmaster
        
        # イベント発生中設定.
        config = BackendApi.get_current_raideventconfig(model_mgr)
        self.__preconfig_mid = config.mid
        self.__preconfig_starttime = config.starttime
        self.__preconfig_endtime = config.endtime
        self.__preconfig_timebonus = config.timebonus_time
        timebonus_time = []
        now = OSAUtil.get_now()
        BackendApi.update_raideventconfig(self.__eventmaster.id, now, now + datetime.timedelta(days=1), timebonus_time=timebonus_time)
        
        # 救援.
        def addRequest(v_player, o_player):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_friendrequest(model_mgr, v_player, o_player)
            model_mgr.write_all()
            model_mgr.write_end()
        
        def addFriend(v_player, o_player):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_friend(model_mgr, v_player.id, o_player.id)
            model_mgr.write_all()
            model_mgr.write_end()
        
        for _ in xrange(20):
            player = self.create_dummy(DummyType.PLAYER, friendlimit=100)
            addRequest(self.__player0, player)
            addFriend(player, self.__player0)
            
            # ハプニング情報.
            happening = self.create_dummy(DummyType.HAPPENING, player.id, self.__happeningmaster.id,  progress=happeningmaster.execution, eventid=self.__eventmaster.id)
            
            # レイド.
            raidboss = self.create_dummy(DummyType.RAID, player, happeningmaster, happening)
            raidboss.addDamageRecord(player.id, 1)
            raidboss.refrectDamageRecord()
            raidboss.raid.save()
            
            model_mgr = ModelRequestMgr()
            BackendApi.tr_send_raidhelp(model_mgr, player.id)
            model_mgr.write_all()
            model_mgr.write_end()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        keys = (
            'url_raidevent_top',
            'raidhelplist',
            'url_page_next',
            'cur_page',
            'page_max',
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
        config.timebonus_time = self.__preconfig_timebonus
        model_mgr.set_save(config)
        model_mgr.write_all()
        model_mgr.write_end()
