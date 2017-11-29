# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.modelgroup import ModelGroupBase
from platinumegg.app.cabaret.models.Card import CardSortMaster, CardMaster
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
import math
import settings_sub

class CardUtil:
    @staticmethod
    def calcPower(gtype, basepower, maxpower, level, maxlevel, takeover=0):
        if maxlevel == 1 or maxlevel <= level:
            return maxpower + takeover
        else:
            if gtype == Defines.CardGrowthType.BALANCE:
                # pow = min_atk + (max_atk - min_atk)/(max_level - min_level) * (level-min_level).
                return int(basepower + (maxpower - basepower) / (maxlevel - 1) * (level - 1)) + takeover
            elif gtype == Defines.CardGrowthType.PRECOCIOUS:
                # α = (max_atk - min_atk)/(max_level - min_level)^2.
                # pow = min_atk + α*(level - min_level)^2.
                a = (maxpower - basepower)/math.pow((maxlevel - 1), 2)
                return int(basepower + a * math.pow((level - 1), 2)) + takeover
            elif gtype == Defines.CardGrowthType.BANSEI:
                # α = (min_atk - max_atk)/(min_level - max_level)^2.
                # pow = max_atk + α*(level - max_level)^2.
                a = (basepower - maxpower)/math.pow((1 - maxlevel), 2)
                return int(maxpower + a * math.pow((level - maxlevel), 2)) + takeover
            raise CabaretError(u'未対応の成長タイプ.%d' % gtype)
    
    @staticmethod
    def calcSellPrice(baseprice, maxprice, level, maxlevel):
        return baseprice
    
    @staticmethod
    def calcSellPriceTreasure(rare):
        return Defines.Rarity.TREASURE_WHEN_SELL.get(rare, 0)
    
    @staticmethod
    def canSellMany(uid, cardset):
        """一括で売却可能かを判定.
        """
        return cardset.master.rare < Defines.Rarity.RARE and cardset.master.hklevel == 1 and cardset.card.exp == 0
    
    @staticmethod
    def checkSellable(uid, deck, cardset):
        """売れるかチェック.
        エラーの場合は即エラー.
        """
        card = cardset.card
        if uid != card.uid:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        elif card.protection:
            raise CabaretError(u'保護中のキャストは退店できません', CabaretError.Code.ILLEGAL_ARGS)
        elif deck.is_member(card.id):
            raise CabaretError(u'出勤中のキャストは退店できません', CabaretError.Code.ILLEGAL_ARGS)
        return Defines.Rarity.RARE <= cardset.master.rare, 1 < cardset.master.hklevel
    
    @staticmethod
    def checkEvolvable(cardmaster):
        """進化可能かチェック.
        """
        if cardmaster.ckind != Defines.CardKind.NORMAL:
            return False
        elif not cardmaster.rare in Defines.Rarity.EVOLUTION_ABLES:
            return False
        elif Defines.HKLEVEL_MAX <= cardmaster.hklevel:
            return False
        return True
    
    @staticmethod
    def checkStockableMaster(cardmaster, raise_on_error=True):
        """ストックできるかチェック.
        """
        if Defines.CardKind.NORMAL != cardmaster.ckind:
            if raise_on_error:
                raise CabaretError(u'アクセサリはストックできません', CabaretError.Code.ILLEGAL_ARGS)
            else:
                return False
        elif not cardmaster.rare in Defines.Rarity.TRANSFER:
            if raise_on_error:
                raise CabaretError(u'レア度が%sのキャストはストックできません' % Defines.Rarity.NAMES[cardmaster.rare], CabaretError.Code.ILLEGAL_ARGS)
            else:
                return False
        return True
    
    @staticmethod
    def checkStockable(uid, deck, cardset, raise_on_error=True):
        """ストックできるかチェック.
        """
        card = cardset.card
        if uid != card.uid:
            if raise_on_error:
                raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
            else:
                return False
        elif card.protection:
            if raise_on_error:
                raise CabaretError(u'保護中のキャストはストックできません', CabaretError.Code.ILLEGAL_ARGS)
            else:
                return False
        elif deck.is_member(card.id):
            if raise_on_error:
                raise CabaretError(u'出勤中のキャストはストックできません', CabaretError.Code.ILLEGAL_ARGS)
            else:
                return False
        return CardUtil.checkStockableMaster(cardset.master, raise_on_error=raise_on_error)
    
    @staticmethod
    def makeThumbnailUrlIcon(master):
        """52*52サムネ画像.
        """
        return u'%s/H%d/Card_thumb_52_52.png' % (master.thumb, master.hklevel)
    
    @staticmethod
    def makeThumbnailUrlSmall(master):
        """60*75サムネ画像.
        """
        return u'%s/H%d/Card_thumb_60_75.png' % (master.thumb, master.hklevel)
    
    @staticmethod
    def makeThumbnailUrlMiddle(master):
        """110*138サムネ画像.
        """
        return u'%s/H%d/Card_thumb_110_138.png' % (master.thumb, master.hklevel)
    
    @staticmethod
    def makeThumbnailUrlLarge(master):
        """320*400サムネ画像.
        """
        return u'%s/H%d/Card_thumb_320_400.png' % (master.thumb, master.hklevel)
    
    @staticmethod
    def makeThumbnailUrlBustup(master):
        """320*314バストアップ画像.
        """
        return u'%s/H%d/Card_thumb_320_314.png' % (master.thumb, master.hklevel)
    
    @staticmethod
    def makeThumbnailUrlMemory(master):
        """70*88思い出画像.
        """
        return u'%s/H%d/Card_thumb_70_88.png' % (master.thumb, master.hklevel)

