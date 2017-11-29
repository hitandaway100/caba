# -*- coding: utf-8 -*-
from platinumegg.lib.redis.client import Client
from platinumegg.app.cabaret.kpi.models.player import PlayerLevelDistributionAmount
from platinumegg.app.cabaret.kpi.models.tutorial import TutorialQuit
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.kpi.models.card import CardDistributionAmount,\
    RingGetNumHash
from platinumegg.app.cabaret.kpi.models.battle import BattleRankupCount,\
    BattleRankPlayCount
from platinumegg.app.cabaret.kpi.models.scout import ScoutCompleteCount
from platinumegg.app.cabaret.kpi.models.raid import DailyRaidAppearCount,\
    DailyRaidDestroyCount
from platinumegg.app.cabaret.kpi.models.raidevent import RaidEventPoint,\
    RaidEventConsumePoint, RaidEventDailyTicket, RaidEventDailyConsumeTicket,\
    RaidEventDestroyUserNum, RaidEventDestroyUserNumBig,\
    RaidEventDestroyLevelMap, RaidEventStageDistributionAmount
from platinumegg.app.cabaret.kpi.models.scoutevent import ScoutEventStageDistributionAmount,\
    ScoutEventPointSet, ScoutEventGachaPointConsumeHash,\
    ScoutEventTipConsumeHash, ScoutEventTanzakuHash
from platinumegg.app.cabaret.kpi.models.battleevent import BattleEventFame,\
    BattleEventJoin, BattleEventMemberCount, BattleEventResult,\
    BattleEventBattleCountAttack, BattleEventBattleCountAttackWin,\
    BattleEventBattleCountDefense, BattleEventBattleCountDefenseWin,\
    BattleEventDailyUserRankSet,BattleEventPieceCollect
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.kpi.models.invite import InviteCount
from platinumegg.app.cabaret.kpi.models.movie import MovieViewCount, PcMovieViewCount
from platinumegg.app.cabaret.kpi.models.item import ItemDistributionAmount
from platinumegg.app.cabaret.kpi.models.login import WeeklyLoginSet
from platinumegg.app.cabaret.kpi.models.payment import FQ5PaymentSet,\
    DailyPaymentPointSet
from platinumegg.app.cabaret.kpi.models.gacha import GachaLastStepSortSet,\
    PaymentGachaLastPlayTimeSortedSet, PaymentGachaPlayerLeaderHash
from platinumegg.app.cabaret.kpi.models.event import EventJoinDaily,\
    EventPlayDaily, EventGachaPaymentUUDaily, EventShopPaymentUUDaily,\
    EventGachaPaymentPointDaily, EventShopPaymentPointDaily


