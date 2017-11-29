# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.test.cabaclubtestpage import CabaclubTest
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.CabaretClub import CabaClubStorePlayerData,\
    CabaClubScorePlayerData

class ApiTest(CabaclubTest):
    """キャバクラシステムの機能面の動作確認.
    ユーザーアクション 盛り上げる.
    """
    
    def setUp(self):
        ua_type = Defines.CabaClubEventUAType.LIVEN_UP
        # ユーザーを用意.
        self.__player = self.create_dummy(DummyType.PLAYER)
        # 店舗を用意.
        cabaclub_dummy = self.setUpCabaclub(self.__player)
        self.__cabaclub_dummy = cabaclub_dummy
        self.__storemaster = cabaclub_dummy.stores[ua_type]
        self.__eventmaster = cabaclub_dummy.events[ua_type]
        # 前回更新時間を戻しておく.
        storeplayerdata = cabaclub_dummy.storeplayerdata[ua_type]
        storeplayerdata.is_open = True
        storeplayerdata.event_id = self.__eventmaster.id
        storeplayerdata.etime = cabaclub_dummy.now
        storeplayerdata.save()
        # ユーザアクション実行.
        def tr():
            model_mgr = ModelRequestMgr()
            BackendApi.tr_cabaclubstore_useraction(model_mgr, self.__player.id, self.__storemaster, cabaclub_dummy.now)
            model_mgr.write_all()
            model_mgr.write_end()
        db_util.run_in_transaction(tr)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        # 店舗情報の確認.
        storeplayerdata = CabaClubStorePlayerData.getByKey(CabaClubStorePlayerData.makeID(self.__player.id, self.__storemaster.id))
        if not storeplayerdata.ua_flag:
            raise AppTestError(u'ユーザアクションフラグが設定されていません')
        # 特別なマネーの確認.
        scoredata = CabaClubScorePlayerData.getByKey(self.__player.id)
        if (self.__cabaclub_dummy.score.money - scoredata.money) != self.__eventmaster.ua_cost:
            raise AppTestError(u'特別なマネーが正しく消費されていません')

