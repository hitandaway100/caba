# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase
from defines import Defines

class ApiTest(BattleEventApiTestBase):
    """バトルイベント説明ページ(指名キャスト).
    """
    def setUp2(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.makePlayer(1000)
        
        # イベントマスター.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100)
        eventmaster_kwargs = {
            'rankingprizes' : [{
                'rank_min' : 1,
                'rank_max' : 10,
                'prize' : [prize.id],
            },
            {
                'rank_min' : 11,
                'rank_max' : 20,
                'prize' : [prize.id],
            }]
        }
        eventmaster = self.setUpEvent(eventmaster_kwargs, model_mgr=model_mgr)
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
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
            Defines.URLQUERY_CTYPE:'ranking',
        }
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%d/prizes' % self.__eventmaster.id
    
    def check(self):
        keys = (
            'battleevent_score',
            'is_opened',
            'url_explain_detail',
            'url_explain_prizes',
            'url_explain_faq',
            'url_battleevent_top',
            'url_battleevent_explain',
            'url_battleevent_ranking',
            'rankingprizelist',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
