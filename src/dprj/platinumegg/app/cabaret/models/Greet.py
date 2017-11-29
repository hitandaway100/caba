# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseModel
from platinumegg.app.cabaret.models.base.fields import PositiveBigAutoField,\
    AppDateTimeField
from platinumegg.lib.opensocial.util import OSAUtil
from django.db.models.fields import BigIntegerField
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil

class GreetLog(BaseModel):
    """あいさつ履歴.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    fromid = models.PositiveIntegerField(db_index=True, verbose_name=u'あいさつしたユーザID')
    toid = models.PositiveIntegerField(db_index=True, verbose_name=u'あいさつされたユーザID')
    gtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'あいさつした時間')
    commenttextid = models.CharField(max_length=64, verbose_name=u'コメントTEXTID', default='')

class GreetData(BaseModel):
    """あいさつ情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    FIXED_COLUMNS = (
        'fromid','toid'
    )
    
    id = BigIntegerField(primary_key=True, verbose_name=u'ID((ユーザID<<32)+相手のID)')
    fromid = models.PositiveIntegerField(db_index=True, verbose_name=u'あいさつしたユーザID')
    toid = models.PositiveIntegerField(db_index=True, verbose_name=u'あいさつされたユーザID')
    ltime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'最後にあいさつした時間')
    
    @classmethod
    def makeID(cls, uid, oid):
        return (uid << 32) + oid
    
    @classmethod
    def makeInstance(cls, key):
        ins = cls()
        ins.id = key
        ins.fromid = (key >> 32)
        ins.toid = (key & 0xffffffff)
        return ins

class GreetPlayerData(BaseModel):
    """プレイヤーのあいさつ情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    ltime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'最後にあいさつした時間')
    today = models.PositiveSmallIntegerField(default=0, verbose_name=u'本日あいさつ回数')
    yesterday = models.PositiveSmallIntegerField(default=0, verbose_name=u'前日あいさつ回数')
    total = models.PositiveIntegerField(default=0, verbose_name=u'総あいさつ回数')
    
    def getTodayCount(self):
        """今日の挨拶回数を取得.
        """
        now = OSAUtil.get_now()
        if DateTimeUtil.judgeSameDays(self.ltime, now):
            return self.today
        else:
            return 0
    
    def addCount(self, cnt=1):
        """あいさつ回数を加算.
        """
        now = OSAUtil.get_now()
        if not DateTimeUtil.judgeSameDays(self.ltime, now):
            self.yesterday = self.today
            self.today = 0
        self.today += cnt
        self.total += cnt
        self.ltime = now
