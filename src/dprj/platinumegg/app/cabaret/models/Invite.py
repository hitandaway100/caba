# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseModel
from platinumegg.app.cabaret.models.Player import BasePerPlayerBase
from platinumegg.app.cabaret.models.base.models import BaseMasterWithName
from platinumegg.app.cabaret.models.base.fields import AppDateTimeField, JsonCharField
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class InviteMaster(BaseMasterWithName):
    """招待マスターデータ.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    prizes = JsonCharField(default=list, verbose_name=u'報酬')
    schedule = models.PositiveIntegerField(default=0, verbose_name=u'スケジュール')
    
    def get_prizes(self, count_min=1, count_max=None):
        def countfilter(table):
            keys = table.keys()
            for key in keys:
                if count_min <= key <= (count_max or count_min):
                    continue
                del table[key]
            return table
        
        prizes = self.prizes
        if isinstance(prizes, list):
            return countfilter(dict(prizes))
        elif not isinstance(prizes, dict):
            return {}
        
        table = countfilter(dict(prizes.get('normal') or []))
        repeat = prizes.get('repeat') or []
        
        for data in repeat:
            prize = data.get('prize')
            if not prize:
                continue
            
            d_min = max(1, data.get('min', 1))
            if count_max is None:
                d_max = d_min
            else:
                d_max = min(data.get('max', count_max), count_max)
            interval = max(1, data.get('interval', 1))
            
            d = d_min
            while d <= d_max:
                if count_min <= d:
                    arr = table[d] = table.get(d) or []
                    arr.extend(prize)
                d += interval
        return table

class Invite(BasePerPlayerBase):
    """招待.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'招待マスターID')
    cnt = models.PositiveIntegerField(default=0, verbose_name=u'招待回数')

class InviteData(BaseModel):
    """招待詳細.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.CharField(primary_key=True, max_length=16, verbose_name=u'ユーザID(DMM)')
    fid = models.PositiveIntegerField(db_index=True, verbose_name=u'誰から招待されたかユーザID')
    state = models.PositiveSmallIntegerField(verbose_name=u'状態', choices=dict_to_choices(Defines.InviteState.NAMES))
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'招待通知受信日時')


