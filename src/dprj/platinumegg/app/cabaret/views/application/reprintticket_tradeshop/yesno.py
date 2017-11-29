# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.reprintticket_tradeshop.base import ReprintTradeShopBaseHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Player import PlayerRequest
from platinumegg.app.cabaret.models.Gacha import GachaTicket
import settings
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.ReprintTicketTradeShop import ReprintTicketTradeShopMaster

class Handler(ReprintTradeShopBaseHandler):
    """復刻チケット交換所交換確認.
    """

    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRequest]

    def process(self):
        req_args = self.getUrlArgs('/reprintticket_tradeshopyesno/')
        v_player = self.getViewerPlayer()

        model_mgr = self.getModelMgr()
        try:
            mid = int(req_args.get(0))
            num = int(self.request.get(Defines.URLQUERY_NUMBER, None))
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)

        self.check_validation(model_mgr, mid, num)
        tradeshopmaster = BackendApi.get_model(model_mgr, ReprintTicketTradeShopMaster, mid, using=settings.DB_READONLY)

        cardmaster = BackendApi.get_cardmasters([tradeshopmaster.card_id], model_mgr, using=settings.DB_READONLY).values()[0]
        if cardmaster is None:
            raise CabaretError(u'カードの選択が不正です', CabaretError.Code.ILLEGAL_ARGS)

        userdata = BackendApi.get_reprintticket_tradeshop_playerdata(model_mgr, v_player.id, tradeshopmaster, using=settings.DB_DEFAULT)
        tradecount = BackendApi.get_reprintticket_tradeshop_usertradecount(userdata)
        card_data = self._get_carddata(cardmaster)
        ticket_id = self.get_ticketid(tradeshopmaster.ticket_id)
        gachakey = GachaTicket.makeID(v_player.id, ticket_id)

        playerdata = BackendApi.get_model(model_mgr, GachaTicket, gachakey, using=settings.DB_DEFAULT)
        if playerdata is None:
            # チケットを持っていないと確認画面には移動出来ない.
            raise CabaretError(u'チケットが存在しません')

        url = OSAUtil.addQuery(UrlMaker.reprintticket_tradeshopdo(mid, v_player.req_confirmkey), Defines.URLQUERY_NUMBER, num)
        self.html_param['tradenum'] = num
        self.html_param['item'] = self.get_item_wrapper(v_player.id, card_data, tradeshopmaster, playerdata.num, tradecount, url)
        self.writeAppHtml('reprintticket_tradeshop/yesno')

def main(request):
    return Handler.run(request)
