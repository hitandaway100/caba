# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerGold,\
    PlayerDeck, PlayerRequest
from platinumegg.app.cabaret.util.scout import ScoutDropItemData
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import urllib
from platinumegg.test.pc.base import PcTestBase

class ApiTest(PcTestBase):
    """レイド攻撃(倒しきれない).
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # アイテム.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER)
        data = ScoutDropItemData.create(Defines.ItemType.ITEM, itemmaster.id, filters={'ptype':Defines.CharacterType.TYPE_001}, rate=10000)
        items = [data.get_dropitem_dict()]
        
        # レイドマスター.
        raidmaster = self.create_dummy(DummyType.RAID_MASTER, hp=9999999)
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
        
        self.__player0.gold = 0
        self.__player0.getModel(PlayerGold).save()
        
        self.__player0.cardlimititem = 100
        self.__player0.getModel(PlayerDeck).save()
        
        model_mgr = ModelRequestMgr()
        self.__playerhappening = BackendApi.get_playerhappening(model_mgr, self.__player0.id)
        
        self.__requestkey = self.__player0.req_confirmkey
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
            Defines.URLQUERY_ID:self.__raid.id,
            Defines.URLQUERY_BATTLE:urllib.quote(self.__requestkey, ''),
        }
    
    def check(self):
        self.checkResponseStatus()
        
        model_mgr = ModelRequestMgr()
        
        # 確認キー.
        playerrequest = BackendApi.get_model(model_mgr, PlayerRequest, self.__player0.id)
        if self.__requestkey == playerrequest.req_confirmkey:
            raise AppTestError(u'確認キーが更新されていない')
        elif self.__requestkey != playerrequest.req_alreadykey:
            raise AppTestError(u'確認済みのキーが更新されていない')
        
        # ダメージレコード.
        raidboss = BackendApi.get_raid(model_mgr, self.__raid.id)
        record = raidboss.getDamageRecord(self.__player0.id)
        if record.damage == 0 or record.damage_cnt == 0:
            raise AppTestError(u'ダメージが記録されていない')
        
        # ダメージ.
        maxhp = raidboss.get_maxhp()
        if (maxhp - record.damage) != raidboss.raid.hp:
            raise AppTestError(u'ダメージが正しくない')
        
