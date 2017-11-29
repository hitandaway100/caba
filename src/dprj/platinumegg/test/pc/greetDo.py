# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.test.pc.base import PcTestBase
from defines import Defines
from platinumegg.app.cabaret.models.Greet import GreetLog, GreetData,\
    GreetPlayerData
from platinumegg.app.cabaret.models.Player import PlayerGachaPt

class ApiTest(PcTestBase):
    """あいさつ実行.
    """
    
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        self.__player1 = self.create_dummy(DummyType.PLAYER)
        
        # 履歴を消しておく.
        for g in GreetLog.fetchValues(filters={'fromid':self.__player0.id,'toid':self.__player1.id}):
            g.delete()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
            Defines.URLQUERY_ID:self.__player1.id,
        }
    
    def check(self):
        self.checkResponseStatus()
        
        p = PlayerGachaPt.getByKey(self.__player0.id)
        if p.gachapt != Defines.GREET_GACHA_PT:
            raise AppTestError(u'引抜ポイントが加算されてない.%d' % p.gachapt)
        
        g = GreetData.getByKey(GreetData.makeID(self.__player0.id, self.__player1.id))
        if g is None:
            raise AppTestError(u'引抜データがない')
        
        g = GreetPlayerData.getByKey(self.__player0.id)
        if g is None:
            raise AppTestError(u'引抜プレイヤーデータがない')
        
        g = GreetLog.fetchValues(filters={'fromid':self.__player0.id,'toid':self.__player1.id})
        if len(g) < 1:
            raise AppTestError(u'履歴がない')
    
