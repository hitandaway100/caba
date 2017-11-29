# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.tradeshop.base import TradeShopBaseHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
from defines import Defines

class Handler(TradeShopBaseHandler):
    """ポイントガチャ交換結果ページ.
    表示するもの:
        交換結果.
    """

    @classmethod
    def getViewerPlayerClassList(cls):
        return []

    def process(self):
        req_args = self.getUrlArgs('/tradeshopresult/')

        try:
            itemmid = int(req_args.get(0))
            num = int(self.request.get(Defines.URLQUERY_NUMBER, None))
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)

        model_mgr = self.getModelMgr()

        tradeshopitemmaster = BackendApi.get_tradeshopitemmaster(model_mgr, itemmid, using=settings.DB_READONLY)
        self.html_param['item'] = self.get_itemdata(tradeshopitemmaster)
        self.writeAppHtml('tradeshop/result')

def main(request):
    return Handler.run(request)
