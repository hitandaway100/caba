# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseModel
from platinumegg.app.cabaret.models.base.fields import PositiveBigIntegerField,\
    AppDateTimeField
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class Friend(BaseModel):
    """仲間.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    FIXED_COLUMNS = (
        'uid','fid'
    )
    
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID((ユーザID<<32)+フレンドID)')
    uid = models.PositiveIntegerField(verbose_name=u'ユーザID')
    fid = models.PositiveIntegerField(db_index=True, verbose_name=u'フレンドID')
    state = models.PositiveSmallIntegerField(verbose_name=u'状態', choices=dict_to_choices(Defines.FriendState.NAMES))
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'更新時間')
    
    @staticmethod
    def makeID(uid, fid):
        return (uid << 32) + fid
    
    @staticmethod
    def create(uid, fid, state):
        ins = Friend()
        ins.id = Friend.makeID(uid, fid)
        ins.uid = uid
        ins.fid = fid
        ins.state = state
        return ins
    
    @classmethod
    def makeInstance(cls, key):
        uid = (key >> 32)
        fid = (key & 0xffffffff)
        return Friend.create(uid, fid, 0)

class FriendRecordNum(BaseModel):
    """リクエスト数とかここで持っておこう.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    num = models.PositiveSmallIntegerField(default=0, verbose_name=u'Friend数')
