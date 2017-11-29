# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerGold,\
    PlayerDeck
from platinumegg.app.cabaret.util.scout import ScoutDropItemData
from defines import Defines
from platinumegg.test.pc.base import PcTestBase
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(PcTestBase):
    """レイド取得.
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # アイテム.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER)
        data = ScoutDropItemData.create(Defines.ItemType.ITEM, itemmaster.id, filters={'ptype':Defines.CharacterType.TYPE_001}, rate=10000)
        items = [data.get_dropitem_dict()]
        
        # レイドマスター.
        raidmaster = self.create_dummy(DummyType.RAID_MASTER)
        self.__raidmaster = raidmaster
        
        # ハプニング.
        happeningmaster = self.create_dummy(DummyType.HAPPENING_MASTER, raidmaster.id, items=items)
        self.__happeningmaster = happeningmaster
        
        # ハプニング情報.
        happening = self.create_dummy(DummyType.HAPPENING, self.__player0.id, self.__happeningmaster.id,  progress=happeningmaster.execution)
        self.__happening = happening
        
        # レイド.
        raid = self.create_dummy(DummyType.RAID, self.__player0, happeningmaster, happening)
        self.__raid = raid
        
        # 経験値情報.
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 1, exp=0)
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 2, exp=999)
        self.__player0.level = 1
        self.__player0.exp = 0
        self.__player0.getModel(PlayerExp).save()
        
        self.__player0.gold = 0
        self.__player0.getModel(PlayerGold).save()
        
        self.__player0.cardlimititem = 100
        self.__player0.getModel(PlayerDeck).save()
        
        self.__player1 = self.create_dummy(DummyType.PLAYER)
        
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
        
        leader = BackendApi.get_leaders([self.__player1.id]).get(self.__player1.id)
        BackendApi.save_raidhelpcard(ModelRequestMgr(), self.__player0.id, raid.id, leader)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
            Defines.URLQUERY_ID:self.__raid.id,
        }
    
    def check(self):
        
        self.checkResponseStatus()
        
        keys = (
            'happening',
            'damagerecordlist',
            'playerlist',
            'battlekey',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        if not self.resultbody['happening'].get('raid'):
            raise AppTestError(u'レイドが設定されていない')
