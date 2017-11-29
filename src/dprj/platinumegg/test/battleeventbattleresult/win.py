# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase
from platinumegg.app.cabaret.util.redisbattleevent import BattleEventOppList
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.apprandom import AppRandom

class ApiTest(BattleEventApiTestBase):
    """バトルイベント結果(勝利).
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
        BattleEventOppList.create(self.__player0.id, [player.id]).save()
        self.__player1 = player
        
        # 対戦書き込み.
        model_mgr = ModelRequestMgr()
        v_deck = BackendApi.get_deck(self.__player0.id, model_mgr)
        o_deck = BackendApi.get_deck(self.__player1.id, model_mgr)
        v_deck_cardlist = BackendApi.get_cards(v_deck.to_array(), model_mgr)
        o_deck_cardlist = BackendApi.get_cards(o_deck.to_array(), model_mgr)
        data = BackendApi.battle(self.__player0, v_deck_cardlist, self.__player1, o_deck_cardlist, AppRandom(), self.__eventmaster)
        BackendApi.tr_battleevent_battle(model_mgr, eventmaster, eventrankmaster, eventrankmaster, self.__player0, self.__player1, v_deck.to_array(), o_deck.to_array(), data, 1, None, False, self.__player0.req_confirmkey, now=OSAUtil.get_now())
        model_mgr.write_all()
        model_mgr.write_end()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%d' % self.__eventmaster.id
    
    def check(self):
        keys = (
            'player',
            'o_player',
            'resultdata',
            'prize',
            'levelupcardlist',
            'item_list',
            'battleevent_score',
            'url_battleevent_top',
            'url_battleevent_ranking',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
