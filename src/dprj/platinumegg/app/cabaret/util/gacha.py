# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Card import CardMaster, CardSortMaster
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.apprandom import AppRandom
from platinumegg.app.cabaret.models.Gacha import GachaGroupMaster
from defines import Defines
import urllib

class GachaUtil:
    """
    """
    
    @staticmethod
    def makeGachaEffectPath(gachamaster):
        if gachamaster.consumetype == Defines.GachaConsumeType.RANKING:
            # ランキングガチャ.
            effectpath = 'gacharank/effect2.html'
        elif gachamaster.consumetype == Defines.GachaConsumeType.CHRISTMAS:
            # クリスマスガチャ.
            effectpath = 'gachaxmas/effect2.html'
        elif gachamaster.consumetype == Defines.GachaConsumeType.FUKUBUKURO:
            # 福袋ガチャ(新年度verに切り替え).
            effectpath = 'gachahappybag2/effect2.html'
        elif gachamaster.consumetype == Defines.GachaConsumeType.FUKUBUKURO2016:
            # 福袋ガチャ 2016ver.
            effectpath = 'gachahappybag201608/effect2.html'
        elif gachamaster.consumetype == Defines.GachaConsumeType.FUKUBUKURO2017:
            # 福袋ガチャ　2017ver.
            effectpath = 'gachahappybag201701/effect2.html'
        elif gachamaster.consumetype == Defines.GachaConsumeType.XMAS_OMAKE:
            # クリスマスガチャ 2015.
            effectpath = 'gachaxmas2015/effect2.html'
        elif gachamaster.consumetype in Defines.GachaConsumeType.PREMIUM_TYPES:
            effectpath = 'gachagold/effect2.html'
        elif gachamaster.consumetype == Defines.GachaConsumeType.SCOUTEVENT and Defines.SCOUTEVENTGACHA_USE_EXCLUSIVE_USE_EFFECT:
            if Defines.SCOUTEVENTGACHA_FOR_VALENTINE:
                effectpath = 'gachascev/effect2.html'
            else:
                effectpath = 'gachacastmedal/effect2.html'
        else:
            effectpath = 'gachanormal/effect2.html'
        return effectpath
    
    @staticmethod
    def makeGachaDataUrl(v_player, gachamaster, page=0, lottery_point=0, morecast=0):
        dataUrl = 'gacha/%d/%s/%s/%s/%d' % (gachamaster.id, urllib.quote(v_player.req_alreadykey, ''), page, lottery_point, morecast)
        return dataUrl

class GachaMasterSet():
    """
    """
    def __init__(self, gachamaster, gachaboxmaster, schedulemaster=None):
        self.__gachamaster = gachamaster
        self.__gachaboxmaster = gachaboxmaster
        self.__schedulemaster = schedulemaster
    
    def __getattr__(self, name):
        if self.__dict__.has_key(name):
            return self.__dict__[name]
        else:
            for model in (self.__gachamaster, self.__gachaboxmaster):
                v = getattr(model, name, None)
                if v is not None:
                    return v
            raise AttributeError('%s instance has no attribute %s.' % (self.__class__, name))
    @property
    def master(self):
        return self.__gachamaster
    @property
    def boxmaster(self):
        return self.__gachaboxmaster
    @property
    def schedulemaster(self):
        return self.__schedulemaster

class GachaBoxCardData:
    """ガチャBOX内カード情報.
    """
    def __init__(self, cardid, rate, point=0):
        self.__cardid = cardid
        self.__rate = rate
        self.__point = point
    
    @staticmethod
    def createByTableData(data):
        try:
            cardid = int(data['id'])
            rate = int(data['rate'])
            point = int(data.get('point', 0))
        except:
            raise CabaretError(u'ガチャのBOX内容が不正です.', CabaretError.Code.INVALID_MASTERDATA)
        return GachaBoxCardData(cardid, rate, point)
    
    @property
    def card(self):
        return self.__cardid
    
    @property
    def rate(self):
        return self.__rate
    
    @property
    def point(self):
        return self.__point
    
    def validate(self, model_mgr=None):
        model_mgr = model_mgr or ModelRequestMgr()
        if model_mgr.get_model(CardMaster, self.__cardid) is None:
            raise CabaretError(u'ガチャのBOXのグループに存在しないキャストが含まれています.cardid=%d' % self.__cardid, CabaretError.Code.INVALID_MASTERDATA)
    
    def to_data(self):
        """DB用のデータ.
        """
        return {
            'id' : self.card,
            'rate' : self.rate,
            'point' : self.point,
        }

