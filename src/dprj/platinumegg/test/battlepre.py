# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Card import Deck
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerDeck

class ApiTest(ApiTestBase):
    """バトル確認.
    """
    
    def setUp(self):
        # DMMID.
        self.__player = self.makePlayer()
        self.__o_player = self.makePlayer()
        
        self.__rankmaster = self.create_dummy(DummyType.BATTLE_RANK_MASTER)
        self.__battleplayer = self.create_dummy(DummyType.BATTLE_PLAYER, self.__player.id, rank=self.__rankmaster.id, oid=self.__o_player.id)
    
    def makePlayer(self):
        player = self.create_dummy(DummyType.PLAYER)
        player.deckcapacitylv = 999
        player.getModel(PlayerDeck).save()
        
        # デッキ.
        deck = Deck(id=player.id)
        
        arr = []
        for _ in xrange(Defines.DECK_CARD_NUM_MAX - 3):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
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
            'battleplayer',
            'max_rank',
            'o_player',
            'item_list',
            'url_battle_do',
            'url_battle_oppselect',
            'opponent_change_restnum',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
