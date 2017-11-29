# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.views.application.reprintticket_tradeshop.base import ReprintTradeShopBaseHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Player import PlayerDeck, PlayerKey
from platinumegg.app.cabaret.models.Gacha import GachaTicket
import settings
import settings_sub
import urllib
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.ReprintTicketTradeShop import ReprintTicketTradeShopMaster,\
    ReprintTicketTradeShopPlayerData

class Handler(ReprintTradeShopBaseHandler):
    """復刻チケット交換所交換処理.
    """

    def process(self):
        req_args = self.getUrlArgs('/reprintticket_tradeshopdo/')

        try:
            trademasterid = int(req_args.get(0))
            confirmkey = urllib.unquote(req_args.get(1))
            num = int(self.request.get(Defines.URLQUERY_NUMBER, None))
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
        model_mgr = self.getModelMgr()
        self.check_validation(model_mgr, trademasterid, num)
        v_player = self.getViewerPlayer()

        try:
            model_mgr = db_util.run_in_transaction(self.tr_write, v_player.id, trademasterid, confirmkey, num)
            model_mgr.write_end()
        except CabaretError, err:
            if settings_sub.IS_LOCAL:
                raise
            elif err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                url = UrlMaker.reprintticket_tradeshopyesno(trademasterid)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return

        url = OSAUtil.addQuery(UrlMaker.reprintticket_tradeshopresult(trademasterid), Defines.URLQUERY_NUMBER, num)
        url = self.makeAppLinkUrlRedirect(url)
        self.appRedirect(url)

    def tr_write(self, uid, tradeshopmaster, confirmkey, num):
        """アイテム交換書き込み
        """
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_player(self, uid, [PlayerDeck, PlayerKey], model_mgr=model_mgr)
        BackendApi.tr_reprintticket_tradeshop_item(model_mgr, player, tradeshopmaster, confirmkey, num)

        model_mgr.write_all()
        return model_mgr


def main(request):
    return Handler.run(request)
