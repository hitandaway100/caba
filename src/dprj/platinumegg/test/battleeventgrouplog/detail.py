# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase
import datetime
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventRank

class ApiTest(BattleEventApiTestBase):
    """バトルイベントバトル履歴詳細.
    """
    def setUp2(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.makePlayer(1000)
        
        # イベントマスター.
        eventmaster = self.setUpEvent(model_mgr=model_mgr)
        self.__eventmaster = eventmaster
        
        # ランクのマスター.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=1000)
        params = {
            'winprizes' : [{
                'prizes' : [prize.id],
                'rate' : 100,
            }],
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
        
        # ログインしておく.
        self.setLoginBonusReceived(self.__player0.id)
        
        cdate = datetime.date.today() - datetime.timedelta(days=1)
        rankrecord = BattleEventRank.getByKey(BattleEventRank.makeID(self.__player0.id, self.__eventmaster.id))
        rankmaster = self.createRankMaster(params=params)
        self.__ranklog = self.addRankLog(rankrecord, rankmaster, cdate)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/detail/%d' % self.__ranklog.id
    
    def check(self):
        keys = (
            'battleevent_rank',
            'playerlist',
            'url_battleevent_ranklog',
            'url_battleevent_top',
            'url_battleevent_explain',
            'url_battleevent_ranking',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
