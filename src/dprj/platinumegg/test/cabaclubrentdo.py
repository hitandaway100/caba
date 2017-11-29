# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.test.cabaclubtestpage import CabaclubTest
from platinumegg.app.cabaret.models.CabaretClub import CabaClubStorePlayerData,\
    CabaClubScorePlayerData
from platinumegg.app.cabaret.util.cabaclub_store import CabaclubStoreSet

class ApiTest(CabaclubTest):
    """キャバクラシステム店舗借り入れ書き込み.
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
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_DAYS : self.__storemaster.days_0,
        }
        return params
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%d' % self.__storemaster.id
    
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
