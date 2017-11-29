# -*- coding: utf-8 -*-
import settings
import settings_sub
from copy import copy
from defines import Defines
from platinumegg.app.cabaret.models.base.models import BaseMaster
from platinumegg.app.cabaret.models.Card import CardSortMaster, CardMaster

class CardMasterViewMeta(type):
    def __new__(cls, name, bases, attrs):
        excludes = (Defines.PUBLISH_STATUS_COLUMN, Defines.MASTER_EDITTIME_COLUMN)
        fields = {}
        for model_cls in (CardSortMaster, CardMaster):
            for field in model_cls.get_fields():
                if field.name in excludes or attrs.has_key(field.name):
                    continue
                fields[field.name] = copy(field)
        fields.update(attrs)
        cls = type(name, bases, fields)
        return cls

class CardMasterView(BaseMaster):
    """CardMasterのView.
    """
    __metaclass__ = CardMasterViewMeta
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def save(self, force_insert=False, force_update=False, using=settings.DB_DEFAULT):
        """保存.
        泥臭いなぁ.
        """
        self.albumhklevel = (self.album << 32) + self.hklevel
        for model_cls in (CardMaster, CardSortMaster):
            model = model_cls()
            for field in model_cls.get_fields():
                setattr(model, field.name, getattr(self, field.name))
            model.save(force_insert=force_insert, force_update=force_update, using=using)
