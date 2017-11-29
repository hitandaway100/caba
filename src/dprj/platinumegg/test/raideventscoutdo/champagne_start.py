# -*- coding: utf-8 -*-
from platinumegg.test.raideventscoutdo import RaidEventScoutDoApiTest
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.base import AppTestError
from platinumegg.app.cabaret.util.scout import ScoutHappeningData
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(RaidEventScoutDoApiTest):
    """レイドイベントスカウト実行(シャンパンコール開始).
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
        champagnedata = self.create_dummy(DummyType.RAID_EVENT_CHAMPAGNE, player.id, self.eventmaster.id, self.eventmaster.champagne_num_max)
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
        
        redirect_url = self.response['redirect_url']
        if redirect_url.find('/raidevent/showtime/effect') == -1:
            raise AppTestError(u'演出に遷移していない')
        
        champagnedata = BackendApi.get_raidevent_champagne(ModelRequestMgr(), self.player.id)
        if champagnedata is None:
            raise AppTestError(u'シャンパン情報が見つからない')
        elif not champagnedata.isChampagneCall(self.eventmaster.id):
            raise AppTestError(u'シャンパンコール状態になっていない')
        elif champagnedata.num != 0:
            raise AppTestError(u'シャンパン数がリセットされていない')