class KpiOperator:
    """KPI操作.
    """
    def __init__(self):
        self.__processes = {}
    
    def __append_process(self, using, func, *args, **kwargs):
        arr = self.__processes[using] = self.__processes.get(using) or []
        arr.append((func, args, kwargs))
    
    def __set_save(self, model):
        def func(pipe, model):
            model.save(pipe)
        self.__append_process(model.getDBName(), func, model)
    
    def __set_delete(self, model):
        def func(pipe, model):
            model.delete(pipe)
        self.__append_process(model.getDBName(), func, model)
    
    def save(self):
        if not self.__processes:
            return
        
        for dbname, arr in self.__processes.items():
            redisdb = Client.get(dbname)
            pipe = redisdb.pipeline()
            for func, args, kwargs in arr:
                func(pipe, *args, **kwargs)
            pipe.execute()
        
        self.__processes = {}
    
    #=================================================
    # プレイヤー.
    def set_save_playerlevel(self, uid, level):
        """プレイヤーのレベルを保存.
        """
        self.__set_save(PlayerLevelDistributionAmount.create(uid, level))
        return self
    
    def set_save_tutorialstate(self, uid, tutorialstate, now=None):
        """プレイヤーのチュートリアル状態を保存.
        """
        now = now or OSAUtil.get_now()
        self.__set_save(TutorialQuit.create(now, uid, tutorialstate))
        return self
    
    #=================================================
    # カード.
    def set_save_cardmasterid(self, cardid, mid):
        """カードのマスターIDを設定.
        """
        self.__set_save(CardDistributionAmount.create(cardid, mid))
        return self
    
    def set_delete_cardmasterid(self, cardid, mid):
        """カードのマスターIDを設定.
        """
        self.__set_delete(CardDistributionAmount.create(cardid, mid))
        return self
    
    def set_incr_ringnum(self, uid, mid, way, now=None):
        """指輪流通量のインクリメント.
        """
        def func(pipe):
            RingGetNumHash.incrby(uid, mid, way, now or OSAUtil.get_now(), 1, pipe)
        self.__append_process(RingGetNumHash.getDBName(), func)
        return self
    
    #=================================================
    # アイテム.
    def set_save_itemnum(self, uid, mid, rnum, vnum):
        """アイテム所持数を設定.
        """
        self.__set_save(ItemDistributionAmount.create(uid, mid, rnum, vnum))
        return self
    
    #=================================================
    # スカウト.
    def set_incrment_scoutcomplete_count(self, scout, now=None):
        """スカウトクリア数を増やす.
        """
        def func(pipe, scout, now):
            ScoutCompleteCount.incrby(now, scout, 1, pipe)
        self.__append_process(ScoutCompleteCount.getDBName(), func, scout, now or OSAUtil.get_now())
        return self
    
    #=================================================
    # バトル.
    def set_incrment_battlerankup_count(self, rank, now=None):
        """バトルのランクアップ数を増やす.
        """
        def func(pipe, rank, now):
            BattleRankupCount.incrby(now, rank, 1, pipe)
        self.__append_process(BattleRankupCount.getDBName(), func, rank, now or OSAUtil.get_now())
        return self
    
    def set_incrment_battleplay_count(self, rank, now=None):
        """バトル回数を増やす.
        """
        def func(pipe, rank, now):
            BattleRankPlayCount.incrby(now, rank, 1, pipe)
        self.__append_process(BattleRankPlayCount.getDBName(), func, rank, now or OSAUtil.get_now())
        return self
    
    #=================================================
    # レイド.
    def set_incrment_raidappear_count(self, raidid, level, now=None):
        """レイド出現回数を増やす.
        """
        def func(pipe, raidid, level, now):
            DailyRaidAppearCount.incrby(now, raidid, level, 1, pipe)
        self.__append_process(DailyRaidAppearCount.getDBName(), func, raidid, level, now or OSAUtil.get_now())
        return self
    
    def set_incrment_raiddestroy_count(self, raidid, level, now=None):
        """レイド討伐回数を増やす.
        """
        def func(pipe, raidid, level, now):
            DailyRaidDestroyCount.incrby(now, raidid, level, 1, pipe)
        self.__append_process(DailyRaidDestroyCount.getDBName(), func, raidid, level, now or OSAUtil.get_now())
        return self
    
    #=================================================
    # イベント共通.
    def __set_save_event_join(self, uid, now, is_pc):
        """日別イベント参加数.
        イベントTOPとルール説明を見たUU.
        """
        self.__set_save(EventJoinDaily.create(DateTimeUtil.toLoginTime(now or OSAUtil.get_now()), uid, is_pc))
        return self
    
    def __set_save_event_play(self, uid, now, is_pc):
        """日別イベントプレイ数.
        イベントポイントを自分で稼いだユーザ数.
        """
        self.__set_save(EventPlayDaily.create(DateTimeUtil.toLoginTime(now or OSAUtil.get_now()), uid, is_pc))
        return self
    
    #=================================================
    # レイドイベント.
    def set_save_raidevent_point(self, eventid, uid, point):
        """ユーザー毎の秘宝獲得数.
        """
        self.__set_save(RaidEventPoint.create(eventid, uid, point))
        return self
    
    def set_save_raidevent_consume_point(self, eventid, uid, point):
        """ユーザー別消費秘宝数.
        """
        self.__set_save(RaidEventConsumePoint.create(eventid, uid, point))
        return self
    
    def set_increment_raidevent_ticket(self, eventid, uid, ticket, now=None):
        """日別イベント用チケット交換数.
        """
        def func(pipe):
            RaidEventDailyTicket.incrby(now or OSAUtil.get_now(), eventid, uid, ticket, pipe)
        self.__append_process(RaidEventDailyTicket.getDBName(), func)
        return self
    
    def set_increment_raidevent_consume_ticket(self, eventid, uid, ticket, now=None):
        """日別イベントガチャ実行数.
        """
        def func(pipe):
            RaidEventDailyConsumeTicket.incrby(now or OSAUtil.get_now(), eventid, uid, ticket, pipe)
        self.__append_process(RaidEventDailyConsumeTicket.getDBName(), func)
        return self
    
    def set_save_raidevent_destroy(self, eventid, uid, destroy):
        """通常太客討伐回数別ユーザー数.
        """
        self.__set_save(RaidEventDestroyUserNum.create(eventid, uid, destroy))
        return self
    
    def set_save_raidevent_destroy_big(self, eventid, uid, destroy_big):
        """大ボス討伐回数別ユーザー数.
        """
        self.__set_save(RaidEventDestroyUserNumBig.create(eventid, uid, destroy_big))
        return self
    
    def set_increment_raidevent_destroy_level(self, eventid, raidid, level, destroy=1):
        """超太客Lv別討伐回数.
        """
        def func(pipe):
            RaidEventDestroyLevelMap.incrby(eventid, raidid, level, destroy, pipe)
        self.__append_process(RaidEventDestroyLevelMap.getDBName(), func)
        return self
    
    def set_save_raidevent_join(self, uid, now, is_pc):
        """日別レイドイベント参加数.
        イベントTOPとルール説明を見たUU.
        """
        return self.__set_save_event_join(uid, now, is_pc)
    
    def set_save_raidevent_play(self, uid, now, is_pc):
        """日別レイドイベントプレイ数.
        イベント超太客を接客したユーザ数.
        """
        return self.__set_save_event_play(uid, now, is_pc)
    
    def set_save_raidevent_stagenumber(self, eventid, uid, stagenumber):
        """到達ステージの設定.
        """
        self.__set_save(RaidEventStageDistributionAmount.create(eventid, uid, stagenumber))
        return self
    
    #=================================================
    # スカウトイベント.
    def set_save_scoutevent_stagenumber(self, eventid, uid, stagenumber):
        """到達ステージの設定.
        """
        self.__set_save(ScoutEventStageDistributionAmount.create(eventid, uid, stagenumber))
        return self
    
    def set_save_scoutevent_point(self, eventid, uid, point):
        """イベントポイント.
        """
        self.__set_save(ScoutEventPointSet.create(eventid, uid, point))
        return self
    
    def set_save_scoutevent_join(self, uid, now, is_pc):
        """日別スカウトイベント参加数.
        イベントTOPとルール説明を見たUU.
        """
        return self.__set_save_event_join(uid, now, is_pc)
    
    def set_save_scoutevent_play(self, uid, now, is_pc):
        """日別スカウトイベントプレイ数.
        イベントスカウトを実行したユーザ数.
        """
        return self.__set_save_event_play(uid, now, is_pc)
    
    def set_increment_scoutevent_consume_gachapoint(self, eventid, uid, point):
        """スカウトイベントガチャの消費ポイント.
        """
        def func(pipe):
            ScoutEventGachaPointConsumeHash.incrby(eventid, uid, point)
        self.__append_process(ScoutEventGachaPointConsumeHash.getDBName(), func)
        return self
    
    def set_increment_scoutevent_consume_tip(self, uid, cast_number, num):
        """スカウトイベントチップの消費量.
        """
        def func(pipe):
            ScoutEventTipConsumeHash.incrby(uid, cast_number, num)
        self.__append_process(ScoutEventTipConsumeHash.getDBName(), func)
        return self
    
    def set_increment_scoutevent_get_tanzaku(self, uid, tanzaku_number, num):
        """スカウトイベント短冊の獲得数.
        """
        def func(pipe):
            ScoutEventTanzakuHash.incrby(uid, tanzaku_number, num)
        self.__append_process(ScoutEventTanzakuHash.getDBName(), func)
        return self
    
    #=================================================
    # バトルイベント.
    def set_increment_battleevent_member_count(self, rank, cnt=1, now=None):
        """バトルイベントランク別所属人数.
        """
        logintime = DateTimeUtil.toLoginTime(now or OSAUtil.get_now())
        def func(pipe):
            BattleEventMemberCount.incrby(logintime, rank, cnt, pipe)
        self.__append_process(BattleEventMemberCount.getDBName(), func)
        return self
    
    def set_save_battleevent_battle_join(self, uid, rank, now=None):
        """イベントバトルに参加.
        """
        logintime = DateTimeUtil.toLoginTime(now or OSAUtil.get_now())
        self.__set_save(BattleEventJoin.create(logintime, uid, rank))
        return self
    
    def set_save_battleevent_result(self, uid, rank, grouprank, point, now=None):
        """イベント結果.
        """
        logintime = DateTimeUtil.toLoginTime(now or OSAUtil.get_now())
        self.__set_save(BattleEventResult.create(logintime, uid, rank, grouprank, point))
        return self
    
    def set_save_battleevent_famepoint(self, eventid, uid, point):
        """名声ポイント.
        """
        self.__set_save(BattleEventFame.create(eventid, uid, point))
        return self
    
    def set_increment_battleevent_battlecount(self, uid, rank, cnt_add, is_attack, is_win, now=None):
        """バトル回数を加算.
        """
        logintime = DateTimeUtil.toLoginTime(now or OSAUtil.get_now())
        
        if is_attack:
            battlecount_cls, battlewincount_cls = (BattleEventBattleCountAttack, BattleEventBattleCountAttackWin)
        else:
            battlecount_cls, battlewincount_cls = (BattleEventBattleCountDefense, BattleEventBattleCountDefenseWin)
        
        def func_battlecount(pipe):
            battlecount_cls.incrby(logintime, uid, cnt_add, pipe)
        self.__append_process(battlecount_cls.getDBName(), func_battlecount)
        
        if is_win:
            def func_wincount(pipe):
                battlewincount_cls.incrby(logintime, uid, cnt_add, pipe)
            self.__append_process(battlewincount_cls.getDBName(), func_wincount)
        
        self.__set_save(BattleEventDailyUserRankSet.create(logintime, uid, rank))
        
        return self
    
    def set_save_battleevent_join(self, uid, now, is_pc):
        """日別バトルイベント参加数.
        イベントTOPとルール説明を見たUU.
        """
        return self.__set_save_event_join(uid, now, is_pc)
    
    def set_save_battleevent_play(self, uid, now, is_pc):
        """日別バトルイベントプレイ数.
        イベントバトルを仕掛けたユーザ数.
        """
        return self.__set_save_event_play(uid, now, is_pc)
    
    def set_save_battleevent_piece_collect(self, rare):
        """日別バトルイベントのピース獲得数.
        """
        logintime = DateTimeUtil.toLoginTime(OSAUtil.get_now())
        self.__set_save(BattleEventPieceCollect.create(logintime, rare))
        return self
    #=================================================
    # 招待.
    def set_increment_invite_count(self, cnt=1, now=None):
        """招待回数.
        """
        def func(pipe):
            InviteCount.incrby(now or OSAUtil.get_now(), InviteCount.TARGET.SEND, cnt, pipe)
        self.__append_process(InviteCount.getDBName(), func)
        return self
    
    def set_increment_invite_success_count(self, cnt=1, now=None):
        """招待成功数.
        """
        def func(pipe):
            InviteCount.incrby(now or OSAUtil.get_now(), InviteCount.TARGET.SUCCESS, cnt, pipe)
        self.__append_process(InviteCount.getDBName(), func)
        return self
    
    def set_increment_invite_tutoend_count(self, cnt=1, now=None):
        """招待成功してチュートリアルも終わった数.
        """
        def func(pipe):
            InviteCount.incrby(now or OSAUtil.get_now(), InviteCount.TARGET.TUTOEND, cnt, pipe)
        self.__append_process(InviteCount.getDBName(), func)
        return self
    
    #=================================================
    # 動画再生.
    def set_incrment_movieview_count(self, mid, now=None):
        """動画再生回数を増やす.
        """
        def func(pipe, scout, now):
            MovieViewCount.incrby(now, mid, 1, pipe)
        self.__append_process(MovieViewCount.getDBName(), func, mid, now or OSAUtil.get_now())
        return self
    
    def set_incrment_pcmovieview_count(self, mid, now=None):
        """動画(PC)再生回数を増やす.
        """
        def func(pipe, scout, now):
            PcMovieViewCount.incrby(now, mid, 1, pipe)
        self.__append_process(PcMovieViewCount.getDBName(), func, mid, now or OSAUtil.get_now())
        return self
    
    #=================================================
    # 過去1週間のログイン.
    def set_save_weeklylogin(self, uid, is_pc, now=None):
        """過去1週間のログインUU算出のために当日ログインを記録.
        """
        logintime = DateTimeUtil.toLoginTime(now or OSAUtil.get_now())
        self.__set_save(WeeklyLoginSet.create(logintime, uid, is_pc))
        return self
    
    #=================================================
    # 課金FQ5ユーザー.
    def set_save_payment_fq5(self, uid, mid, now=None):
        """連続ログインが5以上の課金ユーザーを記録.
        """
        logintime = DateTimeUtil.toLoginTime(now or OSAUtil.get_now())
        self.__set_save(FQ5PaymentSet.create(logintime, uid, mid))
        return self
    
    #=================================================
    # ガチャ.
    def set_save_gacha_laststep(self, uid, mid, step, now=None):
        """連続ログインが5以上の課金ユーザーを記録.
        """
        logintime = DateTimeUtil.toLoginTime(now or OSAUtil.get_now())
        self.__set_save(GachaLastStepSortSet.create(logintime, uid, mid, step))
        return self
    
    def set_save_gacha_play(self, uid, is_pc, point, now=None):
        """日別イベントガチャプレイ数と消費ポイント.
        """
        logintime = DateTimeUtil.toLoginTime(now or OSAUtil.get_now())
        # プレイ数.
        self.__set_save(EventGachaPaymentUUDaily.create(logintime, uid, is_pc))
        # 消費ポイント.
        def func(pipe, uid, date, point, is_pc):
            EventGachaPaymentPointDaily.incrby(date, point, is_pc, pipe)
            DailyPaymentPointSet.incrby(uid, date, point, pipe)
        self.__append_process(EventGachaPaymentPointDaily.getDBName(), func, uid, logintime, point, is_pc)
        return self
    
    def set_save_paymentgacha_playerdata(self, uid, gachaid, leadercard_mid, now=None):
        """期間限定課金ガチャプレイ時のデータ.
        """
        # リーダーカード情報.
        self.__set_save(PaymentGachaPlayerLeaderHash.create(uid, gachaid, leadercard_mid, now))
        # ガチャを引いた時間.
        self.__set_save(PaymentGachaLastPlayTimeSortedSet.create(uid, now))
        return self
    
    #=================================================
    # ショップ.
    def set_save_shop_buy(self, uid, is_pc, point, now=None):
        """日別イベントショップ購入数と消費ポイント.
        """
        logintime = DateTimeUtil.toLoginTime(now or OSAUtil.get_now())
        # 購入数.
        self.__set_save(EventShopPaymentUUDaily.create(logintime, uid, is_pc))
        # 消費ポイント.
        def func(pipe, uid, date, point, is_pc):
            EventShopPaymentPointDaily.incrby(date, point, is_pc, pipe)
            DailyPaymentPointSet.incrby(uid, date, point, pipe)
        self.__append_process(EventShopPaymentPointDaily.getDBName(), func, uid, logintime, point, is_pc)
        return self
