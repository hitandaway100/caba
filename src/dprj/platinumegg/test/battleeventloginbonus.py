# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase
import datetime
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventRank

class ApiTest(BattleEventApiTestBase):
    """バトルイベントログインボーナス受け取り.
    """
    def setUp2(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # イベントマスター.
        eventmaster = self.setUpEvent(model_mgr=model_mgr)
        self.__eventmaster = eventmaster
        
        # ランクのマスター.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100)
        params = {
            'loginbonus' : [prize.id],
        }
        eventrankmaster = self.createRankMaster(params=params)
        self.__eventrankmaster = eventrankmaster
        
        # オープニングを閲覧済みに.
        self.setOpeningViewTime(self.__player0.id)
        
        # 参加させておく.
        self.joinRank(self.__player0.id)
        
        cdate = datetime.date.today()
        rankrecord = BattleEventRank.getByKey(BattleEventRank.makeID(self.__player0.id, self.__eventmaster.id))
        # 未受け取りにしておく.
        model_mgr = ModelRequestMgr()
        rankrecord.utime = OSAUtil.get_datetime_min()
        model_mgr.set_save(rankrecord)
        model_mgr.write_all()
        model_mgr.write_end()
        
        for _ in xrange(5):
            cdate -= datetime.timedelta(days=1)
            rankmaster = self.createRankMaster(params=params)
            self.addRankLog(rankrecord, rankmaster, cdate)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        keys = (
            'redirect_url',
        )
        for k in keys:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない' % k)
        if self.response['redirect_url'].find('battleeventloginbonusanim') == -1:
            raise AppTestError(u'演出に飛んでいない')
