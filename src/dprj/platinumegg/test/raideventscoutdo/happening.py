# -*- coding: utf-8 -*-
from platinumegg.test.raideventscoutdo import RaidEventScoutDoApiTest
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.base import AppTestError
from defines import Defines
from platinumegg.app.cabaret.util.scout import ScoutHappeningData
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(RaidEventScoutDoApiTest):
    """レイドイベントスカウト実行(ハプニング発生).
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
        
        self.checkEventScoutResultEvent(playdata, [Defines.ScoutEventType.HAPPENING])
        
        # ハプニング発生結果を検証.
        happeningset = BackendApi.get_current_happening(ModelRequestMgr(), self.player.id)
        if happeningset is None or happeningset.happening.mid != self.happeningmaster.id:
            raise AppTestError(u'ハプニングが開始されていない.')
