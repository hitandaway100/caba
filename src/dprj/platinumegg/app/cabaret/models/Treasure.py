# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseModel, BaseMaster
from platinumegg.app.cabaret.models.base.fields import PositiveBigAutoField,\
    AppDateTimeField, JsonCharField
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.models.base.util import dict_to_choices

class BaseTreasureTable(BaseMaster):
    """宝箱テーブル.
    """
    class Meta:
        abstract = True
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'テーブル名', help_text=u'アプリでは使用しません')
    thumb = models.CharField(max_length=48, verbose_name=u'宝箱Top画像')
    schedule = models.PositiveIntegerField(default=0, verbose_name=u'期間')
    table = JsonCharField(default=list, verbose_name=u'出現する宝箱')

class BaseTreasureMaster(BaseMaster):
    """宝箱マスターデータ.
    """
    class Meta:
        abstract = True
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    itype = models.PositiveSmallIntegerField(db_index=True, verbose_name=u'中身の種別', choices=dict_to_choices(Defines.ItemType.TREASURE_ITEM_TYPES))
    ivalue1 = models.PositiveIntegerField(default=0, verbose_name=u'アイテムID')
    ivalue2 = models.PositiveIntegerField(default=1, verbose_name=u'個数,金額')
    probability = models.PositiveIntegerField(default=0, verbose_name=u'確率')
    priority = models.PositiveSmallIntegerField(default=0, verbose_name=u'優先度')

class BaseTreasure(BaseModel):
    """宝箱.
    """
    class Meta:
        abstract = True
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    uid = models.PositiveIntegerField(verbose_name=u'ユーザID')
    mid = models.PositiveIntegerField(verbose_name=u'マスターID')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'獲得時間')
    etime = AppDateTimeField(db_index=True, default=OSAUtil.get_now, verbose_name=u'受取終了時間')

class BaseTreasureNotOpened(BaseTreasure):
    """宝箱(未開封).
    """
    class Meta:
        abstract = True

class BaseTreasureOpened(BaseTreasure):
    """宝箱プレイ情報.
    """
    class Meta:
        abstract = True
    otime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'開封した時間')

#====================================================
# 金.
class TreasureTableGoldMaster(BaseTreasureTable):
    """宝箱(金)の出現テーブル.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class TreasureGoldMaster(BaseTreasureMaster):
    """宝箱(金)マスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class TreasureGold(BaseTreasureNotOpened):
    """宝箱(金)情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class TreasureGoldOpened(BaseTreasure):
    """開封済み宝箱(金)情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    otime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'開封した時間')

#====================================================
# 銀.
class TreasureTableSilverMaster(BaseTreasureTable):
    """宝箱(銀)の出現テーブル.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class TreasureSilverMaster(BaseTreasureMaster):
    """宝箱(銀)マスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class TreasureSilver(BaseTreasureNotOpened):
    """宝箱(銀)情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class TreasureSilverOpened(BaseTreasure):
    """開封済み宝箱(銀).
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    otime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'開封した時間')

#====================================================
# 銅.
class TreasureTableBronzeMaster(BaseTreasureTable):
    """宝箱(銅)の出現テーブル.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class TreasureBronzeMaster(BaseTreasureMaster):
    """宝箱(銅)マスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class TreasureBronze(BaseTreasureNotOpened):
    """宝箱(銅)情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class TreasureBronzeOpened(BaseTreasure):
    """開封済み宝箱(銅).
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    otime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'開封した時間')

