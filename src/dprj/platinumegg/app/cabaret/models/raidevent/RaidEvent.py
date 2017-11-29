# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.models import BaseMaster, Singleton,\
    BaseModel
from platinumegg.app.cabaret.models.base.fields import JsonCharField,\
    AppDateTimeField, PositiveBigIntegerField, ObjectField, TinyIntField, PositiveBigAutoField
from platinumegg.app.cabaret.models.Player import BasePerPlayerBase
from defines import Defines
import datetime

class RaidEventMaster(BaseMaster):
    """レイドイベントのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'イベント名')
    subname = models.CharField(max_length=64, verbose_name=u'イベントサブタイトル', blank=True, default='')
    htmlname = models.CharField(max_length=48, verbose_name=u'HTMLディレクトリ名')
    effectname = models.CharField(max_length=48, verbose_name=u'演出ディレクトリ名')
    raidtable = JsonCharField(default=list, verbose_name=u'レイド出現テーブル')
    raidtable_timebonus = JsonCharField(default=list, verbose_name=u'レイド出現テーブル(タイムボーナス)')
    raidtable_big = JsonCharField(default=list, verbose_name=u'大ボス出現後レイド出現テーブル')
    raidtable_timebonus_big = JsonCharField(default=list, verbose_name=u'大ボス出現後レイド出現テーブル(タイムボーナス)')
    rankingprizes = JsonCharField(default=list, verbose_name=u'ランキング報酬')
    destroyprizes = JsonCharField(default=dict, verbose_name=u'討伐回数報酬')
    destroyprizes_big = JsonCharField(default=dict, verbose_name=u'討伐回数報酬(大ボス)')
    pointratio = models.PositiveIntegerField(default=0, verbose_name=u'ポイントの交換レート')
    rankingprize_text = models.PositiveIntegerField(default=0, verbose_name=u'ランキング報酬文言')
    destroyprize_text = models.PositiveIntegerField(default=0, verbose_name=u'討伐回数報酬文言')
    pointname = models.CharField(max_length=48, verbose_name=u'秘宝名')
    ticketname = models.CharField(max_length=48, verbose_name=u'ガチャチケット名')
    pointthumb = models.CharField(max_length=48, verbose_name=u'秘宝サムネ')
    ticketthumb = models.CharField(max_length=48, verbose_name=u'ガチャチケットサムネ')
    combobonus = JsonCharField(default=list, verbose_name=u'コンボボーナステーブル', help_text=u'[[参加人数,加算する倍率％],...]という形式')
    feverchancetime = models.PositiveIntegerField(default=0, verbose_name=u'フィーバーチャンスの制限時間[sec]')
    feverchancepowup = models.PositiveIntegerField(default=100, verbose_name=u'フィーバーチャンスで加算する倍率[％]')
    fastbonustable = JsonCharField(default=list, verbose_name=u'秘宝ボーナス', help_text=u'[[発見してからの経過時間(sec),倍率％],...]という形式')
    joinprizes = JsonCharField(default=list, verbose_name=u'イベント開始報酬')
    joinprize_text = models.PositiveIntegerField(default=0, verbose_name=u'イベント開始報酬文言')
    topimg = models.CharField(default='', blank=True, max_length=96, verbose_name=u'トップページ画像')
    topbuttontext = models.CharField(max_length=48, verbose_name=u'TOPページスカウトボタン下の文言', blank=True, default='')
    img_appeal = JsonCharField(default=list, verbose_name=u'訴求画像リスト', blank=True)
    beginer_days = models.PositiveSmallIntegerField(default=0, verbose_name=u'新店舗判定日数')
    beginer_rankingprizes = JsonCharField(default=list, verbose_name=u'新店舗ランキング報酬')
    beginer_rankingprize_text = models.PositiveIntegerField(default=0, verbose_name=u'新店舗ランキング報酬文言')
    op = models.PositiveIntegerField(default=0, verbose_name=u'オープニング演出ID')
    ed = models.PositiveIntegerField(default=0, verbose_name=u'エンディング演出ID')
    
    # エイプリルフール.
    material0 = models.PositiveIntegerField(default=0, verbose_name=u'材料0のID')
    material1 = models.PositiveIntegerField(default=0, verbose_name=u'材料1のID')
    material2 = models.PositiveIntegerField(default=0, verbose_name=u'材料2のID')
    champagne_num_max = TinyIntField(default=0, verbose_name=u'SHOWTIMEまでのシャンパンの必要数')
    champagne_time = models.PositiveSmallIntegerField(default=0, verbose_name=u'SHOWTIMEの制限時間')
    champagne_material_bonus = models.PositiveSmallIntegerField(default=0, verbose_name=u'SHOWTIME時の材料の増加量(％)')
    
    flag_dedicated_stage = models.BooleanField(default=False, verbose_name=u'専用ステージフラグ')
    
    @property
    def codename(self):
        return self.htmlname.split('/')[-1]
    
    @property
    def gachaname(self):
        """カラム追加するかも.
        """
        arr = self.htmlname.split('/')
        return arr[-1] if arr[-1] else arr[-2]
    
    def __get_destroyprizes(self, attname, destroy_min, destroy_max):
        destroyprizes = getattr(self, attname)
        if isinstance(destroyprizes, list):
            return dict(destroyprizes)
        elif not isinstance(destroyprizes, dict):
            return {}
        
        table = dict(destroyprizes.get('normal') or [])
        repeat = destroyprizes.get('repeat') or []
        
        for data in repeat:
            prize = data.get('prize')
            if not prize:
                continue
            
            d_min = max(1, data.get('min', 1))
            d_max = min(data.get('max', destroy_max), destroy_max)
            interval = max(1, data.get('interval', 1))
            
            d = d_min
            while d <= d_max:
                if destroy_min <= d:
                    arr = table[d] = table.get(d) or []
                    arr.extend(prize)
                d += interval
        return table
    
    def __get_next_destroyprizes(self, attname, cur_destroy):
        """次に貰える報酬.
        """
        destroyprizes = getattr(self, attname)
        if isinstance(destroyprizes, list):
            table = dict(destroyprizes)
            repeat = []
        elif isinstance(destroyprizes, dict):
            table = dict(destroyprizes.get('normal') or [])
            repeat = destroyprizes.get('repeat') or []
        else:
            table = {}
            repeat = []
        
        dest_table = {}
        if table:
            destroy_num_list = table.keys()
            destroy_num_list.sort()
            if cur_destroy < destroy_num_list[-1]:
                for num in destroy_num_list:
                    if cur_destroy < num and table[num]:
                        dest_table[num] = table[num][:]
                        break
        
        for data in repeat:
            prize = data.get('prize')
            if not prize:
                continue
            
            d_min = max(1, data.get('min', 1))
            interval = max(1, data.get('interval', 1))
            d_max = min(data.get('max', cur_destroy+interval), cur_destroy+interval)
            
            d = max(d_min, int(((cur_destroy+1) - d_min) / interval) * interval + d_min)
            while d <= d_max:
                if cur_destroy < d:
                    arr = dest_table[d] = dest_table.get(d) or []
                    arr.extend(prize)
                    break
                d += interval
        if dest_table:
            num = min(dest_table.keys())
            return num, dest_table[num]
        else:
            return 0, None
    
    def get_destroyprizes(self, destroy_min=1, destroy_max=1000):
        return self.__get_destroyprizes('destroyprizes', destroy_min, destroy_max)
    def get_destroyprizes_big(self, destroy_min=1, destroy_max=1000):
        return self.__get_destroyprizes('destroyprizes_big', destroy_min, destroy_max)
    
    def get_next_destroyprizes(self, cur_destroy):
        return self.__get_next_destroyprizes('destroyprizes', cur_destroy)
    def get_next_destroyprizes_big(self, cur_destroy):
        return self.__get_next_destroyprizes('destroyprizes_big', cur_destroy)
    
    def getMaterialDict(self):
        dest = {}
        for i in xrange(Defines.RAIDEVENT_MATERIAL_KIND_MAX):
            material = getattr(self, 'material%d' % i)
            if material:
                dest[i] = material
        return dest

class CurrentRaidEventConfig(Singleton):
    """開催中または開催予定のレイド.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    mid = models.PositiveIntegerField(default=0, verbose_name=u'イベントのマスターID')
    starttime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'開始時間')
    endtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'終了時間')
    prize_flag = models.PositiveIntegerField(default=0, verbose_name=u'ランキング報酬配布フラグ')
    bigtime = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'大ボス出現時間')
    ticket_endtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'秘宝交換とガチャ公開終了時間')
    timebonus_time = JsonCharField(default=list, verbose_name=u'タイムボーナス時間')
    combobonus_opentime = JsonCharField(default=list, verbose_name=u'コンボボーナス公開開始時間')
    feverchance_opentime = JsonCharField(default=list, verbose_name=u'フィーバーチャンス公開開始時間')
    fastbonus_opentime = JsonCharField(default=list, verbose_name=u'秘宝ボーナス公開開始時間')
    epilogue_endtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'エピローグ終了時間')
    beginer_prize_flag = models.PositiveIntegerField(default=0, verbose_name=u'新店舗ランキング報酬配布フラグ')
    stageschedule = JsonCharField(default=list, verbose_name=u'途中追加されるステージのスケジュール')
    
    def get_stage_max(self, now=None):
        """現在の最大ステージ数.
        無制限の場合はNone.
        """
        stage_max = None
        if self.stageschedule:
            now = now or OSAUtil.get_now()
            self.stageschedule.sort(key=lambda x:x['time'])
            for data in self.stageschedule:
                if data['time'] <= now:
                    continue
                stage_max = data['stage'] - 1
                break
        return stage_max

