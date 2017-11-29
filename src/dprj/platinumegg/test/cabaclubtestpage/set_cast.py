# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.test.cabaclubtestpage import CabaclubTest
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.CabaretClub import CabaClubCastPlayerData

class ApiTest(CabaclubTest):
    """キャバクラシステムの機能面の動作確認.
    キャスト配置.
    """
    
    def setUp(self):
        ua_type = Defines.CabaClubEventUAType.LIVEN_UP
        # ユーザーを用意.
        self.__player = self.create_dummy(DummyType.PLAYER)
        # 店舗を用意.
        cabaclub_dummy = self.setUpCabaclub(self.__player)
        self.__cabaclub_dummy = cabaclub_dummy
        self.__storemaster = cabaclub_dummy.stores[ua_type]
        # キャストの配置を空にしておく.
        self.create_dummy(DummyType.CABA_CLUB_CAST_PLAYER_DATA, self.__player.id, self.__storemaster.id, [])
        self.__cardidlist = [card.id for card in cabaclub_dummy.cardlist]
        # 配置実行.
        def tr():
            model_mgr = ModelRequestMgr()
            BackendApi.tr_cabaclubstore_set_cast(model_mgr, self.__player.id, self.__storemaster, self.__cardidlist, cabaclub_dummy.now)
            model_mgr.write_all()
            model_mgr.write_end()
        db_util.run_in_transaction(tr)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        castdata = CabaClubCastPlayerData.getByKey(CabaClubCastPlayerData.makeID(self.__player.id, self.__storemaster.id))
        if len(castdata.cast) != len(set(castdata.cast) | set(self.__cardidlist)):
            raise AppTestError(u'キャストが正しく配置されていません')
