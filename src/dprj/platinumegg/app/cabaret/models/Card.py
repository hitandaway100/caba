# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.models import BaseMaster, BaseMasterWithThumbnail,\
    BaseModel
from platinumegg.app.cabaret.models.base.fields import PositiveBigIntegerField,\
    JsonCharField, AppDateTimeField, ObjectField
from platinumegg.app.cabaret.models.Player import BasePerPlayerBase,\
    BasePerPlayerBaseWithMasterID
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.base.util import dict_to_choices

def rangedict(vmin, vmax):
    data = {}
    for i in range(vmin, vmax):
        data[i] = i
    return data

class CardMaster(BaseMasterWithThumbnail):
    """カードマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    ckind = models.PositiveSmallIntegerField(default=Defines.CardKind.NORMAL, choices=dict_to_choices(Defines.CardKind.NAMES), verbose_name=u'カードの種類(通常or教育or進化)')
    gtype = models.PositiveSmallIntegerField(default=Defines.CardGrowthType.BALANCE, choices=dict_to_choices(Defines.CardGrowthType.NAMES), verbose_name=u'成長タイプ(早熟orバランスor晩成)')
    cost = models.PositiveSmallIntegerField(default=0, verbose_name=u'コスト')
    basepower = models.PositiveIntegerField(default=1, verbose_name=u'接客力(基礎値)')
    maxpower = models.PositiveIntegerField(default=1, verbose_name=u'接客力(最大値)')
    maxlevel = models.PositiveIntegerField(default=1, verbose_name=u'最大レベル')
    skill = models.PositiveIntegerField(verbose_name=u'サービス(スキル)')
    albumhklevel = PositiveBigIntegerField(unique=True, verbose_name=u'(アルバム番号<<32)+ハメ管理レベル')
    basematerialexp = models.PositiveIntegerField(verbose_name=u'強化素材経験値(基礎)')
    maxmaterialexp = models.PositiveIntegerField(verbose_name=u'強化素材経験値(最大)')
    baseprice = models.PositiveIntegerField(verbose_name=u'売値(基礎)')
    maxprice = models.PositiveIntegerField(verbose_name=u'売値(最大)')
    evolcost = models.PositiveIntegerField(verbose_name=u'進化費用')
    dmmurl = JsonCharField(verbose_name=u'DMMの動画ページのURL', default=list, blank=True)
    
    @classmethod
    def makeAlbumHklevel(cls, album, hklevel):
        return (album << 32) + hklevel
    
    @property
    def album(self):
        return int(self.albumhklevel >> 32)
    @property
    def hklevel(self):
        return int(self.albumhklevel & 0xffffffff)

class CardSortMaster(BaseMaster):
    """カードソート用マスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    ctype = models.PositiveSmallIntegerField(db_index=True, verbose_name=u'タイプ', default=Defines.CharacterType.TYPE_001, choices=dict_to_choices(Defines.CharacterType.NAMES))
    rare = models.PositiveSmallIntegerField(verbose_name=u'レア度', choices=dict_to_choices(Defines.Rarity.NAMES))
    album = models.PositiveIntegerField(db_index=True, verbose_name=u'アルバム番号')
    hklevel = models.PositiveSmallIntegerField(db_index=True, verbose_name=u'ハメ管理レベル', default=1, choices=rangedict(1, Defines.HKLEVEL_MAX+1).items())

