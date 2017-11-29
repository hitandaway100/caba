# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase
import urllib
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventRevenge
from platinumegg.app.cabaret.models.Player import PlayerGold

class ApiTest(BattleEventApiTestBase):
    """バトルイベント対戦書き込み(仕返しで勝利).
    """
    def setUp2(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.makePlayer(1000)
        
        # イベントマスター.
        eventmaster = self.setUpEvent(model_mgr=model_mgr)
        self.__eventmaster = eventmaster
        
        # ランクのマスター.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER, mid=Defines.ItemEffect.ACTION_SMALL_RECOVERY, evalue=2)
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, item=itemmaster)
        params = {
            'winprizes' : [{
                'prizes' : [prize.id],
                'rate' : 100,
            }],
            'battlepoint_w' : 100,
            'battlepoint_lv' : 10,
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
        player = self.makePlayer(10)
        self.joinRank(player.id)
        # 仕返し作成.
        revenge = self.createRevenge(self.__player0.id, player.id)
        self.__player1 = player
        self.__revenge = revenge
        
        # 書き込み前のプレゼント数.
        self.__present_num = BackendApi.get_present_num(self.__player0.id)
        
        # 書き込み前のバトルポイント.
        def score(model):
            if model:
                return model.getPointToday(), model.point_total, model.getWinToday()
            else:
                return 0, 0, 0
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
        return u'/%s/%d/%d' % (urllib.quote(self.__player0.req_confirmkey, ''), self.__player1.id, self.__revenge.id)
    
    def check(self):
        model_mgr = ModelRequestMgr()
        # 結果が保存されているか.
        battleresult = BackendApi.get_battleevent_battleresult(model_mgr, self.__eventmaster.id, self.__player0.id)
        if battleresult is None:
            raise AppTestError(u'結果が保存されていない')
        elif battleresult.result != Defines.BattleResultCode.WIN:
            raise AppTestError(u'結果が想定と違う.%d' % battleresult.result)
        
        # バトルポイント.
        def checkScore(point, today_pre, total_pre, today_test, total_test):
            pointmin = int(point * self.__eventrankmaster.pointrandmin / 100)
            pointmax = int(point * self.__eventrankmaster.pointrandmax / 100)
            if pointmin <= (today_test - today_pre) <= pointmax and pointmin <= (total_test - total_pre) <= pointmax:
                return True
            else:
                return False
        
        point = self.__eventrankmaster.battlepoint_w
        point += max(0, self.__player1.level - self.__player0.level) * self.__eventrankmaster.battlepoint_lv
        scorerecord0 = BackendApi.get_battleevent_scorerecord(model_mgr, self.__eventmaster.id, self.__player0.id)
        scorerecord1 = BackendApi.get_battleevent_scorerecord(model_mgr, self.__eventmaster.id, self.__player1.id)
        if scorerecord0 is None:
            raise AppTestError(u'勝った方のスコアレコードが作られていない')
        elif not checkScore(point, self.__score0[0], self.__score0[1], scorerecord0.getPointToday(), scorerecord0.point_total):
            raise AppTestError(u'スコアレコードが正しくない')
        elif (scorerecord0.getWinToday()-1) != self.__score0[2]:
            raise AppTestError(u'勝利数が正しくない')
        
        if scorerecord1 and self.__score1 != (scorerecord1.getPointToday(), scorerecord1.point_total, scorerecord1.getWinToday()):
            raise AppTestError(u'負けた方のスコアレコードが正しくない')
        
        # 履歴が増えているか.
        if (self.__log_num0+1) != BackendApi.get_battleevent_battlelog_num(model_mgr, self.__player0.id):
            raise AppTestError(u'勝った方の履歴数が正しくない')
        elif (self.__log_num1+1) != BackendApi.get_battleevent_battlelog_num(model_mgr, self.__player1.id):
            raise AppTestError(u'負けた方の履歴数が正しくない')
        
        # 仕返しレコードが更新されているか.
        revenge = BattleEventRevenge.getByKey(self.__revenge.id)
        if revenge is None:
            raise AppTestError(u'仕返しレコードがない')
        elif revenge.uid != self.__player1.id or revenge.oid != self.__player0.id:
            raise AppTestError(u'仕返しレコードが正しく更新されていない')
        
        # プレゼントが増えているか.
        if (self.__present_num + 1) != BackendApi.get_present_num(self.__player0.id):
            raise AppTestError(u'プレゼントが届いていない')
        
        # お金が増えているか.
        playergold = model_mgr.get_model(PlayerGold, self.__player0.id)
        if playergold.gold != (self.__player0.gold+100):
            raise AppTestError(u'報酬のお金が付与されていない')
