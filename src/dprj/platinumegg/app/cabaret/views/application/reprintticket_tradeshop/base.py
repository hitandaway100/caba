# -*- coding: utf-8 -*-
from operator import attrgetter

from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import settings
from defines import Defines
from platinumegg.app.cabaret.models.Gacha import GachaTicket
from platinumegg.app.cabaret.models.ReprintTicketTradeShop import ReprintTicketTradeShopMaster
from platinumegg.app.cabaret.models.Skill import SkillMaster

class ReprintTradeShopBaseHandler(AppHandler):
    """ショップのハンドラ.
    """
    selected_id = Defines.GachaConsumeType.GachaTicketType.CASTTRADE_TICKET
    sequence = (
        Defines.GachaConsumeType.GachaTicketType.CASTTRADE_TICKET,
        Defines.GachaConsumeType.GachaTicketType.REPRINT_TICKET
    )

    def preprocess(self):
        self.html_param['url_reprintticket_tradeshop'] = self.makeAppLinkUrl(UrlMaker.reprintticket_tradeshop())
        self.html_param['url_gacha'] = self.makeAppLinkUrl(UrlMaker.gacha())
        self.html_param['banner'] = 'banner/reprint/exchange_place_header_lc.png'

    def check_validation(self, model_mgr, tradeshop_id, num):
        tradeshop = BackendApi.get_model(model_mgr, ReprintTicketTradeShopMaster, tradeshop_id, using=settings.DB_READONLY)
        if tradeshop is None:
            raise CabaretError(u'該当しないIDが指定されています', CabaretError.Code.ILLEGAL_ARGS)
        if not BackendApi.check_schedule_error_or_nowtime(model_mgr, tradeshop.schedule_id):
            raise CabaretError(u'期間外のIDが指定されています', CabaretError.Code.ILLEGAL_ARGS)
        if num <= 0:
            raise CabaretError(u'交換個数に0以下が指定されています', CabaretError.Code.ILLEGAL_ARGS)

    def _dataformat(self, name, thumb=None, thumb_middle=None, kind=None, iconUrl=None, rare=None, skillname=None, skilltext=None, basepower=None, cost=None):
        data = {
            'name': name,
            'kind': kind,
            'iconUrl': iconUrl,
            'thumbUrl': self.makeAppLinkUrlImg(thumb),
            'thumbUrlMiddle': self.makeAppLinkUrlImg(thumb_middle),
            'rare': rare,
            'skillname': skillname,
            'skilltext': skilltext,
            'basepower': basepower,
            'cost': cost
        }
        return data

    def get_items(self, model_mgr, uid, ticket_tradeshop_masters, countdata):
        card_ids = [x.card_id for x in ticket_tradeshop_masters]
        cardmasters = BackendApi.get_cardmasters(card_ids, model_mgr, using=settings.DB_READONLY)

        skill_ids = [cardmaster.skill for cardmaster in cardmasters.values()]
        skillmasters = {skillmaster.id: skillmaster for skillmaster in BackendApi.get_skillmaster_list(model_mgr, skill_ids)}

        tradeshop_list = sorted(ticket_tradeshop_masters, key=attrgetter('card_id'))
        gachaticket_ids = {GachaTicket.makeID(uid, self.get_ticketid(x.ticket_id)) for x in ticket_tradeshop_masters}
        gachatickets = BackendApi.get_model_dict(model_mgr, GachaTicket, gachaticket_ids)
        dataformat_list = []
        for trademaster in sorted(tradeshop_list, key=attrgetter('priority'), reverse=True):
            cardmaster = cardmasters[trademaster.card_id]
            skillmaster = skillmasters[cardmaster.skill]
            card_data = self._get_carddata(cardmaster, skillmaster)
            ticketid = self.get_ticketid(trademaster.ticket_id)
            player_ticketnum = self.get_player_ticketnum(gachatickets, GachaTicket.makeID(uid, ticketid))
            url = UrlMaker.reprintticket_tradeshopyesno(trademaster.id)
            dataformat_list.append(
                self.get_item_wrapper(uid, card_data, trademaster, player_ticketnum, countdata[trademaster.id], url)
            )
        return dataformat_list

    def get_item_wrapper(self, uid, card_data, trademaster, player_ticketnum, tradecount, url):
        data = {
            'uid': uid,
            'tradeshopmid': trademaster.id,
            'stock': trademaster.stock,
            'ticket_id': self.get_ticketid(trademaster.ticket_id),
            'use_ticketnum': trademaster.use_ticketnum,
            'player_ticketnum': player_ticketnum,
            'tradecount': tradecount,
            'url': url,
        }
        card_data.update(self.get_item(**data))
        return card_data

    def get_item(self, uid, tradeshopmid, stock, ticket_id, use_ticketnum, player_ticketnum, tradecount, url):
        data = {}
        data["next_url"] = self.makeAppLinkUrl(url)
        data["use_ticketnum"] = use_ticketnum
        data["ticket_name"] = Defines.GachaConsumeType.GachaTicketType.NAMES[ticket_id]
        data["player_ticketnum"] = player_ticketnum
        data["is_trade"] = self.is_trade(use_ticketnum, player_ticketnum)
        data["is_maxcount"] = self.is_maxcount(stock, tradecount)
        data["stock"] = stock
        data["tradecount"] = tradecount
        return data

    def get_ticketid(self, ticketid):
        if ticketid == 0:
            return Defines.GachaConsumeType.GachaTicketType.REPRINT_TICKET
        return ticketid

    def get_player_ticketnum(self, gachatickets, gachaticket_id):
        if gachatickets.has_key(gachaticket_id):
            return gachatickets[gachaticket_id].num
        return 0

    def is_maxcount(self, stock, tradecount):
        """False の場合に交換が可能.
        """
        if stock == 0:
            return False
        elif stock <= tradecount:
            return True
        return False

    def is_trade(self, use_ticketnum, player_ticketnum):
        if use_ticketnum <= player_ticketnum:
            return True
        return False

    def _get_carddata(self, cardmaster, skillmaster=None):
        thumb = CardUtil.makeThumbnailUrlIcon(cardmaster)
        thumb_middle = CardUtil.makeThumbnailUrlMiddle(cardmaster)
        icon = self.makeAppLinkUrlImg(Defines.CharacterType.ICONS[cardmaster.ctype])
        rare = {
            'str': Defines.Rarity.NAMES.get(cardmaster.rare),
            'color': Defines.Rarity.COLORS.get(cardmaster.rare, '#ffffff')
        }
        if isinstance(skillmaster, SkillMaster):
            skillname = skillmaster.name
            skilltext = skillmaster.text
        else:
            skillname = None
            skilltext = None
        return self._dataformat(name=cardmaster.name, thumb=thumb, thumb_middle=thumb_middle, kind=cardmaster.ckind, iconUrl=icon, rare=rare, skillname=skillname, skilltext=skilltext, basepower=cardmaster.basepower, cost=cardmaster.cost)
