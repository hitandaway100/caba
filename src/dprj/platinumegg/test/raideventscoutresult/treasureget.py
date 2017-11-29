# -*- coding: utf-8 -*-
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from defines import Defines
from platinumegg.test.raideventscoutresult import RaidEventScoutResultApiTest

class ApiTest(RaidEventScoutResultApiTest):
    """レイドイベントスカウト結果(宝箱獲得).
    """
    def createPlayer(self):
        """プレイヤー情報作成.
        """
        player = self.create_dummy(DummyType.PLAYER)
        
        # 宝箱獲得数.
        model_mgr = ModelRequestMgr()
        self.__treasure_num = BackendApi.get_treasure_num(model_mgr, Defines.TreasureType.GOLD, player.id)
        
        return player
    
    def getStageParams(self):
        """ステージ情報作成.
        """
        # 宝箱(中身はなんでもいい).
        self.__treasuremaster = self.create_dummy(DummyType.TREASURE_GOLD_MASTER, Defines.ItemType.GOLD, 0, 100)
        
        # 出現テーブル.
        self.__treasuretablemaster = self.create_dummy(DummyType.TREASURE_TABLE_GOLD_MASTER, [self.__treasuremaster.id])
        
        stageparams = {
            'execution' : 100,
            'treasuregold' : 1,
        }
        return stageparams
