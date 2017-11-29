# -*- coding: utf-8 -*-
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.lbsugorokudo import SugorokuApiTest
from platinumegg.lib.opensocial.util import OSAUtil

class ApiTest(SugorokuApiTest):
    """双六ログインボーナス(達成済み報酬をもらう).
    """
    def setUp(self):
        # マップ.
        mapdata = self.create_map(3)
        self.__map_master = mapdata.map_master
        self.__mass_dict = mapdata.mass_dict
        # 停まるマス.
        self.update_squares_master(mapdata.mass_dict[3], last=True)
        # ログインボーナス.
        self.__loginbonus_master = self.create_loginbonus([mapdata.map_master.id])
        # プレイヤー.
        self.__player = self.create_dummy(DummyType.PLAYER)
        # 進行情報作成.
        self.__playdata = self.create_dummy(DummyType.LOGIN_BONUS_SUGOROKU_PLAYER_DATA, uid=self.__player.id, mid=self.__loginbonus_master.id, loc=3)
        self.__present_num = BackendApi.get_present_num(self.__player.id)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def check(self):
        # レスポンスの内容を確認.
        self.check_response(self.__loginbonus_master)
        # プレイヤー情報を確認.
        model_mgr = ModelRequestMgr()
        playerdata = BackendApi.get_loginbonus_sugoroku_playerdata(model_mgr, self.__player.id, self.__loginbonus_master.id)
        self.check_playerdata(playerdata, 3, [self.__mass_dict[3].id], self.__present_num + 1, number=0)
