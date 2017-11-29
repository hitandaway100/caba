# -*- coding: utf-8 -*-
from platinumegg.test.raideventscoutanim import RaidEventScoutAnimApiTest
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.scout import ScoutHappeningData

class ApiTest(RaidEventScoutAnimApiTest):
    """レイドイベントスカウト演出(ハプニング発生).
    """
    def createPlayer(self):
        """プレイヤー情報作成.
        """
        player = self.create_dummy(DummyType.PLAYER)
        return player
    
    def getStageParams(self):
        """ステージ情報作成.
        """
        data = ScoutHappeningData.create(self.happeningmaster.id, 10000)
        happenings = [data.get_dict()]
        
        stageparams = {
            'execution' : 100,
            'happenings' : happenings,
        }
        return stageparams
