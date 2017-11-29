# -*- coding: utf-8 -*-
import random, time
import settings_sub

from django.db import models
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.models import Singleton, BaseMaster,\
    BaseMasterWithThumbnail, BaseModel
from platinumegg.app.cabaret.models.base.fields import AppDateTimeField,\
    JsonCharField, PositiveBigIntegerField, ObjectField, PositiveBigAutoField
from platinumegg.app.cabaret.models.Player import BasePerPlayerBase,\
    BasePerPlayerBaseWithMasterID
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.util.apprandom import AppRandom
from defines import Defines
from platinumegg.app.cabaret.models.Battle import BattleRankMaster
import datetime
from platinumegg.app.cabaret.models.base.util import get_pointprizes,\
    dict_to_choices
import settings

class CurrentBattleEventConfig(Singleton):
    """開催中または開催予定のバトルイベント.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    mid = models.PositiveIntegerField(default=0, verbose_name=u'イベントのマスターID')
    starttime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'開始時間')
    endtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'終了時間')
    prize_flag = models.PositiveIntegerField(default=0, verbose_name=u'ランキング報酬配布フラグ')
    is_emergency = models.BooleanField(default=False, verbose_name=u'緊急事態フラグ')
    daily_prize_flag = models.PositiveIntegerField(default=0, verbose_name=u'日別ランキング報酬配布フラグ')
    daily_prize_date = models.DateField(default=datetime.date.today, verbose_name=u'日別ランキング報酬配布日時')
    epilogue_endtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'エピローグ終了時間')
    rankschedule = JsonCharField(default=list, verbose_name=u'途中追加されるランクのスケジュール')
    beginer_prize_flag = models.PositiveIntegerField(default=0, verbose_name=u'新店舗ランキング報酬配布フラグ')
    ticket_endtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'ticket終了時間')
    
    def isFirstDay(self, now=None):
        """イベント初日か.
        """
        now = now or OSAUtil.get_now()
        basetime = DateTimeUtil.toLoginTime(now)
        return basetime <= self.starttime
    
    def getDailyPrizeFlag(self, today):
        if today == self.daily_prize_date:
            return self.daily_prize_flag
        else:
            return 0
    
    def getRankMax(self, now=None):
        """現在の最大ランク.
        無制限の場合はNone.
        """
        now = now or OSAUtil.get_now()
        rank_max = None
        self.rankschedule.sort(key=lambda x:x['time'])
        for data in self.rankschedule:
            if data['time'] <= now:
                continue
            rank_max = data['rank'] - 1
            break
        return rank_max
    
    def getNewbieRankOpenTime(self, now=None):
        """現在の最大ランクが公開された時間.
        無制限の場合はNone.
        """
        now = now or OSAUtil.get_now()
        t = None
        self.rankschedule.sort(key=lambda x:x['time'])
        for data in self.rankschedule:
            if now < data['time']:
                break
            t = data['time']
        return t

class BattleEventMaster(BaseMaster):
    """バトルイベントのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'イベント名')
    subname = models.CharField(max_length=64, verbose_name=u'イベントサブタイトル', default='', blank=True)
    htmlname = models.CharField(max_length=48, verbose_name=u'HTMLディレクトリ名')
    effectname = models.CharField(max_length=48, verbose_name=u'演出ディレクトリ名')
    rankingprizes = JsonCharField(default=list, verbose_name=u'バトルPTランキング報酬')
    rankingprize_text = models.PositiveIntegerField(default=0, verbose_name=u'バトルPTランキング報酬文言')
    pointprizes = JsonCharField(default=list, verbose_name=u'名声PT達成報酬')
    pointprize_text = models.PositiveIntegerField(default=0, verbose_name=u'名声PT達成報酬文言')
    specialtype = models.PositiveSmallIntegerField(default=Defines.CharacterType.ALL, verbose_name=u'特効属性', choices=dict_to_choices(Defines.CharacterType.SKILL_TARGET_NAMES))
    specialtable = JsonCharField(default=list, verbose_name=u'特効属性テーブル', help_text=u'[[レア度,[ハメ管理度1の倍率,ハメ管理度2の倍率..]],...]')
    rankstart = models.PositiveSmallIntegerField(default=1, verbose_name=u'イベント開始時のランク')
    rankbeginer = models.PositiveSmallIntegerField(default=1, verbose_name=u'初心者のランク(2日目以降)')
    topimg = models.CharField(default='', blank=True, max_length=96, verbose_name=u'トップページ画像')
    specialcard = JsonCharField(default=list, verbose_name=u'特効キャスト')
    battleticket_rate = JsonCharField(default=list, verbose_name=u'バトルチケット効果')
    is_goukon = models.BooleanField(default=False, verbose_name=u'合コンイベントフラグ')
    bpcalctype = models.PositiveSmallIntegerField(default=Defines.BattleEventPointCalculationType.LEVEL, verbose_name=u'BP計算方法', choices=dict_to_choices(Defines.BattleEventPointCalculationType.NAMES))
    img_appeal = JsonCharField(default=list, verbose_name=u'訴求画像リスト', blank=True)
    beginer_days = models.PositiveSmallIntegerField(default=0, verbose_name=u'新店舗判定日数')
    beginer_rankingprizes = JsonCharField(default=list, verbose_name=u'新店舗ランキング報酬')
    beginer_rankingprize_text = models.PositiveIntegerField(default=0, verbose_name=u'新店舗ランキング報酬文言')
    presentnumber_default = models.PositiveSmallIntegerField(default=0, verbose_name=u'初回贈り物通し番号')
    op = models.PositiveIntegerField(default=0, verbose_name=u'オープニング演出ID')
    ed = models.PositiveIntegerField(default=0, verbose_name=u'エンディング演出ID')
    
    @property
    def codename(self):
        return self.htmlname.split('/')[-1]
    
    def get_pointprizes(self, point_min=1, point_max=None):
        return get_pointprizes(self.pointprizes, point_min, point_max)

