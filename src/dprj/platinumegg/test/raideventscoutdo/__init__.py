# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.raideventtest import RaidEventApiTest
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerGold
from platinumegg.app.cabaret.models.raidevent.RaidEventScout import RaidEventScoutPlayData
from defines import Defines

class RaidEventScoutDoApiTest(RaidEventApiTest):
    """レイドイベントスカウト実行.
    """
    
    def setUp(self):
        # Player.
        self.__player0 = self.createPlayer()
        
        # レイドイベントを準備.
        self.setUpRaidEvent(self.__player0, dedicated_stage_max=self.get_dedicated_stage_max(), is_open=True)
        
        # オープニングとタイムボーナスを閲覧済みにする.
        eventflagrecord = self.create_dummy(DummyType.RAID_EVENT_FLAGS, self.eventmaster.id, self.player.id, tbvtime=self.raidevent_config.starttime)
        self.__eventflagrecord = eventflagrecord
        
        # イベントスコア.
        eventscore = self.create_dummy(DummyType.RAID_EVENT_SCORE, self.eventmaster.id, self.__player0.id, destroy=1)
        self.__eventscore = eventscore
        
        # 進行情報.
        self.__playdata = self.createPlayData()
    
    @property
    def player(self):
        return self.__player0
    
    @property
    def eventplaydata(self):
        return self.__playdata
    
    def get_dedicated_stage_max(self):
        return 5
    
    def createPlayer(self):
        """プレイヤー情報作成.
        """
        return self.create_dummy(DummyType.PLAYER)
    
    def createPlayData(self):
        return self.create_dummy(DummyType.RAID_EVENT_SCOUT_PLAY_DATA, self.player.id, self.eventmaster.id)
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        stagemaster = self.getStageByNumber(self.eventplaydata.stage)
        return u'/{}/{}'.format(stagemaster.id, self.eventplaydata.confirmkey)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.player.dmmid,
        }
    
    def getWroteEventScoutPlayData(self):
        playdata = RaidEventScoutPlayData.getByKey(self.eventplaydata.id)
        return playdata
    
    def checkEventCommonResult(self, playdata):
        """共通の実行結果を確認.
        """
        if playdata is None:
            raise AppTestError(u'進行情報が保存されていない')
        elif playdata.alreadykey != self.eventplaydata.confirmkey:
            raise AppTestError(u'重複確認用のキーが正しくない')
        
        # 報酬.
        resultlist = playdata.result.get('result', None)
        if resultlist is None:
            raise AppTestError(u'結果が設定されていない')
        
        post_exp = self.player.exp
        post_gold = self.player.gold
        for result in resultlist:
            post_exp += result['exp_add']
            post_gold += result['gold_add']
        
        # お金確認.
        playergold = PlayerGold.getByKey(playdata.uid)
        if playergold.gold != post_gold:
            raise AppTestError(u'お金が正しくない')
        
        # 経験値.
        playerexp = PlayerExp.getByKey(playdata.uid)
        if playerexp.exp != post_exp:
            raise AppTestError(u'経験値が正しくない')
        
        # イベント設定されているか.
        eventlist = playdata.result.get('event', None)
        if not eventlist:
            raise AppTestError(u'イベントが設定されていない')
    
    def checkEventScoutResultEvent(self, playdata, eventtypelist):
        """スカウトの結果イベントを確認
        """
        eventlist = playdata.result.get('event', None)
        if not eventlist:
            raise AppTestError(u'イベントが設定されていない')
        
        tmp_eventtypelist = eventtypelist[:]
        dest = {}
        for event in eventlist:
            eventtype = event.get_type()
            if eventtype in tmp_eventtypelist:
                dest[eventtype] = event
                tmp_eventtypelist.remove(eventtype)
        
        if tmp_eventtypelist:
            raise AppTestError(u'実行結果が足りません...{}'.format(u','.join([Defines.ScoutEventType.NAMES[eventtype] for eventtype in tmp_eventtypelist])))
        
        return dest
