# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.Player import BasePerPlayerBase, BasePerPlayerBaseWithMasterID
from defines import Defines
from platinumegg.app.cabaret.models.base.models import BaseMaster
from platinumegg.app.cabaret.models.base.fields import JsonCharField

class LevelUpBonusMaster(BaseMaster):
    """アイテムのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'ID')
    version = models.PositiveSmallIntegerField(default=0, verbose_name=u'バージョン番号')
    level = models.PositiveSmallIntegerField(default=0, verbose_name=u'到達レベル')
    prize_id = JsonCharField(default=list, verbose_name=u'プライズIDのリスト')
    levelupbonus_text = models.PositiveIntegerField(default=0, verbose_name=u'レベルアップ達成ボーナス報酬文言')

class LevelUpBonusPlayerData(BasePerPlayerBaseWithMasterID):
    """レベルアップ達成ボーナスのプレイヤー情報.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME
    last_prize_level = models.PositiveIntegerField(default=0, verbose_name=u'最後に達成したレベル')

    @staticmethod
    def makeID(uid, version):
        return (uid << 32) + version

    @classmethod
    def createInstance(cls, key):
        ins = cls()
        ins.id = key
        ins.uid = (key >> 32)
        ins.mid = key & 0xffffffff
        ins.last_prize_level = 0
        return ins