class BattleEventRankMaster(BaseMasterWithThumbnail):
    """バトルイベントランクのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    eventid = models.PositiveIntegerField(db_index=True, verbose_name=u'バトルイベントマスターID')
    rank = models.PositiveIntegerField(verbose_name=u'ランク番号')
    bpcost = models.PositiveSmallIntegerField(default=0, verbose_name=u'消費気力')
    membernummax_auto = models.PositiveSmallIntegerField(verbose_name=u'自動割り振り時のグループの人数上限')
    membernummax_additional = models.PositiveSmallIntegerField(verbose_name=u'自動割り振り後の追加人数上限')
    loginbonus = JsonCharField(default=list, verbose_name=u'ログイン時の報酬', help_text=u'いつもの報酬IDリスト')
    loginbonus_text = models.PositiveIntegerField(default=0, verbose_name=u'ログイン時の報酬文言')
    pointtable = JsonCharField(default=list, verbose_name=u'獲得名声ポイントテーブル', help_text=u'[[\"default\", 未設定の順位の名声ポイント],[順位, 名声ポイント],[順位, 名声ポイント]...]')
    rankuptable = JsonCharField(default=list, verbose_name=u'ランクアップテーブル', help_text=u'[[順位, ランク増減],[順位, ランク増減]...]')
    battlepoint_w = models.PositiveIntegerField(verbose_name=u'勝利時の獲得バトルPT')
    battlepoint_l = models.PositiveIntegerField(verbose_name=u'敗北時の獲得バトルPT')
    battlepoint_lv = models.PositiveIntegerField(verbose_name=u'能力差での獲得バトルPTの上昇量')
    battlepointreceive = models.PositiveIntegerField(verbose_name=u'受動時の獲得バトルPT')
    winprizes = JsonCharField(default=list, verbose_name=u'勝利報酬')
    winprizes_text = models.PositiveIntegerField(default=0, verbose_name=u'勝利報酬文言')
    loseprizes = JsonCharField(default=list, verbose_name=u'敗北報酬')
    loseprizes_text = models.PositiveIntegerField(default=0, verbose_name=u'敗北報酬文言')
    rankingprizes = JsonCharField(default=list, verbose_name=u'バトルPTランキング報酬')
    rankingprize_text = models.PositiveIntegerField(default=0, verbose_name=u'バトルPTランキング報酬文言')
    group_rankingprizes = JsonCharField(default=list, verbose_name=u'グループ内ランキング報酬')
    group_rankingprize_text = models.PositiveIntegerField(default=0, verbose_name=u'グループ内ランキング報酬文言')
    fevertable = JsonCharField(default=list, verbose_name=u'フィーバー発生率テーブル', help_text=u'[[\"default\", 未設定の順位の発生確率[%]],[順位, 発生確率[%]],[順位, 発生確率[%]]...]')
    feverpointrate = models.PositiveSmallIntegerField(default=0, verbose_name=u'フィーバー時のポイント倍率')
    fevertimelimit = models.PositiveSmallIntegerField(default=0, verbose_name=u'フィーバーの制限時間[秒]')
    level_upper = models.PositiveIntegerField(default=0, verbose_name=u'グループマッチングレベル差分範囲(上限)', help_text=u'上限と下限が0の場合は全検索')
    level_lower = models.PositiveIntegerField(default=0, verbose_name=u'グループマッチングレベル差分範囲(下限)', help_text=u'上限と下限が0の場合は全検索')
    cardid = models.PositiveIntegerField(default=0, verbose_name=u'キャスト')
    battlepointprizes = JsonCharField(default=list, verbose_name=u'バトルPT達成報酬')
    battlepointprize_text = models.PositiveIntegerField(default=0, verbose_name=u'バトルPT達成報酬文言')
    battlepointrate = models.PositiveSmallIntegerField(default=100, verbose_name=u'バトルPT獲得倍率[%]')
    pointrandmin = models.PositiveSmallIntegerField(default=100, verbose_name=u'獲得バトルPT乱数下限(％)')
    pointrandmax = models.PositiveSmallIntegerField(default=100, verbose_name=u'獲得バトルPT乱数上限(％)')
    # 追加仕様の分
    base_drop = models.PositiveSmallIntegerField(default=20, verbose_name=u'ベースドロップ率')
    max_rise = models.PositiveSmallIntegerField(default=20, verbose_name=u'最大上昇値')
    rise = models.PositiveSmallIntegerField(default=1, verbose_name=u'上昇値')
    rival_rise = models.PositiveSmallIntegerField(default=20, verbose_name=u'ライバル勝利時の上昇値')
    rarity = JsonCharField(default=list, verbose_name=u'レアの抽選')
    
    @staticmethod
    def makeID(eventid, rank):
        return (eventid << 32) + rank
    
    @classmethod
    def makeInstance(cls, key):
        ins = cls()
        ins.id = key
        ins.eventid = int(key >> 32)
        ins.rank = int(key & 0xffffffff)
        return ins
    
    @property
    def membernummax(self):
        return self.membernummax_auto + self.membernummax_additional
    
    @property
    def str_battlepointrate(self):
        if self.battlepointrate % 100 == 0:
            return '%d' % int(self.battlepointrate / 100)
        else:
            return '%.1f' % (self.battlepointrate / 100.0)
    
    @staticmethod
    def select(clumnprizes, rand=None):
        """報酬を選択.
        """
        rand = rand or AppRandom()
        
        rate_total = 0
        datalist = []
        for v in clumnprizes:
            data = BattleRankMaster.PrizeData(v)
            if 0 < data.rate:
                rate_total += data.rate
                datalist.append(data)
        if len(datalist) == 0:
            return []
        
        v = rand.getIntN(rate_total)
        
        prizes = []
        for data in datalist:
            v -= data.rate
            if v < 0:
                prizes = data.prizes
                break
        return prizes
    
    def select_winprize(self, rand=None):
        """勝利報酬を選択.
        """
        return BattleEventRankMaster.select(self.winprizes, rand)
    
    def select_loseprize(self, rand=None):
        """敗北報酬を選択.
        """
        return BattleEventRankMaster.select(self.loseprizes, rand)
    
    def getRankUpValue(self, grouprank, point, rank_max):
        """ランクアップ変化量.
        """
        table = dict(self.rankuptable)
        arr = table.keys()
        arr.sort(key=lambda x:x if x != "default" else 0, reverse=True)
        v = table.get("default", 0)
        for rank in arr:
            if rank < grouprank:
                break
            v = table[rank]
        if point < 1:
            v = min(0, v)
        if rank_max is not None:
            v = min(max(1, self.rank + v), rank_max) - self.rank
        return v
    
    def getRankUpText(self, grouprank, point, rank_max):
        """ランクアップ表示テキスト.
        """
        updown = self.getRankUpValue(grouprank, point, rank_max)
        if updown == 0:
            return u'STAY'
        elif 0 < updown:
            return u'%dランクUP' % updown
        else:
            return u'%dランクDOWN' % (-updown)
    
    def getPoint(self, grouprank, battlepoint):
        if battlepoint < 1:
            return 0
        table = dict(self.pointtable)
        if table.has_key(grouprank):
            return table[grouprank]
        else:
            return table.get("default", 0)
    
    def getFeverRate(self, grouprank, is_worst=False):
        """フィーバー発生率.
        """
        if is_worst:
            table = dict(self.fevertable)
            v = table.get("worst")
            if v is not None:
                return v
        
        table = dict([tmp for tmp in self.fevertable if tmp[0] != "last"])
        arr = table.keys()
        arr.sort(key=lambda x:x if x != "default" else 0, reverse=True)
        v = table.get("default", 0)
        for rank in arr:
            if rank < grouprank:
                break
            v = table[rank]
        return v
    
    def get_battlepointprizes(self, point_min=1, point_max=None):
        return get_pointprizes(self.battlepointprizes, point_min, point_max)

class BattleEventPieceMaster(BaseMaster):
    """バトルイベント勝利時にピースをドロップする時に参照するマスターデータ
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    eventid = models.PositiveIntegerField(verbose_name=u'イベントマスターID')
    number = models.PositiveSmallIntegerField(verbose_name=u'レア度通し番号')
    name = models.CharField(max_length=64, verbose_name=u'ピースのまとまり画像フォルダ')
    item_lottery = JsonCharField(default=list,verbose_name=u'アイテムドロップ確率')
    complete_prize = models.PositiveIntegerField(verbose_name=u'コンプリート報酬')
    complete_prize_text =  models.PositiveIntegerField(verbose_name=u'コンプリート報酬文言')
    complete_prize_name = models.CharField(max_length=64,default="",verbose_name=u'コンプリート報酬の名前',help_text=u'プルダウンで表示される名前に使われます')
    complete_item_prize_text =  models.PositiveIntegerField(verbose_name=u'コンプリート報酬文言')
    complete_cnt_max = models.PositiveSmallIntegerField(verbose_name=u'コンプリートの最大周回回数')

    @classmethod
    def makeID(cls, eventid, number):
        return (eventid << 32) + number

    @classmethod
    def makeInstance(cls, key):
        ins = cls()
        ins.id = key
        ins.eventid = (key >> 32)
        ins.number = key & 0xffffffff
        return ins