class RaidEventRaidMaster(BaseMaster):
    """イベント用レイドデータ.
    RaidMasterのイベント用拡張.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    eventid = models.PositiveIntegerField(db_index=True, verbose_name=u'レイドイベントマスターID')
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'レイドマスターID')
    specialcard = JsonCharField(default=list, verbose_name=u'特効キャスト')
    specialcard_treasure = JsonCharField(default=list, verbose_name=u'特攻ボーナス秘宝獲得率UP')
    ownerpoint = models.PositiveIntegerField(default=0, verbose_name=u'発見者報酬ポイント基本値')
    ownerpoint_growth = models.PositiveIntegerField(default=0, verbose_name=u'発見者報酬ポイント成長度')
    mvppoint = models.PositiveIntegerField(default=0, verbose_name=u'MVP報酬ポイント基本値')
    mvppoint_growth = models.PositiveIntegerField(default=0, verbose_name=u'MVP報酬ポイント成長度')
    ownerpoint_timebonus = models.PositiveIntegerField(default=0, verbose_name=u'発見者報酬ポイント(タイムボーナス)基本値')
    ownerpoint_timebonus_growth = models.PositiveIntegerField(default=0, verbose_name=u'発見者報酬ポイント(タイムボーナス)成長度')
    mvppoint_timebonus = models.PositiveIntegerField(default=0, verbose_name=u'MVP報酬ポイント(タイムボーナス)基本値')
    mvppoint_timebonus_growth = models.PositiveIntegerField(default=0, verbose_name=u'MVP報酬ポイント(タイムボーナス)成長度')
    big = models.BooleanField(default=False, verbose_name=u'大ボスフラグ')
    pointrandmin = models.PositiveSmallIntegerField(default=100, verbose_name=u'報酬ポイント乱数下限(％)')
    pointrandmax = models.PositiveSmallIntegerField(default=100, verbose_name=u'報酬ポイント乱数上限(％)')
    
    # エイプリルフール.
    champagne = TinyIntField(default=0, verbose_name=u'獲得できるシャンパンの数')
    material = TinyIntField(default=0, verbose_name=u'発見者の材料番号(0〜2)', choices=[(i, i) for i in xrange(Defines.RAIDEVENT_MATERIAL_KIND_MAX)])
    material_droprate = models.PositiveSmallIntegerField(default=0, verbose_name=u'発見者の材料ドロップ率(0〜1000)')
    material_num_min = models.PositiveSmallIntegerField(default=0, verbose_name=u'発見者の材料個数の最小')
    material_num_max = models.PositiveSmallIntegerField(default=0, verbose_name=u'発見者の材料個数の最大')
    material_help = TinyIntField(default=0, verbose_name=u'救援者の材料番号(0〜2)', choices=[(i, i) for i in xrange(Defines.RAIDEVENT_MATERIAL_KIND_MAX)])
    material_droprate_help = models.PositiveSmallIntegerField(default=0, verbose_name=u'救援者の材料ドロップ率(0〜1000)')
    material_num_min_help = models.PositiveSmallIntegerField(default=0, verbose_name=u'救援者の材料個数の最小')
    material_num_max_help = models.PositiveSmallIntegerField(default=0, verbose_name=u'救援者の材料個数の最大')
    
    @staticmethod
    def makeID(eventid, mid):
        return (eventid << 32) + mid
    
    @staticmethod
    def makeInstance(key):
        ins = RaidEventRaidMaster()
        ins.id = key
        ins.eventid = int(key>>32)
        ins.mid = int(key&0xffffffff)
        return ins

class RaidEventScore(BasePerPlayerBase):
    """レイドイベントランキング用スコア.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントのマスターID')
    point = PositiveBigIntegerField(default=0, verbose_name=u'所持ポイント')
    point_total = PositiveBigIntegerField(default=0, verbose_name=u'累計ポイント')
    destroy = models.PositiveIntegerField(default=0, verbose_name=u'討伐回数')
    destroy_big = models.PositiveIntegerField(default=0, verbose_name=u'討伐回数(大ボス)')
    ticket = models.PositiveIntegerField(default=0, verbose_name=u'チケット')

