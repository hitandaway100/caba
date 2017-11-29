# -*- coding: utf-8 -*-
import settings_sub
from platinumegg.app.cabaret.models.promotion.base import PromotionDataBase,\
    PromotionRequirementMasterBase, PromotionPrizeMasterBase,\
    PromotionConfigBase


class PromotionConfigCsc(PromotionConfigBase):
    """CSC向けクロスプロモーション設定マスターデータ.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME

class PromotionPrizeMasterCsc(PromotionPrizeMasterBase):
    """CSC向けクロスプロモーション報酬マスターデータ.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME

class PromotionRequirementMasterCsc(PromotionRequirementMasterBase):
    """CSC向けクロスプロモーション条件マスターデータ.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME

class PromotionDataCsc(PromotionDataBase):
    """CSC向けクロスプロモーション達成データ.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME
