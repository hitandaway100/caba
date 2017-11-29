# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import Singleton, BaseModel
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.fields import TinyIntField,\
    AppDateTimeField, JsonCharField, PositiveAutoField, ObjectField
from defines import Defines
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class AppConfig(Singleton):
    """メンテナンス設定.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    maintenancetype = TinyIntField(verbose_name=u'メンテフラグ', choices=dict_to_choices(Defines.MaintenanceType.NAMES), default=Defines.MaintenanceType.EMERGENCY)
    stime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'メンテ開始時間')
    etime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'メンテ終了時間')
    master = models.PositiveIntegerField(default=0, verbose_name=u'マスターデータ番号')
    
    def is_maintenance(self):
        if self.is_emergency():
            return True
        elif self.stime <= OSAUtil.get_now() < self.etime:
            return True
        return False
    
    def is_platform_maintenance(self):
        """プラットフォームのメンテか.
        """
        return self.maintenancetype in (Defines.MaintenanceType.REGULAR_PLATFORM, Defines.MaintenanceType.EMERGENCY_PLATFORM)
    
    def is_emergency(self):
        """緊急メンテか.
        """
        return self.maintenancetype in (Defines.MaintenanceType.EMERGENCY, Defines.MaintenanceType.EMERGENCY_PLATFORM)
    
    @classmethod
    def getModel(cls):
        model = cls.getSingletonModel()
        if model is None:
            model = cls()
            model.save()
        return model

class PreRegistConfig(Singleton):
    """事前登録設定.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    etime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'事前登録終了時間')
    prizes = JsonCharField(default=list, verbose_name=u'事前登録報酬')
    
    def is_before_publication(self):
        now = OSAUtil.get_now()
        if now < self.etime:
            return True
        return False
    

class MessageQueue(BaseModel):
    """メッセージAPIのキュー.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveAutoField(primary_key=True, verbose_name=u'ID')
    stime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'送信開始時間', db_index=True)
    title = models.CharField(max_length=26, verbose_name=u'タイトル')
    body = models.CharField(max_length=100, verbose_name=u'本文')
    recipients = ObjectField(default=list, verbose_name=u'送信先(未指定の場合は全員)')
    jumpto = models.CharField(max_length=100, verbose_name=u'飛び先', blank=True)

