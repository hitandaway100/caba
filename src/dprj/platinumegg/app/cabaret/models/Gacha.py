# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMasterWithThumbnail,\
    BaseMaster, BaseMasterWithName, BaseModel
from platinumegg.app.cabaret.models.Player import BasePerPlayerBase,\
    BasePerPlayerBaseWithMasterID
from platinumegg.app.cabaret.models.base.fields import ObjectField,\
    JsonCharField, AppDateTimeField, PositiveBigIntegerField, PositiveAutoField,\
    PositiveBigAutoField
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
import random
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.util.apprandom import AppRandom
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class GachaMaster(BaseMasterWithThumbnail):
    """引きぬきガチャのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    pay_thumb = models.CharField(max_length=128, verbose_name=u'課金用サムネイル')
    pay_thumb_pc = models.CharField(max_length=128, verbose_name=u'PC版課金用サムネイル')
    unique_name = models.CharField(max_length=32, unique=True, verbose_name=u'ユニークキー')
    tabname = models.CharField(max_length=16, default=u'', verbose_name=u'タブ名', blank=True)
    tabengname = models.CharField(max_length=16, default=u'', verbose_name=u'タブ名(リンク用)', blank=True)
    schedule = models.PositiveIntegerField(default=0, verbose_name=u'期間')
    stime_text = models.CharField(max_length=64, default='', verbose_name=u'開始時間表示用テキスト', help_text=u'未設定の場合はscheduleを見て表示します', blank=True)
    etime_text = models.CharField(max_length=64, default='', verbose_name=u'終了時間表示用テキスト', help_text=u'未設定の場合はscheduleを見て表示します', blank=True)
    continuity = models.PositiveSmallIntegerField(default=1, verbose_name=u'回数')
    consumetype = models.PositiveSmallIntegerField(verbose_name=u'消費するもの', choices=dict_to_choices(Defines.GachaConsumeType.NAMES), db_index=True)
    consumevalue = models.PositiveIntegerField(verbose_name=u'消費量')
    stock = models.PositiveSmallIntegerField(default=0, verbose_name=u'ガチャの在庫数', help_text=u'0で無制限')
    firsttimetype = models.PositiveSmallIntegerField(verbose_name=u'毎日初回 or 1度きり', choices=dict_to_choices(Defines.GachaFirsttimeType.NAMES))
    firststock = models.PositiveSmallIntegerField(verbose_name=u'初回ガチャの在庫数')
    firstcontinuity = models.PositiveSmallIntegerField(verbose_name=u'初回ガチャを1度に回す回数')
    consumefirstvalue = models.PositiveIntegerField(verbose_name=u'初回消費量')
    boxid = models.PositiveIntegerField(default=0, verbose_name=u'BoxID')
    special_boxid = JsonCharField(default=list, verbose_name=u'回数別BoxID', blank=True)
    rarity_fixed_boxid = models.PositiveIntegerField(default=0, verbose_name=u'レアリティ確定の際に使用するBoxID')
    rarity_fixed_num = models.PositiveSmallIntegerField(default=0, verbose_name=u'レアリティ確定枚数')
    bonus = JsonCharField(default=list, verbose_name=u'おまけ')
    variableconsumevalue = JsonCharField(default=dict, verbose_name=u'変動消費量')
    premium = models.BooleanField(default=False, verbose_name=u'プレミアムフラグ(課金ガチャ用)')
    stepid = models.PositiveIntegerField(default=0, verbose_name=u'StepID')
    step = models.PositiveIntegerField(default=0, verbose_name=u'ステップ番号')
    stepsid = models.PositiveIntegerField(default=0, verbose_name=u'ステップ開始ガチャID')
    seattableid = models.PositiveIntegerField(default=0, verbose_name=u'シートテーブルID')
    addsocardflg = models.BooleanField(default=0, verbose_name=u'特効追加注意表示フラグ')
    img_rule = models.CharField(max_length=128, verbose_name=u'ルール画像', blank=True, default='')
    point_rate = JsonCharField(default=list, verbose_name=u'ポイントレート',help_text=u'[9月中期新規追加ガチャ]のイベント時にガチャを回した際に付与されるポイント')
    trade_shop_master_id = models.PositiveSmallIntegerField(verbose_name=u'TradeShopMasetrID',default=0)
    gacha_explain_text_id = models.PositiveSmallIntegerField(verbose_name=u'GachaExplainTextID', default=0)
    def get_bonus_all(self, with_name=False):
        """おまけを全て取得.
        """
        if not self.bonus or not isinstance(self.bonus, list):
            return []
        elif not isinstance(self.bonus[0], dict):
            return [self.bonus]
        else:
            return [data['prize'] for data in self.bonus]
    
    def get_bonus_name(self):
        """おまけの名前を取得.
        """
        if not self.bonus or not isinstance(self.bonus, list):
            return []
        elif not isinstance(self.bonus[0], dict):
            return ['おまけ%d' % (i+1) for i in xrange(len(self.bonus))]
        else:
            return [data.get('name', 'おまけ%d' % (i+1)) for i,data in enumerate(self.bonus)]
    
    def choice_bonus(self, rand=None):
        """おまけを選定.
        """
        if not self.bonus or not isinstance(self.bonus, list):
            return []
        elif not isinstance(self.bonus[0], dict):
            return self.bonus
        
        rand = rand or AppRandom()
        rate_total = sum([data.get('rate', 0) for data in self.bonus])
        if rate_total < 1 or AppRandom.RAND_MAX <= rate_total:
            raise CabaretError(u'おまけの確率が壊れています', CabaretError.Code.INVALID_MASTERDATA)
        
        v = rand.getIntN(rate_total)
        for data in self.bonus:
            rate = data.get('rate', 0)
            v -= rate
            if 0 < rate and v <= 0:
                return data['prize']
        raise CabaretError(u'想定外のバグです')

class GachaBoxMaster(BaseMaster):
    """ボックス.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'名前')
    box = JsonCharField(default=list, verbose_name=u'BOX内容')
    banner = models.CharField(max_length=64, verbose_name=u'ページ上部のバナー画像', blank=True)

    def lottery_cardgroup_id(self, random):
        lottery = sum([int(data['rate']) for data in self.box])
        randint = random.getIntN(lottery)
        total_rate = 0
        for data in self.box:
            total_rate += int(data['rate'])
            if randint < total_rate:
                return int(data['id'])

