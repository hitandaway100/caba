# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseModel
from platinumegg.app.cabaret.models.base.fields import PositiveBigAutoField,\
    ObjectField, AppDateTimeField
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines

class UserLogBase(BaseModel):
    """ユーザログ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = True
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    uid = models.PositiveIntegerField(verbose_name=u'ユーザーID')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'作成した時間')
    data = ObjectField(verbose_name=u'データ')
    
    @classmethod
    def create(cls, uid, *args, **kwargs):
        ins = cls()
        ins.uid = uid
        ins._setData(*args, **kwargs)
        return ins
    
    def _setData(self, *args, **kwargs):
        """各ログごとのデータを書き込む.
        """
        raise NotImplementedError()
    
    def getData(self, key, default=None):
        data = self.data or {}
        return data.get(key, default)

class UserLogLoginBonus(UserLogBase):
    """ログインボーナス"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, ldays, pdays, tldays, tldays_view):
        self.data = {
            'ldays' : ldays,
            'pdays' : pdays,
            'tldays' : tldays,
            'tldays_view' : tldays_view,
        }
    @property
    def ldays(self):
        return self.data.get('ldays', 0)
    @property
    def pdays(self):
        return self.data.get('pdays', 0)

class UserLogLoginBonusTimeLimited(UserLogBase):
    """期間で区切られたログインボーナス"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, mid, days):
        self.data = {
            'mid' : mid,
            'days' : days,
        }
    @property
    def mid(self):
        return self.data.get('mid', 0)
    @property
    def days(self):
        return self.data.get('days', 0)

class UserLogComeBack(UserLogBase):
    """カムバックキャンペーン受け取り"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, mid, days):
        self.data = {
            'mid' : mid,
            'days' : days,
        }
    @property
    def mid(self):
        return self.data.get('mid', 0)
    @property
    def days(self):
        return self.data.get('days', 0)

class UserLogCardGet(UserLogBase):
    """カード獲得"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, mid, way, autosell=False):
        self.data = {
            'mid' : mid,
            'way' : way,
            'autosell' : autosell,
        }
    @property
    def mid(self):
        return self.data.get('mid', 0)
    @property
    def way(self):
        return Defines.CardGetWayType.NAMES.get(self.data.get('way', -1), u'不明')
    @property
    def autosell(self):
        return self.data.get('autosell', False)

class UserLogCardSell(UserLogBase):
    """カード売却"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, idlist, price, treasure=0):
        self.data = {
            'cardlist' : idlist,
            'price' : price,
            'treasure' : treasure,
        }
    @property
    def cardidlist(self):
        arr = self.data.get('cardlist') or []
        return arr[:]
    @property
    def price(self):
        return self.data.get('price', 0)
    @property
    def treasure(self):
        return self.data.get('treasure', 0)

class UserLogComposition(UserLogBase):
    """教育"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    @staticmethod
    def makeCardData(cardset):
        return {
            'id' : cardset.id,
            'mid' : cardset.master.id,
            'exp' : cardset.card.exp,
        }
    
    def _setData(self, base_cardset, material_cardsetlist, exp_add, is_great_success, skilllevel, skilllevelup):
        self.data = {
            'base' : UserLogComposition.makeCardData(base_cardset),
            'materials' : [UserLogComposition.makeCardData(cardset) for cardset in material_cardsetlist],
            'is_great' : is_great_success,
            'exp' : exp_add,
            'slv' : skilllevel,
            'slvup' : skilllevelup,
        }
    
    @property
    def basecard(self):
        return self.data.get('base')
    @property
    def materiallist(self):
        return self.data.get('materials') or []
    @property
    def is_great(self):
        return self.data.get('is_great')
    @property
    def exp(self):
        return self.data.get('exp', 0)

class UserLogEvolution(UserLogBase):
    """ハメ管理"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    @staticmethod
    def makeCardData(cardset):
        return {
            'id' : cardset.id,
            'mid' : cardset.master.id,
            'level' : cardset.card.level,
            'power' : cardset.power,
        }
    
    def _setData(self, base_cardset, material_cardset, takeover):
        self.data = {
            'base' : UserLogEvolution.makeCardData(base_cardset),
            'material' : UserLogEvolution.makeCardData(material_cardset),
            'takeover' : takeover,
        }
    @property
    def basecard(self):
        return self.data.get('base')
    @property
    def material(self):
        return self.data.get('material')
    @property
    def takeover(self):
        return self.data.get('takeover', 0)

