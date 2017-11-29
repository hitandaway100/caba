# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.scout import ScoutDropItemData
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Player import PlayerFriend

class ApiTest(ApiTestBase):
    """レイドフレンド選択(設定).
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        self.__player0.friendlimit = 10
        self.__player0.getModel(PlayerFriend).save()
        
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
        
        self.__o_player = self.create_dummy(DummyType.PLAYER)
        addRequest(self.__player0, self.__o_player)
        addFriend(self.__o_player, self.__player0)
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/set/%d/%d' % (self.__raid.id, self.__o_player.id)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        model_mgr = ModelRequestMgr()
        cardset = BackendApi.get_raidhelpcard(model_mgr, self.__player0.id, self.__raid.id)
        leader = BackendApi.get_leaders([self.__o_player.id]).get(self.__o_player.id)
        if cardset is None:
            raise AppTestError(u'カードが設定されていない')
        elif leader.id != cardset.id:
            raise AppTestError(u'カードが違う')
        elif cardset.card.uid != self.__o_player.id:
            raise AppTestError(u'ユーザーが違う')
        elif leader.power != cardset.power:
            raise AppTestError(u'パラメータが違う')
        elif leader.card.skilllevel != cardset.card.skilllevel:
            raise AppTestError(u'スキルレベルが違う')
