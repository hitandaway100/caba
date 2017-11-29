# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster


class PlayerLevelExpMaster(BaseMaster):
    """プレイヤーの経験値.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    level = models.PositiveIntegerField(primary_key=True, verbose_name=u'レベル')
    exp = models.PositiveIntegerField(db_index=True, default=0, verbose_name=u'経験値')
    ap = models.PositiveSmallIntegerField(default=10, verbose_name=u'体力最大値')
    hp = models.PositiveIntegerField(default=10, verbose_name=u'ボス戦用HP')
    deckcapacity = models.PositiveSmallIntegerField(default=10, verbose_name=u'デッキコスト上限')
    cardlimit = models.PositiveSmallIntegerField(default=10, verbose_name=u'カード所持数上限')
    friendlimit = models.PositiveSmallIntegerField(default=10, verbose_name=u'仲間上限')
