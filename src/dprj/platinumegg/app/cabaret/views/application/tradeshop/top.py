# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.tradeshop.base import TradeShopBaseHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.util.item import ItemUtil
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Player import PlayerTradeShop, PlayerDeck
from platinumegg.app.cabaret.models.TradeShop import TradeShopPlayerData
import settings
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil

class Handler(TradeShopBaseHandler):
    """ポイントガチャ交換所.
    表示するもの.
    """

    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerDeck]

    def process(self):
        model_mgr = self.getModelMgr()

        # プレイヤー情報
        v_player = self.getViewerPlayer()
        obj_player = Objects.player(self, v_player)

        # 交換レートリスト取得
        #tradelist = BackendApi.get_tradeshopmaster_all(model_mgr, using=settings.DB_READONLY)
        #tradelist.sort(key=...)

        # カード所持数
        cardnum = BackendApi.get_cardnum(v_player.id, model_mgr, using=settings.DB_READONLY)
        cardrest = v_player.cardlimit - cardnum
        is_cardnum_max = cardrest < 1

        obj_tradelist = []
        limited_masters = {} # ストック制限があるマスター.
        # slide_cards = {} # スライド表示するカード.
        header_img_list = {} # ヘッダ画像.

        self.putFromBackPageLinkUrl()

        self.html_param['player'] = obj_player
        self.html_param['tradelist'] = obj_tradelist
        self.html_param['headerlist'] = header_img_list
        # self.html_param['slidelist'] = obj_slidelist # 必要か判断出来ない

        tradeshopmaster = BackendApi.get_current_tradeshopmaster(model_mgr, using=settings.DB_READONLY)
        if tradeshopmaster is None:
            raise CabaretError(u'交換所の開催期間外です', CabaretError.Code.EVENT_CLOSED)

        userdata = None
        userpoint = BackendApi.get_tradeshop_userpoint(model_mgr, v_player.id)
        if userpoint is None:
            userdata = PlayerTradeShop.createInstance(uid)
            userpoint = userdata.point
        self.html_param['user_point'] = userpoint

        self.html_param['itemdata'] =  self.get_tradeitem_list(model_mgr, tradeshopmaster.trade_shop_item_master_ids, userpoint)

        tradeshopitemmasters = BackendApi.get_tradeshopitemmaster_list(model_mgr, tradeshopmaster.trade_shop_item_master_ids)
        tradecount_data = BackendApi.get_tradeshopitem_tradecountdata(model_mgr, v_player.id, tradeshopitemmasters)

        model_mgr = db_util.run_in_transaction(self.tr_write, userdata, tradecount_data)
        model_mgr.write_end()
        self.writeAppHtml('tradeshop/top')

    def get_tradeitem_list(self, model_mgr, itemids, userpoint):
        from itertools import chain

        def get_tradeshopdata(masterlist):
            itemlist = self._get_itemlist(model_mgr, masterlist, userpoint)
            cardlist = self._get_cardlist(model_mgr, masterlist, userpoint)
            ticketlist = self._get_ticketlist(model_mgr, masterlist, userpoint)
            return (cardlist, ticketlist, itemlist)

        def get_tradeshopitemmasters():
            if itemids:
                return BackendApi.get_tradeshopitemmaster_list(model_mgr, itemids, using=settings.DB_READONLY)
            return []

        return list(chain.from_iterable(get_tradeshopdata(get_tradeshopitemmasters())))

    def _get_itemlist(self, model_mgr, tradeshopitemmasters, userpoint):
        filtered_masters = filter((lambda x: x.itype == Defines.ItemType.ITEM), tradeshopitemmasters)
        filtered_masters.sort(key=(lambda x: x.itemid))

        data = []
        for tradeshopitem in filtered_masters:
            itemdata = self._get_item(model_mgr, tradeshopitem)
            data.append(self._add_dataformat(itemdata, userpoint))
        return sorted(data, key=(lambda x: x['id']))

    def _get_cardlist(self, model_mgr, tradeshopitemmasters, userpoint):
        filtered_masters = filter((lambda x: x.itype == Defines.ItemType.CARD), tradeshopitemmasters)
        filtered_masters.sort(key=(lambda x: x.itemid))

        data = []
        for tradeshopitem in filtered_masters:
            carddata = self._get_card(model_mgr, tradeshopitem)
            data.append(self._add_dataformat(carddata, userpoint))
        return sorted(data, key=(lambda x: x['id']))

    def _get_ticketlist(self, model_mgr, tradeshopitemmasters, userpoint):
        itemtype = Defines.ItemType
        filtered_masters = filter((lambda x: x.itype in self.tickettypes), tradeshopitemmasters)
        ticketlist = sorted([master.itype for master in filtered_masters])

        data = []
        for tradeshopitem, ticket in zip(filtered_masters, ticketlist):
            ticketdata = self._get_ticket(tradeshopitem)
            data.append(self._add_dataformat(ticketdata, userpoint))
        return sorted(data, key=(lambda x: x['id']))

    def _add_dataformat(self, data, userpoint):
        data['trade_max'] = self._get_trademax(data, userpoint)
        data['is_can_trade_trademax'] = self._get_can_trade_trademax(data)
        data['is_can_trade_stock'] = self._get_can_trade_stock(data)
        return data

    def _get_trademax(self, data, userpoint):
        return userpoint / data['use_point']

    def _get_can_trade_trademax(self, data):
        if data['trade_max'] <= 0:
            return None
        return True

    def _get_can_trade_stock(self, data):
        if data['trade_cnt'] is not None:
            if (data['stock'] > 0) and (data['stock'] - data['trade_cnt'] <= 0):
                return None
        return True

    def tr_write(self, userdata, tradecount_data):
        model_mgr = ModelRequestMgr()
        if userdata is not None:
            model_mgr.set_save(userdata)

        for key, value in tradecount_data.iteritems():
            if value is None:
                model_mgr.set_save(TradeShopPlayerData.createInstance(key))
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
