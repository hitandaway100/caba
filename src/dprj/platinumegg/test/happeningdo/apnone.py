# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerGold,\
    PlayerHappening
from defines import Defines
from platinumegg.app.cabaret.models.Happening import Happening
import urllib

class ApiTest(ApiTestBase):
    """ハプニング実行(体力不足).
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # レイド.
        raidmaster = self.create_dummy(DummyType.RAID_MASTER)
        
        # ハプニング.
        happeningmaster = self.create_dummy(DummyType.HAPPENING_MASTER, raidmaster.id, apcost=65535)
        self.__happeningmaster = happeningmaster
        
        # ハプニング情報.
        happening = self.create_dummy(DummyType.HAPPENING, self.__player0.id, self.__happeningmaster.id)
        self.__happening = happening
        
        # 経験値情報.
        for i in xrange(Defines.BIGINNER_PLAYERLEVEL):
            self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, i+1, exp=i+1)
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, Defines.BIGINNER_PLAYERLEVEL+1, exp=999)
        self.__player0.level = Defines.BIGINNER_PLAYERLEVEL
        self.__player0.exp = Defines.BIGINNER_PLAYERLEVEL
        self.__player0.getModel(PlayerExp).save()
        
        self.__player0.gold = 0
        self.__player0.getModel(PlayerGold).save()
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%s' % urllib.quote(self.__player0.req_confirmkey, safe='')
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        # 進行情報があるかを確認.
        happening = Happening.getByKey(self.__happening.id)
        playerhappening = PlayerHappening.getByKey(self.__player0.id)
        
        if happening is None:
            raise AppTestError(u'進行情報が保存されていない')
        
        # 報酬.
        resultlist = playerhappening.happening_result.get('result', None)
        if resultlist is None:
            raise AppTestError(u'結果が設定されていない')
        
        gold_add = 0
        for result in resultlist:
            self.__player0.exp += result['exp_add']
            gold_add += result['gold_add']
        
        # お金確認.
        if happening.gold != gold_add:
            raise AppTestError(u'お金が正しくない')
        
        # 経験値.
        playerexp = PlayerExp.getByKey(self.__player0.id)
        if playerexp.exp != self.__player0.exp:
            raise AppTestError(u'お金が正しくない')
        
        # イベント設定されているか.
        eventlist = playerhappening.happening_result.get('event', None)
        if not eventlist:
            raise AppTestError(u'イベントが設定されていない')
        
        # イベント設定されているか.
        eventlist = playerhappening.happening_result.get('event', None)
        if not eventlist:
            raise AppTestError(u'イベントが設定されていない')
        
        # 体力不足のイベントが設定されているか.
        targetevent = None
        for event in eventlist:
            if event.get_type() == Defines.ScoutEventType.AP_NONE:
                targetevent = event
        if targetevent is None:
            raise AppTestError(u'体力不足イベントが設定されていない')
