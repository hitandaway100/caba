# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster,\
    Singleton, BaseMasterWithName, BaseModel
from platinumegg.app.cabaret.models.base.fields import ObjectField,\
    JsonCharField, AppDateTimeField, PositiveBigIntegerField
from platinumegg.app.cabaret.models.Player import BasePerPlayerBase,\
    BasePerPlayerBaseWithMasterID
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.models.base.util import get_pointprizes
from platinumegg.app.cabaret.models.EventScout import EventScoutStageMaster,\
    EventScoutPlayData
import datetime

class ScoutEventMaster(BaseMaster):
    """スカウトイベントのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'イベント名')
    subname = models.CharField(max_length=64, verbose_name=u'イベントサブタイトル', blank=True, default='')
    htmlname = models.CharField(max_length=48, verbose_name=u'HTMLディレクトリ名')
    effectname = models.CharField(max_length=48, verbose_name=u'演出ディレクトリ名')
    rankingprizes = JsonCharField(default=list, verbose_name=u'ランキング報酬')
    rankingprize_text = models.PositiveIntegerField(default=0, verbose_name=u'ランキング報酬文言')
    pointprizes = JsonCharField(default=list, verbose_name=u'ポイント達成報酬')
    pointprize_text = models.PositiveIntegerField(default=0, verbose_name=u'ポイント達成報酬文言')
    specialcard = JsonCharField(default=list, verbose_name=u'特効カード')
    fevertime = models.PositiveIntegerField(default=0, verbose_name=u'フィーバー時間（秒）')
    gumtradeitem = models.PositiveSmallIntegerField(default=0, verbose_name=u'スカウトガム交換アイテム', choices=[(0,u'交換なし')]+Defines.ItemEffect.NAMES.items())
    topimg = models.CharField(default='', blank=True, max_length=96, verbose_name=u'トップページ画像')
    movie_op = models.PositiveIntegerField(default=0, verbose_name=u'オープニング後に開放される動画')
    img_appeal = JsonCharField(default=list, verbose_name=u'訴求画像リスト', blank=True)
    img_produce = models.TextField(verbose_name=u'プロデュースイベント画像', blank=True)
    beginer_days = models.PositiveSmallIntegerField(default=0, verbose_name=u'新店舗判定日数')
    beginer_rankingprizes = JsonCharField(default=list, verbose_name=u'新店舗ランキング報酬')
    beginer_rankingprize_text = models.PositiveIntegerField(default=0, verbose_name=u'新店舗ランキング報酬文言')
    is_produce = models.BooleanField(default=False, verbose_name=u'プロデュースイベントフラグ')
    gachaptname = models.CharField(max_length=48, default=u'カカオ', blank=True, verbose_name=u'専用ガチャポイント名')
    gachaptimg = models.CharField(max_length=128, default=u'item/scevent/common/event_item_choco_02_s.png', blank=True, verbose_name=u'専用ガチャポイント画像')
    op = models.PositiveIntegerField(default=0, verbose_name=u'オープニング演出ID')
    ed = models.PositiveIntegerField(default=0, verbose_name=u'エンディング演出ID')
    
    # 逢引ラブタイム機能.
    lovetime_star = models.PositiveSmallIntegerField(default=0, verbose_name=u'逢引ラブタイムでの星の必要数')
    lovetime_timelimit = models.PositiveSmallIntegerField(default=0, verbose_name=u'逢引ラブタイム制限時間(sec)')
    lovetime_tanzakuup = models.PositiveSmallIntegerField(default=0, verbose_name=u'逢引ラブタイムでの短冊の増加量(％)')
    tanzaku_name = models.CharField(max_length=48, default=u'短冊', blank=True, verbose_name=u'短冊の総称')
    lovetime_starname = models.CharField(max_length=48, default=u'星', blank=True, verbose_name=u'星の名前')
    lovetime_starimgon = models.CharField(max_length=96, default=u'common/scev_rose_m.png', blank=True, verbose_name=u'星の取得画像')
    lovetime_starimgoff = models.CharField(max_length=96, default=u'common/scev_empty_rose.png', blank=True, verbose_name=u'星の未取得画像')
    lovetime_pointname = models.CharField(max_length=48, default=u'チップ', blank=True, verbose_name=u'チップの名前')
    
    @property
    def codename(self):
        return self.htmlname.split('/')[-1]
    
    @property
    def gachaname(self):
        """カラム追加するかも.
        """
        arr = self.htmlname.split('/')
        return arr[-1] if arr[-1] else arr[-2]
    
    def get_pointprizes(self, point_min=1, point_max=None):
        pointprizes = self.pointprizes
        if isinstance(pointprizes, list):
            return dict(pointprizes)
        elif not isinstance(pointprizes, dict):
            return {}
        
        table = dict(pointprizes.get('normal') or [])
        repeat = pointprizes.get('repeat') or []
        
        for data in repeat:
            prize = data.get('prize')
            if not prize:
                continue
            
            d_min = max(1, data.get('min', 1))
            if point_max is None:
                d_max = d_min
            else:
                d_max = min(data.get('max', point_max), point_max)
            interval = max(1, data.get('interval', 1))
            
            d = d_min
            while d <= d_max:
                if point_min <= d:
                    arr = table[d] = table.get(d) or []
                    arr.extend(prize)
                d += interval
        return table

class CurrentScoutEventConfig(Singleton):
    """開催中または開催予定のスカウトイベント.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    mid = models.PositiveIntegerField(default=0, verbose_name=u'イベントのマスターID')
    starttime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'開始時間')
    endtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'終了時間')
    prize_flag = models.PositiveIntegerField(default=0, verbose_name=u'ランキング報酬配布フラグ')
    epilogue_endtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'エピローグ終了時間')
    stageschedule = JsonCharField(default=list, verbose_name=u'途中追加されるステージのスケジュール')
    present_endtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'ハート投入終了時間')
    beginer_prize_flag = models.PositiveIntegerField(default=0, verbose_name=u'新店舗ランキング報酬配布フラグ')
    tip_prize_flag = models.PositiveIntegerField(default=0, verbose_name=u'チップ業績報酬配布フラグ')
    
    def get_stage_max(self, now=None):
        """現在の最大ステージ数.
        無制限の場合はNone.
        """
        now = now or OSAUtil.get_now()
        stage_max = None
        self.stageschedule.sort(key=lambda x:x['time'])
        for data in self.stageschedule:
            if data['time'] <= now:
                continue
            stage_max = data['stage'] - 1
            break
        return stage_max
    
    def reset_prize_flags(self):
        """報酬配布フラグをリセット.
        """
        self.prize_flag = 0
        self.beginer_prize_flag = 0
        self.tip_prize_flag = 0

