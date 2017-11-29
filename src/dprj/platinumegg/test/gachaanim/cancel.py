# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.gacha import GachaBoxCardData,\
    GachaBoxGroupData
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerDeck
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.lib.platform.api.objects import PaymentData

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
        boxdata = GachaBoxGroupData(group.id, 10000, continuity)
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
        
        # 課金レコード.
        self.__payment_entry = self.create_dummy(DummyType.GACHA_PAYMENT_ENTRY, self.__player.id, self.__gachamaster.id, PaymentData.Status.START, continuity)
        
        self.__present_num = BackendApi.get_present_num(self.__player.id)
        self.__cardnum = BackendApi.get_cardnum(self.__player.id)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            'paymentId' : self.__payment_entry.id,
            Defines.URLQUERY_STATE : PaymentData.Status.CANCEL,
        }
    
    def get_urlargs(self):
        return '/%d/%s' % (self.__gachamaster.id, self.__player.req_confirmkey)
    
    def check(self):
        model_mgr = ModelRequestMgr()
        entry = BackendApi.get_gachapaymententry(model_mgr, self.__payment_entry.id)
        if entry is None:
            raise AppTestError(u'課金レコードが作成されていない')
        elif entry.state != PaymentData.Status.CANCEL:
            raise AppTestError(u'課金ステータスが異常です.status=%s' % entry.state)