class GachaBoxGachaDetailMaster(BaseMaster):
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ガチャID')
    allowreset_rarity = models.PositiveIntegerField(default=0, verbose_name=u'リセット許可レアリティ', choices=dict_to_choices(Defines.Rarity.NAMES))
    allowreset_cardidlist = JsonCharField(default=list, verbose_name=u'リセット許可カードIDリスト')
    limit_resettime = models.PositiveIntegerField(default=0, verbose_name=u'リセット可能回数')
    prizelist = JsonCharField(default=list, verbose_name=u'BOX引き切り報酬')
    textid = models.PositiveIntegerField(default=0, verbose_name=u'報酬文言')

class GachaGroupMaster(BaseMaster):
    """ボックスのグループ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(default='', max_length=48, verbose_name=u'名前')
    rare = models.PositiveSmallIntegerField(verbose_name=u'レア度', choices=dict_to_choices(Defines.Rarity.NAMES_INCLUDE_ALL), default=Defines.Rarity.ALL)
    table = JsonCharField(default=list, verbose_name=u'テーブル')
    expectation = models.PositiveSmallIntegerField(verbose_name=u'期待度', choices=dict_to_choices(Defines.RankingGachaExpect.NAMES), default=Defines.RankingGachaExpect.LOW)
    
    def getCardNum(self):
        return len(self.table)
    

class GachaStepupMaster(BaseMaster):
    """ステップアップ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    stepmax = models.PositiveIntegerField(default=0, verbose_name=u'最大ステップ数')
    lapdaymax = models.PositiveIntegerField(default=0, verbose_name=u'最大周回数（日あたり）')
    stepreset = models.BooleanField(default=False, verbose_name=u'ステップリセット有無')
    stepresettime = models.PositiveSmallIntegerField(default=0, verbose_name=u'リセット時間(00:00:00からの秒数)')
    lapreset = models.BooleanField(default=False, verbose_name=u'週回数リセット有無')
    lapresettime = models.PositiveSmallIntegerField(default=0, verbose_name=u'リセット時間(00:00:00からの秒数)')
    img_banner = models.CharField(max_length=128, verbose_name=u'ルール画像上部のバナー', blank=True)
    img_rule = models.CharField(max_length=128, verbose_name=u'ルール画像', blank=True)