class ScoutEventStageMaster(EventScoutStageMaster):
    """スカウトイベントのステージマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    thumbfever = models.CharField(max_length=128, verbose_name=u'フィーバー時演出背景')
    
    eventpointmin = models.PositiveIntegerField(default=0, verbose_name=u'獲得イベントポイント最小値')
    eventpointmax = models.PositiveIntegerField(default=0, verbose_name=u'獲得イベントポイント最大値')
    
    bustup = JsonCharField(default=list, verbose_name=u'バストアップ画像')
    bustuprate_0 = models.PositiveIntegerField(default=0, verbose_name=u'バストアップ画像がだれも出ない確率')
    bustuprate_1 = models.PositiveIntegerField(default=0, verbose_name=u'バストアップ画像が1人出る確率')
    bustuprate_2 = models.PositiveIntegerField(default=0, verbose_name=u'バストアップ画像が2人出る確率')
    
    movie = models.PositiveIntegerField(default=0, verbose_name=u'クリア時に開放される動画')
    
    eventrate_gachapt = models.PositiveSmallIntegerField(default=0, verbose_name=u'専用ガチャPTのドロップ発生率')
    gachaptmin = models.PositiveIntegerField(default=0, verbose_name=u'専用ガチャPT獲得の下限')
    gachaptmax = models.PositiveIntegerField(default=0, verbose_name=u'専用ガチャPT獲得の上限')
    
    eventrate_lt_star = models.PositiveSmallIntegerField(default=0, verbose_name=u'逢引ラブタイム機能での星のドロップ発生率')
    lovetime_star_min = models.PositiveSmallIntegerField(default=0, verbose_name=u'逢引ラブタイムでの星のドロップ数の最小')
    lovetime_star_max = models.PositiveSmallIntegerField(default=0, verbose_name=u'逢引ラブタイムでの星のドロップ数の最大')

class ScoutEventPresentPrizeMaster(BaseMasterWithName):
    """スカウトイベントのハートプレゼント報酬マスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    eventid = models.PositiveIntegerField(db_index=True, verbose_name=u'スカウトイベントマスターID')
    number = models.PositiveIntegerField(db_index=True, verbose_name=u'通し番号(これでソート)')
    mgrname = models.CharField(max_length=64, verbose_name=u'管理用の名前')
    prizes  = JsonCharField(default=list, verbose_name=u'報酬テーブル')
    prize_text = models.PositiveIntegerField(default=0, verbose_name=u'報酬文言')
    
    @staticmethod
    def makeID(eventid, number):
        return (eventid << 32) + number
    
    def get_pointprizes(self, point_min=1, point_max=None):
        return get_pointprizes(self.prizes, point_min, point_max)