class RaidEventFlags(BasePerPlayerBase):
    """レイドイベントフラグ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントのマスターID')
    opvtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'OP演出閲覧時間')
    tbvtime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'タイムボーナス演出閲覧時間')
    destroyprize_flags = ObjectField(default=list, verbose_name=u'討伐回数報酬受取りフラグ')
    destroyprize_big_flags = ObjectField(default=list, verbose_name=u'討伐回数報酬受取りフラグ(大ボス)')
    destroyprize_received = ObjectField(default=list, verbose_name=u'直前に受け取った報酬')
    epvtime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'EP演出閲覧時間')

class RaidEventFlagsUnwilling(BasePerPlayerBase):
    """レイドイベントフラグ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントのマスターID')
    bigbosstime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'大ボス演出閲覧時間')

class RaidEventChampagne(BaseModel):
    """レイドイベントシャンパン所持数.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    eventid = models.PositiveIntegerField(default=0, verbose_name=u'イベントのマスターID')
    num = TinyIntField(default=0, verbose_name=u'所持数')
    etime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'SHOWTIME終了時間')
    
    def getChampagneNum(self, eventid):
        """現在のシャンパン所持数を取得.
        """
        return self.num if eventid == self.eventid else 0
    
    def setChampagneNum(self, eventid, num):
        """現在のシャンパン所持数を設定.
        """
        self.eventid = eventid
        self.num = num
    
    def addChampagneNum(self, eventid, num, nummax):
        """現在のシャンパン所持数を加算.
        """
        self.setChampagneNum(eventid, min(self.getChampagneNum(eventid) + num, nummax))
    
    def setStartChampagneCall(self, eventid, timelimit_sec, now=None):
        """SHOWTIME開始設定.
        """
        # シャンパン所持数を0に.
        self.setChampagneNum(eventid, 0)
        # 終了時間を設定.
        now = now or OSAUtil.get_now()
        self.etime = now + datetime.timedelta(seconds=timelimit_sec)
    
    def isChampagneCall(self, eventid, now=None):
        """SHOWTIME判定.
        """
        now = now or OSAUtil.get_now()
        return self.eventid == eventid and now <= self.etime

class RaidEventSpecialBonusScore(BaseModel):
    """レイドイベント特攻ボーナスによる裏社会の秘宝倍率テーブル.
    """
    id = models.PositiveIntegerField(primary_key=True, db_index=True, verbose_name=u'ユーザID')
    bonusscore = models.PositiveSmallIntegerField(default=0, verbose_name=u'裏社会の秘宝ボーナス獲得UP倍率')
    last_happening_score = models.PositiveSmallIntegerField(default=0, verbose_name=u'前回レイドのボーナス倍率')

    @classmethod
    def makeInstance(cls, uid, bonusscore=0):
        ins = cls()
        ins.id = uid
        ins.bonusscore = bonusscore
        ins.last_happening_score = bonusscore
        return ins

class RaidEventSpecialBonusScoreLog(BaseModel):
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    bonusscore = models.PositiveSmallIntegerField(default=0, verbose_name=u'裏社会の秘宝ボーナス獲得UP倍率')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'ログ生成時間')

    @classmethod
    def makeInstance(cls, raidlogid, bonusscore=0):
        ins = cls()
        ins.id = raidlogid
        ins.bonusscore = bonusscore
        return ins

class RaidEventHelpSpecialBonusScore(BaseModel):
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    raidid = PositiveBigIntegerField(db_index=True, verbose_name=u'レイドID')
    uid = models.PositiveIntegerField(verbose_name=u'救援時ボーナスの所有者')
    bonusscore = models.PositiveSmallIntegerField(default=0, verbose_name=u'裏社会の秘宝ボーナス獲得UP倍率')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'ログ生成時間')

    @classmethod
    def makeInstance(cls, raidid, uid, bonusscore=0):
        ins = cls()
        ins.raidid = raidid
        ins.uid = uid
        ins.bonusscore = bonusscore
        return ins
