# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerLogin
import datetime
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.AccessBonus import AccessBonusMaster
from platinumegg.app.cabaret.util.api import BackendApi
import cPickle

class ApiTest(ApiTestBase):
    """ログインボーナス受け取り(初回ログイン).
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__player.ldays = 2
        self.__player.lbtime = OSAUtil.get_now() - datetime.timedelta(days=2)
        self.__player.getModel(PlayerLogin).save()
        
        model_mgr = ModelRequestMgr()
        # アクセスボーナスを消しておく.
        for model in model_mgr.get_mastermodel_all(AccessBonusMaster):
            model_mgr.set_delete(model)
        # 全プレ渡しておくかぁ.
        presenteveryone_list = BackendApi.get_presenteveryone_list_forloginbonus(model_mgr)
        if presenteveryone_list:
            BackendApi.tr_receive_presenteveryone(model_mgr, self.__player.id, presenteveryone_list)
        
        model_mgr.write_all()
        model_mgr.write_end()
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100)
        
        # ログインボーナス.
        self.create_dummy(DummyType.LOGIN_BONUS_MASTER, 1, prizes=[prize.id])
        
        # 設定.
        model_mgr = ModelRequestMgr()
        config = BackendApi.get_current_totalloginbonusconfig(model_mgr)
        self.__ori_config = cPickle.dumps(config)
        BackendApi.update_totalloginbonusconfig(model_mgr, 0, OSAUtil.get_datetime_min(), OSAUtil.get_datetime_min(), continuity_login=True)
        
        # プレゼント数.
        self.__present_num = BackendApi.get_present_num(self.__player.id, model_mgr)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def check(self):
        model_mgr = ModelRequestMgr()
        playerlogin = PlayerLogin.getByKey(self.__player.id)
        # 連続ログイン日数.
        if playerlogin.ldays != 1:
            raise AppTestError(u'連続ログイン日数が正しくない.%d' % playerlogin.ldays)
        # プレイ日数.
        elif playerlogin.pdays != (self.__player.pdays+1):
            raise AppTestError(u'プレイ日数が正しくない')
        # ログインボーナス受取済みフラグ.
        elif not BackendApi.check_loginbonus_received(playerlogin):
            raise AppTestError(u'ログインボーナスを受け取っていない')
        # プレゼント数.
        elif (self.__present_num + 1) != BackendApi.get_present_num(self.__player.id, model_mgr):
            raise AppTestError(u'プレゼントが正しく付与されていない')
    
    def finish(self):
        model_mgr = ModelRequestMgr()
        config = cPickle.loads(self.__ori_config)
        BackendApi.update_totalloginbonusconfig(model_mgr, config.mid, config.stime, config.etime, config.continuity_login)
