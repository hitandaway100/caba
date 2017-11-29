# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
import datetime
from platinumegg.app.cabaret.models.Player import PlayerRequest, PlayerGold,\
    PlayerDeck, PlayerTreasure
from defines import Defines
from platinumegg.app.cabaret.models.Happening import RaidPrizeDistributeQueue
from platinumegg.app.cabaret.util.happening import HappeningUtil

class ApiTest(ApiTestBase):
    """スカウトイベント用のレイド実行(勝利).
    """
    def setUp(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        self.__player1 = self.create_dummy(DummyType.PLAYER)
        
        # 報酬.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER)
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, gachapt=10, item=itemmaster)
        
        # イベントマスター.
        eventmaster = self.create_dummy(DummyType.SCOUT_EVENT_MASTER, lovetime_tanzakuup=100)
        self.__eventmaster = eventmaster
        
        # ステージマスター.
        stagemaster = self.create_dummy(DummyType.SCOUT_EVENT_STAGE_MASTER, eventid=eventmaster.id, stage=1)
        self.__stagemaster = stagemaster
        
        # OPを閲覧済みに.
        flagrecord = self.create_dummy(DummyType.SCOUT_EVENT_FLAGS, self.__player0.id, self.__eventmaster.id, OSAUtil.get_now())
        self.__flagrecord = flagrecord
        
        # 逢引ラブタイム状態にする.
        playdata = self.create_dummy(DummyType.SCOUT_EVENT_PLAY_DATA, self.__player0.id, self.__eventmaster.id, lovetime_etime=OSAUtil.get_now()+datetime.timedelta(days=1))
        self.__scoutevent_playdata = playdata
        
        # イベント発生中設定.
        config = BackendApi.get_current_scouteventconfig(model_mgr)
        self.__preconfig_mid = config.mid
        self.__preconfig_starttime = config.starttime
        self.__preconfig_endtime = config.endtime
        now = OSAUtil.get_now()
        BackendApi.update_scouteventconfig(self.__eventmaster.id, now, now + datetime.timedelta(days=1))
        
        # レイドマスター.
        raidmaster = self.create_dummy(DummyType.RAID_MASTER, hp=1, prizes=[prize.id], helpprizes=[prize.id], cabaretking=100, demiworld=10)
        self.__raidmaster = raidmaster
        
        # ハプニング.
        happeningmaster = self.create_dummy(DummyType.HAPPENING_MASTER, raidmaster.id)
        self.__happeningmaster = happeningmaster
        
        # 短冊とキャストの情報.
        tanzaku_master = self.create_dummy(DummyType.SCOUT_EVENT_TANZAKU_CAST_MASTER, self.__eventmaster.id, 0, prizes=[prize.id])
        self.__tanzaku_master = tanzaku_master
        
        # イベント用レイド設定.
        scouteventraidmaster = self.create_dummy(DummyType.SCOUT_EVENT_RAID_MASTER, self.__eventmaster.id, self.__raidmaster.id, tanzaku_number=tanzaku_master.number, tanzaku_randmin=10, tanzaku_randmax=10, tanzaku_help_number=tanzaku_master.number, tanzaku_help_randmin=3, tanzaku_help_randmax=3)
        self.__scouteventraidmaster = scouteventraidmaster
        
        # 短冊所持情報.
        tanzaku_nums = {
            tanzaku_master.number : 0
        }
        tanzaku_data = self.create_dummy(DummyType.SCOUT_EVENT_TANZAKU_CAST_DATA, self.__player1.id, self.__eventmaster.id, tanzaku_nums=tanzaku_nums)
        self.__tanzaku_data1 = tanzaku_data
        tanzaku_data = self.create_dummy(DummyType.SCOUT_EVENT_TANZAKU_CAST_DATA, self.__player0.id, self.__eventmaster.id, tanzaku_nums=tanzaku_nums)
        self.__tanzaku_data0 = tanzaku_data
        
        # ハプニング情報.
        eventvalue = HappeningUtil.make_scouteventvalue(self.__eventmaster.id)
        happening = self.create_dummy(DummyType.HAPPENING, self.__player0.id, self.__happeningmaster.id,  progress=happeningmaster.execution, eventid=eventvalue)
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
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        return u'/do/{}/{}'.format(self.__raid.id, self.__player0.req_confirmkey)
    
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
        
        # 短冊.
        def check_tanzaku_num(tanzaku_data_pre, is_lovetime):
            uid = tanzaku_data_pre.uid
            ownername = u'発見者' if self.__player0.id == uid else '救援者'
            
            tanzaku_data_post = BackendApi.get_scoutevent_tanzakucastdata(model_mgr, uid, self.__eventmaster.id)
            if tanzaku_data_post is None:
                raise AppTestError(u'{}の短冊情報が消えている'.format(ownername))
            
            sep = '' if self.__player0.id == uid else '_help'
            tanzakuup = self.__eventmaster.lovetime_tanzakuup if is_lovetime else 0
            
            tanzaku_number = getattr(self.__scouteventraidmaster, 'tanzaku{}_number'.format(sep))
            tanzaku_randmin = getattr(self.__scouteventraidmaster, 'tanzaku{}_randmin'.format(sep)) * (100 + tanzakuup) / 100
            tanzaku_randmax = getattr(self.__scouteventraidmaster, 'tanzaku{}_randmax'.format(sep)) * (100 + tanzakuup) / 100
            
            tanzaku_diff = tanzaku_data_post.get_tanzaku(tanzaku_number) - tanzaku_data_pre.get_tanzaku(tanzaku_number)
            if not (tanzaku_randmin <= tanzaku_diff <= tanzaku_randmax):
                raise AppTestError(u'{}の短冊の増加量が想定外です'.format(ownername))
        check_tanzaku_num(self.__tanzaku_data0, self.__scoutevent_playdata.is_lovetime())
        
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
        
        # 短冊.
        check_tanzaku_num(self.__tanzaku_data1, False)
    
    def finish(self):
        model_mgr = ModelRequestMgr()
        config = BackendApi.get_current_scouteventconfig(model_mgr)
        config.mid = self.__preconfig_mid
        config.starttime = self.__preconfig_starttime
        config.endtime = self.__preconfig_endtime
        model_mgr.set_save(config)
        model_mgr.write_all()
        model_mgr.write_end()
