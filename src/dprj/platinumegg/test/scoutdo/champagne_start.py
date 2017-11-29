# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerGold,\
    PlayerDeck
from platinumegg.app.cabaret.models.Scout import ScoutPlayData
from defines import Defines
from platinumegg.app.cabaret.util.scout import ScoutDropItemData,\
    ScoutHappeningData
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import datetime

class ApiTest(ApiTestBase):
    """スカウト実行(シャンパンコール開始).
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # ボス.
        boss = self.create_dummy(DummyType.BOSS_MASTER)
        # エリア.
        area = self.create_dummy(DummyType.AREA_MASTER, bossid=boss.id)
        
        # カード.
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        data = ScoutDropItemData.create(Defines.ItemType.CARD, cardmaster.id, filters={'ptype':Defines.CharacterType.TYPE_001}, rate=10000)
        dropitems = [data.get_dropitem_dict()]
        self.__cardmaster = cardmaster
        
        # スカウト.
        scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area, execution=100, dropitems=dropitems)
        self.__scout = scout
        for _ in xrange(5):
            scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area, opencondition=scout.id)
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, gachapt=10)
        
        # レイドマスター.
        raidmaster = self.create_dummy(DummyType.RAID_MASTER, hp=1, prizes=[prize.id], helpprizes=[prize.id], cabaretking=100, demiworld=10)
        self.__raidmaster = raidmaster
        
        # ハプニング.
        happeningmaster = self.create_dummy(DummyType.HAPPENING_MASTER, raidmaster.id)
        self.__happeningmaster = happeningmaster
        
        # レイドイベント.
        data = ScoutHappeningData.create(happeningmaster.id, 10000)
        happenings = [data.get_dict()]
        eventmaster = self.create_dummy(DummyType.RAID_EVENT_MASTER, happenings, champagne_num_max=10, champagne_time=300)
        self.__eventmaster = eventmaster
        
        # シャンパン情報.
        champagnedata = self.create_dummy(DummyType.RAID_EVENT_CHAMPAGNE, self.__player0.id, eventmaster.id, eventmaster.champagne_num_max)
        self.__champagnedata = champagnedata
        
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
        url = self.response.get('redirect_url')
        if not url:
            raise AppTestError(u'リダイレクト先が設定されていない')
        elif url.find('showtime') == -1:
            raise AppTestError(u'演出に遷移していない')
        
        champagnedata = BackendApi.get_raidevent_champagne(ModelRequestMgr(), self.__player0.id)
        if champagnedata is None:
            raise AppTestError(u'シャンパン情報が見つからない')
        elif not champagnedata.isChampagneCall(self.__eventmaster.id):
            raise AppTestError(u'シャンパンコール状態になっていない')
        elif champagnedata.num != 0:
            raise AppTestError(u'シャンパン数がリセットされていない')
    
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
