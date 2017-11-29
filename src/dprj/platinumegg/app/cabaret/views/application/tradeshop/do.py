# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.views.application.tradeshop.base import TradeShopBaseHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Player import PlayerTradeShop, PlayerDeck,\
    PlayerGold, PlayerGachaPt, PlayerKey
import settings
import settings_sub
import urllib
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
class Handler(TradeShopBaseHandler):
    """ポイントガチャ交換書き込み.
    """

    def process(self):
        req_args = self.getUrlArgs('/tradeshopdo/')

        try:
            itemmid = int(req_args.get(0))
            confirmkey = urllib.unquote(req_args.get(1))
            num = int(self.request.get(Defines.URLQUERY_NUMBER, None))
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)

        model_mgr = self.getModelMgr()

        tradeshopmaster = BackendApi.get_current_tradeshopmaster(model_mgr, using=settings.DB_READONLY)
        if tradeshopmaster is None:
            raise CabaretError(u'交換所のマスターデータが見つかりません', CabaretError.Code.ILLEGAL_ARGS)

        v_player = self.getViewerPlayer()

        try:
            model_mgr = db_util.run_in_transaction(self.tr_write, v_player.id, itemmid, confirmkey, num)
            model_mgr.write_end()
        except CabaretError, err:
            if settings_sub.IS_LOCAL:
                raise
            elif err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                url = UrlMaker.tradeshopyesno(itemmid)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return

        url = OSAUtil.addQuery(UrlMaker.tradeshopresult(itemmid), Defines.URLQUERY_NUMBER, num)
        url = self.makeAppLinkUrlRedirect(url)
        self.appRedirect(url)

    def tr_write(self, uid, tradeshopitemmaster, confirmkey, num):
        """アイテム交換書き込み
        """
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_player(self, uid, [PlayerTradeShop, PlayerDeck, PlayerGold, PlayerGachaPt, PlayerKey], model_mgr=model_mgr)
        BackendApi.tr_tradeshop_item(model_mgr, player, tradeshopitemmaster, confirmkey, num)

        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
