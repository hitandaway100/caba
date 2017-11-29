# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.apprandom import AppRandom
from platinumegg.app.cabaret.models.Scout import ScoutMaster
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.app.cabaret.models.Item import ItemMaster
from platinumegg.app.cabaret.models.Happening import HappeningMaster
from platinumegg.app.cabaret.models.EventScout import EventScoutStageMaster
from platinumegg.lib.opensocial.util import OSAUtil

class ScoutEventData:
    """スカウトのイベントデータ.
    """
    @classmethod
    def create(cls, **kwargs):
        raise NotImplementedError()
    
    @classmethod
    def get_type(self):
        raise NotImplementedError()
    
    def __init__(self, data):
        self.data = data

class ScoutEventNone(ScoutEventData):
    """なにもなかった.
    """
    @classmethod
    def create(cls):
        return cls({})
    
    @classmethod
    def get_type(self):
        return Defines.ScoutEventType.NONE

class ScoutEventComplete(ScoutEventData):
    """完了.
    """
    @classmethod
    def create(cls, scoutid):
        return cls({
            'scoutid' : scoutid,
        })
    @classmethod
    def get_type(self):
        return Defines.ScoutEventType.COMPLETE
    @property
    def scoutid(self):
        return self.data['scoutid']

class ScoutEventApNone(ScoutEventData):
    """行動力が足りない.
    """
    @classmethod
    def create(cls, scoutid):
        return cls({
            'scoutid' : scoutid,
        })
    @classmethod
    def get_type(self):
        return Defines.ScoutEventType.AP_NONE
    @property
    def scoutid(self):
        return self.data['scoutid']

class ScoutEventLevelup(ScoutEventData):
    """レベルアップ.
    """
    @classmethod
    def create(cls, level):
        return cls({
            'level' : level,
        })
    @classmethod
    def get_type(self):
        return Defines.ScoutEventType.LEVELUP
    @property
    def level(self):
        return self.data['level']
    
    def set_level(self, level):
        self.data['level'] = level

class ScoutEventGetCard(ScoutEventData):
    """カード獲得.
    """
    @classmethod
    def create(cls, cardid, silhouette=None, is_success=None, heart=0):
        data = {
            'card' : cardid,
            'is_new' : False,
            'silhouette' : silhouette,
            'heart' : heart,
        }
        if is_success is not None:
            data['success'] = is_success
        return cls(data)
    @classmethod
    def get_type(self):
        return Defines.ScoutEventType.GET_CARD
    @property
    def card(self):
        return self.data['card']
    @property
    def is_new(self):
        return self.data['is_new']
    @property
    def silhouette(self):
        return self.data['silhouette']
    @property
    def is_received(self):
        return self.data.has_key('success')
    @property
    def is_success(self):
        return self.data['success']
    @property
    def autosell(self):
        return self.data.get('sellprice', None) is not None and self.data.get('treasure', None) is not None
    @property
    def sellprice(self):
        return self.data.get('sellprice', 0)
    @property
    def sellprice_treasure(self):
        return self.data.get('treasure', 0)
    
    def set_new(self, flag):
        self.data['is_new'] = flag
    
    def set_result(self, flag, sellprice=None, sellprice_treasure=None):
        self.data['success'] = flag
        self.data['sellprice'] = sellprice
        self.data['treasure'] = sellprice_treasure

class ScoutEventGetItem(ScoutEventData):
    """アイテム獲得.
    """
    @classmethod
    def create(cls, itemid):
        return cls({
            'item' : itemid,
        })
    @classmethod
    def get_type(self):
        return Defines.ScoutEventType.GET_ITEM
    @property
    def item(self):
        return self.data['item']

class ScoutEventEventGacha(ScoutEventData):
    """イベントガチャポイント獲得.
    """
    @classmethod
    def create(cls, point):
        return cls({
            'point' : point,
        })
    @classmethod
    def get_type(self):
        return Defines.ScoutEventType.EVENTGACHA
    @property
    def point(self):
        return self.data['point']

