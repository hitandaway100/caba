# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from collections import namedtuple
from platinumegg.app.cabaret.util.api import BackendApi
import datetime
from random import randint
import math
from platinumegg.app.cabaret.util.card import CardSet

class CabaclubTest(ApiTestBase):
    """キャバクラシステムの機能面の動作確認.
    """
    CabaClubDummy = namedtuple('CabaClubDummy', 'now,section_starttime,cardlist,master,stores,events,storeplayerdata,score,score_weekly,score_weekly_prev')
    
    def setUpCabaclub(self, player, now=None):
        now = now or OSAUtil.get_now()
        etime = BackendApi.to_cabaretclub_section_starttime(now)
        
        uid = player.id
        # カード.
        cardlist = []
        for _ in xrange(5):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER, cost=1)
            cardmaster = BackendApi.get_cardmasters([cardmaster.id]).get(cardmaster.id)
            cardlist.append(CardSet(self.create_dummy(DummyType.CARD, player, cardmaster), cardmaster))
        # マスターデータを用意.
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100)
        # キャバクラシステム.
        cabaclubmaster = self.create_dummy(DummyType.CABA_CLUB_MASTER, customer_prizes=[[prize.id, 10000]], customer_prize_interval=100)
        # 店舗とイベント.
        stores = {}
        events = {}
        storeplayerdata = {}
        for ua_type in (Defines.CabaClubEventUAType.LIVEN_UP, Defines.CabaClubEventUAType.TAKE_MEASURES):
            # イベント.
            events[ua_type] = self.create_dummy(DummyType.CABA_CLUB_EVENT_MASTER, seconds=Defines.CABARETCLUB_STORE_EVENT_INTERVAL, customer_up=150, proceeds_up=200, ua_type=ua_type, ua_value=40, ua_cost=100)
            # 店舗.
            stores[ua_type] = self.create_dummy(DummyType.CABA_CLUB_STORE_MASTER, days=7, cost=100, customer_interval=600, customer_max=99999999, cast_num_max=5, scoutman_num_max=10, scoutman_add_max=10, events=[[events[ua_type].id, 10000]])
            # 店舗情報.
            storeplayerdata[ua_type] = self.create_dummy(DummyType.CABA_CLUB_STORE_PLAYER_DATA, uid, stores[ua_type].id, ltime=now+datetime.timedelta(days=7), etime=now, utime=now)
        # 特別なマネー.
        scoredata = self.create_dummy(DummyType.CABA_CLUB_SCORE_PLAYER_DATA, uid, money=200)
        # 週間スコア情報.
        scoredata_weekly = self.create_dummy(DummyType.CABA_CLUB_SCORE_PLAYER_DATA_WEEKLY, uid, etime=etime)
        # 前の週の週間スコア情報.
        scoredata_weekly_prev = self.create_dummy(DummyType.CABA_CLUB_SCORE_PLAYER_DATA_WEEKLY, uid, etime=etime - datetime.timedelta(days=7), view_result=True)
        return self.CabaClubDummy(now, etime, cardlist, cabaclubmaster, stores, events, storeplayerdata, scoredata, scoredata_weekly, scoredata_weekly_prev)
    
    def calcCustomerAndProceeds(self, cabaclubmaster, cabaclubstoremaster, test_cnt, scoutman_add, cardlist, eventbonus_customer_up, eventbonus_proceeds_up):
        customer, proceeds = 0, 0
        if test_cnt < 1:
            return customer, proceeds
        scoutman_num = scoutman_add + cabaclubstoremaster.scoutman_num_max
        if scoutman_num < 1:
            return customer, proceeds
        # カード取得.
        cast_num = len(cardlist)
        if cast_num < 1:
            return customer, proceeds
        # レアリティ補正.
        cr_correction = cabaclubmaster.cr_correction if cabaclubmaster else dict()
        # 属性補正.
        ctype_customer_correction = cabaclubmaster.ctype_customer_correction if cabaclubmaster else dict()
        ctype_proceeds_correction = cabaclubmaster.ctype_proceeds_correction if cabaclubmaster else dict()
        # いろいろな補正値の集計.デッキ設定でやりたいけどマスターデータを変えられたら困るからここで.
        cost_total = 0
        cr_correction_total = 0
        cabaclub_customer_up_total = 0
        cabaclub_proceeds_up_total = 0
        for card in cardlist:
            master = card.master
            cost_total += master.cost
            cr_correction_total += cr_correction.get(str(master.rare), 100)
            cabaclub_customer_up_total += ctype_customer_correction.get(str(master.ctype), 100)
            cabaclub_proceeds_up_total += ctype_proceeds_correction.get(str(master.ctype), 100)
        # 集客数の計算.
        # (スカウトマン数)*(設定されているキャスト属性集客補正の合計値/設定されているキャスト数)*(キャストレリティ補正)*(乱数値0.8～1.2)*(集客数補正、イベント起きてない場合は1).
        # 忘れそうなのでメモ.eventbonusdata['costomer_up']は補正値の合計ですよ.eventbonusdata['costomer_up'] / test_cntで補正値の平均ですよ.
        customer = scoutman_num * cabaclub_customer_up_total * cr_correction_total * randint(cabaclubstoremaster.customer_rand_min, cabaclubstoremaster.customer_rand_max) * eventbonus_customer_up / (100000000.0 * cast_num)
        # 集客数の上限.
        customer = min(math.ceil(customer), cabaclubstoremaster.customer_max * test_cnt)
        # 売上の計算.
        # (集客人数)*(設定されているキャスト属性売上補正の合計値/設定されているキャスト数)*(設定されているキャストの平均コスト)*(売上数補正、イベントが起きていない場合は1)*(乱数値0.8～1.2)
        proceeds = customer * cabaclub_proceeds_up_total * cost_total * eventbonus_proceeds_up * randint(cabaclubstoremaster.proceeds_rand_min, cabaclubstoremaster.proceeds_rand_max) / (1000000.0 * test_cnt * cast_num * cast_num)
        proceeds = math.ceil(proceeds)
        return int(customer), int(proceeds)
