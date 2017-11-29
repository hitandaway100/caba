# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Card import Deck
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerDeck, PlayerGold
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.apprandom import AppRandom

class ApiTest(ApiTestBase):
    """バトル結果(敗北).
    """
    
    def setUp(self):
        # DMMID.
        self.__player = self.makePlayer(10)
        self.__o_player = self.makePlayer(1000)
        self.__o_player.getModel(PlayerGold).save()
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100)
        
        # ランク.
        prizes = [{'prizes':[prize.id], 'rate':10}]
        self.__rankmaster = self.create_dummy(DummyType.BATTLE_RANK_MASTER, win=10, times=10, loseprizes=prizes)
        # 最大ランクを作っておく.
        self.create_dummy(DummyType.BATTLE_RANK_MASTER, win=10, times=10, loseprizes=prizes)
        
        # 対戦相手設定.
        self.__battleplayer = self.create_dummy(DummyType.BATTLE_PLAYER, self.__player.id, self.__rankmaster.id, oid=self.__o_player.id, win=0, times=self.__rankmaster.times - 1)
        
        model_mgr = ModelRequestMgr()
        v_deck = BackendApi.get_deck(self.__player.id, model_mgr)
        o_deck = BackendApi.get_deck(self.__o_player.id, model_mgr)
        v_deck_cardlist = BackendApi.get_cards(v_deck.to_array(), model_mgr)
        o_deck_cardlist = BackendApi.get_cards(o_deck.to_array(), model_mgr)
        data = BackendApi.battle(self.__player, v_deck_cardlist, self.__o_player, o_deck_cardlist, AppRandom())
        BackendApi.tr_battle(model_mgr, self.__player, self.__o_player, v_deck.to_array(), o_deck.to_array(), data, self.__battleplayer.result)
        model_mgr.write_all()
        model_mgr.write_end()
    
    def makePlayer(self, power):
        player = self.create_dummy(DummyType.PLAYER)
        player.deckcapacitylv = 999
        player.getModel(PlayerDeck).save()
        
        # デッキ.
        deck = Deck(id=player.id)
        
        arr = []
        for _ in xrange(Defines.DECK_CARD_NUM_MAX - 3):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER, basepower=power, maxpower=power)
            card = self.create_dummy(DummyType.CARD, player, cardmaster)
            arr.append(card.id)
        deck.set_from_array(arr)
        deck.save()
        
        return player
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        keys = (
            'player',
            'o_player',
            'resultdata',
            'levelupcardlist',
            'item_list',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
