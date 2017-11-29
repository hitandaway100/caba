# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase

class ApiTest(BattleEventApiTestBase):
    """バトルイベントオープニング.
    """
    def setUp2(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # イベントマスター.
        eventmaster = self.setUpEvent(model_mgr=model_mgr)
        self.__eventmaster = eventmaster
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        url = self.response.get('redirect_url')
        if not url:
            raise AppTestError(u'リダイレクト先が設定されていない')
        elif url.find('eventscenario') == -1:
            raise AppTestError(u'演出に遷移していない')
        
        model_mgr = ModelRequestMgr()
        if BackendApi.check_battleevent_lead_opening(model_mgr, self.__player0.id, self.__eventmaster.id):
            raise AppTestError(u'演出の閲覧時間が更新されていない')
