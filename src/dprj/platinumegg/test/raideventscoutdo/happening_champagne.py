# -*- coding: utf-8 -*-
from platinumegg.test.raideventscoutdo import RaidEventScoutDoApiTest
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.base import AppTestError
from defines import Defines
from platinumegg.app.cabaret.util.scout import ScoutHappeningData
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.lib.opensocial.util import OSAUtil
import datetime
from platinumegg.app.cabaret.util.happening import HappeningUtil

class ApiTest(RaidEventScoutDoApiTest):
    """レイドイベントスカウト実行(シャンパンコール中のハプニング発生).
    """
    def createPlayer(self):
        """プレイヤー情報作成.
        """
        player = self.create_dummy(DummyType.PLAYER)
        
        return player
    
    def setUpRaidEvent(self, player, dedicated_stage_max, is_open):
        dest = super(self.__class__, self).setUpRaidEvent(player, dedicated_stage_max, is_open)
        
        # シャンパン数を設定.
        self.eventmaster.champagne_num_max = 1
        self.eventmaster.champagne_time = 3600
        self.eventmaster.save()
        
        # シャンパン情報.
        champagnedata = self.create_dummy(DummyType.RAID_EVENT_CHAMPAGNE, player.id, self.eventmaster.id, 0, OSAUtil.get_now() + datetime.timedelta(days=1))
        self.__champagnedata = champagnedata
        return dest
    
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
        
        model_mgr = ModelRequestMgr()
        # ハプニング発生結果を検証.
        happeningset = BackendApi.get_current_happening(model_mgr, self.player.id)
        if happeningset is None or happeningset.happening.mid != self.happeningmaster.id:
            raise AppTestError(u'ハプニングが開始されていない.')
        
        # シャンパンコール状態の確認.
        raidboss = BackendApi.get_raid(model_mgr, happeningset.id, happening_eventvalue=HappeningUtil.make_raideventvalue(self.eventmaster.id))
        record = raidboss.getDamageRecord(self.player.id)
        if not record.champagne:
            raise AppTestError(u'シャンパンコールのフラグが立っていない.')
