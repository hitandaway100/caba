# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase
from platinumegg.app.cabaret.util.redisbattleevent import BattleEventOppList
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.apprandom import AppRandom
from platinumegg.app.cabaret.models.Player import PlayerRequest

class ApiTest(BattleEventApiTestBase):
    """バトルイベントバトル履歴.
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
        
        for _ in xrange(4):
            # 仕掛けて勝利.
            player = self.makePlayer(10)
            self.joinRank(player.id)
            self.battle(self.__player0, player)
            
            # 仕掛けて敗北.
            player = self.makePlayer(10000)
            self.joinRank(player.id)
            self.battle(self.__player0, player)
            
            # 受けて勝利.
            player = self.makePlayer(10)
            self.joinRank(player.id)
            self.battle(player, self.__player0)
            
            # 受けて敗北.
            player = self.makePlayer(10000)
            self.joinRank(player.id)
            self.battle(player, self.__player0)
    
    def battle(self, player, o_player):
        
        BattleEventOppList.create(player.id, [o_player.id]).save()
        
        model_mgr = ModelRequestMgr()
        v_deck = BackendApi.get_deck(player.id, model_mgr)
        o_deck = BackendApi.get_deck(o_player.id, model_mgr)
        v_deck_cardlist = BackendApi.get_cards(v_deck.to_array(), model_mgr)
        o_deck_cardlist = BackendApi.get_cards(o_deck.to_array(), model_mgr)
        data = BackendApi.battle(player, v_deck_cardlist, o_player, o_deck_cardlist, AppRandom(), self.__eventmaster)
        BackendApi.tr_battleevent_battle(model_mgr, self.__eventmaster, self.__eventrankmaster, self.__eventrankmaster, player, o_player, v_deck.to_array(), o_deck.to_array(), data, 1, None, False, player.req_confirmkey, now=OSAUtil.get_now())
        model_mgr.write_all()
        model_mgr.write_end()
        
        self.__player0.setModel(BackendApi.get_model(model_mgr, PlayerRequest, self.__player0.id))
    
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
            'battleloglist',
            'url_battleevent_top',
            'url_battleevent_explain',
            'url_battleevent_ranking',
#            'url_page_next',
            'cur_page',
            'page_max',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