class BattleEventGroupBase(BaseModel):
    """バトルイベントグループデータのベース.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = True
    
    FIXED_COLUMNS = (
        'eventid','rankid',
    )
    
    eventid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントマスターID')
    rankid = PositiveBigIntegerField(db_index=True, verbose_name=u'ランクマスターID')
    cdate = models.DateField(verbose_name=u'作成日', db_index=True)

class BattleEventGroup(BattleEventGroupBase):
    """バトルイベントグループデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    useridlist = ObjectField(default=list, verbose_name=u'参加ユーザID')
    fixed = models.BooleanField(default=False, verbose_name=u'参加募集可能フラグ')
    level_min = models.PositiveIntegerField(default=0, verbose_name=u'グループマッチングレベル範囲(上限)')
    level_max = models.PositiveIntegerField(default=0, verbose_name=u'グループマッチングレベル範囲(下限)')

class BattleEventGroupLog(BattleEventGroupBase):
    """バトルイベントグループ履歴.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    userdata = ObjectField(default=list, verbose_name=u'参加ユーザの情報(獲得ポイント,連勝数,名声ポイント,ランク変化)')

class BattleEventFlags(BasePerPlayerBase):
    """バトルイベントフラグ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントのマスターID')
    opvtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'OP演出閲覧時間')
    epvtime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'EP演出閲覧時間')
    scvtime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'中押し演出閲覧時間')

