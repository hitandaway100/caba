# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.gacha import GachaBoxCardData,\
    GachaBoxGroupData, GachaBox
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerDeck,\
    PlayerRequest
from platinumegg.app.cabaret.models.Gacha import GachaPlayData, GachaPlayCount
from platinumegg.app.cabaret.util.api import BackendApi

class ApiTest(ApiTestBase):
    """引抜実行(引抜ポイント).
    """
    def setUp(self):
        # カード.
        table = []
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        data = GachaBoxCardData(cardmaster.id, 10000)
        table.append(data.to_data())
        
        # グループ.
        group = self.create_dummy(DummyType.GACHA_GROUP_MASTER, table=table)
        
        # おまけ.
        item = self.create_dummy(DummyType.ITEM_MASTER)
        prize = self.create_dummy(DummyType.PRIZE_MASTER, item=item, itemnum=1)
        bonus = [prize.id]
        
        # ガチャ.
        continuity = 10
        boxdata = GachaBoxGroupData(group.id, 10000, continuity+1)
        box = [boxdata.to_data()]
        self.__gachamaster_gachapt = self.create_dummy(DummyType.GACHA_MASTER, box=box, bonus=bonus, continuity=continuity, consumetype=Defines.GachaConsumeType.GACHAPT, consumevalue=10)
        self.__gachamaster_ticket = self.create_dummy(DummyType.GACHA_MASTER, box=box, bonus=bonus, continuity=continuity, consumetype=Defines.GachaConsumeType.TRYLUCKTICKET, consumevalue=1)
        self.__gachamaster_pay = self.create_dummy(DummyType.GACHA_MASTER, box=box, bonus=bonus, continuity=continuity, consumetype=Defines.GachaConsumeType.PAYMENT, consumevalue=10)
        
        # プレイヤー.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        # 引抜ポイントとチケット.
        playergachapt = self.__player.getModel(PlayerGachaPt)
        playergachapt.gachapt = continuity * 10
        playergachapt.ticket = 1
        playergachapt.save()
        
        # カード所持上限.
        playerdeck = self.__player.getModel(PlayerDeck)
        playerdeck.cardlimitlv = continuity
        playerdeck.save()
        
        # プレイ情報.
        self.__playdata_gachapt = self.create_dummy(DummyType.GACHA_PLAY_DATA, self.__player.id, self.__gachamaster_gachapt.boxid)
        self.__playdata_ticket = self.create_dummy(DummyType.GACHA_PLAY_DATA, self.__player.id, self.__gachamaster_ticket.boxid)
        self.__playdata_pay = self.create_dummy(DummyType.GACHA_PLAY_DATA, self.__player.id, self.__gachamaster_pay.boxid)
        
        self.__gachamaster = self.__gachamaster_gachapt
        self.__playdata = self.__playdata_gachapt
        self.__continuity = continuity
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            Defines.URLQUERY_NUMBER : self.__continuity,
        }
    
    def get_urlargs(self):
        return '/%d/%s' % (self.__gachamaster.id, self.__player.req_confirmkey)
    
    def check(self):
        playerrequest = PlayerRequest.getByKey(self.__player.id)
        # プレイ情報.
        playdata = GachaPlayData.getByKey(GachaPlayData.makeID(self.__player.id, self.__gachamaster.boxid))
        playcount = GachaPlayCount.getByKey(GachaPlayCount.makeID(self.__player.id, self.__gachamaster.id))
        
        if playerrequest.req_confirmkey == self.__player.req_confirmkey or playerrequest.req_alreadykey != self.__player.req_confirmkey:
            raise AppTestError(u'ガチャプレイ情報の確認キーが更新されていない')
        elif playcount.getTodayPlayCnt() < 1:
            raise AppTestError(u'ガチャプレイ回数が増えていない.%d, %d, %s' % (playcount.getTodayPlayCnt(), playcount.cnt, playcount.ptime))
        
        # BOX確認.
        box = GachaBox(self.__gachamaster, playdata)
        if box.get_rest_num() != 1:
            raise AppTestError(u'BOXのカードがうまく消費されていない.%d' % box.get_rest_num())
        
        # カードが増えているか.
        cardnum = BackendApi.get_cardnum(self.__player.id)
        if cardnum != self.__gachamaster.continuity:
            raise AppTestError(u'カード枚数がおかしい %d vs %d' % (cardnum, self.__gachamaster.continuity))
        elif cardnum != len(playdata.result['result']):
            raise AppTestError(u'ガチャの結果の長さがおかしい %d vs %d' % (cardnum, len(playdata.result['result'])))
        
        # おまけが来ているか.
        present_num = BackendApi.get_present_num(self.__player.id)
        if present_num < 1:
            raise AppTestError(u'おまけが来ていない')
        
        # ポイント消費確認.
        playergachapt = PlayerGachaPt.getByKey(self.__player.id)
        if 0 < playergachapt.gachapt:
            raise AppTestError(u'引抜ポイントを消費していない')



