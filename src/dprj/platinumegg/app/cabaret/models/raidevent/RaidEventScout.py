# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.EventScout import EventScoutPlayData,\
    EventScoutStageMaster
import settings_sub
from platinumegg.app.cabaret.models.base.fields import JsonCharField

class RaidEventScoutStageMaster(EventScoutStageMaster):
    """イベントスカウトのステージマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    happenings_timebonus = JsonCharField(default=list, verbose_name=u'レイド出現テーブル(タイムボーナス)')
    happenings_big = JsonCharField(default=list, verbose_name=u'大ボス出現後レイド出現テーブル')
    happenings_timebonus_big = JsonCharField(default=list, verbose_name=u'大ボス出現後レイド出現テーブル(タイムボーナス)')

class RaidEventScoutPlayData(EventScoutPlayData):
    """イベントスカウトの進行情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def setResult(self, result, eventlist, flag_earlybonus=False, champagnecall_started=False):
        self._setResult(result, eventlist, flag_earlybonus)
        if champagnecall_started:
            self.result.update(champagne=1)