class UserLogLevelUpBonus(UserLogBase):
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

    def _setData(self, mid, prizeid, level):
        self.data = {
            'mid' : mid or Defines.LEVELUP_BONUS_VERSION,
            'prizeid' : prizeid or [],
            'level' : level or 0,
        }
    @property
    def prizeid(self):
        return self.data.get('prizeid') or 0
    @property
    def level(self):
        return self.data.get('level') or 0
    @property
    def mid(self):
        return self.data.get('mid') or 0

class UserLogGacha(UserLogBase):
    """ガチャ"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, mid, continuity, consumevalue, is_first, cardidlist, seat_prizeid, point_add, point_total, point_whole=0, seat_last=None):
        self.data = {
            'mid' : mid,
            'continuity' : continuity,
            'consumevalue' : consumevalue,
            'is_first' : is_first,
            'cardlist' : cardidlist,
            'seat_prizeid' : seat_prizeid or 0,
            'seat_last' : seat_last,
            'point_add' : point_add,
            'point_total' : point_total,
            'point_whole' : point_whole,
        }
    @property
    def mid(self):
        return self.data.get('mid', 0)
    @property
    def continuity(self):
        return self.data.get('continuity', 0)
    @property
    def consumevalue(self):
        return self.data.get('consumevalue', 0)
    @property
    def is_first(self):
        return self.data.get('is_first')
    @property
    def cardidlist(self):
        return self.data.get('cardlist') or []
    @property
    def seat_prizeid(self):
        return self.data.get('seat_prizeid') or 0
    @property
    def point_add(self):
        return self.data.get('point_add') or 0
    @property
    def point_total(self):
        return self.data.get('point_total') or 0
    @property
    def point_whole(self):
        return self.data.get('point_whole') or 0

class UserLogAreaComplete(UserLogBase):
    """エリアクリア"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    class EventScoutType:
        (
            NONE,
            SCOUT,
            RAID,
            PRODUCE,
        ) = range(4)
    
    def _setData(self, area, eventtype=0):
        self.data = {
            'area' : area,
            'eventtype' : eventtype or UserLogAreaComplete.EventScoutType.NONE,
        }
    @property
    def area(self):
        return self.data.get('area', 0)

class UserLogScoutComplete(UserLogBase):
    """スカウトクリア"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, scout, eventtype=0):
        self.data = {
            'scout' : scout,
            'eventtype' : eventtype or UserLogAreaComplete.EventScoutType.NONE,
        }
    @property
    def scout(self):
        return self.data.get('scout', 0)

class UserLogPresentSend(UserLogBase):
    """プレゼント送信"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, presentid, itype, ivalue, inum, textid):
        self.data = {
            'present' : presentid,
            'itype' : itype,
            'ivalue' : ivalue,
            'inum' : inum,
            'textid' : textid,
        }
    @property
    def presentid(self):
        return self.data.get('present', 0)
    @property
    def itype(self):
        return self.data.get('itype', 0)
    @property
    def ivalue(self):
        return self.data.get('ivalue', 0)
    @property
    def inum(self):
        return self.data.get('inum', 0)
    @property
    def textid(self):
        return self.data.get('textid', 0)

class UserLogPresentReceive(UserLogBase):
    """プレゼント受取"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, presentid):
        self.data = {
            'present' : presentid,
        }
    @property
    def presentid(self):
        return self.data.get('present', 0)

class UserLogItemGet(UserLogBase):
    """アイテム獲得"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, mid, vnum, rnum, vnum_add, rnum_add):
        self.data = {
            'mid' : mid,
            'vnum' : vnum,
            'rnum' : rnum,
            'vnum_add' : vnum_add,
            'rnum_add' : rnum_add,
        }
    @property
    def mid(self):
        return self.data.get('mid', 0)
    @property
    def vnum(self):
        return self.data.get('vnum', 0)
    @property
    def rnum(self):
        return self.data.get('rnum', 0)
    @property
    def vnum_add(self):
        return self.data.get('vnum_add', 0)
    @property
    def rnum_add(self):
        return self.data.get('rnum_add', 0)

class UserLogTicketGet(UserLogBase):
    """追加分ガチャチケット獲得"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, tickettype, num, addnum):
        self.data = {
            'tickettype' : tickettype,
            'num' : num,
            'addnum' : addnum,
        }
    @property
    def tickettype(self):
        return self.data.get('tickettype', 0)
    @property
    def num(self):
        return self.data.get('num', 0)
    @property
    def addnum(self):
        return self.data.get('addnum', 0)

class UserLogItemUse(UserLogBase):
    """アイテム使用"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, mid, vnum, rnum, vnum_rem, rnum_rem):
        self.data = {
            'mid' : mid,
            'vnum' : vnum,
            'rnum' : rnum,
            'vnum_rem' : vnum_rem,
            'rnum_rem' : rnum_rem,
        }
    @property
    def mid(self):
        return self.data.get('mid', 0)
    @property
    def vnum(self):
        return self.data.get('vnum', 0)
    @property
    def rnum(self):
        return self.data.get('rnum', 0)
    @property
    def vnum_rem(self):
        return self.data.get('vnum_rem', 0)
    @property
    def rnum_rem(self):
        return self.data.get('rnum_rem', 0)

