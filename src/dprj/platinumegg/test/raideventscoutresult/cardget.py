# -*- coding: utf-8 -*-
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.app.cabaret.util.scout import ScoutDropItemData
from platinumegg.test.raideventscoutresult import RaidEventScoutResultApiTest

class ApiTest(RaidEventScoutResultApiTest):
    """レイドイベントスカウト結果(カード獲得).
    """
    def createPlayer(self):
        """プレイヤー情報作成.
        """
        player = self.create_dummy(DummyType.PLAYER)
        return player
    
    def getStageParams(self):
        """ステージ情報作成.
        """
        # カード.
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        data = ScoutDropItemData.create(Defines.ItemType.CARD, cardmaster.id, rate=10000)
        dropitems = [data.get_dropitem_dict()]
        self.__cardmaster = cardmaster
        
        stageparams = {
            'execution' : 100,
            'dropitems' : dropitems,
        }
        return stageparams
