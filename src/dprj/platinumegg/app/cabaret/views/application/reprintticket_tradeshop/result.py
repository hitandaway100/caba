# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.reprintticket_tradeshop.base import ReprintTradeShopBaseHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
from defines import Defines
from platinumegg.app.cabaret.models.ReprintTicketTradeShop import ReprintTicketTradeShopMaster

class Handler(ReprintTradeShopBaseHandler):
    """ポイントガチャ交換結果ページ.
    表示するもの:
        交換結果.
    """

    @classmethod
    def getViewerPlayerClassList(cls):
        return []

    def process(self):
        req_args = self.getUrlArgs('/reprintticket_tradeshopresult/')
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        try:
            mid = int(req_args.get(0))
            num = int(self.request.get(Defines.URLQUERY_NUMBER, None))
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
        self.check_validation(model_mgr, mid, num)
        tradeshop = BackendApi.get_model(model_mgr, ReprintTicketTradeShopMaster, mid, using=settings.DB_READONLY)

        model_mgr = self.getModelMgr()

        cardmasters = BackendApi.get_cardmasters([tradeshop.card_id], model_mgr, using=settings.DB_READONLY)
        item = self._get_carddata(cardmasters.values()[0])
        item["ticket_name"] = Defines.GachaConsumeType.GachaTicketType.NAMES[self.get_ticketid(tradeshop.ticket_id)]
        self.html_param['item'] = item
        self.html_param["item_num"] = num
        self.writeAppHtml('reprintticket_tradeshop/result')

def main(request):
    return Handler.run(request)
