# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster, BaseModel
from platinumegg.app.cabaret.models.base.fields import PositiveBigAutoField,\
    AppDateTimeField, PositiveBigIntegerField
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.models.base.util import dict_to_choices

class PresentBase(BaseModel):
    """プレゼント.
    """
    class Meta:
        abstract = True
    fromid = models.PositiveIntegerField(verbose_name=u'送信したユーザID')
    toid = models.PositiveIntegerField(verbose_name=u'受け取るユーザID')
    itype = models.PositiveSmallIntegerField(verbose_name=u'種別(PM or 引き抜きPt or アイテム or カード)', choices=dict_to_choices(Defines.ItemType.PRESENT_TYPES))
    ivalue = models.PositiveIntegerField(verbose_name=u'値(金額 or Pt or アイテムID or カードID)')
    inum = models.PositiveIntegerField(verbose_name=u'個数(アイテム or カードのみ)', default=0)
    textid = models.PositiveIntegerField(verbose_name=u'テキストID')
    limittime = AppDateTimeField(db_index=True, default=OSAUtil.get_now, verbose_name=u'有効期限')

class Present(PresentBase):
    """プレゼント.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'送信時間')
    
    @staticmethod
    def create(fromid, toid, itype, ivalue, textid=0, limittime=None, inum=1):
        """プレゼント作成.
        """
        ins = Present()
        ins.fromid = fromid
        ins.toid = toid
        ins.itype = itype
        ins.ivalue = ivalue
        ins.textid = textid
        ins.inum = inum
        if limittime:
            ins.limittime = limittime
        else:
            ins.limittime = OSAUtil.get_now() + Defines.PRESENT_RECEIVE_TIMELIMIT
        return ins
    
    @staticmethod
    def createByGold(fromid, toid, gold, textid=0, limittime=None):
        """お金.
        """
        return Present.create(fromid, toid, Defines.ItemType.GOLD, gold, textid, limittime)
    
    @staticmethod
    def createByGachaPt(fromid, toid, point, textid=0, limittime=None):
        """引きぬきポイント.
        """
        return Present.create(fromid, toid, Defines.ItemType.GACHA_PT, point, textid, limittime)
    
    @staticmethod
    def createByItem(fromid, toid, itemmaster, textid=0, limittime=None, num=1):
        """アイテム.
        """
        return Present.create(fromid, toid, Defines.ItemType.ITEM, itemmaster.id, textid, limittime, num)
    
    @staticmethod
    def createByCard(fromid, toid, cardmaster, textid=0, limittime=None, num=1):
        """カード.
        """
        return Present.create(fromid, toid, Defines.ItemType.CARD, cardmaster.id, textid, limittime, num)
    
    @staticmethod
    def createByRareoverTicket(fromid, toid, ticket, textid=0, limittime=None):
        """レア以上チケット.
        """
        return Present.create(fromid, toid, Defines.ItemType.RAREOVERTICKET, ticket, textid, limittime)
    
    @staticmethod
    def createByTicket(fromid, toid, ticket, textid=0, limittime=None):
        """運試しチケット.
        """
        return Present.create(fromid, toid, Defines.ItemType.TRYLUCKTICKET, ticket, textid, limittime)
    
    @staticmethod
    def createByMemoriesTicket(fromid, toid, ticket, textid=0, limittime=None):
        """思い出チケット.
        """
        return Present.create(fromid, toid, Defines.ItemType.MEMORIESTICKET, ticket, textid, limittime)
    
    @staticmethod
    def createByGachaTicket(fromid, toid, ticket, textid=0, limittime=None):
        """引き抜きチケット.
        """
        return Present.create(fromid, toid, Defines.ItemType.GACHATICKET, ticket, textid, limittime)
    
    @staticmethod
    def createByAdditionalTicket(fromid, toid, tickettype, num, textid=0, limittime=None):
        """追加ガチャチケット.
        """
        return Present.create(fromid, toid, Defines.ItemType.ADDITIONAL_GACHATICKET, tickettype, textid, limittime, inum=num)
    
    @staticmethod
    def createByGoldKey(fromid, toid, num, textid=0, limittime=None):
        """金の鍵.
        """
        return Present.create(fromid, toid, Defines.ItemType.GOLDKEY, num, textid, limittime)
    
    @staticmethod
    def createBySilverKey(fromid, toid, num, textid=0, limittime=None):
        """銀の鍵.
        """
        return Present.create(fromid, toid, Defines.ItemType.SILVERKEY, num, textid, limittime)
    
    @staticmethod
    def createByEventGachaTicket(fromid, toid, eventid, num, textid=0, limittime=None):
        """イベントガチャチケット.
        """
        return Present.create(fromid, toid, Defines.ItemType.EVENT_GACHATICKET, eventid, textid, limittime, num)
    
    @staticmethod
    def createByScoutEventTanzaku(fromid, toid, tanzaku_number, num, textid=0, limittime=None):
        """スカウトイベント短冊.
        """
        return Present.create(fromid, toid, Defines.ItemType.SCOUTEVENT_TANZAKU, tanzaku_number, textid, limittime, num)
    
    @staticmethod
    def createByCabaretClubMoney(fromid, toid, value, textid=0, limittime=None):
        """キャバクラシステムの特別なマネー.
        """
        return Present.create(fromid, toid, Defines.ItemType.CABARETCLUB_SPECIAL_MONEY, value, textid, limittime)
    
    @staticmethod
    def createByCabaretClubHonor(fromid, toid, value, textid=0, limittime=None):
        """名声ポイント.
        """
        return Present.create(fromid, toid, Defines.ItemType.CABARETCLUB_HONOR_POINT, value, textid, limittime)

    @staticmethod
    def createByPlatinumPiece(fromid, toid, num, textid=0, limittime=None):
        """プラチナの欠片
        """
        return Present.create(fromid, toid, Defines.ItemType.PLATINUM_PIECE, num, textid, limittime)

    @staticmethod
    def createByBattleTicket(fromid, toid, num, textid=0, limittime=None):
        """プラチナの欠片
        """
        return Present.create(fromid, toid, Defines.ItemType.BATTLE_TICKET, num, textid, limittime)

    @staticmethod
    def createByCrystalPiece(fromid, toid, num, textid=0, limittime=None):
        """クリスタルの欠片
        """
        return Present.create(fromid, toid, Defines.ItemType.CRYSTAL_PIECE, num, textid, limittime)


class PresentReceived(PresentBase):
    """受取済みのプレゼント.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'受け取った時間')
    
    @staticmethod
    def createByPresent(present):
        ins = PresentReceived()
        for field in Present.get_fields():
            setattr(ins, field.name, getattr(present, field.name))
        ins.id = present.id
        ins.ctime = OSAUtil.get_now()
        return ins