class GachaSeatTableMaster(BaseMasterWithThumbnail):
    """ガチャのおまけシートマスター.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    seatid = models.PositiveIntegerField(verbose_name=u'シートID')
    specialseat = JsonCharField(default=list, verbose_name=u'回数ごとの特別なシート', help_text="[[回数,シートID],...]")
    
    def getSeatId(self, lap):
        table = dict(self.specialseat)
        return table.get(lap, self.seatid)

class GachaSeatMaster(BaseMasterWithName):
    """ガチャのおまけシート報酬マスター.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    effectname = models.CharField(max_length=48, verbose_name=u'演出名')
    img_effect = models.CharField(max_length=128, verbose_name=u'演出用画像', blank=True)
    textid = models.PositiveIntegerField(default=0, verbose_name=u'報酬文言')
    prize_0 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID0')
    weight_0 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み0')
    thumb_0 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像0', blank=True)
    prize_1 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID1')
    weight_1 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み1')
    thumb_1 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像1', blank=True)
    prize_2 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID2')
    weight_2 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み2')
    thumb_2 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像2', blank=True)
    prize_3 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID3')
    weight_3 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み3')
    thumb_3 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像3', blank=True)
    prize_4 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID4')
    weight_4 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み4')
    thumb_4 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像4', blank=True)
    prize_5 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID5')
    weight_5 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み5')
    thumb_5 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像5', blank=True)
    prize_6 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID6')
    weight_6 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み6')
    thumb_6 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像6', blank=True)
    prize_7 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID7')
    weight_7 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み7')
    thumb_7 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像7', blank=True)
    prize_8 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID8')
    weight_8 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み8')
    thumb_8 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像8', blank=True)
    prize_9 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID9')
    weight_9 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み9')
    thumb_9 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像9', blank=True)
    prize_10 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID10')
    weight_10 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み10')
    thumb_10 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像10', blank=True)
    prize_11 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID11')
    weight_11 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み11')
    thumb_11 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像11', blank=True)
    prize_12 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID12')
    weight_12 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み12')
    thumb_12 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像12', blank=True)
    prize_13 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID13')
    weight_13 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み13')
    thumb_13 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像13', blank=True)
    prize_14 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID14')
    weight_14 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み14')
    thumb_14 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像14', blank=True)
    prize_15 = models.PositiveIntegerField(default=0, verbose_name=u'報酬ID15')
    weight_15 = models.PositiveSmallIntegerField(default=0, verbose_name=u'報酬重み15')
    thumb_15 = models.CharField(max_length=128, default='', verbose_name=u'報酬画像15', blank=True)
    
    def getPrizeId(self, idx):
        return getattr(self, 'prize_%d' % idx, None)
    def getWeight(self, idx):
        return getattr(self, 'weight_%d' % idx, None)
    def getThumb(self, idx):
        return getattr(self, 'thumb_%d' % idx, None)
    
    def select(self, playdata=None, rand=None):
        rand = rand or AppRandom()
        
        idx = 0
        indexlist = []
        weightlist = []
        opened = []
        while True:
            prizeid = self.getPrizeId(idx)
            if prizeid is None:
                break
            weight = self.getWeight(idx)
            if prizeid and weight:
                if playdata and playdata.getFlag(idx):
                    opened.append(idx)
                else:
                    indexlist.append(idx)
                    weightlist.append(weight)
            idx += 1
        
        if not weightlist:
            if opened:
                playdata.clearFlags()
                return self.select(playdata, rand)
            else:
                return None
        
        v = rand.getIntN(sum(weightlist))
        for idx,weight in enumerate(weightlist):
            if v < weight:
                return indexlist[idx]
            v -= weight
        return None

def getSeed():
    return int(random.random() * 65535)

class GachaPlayCount(BasePerPlayerBase):
    """ガチャプレイ回数.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'マスターID')
    cnt = models.PositiveIntegerField(default=0, verbose_name=u'本日プレイ回数')
    cnttotal = models.PositiveIntegerField(default=0, verbose_name=u'総プレイ回数')
    step = models.PositiveIntegerField(default=0, verbose_name=u'本日ステップ数')
    steptotal = models.PositiveIntegerField(default=0, verbose_name=u'総ステップ数')
    lap = models.PositiveIntegerField(default=0, verbose_name=u'本日周回数')
    laptotal = models.PositiveIntegerField(default=0, verbose_name=u'総周回数')
    ptime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'最終プレイ時間')
    
    def getTodayPlayCnt(self, now=None):
        now = now or OSAUtil.get_now()
        if DateTimeUtil.judgeSameDays(now, self.ptime):
            return self.cnt
        else:
            return 0
    
    def addPlayCnt(self, cnt=1, now=None):
        self.cnt = self.getTodayPlayCnt(now) + cnt
        self.cnttotal += cnt
        self.ptime = now or OSAUtil.get_now()

class GachaConsumePoint(BasePerPlayerBase):
    """ガチャ台別の消費ポイント.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'マスターID')
    point = models.PositiveIntegerField(default=0, verbose_name=u'総消費ポイント')

