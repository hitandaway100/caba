# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMasterWithThumbnail
from platinumegg.app.cabaret.models.Player import BasePerPlayerBase
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.present import PrizeData
from platinumegg.app.cabaret.models.base.fields import AppDateTimeField
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class ShopItemMaster(BaseMasterWithThumbnail):
    """ショップに並べる商品のマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    ITEM_LENGTH = 3
    
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    schedule = models.PositiveIntegerField(default=0, verbose_name=u'期間')
    consumetype = models.PositiveSmallIntegerField(default=Defines.ShopConsumeType.PAYMENT, verbose_name=u'消費するもの', choices=Defines.ShopConsumeType.NAMES.items())
    price = models.PositiveIntegerField(default=0, verbose_name=u'値段')
    stock = models.PositiveSmallIntegerField(default=0, verbose_name=u'在庫')
    itype0 = models.PositiveSmallIntegerField(default=0, verbose_name=u'商品種別0', choices=dict_to_choices(Defines.ItemType.BUY_ABLE_TYPES))
    iid0 = models.PositiveIntegerField(default=0, verbose_name=u'商品ID0')
    inum0 = models.PositiveIntegerField(default=0, verbose_name=u'商品個数0')
    itype1 = models.PositiveSmallIntegerField(default=0, verbose_name=u'商品種別1', choices=dict_to_choices(Defines.ItemType.BUY_ABLE_TYPES))
    iid1 = models.PositiveIntegerField(default=0, verbose_name=u'商品ID1')
    inum1 = models.PositiveIntegerField(default=0, verbose_name=u'商品個数1')
    itype2 = models.PositiveSmallIntegerField(default=0, verbose_name=u'商品種別2', choices=dict_to_choices(Defines.ItemType.BUY_ABLE_TYPES))
    iid2 = models.PositiveIntegerField(default=0, verbose_name=u'商品ID2')
    inum2 = models.PositiveIntegerField(default=0, verbose_name=u'商品個数2')
    pri = models.PositiveSmallIntegerField(default=0, verbose_name=u'優先順位')
    beginer = models.BooleanField(default=False, verbose_name=u'初心者用', choices={True:u'初心者限定',False:u'通常'}.items())
    
    def getItemList(self, num=1):
        """設定されているアイテム.
        """
        items = {}
        for i in xrange(ShopItemMaster.ITEM_LENGTH):
            itype = getattr(self, 'itype%d' % i)
            iid = getattr(self, 'iid%d' % i)
            inum = getattr(self, 'inum%d' % i) * num
            key = (itype << 32) + iid
            if inum == 0:
                continue
            elif itype == Defines.ItemType.CARD and 0 < iid:
                prize = items.get(key) or PrizeData.create(cardid=iid, cardnum=0)
                prize.cardnum += inum
                items[key] = prize
            elif itype == Defines.ItemType.ITEM and 0 < iid:
                prize = items.get(key) or PrizeData.create(itemid=iid, cardnum=0)
                prize.itemnum += inum
                items[key] = prize
            elif itype == Defines.ItemType.RAREOVERTICKET:
                prize = items.get(key) or PrizeData.create()
                prize.rareoverticket += inum
                items[key] = prize
            elif itype == Defines.ItemType.TRYLUCKTICKET:
                prize = items.get(key) or PrizeData.create()
                prize.ticket += inum
                items[key] = prize
            elif itype == Defines.ItemType.MEMORIESTICKET:
                prize = items.get(key) or PrizeData.create()
                prize.memoriesticket += inum
                items[key] = prize
            elif itype == Defines.ItemType.GACHATICKET:
                prize = items.get(key) or PrizeData.create()
                prize.gachaticket += inum
                items[key] = prize
            elif itype == Defines.ItemType.GOLDKEY:
                prize = items.get(key) or PrizeData.create()
                prize.goldkey += inum
                items[key] = prize
            elif itype == Defines.ItemType.GOLDKEY:
                prize = items.get(key) or PrizeData.create()
                prize.goldkey += inum
                items[key] = prize
            elif itype == Defines.ItemType.SILVERKEY:
                prize = items.get(key) or PrizeData.create()
                prize.silverkey += inum
                items[key] = prize
            elif itype == Defines.ItemType.EVENT_GACHATICKET:
                prize = items.get(key) or PrizeData.create(eventticket_id=iid)
                prize.eventticket_num += inum
                items[key] = prize
            elif itype == Defines.ItemType.CABARETCLUB_SPECIAL_MONEY:
                prize = items.get(key) or PrizeData.create()
                prize.cabaclub_money += inum
                items[key] = prize
            elif itype == Defines.ItemType.CABARETCLUB_HONOR_POINT:
                prize = items.get(key) or PrizeData.create()
                prize.cabaclub_honor += inum
                items[key] = prize
            else:
                raise CabaretError(u'商品設定に誤りがあります.id=%d' % self.id, CabaretError.Code.INVALID_MASTERDATA)
        return items.values()

class ShopItemBuyData(BasePerPlayerBase):
    """ショップの購入情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'マスターID')
    cnt = models.PositiveIntegerField(default=0, verbose_name=u'本日購入回数')
    cnt_total = models.PositiveIntegerField(default=0, verbose_name=u'総購入回数')
    btime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'最終購入時間')
    
    def getTodayBuyCnt(self, now=None):
        now = now or OSAUtil.get_now()
        if DateTimeUtil.judgeSameDays(now, self.btime):
            return self.cnt
        else:
            return 0
    
    def addBuyCnt(self, cnt=1, now=None):
        self.cnt = self.getTodayBuyCnt(now) + cnt
        self.cnt_total += cnt
        self.btime = now or OSAUtil.get_now()
