# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.reprintticket_tradeshop.base import ReprintTradeShopBaseHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.util.item import ItemUtil
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.app.cabaret.models.Gacha import GachaTicket
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.ReprintTicketTradeShop import ReprintTicketTradeShopMaster, ReprintTicketTradeShopPlayerData
import settings
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
from collections import namedtuple

class Handler(ReprintTradeShopBaseHandler):
    """復刻チケット交換所トップページ.
    """

    def process(self):
        model_mgr = self.getModelMgr()
        
        tradeshop_masters_all = BackendApi.get_current_reprintticket_tradeshopmaster(model_mgr)
        if tradeshop_masters_all is None:
            self.html_param['is_open'] = False
            self.writeAppHtml('reprintticket_tradeshop/top')
            return
        else:
            self.html_param['is_open'] = True

        req_args = self.getUrlArgs('/reprintticket_tradeshop/')
        ticketids = sorted({x.ticket_id for x in tradeshop_masters_all}, key=self.sequence.index)

        if len(req_args.args) == 0:
            if self.selected_id in ticketids:
                selected_ticketid = self.selected_id
            else:
                selected_ticketid = ticketids[0]
        else:
            try:
                selected_ticketid = int(req_args.get(0))
            except ValueError:
                raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)

        tradeshop_masters = filter(lambda x:x.ticket_id==selected_ticketid, tradeshop_masters_all)

        self.html_param['ticket_tabs'] = self.make_tickettabs(ticketids, selected_ticketid)

        # プレイヤー情報
        v_player = self.getViewerPlayer()
        obj_player = Objects.player(self, v_player)
        datalist = BackendApi.get_reprintticket_tradeshop_playerdata_list(model_mgr, v_player.id, tradeshop_masters, using=settings.DB_DEFAULT)
        midlist = [master.id for master in tradeshop_masters]
        dataset = {data.mid for data in datalist if data is not None}
        diff_masterids = list(set(midlist) - dataset)

        diff_playerdata = []
        for masterid in diff_masterids:
            key = ReprintTicketTradeShopPlayerData.makeID(v_player.id, masterid)
            playerdata = ReprintTicketTradeShopPlayerData.createInstance(key)
            diff_playerdata.append(playerdata)
        datalist.extend(diff_playerdata)
        userdata = {x.mid: x for x in datalist}
        user_countdata = BackendApi.get_reprintticket_tradeshop_tradecountdata(midlist, userdata)

        self.html_param['player'] = obj_player
        self.html_param['itemdata'] = self.get_items(model_mgr, v_player.id, tradeshop_masters, user_countdata)

        user_ticket_id = GachaTicket.makeID(v_player.id, selected_ticketid)
        gacha_ticket = BackendApi.get_model(model_mgr, GachaTicket, user_ticket_id)
        self.html_param['gacha_ticket_num'] = gacha_ticket.num if gacha_ticket else 0
        # the key `gacha_ticket_name` is already in use
        self.html_param['gacha_ticket_label'] = Defines.GachaConsumeType.GachaTicketType.NAMES[selected_ticketid]
        self.html_param['gacha_ticket_thumbnail'] = Defines.GachaConsumeType.GachaTicketType.THUMBNAIL[selected_ticketid]

        if 0 < len(diff_masterids):
            try:
                model_mgr = db_util.run_in_transaction(self.tr_write, diff_playerdata)
                model_mgr.write_end()
            except:
                pass

        self.writeAppHtml('reprintticket_tradeshop/top')

    def tr_write(self, diff_playerdata):
        model_mgr = ModelRequestMgr()
        for playerdata in diff_playerdata:
            model_mgr.set_save(playerdata)
        model_mgr.write_all()
        return model_mgr

    def make_tickettabs(self, ticketids, selected_ticketid):
        Tab = namedtuple('Tab', 'name url is_selected')
        tabs = []
        gtype = Defines.GachaConsumeType.GachaTicketType
        nameTable = {gtype.REPRINT_TICKET:"復刻", gtype.CASTTRADE_TICKET:"キャスト指定"}
        for ticket_id in ticketids:
            url = self.makeAppLinkUrl(UrlMaker.reprintticket_tradeshop(ticket_id))
            tabs.append(Tab(nameTable[ticket_id], url, selected_ticketid == ticket_id))
        return tabs

def main(request):
    return Handler.run(request)
