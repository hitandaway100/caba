# -*- coding: utf-8 -*-
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.scout import ScoutHappeningData
from platinumegg.test.raideventscoutresult import RaidEventScoutResultApiTest

class ApiTest(RaidEventScoutResultApiTest):
    """レイドイベントスカウト結果(ハプニング発生).
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
