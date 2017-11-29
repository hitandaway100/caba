# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Card import Deck

class ApiTest(ApiTestBase):
    """プロフィールページ.
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        self.__player1 = self.create_dummy(DummyType.PLAYER)
        
        # デッキ.
        deck = Deck(id=self.__player1.id)
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        deck.leader = self.create_dummy(DummyType.CARD, self.__player1, cardmaster).id
        
        for i in xrange(9):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            setattr(deck, 'mamber%d' % i, self.create_dummy(DummyType.CARD, self.__player1, cardmaster).id)
        deck.save()
    
    def get_urlargs(self):
        return '/%d' % self.__player1.id
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        keys = (
            'is_blacklist',
            'player',
            'leader',
            'newbie_cardlist',
            'is_friend',
            'did_send_friendrequest',
            'receive_friendrequest',
            'friend_num',
            'profilecomment',
            'battlekos',
            'rarelog',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
