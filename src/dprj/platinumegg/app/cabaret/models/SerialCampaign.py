# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster, BaseModel
from platinumegg.app.cabaret.models.base.fields import AppDateTimeField,\
    JsonCharField, PositiveBigAutoField
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID


class SerialCampaignMaster(BaseMaster):
    """シリアルコードキャンペーンのマスター.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'雑誌名')
    rtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'雑誌の発売日', help_text=u'表示用です.期間とは別です.')
    header = models.CharField(max_length=96, verbose_name=u'ヘッダ画像')
    schedule = models.PositiveIntegerField(default=0, verbose_name=u'入力可能期間')
    prizes = JsonCharField(default=list, verbose_name=u'報酬')
    prize_img = models.CharField(max_length=96, verbose_name=u'報酬画像')
    prize_text = models.PositiveIntegerField(default=0, verbose_name=u'報酬文言')
    limit_pp = models.PositiveIntegerField(default=0, verbose_name=u'入力回数制限', help_text=u'一人あたりの回数制限.0で無制限')
    share_serial = models.BooleanField(default=0, verbose_name=u'共有シリアルコードフラグ', help_text=u'共有シリアルコードを設定する場合はチェック.')

class SerialCode(BaseModel):
    """シリアルコード.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    serial = models.CharField(unique=True, max_length=20, verbose_name=u'シリアルコード')
    mid = models.PositiveIntegerField(default=0, verbose_name=u'マスターID')
    uid = models.PositiveIntegerField(default=0, verbose_name=u'入力したユーザー')
    itime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'入力した時間')
    is_pc = models.BooleanField(default=False, verbose_name=u'PC or SP')

class SerialCount(BasePerPlayerBaseWithMasterID):
    """シリアルコード入力回数.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    cnt = models.PositiveIntegerField(default=0, verbose_name=u'入力回数')

class ShareSerialLog(BaseModel):
    """共有シリアルコードの入力情報を記録.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    serial = models.CharField(max_length=20, verbose_name=u'シリアルコード')
    mid = models.PositiveIntegerField(default=0, verbose_name=u'マスターID')
    uid = models.PositiveIntegerField(default=0, verbose_name=u'入力したユーザー')
    itime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'入力した時間')
    is_pc = models.BooleanField(default=False, verbose_name=u'PC or SP')
    
    @classmethod
    def createBySerialCode(cls, serialcode):
        ins = cls()
        ins.serial = serialcode.serial
        ins.mid = serialcode.mid
        return ins
