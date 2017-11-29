# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase

class ApiTest(BattleEventApiTestBase):
    """バトルイベント対戦相手にらみ合い.
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
        
        # 対戦相手を設定.
        player = self.create_dummy(DummyType.PLAYER)
        self.joinRank(player.id)
        # 仕返し作成.
        revenge = self.createRevenge(self.__player0.id, player.id)
        self.__player1 = player
        self.__revenge = revenge
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%d/%d' % (self.__player1.id, self.__revenge.id)
    
    def check(self):
        keys = (
            'player',
            'o_player',
            'battleevent_rank',
            'url_battle_do',
            'url_battle_oppselect',
        )
        for k in keys:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない' % k)
