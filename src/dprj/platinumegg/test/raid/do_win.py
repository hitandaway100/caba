# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerGold,\
    PlayerDeck, PlayerTreasure, PlayerRequest
from platinumegg.app.cabaret.util.scout import ScoutDropItemData
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import urllib
from platinumegg.app.cabaret.models.Happening import RaidPrizeDistributeQueue

class ApiTest(ApiTestBase):
    """レイド攻撃(倒した).
    """
    def setUp(self):
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
        
        # ハプニング情報.
        happening = self.create_dummy(DummyType.HAPPENING, self.__player0.id, self.__happeningmaster.id,  progress=happeningmaster.execution)
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
        
        if Defines.RAID_PRIZE_DISTRIBUTION_OUTSIDE:
            queue = RaidPrizeDistributeQueue.getValues(filters={'raidid':self.__raid.id})
            if queue is None:
                raise AppTestError(u'報酬配布用のキューが作成されていない')
        else:
            present_num1 = BackendApi.get_present_num(self.__player1.id)
            if self.__present_num1 == present_num1:
                raise AppTestError(u'救援者に報酬が付与されていない')
            
            playertreasure1 = PlayerTreasure.getByKey(self.__player1.id)
            if playertreasure1.demiworld != self.__raid.get_demiworld():
                raise AppTestError(u'裏社会の秘宝が付与されていない')
        
