# -*- coding: utf-8 -*-
from platinumegg.test.raideventscoutdo import RaidEventScoutDoApiTest
from platinumegg.test.base import AppTestError
from defines import Defines

class ApiTest(RaidEventScoutDoApiTest):
    """レイドイベントスカウト実行(体力不足).
    """
    def getStageParams(self):
        """ステージ情報作成.
        """
        stageparams = {
            'execution' : 100,
            'apcost' : self.player.apmax + 1,
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
        if playdata.progress != 0:
            raise AppTestError(u'進行してしまっている')
        
        self.checkEventScoutResultEvent(playdata, [Defines.ScoutEventType.AP_NONE])
    
