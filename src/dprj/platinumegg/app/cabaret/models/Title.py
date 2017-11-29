# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMasterWithThumbnail, BaseModel
from platinumegg.app.cabaret.models.base.fields import AppDateTimeField
from platinumegg.lib.opensocial.util import OSAUtil

class TitleMaster(BaseMasterWithThumbnail):
    """称号のマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    days = models.PositiveIntegerField(default=0, verbose_name=u'獲得後の有効期間(日)')
    cost = models.PositiveIntegerField(default=0, verbose_name=u'消費名誉ポイント')
    gold_up = models.SmallIntegerField(default=0, verbose_name=u'獲得CG補正(％)')
    exp_up = models.SmallIntegerField(default=0, verbose_name=u'獲得経験値補正(％)')
    raidevent_point_up = models.SmallIntegerField(default=0, verbose_name=u'レイドイベントの特効獲得ポイント補正(％)')
    raidevent_power_up = models.SmallIntegerField(default=0, verbose_name=u'レイドイベントの特効接客力補正(％)')
    scoutevent_point_up = models.SmallIntegerField(default=0, verbose_name=u'スカウトイベントの特効獲得ポイント補正(％)')
    battleevent_point_up = models.SmallIntegerField(default=0, verbose_name=u'バトルイベントの特効獲得ポイント補正(％)')
    battleevent_power_up = models.SmallIntegerField(default=0, verbose_name=u'バトルイベントの特効接客力補正(％)')
    priority = models.PositiveSmallIntegerField(default=0, verbose_name=u'交換所での優先順位')

class TitlePlayerData(BaseModel):
    """称号のプレイヤーデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    title = models.PositiveIntegerField(default=0, verbose_name=u'称号マスターID')
    stime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'称号獲得時間')