class BattleEventScore(BasePerPlayerBase):
    """プレイヤーのスコア情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントID')
    point = PositiveBigIntegerField(default=0, verbose_name=u'本日バトルポイント')
    point_total = PositiveBigIntegerField(default=0, db_index=True, verbose_name=u'総バトルポイント')
    win = models.PositiveIntegerField(default=0, verbose_name=u'連勝数')
    winmax = models.PositiveIntegerField(default=0, verbose_name=u'連勝数の最大')
    ltime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'最後にバトルポイントを加算した時間')
    result = PositiveBigIntegerField(default=0, verbose_name=u'前回の対戦結果')
    feveretime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'フィーバー終了時間')
    
    def isToday(self, now=None):
        """今日のスコアなのか判定.
        """
        now = now or OSAUtil.get_now()
        basetime = DateTimeUtil.toLoginTime(now)
        return basetime <= self.ltime
    
    def getPointToday(self, now=None):
        """本日獲得ポイントの取得.
        """
        if self.isToday(now=now):
            return self.point
        else:
            return 0
    
    def getWinToday(self, now=None):
        """本日現在連勝数の取得.
        """
        if self.isToday(now=now):
            return self.win
        else:
            return 0
    
    def getWinMaxToday(self, now=None):
        """本日最大連勝数の取得.
        """
        if self.isToday(now=now):
            return self.winmax
        else:
            return 0
    
    def addPoint(self, point, now=None):
        """バトルポイントの加算.
        """
        now = now or OSAUtil.get_now()
        self.point = self.getPointToday(now=now) + point
        self.point_total += point
        self.winmax = max(self.winmax, self.win)
        self.win = self.getWinToday(now=now)
        self.ltime = now
    
    def addPointWithBattleResult(self, point, is_win, now=None):
        """勝敗結果とともにバトルポイントの加算.
        """
        now = now or OSAUtil.get_now()
        self.point = self.getPointToday(now=now) + point
        self.point_total += point
        if is_win:
            self.win = self.getWinToday(now=now) + 1
            self.winmax = max(self.winmax, self.win)
        else:
            self.winmax = max(self.winmax, self.getWinToday(now=now))
            self.win = 0
        self.ltime = now

class BattleEventScorePerRank(BasePerPlayerBaseWithMasterID):
    """ランク別プレイヤーのスコア情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    FIXED_COLUMNS = (
        'uid','mid','eventid','rank'
    )
    
    eventid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントID')
    rank = models.PositiveSmallIntegerField(verbose_name=u'ランク')
    point = PositiveBigIntegerField(default=0, verbose_name=u'バトルポイント')
    
    @classmethod
    def makeMid(cls, eventid, rank):
        return (eventid << 6) + rank
    
    @classmethod
    def makeInstance(cls, key):
        model = cls()
        primary_key_column = cls.get_primarykey_column()
        setattr(model, primary_key_column, key)
        model.uid = (key >> 32)
        model.mid = key & 0xffffffff
        model.eventid = (model.mid >> 6)
        model.rank = model.mid & 0xff
        return model