class GachaPlayData(BasePerPlayerBase):
    """ガチャプレイ情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'マスターID')
    seed = models.PositiveIntegerField(default=getSeed, verbose_name=u'乱数シード')
    counts = ObjectField(default=dict, verbose_name=u'グループ選択回数')
    result = ObjectField(default=dict, verbose_name=u'前回の結果')
    
    def resetGroupCounts(self):
        self.counts = {}
    
    def addGroupCount(self, groupid, cnt=1):
        self.counts[groupid] = self.getGroupCount(groupid) + cnt
    
    def getGroupCount(self, groupid):
        return self.counts.get(groupid, 0)

class GachaSlideCastMaster(BaseMaster):
    """スライド表示するキャスト設定.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ガチャID')
    castlist = JsonCharField(default=list, verbose_name=u'表示するキャスト')
    
class GachaHeaderMaster(BaseMaster):
    """一枚絵をスライド表示する画像設定.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ガチャID')
    header = JsonCharField(default=list, verbose_name=u'表示する画像')

class GachaSeatTablePlayCount(BasePerPlayerBaseWithMasterID):
    """ガチャのシートテーブルごとのプレイ回数情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    lap = models.PositiveIntegerField(default=0, verbose_name=u'周回数')
    cnt = models.PositiveIntegerField(default=0, verbose_name=u'プレイ回数')

class GachaSeatPlayData(BasePerPlayerBaseWithMasterID):
    """ガチャのおまけシート情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    seed = models.PositiveIntegerField(default=getSeed, verbose_name=u'乱数シード')
    last = models.PositiveSmallIntegerField(default=0, verbose_name=u'最後に受け取った報酬')
    flag_0 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ0')
    flag_1 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ1')
    flag_2 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ2')
    flag_3 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ3')
    flag_4 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ4')
    flag_5 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ5')
    flag_6 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ6')
    flag_7 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ7')
    flag_8 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ8')
    flag_9 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ9')
    flag_10 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ10')
    flag_11 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ11')
    flag_12 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ12')
    flag_13 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ13')
    flag_14 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ14')
    flag_15 = models.BooleanField(default=False, verbose_name=u'報酬受け取りフラグ15')
    
    def clearFlags(self):
        idx = 0
        while True:
            if not hasattr(self, 'flag_%d' % idx):
                break
            self.setFlag(idx, False)
            idx += 1
    
    def getFlag(self, idx):
        return getattr(self, 'flag_%d' % idx, False)
    
    def setFlag(self, idx, flag=True):
        return setattr(self, 'flag_%d' % idx, flag)
    
    def is_first(self):
        idx = 0
        while True:
            if not hasattr(self, 'flag_%d' % idx):
                break
            if self.getFlag(idx):
                return False
            idx += 1
        return True
    
    def getReceivedNum(self):
        idx = 0
        cnt = 0
        while True:
            if not hasattr(self, 'flag_%d' % idx):
                break
            if self.getFlag(idx):
                cnt += 1
            idx += 1
        return cnt

class GachaTicket(BasePerPlayerBaseWithMasterID):
    """追加分のチケット所持数.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    num = models.PositiveIntegerField(default=0, verbose_name=u'所持数')

