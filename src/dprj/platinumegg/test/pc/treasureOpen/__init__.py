# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Player import PlayerKey
from defines import Defines
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.pc.base import PcTestBase

class PcTreasureGetApiTestBase(PcTestBase):
    """宝箱取得のテスト.
    """
    @classmethod
    def get_treasure_type(cls):
        raise NotImplementedError
    @classmethod
    def get_treasure_itemtype(cls):
        raise NotImplementedError
    
    @property
    def player(self):
        return self.__player
    @property
    def treasuremaster(self):
        return self.__treasuremasters[self.get_treasure_itemtype()]
    @property
    def treasure(self):
        return self.__treasures[self.get_treasure_itemtype()]
    @property
    def prevpresentnum(self):
        return self.__prevpresentnum
    
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__keynum = 10
        
        # 宝箱を開ける為、鍵の数を変えておく
        player_key = self.__player.getModel(PlayerKey)
        player_key.goldkey = self.__keynum
        player_key.silverkey = self.__keynum
        player_key.save()
        
        self.__prevpresentnum = BackendApi.get_present_num(self.__player.id, arg_model_mgr=None, using=settings.DB_DEFAULT)
        
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER, Defines.ItemEffect.ACTION_ALL_RECOVERY)
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        
        treasure_type = self.get_treasure_type()
        TABLE = {
            Defines.TreasureType.GOLD : (DummyType.TREASURE_GOLD_MASTER, DummyType.TREASURE_GOLD),
            Defines.TreasureType.SILVER : (DummyType.TREASURE_SILVER_MASTER, DummyType.TREASURE_SILVER),
            Defines.TreasureType.BRONZE : (DummyType.TREASURE_BRONZE_MASTER, DummyType.TREASURE_BRONZE),
        }
        dummy_type_master, dummy_type_model = TABLE[treasure_type]
        
        # 宝箱のマスター.
        MASTER_TABLE = (
            # (itype, ivalue1, ivalue2).
            (Defines.ItemType.GOLD, 0, 1),
            (Defines.ItemType.GACHA_PT, 0, 1),
            (Defines.ItemType.ITEM, itemmaster.id, 1),
            (Defines.ItemType.CARD, cardmaster.id, 1),
            (Defines.ItemType.GACHATICKET, 0, 1),
            (Defines.ItemType.TRYLUCKTICKET, 0, 1),
            (Defines.ItemType.MEMORIESTICKET, 0, 1),
        )
        treasuremasters = {}
        treasures = {}
        for itype, ivalue1, ivalue2 in MASTER_TABLE:
            treasuremaster = self.create_dummy(dummy_type_master, itype, ivalue1, ivalue2)
            treasuremasters[itype] = treasuremaster
            treasures[itype] = self.create_dummy(dummy_type_model, self.__player.id, treasuremaster.id)
        
        self.__treasuremasters = treasuremasters
        self.__treasures = treasures
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_CTYPE:self.get_treasure_type(),
            Defines.URLQUERY_ID:self.treasure.id,
        }
    
    def check(self):
        self.checkResponseStatus()
        
        keys = (
            'treasureitem',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        model_mgr = ModelRequestMgr()
        treasure_type = self.get_treasure_type()
        
        # 宝箱.
        treasure = BackendApi.get_treasure(model_mgr, treasure_type, self.treasure.id)
        treasure_deleted = BackendApi.get_treasure(model_mgr, treasure_type, self.treasure.id, deleted=True)
        if treasure:
            raise AppTestError(u'宝箱が残っている')
        elif treasure_deleted is None:
            raise AppTestError(u'開封済み宝箱が作られていない')
        
        # カギ.
        playerkey = PlayerKey.getByKey(self.__player.id)
        if treasure_type == Defines.TreasureType.GOLD:
            if playerkey.goldkey == self.__keynum:
                raise AppTestError(u'金の鍵所持数がおかしい')
        elif treasure_type == Defines.TreasureType.SILVER:
            if playerkey.silverkey == self.__keynum:
                raise AppTestError(u'銀の鍵所持数がおかしい')
        
        # プレゼント.
        presentnum = BackendApi.get_present_num(self.player.id)
        if presentnum == self.prevpresentnum:
            raise AppTestError(u'プレゼントの所持数がおかしい')
        
