# *-* coding: utf-8 *-*

import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster

class NgCastMaster(BaseMaster):
    """
        This table contains the id and names of cast that are no longer in use.
        Casts can be no longer in use, if they stopped or retire from their "work"
        Trivia:
                NG = No Good (駄目）
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=128, verbose_name=u'キャスト名', blank=False)
    flag = models.BooleanField(default=True, verbose_name="NGキャストのチェックを無効")
