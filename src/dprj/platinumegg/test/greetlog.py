# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Card import Deck

class ApiTest(ApiTestBase):
    """あいさつ履歴.
    """
    
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        uid = self.__player.id
        
        for _ in xrange(16):
            o_player = self.create_dummy(DummyType.PLAYER)
            oid = o_player.id
            model_mgr = ModelRequestMgr()
            deck = Deck(id=oid)
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            deck.leader = self.create_dummy(DummyType.CARD, o_player, cardmaster).id
            model_mgr.set_save(deck)
            BackendApi.tr_greet(model_mgr, oid, uid, False)
            model_mgr.write_all()
            model_mgr.write_end()
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def check(self):
        keys = (
            'greetlog_list',
#            'url_next',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