class ScoutEventHappening(ScoutEventData):
    """ハプニング発生.
    """
    @classmethod
    def create(cls, happeningid):
        return cls({
            'happening' : happeningid,
        })
    @classmethod
    def get_type(self):
        return Defines.ScoutEventType.HAPPENING
    @property
    def happening(self):
        return self.data['happening']

class ScoutEventGetTreasure(ScoutEventData):
    """宝箱発見.
    """
    @classmethod
    def create(cls, treasuretype):
        return cls({
            'treasuretype' : treasuretype,
        })
    @classmethod
    def get_type(self):
        return Defines.ScoutEventType.GET_TREASURE
    @property
    def treasuretype(self):
        return self.data['treasuretype']

class ScoutEventLoveTimeStar(ScoutEventData):
    """スカウトイベントの逢引ラブタイムシステムの星.
    """
    @classmethod
    def create(cls, num):
        return cls({
            'num' : num,
        })
    @classmethod
    def get_type(self):
        return Defines.ScoutEventType.LOVETIME_STAR
    @property
    def num(self):
        return self.data['num']
    
    def set_star(self, num):
        self.data['num'] = num

TABLE = {
    Defines.ScoutEventType.NONE : ScoutEventNone,
    Defines.ScoutEventType.COMPLETE : ScoutEventComplete,
    Defines.ScoutEventType.AP_NONE : ScoutEventApNone,
    Defines.ScoutEventType.LEVELUP : ScoutEventLevelup,
    Defines.ScoutEventType.GET_CARD : ScoutEventGetCard,
    Defines.ScoutEventType.GET_ITEM : ScoutEventGetItem,
    Defines.ScoutEventType.HAPPENING : ScoutEventHappening,
    Defines.ScoutEventType.GET_TREASURE : ScoutEventGetTreasure,
    Defines.ScoutEventType.EVENTGACHA : ScoutEventEventGacha,
    Defines.ScoutEventType.LOVETIME_STAR : ScoutEventLoveTimeStar,
}

def get_class_by_type(eventtype):
    data_cls = TABLE.get(eventtype, None)
    if data_cls is None:
        raise CabaretError(u'未実装のスカウト内イベント:%d' % eventtype)
    return data_cls


class ScoutDropItemData():
    """ドロップアイテム情報.
    タイプ(カード or トロフィ or アイテム).
    マスターID.
    タイプ一致.
    重み.
    """
    def __init__(self, **data):
        self.itype = data.get('itemtype', None)
        self.mid = data.get('master', None)
        self.filters = data.get('filters', {})
        self.rate = data.get('rate', 0)
        self.silhouette = data.get('silhouette', None)
        self.heart = data.get('heart', 0)
        self.__data = data
        if self.itype is None or not self.itype in (Defines.ItemType.CARD, Defines.ItemType.ITEM):
            raise CabaretError(u'想定外のタイプです:%s' % self.itype, CabaretError.Code.INVALID_MASTERDATA)
        elif not self.mid:
            raise CabaretError(u'マスターIDが設定されていません', CabaretError.Code.INVALID_MASTERDATA)
    
    def check(self, player):
        # これ直したいけどいつ直そうか.
#        if self.itype == Defines.ItemType.CARD and player.cardlimit <= self.__data.get('cardnum', 0):
#            return False
        
        for key,args in self.filters.items():
            arr = key.split('__', 1)
            attname, kw = arr if len(arr) == 2 else (arr[0], None)
            if self.itype == Defines.ItemType.CARD and player.cardlimit <= self.__data.get('cardnum', 0):
                return False
            elif kw == 'in':
                if not getattr(player, attname) in args:
                    return False
            else:
                if getattr(player, attname) != args:
                    return False
        return True
    
    def get_dropitem_dict(self):
        return self.__data
    
    @staticmethod
    def create(itemtype, master, filters=None, rate=None):
        return ScoutDropItemData(itemtype=itemtype, master=master, filters=filters or {}, rate=rate)
    
    def validate(self):
        master = None
        if self.itype == Defines.ItemType.CARD:
            master = CardMaster.getByKey(self.mid)
        elif self.itype == Defines.ItemType.ITEM:
            master = ItemMaster.getByKey(self.mid)
        if master is None:
            raise CabaretError(u'存在しないマスターがドロップアイテムテーブルに設定されています.')

