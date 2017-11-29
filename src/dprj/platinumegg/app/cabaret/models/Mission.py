# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster,\
    BaseModel
from platinumegg.app.cabaret.models.base.fields import JsonCharField,\
    AppDateTimeField
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Player import BasePerPlayerBase
from defines import Defines
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class PanelMissionPanelMaster(BaseMaster):
    """パネルミッションのパネル.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'名前')
    effectname = models.CharField(default='', max_length=64, verbose_name=u'演出名', blank=True)
    image = models.CharField(default='', max_length=96, verbose_name=u'達成時のパネル画像')
    header = models.CharField(default='', max_length=96, verbose_name=u'ヘッダ画像', blank=True)
    rule = models.CharField(default='', max_length=96, verbose_name=u'ルール画像', blank=True)
    prizes = JsonCharField(default=list, verbose_name=u'全達成報酬')
    prize_text = models.PositiveIntegerField(default=0, verbose_name=u'全達成報酬テキスト')

class PanelMissionMissionMaster(BaseMaster):
    """パネルミッションのミッション.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=64, verbose_name=u'名前')
    panel = models.PositiveSmallIntegerField(db_index=True, verbose_name=u'パネルID')
    number = models.PositiveSmallIntegerField(verbose_name=u'ミッション番号')
    image_pre = models.CharField(default='', max_length=96, verbose_name=u'達成前のパネル画像')
    image_post = models.CharField(default='', max_length=96, verbose_name=u'達成後のパネル画像')
    prizes = JsonCharField(default=list, verbose_name=u'達成報酬')
    prize_text = models.PositiveIntegerField(default=0, verbose_name=u'達成報酬テキスト')
    condition_type = models.PositiveSmallIntegerField(default=0, verbose_name=u'達成条件種別', choices=dict_to_choices(Defines.PanelMissionCondition.NAMES))
    condition_value1 = models.PositiveSmallIntegerField(default=0, verbose_name=u'達成条件の値1')
    condition_value2 = models.PositiveSmallIntegerField(default=0, verbose_name=u'達成条件の値2')
    condition_text = models.TextField(default='', verbose_name=u'達成条件の説明', blank=True)
    
    @classmethod
    def makeID(cls, panel, number):
        return (panel << 16) + number
    
    @classmethod
    def makeInstance(cls, key):
        model = cls()
        primary_key_column = cls.get_primarykey_column()
        setattr(model, primary_key_column, key)
        model.panel = (key >> 16)
        model.number = key & 0xffff
        return model

class PlayerPanelMission(BaseModel):
    """パネルミッションのプレイヤー情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    panel = models.PositiveSmallIntegerField(default=1, verbose_name=u'現在のパネル')
    cleared = models.PositiveSmallIntegerField(default=0, verbose_name=u'直前にクリアしたパネル')

class PanelMissionData(BasePerPlayerBase):
    """パネルミッションの達成情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    mid = models.PositiveSmallIntegerField(db_index=True, verbose_name=u'パネルID')
    stime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'開始時間')
    cnt1 = models.PositiveSmallIntegerField(default=0, verbose_name=u'達成率1')
    etime1 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'達成した時間1')
    rtime1 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'報酬を受け取った時間1')
    cnt2 = models.PositiveSmallIntegerField(default=0, verbose_name=u'達成率2')
    etime2 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'達成した時間2')
    rtime2 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'報酬を受け取った時間2')
    cnt3 = models.PositiveSmallIntegerField(default=0, verbose_name=u'達成率3')
    etime3 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'達成した時間3')
    rtime3 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'報酬を受け取った時間3')
    cnt4 = models.PositiveSmallIntegerField(default=0, verbose_name=u'達成率4')
    etime4 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'達成した時間4')
    rtime4 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'報酬を受け取った時間4')
    cnt5 = models.PositiveSmallIntegerField(default=0, verbose_name=u'達成率5')
    etime5 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'達成した時間5')
    rtime5 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'報酬を受け取った時間5')
    cnt6 = models.PositiveSmallIntegerField(default=0, verbose_name=u'達成率6')
    etime6 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'達成した時間6')
    rtime6 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'報酬を受け取った時間6')
    cnt7 = models.PositiveSmallIntegerField(default=0, verbose_name=u'達成率7')
    etime7 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'達成した時間7')
    rtime7 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'報酬を受け取った時間7')
    cnt8 = models.PositiveSmallIntegerField(default=0, verbose_name=u'達成率8')
    etime8 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'達成した時間8')
    rtime8 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'報酬を受け取った時間8')
    cnt9 = models.PositiveSmallIntegerField(default=0, verbose_name=u'達成率9')
    etime9 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'達成した時間9')
    rtime9 = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'報酬を受け取った時間9')
    
    def get_data(self, number):
        return {
            'cnt' : getattr(self, 'cnt%d' % number),
            'etime' : getattr(self, 'etime%d' % number),
            'rtime' : getattr(self, 'rtime%d' % number),
        }
    
    def set_data(self, number, cnt, etime, rtime):
        setattr(self, 'cnt%d' % number, cnt)
        setattr(self, 'etime%d' % number, etime)
        setattr(self, 'rtime%d' % number, rtime)
