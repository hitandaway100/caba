# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerGold,\
    PlayerDeck
from platinumegg.app.cabaret.models.Scout import ScoutPlayData
from defines import Defines

class ApiTest(ApiTestBase):
    """スカウト実行(スカウト完了).
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # ボス.
        boss = self.create_dummy(DummyType.BOSS_MASTER)
        # エリア.
        area = self.create_dummy(DummyType.AREA_MASTER, bossid=boss.id)
        # スカウト.
        scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area, execution=1)
        self.__scout = scout
        for _ in xrange(5):
            scout = self.create_dummy(DummyType.SCOUT_MASTER, area=area, opencondition=scout.id)
        
        # 経験値情報.
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 1, exp=0)
        self.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, 2, exp=1)
        self.__player0.level = 1
        self.__player0.exp = 0
        self.__player0.getModel(PlayerExp).save()
        
        self.__player0.gold = 0
        self.__player0.getModel(PlayerGold).save()
        
        # 途中まで進んでいるかもしれないので消しておく.
        playdata = ScoutPlayData.getByKey(ScoutPlayData.makeID(self.__player0.id, self.__scout.id))
        if playdata:
            playdata.delete()
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%d' % self.__scout.id
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
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
        
        # デッキコスト.
        playerdeck = PlayerDeck.getByKey(playdata.uid)
        if playerdeck.deckcapacityscout != (self.__player0.deckcapacityscout + 1):
            raise AppTestError(u'デッキコスト上限が正しくない')
        
        # イベント設定されているか.
        eventlist = playdata.result.get('event', None)
        if not eventlist:
            raise AppTestError(u'イベントが設定されていない')
        
        # レベルアップとスカウト完了のイベントが設定されているか.
        levelupevent = None
        completeevent = None
        for event in eventlist:
            if event.get_type() == Defines.ScoutEventType.LEVELUP:
                levelupevent = event
            elif event.get_type() == Defines.ScoutEventType.COMPLETE:
                completeevent = event
        if levelupevent is None:
            raise AppTestError(u'レベルアップイベントが設定されていない')
        elif completeevent is None:
            raise AppTestError(u'スカウト完了イベントが設定されていない')
        elif playerexp.level != levelupevent.level:
            raise AppTestError(u'レベルアップイベントに正しくレベルが設定されていない.%d vs %d' % (playerexp.level, levelupevent.level))
        elif playdata.mid != completeevent.scoutid:
            raise AppTestError(u'完了イベントに正しくスカウトIDが設定されていない.%d vs %d' % (playdata.mid, completeevent.scoutid))