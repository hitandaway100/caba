# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMasterWithThumbnail
from platinumegg.app.cabaret.models.base.fields import ObjectField,\
    JsonCharField, AppDateTimeField
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.apprandom import AppRandom

class EventScoutStageMaster(BaseMasterWithThumbnail):
    """イベント用スカウトのステージマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = True
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    eventid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントマスターID')
    stage = models.PositiveIntegerField(verbose_name=u'ステージ番号')
    area = models.PositiveIntegerField(verbose_name=u'エリア番号')
    areaname = models.CharField(max_length=48, verbose_name=u'エリア名')
    prizes = JsonCharField(default=list, verbose_name=u'クリア報酬')
    boss = models.PositiveIntegerField(verbose_name=u'ボスID')
    bossprizes = JsonCharField(default=list, verbose_name=u'ボス撃破報酬')
    bossscenario = models.PositiveIntegerField(default=0, verbose_name=u'ボス撃破時に再生するシナリオ')
    girls = JsonCharField(default=list, verbose_name=u'出現する女性')
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
    
    earlybonus = JsonCharField(default=list, verbose_name=u'早期クリアボーナス', help_text=u'次のエリアが公開されていない時にクリア時に付与されるプレゼント')
    earlybonus_text = models.PositiveIntegerField(default=0, verbose_name=u'早期クリアボーナス報酬文言')

class EventScoutPlayData(BasePerPlayerBaseWithMasterID):
    """イベント用スカウトのスカウトイベントの進行情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = True
    stage = models.PositiveIntegerField(default=0, verbose_name=u'現在のステージ番号')
    cleared = models.PositiveIntegerField(default=0, verbose_name=u'クリア済みのステージ番号')
    progress = models.PositiveIntegerField(default=0, verbose_name=u'ステージ実行回数(進行度)')
    seed = models.PositiveIntegerField(default=AppRandom.makeSeed, verbose_name=u'乱数シード')
    confirmkey = models.CharField(max_length=20, default=OSAUtil.makeSessionID, verbose_name=u'重複確認用のキー')
    alreadykey = models.CharField(max_length=20, default='', verbose_name=u'重複確認用のキー')
    result = ObjectField(default=dict, verbose_name=u'前回の実行結果')
    ptime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'最終プレイ時間')
    
    def _setResult(self, result, eventlist, flag_earlybonus=False):
        self.result = {
            'result' : result,
            'event' : eventlist,
            'earlybonus' : flag_earlybonus,
        }
