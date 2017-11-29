# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.fields import AppDateTimeField


class InfomationMaster(BaseMaster):
    """お知らせのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    title = models.TextField(verbose_name=u'タイトル')
    body = models.TextField(verbose_name=u'本文')
    jumpto = models.TextField(verbose_name=u'クリック時の飛び先', blank=True)
    imageurl = models.TextField(verbose_name=u'画像URL', blank=True)
    stime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'掲載開始日')
    etime = AppDateTimeField(default=OSAUtil.get_now, db_index=True, verbose_name=u'掲載終了日')

class BannerBase(BaseMaster):
    class Meta:
        abstract = True
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.TextField(verbose_name=u'名前(画像のalt属性に設定します)')
    jumpto = models.TextField(verbose_name=u'クリック時の飛び先', blank=True)
    imageurl = models.TextField(verbose_name=u'画像URL')
    priority = models.PositiveIntegerField(default=0, verbose_name=u'優先度')
    stime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'掲載開始日')
    etime = AppDateTimeField(default=OSAUtil.get_now, db_index=True, verbose_name=u'掲載終了日')
    comment_external = models.TextField(verbose_name=u'外部リンク用文言', default='', blank=True)

class TopBannerMaster(BannerBase):
    """トップページのバナー.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class EventBannerMaster(BannerBase):
    """イベントバナー.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    comment = models.TextField(verbose_name=u'バナー下の文言')
    forpage = models.BooleanField(default=True, verbose_name=u'TOP,マイページで表示するフラグ')
    formenu = models.BooleanField(default=False, verbose_name=u'メニュー表示フラグ')
    teaserheader = models.TextField(default='', verbose_name=u'ティザーページのヘッダ画像', blank=True)
    teaserbody = models.TextField(default='', verbose_name=u'ティザーページのボディ画像', blank=True)
    teaserbodytitle = models.TextField(default='', verbose_name=u'ティザーページのボディタイトルテキスト', blank=True)
    teaserbodybottom = models.TextField(default='', verbose_name=u'ティザーページのボディ下部テキスト', blank=True)
    teaserscheduletext= models.TextField(default='', verbose_name=u'ティザーページ期間表示文言', blank=True)
    
    @property
    def has_teaser(self):
        return self.teaserheader or self.teaserbody

class PopupMaster(BaseMaster):
    """ポップアップ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=32, verbose_name=u'名前')
    title = models.CharField(max_length=32, verbose_name=u'タイトル')
    imageurl = models.TextField(verbose_name=u'画像URL')
    priority = models.PositiveIntegerField(default=0, verbose_name=u'優先度')
    stime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'掲載開始日')
    etime = AppDateTimeField(default=OSAUtil.get_now, db_index=True, verbose_name=u'掲載終了日')
    banner = models.PositiveIntegerField(default=0, verbose_name=u'イベントバナーID')
    bannerflag = models.BooleanField(default=False, verbose_name=u'イベントバナー表示フラグ')
