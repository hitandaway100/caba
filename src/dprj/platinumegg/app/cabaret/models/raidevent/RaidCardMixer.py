# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster, BaseModel
from platinumegg.app.cabaret.models.base.fields import PositiveBigIntegerField
from defines import Defines
from platinumegg.app.cabaret.models.base.util import dict_to_choices

class RaidEventRecipeMaster(BaseMaster):
    """キャスト交換のレシピ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'名前')
    thumb = models.CharField(max_length=128, verbose_name=u'サムネイル', blank=True)
    eventid = models.PositiveIntegerField(db_index=True, default=0, verbose_name=u'イベントID')
    itype = models.PositiveSmallIntegerField(verbose_name=u'種別(アイテム or チケット)', choices=dict_to_choices(Defines.ItemType.TRADE_TYPES))
    itemid = models.PositiveIntegerField(default=0, verbose_name=u'アイテムID')
    itemnum = models.PositiveIntegerField(default=0, verbose_name=u'アイテム個数')
    stock = models.PositiveSmallIntegerField(default=0, verbose_name=u'在庫数', help_text=u'0で無制限')
    materialnum0 = models.PositiveIntegerField(default=0, verbose_name=u'材料0の個数')
    materialnum1 = models.PositiveIntegerField(default=0, verbose_name=u'材料1の個数')
    materialnum2 = models.PositiveIntegerField(default=0, verbose_name=u'材料2の個数')
    pri = models.PositiveSmallIntegerField(default=0, verbose_name=u'並べるときの優先順位', help_text=u'0〜65535')
    
    def getMaterialNum(self, idx):
        return getattr(self, 'materialnum%d' % idx)

class RaidEventMaterialMaster(BaseMaster):
    """キャスト交換の素材アイテムマスター.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'名前')
    thumb = models.CharField(max_length=128, verbose_name=u'サムネイル', blank=True)
    unit = models.CharField(max_length=8, verbose_name=u'単位', default=u'個')

class RaidEventMixData(BaseModel):
    """キャスト交換のユーザデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID((ユーザID<<32)+レシピID')
    eventid = models.PositiveIntegerField(default=0, verbose_name=u'イベントID')
    cnt = models.PositiveIntegerField(default=0, verbose_name=u'交換回数')
    
    @staticmethod
    def makeID(uid, mid):
        return (uid << 32) + mid
    
    @property
    def uid(self):
        return self.id >> 32
    
    @property
    def mid(self):
        return self.id & 0xffffffff
    
    def getCount(self, eventid):
        """配合回数を取得.
        """
        return self.cnt if eventid == self.eventid else 0
    
    def setCount(self, eventid, cnt):
        """配合回数を取得.
        """
        self.eventid = eventid
        self.cnt = cnt
    
    def addCount(self, eventid, cnt=1):
        """配合回数を加算.
        """
        self.setCount(eventid, self.getCount(eventid) + cnt)
    
class RaidEventMaterialData(BaseModel):
    """キャスト交換の素材の所持数.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    eventid = models.PositiveIntegerField(default=0, verbose_name=u'イベントID')
    material0 = PositiveBigIntegerField(default=0, verbose_name=u'材料0の所持数')
    material1 = PositiveBigIntegerField(default=0, verbose_name=u'材料1の所持数')
    material2 = PositiveBigIntegerField(default=0, verbose_name=u'材料2の所持数')
    
    def __updateEventId(self, eventid):
        if eventid == self.eventid:
            return
        self.eventid = eventid
        for i in xrange(Defines.RAIDEVENT_MATERIAL_KIND_MAX):
            setattr(self, 'material%d' % i, 0)
    
    def getMaterialNum(self, eventid, material):
        """材料の所持数を取得.
        """
        self.__updateEventId(eventid)
        return getattr(self, 'material%d' % material, 0)
    
    def setMaterialNum(self, eventid, material, num):
        """材料の所持数を取得.
        """
        self.__updateEventId(eventid)
        num = min(num, Defines.VALUE_MAX)
        setattr(self, 'material%d' % material, num)
    
    def addMaterialNum(self, eventid, material, num):
        """材料の所持数を加算.
        """
        self.setMaterialNum(eventid, material, self.getMaterialNum(eventid, material) + num)
