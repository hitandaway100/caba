# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase
from platinumegg.app.cabaret.util.redisbattleevent import BattleEventOppList
import urllib
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Player import PlayerGold

class ApiTest(BattleEventApiTestBase):
    """バトルイベント対戦書き込み(敗北).
    """
    def setUp2(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.makePlayer(10)
        
        # イベントマスター.
        eventmaster = self.setUpEvent(model_mgr=model_mgr)
        self.__eventmaster = eventmaster
        
        # ランクのマスター.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER, mid=Defines.ItemEffect.ACTION_SMALL_RECOVERY, evalue=2)
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, item=itemmaster)
        params = {
            'loseprizes' : [{
                'prizes' : [prize.id],
                'rate' : 100,
            }],
            'battlepoint_w' : 100,
            'battlepoint_l' : 200,
            'battlepoint_lv' : 10,
            'battlepointreceive' : 30,
        }
        eventrankmaster = self.createRankMaster(params=params)
        self.__eventrankmaster = eventrankmaster
        
        # オープニングを閲覧済みに.
        self.setOpeningViewTime(self.__player0.id)
        
        # 参加させておく.
        self.joinRank(self.__player0.id)
        
        # 参加させておく.
        self.setLoginBonusReceived(self.__player0.id)
        
        # 対戦相手を設定.
        player = self.makePlayer(1000)
        self.joinRank(player.id)
        BattleEventOppList.create(self.__player0.id, [player.id]).save()
        self.__player1 = player
        
        # 書き込み前のプレゼント数.
        self.__present_num = BackendApi.get_present_num(self.__player0.id)
        
        # 書き込み前のバトルポイント.
        def score(model):
            if model:
                return model.getPointToday(), model.point_total
            else:
                return 0, 0
        self.__score0 = score(BackendApi.get_battleevent_scorerecord(model_mgr, self.__eventmaster.id, self.__player0.id))
        self.__score1 = score(BackendApi.get_battleevent_scorerecord(model_mgr, self.__eventmaster.id, self.__player1.id))
        
        # 書き込み前の履歴数.
        self.__log_num0 = BackendApi.get_battleevent_battlelog_num(model_mgr, self.__player0.id)
        self.__log_num1 = BackendApi.get_battleevent_battlelog_num(model_mgr, self.__player1.id)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%s/%d' % (urllib.quote(self.__player0.req_confirmkey, ''), self.__player1.id)
    
    def check(self):
        model_mgr = ModelRequestMgr()
        # 結果が保存されているか.
        battleresult = BackendApi.get_battleevent_battleresult(model_mgr, self.__eventmaster.id, self.__player0.id)
        if battleresult is None:
            raise AppTestError(u'結果が保存されていない')
        elif battleresult.result != Defines.BattleResultCode.LOSE:
            raise AppTestError(u'結果が想定と違う.%d' % battleresult.result)
        
        # バトルポイント.
        def checkScore(point, today_pre, total_pre, today_test, total_test):
            pointmin = int(point * self.__eventrankmaster.pointrandmin / 100)
            pointmax = int(point * self.__eventrankmaster.pointrandmax / 100)
            if pointmin <= (today_test - today_pre) <= pointmax and pointmin <= (total_test - total_pre) <= pointmax:
                return True
            else:
                return False
        
        point0 = self.__eventrankmaster.battlepoint_l
        point1 = self.__eventrankmaster.battlepointreceive
        scorerecord0 = BackendApi.get_battleevent_scorerecord(model_mgr, self.__eventmaster.id, self.__player0.id)
        scorerecord1 = BackendApi.get_battleevent_scorerecord(model_mgr, self.__eventmaster.id, self.__player1.id)
        if scorerecord0 is None:
            raise AppTestError(u'スコアレコードが作られていない')
        elif not checkScore(point0, self.__score0[0], self.__score0[1], scorerecord0.getPointToday(), scorerecord0.point_total):
            raise AppTestError(u'スコアレコードが正しくない')
        elif scorerecord0.getWinToday() != 0:
            raise AppTestError(u'勝利数が正しくない')
        
        if scorerecord1 is None:
            raise AppTestError(u'受けた方のスコアレコードが作られていない')
        elif not checkScore(point1, self.__score1[0], self.__score1[1], scorerecord1.getPointToday(), scorerecord1.point_total):
            raise AppTestError(u'受けた方のスコアレコードが正しくない')
        
        # 履歴が増えているか.
        if (self.__log_num0+1) != BackendApi.get_battleevent_battlelog_num(model_mgr, self.__player0.id):
            raise AppTestError(u'勝った方の履歴数が正しくない')
        elif (self.__log_num1+1) != BackendApi.get_battleevent_battlelog_num(model_mgr, self.__player1.id):
            raise AppTestError(u'負けた方の履歴数が正しくない')
        
        # プレゼントが増えているか.
        if (self.__present_num + 1) != BackendApi.get_present_num(self.__player0.id):
            raise AppTestError(u'プレゼントが届いていない')
        
        # お金が増えているか.
        playergold = model_mgr.get_model(PlayerGold, self.__player0.id)
        if playergold.gold != (self.__player0.gold+100):
            raise AppTestError(u'報酬のお金が付与されていない')
