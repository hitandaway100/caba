# -*- coding: utf-8 -*-
from platinumegg.test.raideventscoutdo import RaidEventScoutDoApiTest
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.base import AppTestError
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from defines import Defines

class ApiTest(RaidEventScoutDoApiTest):
    """レイドイベントスカウト実行(宝箱獲得).
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
        targetevent = self.checkEventScoutResultEvent(playdata, [Defines.ScoutEventType.GET_TREASURE])[Defines.ScoutEventType.GET_TREASURE]
        if targetevent.treasuretype != Defines.TreasureType.GOLD:
            raise AppTestError(u'宝箱獲得イベントに正しくカードが設定されていない.{}'.format(targetevent.treasuretype))
        
        treasure_num = BackendApi.get_treasure_num(ModelRequestMgr(), Defines.TreasureType.GOLD, self.player.id)
        if (self.__treasure_num + 1) != treasure_num:
            raise AppTestError(u'宝箱の所持数が想定外.{} vs {}'.format((self.__treasure_num + 1), treasure_num))
