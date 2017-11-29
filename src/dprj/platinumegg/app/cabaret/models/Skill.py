# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMasterWithName
from defines import Defines
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class SkillMaster(BaseMasterWithName):
    """スキルのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    class Skill():
        def __init__(self, etarget=0, etypelist=None, epower=0, etext=None, eskill=0):
            self.etarget = etarget
            self.etypelist = etypelist or []
            self.epower = epower
            self.etext = etext or u''
            self.eskill = eskill
    
    MULTI_SKILL_NUM_MAX = 4
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    etarget = models.PositiveSmallIntegerField(verbose_name=u'効果対象', choices=dict_to_choices(Defines.SkillTarget.NAMES))
    etype = models.PositiveSmallIntegerField(verbose_name=u'対象タイプ', choices=dict_to_choices(Defines.CharacterType.SKILL_TARGET_NAMES))
    eskill = models.PositiveSmallIntegerField(verbose_name=u'スキル効果', choices=dict_to_choices(Defines.SkillEffect.NAMES), default=0)
    epower = models.PositiveIntegerField(verbose_name=u'上昇する接客力')
    etext = models.TextField(verbose_name=u'効果テキスト', blank=True)
    etarget1 = models.PositiveSmallIntegerField(verbose_name=u'効果対象', choices=dict_to_choices(Defines.SkillTarget.NAMES), default=0)
    etype1 = models.PositiveSmallIntegerField(verbose_name=u'対象タイプ', default=0, choices=dict_to_choices(Defines.CharacterType.SKILL_TARGET_NAMES_SUB))
    eskill1 = models.PositiveSmallIntegerField(verbose_name=u'スキル効果', choices=dict_to_choices(Defines.SkillEffect.NAMES), default=0)
    epower1 = models.PositiveIntegerField(verbose_name=u'上昇する接客力', default=0)
    etext1 = models.TextField(verbose_name=u'効果テキスト', blank=True)
    etarget2 = models.PositiveSmallIntegerField(verbose_name=u'効果対象', choices=dict_to_choices(Defines.SkillTarget.NAMES), default=0)
    etype2 = models.PositiveSmallIntegerField(verbose_name=u'対象タイプ', default=0, choices=dict_to_choices(Defines.CharacterType.SKILL_TARGET_NAMES_SUB))
    eskill2 = models.PositiveSmallIntegerField(verbose_name=u'スキル効果', choices=dict_to_choices(Defines.SkillEffect.NAMES), default=0)
    epower2 = models.PositiveIntegerField(verbose_name=u'上昇する接客力', default=0)
    etext2 = models.TextField(verbose_name=u'効果テキスト', blank=True)
    etarget3 = models.PositiveSmallIntegerField(verbose_name=u'効果対象', choices=dict_to_choices(Defines.SkillTarget.NAMES), default=0)
    etype3 = models.PositiveSmallIntegerField(verbose_name=u'対象タイプ', default=0, choices=dict_to_choices(Defines.CharacterType.SKILL_TARGET_NAMES_SUB))
    eskill3 = models.PositiveSmallIntegerField(verbose_name=u'スキル効果', choices=dict_to_choices(Defines.SkillEffect.NAMES), default=0)
    epower3 = models.PositiveIntegerField(verbose_name=u'上昇する接客力', default=0)
    etext3 = models.TextField(verbose_name=u'効果テキスト', blank=True)
    erate1 = models.PositiveSmallIntegerField(verbose_name=u'発動率Lv.1')
    erate2 = models.PositiveSmallIntegerField(verbose_name=u'発動率Lv.2')
    erate3 = models.PositiveSmallIntegerField(verbose_name=u'発動率Lv.3')
    erate4 = models.PositiveSmallIntegerField(verbose_name=u'発動率Lv.4')
    erate5 = models.PositiveSmallIntegerField(verbose_name=u'発動率Lv.5')
    erate6 = models.PositiveSmallIntegerField(verbose_name=u'発動率Lv.6')
    erate7 = models.PositiveSmallIntegerField(verbose_name=u'発動率Lv.7')
    erate8 = models.PositiveSmallIntegerField(verbose_name=u'発動率Lv.8')
    erate9 = models.PositiveSmallIntegerField(verbose_name=u'発動率Lv.9')
    erate10 = models.PositiveSmallIntegerField(verbose_name=u'発動率Lv.10')
    group = models.PositiveIntegerField(verbose_name=u'グループ', help_text=u'同じ値が入っていれば教育時にスキルアップの対象になる', default=0)
    
    def get_rate(self, level):
        return getattr(self, 'erate%d' % level, self.erate1)
    
    def get_skill(self, number):
        str_number = str(number) if 0 < number else ''
        epower = getattr(self, 'epower%s' % str_number)
        if epower < 1:
            # 未設定.
            return None
        
        etarget = getattr(self, 'etarget%s' % str_number)
        tmp_etype = getattr(self, 'etype%s' % str_number)
        etext = getattr(self, 'etext%s' % str_number) or self.text
        eskill = getattr(self, 'eskill%s' % str_number)
        
        if tmp_etype == Defines.CharacterType.ALL:
            etypelist = Defines.CharacterType.LIST
        else:
            etypelist = []
            for _ in xrange(Defines.CharacterType.NUM_MAX - 1):
                etype = tmp_etype % 10
                if etype in Defines.CharacterType.LIST:
                    etypelist.append(etype)
                tmp_etype = int(tmp_etype / 10)
        
        return SkillMaster.Skill(etarget, list(set(etypelist)), epower, etext, eskill)

