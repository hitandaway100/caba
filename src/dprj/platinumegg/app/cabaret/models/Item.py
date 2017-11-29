# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMasterWithThumbnail
from platinumegg.app.cabaret.models.Player import BasePerPlayerBase
from defines import Defines
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class ItemMaster(BaseMasterWithThumbnail):
    """アイテムのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'ID', choices=dict_to_choices(Defines.ItemEffect.NAMES))
    evalue = models.PositiveSmallIntegerField(default=0, verbose_name=u'効果の値')
    unit = models.CharField(max_length=16, verbose_name=u'単位', default=u'')
    pri = models.PositiveSmallIntegerField(default=0, verbose_name=u'優先順位')

class Item(BasePerPlayerBase):
    """アイテムの所持数.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    mid = models.PositiveSmallIntegerField(db_index=True, verbose_name=u'マスターデータID')
    rnum = models.PositiveIntegerField(default=0, verbose_name=u'所持数(課金)')
    vnum = models.PositiveIntegerField(default=0, verbose_name=u'所持数(プレゼント等)')
    
    @property
    def num(self):
        return self.rnum + self.vnum
    
