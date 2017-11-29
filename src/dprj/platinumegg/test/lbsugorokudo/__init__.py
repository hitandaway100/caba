# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from collections import namedtuple
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusSugorokuMapMaster

class SugorokuApiTest(ApiTestBase):
    """双六ログインボーナス.
    """
    def __init__(self, *args, **kwargs):
        ApiTestBase.__init__(self, *args, **kwargs)
        self.__config_datalist = None
    
    def create_map(self, squares_num):
        """双六のマップを作成.
        """
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100)
        # マップ.
        map_master = self.create_dummy(DummyType.LOGIN_BONUS_SUGOROKU_MAP_MASTER, prizeidlist=[prize.id])
        # マス作成.
        mass_dict = dict([(i+1, self.create_dummy(DummyType.LOGIN_BONUS_SUGOROKU_MAP_SQUARES_MASTER, map_master.id, i+1)) for i in xrange(squares_num)])
        return namedtuple("SugorokuMap", "map_master,mass_dict")(map_master, mass_dict)
    
    def create_loginbonus(self, maplist, is_open=True):
        """双六のログインボーナスを作成.
        """
        map_id_list = [map_id.id if isinstance(map_id, LoginBonusSugorokuMapMaster) else map_id for map_id in maplist]
        loginbonusmaster = self.create_dummy(DummyType.LOGIN_BONUS_SUGOROKU_MASTER, map_id_list)
        if is_open:
            # ログインボーナスを設定.
            model_mgr = ModelRequestMgr()
            config = BackendApi.get_current_loginbonustimelimitedconfig(model_mgr)
            if self.__config_datalist is None:
                self.__config = config
                self.__config_datalist = config.datalist[:]
                config.datalist = []
            config.setData(loginbonusmaster.id, OSAUtil.get_now(), OSAUtil.get_datetime_max(), sugoroku=True)
            config.save()
            model_mgr.save_models_to_cache([config])
        return loginbonusmaster
    
    def update_squares_master(self, squares_master, **kwargs):
        for k,v in kwargs.items():
            setattr(squares_master, k, v)
        squares_master.save()
    
    def check_response(self, loginbonus_master):
        # 進行情報確認.
        redirect_url = self.response.get('redirect_url') or ''
        if redirect_url.find('/lbsugorokuanim/{}/0/'.format(loginbonus_master.id)) == -1:
            raise AppTestError(u'リダイレクト先が正しくない.{}'.format(self.loginbonus_master.id))
    
    def check_playerdata(self, playerdata, location, square_id_list, present_num, number=6, lose_turns=0):
        if playerdata.result.get('number') != number:
            raise AppTestError(u'出目が正しくない.{}'.format(playerdata.result.get('number')))
        elif playerdata.loc != location:
            raise AppTestError(u'現在地が正しくない.{}'.format(playerdata.loc))
        elif playerdata.lose_turns != lose_turns:
            raise AppTestError(u'残り休み回数が正しくない.')
        elif playerdata.result.get('square_id_list') != square_id_list:
            raise AppTestError(u'停まったマスが正しくない.')
        elif present_num != BackendApi.get_present_num(playerdata.uid):
            raise AppTestError(u'報酬が付与されていない.')
    
    def finish(self):
        if self.__config_datalist is not None:
            # 設定を戻す.
            self.__config.datalist = self.__config_datalist
            self.__config.save()
            ModelRequestMgr().save_models_to_cache([self.__config])
