# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster


class GachaExplainMaster(BaseMaster):
    """ガチャの説明テキストのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    explain_text = models.TextField(default='', verbose_name=u'ガチャの説明テキスト', blank=True)
