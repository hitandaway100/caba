# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerGold,\
    PlayerDeck
from platinumegg.app.cabaret.models.Scout import ScoutPlayData
from defines import Defines
from platinumegg.app.cabaret.util.scout import ScoutHappeningData
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import datetime
from platinumegg.app.cabaret.util.happening import HappeningUtil

class ApiTest(ApiTestBase):
    """スカウト実行(シャンパンコール中のハプニング発生).
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # ボス.
        boss = self.create_dummy(DummyType.BOSS_MASTER)
        # エリア.
        area = self.create_dummy(DummyType.AREA_MASTER, bossid=boss.id)
        
        # レイド.
        raidmaster = self.create_dummy(DummyType.RAID_MASTER)
        
        # ハプニング.
        happeningmaster = self.create_dummy(DummyType.HAPPENING_MASTER, raidmaster.id, execution=0)
        data = ScoutHappeningData.create(happeningmaster.id, 10000)
        happenings = [data.get_dict()]
        self.__happeningmaster = happeningmaster
        
        # レイドイベント.
        data = ScoutHappeningData.create(happeningmaster.id, 10000)
        eventmaster = self.create_dummy(DummyType.RAID_EVENT_MASTER, happenings, champagne_num_max=10, champagne_time=300)
        self.__eventmaster = eventmaster
        
        # シャンパン情報.
        champagnedata = self.create_dummy(DummyType.RAID_EVENT_CHAMPAGNE, self.__player0.id, eventmaster.id, eventmaster.champagne_num_max)
        self.__champagnedata = champagnedata
        
        # スカウト.
        scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area, execution=100, happenings=happenings)
        self.__scout = scout
        for _ in xrange(5):
            scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area, opencondition=scout.id)
        
        # 経験値情報.
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 1, exp=0)
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 2, exp=999)
        self.__player0.level = 1
        self.__player0.exp = 0
        self.__player0.getModel(PlayerExp).save()
        
        self.__player0.gold = 0
        self.__player0.getModel(PlayerGold).save()
        
        self.__player0.cardlimititem = 100
        self.__player0.getModel(PlayerDeck).save()
        
        # 途中まで進んでいるかもしれないので消しておく.
        playdata = ScoutPlayData.getByKey(ScoutPlayData.makeID(self.__player0.id, self.__scout.id))
        if playdata:
            playdata.delete()
        
        # イベント発生中設定.
        model_mgr = ModelRequestMgr()
        config = BackendApi.get_current_raideventconfig(model_mgr)
        self.__preconfig_mid = config.mid
        self.__preconfig_starttime = config.starttime
        self.__preconfig_endtime = config.endtime
        self.__preconfig_timebonus = config.timebonus_time
        timebonus_time = []
        now = OSAUtil.get_now()
        BackendApi.update_raideventconfig(self.__eventmaster.id, now, now + datetime.timedelta(days=1), timebonus_time=timebonus_time)
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%d' % self.__scout.id
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        model_mgr = ModelRequestMgr()
        
        # 進行情報があるかを確認.
        playdata = ScoutPlayData.getByKey(ScoutPlayData.makeID(self.__player0.id, self.__scout.id))
        if playdata is None:
            raise AppTestError(u'進行情報が保存されていない')
        elif playdata.progress == 0:
            raise AppTestError(u'進行度が進んでいない')
        
        # 報酬.
        resultlist = playdata.result.get('result', None)
        if not resultlist:
            raise AppTestError(u'結果が設定されていない')
        
        for result in resultlist:
            self.__player0.exp += result['exp_add']
            self.__player0.gold += result['gold_add']
        
        # お金確認.
        playergold = PlayerGold.getByKey(playdata.uid)
        if playergold.gold != self.__player0.gold:
            raise AppTestError(u'お金が正しくない')
        
        # 経験値.
        playerexp = PlayerExp.getByKey(playdata.uid)
        if playerexp.exp != self.__player0.exp:
            raise AppTestError(u'お金が正しくない')
        
        # イベント設定されているか.
        eventlist = playdata.result.get('event', None)
        if not eventlist:
            raise AppTestError(u'イベントが設定されていない')
        
        # ハプニング発生のイベントが設定されているか.
        targetevent = None
        for event in eventlist:
            if event.get_type() == Defines.ScoutEventType.HAPPENING:
                targetevent = event
        if targetevent is None:
            raise AppTestError(u'ハプニング発生イベントが設定されていない')
        elif targetevent.happening != self.__happeningmaster.id:
            raise AppTestError(u'ハプニング発生イベントに正しくハプニングが設定されていない.%d vs %d' % (targetevent.happening, self.__happeningmaster.id))
        
        happeningset = BackendApi.get_current_happening(model_mgr, self.__player0.id)
        if happeningset is None or happeningset.happening.mid != self.__happeningmaster.id:
            raise AppTestError(u'ハプニングが開始されていない.')
        
        raidboss = BackendApi.get_raid(model_mgr, happeningset.id, happening_eventvalue=HappeningUtil.make_raideventvalue(self.__eventmaster.id))
        record = raidboss.getDamageRecord(self.__player0.id)
        if not record.champagne:
            raise AppTestError(u'シャンパンコールのフラグが立っていない.')
    
    def finish(self):
        model_mgr = ModelRequestMgr()
        config = BackendApi.get_current_raideventconfig(model_mgr)
        config.mid = self.__preconfig_mid
        config.starttime = self.__preconfig_starttime
        config.endtime = self.__preconfig_endtime
        config.timebonus_time = self.__preconfig_timebonus
        model_mgr.set_save(config)
        model_mgr.write_all()
        model_mgr.write_end()
