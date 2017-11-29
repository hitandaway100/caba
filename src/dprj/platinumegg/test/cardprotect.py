# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi

class ApiTest(ApiTestBase):
    """カード保護.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        model_mgr = ModelRequestMgr()
        protects = []
        for _ in xrange(5):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            card = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
            card.protection = True
            model_mgr.set_save(card)
            protects.append(card.id)
        
        not_protects = []
        for _ in xrange(5):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER)
            card = self.create_dummy(DummyType.CARD, self.__player, cardmaster)
            card.protection = False
            model_mgr.set_save(card)
            not_protects.append(card.id)
        
        model_mgr.write_all()
        model_mgr.write_end()
        
        self.__protects = protects
        self.__not_protects = not_protects
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_ADD:','.join([str(cid) for cid in self.__not_protects]),
            Defines.URLQUERY_REM:','.join([str(cid) for cid in self.__protects]),
        }
    
    def check(self):
        cardsetlist = BackendApi.get_cards(self.__not_protects)
        for cardset in cardsetlist:
            if not cardset.card.protection:
                raise AppTestError(u'保護設定されていない')
        cardsetlist = BackendApi.get_cards(self.__protects)
        for cardset in cardsetlist:
            if cardset.card.protection:
                raise AppTestError(u'保護設定が解除されていない')
