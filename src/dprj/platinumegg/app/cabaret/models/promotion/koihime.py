# -*- coding: utf-8 -*-
import settings_sub
from platinumegg.app.cabaret.models.promotion.base import PromotionDataBase,\
    PromotionRequirementMasterBase, PromotionPrizeMasterBase,\
    PromotionConfigBase


class PromotionConfigKoihime(PromotionConfigBase):
    """恋姫†夢想向けクロスプロモーション設定マスターデータ.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME

class PromotionPrizeMasterKoihime(PromotionPrizeMasterBase):
    """恋姫†夢想向けクロスプロモーション報酬マスターデータ.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME

class PromotionRequirementMasterKoihime(PromotionRequirementMasterBase):
    """恋姫†夢想向けクロスプロモーション条件マスターデータ.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME

class PromotionDataKoihime(PromotionDataBase):
    """恋姫†夢想向けクロスプロモーション達成データ.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME
