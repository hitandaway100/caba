# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.tradeshop.base import TradeShopBaseHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Player import PlayerRequest, PlayerTradeShop
import settings
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil

class Handler(TradeShopBaseHandler):
    """ポイントガチャ交換確認.
    """

    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRequest, PlayerTradeShop]

    def process(self):
        req_args = self.getUrlArgs('/tradeshopyesno/')
        v_player = self.getViewerPlayer()

        try:
            itemmid = int(req_args.get(0))
            num = int(self.request.get(Defines.URLQUERY_NUMBER, None))
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)

        model_mgr = self.getModelMgr()
        tradeshopmaster = BackendApi.get_current_tradeshopmaster(model_mgr, using=settings.DB_READONLY)

        if (itemmid is None) or (itemmid not in tradeshopmaster.trade_shop_item_master_ids):
            raise CabaretError(u'アイテムの選択が不正です', CabaretError.Code.ILLEGAL_ARGS)

        tradeshopitemmaster = BackendApi.get_tradeshopitemmaster(model_mgr, itemmid, using=settings.DB_READONLY)
        url = OSAUtil.addQuery(UrlMaker.tradeshopdo(itemmid, v_player.req_confirmkey), Defines.URLQUERY_NUMBER, num)
        obj_item = self.get_itemdata(tradeshopitemmaster)
        obj_item['next_url'] = self.makeAppLinkUrl(url)

        self.html_param['usenum'] = num
        self.html_param['item'] = obj_item
        self.html_param['user_point'] = v_player.point
        self.writeAppHtml('tradeshop/yesno')

def main(request):
    return Handler.run(request)
