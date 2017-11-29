# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseModel
from platinumegg.app.cabaret.models.base.fields import PositiveBigAutoField,\
    ObjectField, AppDateTimeField
from platinumegg.lib.opensocial.util import OSAUtil


class PlayerLog(BaseModel):
    """行動履歴.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = True
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    uid = models.PositiveIntegerField(db_index=True, verbose_name=u'作成したユーザーID')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'作成した時間')
    logtype = models.PositiveSmallIntegerField(verbose_name=u'種別')
    data = ObjectField(verbose_name=u'履歴情報')
