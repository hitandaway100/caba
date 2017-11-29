# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase
from defines import Defines
from platinumegg.app.cabaret.util.redisbattleevent import BattleEventOppList

class ApiTest(BattleEventApiTestBase):
    """バトルイベント対戦相手(近いレベル).
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
        opplist = []
        for _ in xrange(Defines.BATTLEEVENT_OPPONENT_NUM):
            player = self.create_dummy(DummyType.PLAYER)
            self.joinRank(player.id)
            opplist.append(player.id)
        BattleEventOppList.create(self.__player0.id, opplist).save()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/lv/0'
    
    def check(self):
        keys = (
            'cur_topic',
            'url_battleevent_opplist_lv',
            'url_battleevent_opplist_revenge',
            'url_battleevent_opplist_update',
            'playerlist',
        )
        for k in keys:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない' % k)
        
        if self.response.get('cur_topic') != 'lv':
            raise AppTestError(u'トピックが違う')
        elif not self.response.get('playerlist'):
            raise AppTestError(u'対戦相手が設定されていない')
