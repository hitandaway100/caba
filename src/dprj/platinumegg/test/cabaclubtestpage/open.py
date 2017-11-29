# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.test.cabaclubtestpage import CabaclubTest
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.CabaretClub import CabaClubStorePlayerData
from platinumegg.app.cabaret.util.cabaclub_store import CabaclubStoreSet

class ApiTest(CabaclubTest):
    """キャバクラシステムの機能面の動作確認.
    店舗開店.
    """
    
    def setUp(self):
        ua_type = Defines.CabaClubEventUAType.LIVEN_UP
        # ユーザーを用意.
        self.__player = self.create_dummy(DummyType.PLAYER)
        # 店舗を用意.
        cabaclub_dummy = self.setUpCabaclub(self.__player)
        self.__storemaster = cabaclub_dummy.stores[ua_type]
        # 開店実行.
        def tr():
            model_mgr = ModelRequestMgr()
            BackendApi.tr_cabaclub_store_open(model_mgr, self.__player.id, self.__storemaster, cabaclub_dummy.now)
            model_mgr.write_all()
            model_mgr.write_end()
        db_util.run_in_transaction(tr)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        storeplayerdata = CabaClubStorePlayerData.getByKey(CabaClubStorePlayerData.makeID(self.__player.id, self.__storemaster.id))
        store = CabaclubStoreSet(self.__storemaster, storeplayerdata)
        if not store.is_alive(OSAUtil.get_now()):
            raise AppTestError(u'期限が切れています')
        elif not store.playerdata.is_open:
            raise AppTestError(u'開店していません')