class DefaultCardMaster(BaseMaster):
    """デフォルト所持カードのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    ctype = models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'タイプ', choices=dict_to_choices(Defines.CharacterType.NAMES))
    leader = models.PositiveIntegerField(db_index=True, verbose_name=u'リーダー')
    members = JsonCharField(default=list, verbose_name=u'メンバー', help_text=u'ユーザー登録時にデッキに設定します')
    box = JsonCharField(default=list, verbose_name=u'BOX', help_text=u'ユーザー登録時にBOXに設定します')

class CardBase(BasePerPlayerBase):
    """カード.
    """
    class Meta:
        abstract = True
    
    FIXED_COLUMNS = (
        'uid',
    )
    
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'マスターID')
    exp = models.PositiveIntegerField(default=0, verbose_name=u'経験値')
    level = models.PositiveIntegerField(default=1, verbose_name=u'レベル')
    skilllevel = models.PositiveSmallIntegerField(default=1, verbose_name=u'サービスレベル')
    takeover = models.PositiveIntegerField(default=0, verbose_name=u'引き継いだ接客力')
    protection = models.BooleanField(default=False, verbose_name=u'保護フラグ')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'作成時間')
    way = models.PositiveSmallIntegerField(default=Defines.CardGetWayType.OTHER, verbose_name=u'取得方法')
    
class Card(CardBase):
    """カード個別情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class CardDeleted(CardBase):
    """削除済みのカード.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    dtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'削除時間')
    
    @staticmethod
    def create(card):
        ins = CardDeleted()
        for field in Card._meta.fields:
            setattr(ins, field.name, getattr(card, field.name))
        return ins
    
class DeckBase(BaseModel):
    """デッキ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = True
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID');
    leader = PositiveBigIntegerField(verbose_name=u'リーダー')
    member1 = PositiveBigIntegerField(default=0, verbose_name=u'デッキメンバー1')
    member2 = PositiveBigIntegerField(default=0, verbose_name=u'デッキメンバー2')
    member3 = PositiveBigIntegerField(default=0, verbose_name=u'デッキメンバー3')
    member4 = PositiveBigIntegerField(default=0, verbose_name=u'デッキメンバー4')
    member5 = PositiveBigIntegerField(default=0, verbose_name=u'デッキメンバー5')
    member6 = PositiveBigIntegerField(default=0, verbose_name=u'デッキメンバー6')
    member7 = PositiveBigIntegerField(default=0, verbose_name=u'デッキメンバー7')
    member8 = PositiveBigIntegerField(default=0, verbose_name=u'デッキメンバー8')
    member9 = PositiveBigIntegerField(default=0, verbose_name=u'デッキメンバー9')
    
    __deck_arr = None
    
    def to_array(self):
        if self.__deck_arr is None:
            arr = []
            if self.leader:
                arr.append(self.leader)
            for i in xrange(Defines.DECK_CARD_NUM_MAX-1):
                cid = getattr(self, 'member%d' % (i+1))
                if cid:
                    arr.append(cid)
            self.__deck_arr = arr
        return self.__deck_arr
    
    def set_from_array(self, arr):
        """配列をデッキに設定.
        """
        if len(arr) < 1 or arr[0] < 1:
            raise CabaretError(u'デッキにはリーダーが必要です', CabaretError.Code.ILLEGAL_ARGS)
        
        self.leader = arr[0]
        idx = 1
        for i in xrange(Defines.DECK_CARD_NUM_MAX-1):
            cid = 0
            if (i+1) < len(arr):
                cid = arr[i+1]
            
            setattr(self, 'member%d' % (i+1), 0)
            if 0 < cid:
                setattr(self, 'member%d' % idx, cid)
                idx += 1
        self.__deck_arr = None
    
    def is_member(self, cardid):
        return cardid in self.to_array()

class Deck(DeckBase):
    """デッキ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class RaidDeck(DeckBase):
    """レイドデッキ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class CardAcquisition(BasePerPlayerBaseWithMasterID):
    """カード取得フラグ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    gtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'手に入れた時間')
    maxlevel = models.PositiveIntegerField(default=0, verbose_name=u'手に入れた最大レベル')

class AlbumAcquisition(BasePerPlayerBaseWithMasterID):
    """アルバム開放フラグ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    gtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'手に入れた時間')

