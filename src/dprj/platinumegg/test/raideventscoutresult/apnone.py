# -*- coding: utf-8 -*-
from platinumegg.test.raideventscoutresult import RaidEventScoutResultApiTest

class ApiTest(RaidEventScoutResultApiTest):
    """レイドイベントスカウト結果(体力不足).
    """
    def getStageParams(self):
        """ステージ情報作成.
        """
        stageparams = {
            'execution' : 100,
            'apcost' : self.player.apmax + 1,
        }
        return stageparams
    
