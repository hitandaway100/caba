# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster, Singleton
from defines import Defines
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID
from platinumegg.app.cabaret.models.base.fields import AppDateTimeField
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class TradeMaster(BaseMaster):
    """秘宝交換マスターデータ.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    itype = models.PositiveSmallIntegerField(verbose_name=u'種別(アイテム or チケット)', choices=dict_to_choices(Defines.ItemType.TRADE_TYPES))
    itemid = models.PositiveIntegerField(default=0, verbose_name=u'アイテムID')
    itemnum = models.PositiveIntegerField(default=0, verbose_name=u'アイテム個数')
    rate_cabaretking = models.PositiveIntegerField(default=0, verbose_name=u'レート(キャバ王の秘宝 or プラチナの欠片 or バトルチケット or クリスタルの欠片)')
    rate_demiworld = models.PositiveIntegerField(default=0, verbose_name=u'レート(裏社会の秘宝)[未使用]')
    schedule = models.PositiveIntegerField(default=0, verbose_name=u'スケジュール')
    stock = models.PositiveIntegerField(default=0, verbose_name=u'在庫数')
    reset_stock_monthly = models.BooleanField(default=False, verbose_name=u'月初に在庫数をリセットするフラグ')
    slidecapture = models.TextField(default='', verbose_name=u'画面上部でスライド表示させるキャプチャ画像(カード限定)', blank=True)
    header = models.TextField(default='', verbose_name=u'画面上部のヘッダ画像', blank=True)
    is_used_platinum_piece = models.BooleanField(default=False, verbose_name=u'交換にプラチナの欠片を使うか否か')
    is_used_battle_ticket = models.BooleanField(default=False, verbose_name=u'交換にバトルチケットを使うか否か')
    is_used_crystal_piece = models.BooleanField(default=False, verbose_name=u'交換にクリスタルの欠片を使うか否か')
class TradeResetTime(Singleton):
    """秘宝交換リセット時間.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME
    resettime = AppDateTimeField(default=OSAUtil.get_datetime_min(), verbose_name=u'リセット予定時間')

class TradePlayerData(BasePerPlayerBaseWithMasterID):
    """秘宝交換のプレイヤー情報.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME
    cnt = models.PositiveIntegerField(default=0, verbose_name=u'期間中交換回数')
    ltime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'最後に交換した時間')
