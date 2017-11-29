# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster


class ScenarioMaster(BaseMaster):
    """イベントシナリオ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    number = models.PositiveIntegerField(db_index=True, verbose_name=u'シナリオ番号')
    name = models.CharField(max_length=48, verbose_name=u'名前')
    cast_l = models.CharField(max_length=48, verbose_name=u'左側のキャスト画像', blank=True)
    cast_c = models.CharField(max_length=48, verbose_name=u'中央のキャスト画像', blank=True)
    cast_r = models.CharField(max_length=48, verbose_name=u'右側のキャスト画像', blank=True)
    bg = models.CharField(max_length=48, verbose_name=u'背景画像')
    text_name = models.CharField(max_length=255, verbose_name=u'テキスト(名前)', blank=True)
    text_body = models.CharField(max_length=255, verbose_name=u'テキスト(本文)', blank=True)
    wait = models.PositiveSmallIntegerField(default=0, verbose_name=u'待ちフレーム数')
    touch = models.BooleanField(default=False, verbose_name=u'タッチ待ちフラグ')
    window = models.BooleanField(default=True, verbose_name=u'テキストウィンドウ表示')
    fadeouttime = models.PositiveSmallIntegerField(default=0, verbose_name=u'フェードアウトフレーム数')
    fadeintime = models.PositiveSmallIntegerField(default=0, verbose_name=u'フェードインフレーム数')
    thumb = models.CharField(default='', max_length=96, verbose_name=u'画像の場所', blank=True)