class BattleEventRank(BasePerPlayerBase):
    """プレイヤーのランク情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    mid = models.PositiveIntegerField(verbose_name=u'イベントID')
    rank = models.PositiveIntegerField(default=1, verbose_name=u'現在のランク')
    fame = models.PositiveIntegerField(default=0, verbose_name=u'現在の名声ポイント')
    rank_next = models.PositiveIntegerField(default=1, verbose_name=u'更新予定のランク')
    fame_next = models.PositiveIntegerField(default=0, verbose_name=u'更新予定の名声ポイント')
    utime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'ランクと名声ポイントを更新した時間')
    groups = ObjectField(default=list, verbose_name=u'参加したグループのIDリスト')
    
    @property
    def groupidlist(self):
        return self.groups
    
    def addGroupId(self, groupid):
        return self.groups.append(groupid)
    
    def getCurrentGroupId(self):
        if self.groupidlist:
            return self.groupidlist[-1]
        else:
            return None
    
    def isNeedUpdate(self, config, now=None):
        """更新が必要かを判定.
        """
        if config.is_emergency:
            return False
        
        # 前回のポイント更新時間が現在の日付変更時間よりも前なら更新する.
        now = now or OSAUtil.get_now()
        basetime = DateTimeUtil.toLoginTime(now)
        return self.utime < basetime
    
    def getRank(self, config, now=None):
        """現在のランクを取得.
        """
        if self.isNeedUpdate(config, now):
            return self.rank_next
        else:
            return self.rank
    
    def getFamePoint(self, config, now=None):
        """現在の名声ポイントを取得.
        """
        if self.isNeedUpdate(config, now):
            return self.fame_next
        else:
            return self.fame

class BattleEventRevenge(BaseModel):
    """仕返しレコード.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    uid = models.PositiveIntegerField(verbose_name=u'ユーザID')
    oid = models.PositiveIntegerField(db_index=True, verbose_name=u'対戦相手')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'作成時間')

