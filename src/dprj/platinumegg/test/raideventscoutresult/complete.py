# -*- coding: utf-8 -*-
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerGold
from platinumegg.test.raideventscoutresult import RaidEventScoutResultApiTest

class ApiTest(RaidEventScoutResultApiTest):
    """レイドイベントスカウト結果(完了).
    """
    def createPlayer(self):
        """プレイヤー情報作成.
        """
        player = self.create_dummy(DummyType.PLAYER)
        
        # 経験値情報.
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 1, exp=0)
        levelexpmaster = self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 2, exp=1)
        player.level = levelexpmaster.level - 1
        player.exp = levelexpmaster.exp - 1
        player.getModel(PlayerExp).save()
        
        player.gold = 0
        player.getModel(PlayerGold).save()
        
        return player
    
    def getStageParams(self):
        """ステージ情報作成.
        """
        # ボス.
        boss = self.create_dummy(DummyType.BOSS_MASTER)
        
        # すぐに終わるようにする.
        stageparams = {
            'boss' : boss.id,
            'execution' : 1,
            'exp' : 1,
        }
        return stageparams
