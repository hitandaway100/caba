# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.fields import JsonCharField,\
    AppDateTimeField
from defines import Defines
from platinumegg.app.cabaret.models.base.util import dict_to_choices

def numberitems(nummin, nummax):
    result = {}
    for i in range(nummin, nummax):
        result[i] = i
    return result.items()

class ScheduleMaster(BaseMaster):
    """スケジュール.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    stime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'公開開始時間')
    etime = AppDateTimeField(db_index=True, default=OSAUtil.get_now, verbose_name=u'公開終了時間')
    wday = models.PositiveSmallIntegerField(default=Defines.WeekDay.ALL, verbose_name=u'曜日指定', choices=dict_to_choices(Defines.WeekDay.NAMES))
    shour = models.PositiveSmallIntegerField(default=0, verbose_name=u'日毎の開始時間(時)', choices=numberitems(0, 24))
    sminute = models.PositiveSmallIntegerField(default=0, verbose_name=u'日毎の開始時間(分)', choices=numberitems(0, 60))
    timelimit = models.PositiveSmallIntegerField(default=0, verbose_name=u'日毎の制限時間(分)')
    target = JsonCharField(default=list, verbose_name=u'対象のユーザID下一桁')