class BattleEventBattleLog(BaseModel):
    """対戦履歴.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    uid = models.PositiveIntegerField(db_index=True, verbose_name=u'ユーザID')
    data = ObjectField(default=dict, verbose_name=u'結果データ')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'作成時間')
    
    def setData(self, oid, result, point, v_power, o_power, attack, is_fever=False):
        """結果データを設定.
        """
        self.data = {
            'oid' : oid,
            'result' : result,
            'point' : point,
            'v_power' : v_power,
            'o_power' : o_power,
            'attack' : attack,
            'is_fever' : is_fever,
        }

class BattleEventBattleTime(BaseModel):
    """対戦時間.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    FIXED_COLUMNS = (
        'uid','oid'
    )
    
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    uid = models.PositiveIntegerField(db_index=True, verbose_name=u'仕掛けたユーザーのID')
    oid = models.PositiveIntegerField(db_index=True, verbose_name=u'仕掛けられたユーザーのID')
    btime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'最後に戦った時間')
    
    @classmethod
    def makeID(cls, uid, oid):
        return (uid << 32) + oid
    
    @classmethod
    def makeInstance(cls, key):
        model = cls()
        model.id = key
        model.uid = (key >> 32)
        model.oid = key & 0xffffffff
        model.btime = OSAUtil.get_datetime_min()
        return model

class BattleEventGroupRankingPrize(BasePerPlayerBase):
    """バトルイベントグループランキング報酬受取データ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    mid = models.PositiveIntegerField(verbose_name=u'イベントのマスターID')
    prizes = ObjectField(default=list, verbose_name=u'報酬リスト')
    fixed = models.BooleanField(default=False, verbose_name=u'受け取りフラグ')
    
    def add_prize(self, prizeidlist, textid):
        self.prizes = self.prizes or []
        if prizeidlist:
            self.prizes.append({
                'prizes' : prizeidlist,
                'text' : textid,
            })
    
    def clear_prizes(self):
        self.prizes = []

class BattleEventPieceBase(BaseModel):
    """バトルイベントピース抽象モデル
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = True
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    uid = models.PositiveIntegerField(db_index=True, verbose_name=u'ユーザーID')
    eventid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントマスターID')

