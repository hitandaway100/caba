# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase
from platinumegg.app.cabaret.models.battleevent.BattleEventPresent import BattleEventPresentData

class ApiTest(BattleEventApiTestBase):
    """バトルイベント贈り物ページ(一覧表示).
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
        
        # 贈り物マスター.
        self.__presentmaster = self.makePresentMaster(eventmaster.id, 1, point=100)
        
        # 贈り物のユーザ情報.
        self.makePresentData(self.__player0.id, eventmaster.id, cur_presentmaster=self.__presentmaster)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        keys = (
            'battleeventpresent',
            'battleevent',
        )
        for k in keys:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない')
        
        # データ確認.
        key = BattleEventPresentData.makeID(self.__player0.id, self.__presentmaster.eventid)
        battleeventpresentdata = BattleEventPresentData.getByKey(key)
        if battleeventpresentdata is None:
            raise AppTestError(u'ポイント情報が作成されていない')
        
        data = battleeventpresentdata.getData()
        if data is None:
            raise AppTestError(u'内容が設定されていない')
        elif data['number'] != self.__presentmaster.number or data['content'] != self.__presentmaster.contents[0][0]:
            raise AppTestError(u'内容が想定と違う')
