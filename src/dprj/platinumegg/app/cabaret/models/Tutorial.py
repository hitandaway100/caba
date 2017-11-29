# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster
from platinumegg.app.cabaret.models.base.fields import JsonCharField
from defines import Defines
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class TutorialConfig(BaseMaster):
    """チュートリアル設定.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    ctype = models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'タイプ', choices=dict_to_choices(Defines.CharacterType.NAMES))
#    compositioncard = models.PositiveIntegerField(verbose_name=u'教育の素材で使用するカード')
    scoutdropcard = models.PositiveIntegerField(verbose_name=u'スカウトでドロップするカード')
    scoutarea = models.PositiveIntegerField(verbose_name=u'チュートリアルのスカウトエリア')
    prizes = JsonCharField(default=list, verbose_name=u'チュートリアル完了報酬')
    treasure = models.PositiveIntegerField(verbose_name=u'チュートリアルで発見する宝箱')
    memories = models.PositiveIntegerField(verbose_name=u'チュートリアルで閲覧する思い出アルバム', default=0)
    pcmemories = models.PositiveIntegerField(verbose_name=u'チュートリアルで閲覧する思い出アルバム(PC)', default=0)
