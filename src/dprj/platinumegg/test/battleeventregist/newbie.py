# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
import datetime

class ApiTest(BattleEventApiTestBase):
    """バトルイベント登録.
    新規で参加.
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
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        url = self.response.get('redirect_url')
        if not url:
            raise AppTestError(u'リダイレクト先が設定されていない')
        elif url.find('/battleeventtop/') == -1:
            raise AppTestError(u'イベントTOPに遷移していない')
        
        model_mgr = ModelRequestMgr()
        rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, self.__eventmaster.id, self.__player0.id)
        if rankrecord is None:
            raise AppTestError(u'ランク情報が保存されていない')
        elif not rankrecord.groups:
            raise AppTestError(u'グループが設定されていない')
        
        groupid = rankrecord.groups[-1]
        group = BackendApi.get_battleevent_group(model_mgr, groupid)
        logintime = DateTimeUtil.toLoginTime(OSAUtil.get_now())
        today = datetime.date(logintime.year, logintime.month, logintime.day)
        if group is None:
            raise AppTestError(u'グループが存在しない')
        elif not self.__player0.id in group.useridlist:
            raise AppTestError(u'グループに参加設定されていない')
        elif not self.__player0.id in group.useridlist:
            raise AppTestError(u'グループに参加設定されていない')
        elif group.cdate != today:
            raise AppTestError(u'グループの日付がおかしい')
