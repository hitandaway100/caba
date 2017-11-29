# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMasterWithThumbnail
from platinumegg.app.cabaret.models.base.fields import ObjectField,\
    JsonCharField
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.apprandom import AppRandom

class ScoutMaster(BaseMasterWithThumbnail):
    """スカウトのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    area = models.PositiveIntegerField(db_index=True, verbose_name=u'エリア')
    opencondition = models.PositiveIntegerField(db_index=True, default=0, verbose_name=u'開放条件(スカウトクリア) 0で常時開放')
    execution = models.PositiveSmallIntegerField(default=1, verbose_name=u'クリアまでのポチポチ回数')
    apcost = models.PositiveSmallIntegerField(default=0, verbose_name=u'消費体力')
    exp = models.PositiveIntegerField(default=0, verbose_name=u'獲得経験値')
    goldmin = models.PositiveIntegerField(default=0, verbose_name=u'獲得ポケットマネー最小値')
    goldmax = models.PositiveIntegerField(default=0, verbose_name=u'獲得ポケットマネー最大値')
    
    eventrate_drop = models.PositiveSmallIntegerField(default=0, verbose_name=u'カード発見発生率')
    eventrate_happening = models.PositiveSmallIntegerField(default=0, verbose_name=u'ハプニング発生率')
    eventrate_treasure = models.PositiveSmallIntegerField(default=0, verbose_name=u'宝箱発見発生率')
    
    dropitems = JsonCharField(default=list, verbose_name=u'カード出現テーブル')
    happenings = JsonCharField(default=list, verbose_name=u'発生するハプニング')
    treasuregold = models.PositiveSmallIntegerField(default=0, verbose_name=u'金の宝箱出現率')
    treasuresilver = models.PositiveSmallIntegerField(default=0, verbose_name=u'銀の宝箱出現率')
    treasurebronze = models.PositiveSmallIntegerField(default=0, verbose_name=u'銅の宝箱出現率')

class ScoutPlayData(BasePerPlayerBaseWithMasterID):
    """スカウトの進行情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    progress = models.PositiveIntegerField(default=0, verbose_name=u'実行回数(進行度)')
    seed = models.PositiveIntegerField(default=AppRandom.makeSeed, verbose_name=u'乱数シード')
    dropitems = ObjectField(default=list, verbose_name=u'獲得したカード・トロフィー')
    confirmkey = models.CharField(max_length=20, default=OSAUtil.makeSessionID, verbose_name=u'重複確認用のキー')
    alreadykey = models.CharField(max_length=20, default='', verbose_name=u'重複確認用のキー')
    result = ObjectField(default=dict, verbose_name=u'前回の実行結果')
    
    @staticmethod
    def makeDropItemName(itype, mid):
        return (itype << 32) + mid
    
    def addDropItem(self, itype, mid):
        """ドロップアイテムを追加.
        """
        self.dropitems.append(ScoutPlayData.makeDropItemName(itype, mid))
        self.dropitems = list(set(self.dropitems))
    
    def idDropped(self, itype, mid):
        """ドロップしたことあるか.
        """
        return self.dropitems and ScoutPlayData.makeDropItemName(itype, mid) in self.dropitems
    
    def setResult(self, result, eventlist, champagnecall_started=False):
        self.result = {
            'result' : result,
            'event' : eventlist,
        }
        if champagnecall_started:
            self.result.update(champagne=1)
    
