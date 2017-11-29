# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.pc.base import PcTestBase
from platinumegg.app.cabaret.util.redisdb import RedisModel
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.playerlog import BossWinLog
from platinumegg.app.cabaret.models.Player import PlayerFriend

class ApiTest(PcTestBase):
    """仲間の近況.
    """
    
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        model = self.__player.getModel(PlayerFriend)
        model.friendlimit = 8
        model.save()
        
        def addRequest(v_player, o_player):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_friendrequest(model_mgr, v_player, o_player)
            model_mgr.write_all()
            model_mgr.write_end()
        
        def addFriend(v_player, o_player):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_friend(model_mgr, v_player.id, o_player.id)
            model_mgr.write_all()
            model_mgr.write_end()
        
        redisdb = RedisModel.getDB()
        pipe = redisdb.pipeline()
        for _ in xrange(model.friendlimit):
            player = self.create_dummy(DummyType.PLAYER)
            
            uid = player.id
            
            boss = self.create_dummy(DummyType.BOSS_MASTER)
            areamaster = self.create_dummy(DummyType.AREA_MASTER, boss.id)
            logdata = BossWinLog.makeData(uid, areamaster.id)
            logdata.oid = self.__player.id
            logdata.save()
            
            addRequest(self.__player, player)
            addFriend(player, self.__player)
        
        pipe.execute()
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def check(self):
        self.checkResponseStatus()
        
        keys = (
            'friendlog_list',
        )
        for k in keys:
            if self.resultbody.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
    
