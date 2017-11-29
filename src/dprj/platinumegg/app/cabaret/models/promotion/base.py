# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMasterWithName,\
    Singleton
from platinumegg.app.cabaret.models.base.fields import JsonCharField,\
    AppDateTimeField
from defines import Defines
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class PromotionConfigBase(Singleton):
    """クロスプロモーション設定マスターデータ.
    """
    class Meta:
        abstract = True
        app_label = settings_sub.APP_NAME
    schedule = models.PositiveIntegerField(default=0, verbose_name=u'スケジュール')
    name = models.CharField(max_length=48, verbose_name=u'アプリ名')
    htmlname = models.CharField(max_length=48, verbose_name=u'HTMLディレクトリ名')
    appurl_sp = models.TextField(blank=True, default='', verbose_name=u'SP版アプリURL')
    appurl_sp_stg = models.TextField(blank=True, default='', verbose_name=u'SP版ステージングURL')
    appurl_sp_sandbox = models.TextField(blank=True, default='', verbose_name=u'SP版サンドボックスURL')
    appurl_pc = models.TextField(blank=True, default='', verbose_name=u'PC版アプリURL')
    appurl_pc_stg = models.TextField(blank=True, default='', verbose_name=u'PC版ステージングURL')
    appurl_pc_sandbox = models.TextField(blank=True, default='', verbose_name=u'PC版サンドボックスURL')

class PromotionPrizeMasterBase(BaseMasterWithName):
    """クロスプロモーション報酬マスターデータ.
    """
    class Meta:
        abstract = True
        app_label = settings_sub.APP_NAME
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    rid = models.PositiveIntegerField(default=0, verbose_name=u'条件ID')
    schedule = models.PositiveIntegerField(default=0, verbose_name=u'スケジュール')
    prizes = JsonCharField(default=list, verbose_name=u'報酬')
    prize_text = models.PositiveIntegerField(default=0, verbose_name=u'報酬テキストID')

class PromotionRequirementMasterBase(BaseMasterWithName):
    """クロスプロモーション条件マスターデータ.
    """
    class Meta:
        abstract = True
        app_label = settings_sub.APP_NAME
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    condition_type = models.PositiveIntegerField(default=Defines.PromotionRequirementType.LEVEL, choices=dict_to_choices(Defines.PromotionRequirementType.NAMES), verbose_name=u'達成条件タイプ')
    condition_value = models.PositiveIntegerField(default=0, verbose_name=u'達成条件の値')

class PromotionDataBase(BasePerPlayerBaseWithMasterID):
    """クロスプロモーション達成データ.
    """
    class Meta:
        abstract = True
        app_label = settings_sub.APP_NAME
    
    status = models.PositiveSmallIntegerField(default=Defines.PromotionStatus.NONE, choices=dict_to_choices(Defines.PromotionStatus.NAMES), verbose_name=u'達成状態')
    atime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'達成した時間')
    rtime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'受け取った時間')
