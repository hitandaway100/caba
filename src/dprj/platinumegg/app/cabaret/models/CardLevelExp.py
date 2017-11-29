# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster


class CardLevelExpMster(BaseMaster):
    """カードの経験値.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    level = models.PositiveIntegerField(primary_key=True, verbose_name=u'レベル')
    exp = models.PositiveIntegerField(db_index=True, verbose_name=u'経験値')