class ScoutEventPlayData(EventScoutPlayData):
    """スカウトイベントの進行情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    feveretime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'フィーバー終了時間')
    star = models.PositiveSmallIntegerField(default=0, verbose_name=u'星の所持数')
    lovetime_etime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'逢引ラブタイムの終了時間')
    
    def setResult(self, result, eventlist, point=0, flag_fever_start=False, flag_earlybonus=False, gachapoint=0, is_lovetime_start=False):
        self._setResult(result, eventlist, flag_earlybonus)
        self.result.update({
            'point' : point,
            'feverstart' : flag_fever_start,
            'gachapoint' : gachapoint,
            'lovetime_start' : is_lovetime_start,
        })
    
    def is_lovetime(self, now=None):
        now = now or OSAUtil.get_now()
        return now < self.lovetime_etime
    
    def set_lovetime(self, now, sec):
        self.star = 0
        self.lovetime_etime = now + datetime.timedelta(seconds=sec)

class ScoutEventPlayStageData(BasePerPlayerBaseWithMasterID):
    """スカウトイベントのプレイ情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'クリア時間')
    clevel = models.PositiveIntegerField(default=0, verbose_name=u'クリア時のレベル')
    dropitems = ObjectField(default=list, verbose_name=u'獲得したカード・トロフィー')
    
    @staticmethod
    def makeDropItemName(itype, mid):
        return (itype << 32) + mid
    
    def addDropItem(self, itype, mid):
        """ドロップアイテムを追加.
        """
        self.dropitems.append(ScoutEventPlayData.makeDropItemName(itype, mid))
        self.dropitems = list(set(self.dropitems))
    
    def idDropped(self, itype, mid):
        """ドロップしたことあるか.
        """
        return self.dropitems and ScoutEventPlayData.makeDropItemName(itype, mid) in self.dropitems

class ScoutEventScore(BasePerPlayerBaseWithMasterID):
    """スカウトイベントランキング用スコア.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    point = PositiveBigIntegerField(default=0, verbose_name=u'所持ポイント')
    point_total = PositiveBigIntegerField(default=0, verbose_name=u'累計ポイント')
    point_gacha = PositiveBigIntegerField(default=0, verbose_name=u'専用ガチャポイント')
    tip = PositiveBigIntegerField(default=0, verbose_name=u'チップ所持数')

class ScoutEventFlags(BasePerPlayerBase):
    """スカウトイベントフラグ関係.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントのマスターID')
    opvtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'OP演出閲覧時間')
    destroyprize_received = ObjectField(default=list, verbose_name=u'直前に受け取ったポイント報酬')
    epvtime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'EP演出閲覧時間')

