# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase
from defines import Defines
from platinumegg.app.cabaret.util.redisbattleevent import BattleEventOppList

class ApiTest(BattleEventApiTestBase):
    """バトルイベント対戦相手更新.
    """
    def setUp2(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # イベントマスター.
        eventmaster = self.setUpEvent(model_mgr=model_mgr)
        self.__eventmaster = eventmaster
        
        # ランクのマスター.
        eventrankmaster = self.createRankMaster()
        self.__eventrankmaster = eventrankmaster
        
        # オープニングを閲覧済みに.
        self.setOpeningViewTime(self.__player0.id)
        
        # 参加させておく.
        self.joinRank(self.__player0.id)
        
        # 参加させておく.
        self.setLoginBonusReceived(self.__player0.id)
        
        # 対戦相手候補を作成.
        for _ in xrange(Defines.BATTLEEVENT_OPPONENT_NUM):
            player = self.create_dummy(DummyType.PLAYER)
            self.joinRank(player.id)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/lv/1'
    
    def check(self):
        url = self.response.get('redirect_url')
        if not url:
            raise AppTestError(u'リダイレクト先が設定されていない')
        elif url.find('/battleeventopplist/lv/0') == -1:
            raise AppTestError(u'正しく遷移していない')
        
        model = BattleEventOppList.get(self.__player0.id)
        if model is None:
            # 対戦相手が設定されていない.
            raise AppTestError(u'対戦相手が設定されていない')
