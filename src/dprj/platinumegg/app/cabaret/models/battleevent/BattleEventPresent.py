# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMasterWithThumbnail
from platinumegg.app.cabaret.models.base.fields import PositiveBigIntegerField,\
    JsonCharField
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID

class BattleEventPresentMaster(BaseMasterWithThumbnail):
    """バトルイベントのポイントプレゼントのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    eventid = models.PositiveIntegerField(db_index=True, verbose_name=u'バトルイベントマスターID')
    number = models.PositiveSmallIntegerField(verbose_name=u'通し番号')
    contents = JsonCharField(default=list, verbose_name=u'中身のリスト', help_text=u'[[battleeventpresentcontentmasterのID,odds],...]')
    point = models.PositiveIntegerField(default=0, verbose_name=u'必要ポイント')
    rate = models.PositiveSmallIntegerField(default=0, verbose_name=u'出現率')
    specialnum0 = models.PositiveSmallIntegerField(default=0, verbose_name=u'特別な出現条件0の通し番号')
    specialcnt0 = models.PositiveSmallIntegerField(default=0, verbose_name=u'特別な出現条件0の個数')
    specialnum1 = models.PositiveSmallIntegerField(default=0, verbose_name=u'特別な出現条件1の通し番号')
    specialcnt1 = models.PositiveSmallIntegerField(default=0, verbose_name=u'特別な出現条件1の個数')
    
    @staticmethod
    def makeID(eventid, number):
        return (eventid << 32) + number
    
    @classmethod
    def makeInstance(cls, key):
        ins = cls()
        ins.id = key
        ins.eventid = int(key >> 32)
        ins.number = int(key & 0xffffffff)
        return ins
    
    CONDITION_NUM_MAX = 2
    def getConditionDict(self):
        dest = {}
        for idx in xrange(BattleEventPresentMaster.CONDITION_NUM_MAX):
            number = getattr(self, 'specialnum%d' % idx, 0)
            cnt = getattr(self, 'specialcnt%d' % idx, 0)
            if number and cnt:
                dest[number] = cnt
        return dest

class BattleEventPresentContentMaster(BaseMasterWithThumbnail):
    """バトルイベントのポイントプレゼントの中身マスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    prizes = JsonCharField(default=list, verbose_name=u'報酬IDのリスト')
    prize_text = models.PositiveIntegerField(default=0, verbose_name=u'報酬の文言')
    pri = models.PositiveSmallIntegerField(default=0, verbose_name=u'一覧表示の優先度')

class BattleEventPresentData(BasePerPlayerBaseWithMasterID):
    """バトルイベントのポイントプレゼントのユーザ情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    point = models.PositiveIntegerField(default=0, verbose_name=u'獲得ポイント')
    currentnum = models.PositiveSmallIntegerField(default=0, verbose_name=u'現在のプレゼントの通し番号')
    currentcontent = models.PositiveIntegerField(default=0, verbose_name=u'現在のプレゼントの中身')
    prenum = models.PositiveSmallIntegerField(default=0, verbose_name=u'前回のプレゼントの通し番号')
    precontent = models.PositiveIntegerField(default=0, verbose_name=u'前回のプレゼントの中身')
    
    def __getData(self, num_name, content_name):
        number = getattr(self, num_name)
        content = getattr(self, content_name)
        return dict(number=number, content=content) if number and content else None
    
    def getData(self):
        return self.__getData('currentnum', 'currentcontent')
    
    def getPreData(self):
        return self.__getData('prenum', 'precontent')

class BattleEventPresentCounts(BasePerPlayerBaseWithMasterID):
    """バトルイベントのポイントプレゼントの出現カウンタ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    cnt = models.PositiveSmallIntegerField(default=0, verbose_name=u'出現回数')


