# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerGold,\
    PlayerDeck, PlayerTreasure, PlayerRequest
from platinumegg.app.cabaret.util.scout import ScoutDropItemData,\
    ScoutHappeningData
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import urllib
import datetime
from platinumegg.app.cabaret.models.Happening import RaidPrizeDistributeQueue

class ApiTest(ApiTestBase):
    """レイド攻撃(イベントで倒した).
    """
    def setUp(self):
        model_mgr = ModelRequestMgr()
        now = OSAUtil.get_now()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        self.__player1 = self.create_dummy(DummyType.PLAYER)
        
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
        eventmaster = self.create_dummy(DummyType.RAID_EVENT_MASTER, raidtable=happenings, champagne_num_max=10, champagne_time=300)
        self.__eventmaster = eventmaster
        
        # イベント用レイド設定.
        raideventraidmaster = self.create_dummy(DummyType.RAID_EVENT_RAID_MASTER, self.__eventmaster.id, self.__raidmaster.id, ownerpoint=10, mvppoint=20)
        self.__raideventraidmaster = raideventraidmaster
        
        # シャンパン情報.
        champagnedata = self.create_dummy(DummyType.RAID_EVENT_CHAMPAGNE, self.__player0.id, eventmaster.id, 0, etime=now + datetime.timedelta(seconds=eventmaster.champagne_time))
        self.__champagnedata = champagnedata
        
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
        
        # ハプニング情報.
        happening = self.create_dummy(DummyType.HAPPENING, self.__player0.id, self.__happeningmaster.id,  progress=happeningmaster.execution, eventid=self.__eventmaster.id)
        self.__happening = happening
        
        # レイド.
        raidboss = self.create_dummy(DummyType.RAID, self.__player0, happeningmaster, happening)
        raidboss.addDamageRecord(self.__player0.id, 1)
        raidboss.refrectDamageRecord()
        raidboss.raid.save()
        self.__raid = raidboss
        
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
        
        addRequest(self.__player0, self.__player1)
        addFriend(self.__player1, self.__player0)
        
        model_mgr = ModelRequestMgr()
        BackendApi.tr_send_raidhelp(model_mgr, self.__player0.id)
        model_mgr.write_all()
        model_mgr.write_end()
        
        raidboss.addDamageRecord(self.__player1.id, 1)
        raidboss.refrectDamageRecord()
        raidboss.raid.save()
        
        self.__player0.gold = 0
        self.__player0.getModel(PlayerGold).save()
        
        self.__player0.cardlimititem = 100
        self.__player0.getModel(PlayerDeck).save()
        
        self.__playerhappening = BackendApi.get_playerhappening(model_mgr, self.__player0.id)
        
        self.__present_num0 = BackendApi.get_present_num(self.__player0.id)
        self.__present_num1 = BackendApi.get_present_num(self.__player1.id)
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/do/%d/%s' % (self.__raid.id, urllib.quote(self.__player0.req_confirmkey, ''))
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        model_mgr = ModelRequestMgr()
        
        # 確認キー.
        playerrequest = BackendApi.get_model(model_mgr, PlayerRequest, self.__player0.id)
        if self.__player0.req_confirmkey == playerrequest.req_confirmkey:
            raise AppTestError(u'確認キーが更新されていない')
        elif self.__player0.req_confirmkey != playerrequest.req_alreadykey:
            raise AppTestError(u'確認済みのキーが更新されていない')
        
        # ハプニング.
        happeningset = BackendApi.get_happening(model_mgr, self.__raid.id)
        if happeningset.happening.state != Defines.HappeningState.END:
            raise AppTestError(u'状態が正しくない')
        
        # ダメージレコード.
        raidboss = BackendApi.get_raid(model_mgr, self.__raid.id)
        record = raidboss.getDamageRecord(self.__player0.id)
        if record.damage == 0 or record.damage_cnt == 0:
            raise AppTestError(u'ダメージが記録されていない')
        elif not record.champagne:
            raise AppTestError(u'シャンパンコールフラグが立っていない')
        
        # ダメージ.
        record_pre = self.__raid.getDamageRecord(self.__player0.id)
        if (self.__raid.raid.hp - (record.damage - record_pre.damage)) != raidboss.raid.hp:
            raise AppTestError(u'ダメージが正しくない')
        
        # 秘宝.
        playertreasure0 = PlayerTreasure.getByKey(self.__player0.id)
        if playertreasure0.cabaretking != self.__raid.get_cabaretking():
            raise AppTestError(u'キャバ王の秘宝が付与されていない')
        
        # 報酬.
        present_num0 = BackendApi.get_present_num(self.__player0.id)
        if self.__present_num0 == present_num0:
            raise AppTestError(u'発見者に報酬が付与されていない')
        
        # イベントポイント.
        scorerecord0 = BackendApi.get_raidevent_scorerecord(model_mgr, self.__eventmaster.id, self.__player0.id)
        pointtable = BackendApi.aggregate_raidevent_destroypoint(model_mgr, self.__eventmaster, raidboss)
        arr = pointtable.get(self.__player0.id)
        if not arr:
            raise AppTestError(u'発見者にイベントポイントが付与されていない')
        elif len(arr) != 2:
            raise AppTestError(u'発見者にMVPポイントが付与されていない')
        elif sum(arr) != scorerecord0.point or sum(arr) != scorerecord0.point_total:
            raise AppTestError(u'発見者にポイントがただしく付与されていない')
        
        arr = pointtable.get(self.__player1.id)
        if not arr:
            raise AppTestError(u'協力者にイベントポイントが付与されていない')
        
        if Defines.RAID_PRIZE_DISTRIBUTION_OUTSIDE:
            queue = RaidPrizeDistributeQueue.getValues(filters={'raidid':self.__raid.id})
            if queue is None:
                raise AppTestError(u'報酬配布用のキューが作成されていない')
            
            def write(queue, happening, raidboss, help_prizelist):
                model_mgr = ModelRequestMgr()
                BackendApi.tr_distribute_raid(model_mgr, queue, happening, raidboss, help_prizelist)
                model_mgr.write_all()
                model_mgr.write_end()
            help_prizelist = BackendApi.get_prizelist(model_mgr, raidboss.master.helpprizes)
            write(queue, BackendApi.get_happening(model_mgr, raidboss.id).happening, raidboss, help_prizelist)
        
        # 救援者の報酬を確認.
        present_num1 = BackendApi.get_present_num(self.__player1.id)
        if self.__present_num1 == present_num1:
            raise AppTestError(u'救援者に報酬が付与されていない')
        
        playertreasure1 = PlayerTreasure.getByKey(self.__player1.id)
        if 0 < self.__raid.get_demiworld() and playertreasure1.demiworld != self.__raid.get_demiworld():
            raise AppTestError(u'裏社会の秘宝が付与されていない')
        
        scorerecord1 = BackendApi.get_raidevent_scorerecord(model_mgr, self.__eventmaster.id, self.__player1.id)
        if len(arr) != 1 or sum(arr) != scorerecord1.point or sum(arr) != scorerecord1.point_total:
            raise AppTestError(u'協力者にポイントがただしく付与されていない')
    
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
