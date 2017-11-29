# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseModel, BaseMaster
from platinumegg.app.cabaret.models.base.fields import PositiveBigAutoField,\
    ObjectField, AppDateTimeField, PositiveBigIntegerField, TinyIntField,\
    JsonCharField
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.apprandom import AppRandom

class BattleResult(BaseModel):
    """バトル結果.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    uid = models.PositiveIntegerField(db_index=True, verbose_name=u'仕掛けたユーザID')
    oid = models.PositiveIntegerField(db_index=True, verbose_name=u'仕掛けられたユーザID')
    ctime = AppDateTimeField(db_index=True, default=OSAUtil.get_now, verbose_name=u'バトルを行った時間')
    result = models.SmallIntegerField(verbose_name=u'バトル結果')
    levelupcard = ObjectField(default=dict, verbose_name=u'レベルアップしたカード')
    data = ObjectField(default=dict, verbose_name=u'結果データ')
    anim = ObjectField(default=dict, verbose_name=u'演出データ')

class BattlePlayer(BaseModel):
    """プレイヤーのPVP情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    result = PositiveBigIntegerField(default=0, verbose_name=u'前回の結果ID')
    rank = models.PositiveIntegerField(default=1, verbose_name=u'ランク')
    win_continuity = models.PositiveSmallIntegerField(default=0, verbose_name=u'連勝数')
    times = models.PositiveSmallIntegerField(default=0, verbose_name=u'ノルマ達成回数')
    opponent = models.PositiveIntegerField(default=0, verbose_name=u'対戦相手')
    change_cnt = TinyIntField(default=0, verbose_name=u'対戦相手変更回数')
    rankopplist = ObjectField(default=list, verbose_name=u'同じランクで戦ったことのある相手')
    lpvtime = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'ランディングページを見た時間')

class BattleWin(BaseModel):
    """挑んだ時の勝利数.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    win = models.PositiveIntegerField(default=0, verbose_name=u'勝利数')

class BattleLose(BaseModel):
    """挑んだ時の敗北数.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    lose = models.PositiveIntegerField(default=0, verbose_name=u'敗北数')

class BattleReceiveWin(BaseModel):
    """挑まれた時の勝利数.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    win = models.PositiveIntegerField(default=0, verbose_name=u'勝利数')

class BattleReceiveLose(BaseModel):
    """挑まれた時の敗北数.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    lose = models.PositiveIntegerField(default=0, verbose_name=u'敗北数')

class BattleRankMaster(BaseMaster):
    """ランク.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    region = models.CharField(max_length=48, verbose_name=u'地名', default='')
    town = models.CharField(max_length=48, verbose_name=u'街名', default='')
    text = models.TextField(verbose_name=u'テキスト', default='')
    thumb = models.CharField(max_length=48, verbose_name=u'サムネイル', default='')
    win = models.PositiveSmallIntegerField(default=1, verbose_name=u'次のランクになるための連勝ノルマ')
    times = models.PositiveSmallIntegerField(default=1, verbose_name=u'次のランクになるためのノルマ達成回数')
    bpcost = TinyIntField(default=0, verbose_name=u'このランクでの気力消費量')
    winprizes = JsonCharField(default=list, verbose_name=u'ランクアップ戦を除く勝利報酬')
    loseprizes = JsonCharField(default=list, verbose_name=u'敗北報酬')
    rankupprizes = JsonCharField(default=list, verbose_name=u'ランクアップ戦報酬', help_text=u'次のランクになるためのランクアップ戦の勝利報酬')
    goldkeyrate_base = models.PositiveSmallIntegerField(default=0, verbose_name=u'金の鍵の出現率の基本値')
    goldkeyrate_up = models.PositiveSmallIntegerField(default=10, verbose_name=u'金の鍵の出現率の上昇値')
    silverkeyrate = models.PositiveSmallIntegerField(default=0, verbose_name=u'銀の鍵の出現率')
    
    class PrizeData:
        def __init__(self, data):
            self.prizes = data.get('prizes') or []
            self.rate = max(0, int(data.get('rate')) or 0)
            if not self.prizes:
                raise CabaretError(u'報酬が空です', CabaretError.Code.INVALID_MASTERDATA)
    
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
            raise CabaretError(u'報酬が設定されていません', CabaretError.Code.INVALID_MASTERDATA)
        
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
        return BattleRankMaster.select(self.winprizes, rand)
    
    def select_loseprize(self, rand=None):
        """敗北報酬を選択.
        """
        return BattleRankMaster.select(self.loseprizes, rand)
    
    def select_rankupprize(self, rand=None):
        """ランクアップ報酬を選択.
        """
        return BattleRankMaster.select(self.rankupprizes, rand)
    