class ScoutDropItemSelector():
    """スカウトのドロップアイテムの選別屋さん.
    """
    def __init__(self, player, scoutmaster, cardnum):
        self.__scoutmaster = scoutmaster
        self.__rate_total = 0
        data_list = []
        if isinstance(scoutmaster, ScoutMaster) or isinstance(scoutmaster, EventScoutStageMaster):
            dropitems = scoutmaster.dropitems
        else:
            dropitems = scoutmaster.items
        try:
            data_list = ScoutDropItemSelector.dropitemsTodatalist(dropitems, player, cardnum)
        except:
            raise CabaretError(u'スカウトのドロップアイテムテーブルがおかしいみたいです.id=%d' % scoutmaster.id, CabaretError.Code.INVALID_MASTERDATA)
        for data in data_list:
            self.__rate_total += data.rate
        self.__data_list = data_list
    
    @staticmethod
    def dropitemsTodatalist(dropitems, player, cardnum=0):
        datalist = []
        for dropitem in dropitems:
            _dropitem = {
                'cardnum' : cardnum,
            }
            _dropitem.update(dropitem)
            data = ScoutDropItemData(**_dropitem)
            if player is None or data.check(player):
                datalist.append(data)
        return datalist
    
    @property
    def rate_total(self):
        return self.__rate_total
    
    def select(self, rand=None):
        """選別.
        """
        if self.__rate_total == 0:
            return None
        elif rand is None or type(rand) == int:
            rand = AppRandom()
        
        v = rand.getIntN(self.__rate_total)
        for data in self.__data_list:
            v -= data.rate
            if v < 1:
                return data
        return None
    
    def validate(self):
        for data in self.__data_list:
            data.validate()

class ScoutHappeningSelector():
    """スカウトのハプニングの選別屋さん.
    """
    def __init__(self, player, scoutmaster, happenings=None):
        self.__scoutmaster = scoutmaster
        self.__rate_total = 0
        
        happenings = happenings or scoutmaster.happenings
        
        data_list = []
        try:
            data_list = ScoutHappeningSelector.tableTodatalist(happenings, player)
        except:
            raise CabaretError(u'スカウトのアイテムテーブルがおかしいみたいです.id=%d' % scoutmaster.id, CabaretError.Code.INVALID_MASTERDATA)
        for data in data_list:
            self.__rate_total += data.rate
        
        self.__data_list = data_list
    
    @staticmethod
    def tableTodatalist(happeningtable, player):
        datalist = []
        for happening in happeningtable:
            data = ScoutHappeningData(**happening)
            if player is None or data.check(player):
                datalist.append(data)
        return datalist
    
    @property
    def rate_total(self):
        return self.__rate_total
    
    def select(self, rand=None, rate_max=10000):
        """選別.
        """
        if self.__rate_total < 1:
            return None
        elif rand is None or type(rand) == int:
            rand = AppRandom()
        
        v = rand.getIntN(self.__rate_total)
        for data in self.__data_list:
            v -= data.rate
            if v < 1:
                return data
        return None
    
    def validate(self):
        for data in self.__data_list:
            data.validate()

class ScoutHappeningData():
    """スカウトのハプニング情報.
    """
    def __init__(self, **data):
        self.__mid = data.get('mid', 0)
        self.__rate = data.get('rate', 0)
        if not self.__mid:
            raise CabaretError(u'マスターIDが設定されていません', CabaretError.Code.INVALID_MASTERDATA)
    @property
    def mid(self):
        return self.__mid
    @property
    def rate(self):
        return self.__rate
    
    @staticmethod
    def create(mid, rate):
        return ScoutHappeningData(mid=mid, rate=rate)
    
    def check(self, player):
        return True
    
    def get_dict(self):
        return {
            'mid' : self.mid,
            'rate' : self.rate,
        }
    
    def validate(self):
        if HappeningMaster.getByKey(self.mid) is None:
            raise CabaretError(u'存在しないハプニングが設定されています', CabaretError.Code.INVALID_MASTERDATA)