class GachaBoxGroupData:
    """ガチャBOX内グループ情報.
    """
    def __init__(self, groupid, rate, num=0):
        self.__groupid = groupid
        self.__rate = rate
        self.__num = num
    
    @staticmethod
    def createByBoxData(data):
        try:
            groupid = int(data['id'])
            rate = int(data['rate'])
            num = int(data.get('num', 0))
        except:
            raise CabaretError(u'ガチャのBOX内容が不正です.', CabaretError.Code.INVALID_MASTERDATA)
        return GachaBoxGroupData(groupid, rate, num)
    
    @property
    def group(self):
        return self.__groupid
    
    @property
    def rate(self):
        return self.__rate
    
    @property
    def num(self):
        return self.__num
    
    def validate(self, model_mgr=None):
        model_mgr = model_mgr or ModelRequestMgr()
        if model_mgr.get_model(GachaGroupMaster, self.__groupid) is None:
            raise CabaretError(u'ガチャのBOXに存在しないグループが含まれています.groupid=%d' % self.__groupid, CabaretError.Code.INVALID_MASTERDATA)
    
    def to_data(self):
        """DB用のデータ.
        """
        data = {
            'id' : self.group,
            'rate' : self.rate,
        }
        if 0 < self.num:
            data['num'] = self.num
        return data
    
    def checkSelectable(self, playcnt):
        """選択可能なグループなのか検証.
        """
        if self.num == 0:
            # 何度でも選択可能.
            return True
        elif playcnt < self.num:
            # 上限に達していない.
            return True
        return False

class GachaBoxGroup:
    """ガチャBox.
    """
    def __init__(self, gachagroupmaster):
        table = gachagroupmaster.table
        carddata_list = []
        rate_total = 0
        
        for data in table:
            carddata = GachaBoxCardData.createByTableData(data)
            if 0 < carddata.rate:
                carddata_list.append(carddata)
                rate_total += carddata.rate
        
        self.__carddata_list = carddata_list
        self.__rate_total = rate_total
        self.__gachagroupmaster = gachagroupmaster
    
    @property
    def id(self):
        return self.__gachagroupmaster.id
    
    @property
    def name(self):
        return self.__gachagroupmaster.name
    
    @property
    def rare(self):
        return self.__gachagroupmaster.rare
    
    @property
    def rate_total(self):
        return self.__rate_total
    
    @property
    def carddata_list(self):
        return self.__carddata_list
    
    def select_obj(self, rand=None):
        """グループの中から選別.
        """
        rand = rand or AppRandom()
        v = rand.getIntN(self.rate_total)
        
        for carddata in self.__carddata_list:
            v -= carddata.rate
            if v < 0:
                break
        return carddata
    
    def select(self, rand=None):
        """グループの中から選別.
        """
        return self.select_obj(rand).card
    
    def validate(self, model_mgr=None):
        if len(self.__carddata_list) < 1:
            raise CabaretError(u'ガチャのBOXグループが空またはrateが全て0です.GachaGroupMaster.id=%d' % self.id, CabaretError.Code.INVALID_MASTERDATA)
        model_mgr = model_mgr or ModelRequestMgr()
        for carddata in self.__carddata_list:
            carddata.validate(model_mgr)
            cardsortmaster = model_mgr.get_model(CardSortMaster, carddata.card)
            if cardsortmaster is None or (self.rare != Defines.Rarity.ALL and cardsortmaster.rare != self.rare):
                raise CabaretError(u'ガチャのBOXグループに設定できないキャストが混ざっています.GachaGroupMaster.id=%d, card=%d' % (self.id, carddata.card), CabaretError.Code.INVALID_MASTERDATA)
        if AppRandom.RAND_MAX < self.rate_total:
            raise CabaretError(u'rateの合計が最大値(65535)を超えています.%s' % self.id, CabaretError.Code.INVALID_MASTERDATA)