class ScoutEventPresentNum(BasePerPlayerBase):
    """スカウトイベントプレゼント数レコード.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントのマスターID')
    point = PositiveBigIntegerField(default=0, verbose_name=u'未投入のポイント')
    nums = ObjectField(default=dict, verbose_name=u'各プレゼント数のデータ')
    result_number = models.PositiveSmallIntegerField(default=0, verbose_name=u'前回投入した項目')
    result_pointpre = PositiveBigIntegerField(default=0, verbose_name=u'前回投入前のポイント')
    result_pointpost = PositiveBigIntegerField(default=0, verbose_name=u'前回投入後のポイント')
    
    def get_num(self, present_number):
        return self.nums.get(present_number, 0)
    
    def set_num(self, present_number, num):
        self.nums[present_number] = num
    
    def add_num(self, present_number, num):
        self.set_num(present_number, self.get_num(present_number) + num)

class ScoutEventTanzakuCastMaster(BaseMaster):
    """スカウトイベント逢引システムキャストマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    eventid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントマスターID')
    number = models.PositiveSmallIntegerField(default=0, verbose_name=u'イベント別通し番号', choices=[(i, i) for i in xrange(5)])
    castname = models.CharField(max_length=64, verbose_name=u'キャストの名前')
    castthumb = models.CharField(max_length=128, verbose_name=u'キャスト画像(.png)', blank=True)
    castbg = models.CharField(max_length=128, verbose_name=u'キャスト背景画像(.png)', blank=True)
    castthumb_small = models.CharField(max_length=128, verbose_name=u'キャスト画像小(.png)', blank=True)
    tanzakuname = models.CharField(max_length=48, default=u'短冊', blank=True, verbose_name=u'短冊の名前')
    tanzakuunit = models.CharField(max_length=48, default=u'枚', blank=True, verbose_name=u'短冊の単位')
    tanzakuthumb = models.CharField(max_length=128, verbose_name=u'短冊画像(.png)', blank=True)
    prizes  = JsonCharField(default=list, verbose_name=u'業績報酬テーブル')
    prize_text  = models.PositiveIntegerField(default=0, verbose_name=u'業績報酬テキスト')
    tanzaku = models.PositiveSmallIntegerField(default=0, verbose_name=u'指名に必要な短冊数')
    tip_rate = models.PositiveSmallIntegerField(default=0, verbose_name=u'短冊1枚のチップ交換レート')
    tip_quota = models.PositiveSmallIntegerField(default=0, verbose_name=u'業績報酬のチップ規定数')
    
    @staticmethod
    def makeID(eventid, number):
        return (eventid << 32) + number
    
    @staticmethod
    def makeInstance(key):
        ins = ScoutEventTanzakuCastMaster()
        ins.id = key
        ins.eventid = int(key>>32)
        ins.number = int(key&0xffffffff)
        return ins

