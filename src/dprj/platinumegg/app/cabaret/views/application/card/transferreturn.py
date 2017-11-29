# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
import urllib
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(AppHandler):
    """異動から戻す.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        args = self.getUrlArgs('/transferreturn/')
        try:
            num = int(self.request.get(Defines.URLQUERY_NUMBER, None))
            mid = args.getInt(0)
            confirmkey = urllib.unquote(args.get(1) or '')
        except:
            raise CabaretError(u'不正なアクセスです.', CabaretError.Code.ILLEGAL_ARGS)
        
        cardmaster = BackendApi.get_cardmasters([mid], model_mgr, using=settings.DB_READONLY).get(mid)
        if cardmaster is None or not CardUtil.checkStockableMaster(cardmaster, raise_on_error=True):
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        try:
            wrote_model_mgr = db_util.run_in_transaction(Handler.tr_write, v_player.id, cardmaster, num, confirmkey)
            wrote_model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            elif err.code in (CabaretError.Code.OVER_LIMIT, CabaretError.Code.NOT_ENOUGH):
                # 枠がいっぱいまたはストックが足りない.
                url = UrlMaker.albumdetail(cardmaster.album)
                url = OSAUtil.addQuery(url, Defines.URLQUERY_ERROR, err.code)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
            else:
                raise
        
        url = UrlMaker.transferreturncomplete(mid, num)
        
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    @staticmethod
    def tr_write(uid, cardmaster, num, confirmkey):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_create_card_from_stock(model_mgr, uid, cardmaster, num, confirmkey)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
