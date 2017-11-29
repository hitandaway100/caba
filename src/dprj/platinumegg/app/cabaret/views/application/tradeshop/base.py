# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.item import ItemUtil
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.app.cabaret.util.redistradeshop import RedisPlayerTradeShopPoint
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Player import PlayerTradeShop
import settings
from defines import Defines

class TradeShopBaseHandler(AppHandler):
    """ショップのハンドラ.
    """
    itemtype = Defines.ItemType
    ticketlist = ['RAREOVERTICKET', 'TRYLUCKTICKET', 'GACHATICKET', 'ADDITIONAL_GACHATICKET']
    tickettypes = [
        Defines.ItemType.RAREOVERTICKET,
        Defines.ItemType.TRYLUCKTICKET,
        Defines.ItemType.MEMORIESTICKET,
        Defines.ItemType.GACHATICKET,
        Defines.ItemType.ADDITIONAL_GACHATICKET
    ]

    def preprocess(self):
        self.html_param['url_tradeshop'] = self.makeAppLinkUrl(UrlMaker.tradeshop())
        self.html_param['url_gacha'] = self.makeAppLinkUrl(UrlMaker.gacha())

    def get_itemdata(self, tradeshopitemmaster):
        model_mgr = self.getModelMgr()
        if tradeshopitemmaster.itype == self.itemtype.ITEM:
            return self._get_item(model_mgr, tradeshopitemmaster)
        elif tradeshopitemmaster.itype == self.itemtype.CARD:
            return self._get_card(model_mgr, tradeshopitemmaster)
        elif tradeshopitemmaster.itype in self.tickettypes:
            return self._get_ticket(tradeshopitemmaster)

    def get_userpoint(self, uid):
        return BackendApi.get_tradeshop_userpoint(uid)

    def tradeshop_toppage_url(self):
        return self.makeAppLinkUrl(UrlMaker.tradeshop())

    def _dataformat(self, tradeshopitem, itemname, thumb, kind=None, iconUrl=None, rare=None, next_url=None):
        uid = self.getViewerPlayer().id
        model_mgr = self.getModelMgr()
        data = {
            'id': tradeshopitem.id,
            'itype': tradeshopitem.itype,
            'itemid': tradeshopitem.itemid,
            'itemnum': tradeshopitem.itemnum,
            'name': itemname,
            'kind': kind,
            'stock': tradeshopitem.stock,
            'use_point': tradeshopitem.use_point,
            'thumbUrl': self.makeAppLinkUrlImg(thumb),
            'iconUrl': iconUrl,
            'rare': rare,
            'trade_cnt': BackendApi.get_tradeshop_usertradecount(model_mgr, uid, tradeshopitem.id) or 0,
            'is_inf': self.is_inf(tradeshopitem.stock),
            'next_url': self.makeAppLinkUrl(next_url)
        }
        return data

    def is_inf(self, stock):
        return stock == 0

    def _get_item(self, model_mgr, tradeshopitemmaster):
        itemid = tradeshopitemmaster.itemid
        itemmaster = BackendApi.get_itemmaster(model_mgr, itemid, using=settings.DB_READONLY)
        thumb = ItemUtil.makeThumbnailUrlMiddleByDBString(itemmaster.thumb)
        next_url = UrlMaker.tradeshopyesno(tradeshopitemmaster.id)
        return self._dataformat(tradeshopitemmaster, itemmaster.name, thumb, next_url=next_url)

    def _get_card(self, model_mgr, tradeshopitemmaster):
        carddict = BackendApi.get_cardmasters([tradeshopitemmaster.itemid], model_mgr, using=settings.DB_READONLY)
        card = carddict.get(tradeshopitemmaster.itemid)

        thumb = CardUtil.makeThumbnailUrlIcon(card)
        icon = self.makeAppLinkUrlImg(Defines.CharacterType.ICONS[card.ctype])
        rare = {
            'str': Defines.Rarity.NAMES.get(card.rare),
            'color': Defines.Rarity.COLORS.get(card.rare, '#ffffff')
        }
        next_url = UrlMaker.tradeshopyesno(tradeshopitemmaster.id)
        return self._dataformat(tradeshopitemmaster, card.name, thumb, kind=card.ckind, iconUrl=icon, rare=rare, next_url=next_url)

    def _get_ticket(self, tradeshopitemmaster):
        next_url = UrlMaker.tradeshopyesno(tradeshopitemmaster.id)
        for tickettype in self.ticketlist:
            if tradeshopitemmaster.itype == getattr(self.itemtype, tickettype):
                name = tradeshopitemmaster.ticketname
                thumb = ItemUtil.makeThumbnailUrlMiddleByDBString(tradeshopitemmaster.ticketthumb)
                return self._dataformat(tradeshopitemmaster, name, thumb, next_url=next_url)