class GachaBox:
    """ガチャBox.
    """
    def __init__(self, gachamaster, playdata, blank=False, special_box=None):
        if playdata is None or gachamaster.boxid != playdata.mid:
            raise CabaretError('GachaPlayDataのインスタンスは必須です')
        
        self.__playdata = playdata
        
        groupdata_list, groupdata_dict, rate_total, rest, num_total = self.__aggregateBoxData(gachamaster.box, blank)
        
        self.__groupdata_list = groupdata_list
        self.__groupdata_dict = groupdata_dict
        self.__rate_total = rate_total
        self.__rest = rest
        self.__num_total = num_total
        
        self.__gachamaster = gachamaster
        self.__special_box = special_box or {}
        
        if rest == -1 and AppRandom.RAND_MAX < rate_total:
            raise CabaretError(u'rateの合計が最大値(65535)を超えています.%s' % gachamaster.boxid, CabaretError.Code.INVALID_MASTERDATA)
        
        self.__blank = blank
    
    def __aggregateBoxData(self, box, blank=False):
        groupdata_list = []
        groupdata_dict = {}
        rate_total = 0
        rest = 0
        num_total = 0
        
        for data in box:
            groupdata = GachaBoxGroupData.createByBoxData(data)
            if groupdata.rate < 1:
                continue
            elif 0 < groupdata.num:
                v = max(0, groupdata.num - self.__playdata.getGroupCount(groupdata.group))
                if v < 1 and not blank:
                    # もう出ない.
                    continue
                if rest != -1:
                    rest += v
                    num_total += groupdata.num
            else:
                rest = -1
                num_total = -1
                
            groupdata_list.append(groupdata)
            groupdata_dict[groupdata.group] = groupdata
            rate_total += groupdata.rate
        return (
            groupdata_list,
            groupdata_dict,
            rate_total,
            rest,
            num_total
        )
    
    @property
    def is_empty(self):
        """ボックス終了.
        """
        return self.get_rest_num() < 1
    
    @property
    def is_boxgacha(self):
        """ボックスガチャか.
        """
        return 0 < self.num_total
    
    @property
    def rate_total(self):
        return self.__rate_total
    
    @property
    def rest(self):
        """在庫数.
        """
        return self.__rest
    
    @property
    def num_total(self):
        """在庫総数.
        """
        return self.__num_total
    
    def get_group_id_list(self, cnt=None):
        if cnt is not None and self.__special_box.has_key(cnt):
            _, groupdata_dict, _, _, _ = self.__aggregateBoxData(self.__special_box[cnt], self.__blank)
            return groupdata_dict.keys()
        return self.__groupdata_dict.keys()
    
    def get_groupdata_list(self):
        return self.__groupdata_list[:]
    
    def get_group_totalnum(self, groupid):
        groupdata = self.__groupdata_dict.get(groupid)
        num = 0
        if groupdata is None:
            return None
        elif 0 < groupdata.num:
            num = groupdata.num
        else:
            num = -1
        return num
    
    def get_group_restnum(self, groupid):
        totalnum = self.get_group_totalnum(groupid)
        if totalnum == -1:
            rest = -1
        else:
            cnt = self.__playdata.getGroupCount(groupid) if self.__playdata else 0
            rest = max(0, totalnum - cnt)
        return rest
    
    def get_group_rate(self, groupid):
        groupdata = self.__groupdata_dict.get(groupid)
        if groupdata is None:
            return 0
        
        if self.num_total == -1:
            return groupdata.rate
        else:
            cnt = self.__playdata.getGroupCount(groupdata.group) if self.__playdata else 0
            return groupdata.num - cnt
    
    def get_rest_num(self):
        """在庫数.
        """
        if self.rest == -1:
            return Defines.VALUE_MAX
        else:
            return self.rest
    
    def get_total_num(self):
        """在庫総数.
        """
        if self.num_total == -1:
            return Defines.VALUE_MAX
        else:
            return self.num_total
    
    def select(self, rand=None, cnt=None):
        """グループを選別.
        """
        if self.is_empty:
            raise CabaretError(u'BOXが空っぽです.リセットしましょう')
        
        is_special = False
        
        rand = rand or AppRandom()
        
        if self.__special_box.get(cnt):
            # 特別なOdds.なんか無理やり.
            groupdata_list, _, rate_total, _, _ = self.__aggregateBoxData(self.__special_box[cnt])
            is_special = True
        else:
            groupdata_list, rate_total = (self.__groupdata_list, self.__rate_total)
        
        if self.num_total == -1:
            v = rand.getIntN(rate_total)
            getRate = lambda x:x.rate
        else:
            v = rand.getIntN(self.rest)
            getRate = lambda x:(x.num - self.__playdata.getGroupCount(x.group))
        
        groupdata = None
        for index, groupdata in enumerate(groupdata_list):
            groupdata = groupdata_list[index]
            v -= getRate(groupdata)
            if v < 0:
                break
        
        if groupdata and 0 < groupdata.num:
            self.__playdata.addGroupCount(groupdata.group)
            if groupdata.num <= self.__playdata.getGroupCount(groupdata.group):
                # このグループはもう選べない.
                self.__groupdata_list.pop(index)
                self.rate_total -= groupdata.rate
            if self.__rest != -1:
                self.__rest -= 1
        
        return groupdata.group, is_special
    
    def validate(self):
        if self.__gachamaster.consumetype in Defines.GachaConsumeType.BOX_TYPES and self.__special_box:
            raise CabaretError(u'BOXガチャでは回数ごとのOdds指定はできません', code=CabaretError.Code.INVALID_MASTERDATA)
