# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.models.Present import Present, PresentReceived,\
    PrizeMaster
from defines import Defines
from platinumegg.app.cabaret.models.Card import CardMaster, CardSortMaster
from platinumegg.app.cabaret.models.Item import ItemMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.util.card import CardUtil, ModelCardMaster
from platinumegg.app.cabaret.util.item import ItemUtil
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventMaster
from platinumegg.app.cabaret.models.ScoutEvent import CurrentScoutEventConfig,\
    ScoutEventTanzakuCastMaster

class PresentSet:
    """プレゼント.
    """
    
    def __init__(self, present=None):
        self.__present = present
        self.__textmaster = None
        self.__imaster = None
    @property
    def present(self):
        return self.__present
    
    @property
    def id(self):
        return self.present.id
    
    @property
    def num(self):
        if self.present.itype in (Defines.ItemType.ITEM, Defines.ItemType.CARD, Defines.ItemType.EVENT_GACHATICKET, Defines.ItemType.ADDITIONAL_GACHATICKET, Defines.ItemType.SCOUTEVENT_TANZAKU):
            return self.__present.inum
        else:
            return self.__present.ivalue
    
    @property
    def unit(self):
        if self.present.itype == Defines.ItemType.ITEM:
            unit = self.__imaster.unit
        elif self.present.itype == Defines.ItemType.CARD:
            unit = Defines.CardKind.UNIT[self.__imaster.ckind]
        elif self.__imaster and self.present.itype == Defines.ItemType.SCOUTEVENT_TANZAKU:
            unit = self.__imaster.tanzakuunit
        else:
            unit = Defines.ItemType.UNIT.get(self.present.itype, '')
        return unit
    
    @property
    def numtext(self):
        if self.present.itype == Defines.ItemType.CARD and self.__imaster.ckind == Defines.CardKind.NORMAL and self.num == 1:
            return u''
        else:
            return u'%d%s' % (self.num, self.unit)
    
    @property
    def statusText(self):
        if self.present.itype == Defines.ItemType.CARD and self.__imaster:
            if self.__imaster.ckind == Defines.CardKind.NORMAL:
                return u'最大接客力：%d' % self.__imaster.maxpower
            else:
                return self.__imaster.text
        elif self.present.itype == Defines.ItemType.ITEM and self.__imaster:
            return self.__imaster.text
        else:
            return None
    
    @property
    def numtext_with_x(self):
        numtext = self.numtext
        if numtext:
            return u'x%s' % numtext
        else:
            return numtext
    
    @property
    def text(self):
        if self.__textmaster:
            return self.__textmaster.text
        else:
            return u''
    
    @property
    def itemname(self):
        if self.__imaster and self.present.itype in (Defines.ItemType.CARD, Defines.ItemType.ITEM):
            return self.__imaster.name
        elif self.__imaster and self.present.itype == Defines.ItemType.EVENT_GACHATICKET:
            return self.__imaster.ticketname
        elif self.__imaster and self.present.itype == Defines.ItemType.SCOUTEVENT_TANZAKU:
            return self.__imaster.tanzakuname
        elif self.present.itype == Defines.ItemType.ADDITIONAL_GACHATICKET:
            return Defines.GachaConsumeType.GachaTicketType.NAMES.get(self.present.ivalue, u'')
        else:
            return Defines.ItemType.NAMES.get(self.present.itype, u'')
    
    @property
    def rareData(self):
        if self.__imaster and self.present.itype == Defines.ItemType.CARD and self.__imaster.ckind == Defines.CardKind.NORMAL:
            return {
                'text' : Defines.Rarity.NAMES.get(self.__imaster.rare, ''),
                'color' : Defines.Rarity.COLORS.get(self.__imaster.rare, '#ffffff'),
            }
        else:
            return None
    
    @property
    def typeIconImg(self):
        if self.__imaster and self.present.itype == Defines.ItemType.CARD and self.__imaster.ckind == Defines.CardKind.NORMAL:
            return Defines.CharacterType.ICONS[self.__imaster.ctype]
        else:
            return None
    
    @property
    def itemthumbnail(self):
        if self.__imaster and self.present.itype in (Defines.ItemType.CARD, Defines.ItemType.ITEM):
            if self.present.itype == Defines.ItemType.CARD:
                return CardUtil.makeThumbnailUrlIcon(self.__imaster)
            else:
                return ItemUtil.makeThumbnailUrlSmall(self.__imaster)
        elif self.__imaster and self.present.itype == Defines.ItemType.EVENT_GACHATICKET:
            return ItemUtil.makeThumbnailUrlSmallByDBString(self.__imaster.ticketthumb)
        elif self.__imaster and self.present.itype == Defines.ItemType.SCOUTEVENT_TANZAKU:
            return self.__imaster.tanzakuthumb
        elif self.present.itype == Defines.ItemType.ADDITIONAL_GACHATICKET:
            return ItemUtil.makeThumbnailUrlSmallByDBString(Defines.GachaConsumeType.GachaTicketType.THUMBNAIL[self.present.ivalue])
        else:
            return ItemUtil.makeThumbnailUrlSmallByType(self.present.itype)
    
    @property
    def itemthumbnail_middle(self):
        if self.__imaster and self.present.itype in (Defines.ItemType.CARD, Defines.ItemType.ITEM):
            if self.present.itype == Defines.ItemType.CARD:
                return CardUtil.makeThumbnailUrlMiddle(self.__imaster)
            else:
                return ItemUtil.makeThumbnailUrlMiddle(self.__imaster)
        elif self.__imaster and self.present.itype == Defines.ItemType.EVENT_GACHATICKET:
            return ItemUtil.makeThumbnailUrlMiddleByDBString(self.__imaster.ticketthumb)
        elif self.__imaster and self.present.itype == Defines.ItemType.SCOUTEVENT_TANZAKU:
            return self.__imaster.tanzakuthumb
        elif self.present.itype == Defines.ItemType.ADDITIONAL_GACHATICKET:
            return ItemUtil.makeThumbnailUrlMiddleByDBString(Defines.GachaConsumeType.GachaTicketType.THUMBNAIL[self.present.ivalue])
        else:
            return ItemUtil.makeThumbnailUrlMiddleByType(self.present.itype)
    
    @property
    def itemthumbnail_rect_middle(self):
        if self.__imaster and self.present.itype in (Defines.ItemType.CARD, Defines.ItemType.ITEM):
            if self.present.itype == Defines.ItemType.CARD:
                return CardUtil.makeThumbnailUrlIcon(self.__imaster)
            else:
                return ItemUtil.makeThumbnailUrlMiddle(self.__imaster)
        elif self.__imaster and self.present.itype == Defines.ItemType.EVENT_GACHATICKET:
            return ItemUtil.makeThumbnailUrlMiddleByDBString(self.__imaster.ticketthumb)
        elif self.__imaster and self.present.itype == Defines.ItemType.SCOUTEVENT_TANZAKU:
            return self.__imaster.tanzakuthumb
        elif self.present.itype == Defines.ItemType.ADDITIONAL_GACHATICKET:
            return ItemUtil.makeThumbnailUrlMiddleByDBString(Defines.GachaConsumeType.GachaTicketType.THUMBNAIL[self.present.ivalue])
        else:
            return ItemUtil.makeThumbnailUrlMiddleByType(self.present.itype)
    
    def check_receiveable(self, cardoverlimit):
        """受け取れるか確認.
        """
        if cardoverlimit and self.present.itype == Defines.ItemType.CARD:
            return 'card_over'
        return None
    
    @staticmethod
    def collect(model_mgr, present_idlist, using=settings.DB_DEFAULT, received=False):
        if received:
            arr = model_mgr.get_models(PresentReceived, present_idlist, using=using)
        else:
            arr = model_mgr.get_models(Present, present_idlist, using=using)
        if len(arr) != len(present_idlist):
            return None
        
        presentsetlist = PresentSet.presentToPresentSet(model_mgr, arr, using)
        presents = dict([(presentset.id, presentset) for presentset in presentsetlist])
        return [presents[presentid] for presentid in present_idlist]
    
    @staticmethod
    def presentToPresentSet(model_mgr, presentlist, using=settings.DB_DEFAULT):
        # Presentを取得.
        presentsetlist = []
        cardmasters = {}
        itemmasters = {}
        textmasters = {}
        raideventmasters = {}
        scouteventtanzakumasters = {}
        
        for present in presentlist:
            presentset = PresentSet(present)
            arr = textmasters[present.textid] = textmasters.get(present.textid, [])
            arr.append(presentset)
            if present.itype == Defines.ItemType.ITEM:
                arr = itemmasters[present.ivalue] = itemmasters.get(present.ivalue, [])
                arr.append(presentset)
            elif present.itype == Defines.ItemType.CARD:
                arr = cardmasters[present.ivalue] = cardmasters.get(present.ivalue, [])
                arr.append(presentset)
            elif present.itype == Defines.ItemType.EVENT_GACHATICKET:
                arr = raideventmasters[present.ivalue] = raideventmasters.get(present.ivalue, [])
                arr.append(presentset)
            elif present.itype == Defines.ItemType.SCOUTEVENT_TANZAKU:
                arr = scouteventtanzakumasters[present.ivalue] = scouteventtanzakumasters.get(present.ivalue, [])
                arr.append(presentset)
            else:
                presentset.__imaster = present.ivalue
            
            presentsetlist.append(presentset)
        
        for itemmaster in model_mgr.get_models(ItemMaster, itemmasters.keys(), using=using):
            for presentset in itemmasters[itemmaster.id]:
                presentset.__imaster = itemmaster
        
        cardsortmasters = dict([(master.id, master) for master in model_mgr.get_models(CardSortMaster, cardmasters.keys(), using=using)])
        for cardmaster in model_mgr.get_models(CardMaster, cardmasters.keys(), using=using):
            for presentset in cardmasters[cardmaster.id]:
                presentset.__imaster = ModelCardMaster([cardmaster, cardsortmasters[cardmaster.id]])
        
        for raideventmaster in model_mgr.get_models(RaidEventMaster, raideventmasters.keys(), using=using):
            for presentset in raideventmasters[raideventmaster.id]:
                presentset.__imaster = raideventmaster
        
        if scouteventtanzakumasters:
            config = model_mgr.get_model(CurrentScoutEventConfig, CurrentScoutEventConfig.SINGLE_ID, using=using)
            if config and config.mid:
                idlist = [ScoutEventTanzakuCastMaster.makeID(config.mid, number) for number in scouteventtanzakumasters.keys()]
                for tanzakumaster in model_mgr.get_models(ScoutEventTanzakuCastMaster, idlist, using=using):
                    for presentset in scouteventtanzakumasters[tanzakumaster.number]:
                        presentset.__imaster = tanzakumaster
        
        for textmaster in model_mgr.get_models(TextMaster, textmasters.keys(), using=using):
            for presentset in textmasters[textmaster.id]:
                presentset.__textmaster = textmaster
        return presentsetlist

