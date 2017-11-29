# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.app.cabaret.util.scout import ScoutDropItemData
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Player import PlayerGold, PlayerDeck

class ApiTest(ApiTestBase):
    """ハプニング終了(キャンセル).
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
        
        happening.etime = OSAUtil.get_now()
        happening.save()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%d' % self.__raid.id
    
    def check(self):
        arr = (
            'cancel',
            'prize',
        )
        for k in arr:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない' % k)