class PrizeMaster(BaseMaster):
    """報酬マスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    gold = models.PositiveIntegerField(default=0, verbose_name=u'キャバゴールド')
    gachapt = models.PositiveIntegerField(default=0, verbose_name=u'引抜Pt')
    rareoverticket = models.PositiveIntegerField(default=0, verbose_name=u'レア以上チケット')
    ticket = models.PositiveIntegerField(default=0, verbose_name=u'運試しチケット')
    memoriesticket = models.PositiveIntegerField(default=0, verbose_name=u'思い出チケット')
    gachaticket = models.PositiveIntegerField(default=0, verbose_name=u'引き抜きチケット')
    goldkey = models.PositiveIntegerField(default=0, verbose_name=u'金の鍵')
    silverkey = models.PositiveIntegerField(default=0, verbose_name=u'銀の鍵')
    itemid = models.PositiveIntegerField(default=0, verbose_name=u'アイテムID')
    itemnum = models.PositiveIntegerField(default=0, verbose_name=u'アイテム個数')
    cardid = models.PositiveIntegerField(default=0, verbose_name=u'カードID')
    cardnum = models.PositiveIntegerField(default=0, verbose_name=u'カード枚数')
    eventticket_id = models.PositiveIntegerField(default=0, verbose_name=u'レイドイベントID')
    eventticket_num = models.PositiveIntegerField(default=0, verbose_name=u'レイドイベントチケット枚数')
    additional_ticket_id = models.PositiveIntegerField(default=0, verbose_name=u'追加ガチャチケット種別', choices=dict_to_choices(Defines.GachaConsumeType.GachaTicketType.CHOICES))
    additional_ticket_num = models.PositiveIntegerField(default=0, verbose_name=u'追加ガチャチケット枚数')
    tanzaku_number = models.PositiveSmallIntegerField(default=0, verbose_name=u'スカウトイベント短冊')
    tanzaku_num = models.PositiveIntegerField(default=0, verbose_name=u'スカウトイベント短冊数')
    cabaclub_money = models.PositiveIntegerField(default=0, verbose_name=u'キャバクラシステムの特別なマネー')
    cabaclub_honor = models.PositiveIntegerField(default=0, verbose_name=u'名誉ポイント')
    platinum_piece_num = models.PositiveIntegerField(default=0, verbose_name=u'プラチナの欠片')
    crystal_piece_num = models.PositiveIntegerField(default=0, verbose_name=u'クリスタルの欠片')