class RankingGachaMaster(BaseMaster):
    """ランキングガチャ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID(BoxID)')
    name = models.CharField(max_length=48, verbose_name=u'名前(管理用)')
    randmin = models.PositiveSmallIntegerField(default=0, verbose_name=u'ポイントの乱数幅(下限％)')
    randmax = models.PositiveSmallIntegerField(default=0, verbose_name=u'ポイントの乱数幅(上限％)')
    singleprizes = JsonCharField(default=list, verbose_name=u'単発ランキング報酬')
    singleprize_text = models.PositiveIntegerField(default=0, verbose_name=u'単発ランキング報酬文言')
    totalprizes = JsonCharField(default=list, verbose_name=u'累計ランキング報酬')
    totalprize_text = models.PositiveIntegerField(default=0, verbose_name=u'累計ランキング報酬文言')
    img_rule = models.CharField(max_length=128, verbose_name=u'ルール画像', blank=True)
    img_appeal = JsonCharField(default=list, verbose_name=u'訴求画像リスト')
    group = models.PositiveIntegerField(db_index=True, default=0, verbose_name=u'ランキンググループ番号')
    wholeprizes = JsonCharField(default=list, verbose_name=u'総計pt報酬')
    wholeprize_text = models.PositiveIntegerField(default=0, verbose_name=u'総計pt報酬文言')
    wholewinprizes = JsonCharField(default=list, verbose_name=u'総計pt勝利報酬')
    wholewinprize_text = models.PositiveIntegerField(default=0, verbose_name=u'総計pt勝利報酬文言')
    
    @property
    def is_support_totalranking(self):
        """累計ランキングをサポートしているか.
        """
        return bool(self.totalprizes)
    
    @property
    def is_support_wholepoint(self):
        """総計Ptをサポートしているか.
        """
        return bool(self.wholeprizes or self.wholewinprizes)
    
    def get_wholeprizes(self, point_min=1, point_max=None):
        wholeprizes = self.wholeprizes
        if isinstance(wholeprizes, list):
            return dict(wholeprizes)
        elif not isinstance(wholeprizes, dict):
            return {}
        
        table = dict(wholeprizes.get('normal') or [])
        repeat = wholeprizes.get('repeat') or []
        
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
    
    def get_singleprize_first(self):
        """先頭のランキング報酬情報.
        """
        singleprizes = self.singleprizes[:]
        singleprizes.sort(key=lambda x:x.get("rank_min", 1))
        rank_max = None
        rank_min = None
        prizes = []
        for data in singleprizes:
            if rank_min is not None and data.get("rank_min", 1) != rank_min:
                break
            rank_min = data.get("rank_min", 1)
            data_rank_max = data.get("rank_max", None)
            rank_max = min(data_rank_max, rank_max) if data_rank_max and rank_max else (data_rank_max or rank_max)
            prizes.extend(data['prize'])
        return {
            'rank_min' : rank_min,
            'rank_max' : rank_max,
            'prize' : prizes,
        }

class RankingGachaScore(BasePerPlayerBaseWithMasterID):
    """ランキングガチャスコア情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    single = models.PositiveIntegerField(default=0, verbose_name=u'単発ポイント')
    total = PositiveBigIntegerField(default=0, verbose_name=u'累計ポイント')
    firstpoint = PositiveBigIntegerField(default=0, verbose_name=u'初めてプレイした時の総計pt')
    firsttime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'初めてプレイした時間')

class RankingGachaClose(BaseModel):
    """ランキングガチャ終了処理用.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID(BoxID)')
    utime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'更新時間')
    prize_flag_single = models.PositiveIntegerField(default=0, verbose_name=u'単発ランキング報酬配布フラグ')
    prize_flag_total = models.PositiveIntegerField(default=0, verbose_name=u'累計ランキング報酬配布フラグ')
    prize_flag_whole = models.PositiveIntegerField(default=0, verbose_name=u'総計pt報酬配布フラグ')

class RankingGachaWholeData(BaseModel):
    """ランキングガチャ全体のデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID(BoxID)')
    point = PositiveBigIntegerField(default=0, verbose_name=u'総計pt')

class RankingGachaWholePrizeQueue(BaseModel):
    """ランキングガチャ総計pt報酬配布キュー.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveAutoField(primary_key=True, verbose_name=u'ID')
    boxid = models.PositiveIntegerField(verbose_name=u'BoxID')
    point = PositiveBigIntegerField(verbose_name=u'総計pt')
    prizes = JsonCharField(default=list, verbose_name=u'総計pt報酬')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'作成時間')

class RankingGachaWholePrizeData(BaseModel):
    """ランキングガチャ総計pt報酬ユーザー情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    queueid = models.PositiveIntegerField(default=0, verbose_name=u'受け取った総計pt報酬キューのID')

class RankingGachaPlayLog(BaseModel):
    """ランキングガチャ全体履歴.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    uid = models.PositiveIntegerField(verbose_name=u'ユーザID')
    boxid = models.PositiveIntegerField(verbose_name=u'BoxID')
    point = PositiveBigIntegerField(verbose_name=u'総計pt')
    point_whole = PositiveBigIntegerField(verbose_name=u'総計pt')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'作成時間')

class GachaBoxResetPlayerData(BaseModel):
    """ボックスガチャリセット関係(BOXガチャ詳細関係)のユーザデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    resetcount = models.PositiveIntegerField(default=0, verbose_name=u'リセットした回数')
    is_get_targetrarity = models.BooleanField(default=False, verbose_name=u'リセット許可対象を引き抜いたかどうか')

    @classmethod
    def makeInstance(cls, uid):
        ins = cls()
        ins.id = uid
        ins.resetcount = 0
        ins.is_get_targetrarity = False
        return ins