class PrizeData:
    """報酬データ.
    """
    def __init__(self, gold=0, gachapt=0,
                 itemid=0, itemnum=0, cardid=0, cardnum=0,
                 rareoverticket=0, ticket=0, memoriesticket=0, gachaticket=0,
                 goldkey=0, silverkey=0, cabaretking=0, demiworld=0, eventticket_id=0, eventticket_num=0,
                 additional_ticket_id=0, additional_ticket_num=0, tanzaku_number=0, tanzaku_num=0,
                 cabaclub_money=0, cabaclub_honor=0, platinum_piece_num=0, crystal_piece_num=0):
        self.gold = gold
        self.gachapt = gachapt
        self.itemid = itemid
        self.itemnum = itemnum
        self.cardid = cardid
        self.cardnum = cardnum
        self.rareoverticket = rareoverticket
        self.ticket = ticket
        self.memoriesticket = memoriesticket
        self.gachaticket = gachaticket
        self.goldkey = goldkey
        self.silverkey = silverkey
        self.cabaretking = cabaretking
        self.demiworld = demiworld
        self.eventticket_id = eventticket_id
        self.eventticket_num = eventticket_num
        self.additional_ticket_id = additional_ticket_id
        self.additional_ticket_num = additional_ticket_num
        self.tanzaku_number = tanzaku_number
        self.tanzaku_num = tanzaku_num
        self.cabaclub_money = cabaclub_money
        self.cabaclub_honor = cabaclub_honor
        self.platinum_piece_num = platinum_piece_num
        self.crystal_piece_num = crystal_piece_num
    
    def __setattr__(self, name, value):
        """setterを用意しておく.
        """
        self.__dict__[name] = value
        arr = self.__dict__['_active_keys'] = self.__dict__.get('_active_keys') or set()
        if value:
            arr.add(name)
        elif name in arr:
            arr.remove(name)
    def get_active_keys(self):
        return getattr(self, '_active_keys', None) or set()
    
    @staticmethod
    def create(gold=0, gachapt=0,
                 itemid=0, itemnum=0, cardid=0, cardnum=0,
                 rareoverticket=0, ticket=0, memoriesticket=0, gachaticket=0,
                 goldkey=0, silverkey=0, cabaretking=0, demiworld=0, eventticket_id=0, eventticket_num=0,
                 additional_ticket_id=0, additional_ticket_num=0, tanzaku_number=0, tanzaku_num=0,
                 cabaclub_money=0, cabaclub_honor=0, platinum_piece_num=0, crystal_piece_num=0):
        return PrizeData(gold, gachapt, itemid, itemnum, cardid, cardnum, rareoverticket, ticket,
        memoriesticket, gachaticket, goldkey, silverkey, cabaretking, demiworld, eventticket_id,
        eventticket_num, additional_ticket_id, additional_ticket_num, tanzaku_number, tanzaku_num,
        cabaclub_money, cabaclub_honor, platinum_piece_num, crystal_piece_num)
    @staticmethod
    def createByMaster(prizemaster):
        return PrizeData.create(
                                prizemaster.gold,
                                prizemaster.gachapt,
                                prizemaster.itemid,
                                prizemaster.itemnum,
                                prizemaster.cardid,
                                prizemaster.cardnum,
                                prizemaster.rareoverticket,
                                prizemaster.ticket,
                                prizemaster.memoriesticket,
                                prizemaster.gachaticket,
                                prizemaster.goldkey,
                                prizemaster.silverkey,
                                eventticket_id=prizemaster.eventticket_id,
                                eventticket_num=prizemaster.eventticket_num,
                                additional_ticket_id=prizemaster.additional_ticket_id,
                                additional_ticket_num=prizemaster.additional_ticket_num,
                                tanzaku_number=prizemaster.tanzaku_number, tanzaku_num=prizemaster.tanzaku_num,
                                cabaclub_money=prizemaster.cabaclub_money,
                                cabaclub_honor=prizemaster.cabaclub_honor,
                                platinum_piece_num=prizemaster.platinum_piece_num,
                                crystal_piece_num=prizemaster.crystal_piece_num,
                                )
    def to_master(self):
        prizemaster = PrizeMaster.makeInstance(0)
        prizemaster.gold = self.gold
        prizemaster.gachapt = self.gachapt
        prizemaster.itemid = self.itemid
        prizemaster.itemnum = self.itemnum
        prizemaster.cardid = self.cardid
        prizemaster.cardnum = self.cardnum
        prizemaster.rareoverticket = self.rareoverticket
        prizemaster.ticket = self.ticket
        prizemaster.memoriesticket = self.memoriesticket
        prizemaster.gachaticket = self.gachaticket
        prizemaster.goldkey = self.goldkey
        prizemaster.silverkey = self.silverkey
        prizemaster.eventticket_id = self.eventticket_id
        prizemaster.eventticket_num = self.eventticket_num
        prizemaster.additional_ticket_id = self.additional_ticket_id
        prizemaster.additional_ticket_num = self.additional_ticket_num
        prizemaster.tanzaku_number = self.tanzaku_number
        prizemaster.tanzaku_num = self.tanzaku_num
        prizemaster.cabaclub_money = self.cabaclub_money
        prizemaster.cabaclub_honor = self.cabaclub_honor
        prizemaster.platinum_piece_num = self.platinum_piece_num
        prizemaster.crystal_piece_num = self.crystal_piece_num
        return prizemaster