class UserLogTreasureGet(UserLogBase):
    """宝箱獲得"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, treasuretype, mid):
        self.data = {
            'type' : treasuretype,
            'mid' : mid,
        }
    @property
    def treasuretype(self):
        return self.data.get('type', -1)
    @property
    def mid(self):
        return self.data.get('mid', 0)

class UserLogTreasureOpen(UserLogBase):
    """宝箱開封"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, treasuretype, mid, post_keynum=0):
        self.data = {
            'type' : treasuretype,
            'mid' : mid,
            'post_keynum' : post_keynum,
        }
    @property
    def treasuretype(self):
        return self.data.get('type', -1)
    @property
    def mid(self):
        return self.data.get('mid', 0)

class UserLogTrade(UserLogBase):
    """秘宝交換"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, mid, cabaretking, demiworld):
        self.data = {
            'mid' : mid,
            'cabaretking' : cabaretking,
            'demiworld' : demiworld,
        }
    @property
    def mid(self):
        return self.data.get('mid', 0)
    @property
    def cabaretking(self):
        return self.data.get('cabaretking', 0)
    @property
    def demiworld(self):
        return self.data.get('demiworld', 0)

class UserLogTradeShop(UserLogBase):
    """Pt交換所"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

    def _setData(self, shopid, shopitemid, point):
        self.data = {
            'shopid': shopid,
            'shopitemid': shopitemid,
            'point': point,
        }
    @property
    def shopid(self):
        return self.data.get('shopid', 0)
    @property
    def shopitemid(self):
        return self.data.get('shopitemid', 0)
    @property
    def point(self):
        return self.data.get('point', 0)

class UserLogReprintTicketTradeShop(UserLogBase):
    """復刻チケット交換所"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

    def _setData(self, tradeid, castid, ticketid, num, use_ticketnum, pre_ticketnum):
        self.data = {
            'tradeid': tradeid,
            'castid': castid,
            'ticketid': ticketid,
            'num': num,
            'use_ticketnum': use_ticketnum,
            'pre_ticketnum': pre_ticketnum,
        }
    @property
    def tradeid(self):
        return self.data.get('tradeid', 0)
    @property
    def castid(self):
        return self.data.get('castid', 0)
    @property
    def ticketid(self):
        return self.data.get('ticketid', 0)
    @property
    def num(self):
        return self.data.get('num', 0)
    @property
    def use_ticketnum(self):
        return self.data.get('use_ticketnum', 0)
    @property
    def pre_ticketnum(self):
        return self.data.get('pre_ticketnum', 0)

class UserLogCardStock(UserLogBase):
    """図鑑にカードをストック"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, cardidlist, result_nums):
        self.data = {
            'cards' : cardidlist,
            'nums' : result_nums,
        }
    @property
    def cardidlist(self):
        return self.data.get('cards') or []
    @property
    def result_nums(self):
        return self.data.get('nums') or {}

class UserLogBattleEventPresent(UserLogBase):
    """バトルイベントの贈り物履歴"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, eventid, number, content):
        self.data = {
            'eventid' : eventid,
            'number' : number,
            'content' : content,
        }
    @property
    def eventid(self):
        return self.data.get('eventid', 0)
    @property
    def number(self):
        return self.data.get('number', 0)
    @property
    def content(self):
        return self.data.get('content', 0)

class UserLogScoutEventGachaPt(UserLogBase):
    """カカオの変動履歴"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, eventid, pre, post, add):
        self.data = {
            'eventid' : eventid,
            'pre' : pre,
            'post' : post,
            'add' : add,
        }
    @property
    def eventid(self):
        return self.data.get('eventid', 0)
    @property
    def pt_pre(self):
        return self.data.get('pre', 0)
    @property
    def pt_post(self):
        return self.data.get('post', 0)
    @property
    def pt_add(self):
        return self.data.get('add', 0)

