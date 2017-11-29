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
from platinumegg.app.cabaret.util.cabaclub_store import CabaclubStoreSet

class ApiTest(CabaclubTest):
    """キャバクラシステムの機能面の動作確認.
    店舗借り入れ.
    """
    
    def setUp(self):
        ua_type = Defines.CabaClubEventUAType.LIVEN_UP
        # ユーザーを用意.
        self.__player = self.create_dummy(DummyType.PLAYER)
        # 店舗を用意.
        cabaclub_dummy = self.setUpCabaclub(self.__player)
        self.__cabaclub_dummy = cabaclub_dummy
        self.__storemaster = cabaclub_dummy.stores[ua_type]
        # 期限切れにしておく.
        storeplayerdata = cabaclub_dummy.storeplayerdata[ua_type]
        storeplayerdata.ltime = OSAUtil.get_datetime_min()
        storeplayerdata.customer = 1000
        storeplayerdata.proceeds = 2000
        storeplayerdata.save()
        # 借り入れ実行.
        def tr():
            model_mgr = ModelRequestMgr()
            BackendApi.tr_cabaclub_store_rent(model_mgr, self.__player.id, self.__storemaster.id, self.__storemaster.days_0, cabaclub_dummy.now)
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
        store = CabaclubStoreSet(self.__storemaster, storeplayerdata)
        if not store.is_alive(OSAUtil.get_now()):
            raise AppTestError(u'借り入れできていません')
        elif storeplayerdata.customer != 0 or storeplayerdata.proceeds != 0:
            raise AppTestError(u'スコア情報がリセットされていません')
        # 特別なマネーの確認.
        scoredata = CabaClubScorePlayerData.getByKey(self.__player.id)
        if (self.__cabaclub_dummy.score.money - scoredata.money) != self.__storemaster.cost_0:
            raise AppTestError(u'特別なマネーが正しく消費されていません')
