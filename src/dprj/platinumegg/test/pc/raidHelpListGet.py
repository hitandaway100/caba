# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerFriend
from platinumegg.app.cabaret.util.scout import ScoutDropItemData
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.pc.base import PcTestBase

class ApiTest(PcTestBase):
    """レイド救援一覧.
    """
    def setUp(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        self.__player0.friendlimit = 100
        model_mgr.set_save(self.__player0.getModel(PlayerFriend))
        model_mgr.write_all()
        model_mgr.write_end()
        
        # アイテム.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER)
        data = ScoutDropItemData.create(Defines.ItemType.ITEM, itemmaster.id, filters={'ptype':Defines.CharacterType.TYPE_001}, rate=10000)
        items = [data.get_dropitem_dict()]
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, gachapt=10, item=itemmaster)
        
        # レイドマスター.
        raidmaster = self.create_dummy(DummyType.RAID_MASTER, hp=1000, prizes=[prize.id], helpprizes=[prize.id], cabaretking=100, demiworld=10)
        self.__raidmaster = raidmaster
        
        # ハプニング.
        happeningmaster = self.create_dummy(DummyType.HAPPENING_MASTER, raidmaster.id, items=items)
        self.__happeningmaster = happeningmaster
        
        for _ in xrange(5):
            player = self.create_dummy(DummyType.PLAYER)
            # ハプニング情報.
            happening = self.create_dummy(DummyType.HAPPENING, player.id, self.__happeningmaster.id,  progress=happeningmaster.execution)
            self.__happening = happening
            
            # レイド.
            raidboss = self.create_dummy(DummyType.RAID, player, happeningmaster, happening)
            raidboss.addDamageRecord(player.id, 1)
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
            
            addRequest(player, self.__player0)
            addFriend(self.__player0, player)
            
            model_mgr = ModelRequestMgr()
            BackendApi.tr_send_raidhelp(model_mgr, player.id)
            model_mgr.write_all()
            model_mgr.write_end()
            
            raidboss.addDamageRecord(self.__player0.id, 1)
            raidboss.refrectDamageRecord()
            raidboss.raid.save()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        self.checkResponseStatus()
        
        keys = (
            'raidhelplist',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