class ScoutTreasureSelector():
    """宝箱選別.
    """
    def __init__(self, scoutmaster):
        self.__rate_total = scoutmaster.treasuregold + scoutmaster.treasuresilver + scoutmaster.treasurebronze
        self.__scoutmaster = scoutmaster
    
    def can_select(self):
        return 0 < self.__rate_total
    
    def select(self, rand=None):
        if not self.can_select():
            return None
        elif rand is None:
            rand = AppRandom()
        table = (
            (Defines.TreasureType.GOLD, self.__scoutmaster.treasuregold),
            (Defines.TreasureType.SILVER, self.__scoutmaster.treasuresilver),
            (Defines.TreasureType.BRONZE, self.__scoutmaster.treasurebronze),
        )
        v = rand.getIntN(self.__rate_total)
        for treasure_type, rate in table:
            if 0 < rate and v < rate:
                return treasure_type
            v -= rate
        return None

class ScoutExec:
    
    CONTINUITY_MAX = 10
    
    def __init__(self, player, progressdata, seed, master, nextlevelexp, cardnum=0, do_happening=True, happnings=None, title=None):
        self.ap = player.get_ap()
        self.apmax = player.get_ap_max()
        self.exp = player.exp
        self.result = []
        self.eventlist = []
        self.rand = AppRandom(seed=seed)
        self.happeningselector = None
        self.treasureselector = None
        self.progress = progressdata.progress
        self.master = master
        self.nextlevelexp = nextlevelexp
        self.__exec_cnt = 0
        self.__progressdata = progressdata
        
        self.__eventrate_drop = 1
        self.__eventrate_happening = 0
        self.__eventrate_treasure = 0
        if isinstance(master, ScoutMaster):
            self.__eventrate_drop = master.eventrate_drop
            if do_happening:
                self.__eventrate_happening = master.eventrate_happening
                self.happeningselector = ScoutHappeningSelector(player, master, happnings)
            
            self.treasureselector = ScoutTreasureSelector(master)
            if self.treasureselector.can_select():
                self.__eventrate_treasure = master.eventrate_treasure
        
        self.itemselector = ScoutDropItemSelector(player, master, cardnum)
        
        # 称号効果.
        if title:
            self.__title_effect_gold = title.gold_up
            self.__title_effect_exp = title.exp_up
        else:
            self.__title_effect_gold = 0
            self.__title_effect_exp = 0
        
        self.__player = player
    
    @property
    def is_end(self):
        return 0 < len(self.eventlist)
    
    def end(self):
        if not self.is_end:
            self.addEvent(Defines.ScoutEventType.NONE)
    
    @property
    def is_levelup(self):
        return self.nextlevelexp and self.nextlevelexp.exp <= self.exp
    
    def add_exp(self, exp):
        if self.nextlevelexp:
            self.exp += exp
    
    @property
    def nextexp(self):
        if self.nextlevelexp:
            return self.nextlevelexp.exp
        else:
            return self.exp
    
    @property
    def exec_cnt(self):
        return self.__exec_cnt
    
    def select_event(self):
        """イベント選択.
        """
        eventrate_total = self.__eventrate_drop + self.__eventrate_happening + self.__eventrate_treasure
        if eventrate_total < 1:
            return None
        
        v = self.rand.getIntN(eventrate_total)
        
        if 0 < self.__eventrate_drop and v < self.__eventrate_drop:
            # カードかアイテムがドロップ.
            data = self.itemselector.select(self.rand)
            if data:
                # 何か発見.
                if data.itype == Defines.ItemType.CARD:
                    # カード獲得.
                    return ScoutEventGetCard.create(data.mid)
                elif data.itype == Defines.ItemType.ITEM:
                    # アイテム獲得.
                    return ScoutEventGetItem.create(data.mid)
            return None
        v -= self.__eventrate_drop
        
        if 0 < self.__eventrate_happening and v < self.__eventrate_happening:
            # ハプニング.
            happening = self.happeningselector.select(self.rand)
            if happening:
                return ScoutEventHappening.create(happening.mid)
            return None
        v -= self.__eventrate_happening
        
        if 0 < self.__eventrate_treasure and v < self.__eventrate_treasure:
            # 宝箱発見.
            treasure_type = self.treasureselector.select(self.rand)
            if treasure_type is not None:
                return ScoutEventGetTreasure.create(treasure_type)
            return None
        
        v -= self.__eventrate_treasure
        
        return None
    
    def execute(self, apcost):
        if self.is_end:
            raise CabaretError(u'スカウト実行:終了済み')
        elif self.ap < apcost:
            self.addEvent(Defines.ScoutEventType.AP_NONE, self.master.id)
            self.end()
            return
        elif ScoutExec.CONTINUITY_MAX <= self.__exec_cnt:
            # 一度強制終了.
            self.end()
            return
        
        self.__exec_cnt += 1
        
        ap_pre = self.ap
        self.ap -= apcost
        
        gold_add = int(self.rand.getIntS(self.master.goldmin, self.master.goldmax) * (self.__title_effect_gold + 100) / 100)
        exp_add = int(self.master.exp * (self.__title_effect_exp + 100) / 100)

        # 設定期間中に経験値を指定倍率に上げる.
        if Defines.EXP_START_TIME <= OSAUtil.get_now() <= Defines.EXP_END_TIME:
            exp_add = int(exp_add * Defines.EXP_RATE_OVER)
        exp_pre = self.exp
        self.add_exp(exp_add)
        progress_pre = self.progress
        self.progress += 1
        
        obj = ScoutExec.makeResultObject(self.__player.level,
                                         exp_pre, self.exp, exp_add,
                                         gold_add,
                                         ap_pre, self.ap, self.apmax, apcost, progress_pre, self.progress, self.master.execution)
        self.result.append(obj)
        
        # レベルアップ.
        if self.is_levelup:
            self.addEvent(Defines.ScoutEventType.LEVELUP, self.nextlevelexp.level)
        
        # クリア判定.
        if self.progress == self.master.execution:
            self.addEvent(Defines.ScoutEventType.COMPLETE, self.master.id)
        elif not self.is_end and (self.progress % Defines.SCOUT_EVENT_RATE) == 0:
            event = self.select_event()
            if event:
                self.addEvent(event)
            else:
                self.end()
    
    def addEvent(self, event, *args):
        if not isinstance(event, ScoutEventData):
            eventtype = event
            data_cls = get_class_by_type(eventtype)
            event = data_cls.create(*args)
        self.eventlist.append(event)
    
    @staticmethod
    def makeResultObject(level, exp_pre, exp_post, exp_add, gold_add, ap_pre, ap_post, ap_max, ap_cost, progress_pre, progress_post, execution):
        exp_add = exp_post - exp_pre
        
        return {
            'level':level,
            'exp_pre':exp_pre,
            'exp_post':exp_post,
            'exp_add':exp_add,
            'gold_add':gold_add,
            'ap_pre' : ap_pre,
            'ap_post' : ap_post,
            'ap_max' : ap_max,
            'apcost':ap_cost,
            'progress_pre' : progress_pre,
            'progress' : progress_post,
            'execution' : execution,
        }
    
    def cancelEvent(self):
        # これやだなぁ..
        self.eventlist = []
        self.end()
    
    def aggregatePrizes(self):
        exp_total = 0
        gold_total = 0
        for result in self.result:
            exp_total += result['exp_add']
            gold_total += result['gold_add']
        prize = {
            'gold' : gold_total,
            'exp' : exp_total,
        }
        for event in self.eventlist:
            prize[Defines.ScoutEventType.ENG_NAMES[event.get_type()]] = event
        return prize