class CompositionData(BaseModel):
    """強化合成情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    mid = models.PositiveIntegerField(default=0, verbose_name=u'マスターID')
    exp = models.PositiveIntegerField(default=0, verbose_name=u'経験値')
    level = models.PositiveIntegerField(default=0, verbose_name=u'レベル')
    skilllevel = models.PositiveSmallIntegerField(default=0, verbose_name=u'サービスレベル')
    takeover = models.PositiveIntegerField(default=0, verbose_name=u'引き継いだ接客力')
    result = ObjectField(default=dict, verbose_name=u'合成結果パラメータ')
    
    def set_to_card(self, card):
        card.mid = self.mid
        card.exp = self.exp
        card.level = self.level
        card.skilllevel = self.skilllevel
        card.takeover = self.takeover
    
    def setBasePreParameter(self, basecard):
        """ベースカードの元のパラメータ.
        """
        self.mid = basecard.mid
        self.exp = basecard.exp
        self.level = basecard.level
        self.skilllevel = basecard.skilllevel
        self.takeover = basecard.takeover
    
    def setResult(self, basecardset, materialcardsetlist, is_great_success, gold, exp, exp_pre, lvpre, lvup, skilllvup):
        """合成結果を設定.
        """
        self.result = {
            'base' : basecardset.card.id,
            'material' : [materialcardset.card.id for materialcardset in materialcardsetlist],
            'is_great_success' : is_great_success,
            'gold' : gold,
            'exp' : exp,
            'exp_pre' : exp_pre,
            'lvpre' : lvpre,
            'lvup' : lvup,
            'skilllvup' : skilllvup,
        }
    
    @property
    def result_baseid(self):
        return self.result.get('base', 0)
    
    @property
    def result_materialidlist(self):
        return self.result.get('material', [])
    
    @property
    def result_flag_great_success(self):
        return self.result.get('is_great_success', False)
    
    @property
    def result_cost_gold(self):
        return self.result.get('gold', 0)
    
    @property
    def result_exp(self):
        return self.result.get('exp', 0)
    
    @property
    def result_exp_pre(self):
        return self.result.get('exp_pre', 0)
    
    @property
    def result_lvpre(self):
        return self.result.get('lvpre', 0)
    
    @property
    def result_lvup(self):
        return self.result.get('lvup', 0)
    
    @property
    def result_skilllvup(self):
        return self.result.get('skilllvup', 0)

class EvolutionData(BaseModel):
    """進化合成情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    mid = models.PositiveIntegerField(default=0, verbose_name=u'マスターID')
    exp = models.PositiveIntegerField(default=0, verbose_name=u'経験値')
    level = models.PositiveIntegerField(default=0, verbose_name=u'レベル')
    skilllevel = models.PositiveSmallIntegerField(default=0, verbose_name=u'サービスレベル')
    takeover = models.PositiveIntegerField(default=0, verbose_name=u'引き継いだ接客力')
    result = ObjectField(default=dict, verbose_name=u'合成結果パラメータ')
    
    def set_to_card(self, card):
        card.mid = self.mid
        card.exp = self.exp
        card.level = self.level
        card.skilllevel = self.skilllevel
        card.takeover = self.takeover
    
    def setBasePreParameter(self, basecard):
        """ベースカードの元のパラメータ.
        """
        self.mid = basecard.mid
        self.exp = basecard.exp
        self.level = basecard.level
        self.skilllevel = basecard.skilllevel
        self.takeover = basecard.takeover
    
    def setResult(self, basecard, materialcard, memories_open, takeover):
        """合成結果を設定.
        """
        self.result = {
            'base' : basecard.id,
            'material' : materialcard.id,
            'is_memories_open' : memories_open,
            'takeover' : takeover,
        }
    
    @property
    def result_baseid(self):
        return self.result.get('base', 0)
    
    @property
    def result_materialid(self):
        return self.result.get('material', 0)
    
    @property
    def result_flag_memories_open(self):
        return self.result.get('is_memories_open', False)
    
    @property
    def result_takeover(self):
        return self.result.get('takeover', 0)

class CardStock(BasePerPlayerBaseWithMasterID):
    """カードのストック数.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    num = models.PositiveIntegerField(default=0, verbose_name=u'ストック数')
