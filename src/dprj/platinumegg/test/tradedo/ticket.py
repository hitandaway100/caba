# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerTreasure, PlayerRequest,\
    PlayerGachaPt
from defines import Defines
import urllib
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class ApiTest(ApiTestBase):
    """宝箱一覧.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__trade = self.create_dummy(DummyType.TRADE_MASTER, Defines.ItemType.TRYLUCKTICKET, 0, 1, 1, 1)
        
        NUM = 10
        
        # 秘宝交換する為、秘宝の数を変えておく
        player_treasure = self.__player.getModel(PlayerTreasure)
        
        player_treasure.cabaretking = NUM
        player_treasure.demiworld = NUM
        player_treasure.save()
        self.__treasurenum = player_treasure.get_cabaretking_num()
        
        self.__ticketnum = BackendApi.get_num_by_itemtype(ModelRequestMgr(), self.__player, self.__trade.itype)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def get_urlargs(self):
        return '/%d/%s/' % (self.__trade.id, urllib.quote(self.__player.req_confirmkey, ''))
    
    def check(self):
        
        playerrequest = PlayerRequest.getByKey(self.__player.id)
        if playerrequest.req_confirmkey == self.__player.req_confirmkey:
            raise AppTestError(u'確認キーが更新されていない')
        elif playerrequest.req_alreadykey != self.__player.req_confirmkey:
            raise AppTestError(u'確認済みのキーが正しく設定されていない')
        
        # 秘宝.
        playertreasure = PlayerTreasure.getByKey(self.__player.id)
        cabaretking = playertreasure.get_cabaretking_num()
        if cabaretking == self.__treasurenum:
            raise AppTestError(u'キャバ王の秘宝所持数が減っていない')
        elif cabaretking != (self.__treasurenum - self.__trade.rate_cabaretking):
            raise AppTestError(u'キャバ王の秘宝所持数が正しくない')
        
        # チケット数.
        playergachapt = PlayerGachaPt.getByKey(self.__player.id)
        ticketnum = BackendApi.get_num_by_itemtype(ModelRequestMgr(), playergachapt, self.__trade.itype)
        if ticketnum == self.__ticketnum:
            raise AppTestError(u'チケットの所持数が変わっていない')
        elif ticketnum != (self.__ticketnum + self.__trade.itemnum):
            raise AppTestError(u'チケットの所持数が正しくない')
