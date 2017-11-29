# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMasterWithThumbnail,\
    BaseMaster, BaseModel
from defines import Defines
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID
from platinumegg.app.cabaret.models.base.fields import AppDateTimeField
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class MemoriesMaster(BaseMasterWithThumbnail):
    """思い出アルバムのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    contenttype = models.PositiveSmallIntegerField(verbose_name=u'コンテンツの種類', default=Defines.MemoryContentType.IMAGE, choices=dict_to_choices(Defines.MemoryContentType.NAMES))
    contentdata = models.CharField(max_length=96, verbose_name=u'コンテンツの内容')
    cardid = models.PositiveIntegerField(default=0, db_index=True, verbose_name=u'カードID')
    cardlevel = models.PositiveIntegerField(default=0, verbose_name=u'開放に必要なカードのレベル')

class Memories(BasePerPlayerBaseWithMasterID):
    """思い出アルバムのデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    vtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'閲覧した時間')

class MoviePlayList(BaseMaster):
    """思い出アルバムプレイリスト.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.AutoField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'名前')
    filename = models.CharField(max_length=48, verbose_name=u'ファイル名', unique=True)
    data = models.TextField(verbose_name=u'複合鍵')

class PcMoviePlayList(BaseMaster):
    """思い出アルバムプレイリスト（PC用）.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.AutoField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'名前')
    filename = models.CharField(max_length=48, verbose_name=u'ファイル名', unique=True)

class VoicePlayList(BaseMaster):
    """思い出アルバムプレイリスト（音声）.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.AutoField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'名前')
    filename = models.CharField(max_length=48, verbose_name=u'ファイル名', unique=True)

class MovieViewData(BaseModel):
    """思い出アルバム閲覧情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'アルバムID')
    cnt = models.PositiveIntegerField(default=0, verbose_name=u'閲覧回数')

class PcMovieViewData(BaseModel):
    """思い出アルバム閲覧情報（PC用）.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'アルバムID')
    cnt = models.PositiveIntegerField(default=0, verbose_name=u'閲覧回数')

class EventMovieMaster(BaseMaster):
    """イベント動画のマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=64, verbose_name=u'名前(管理用)')
    sp = models.CharField(default='', max_length=48, verbose_name=u'動画のファイル名(SP)', help_text='動画ファイルの.mp4を除いた名前')
    pc = models.CharField(default='', max_length=48, verbose_name=u'動画のファイル名(PC)', help_text='動画ファイルの.mp4を除いた名前')
    cast = models.CharField(default='', max_length=24, verbose_name=u'女優名')
    title = models.CharField(default='', max_length=48, verbose_name=u'動画タイトル')
    text = models.TextField(default='', verbose_name=u'動画説明')

class EventMovieViewData(BasePerPlayerBaseWithMasterID):
    """イベント動画の閲覧情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    cnt_sp = models.PositiveIntegerField(default=0, verbose_name=u'閲覧回数(SP)')
    cnt_pc = models.PositiveIntegerField(default=0, verbose_name=u'閲覧回数(PC)')
    
    def getCountTotal(self):
        return self.cnt_pc + self.cnt_sp

