# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerLogin
import datetime
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusMaster,\
    AccessBonusMaster
from platinumegg.app.cabaret.util.api import BackendApi

class ApiTest(ApiTestBase):
    """ログインボーナス受け取り(アクセスボーナス).
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__player.pdays = 0
        self.__player.lbtime = OSAUtil.get_now() - datetime.timedelta(days=1)
        self.__player.getModel(PlayerLogin).save()
        
        model_mgr = ModelRequestMgr()
        # ログインボーナスを消しておく.
        for model in model_mgr.get_mastermodel_all(LoginBonusMaster):
            model_mgr.set_delete(model)
        for model in model_mgr.get_mastermodel_all(AccessBonusMaster):
            model_mgr.set_delete(model)
        # 全プレ渡しておくかぁ.
        presenteveryone_list = BackendApi.get_presenteveryone_list_forloginbonus(model_mgr)
        if presenteveryone_list:
            BackendApi.tr_receive_presenteveryone(model_mgr, self.__player.id, presenteveryone_list)
        
        # ロングログインの設定も消しておく.
        config = BackendApi.get_current_loginbonustimelimitedconfig(model_mgr)
        self.__datalist = [data[1] for data in config.datalist]
        BackendApi.update_loginbonustimelimitedconfig(model_mgr, [])
        
        model_mgr.write_all()
        model_mgr.write_end()
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100)
        
        # アクセスボーナス.
        self.create_dummy(DummyType.ACCESS_BONUS_MASTER, 1, prizes=[prize.id])
        
        # プレゼント数.
        self.__present_num = BackendApi.get_present_num(self.__player.id, model_mgr)
        
        BackendApi.update_totalloginbonusconfig(model_mgr, 0, stime=OSAUtil.get_datetime_min(), etime=OSAUtil.get_datetime_min(), mid_next=0, continuity_login=False)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def check(self):
        model_mgr = ModelRequestMgr()
        playerlogin = PlayerLogin.getByKey(self.__player.id)
        # プレイ日数.
        if playerlogin.pdays != (self.__player.pdays+1):
            raise AppTestError(u'プレイ日数が正しくない')
        # ログインボーナス受取済みフラグ.
        elif not BackendApi.check_loginbonus_received(playerlogin):
            raise AppTestError(u'ログインボーナスを受け取っていない')
        # プレゼント数.
        elif (self.__present_num + 1) != BackendApi.get_present_num(self.__player.id, model_mgr):
            raise AppTestError(u'プレゼントが正しく付与されていない')
    
    def finish(self):
        model_mgr = ModelRequestMgr()
        BackendApi.update_loginbonustimelimitedconfig(model_mgr, self.__datalist)
