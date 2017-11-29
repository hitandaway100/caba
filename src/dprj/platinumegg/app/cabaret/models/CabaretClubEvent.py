# -*- coding: utf-8 -*-
from django.db import models

from platinumegg.app.cabaret.models.base.fields import AppDateTimeField
from platinumegg.app.cabaret.models.base.fields import JsonCharField
from platinumegg.app.cabaret.models.base.models import BaseMaster, BaseModel
from platinumegg.app.cabaret.models.base.models import Singleton
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.fields import PositiveBigIntegerField
import settings_sub


class CabaClubRankEventMaster(BaseMaster):
    """経営イベントのマスターデータ"""

    class Meta(object):
        app_label = settings_sub.APP_NAME
        abstract = False

    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'イベントタイトル')
    subname = models.CharField(max_length=64, blank=True, verbose_name=u'イベントサブタイトル')
    htmlname = models.CharField(max_length=48, verbose_name=u'HTMLディレクトリ名')
    rankingprizes = JsonCharField(default=list, verbose_name=u'ランキング報酬')
    rankingprize_text = models.PositiveIntegerField(verbose_name=u'ランキング報酬文言')

    @property
    def codename(self):
        return self.htmlname.split('/')[-1]

class CurrentCabaClubRankEventConfig(Singleton):
    """開催中または開催予定の経営イベント."""

    class Meta(object):
        app_label = settings_sub.APP_NAME
        abstract = False

    mid = models.PositiveIntegerField(default=0, verbose_name=u'イベントのマスターID')
    starttime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'開始時間')
    endtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'終了時間')
    next_starttime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'次回開始時間')
    next_endtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'次回終了時間')
    prize_flag = models.PositiveIntegerField(default=0, verbose_name=u'ランキング報酬配布フラグ')
    previous_mid = models.PositiveIntegerField(default=0, verbose_name=u'前回のイベントのマスターID')

class CabaClubEventRankMaster(BaseModel):
    """経営イベントのプレーヤーのランク情報
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID((ユーザID<<32)+イベントID(mid)')
    uid = models.PositiveIntegerField(db_index=True, verbose_name=u'ユーザID')
    mid = models.PositiveIntegerField(verbose_name=u'経営イベントID')
    proceeds = models.PositiveIntegerField(default=0, verbose_name=u'プレーヤーの総売上')
    today_proceeds = models.PositiveIntegerField(default=0, verbose_name=u'プレーヤーの本日の総売上')

    @classmethod
    def makeID(cls, uid, mid):
        return (uid << 32) + mid

    @classmethod
    def createInstance(cls, key, uid):
        ins = CabaClubEventRankMaster.makeInstance(key)
        ins.uid = uid
        ins.mid = key & 0xfffffff
        return ins