class BattleEventPieceCollection(BattleEventPieceBase):
    """バトルイベントピースの収集テーブル
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    rarity = models.PositiveIntegerField(verbose_name=u'ピースレアリティ')
    piece_number0 = models.BooleanField(default=False, verbose_name=u'ピースナンバー0')
    piece_number1 = models.BooleanField(default=False, verbose_name=u'ピースナンバー1')    
    piece_number2 = models.BooleanField(default=False, verbose_name=u'ピースナンバー2')
    piece_number3 = models.BooleanField(default=False, verbose_name=u'ピースナンバー3')
    piece_number4 = models.BooleanField(default=False, verbose_name=u'ピースナンバー4')
    piece_number5 = models.BooleanField(default=False, verbose_name=u'ピースナンバー5')
    piece_number6 = models.BooleanField(default=False, verbose_name=u'ピースナンバー6')
    piece_number7 = models.BooleanField(default=False, verbose_name=u'ピースナンバー7')
    piece_number8 = models.BooleanField(default=False, verbose_name=u'ピースナンバー8')
    complete_cnt = models.PositiveIntegerField(default=0, verbose_name=u'コンプリートの周回回数')

    @classmethod
    def makeID(cls, uid, eventid, rarity):
        """ID の生成。getByKey とかでデータを引っぱる時などに使用。"""
        return (uid << 32) + (eventid << 16) + rarity

    @classmethod
    def makeInstance(cls, uid, eventid, rarity):
        """インスタンスを生成する。外部から直接は呼ばない。"""
        ins = cls()
        ins.id = cls.makeID(uid, eventid, rarity)
        ins.uid = uid
        ins.eventid = eventid
        ins.rarity = rarity
        return ins

    @classmethod
    def get_or_create_instance(cls, uid, eventid, rarity):
        """instance を取得、無い場合作成"""
        id = cls.makeID(uid, eventid, rarity)
        defaults = dict(uid=uid, eventid=eventid, rarity=rarity)
        ins = cls.get_or_insert(id=id, defaults=defaults)
        return ins

    @classmethod
    def check_user_data(cls, uid, eventid):
        """ユーザのデータがあるか確認"""
        fields = ['id']
        filters = dict(uid=uid, eventid=eventid)
        if cls.getValues(fields=fields, filters=filters, using=settings.DB_READONLY):
            return False
        return True

#     @classmethod
#     def make_all_rarity_and_save(cls, uid, eventid):
#         """イベント開始時に全てのレアリティを最初に作成して保存する。"""
#         [cls.get_or_create_instance(uid, eventid, x).save() for x in range(4)]

    @classmethod
    def is_drop_lottery(cls, lottery_lists):
        """名前で混乱しない用に別名関数を定義しているだけ。select_rarity_box と同じもの。"""
        return cls.select_rarity_box(lottery_lists)

    @classmethod
    def select_rarity_box(cls, lottery_lists):
        """[[BattleEventPieceMaster.number, 60], ...] という形式のデータ構造からレア度を算出する"""
        rand = cls.percentage_100()
        rarity_box = cls.lottery_box(lottery_lists)
        return rarity_box[rand]

    @classmethod
    def item_lottery(cls, item_lottery_lists):
        """
        記述形式 [{'prize': [PrizeMaster.id, ...], 'rate': percent}, ...]
        'prize': PrizeMaster.id はアイテムのマスター ID を指す。複数個の配布に対応出来る様、リストで。
        'rate': percent は 100 分率での確率。整数のみが入る。60 と設定したら、確率 60 % という意味になる。
        """
        present = cls.percentage_100()
        item_lists = [(x['prize'], x['rate']) for x in item_lottery_lists]
        item_box = cls.lottery_box(item_lists)
        return item_box[present]

    @classmethod
    def lottery_box(cls, lottery_lists):
        """抽選用 BOX を作成。"""
        array = []
        for x in lottery_lists:
            array += cls.create_lottery_box(x[0], x[1])
        return array

    @staticmethod
    def create_lottery_box(item, percent):
        """アイテム抽選用のボックスを作成。item には中身 (rarity とか piece_number) が入る。"""
        return [item] * percent

    @staticmethod
    def percentage_100():
        """1/100 で確率を計算する。"""
        random.seed(time.time())
        return random.randint(0, 99)

    def is_max_count(self, complete_max_cnt):
        """カウントが最大値になっているか? なっていたら True を返してコンプリート処理は実行させない。"""
        if complete_max_cnt <= self.complete_cnt:
            return True
        return False

    def update_piece_to_true(self, piece_number):
        """指定のピースのフラグを取得済みに変更する"""
        self.__set_piece_flg(piece_number, True)

    def reset_all_piece_flg(self):
        """全てのピースフラグをリセットする"""
        for x in self.__all_piece_number_lists():
            self.__set_piece_flg(x, False)

    def piece_or_item_drop(self):
        """ピースの取得 (確率でどのピースが貰えるかが決定する)"""
        if self.is_complete():
            return { 'is_item': True }
        piece_box = self.__piece_number_box()
        while True:
            rand = self.percentage_100()
            get_piece = self.__lottery(piece_box[rand])
            if (not get_piece is False) and (not get_piece is None):
                return { 'piece': get_piece }

    def do_complete_process(self, complete_max_cnt):
        """
        ピースをコンプリートしていたら、リセットと回数のカウントアップをする。
        設定回数分コンプリートした場合は False を返し、アイテムの配布に切り替える。
        """
        # 5 週以上はカウントアップする必要無いので (むしろカウントすると MySQL の型のサイズに引っかかるかも)
        if not self.is_max_count(complete_max_cnt):
            self.__complete_count_up()
            if self.complete_cnt < complete_max_cnt:
                self.reset_all_piece_flg()
            return True
        return False

    def is_complete(self):
        """ピースをコンプリートしているかチェック"""
        true_fields = filter(lambda x: self.__dict__[x]==True, self.__all_piece_attributes())
        return len(true_fields) == 9

    def is_complete_morethan_maxcount(self,complete_max_cnt):
        """ピースを最大周回回数までコンプリートしているかのチェック"""
        if complete_max_cnt <= self.complete_cnt:
            return True
        return False

    def __lottery(self, piece_number):
        """抽選"""
        get_piece = None
        if not self.__have_piece(piece_number):
            get_piece = self.__set_piece_flg(piece_number, True)
        return get_piece

    def __piece_number_box(self):
        """ピースの抽選用 BOX を作成。"""
        array = [[x, 11] for x in xrange(8)]
        array.append([8, 12])
        return self.lottery_box(array)

    def __have_piece(self, piece_number):
        """ピースを既に持っているか? 持っていたら True が返り、再抽選させる。"""
        return self.__dict__.get(self.__select_piece(piece_number))

    def __all_piece_attributes(self):
        """全てのピースカラム名を配列に入れる。"""
        return [self.__select_piece(x) for x in self.__all_piece_number_lists()]

    def __all_piece_number_lists(self):
        """0-9 までの配列を作る。ピースのカラム名を生成するのに使用する。"""
        return range(9)

    def __set_piece_flg(self, piece_number, flg):
        """ピース取得情報を flg (True or False) の状態にアップデートする。"""
        get_piece = self.__select_piece(piece_number)
        self.__dict__[get_piece] = flg
        return piece_number

    def __complete_count_up(self):
        """コンプリートの周回回数をカウントアップする。"""
        self.complete_cnt += 1

    def __select_piece(self, piece_number):
        """ピースのカラム名を生成。__dict__ の key で使用する。"""
        if type(piece_number) is int:
            piece_number = str(piece_number)
        return ''.join(['piece_number', piece_number])

class BattleEventContinueVictory(BattleEventPieceBase):
    """バトルイベントの連続勝利数カウントテーブル
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    count = models.PositiveSmallIntegerField(verbose_name=u'連続勝利数')

    @classmethod
    def makeID(cls, uid, eventid):
        return (uid << 32) + eventid

    @classmethod
    def makeInstance(cls, key):
        ins = cls()
        ins.id = key
        ins.uid = (key >> 32)
        ins.eventid = key & 0xffffffff
        ins.count = 0
        return ins

    @classmethod
    def get_or_create_instance(cls, uid, eventid):
        ins_id = cls.makeID(uid, eventid)
        defaults = dict(uid=uid, eventid=eventid, count=0)
        ins = cls.get_or_insert(id=ins_id, defaults=defaults)
        return ins

    def count_up(self):
        self.count += 1

    def reset_count(self):
        self.count = 0
