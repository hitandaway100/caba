# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID
from platinumegg.app.cabaret.models.base.fields import JsonCharField,\
    AppDateTimeField
from platinumegg.lib.opensocial.util import OSAUtil
import datetime
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil


class PresentEveryoneBase(BaseMaster):
    """全プレのベース.
    """
    class Meta:
        abstract = True
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'名前', help_text=u'アプリでは使用しません')
    prizes = JsonCharField(default=list, verbose_name=u'配付するもの')
    textid = models.PositiveIntegerField(verbose_name=u'プレゼントの文言')

class PresentEveryoneLoginBonusMaster(PresentEveryoneBase):
    """ログインボーナス時に配付する全プレ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    prizes_daily = JsonCharField(default=dict, verbose_name=u'日別に配付するもの', help_text=u'{"日数":[報酬ID,...],...}という形式で')
    s_date = models.DateField(default=datetime.date.today, verbose_name=u'配布開始日')
    e_date = models.DateField(default=datetime.date.today, verbose_name=u'配布終了日', db_index=True)
    everyday = models.BooleanField(default=False, verbose_name=u'期間中毎日配布フラグ', help_text=u'フラグが立っているときは毎日配布します')
    
    @property
    def s_time(self):
        return DateTimeUtil.toLoginTime(DateTimeUtil.dateToDateTime(self.s_date))
    
    @property
    def e_time(self):
        return DateTimeUtil.toLoginTime(DateTimeUtil.dateToDateTime(self.e_date))

class PresentEveryoneMypageMaster(PresentEveryoneBase):
    """マイページで配付する全プレ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    schedule = models.PositiveIntegerField(verbose_name=u'期間', db_index=True)

class PresentEveryoneRecord(BaseMaster):
    """実際に配付する全プレレコード.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    date = models.DateField(primary_key=True, verbose_name=u'配布日')
    mid_loginbonus = JsonCharField(default=list, verbose_name=u'全プレ(LB)のIDリスト')
    mid_mypage = JsonCharField(default=list, verbose_name=u'全プレ(マイページ)のIDリスト')
    
    @classmethod
    def pkey_to_str(cls, pkey):
        return pkey.strftime("%Y-%m-%d")
    
    @classmethod
    def str_to_pkey(cls, st):
        return DateTimeUtil.datetimeToDate(DateTimeUtil.strToDateTime(st, dtformat="%Y-%m-%d"), logintime=False)
    

class PresentEveryoneReceiveBase(BasePerPlayerBaseWithMasterID):
    """全プレ受け取り情報.
    """
    class Meta:
        abstract = True
    rtime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'最後に受け取った時間')
    cnt = models.PositiveSmallIntegerField(default=0, verbose_name=u'受け取った回数')

class PresentEveryoneReceiveLoginBonus(PresentEveryoneReceiveBase):
    """ログインボーナスの全プレ受け取り情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class PresentEveryoneReceiveMypage(PresentEveryoneReceiveBase):
    """マイページの全プレ受け取り情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