class ModelCardMaster(ModelGroupBase):
    """カードのマスターデータ.
    """
    class Meta():
        BASE_MODEL = CardMaster
        MODELS = (
            CardSortMaster,
        )
    
    _skill = None
    
    def __init__(self, model_list=None):
        ModelGroupBase.__init__(self, model_list)
        self.__dict__['_skill'] = None
    def setSkill(self, skillmaster):
        if self.skill != skillmaster.id:
            raise CabaretError(u'Invalid skill.%d' % skillmaster.id)
        self._skill = skillmaster
    def getSkill(self):
        return self._skill
    def getSkillGroup(self):
        return self._skill.group if self._skill else None

class CardSet:
    """カード情報見るときはマスターデータも必ずいると思うからセットに.
    """
    def __init__(self, card, modelcardmaster):
        self.__card = card
        self.__master = modelcardmaster
        self.__id = card.id
    @property
    def card(self):
        return self.__card
    @property
    def master(self):
        return self.__master
    
    @property
    def id(self):
        return self.__id or self.card.id
    
    @property
    def power(self):
        """現在接客力.
        """
        return CardUtil.calcPower(self.master.gtype, self.master.basepower, self.master.maxpower, self.card.level, self.master.maxlevel, self.card.takeover)
    
    @property
    def sellprice(self):
        """売値.
        """
        return CardUtil.calcSellPrice(self.master.baseprice, self.master.maxprice, self.card.level, self.master.maxlevel)
    
    @property
    def sellprice_treasure(self):
        """売値.
        """
        return CardUtil.calcSellPriceTreasure(self.master.rare)
    
    @property
    def is_levelmax(self):
        """レベル最大判定.
        """
        return self.master.maxlevel <= self.card.level
    @property
    def is_skilllevelmax(self):
        """スキルレベル最大判定.
        """
        if self.master.skill:
            return Defines.SKILLLEVEL_MAX <= self.card.skilllevel
        else:
            return True
    @property
    def is_can_composition(self):
        """合成可能判定.
        """
        return (self.master.ckind == Defines.CardKind.NORMAL and not (self.is_levelmax and self.is_skilllevelmax)) or settings_sub.IS_BENCH
    
    @property
    def is_can_evolution(self):
        """進化可能判定.
        """
        return CardUtil.checkEvolvable(self.master)
    
    def get_evolution_takeover(self):
        """引き継ぎパラメータの取得.
        """
        power = self.power
        if self.is_levelmax:
            rate = Defines.EVOLUTION_TAKEOVER_RATE_LVMAX
        else:
            rate = Defines.EVOLUTION_TAKEOVER_RATE
        return int(power * rate / 100)

class CardListFilter():
    """カードリストの絞り込み用パラメータ.
    """
    def __init__(self, ctype=None, maxrare=None, ckind=None):
        self.ctype = ctype
        self.maxrare = maxrare
        self.ckind = ckind
        if ckind is None:
            ckind = Defines.CardKind.NAMES.keys()
        elif not isinstance(ckind, (list, tuple)):
            ckind = [ckind]
        self.ckind = ckind
        self.opt_filters = []
    
    def __check_ctype(self, ctype):
        if self.ctype is None:
            return True
        elif isinstance(self.ctype, (list, tuple)):
            return ctype in self.ctype
        else:
            return self.ctype in (Defines.CharacterType.ALL, ctype)
    
    def __check_rare(self, rare):
        if self.maxrare is None or rare <= self.maxrare:
            return True
        else:
            return False
    
    def __check_ckind(self, ckind):
        return ckind in self.ckind
    
    def __check_options(self, card, master):
        for func, args, kwargs in self.opt_filters:
            if not func(card, master, *args, **kwargs):
                return False
        return True
    
    def clone(self):
        ins = CardListFilter(self.ckind, self.maxrare, self.ckind)
        ins.opt_filters = self.opt_filters[:]
        return ins
    
    def check(self, card, master):
        """カードをリストに並べるか確認.
        """
        if self.__check_ctype(master.ctype) and \
                self.__check_rare(master.rare) and \
                self.__check_ckind(master.ckind) and \
                self.__check_options(card, master):
            return True
        else:
            return False
    
    def add_optional_filter(self, func, *args, **kwargs):
        """確認項目の追加.
        funcの第1引数にCard,第２引数にCardMasterを渡します.
        func(card, master, *args, **kwargs)
        """
        self.opt_filters.append((func, args, kwargs))

