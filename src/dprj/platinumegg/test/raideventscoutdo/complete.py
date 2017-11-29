# -*- coding: utf-8 -*-
from platinumegg.test.raideventscoutdo import RaidEventScoutDoApiTest
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerGold
from platinumegg.test.base import AppTestError
from defines import Defines

class ApiTest(RaidEventScoutDoApiTest):
    """レイドイベントスカウト実行(完了).
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
    
    def createPlayData(self):
        return self.create_dummy(DummyType.RAID_EVENT_SCOUT_PLAY_DATA, self.player.id, self.eventmaster.id)
    
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
        
        events = self.checkEventScoutResultEvent(playdata, [Defines.ScoutEventType.LEVELUP, Defines.ScoutEventType.COMPLETE])
        
        # レベルアップの結果を検証.
        playerexp = PlayerExp.getByKey(playdata.uid)
        levelupevent = events[Defines.ScoutEventType.LEVELUP]
        if playerexp.level != levelupevent.level:
            raise AppTestError(u'レベルアップイベントに正しくレベルが設定されていない.{} vs {}'.format(playerexp.level, levelupevent.level))
