# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.models import BaseMasterWithThumbnail
from platinumegg.app.cabaret.models.base.fields import JsonCharField,\
    AppDateTimeField
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID

class AreaMaster(BaseMasterWithThumbnail):
    """エリアのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    opencondition = models.PositiveIntegerField(default=0, verbose_name=u'開放条件(エリアクリア)')
    schedule = models.PositiveIntegerField(default=0, verbose_name=u'開放期間')
    boss = models.PositiveIntegerField(verbose_name=u'ボスID')
    prizes = JsonCharField(default=list, verbose_name=u'クリア報酬')
    girls = JsonCharField(default=list, verbose_name=u'出現する女性')

class AreaPlayData(BasePerPlayerBaseWithMasterID):
    """エリアのプレイ情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'クリア時間')
    clevel = models.PositiveIntegerField(default=0, verbose_name=u'クリア時のレベル')
