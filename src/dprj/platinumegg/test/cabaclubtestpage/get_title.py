# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.Title import TitlePlayerData

class ApiTest(ApiTestBase):
    """称号獲得.
    """
    
    def setUp(self):
        self.__now = OSAUtil.get_now()
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        # 名誉ポイント.
        self.create_dummy(DummyType.CABA_CLUB_SCORE_PLAYER_DATA, uid=self.__player.id, point=200)
        # 称号情報.
        self.create_dummy(DummyType.TITLE_PLAYER_DATA, uid=self.__player.id)
        # 称号獲得書き込み関数.
        def tr(titlemaster):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_title_get(model_mgr, self.__player.id, titlemaster, self.__now)
            model_mgr.write_all()
            model_mgr.write_end()
        # 未設定から設定.
        titlemaster = self.create_dummy(DummyType.TITLE_MASTER, cost=100)
        db_util.run_in_transaction(tr, titlemaster)
        # 設定中の上書き.
        self.__titlemaster = self.create_dummy(DummyType.TITLE_MASTER, cost=100)
        db_util.run_in_transaction(tr, self.__titlemaster)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        titleplayerdata = TitlePlayerData.getByKey(self.__player.id)
        if titleplayerdata.title != self.__titlemaster.id:
            raise AppTestError(u'称号が正しく設定されていません')
        elif titleplayerdata.stime.strftime("%Y%m%d%H%M%S") != self.__now.strftime("%Y%m%d%H%M%S"):
            raise AppTestError(u'stimeが正しくありません')
