# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID
from platinumegg.app.cabaret.models.base.fields import AppDateTimeField, JsonCharField
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.models.base.util import dict_to_choices

class ReprintTicketTradeShopMaster(BaseMaster):
    """復刻チケット交換所マスター.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    card_id = models.PositiveIntegerField(default=0, verbose_name=u'カードID')
    use_ticketnum = models.PositiveSmallIntegerField(default=0, verbose_name=u'交換する際に使うチケットの枚数')
    stock = models.PositiveIntegerField(default=0, verbose_name=u'交換可能個数')
    ticket_id = models.PositiveIntegerField(default=0, verbose_name=u'ガチャチケット種別', choices=dict_to_choices(Defines.GachaConsumeType.GachaTicketType.CHOICES))
    reprintticket_trade_text = models.PositiveIntegerField(verbose_name=u'復刻チケット交換文言')
    priority = models.PositiveSmallIntegerField(default=0, verbose_name=u'表示優先順位')
    schedule_id = models.PositiveIntegerField(default=0, verbose_name=u'期間')

class ReprintTicketTradeShopPlayerData(BasePerPlayerBaseWithMasterID):
    """復刻チケット交換所のプレイヤー情報.
    """
    class Meta:
        abstract = False
        app_label = settings_sub.APP_NAME
    cnt = models.PositiveIntegerField(default=0, verbose_name=u'交換回数')
    ltime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'最後に交換した時間')

    @staticmethod
    def makeID(uid, mid):
        return (uid << 32) + mid

    @classmethod
    def createInstance(cls, makeid):
        ins = cls()
        ins.id = makeid
        ins.uid = (makeid >> 32)
        ins.mid = makeid & 0xffffffff
        ins.cnt = 0
        return ins