class ScoutEventTanzakuCastData(BasePerPlayerBaseWithMasterID):
    """スカウトイベント逢引システムキャスト情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    current_cast = models.SmallIntegerField(default=-1, verbose_name=u'現在指名中のキャスト')
    tanzaku_0 = models.PositiveIntegerField(default=0, verbose_name=u'短冊所持数0')
    tip_0 = models.PositiveIntegerField(default=0, verbose_name=u'チップ投入数0')
    tanzaku_1 = models.PositiveIntegerField(default=0, verbose_name=u'短冊所持数1')
    tip_1 = models.PositiveIntegerField(default=0, verbose_name=u'チップ投入数1')
    tanzaku_2 = models.PositiveIntegerField(default=0, verbose_name=u'短冊所持数2')
    tip_2 = models.PositiveIntegerField(default=0, verbose_name=u'チップ投入数2')
    tanzaku_3 = models.PositiveIntegerField(default=0, verbose_name=u'短冊所持数3')
    tip_3 = models.PositiveIntegerField(default=0, verbose_name=u'チップ投入数3')
    tanzaku_4 = models.PositiveIntegerField(default=0, verbose_name=u'短冊所持数4')
    tip_4 = models.PositiveIntegerField(default=0, verbose_name=u'チップ投入数4')
    
    def get_tanzaku(self, number):
        return getattr(self, 'tanzaku_{}'.format(number))
    def set_tanzaku(self, number, tanzaku):
        tanzaku = min(0xffffffff, tanzaku)
        setattr(self, 'tanzaku_{}'.format(number), tanzaku)
    
    def get_tip(self, number):
        return getattr(self, 'tip_{}'.format(number))
    def set_tip(self, number, tip):
        tip = min(0xffffffff, tip)
        setattr(self, 'tip_{}'.format(number), tip)

class ScoutEventCastPerformanceResult(BaseModel):
    """スカウトイベント業績の最終結果.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'イベントマスターID')
    tip_0 = PositiveBigIntegerField(default=0, verbose_name=u'チップ投入数0')
    tip_1 = PositiveBigIntegerField(default=0, verbose_name=u'チップ投入数1')
    tip_2 = PositiveBigIntegerField(default=0, verbose_name=u'チップ投入数2')
    tip_3 = PositiveBigIntegerField(default=0, verbose_name=u'チップ投入数3')
    tip_4 = PositiveBigIntegerField(default=0, verbose_name=u'チップ投入数4')
    
    def get_tip(self, number):
        return getattr(self, 'tip_{}'.format(number))
    
    def get_tip_all(self):
        arr = []
        while True:
            number = len(arr)
            attr = 'tip_{}'.format(number)
            if not hasattr(self, attr):
                break
            tip = self.get_tip(number)
            arr.append((number, tip))
        return dict(arr)
    
    def get_winner(self):
        """勝者を取得.
        """
        arr = self.get_tip_all().items()
        # チップ数の多い順にソート.
        arr.sort(key=lambda x:x[1], reverse=True)
        
        winner = []
        tip_max = None
        for number, tip in arr:
            if tip < 1 or (tip_max is not None and tip < tip_max):
                # 投入されていない or 最大値でなくなった.
                break
            winner.append(number)
            tip_max = tip
        return winner

class ScoutEventRaidMaster(BaseMaster):
    """スカウトイベント用レイドデータ.
    RaidMasterのスカウトイベント用拡張.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    eventid = models.PositiveIntegerField(db_index=True, verbose_name=u'レイドイベントマスターID')
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'レイドマスターID')
    tanzaku_rate = models.PositiveSmallIntegerField(default=0, verbose_name=u'短冊ドロップ率(％)')
    tanzaku_number = models.PositiveSmallIntegerField(default=0, verbose_name=u'獲得短冊番号')
    tanzaku_randmin = models.PositiveIntegerField(default=0, verbose_name=u'獲得短冊数下限')
    tanzaku_randmax = models.PositiveIntegerField(default=0, verbose_name=u'獲得短冊数上限')
    tanzaku_help_rate = models.PositiveSmallIntegerField(default=0, verbose_name=u'短冊ドロップ率(救援)(％)')
    tanzaku_help_number = models.PositiveSmallIntegerField(default=0, verbose_name=u'獲得短冊番号(救援)')
    tanzaku_help_randmin = models.PositiveIntegerField(default=0, verbose_name=u'獲得短冊数下限(救援)')
    tanzaku_help_randmax = models.PositiveIntegerField(default=0, verbose_name=u'獲得短冊数上限(救援)')
    
    @staticmethod
    def makeID(eventid, mid):
        return (eventid << 32) + mid
    
    @staticmethod
    def makeInstance(key):
        ins = ScoutEventRaidMaster()
        ins.id = key
        ins.eventid = int(key>>32)
        ins.mid = int(key&0xffffffff)
        return ins

class ScoutEventHappeningTableMaster(BaseMaster):
    """スカウトイベントの曜日別ハプニング発生テーブルマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    eventid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントマスターID')
    wday = models.PositiveSmallIntegerField(default=0, verbose_name=u'曜日', choices=[(w, u'{}:{}'.format(w,Defines.WeekDay.NAMES[w])) for w in Defines.WeekDay.LIST])
    happenings = JsonCharField(default=list, verbose_name=u'発生するハプニング')
    
    @staticmethod
    def makeID(eventid, wday):
        return (eventid << 32) + wday
    
    @staticmethod
    def makeInstance(key):
        ins = ScoutEventHappeningTableMaster()
        ins.id = key
        ins.eventid = int(key>>32)
        ins.wday = int(key&0xffffffff)
        return ins
