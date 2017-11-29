# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.gacha import GachaBoxCardData,\
    GachaBoxGroupData, GachaBox
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerDeck,\
    PlayerRequest
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.lib.platform.api.objects import PaymentData
from platinumegg.app.cabaret.models.Gacha import GachaPlayData, GachaPlayCount,\
    RankingGachaScore, RankingGachaWholeData, RankingGachaWholePrizeQueue

class ApiTest(ApiTestBase):
    """引抜実行(ランキング).
    """
    RANKING_POINT = 1000
    
    def setUp(self):
        
        # カード.
        table = []
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        data = GachaBoxCardData(cardmaster.id, 10000, ApiTest.RANKING_POINT)
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
        self.__gachamaster_pay = self.create_dummy(DummyType.GACHA_MASTER, box=box, bonus=bonus, continuity=continuity, consumetype=Defines.GachaConsumeType.RANKING, consumevalue=10)
        
        # ランキング.
        rankingprizes = [
            (1, bonus),
        ]
        wholeprizes = {
            'normal' : [(ApiTest.RANKING_POINT, bonus),]
        }
        self.__rankingmaster = self.create_dummy(DummyType.RANKING_GACHA_MASTER, self.__gachamaster_pay.boxid, singleprizes=rankingprizes, totalprizes=rankingprizes, wholeprizes=wholeprizes, wholewinprizes=bonus)
        self.__queue_cnt = RankingGachaWholePrizeQueue.count()
        
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
        
        self.__gachamaster = self.__gachamaster_pay
        self.__playdata = self.__playdata_pay
        
        # 課金レコード.
        self.__payment_entry = self.create_dummy(DummyType.GACHA_PAYMENT_ENTRY, self.__player.id, self.__gachamaster.id, PaymentData.Status.START, continuity)
        
        self.__present_num = BackendApi.get_present_num(self.__player.id)
        self.__cardnum = BackendApi.get_cardnum(self.__player.id)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
            'paymentId' : self.__payment_entry.id,
            Defines.URLQUERY_STATE : PaymentData.Status.COMPLETED,
        }
    
    def get_urlargs(self):
        return '/%d/%s' % (self.__gachamaster.id, self.__player.req_confirmkey)
    
    def check(self):
        model_mgr = ModelRequestMgr()
        # 課金情報.
        entry = BackendApi.get_gachapaymententry(model_mgr, self.__payment_entry.id)
        if entry is None:
            raise AppTestError(u'課金レコードが作成されていない')
        elif entry.state != PaymentData.Status.COMPLETED:
            raise AppTestError(u'課金ステータスが異常です.status=%s' % entry.state)
        
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
        tmp_card_num = min(self.__cardnum + entry.continuity, self.__player.cardlimit)
        if tmp_card_num != cardnum:
            raise AppTestError(u'カード枚数がおかしい %d vs %d' % (self.__cardnum, cardnum))
        
        # おまけが来ているか.
        present_num = BackendApi.get_present_num(self.__player.id)
        if (self.__present_num + self.__gachamaster.continuity) == present_num:
            raise AppTestError(u'おまけが来ていない')
        
        # ランキングスコア情報.
        scoredata = RankingGachaScore.getByKey(RankingGachaScore.makeID(self.__player.id, self.__rankingmaster.id))
        if scoredata is None:
            raise AppTestError(u'ランキングのスコア情報が作成されていない')
        
        point = self.__gachamaster.continuity * ApiTest.RANKING_POINT
        # 累計Pt.
        if scoredata.total != point:
            raise AppTestError(u'累計Ptが正しくない.%d vs %d' % (scoredata.total, point))
        
        # 単発Pt.
        if scoredata.single != point:
            raise AppTestError(u'単発Ptが正しくない.%d vs %d' % (scoredata.single, point))
        
        # 総計Pt.
        if scoredata.firstpoint != point:
            raise AppTestError(u'初回総計Ptが正しくない.%d vs %d' % (scoredata.firstpoint, point))
        
        wholedata = RankingGachaWholeData.getByKey(self.__rankingmaster.id)
        if wholedata is None:
            raise AppTestError(u'総計Ptが保存されていない')
        elif wholedata.point != point:
            raise AppTestError(u'総計Ptが正しくない.%d vs %d' % (wholedata.point, point))
        
        # 総計Pt達成報酬用のキュー.
        queue_cnt = RankingGachaWholePrizeQueue.count()
        if (self.__queue_cnt + 1) != queue_cnt:
            raise AppTestError(u'総計Pt達成報酬のキューが正しく積まれていない.%d vs %d' % (self.__queue_cnt + 1, queue_cnt))
        
