# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster, BaseModel
from platinumegg.app.cabaret.models.base.fields import ObjectField

class BossMaster(BaseMaster):
    """ボスのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(default='', max_length=48, verbose_name=u'名前')
    commentappear = models.TextField(default='', verbose_name=u'出現時(挑発)コメント')
    commentwin = models.TextField(default='', verbose_name=u'勝利(ユーザが勝利)時コメント')
    commentlose = models.TextField(default='', verbose_name=u'敗北(ユーザが敗北)時コメント')
    thumb = models.CharField(default='', max_length=96, verbose_name=u'サムネイル')
    hp = models.PositiveIntegerField(default=0, verbose_name=u'HP')
    apcost = models.PositiveSmallIntegerField(default=0, verbose_name=u'消費体力')
    attack = models.PositiveIntegerField(default=0, verbose_name=u'攻撃力')
    defense = models.PositiveIntegerField(default=0, verbose_name=u'防御力')
    
    def get_maxhp(self):
        return self.hp

class BossBattle(BaseModel):
    """ボスバトル情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    area = models.PositiveIntegerField(default=0, verbose_name=u'エリアID')
    anim = ObjectField(default=dict, verbose_name=u'バトルの内容')