class ScoutEventExec:
    
    CONTINUITY_MAX = 10
    
    def __init__(self, player, progressdata, seed, master, nextlevelexp, cardnum=0, do_happening=True, happnings=None, is_lovetime=False, title=None, is_full=None):
        self.ap = player.get_ap()
        self.apmax = player.get_ap_max()
        self.exp = player.exp
        self.result = []
        self.eventlist = []
        self.rand = AppRandom(seed=seed)
        self.happeningselector = None
        self.treasureselector = None
        self.is_cleared = master.stage == progressdata.cleared
        if self.is_cleared and master.stage != progressdata.stage:
            resultlist = progressdata.result.get('result', [])
            if resultlist:
                self.progress = resultlist[-1]['progress']
            else:
                self.progress = master.execution
        else:
            self.progress = progressdata.progress
        self.master = master
        self.nextlevelexp = nextlevelexp
        self.__exec_cnt = 0
        self.__progressdata = progressdata
        
        self.__eventrate_drop = 1
        self.__eventrate_happening = 0
        self.__eventrate_treasure = 0
        self.__eventrate_gachapt = 0
        self.__eventrate_drop = master.eventrate_drop
        self.__eventrate_gachapt = getattr(master, 'eventrate_gachapt', 0)
        if do_happening:
            if is_full:
                self.__eventrate_happening = master.eventrate_happening_full
            else:
                self.__eventrate_happening = master.eventrate_happening
            self.happeningselector = ScoutHappeningSelector(player, master, happnings)
        
        self.treasureselector = ScoutTreasureSelector(master)
        if self.treasureselector.can_select():
            if is_full:
                self.__eventrate_treasure = master.eventrate_treasure_full
            else:
                self.__eventrate_treasure = master.eventrate_treasure
        self.itemselector = ScoutDropItemSelector(player, master, cardnum)
        
        self.__eventpointmin = getattr(master, 'eventpointmin', 0)
        self.__eventpointmax = getattr(master, 'eventpointmax', 0)
        self.__eventrate_lt_star = getattr(master, 'eventrate_lt_star', 0) if not is_lovetime else 0
        
        eventrate_total = self.__eventrate_drop
        eventrate_total += self.__eventrate_happening
        eventrate_total += self.__eventrate_treasure
        eventrate_total += self.__eventrate_gachapt
        eventrate_total += self.__eventrate_lt_star
        self.__eventrate_total = eventrate_total
        
        # 称号効果.
        if title:
            self.__title_effect_gold = title.gold_up
            self.__title_effect_exp = title.exp_up
        else:
            self.__title_effect_gold = 0
            self.__title_effect_exp = 0
            
        self.__player = player
    
    @property
    def is_end(self):
        return 0 < len(self.eventlist)
    
    @property
    def exec_cnt(self):
        return self.__exec_cnt
    
    def end(self):
        if not self.is_end:
            self.addEvent(Defines.ScoutEventType.NONE)
    
    @property
    def is_levelup(self):
        return self.nextlevelexp and self.nextlevelexp.exp <= self.exp
    
    def add_exp(self, exp):
        if self.nextlevelexp:
            self.exp += exp
    
    @property
    def nextexp(self):
        if self.nextlevelexp:
            return self.nextlevelexp.exp
        else:
            return self.exp
    
    def select_event(self):
        """イベント選択.
        """
        if self.__eventrate_total < 1:
            return None
        
        v = self.rand.getIntN(self.__eventrate_total)
        
        if 0 <= v < self.__eventrate_drop:
            # カードかアイテムがドロップ.
            data = self.itemselector.select(self.rand)
            if data:
                # 何か発見.
                if data.itype == Defines.ItemType.CARD:
                    # カード獲得.
                    return ScoutEventGetCard.create(data.mid, silhouette=data.silhouette, heart=data.heart)
                elif data.itype == Defines.ItemType.ITEM:
                    # アイテム獲得.
                    return ScoutEventGetItem.create(data.mid)
            return None
        v -= self.__eventrate_drop
        
        if 0 <= v < self.__eventrate_gachapt:
            # イベントガチャポイント.
            point = self.rand.getIntS(self.master.gachaptmin, self.master.gachaptmax)
            return ScoutEventEventGacha.create(point)
        v -= self.__eventrate_gachapt
        
        if 0 <= v < self.__eventrate_happening:
            # ハプニング.
            happening = self.happeningselector.select(self.rand)
            if happening:
                return ScoutEventHappening.create(happening.mid)
            return None
        v -= self.__eventrate_happening
        
        if 0 <= v < self.__eventrate_treasure:
            # 宝箱発見.
            treasure_type = self.treasureselector.select(self.rand)
            if treasure_type is not None:
                return ScoutEventGetTreasure.create(treasure_type)
            return None
        v -= self.__eventrate_treasure
        
        if 0 <= v < self.__eventrate_lt_star:
            # 星.
            num = self.rand.getIntS(self.master.lovetime_star_min, self.master.lovetime_star_max)
            return ScoutEventLoveTimeStar.create(num)
        v -= self.__eventrate_lt_star
        
        return None
    
    def execute(self, apcost):
        if self.is_end:
            raise CabaretError(u'スカウト実行:終了済み')
        elif self.ap < apcost:
            self.addEvent(Defines.ScoutEventType.AP_NONE, self.master.id)
            self.end()
            return
        elif ScoutExec.CONTINUITY_MAX <= self.__exec_cnt:
            # 一度強制終了.
            self.end()
            return
        
        self.__exec_cnt += 1
        
        ap_pre = self.ap
        self.ap -= apcost
        
        gold_add = int(self.rand.getIntS(self.master.goldmin, self.master.goldmax) * (self.__title_effect_gold + 100) / 100)
        exp_add = int(self.master.exp * (self.__title_effect_exp + 100) / 100)

        # 設定期間中に経験値を指定倍率に上げる.
        if Defines.EXP_START_TIME <= OSAUtil.get_now() <= Defines.EXP_END_TIME:
            exp_add = int(exp_add * Defines.EXP_RATE_OVER)

        exp_pre = self.exp
        self.add_exp(exp_add)
        progress_pre = self.progress
        self.progress += 1
        
        # スカウトイベントポイント
        point_add = self.rand.getIntS(self.__eventpointmin, self.__eventpointmax)
        
        obj = ScoutEventExec.makeResultObject(self.__player.level,
                                         exp_pre, self.exp, exp_add,
                                         gold_add,
                                         ap_pre, self.ap, self.apmax, apcost, progress_pre, self.progress, self.master.execution, point_add)
        self.result.append(obj)
        
        # 3ポチ確認.
        eventflag = (self.progress % Defines.SCOUT_EVENT_RATE) == 0
        
        # レベルアップ.
        if self.is_levelup:
            self.addEvent(Defines.ScoutEventType.LEVELUP, self.nextlevelexp.level)
        
        # クリア判定.
        if not self.is_cleared and self.master.execution <= self.progress:
            self.addEvent(Defines.ScoutEventType.COMPLETE, self.master.id)
        elif not self.is_end and eventflag:
            event = self.select_event()
            if event:
                self.addEvent(event)
            else:
                self.end()
    
    def addEvent(self, event, *args):
        if not isinstance(event, ScoutEventData):
            eventtype = event
            data_cls = get_class_by_type(eventtype)
            event = data_cls.create(*args)
        self.eventlist.append(event)
    
    @staticmethod
    def makeResultObject(level, exp_pre, exp_post, exp_add, gold_add, ap_pre, ap_post, ap_max, ap_cost, progress_pre, progress_post, execution, point_add):
        exp_add = exp_post - exp_pre
        
        return {
            'level':level,
            'exp_pre':exp_pre,
            'exp_post':exp_post,
            'exp_add':exp_add,
            'gold_add':gold_add,
            'ap_pre' : ap_pre,
            'ap_post' : ap_post,
            'ap_max' : ap_max,
            'apcost':ap_cost,
            'progress_pre' : progress_pre,
            'progress' : progress_post,
            'execution' : execution,
            'point_add': point_add,
        }
    
    def cancelEvent(self):
        # これやだなぁ..
        self.eventlist = []
        self.end()
    
    def aggregatePrizes(self):
        exp_total = 0
        gold_total = 0
        point_total = 0
        for result in self.result:
            exp_total += result['exp_add']
            gold_total += result['gold_add']
            point_total += result['point_add']
        prize = {
            'gold' : gold_total,
            'exp' : exp_total,
            'point' : point_total,
        }
        for event in self.eventlist:
            prize[Defines.ScoutEventType.ENG_NAMES[event.get_type()]] = event
        return prize
