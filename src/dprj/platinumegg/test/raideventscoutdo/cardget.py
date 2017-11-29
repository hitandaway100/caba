# -*- coding: utf-8 -*-
from platinumegg.test.raideventscoutdo import RaidEventScoutDoApiTest
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.base import AppTestError
from defines import Defines
from platinumegg.app.cabaret.util.scout import ScoutDropItemData

class ApiTest(RaidEventScoutDoApiTest):
    """レイドイベントスカウト実行(カード獲得).
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
    
    def check(self):
        keys = (
            'redirect_url',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        # 書き込み後の進行情報.
        playdata = self.getWroteEventScoutPlayData()
        self.checkEventCommonResult(playdata)
        
        stagemaster = self.getStageByNumber(self.eventplaydata.stage)
        
        # URLを確認.
        redirect_url = self.response['redirect_url']
        if redirect_url.find('/raideventscoutanim/{}/{}'.format(stagemaster.id, playdata.alreadykey)) == -1:
            raise AppTestError(u'リダイレクト先が正しくない')
        
        # 進行度.
        if playdata.progress == 0:
            raise AppTestError(u'進行度が進んでいない')
        
        # カード獲得の結果を検証.
        targetevent = self.checkEventScoutResultEvent(playdata, [Defines.ScoutEventType.GET_CARD])[Defines.ScoutEventType.GET_CARD]
        if targetevent.card != self.__cardmaster.id:
            raise AppTestError(u'カード獲得イベントに正しくカードが設定されていない.{} vs {}'.format(targetevent.card, self.__cardmaster.id))
        elif targetevent.is_received:
            raise AppTestError(u'カード受取判定済になってしまっている')
