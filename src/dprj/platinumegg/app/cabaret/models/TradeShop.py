# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID
from platinumegg.app.cabaret.models.base.fields import AppDateTimeField, JsonCharField
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.models.base.util import dict_to_choices

class TradeShopMaster(BaseMaster):
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    schedule = models.PositiveIntegerField(default=0, verbose_name=u'期間')
    trade_shop_item_master_ids = JsonCharField(default=list, verbose_name=u'TradeShopItemMasterのIDのリスト',help_text=u'')

class TradeShopItemMaster(BaseMaster):
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    itype = models.PositiveSmallIntegerField(verbose_name=u'アイテムタイプ', choices=dict_to_choices(Defines.ItemType.TRADE_TYPES))
    itemid = models.PositiveIntegerField(default=0, verbose_name=u'アイテムID')
    itemnum = models.PositiveIntegerField(default=0, verbose_name=u'一回の交換で獲得できる個数')
    stock = models.PositiveIntegerField(default=0, verbose_name=u'交換可能個数')
    use_point = models.PositiveSmallIntegerField(default=0, verbose_name=u'交換する際に使うポイント')
    ticketname = models.CharField(max_length=48, default='', verbose_name=u'ガチャチケット名', blank=True)
    ticketthumb = models.CharField(max_length=48, default='', verbose_name=u'ガチャチケットサムネ', blank=True)
    additional_ticket_id = models.PositiveIntegerField(default=0, verbose_name=u'追加ガチャチケット種別', choices=dict_to_choices(Defines.GachaConsumeType.GachaTicketType.CHOICES), blank=True)
    pt_change_text = models.PositiveIntegerField(verbose_name=u'Pt交換文言')

class TradeShopPlayerData(BasePerPlayerBaseWithMasterID):
    """アイテム交換のプレイヤー情報.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME
    cnt = models.PositiveIntegerField(default=0, verbose_name=u'期間中交換回数')
    ltime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'最後に交換した時間')

    @staticmethod
    def makeID(uid, tradeshopitemid):
        return (uid << 32) + tradeshopitemid

    @classmethod
    def createInstance(cls, makeid):
        ins = cls()
        ins.id = makeid
        ins.uid = (makeid >> 32)
        ins.mid = makeid & 0xffffffff
        ins.cnt = 0
        return ins