class UserLogRankingGachaWholePrize(UserLogBase):
    """ランキングガチャ総計ポイント報酬受取"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, boxid, prizeidlist, wholepoint):
        self.data = {
            'boxid' : boxid,
            'prizes' : prizeidlist,
            'wholepoint' : wholepoint,
        }
    @property
    def boxid(self):
        return self.data.get('boxid', 0)
    @property
    def prizes(self):
        return self.data.get('prizes') or []
    @property
    def wholepoint(self):
        return self.data.get('wholepoint', 0)

class UserLogCabaClubStore(UserLogBase):
    """キャバクラ経営の店舗の履歴"""
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
        index_together = (('uid','ctime'),)
    class LogType:
        (
            RENTAL,
            CANCEL,
            OPEN,
            CLOSE,
            ADVANCE,
            USER_ACTION,
        ) = range(6)
    
    @classmethod
    def createLogRental(cls, uid, storemaster_id, now, days):
        """レンタル開始ログ.
        """
        ins = cls.create(uid, storemaster_id, UserLogCabaClubStore.LogType.RENTAL, days=days)
        ins.ctime = now
        return ins
    
    @classmethod
    def createLogCancel(cls, uid, storemaster_id, now):
        """レンタル終了ログ.
        """
        ins = cls.create(uid, storemaster_id, UserLogCabaClubStore.LogType.CANCEL)
        ins.ctime = now
        return ins
    
    @classmethod
    def createLogOpen(cls, uid, storemaster_id, now, event_id, cardmidlist, scoutman):
        """開店ログ.
        """
        ins = cls.create(uid, storemaster_id, UserLogCabaClubStore.LogType.OPEN, eid=event_id, card=cardmidlist, scoutm=scoutman)
        ins.ctime = now
        return ins
    
    @classmethod
    def createLogClose(cls, uid, storemaster_id, now):
        """閉店ログ.
        """
        ins = cls.create(uid, storemaster_id, UserLogCabaClubStore.LogType.CLOSE)
        ins.ctime = now
        return ins
    
    @classmethod
    def createLogAdvance(cls, uid, storemaster_id, now, event_id, customer, proceeds, event_counts):
        """時間進行ログ.
        """
        kwargs = {}
        if event_counts:
            kwargs.update(ev=event_counts)
        ins = cls.create(uid, storemaster_id, UserLogCabaClubStore.LogType.ADVANCE, eid=event_id, customer=customer, proceeds=proceeds, **kwargs)
        ins.ctime = now
        return ins
    
    @classmethod
    def createLogUA(cls, uid, storemaster_id, now, event_id):
        """ユーザアクションログ.
        """
        ins = cls.create(uid, storemaster_id, UserLogCabaClubStore.LogType.USER_ACTION, eid=event_id)
        ins.ctime = now
        return ins
    
    def _setData(self, storemaster_id, logtype, **kwargs):
        self.data = {
            'mid' : storemaster_id,
            'type' : logtype,
        }
        self.data.update(**kwargs)
    
    @property
    def storemaster_id(self):
        return self.data.get('mid', 0)
    @property
    def logtype(self):
        return self.data.get('type') or 0
    @property
    def cardmidlist(self):
        return self.data.get('card') or []
    @property
    def scoutman(self):
        return self.data.get('scoutm') or 0
    @property
    def event_id(self):
        return self.data.get('eid', 0)
    @property
    def customer(self):
        return self.data.get('customer', 0)
    @property
    def proceeds(self):
        return self.data.get('proceeds', 0)
    @property
    def days(self):
        return self.data.get('days', 0)
    @property
    def event_counts(self):
        return self.data.get('ev') or dict()

class UserLogScoutEventTipGet(UserLogBase):
    """スカウトイベントチップ獲得.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, eventid, tanzaku_number, tanzaku_num, tanzaku_num_post, tip, tip_post):
        self.data = {
            'eventid' : eventid,
            'number' : tanzaku_number,
            'tanzaku' : tanzaku_num,
            'tanzaku_post' : tanzaku_num_post,
            'tip' : tip,
            'tip_post' : tip_post,
        }
    @property
    def eventid(self):
        return self.data.get('eventid', 0)
    @property
    def tanzaku_number(self):
        return self.data.get('number', -1)
    @property
    def tanzaku_num(self):
        return self.data.get('tanzaku', 0)
    @property
    def tanzaku_num_post(self):
        return self.data.get('tanzaku_post', 0)
    @property
    def tip_num(self):
        return self.data.get('tip', 0)
    @property
    def tip_num_post(self):
        return self.data.get('tip_post', 0)

class UserLogLoginbonusSugoroku(UserLogBase):
    """すごろくログインボーナス.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    def _setData(self, number, squares_id_list):
        self.data = dict(
            number = number,
            squares = squares_id_list
        )
    @property
    def number(self):
        return self.data.get('number', 0)
    @property
    def squares_id_list(self):
        return self.data.get('squares') or []
