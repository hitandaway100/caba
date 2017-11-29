# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.Card import Card
import urllib


class Handler(AppHandler):
    """異動.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        try:
            str_cardidlist = self.request.get(Defines.URLQUERY_CARD, None)
            cardidlist = [int(str_cardid) for str_cardid in str_cardidlist.split(',')]
            if len(cardidlist) == 0:
                raise
            confirmkey = urllib.unquote(self.getUrlArgs('/transferdo/').get(0) or '')
        except:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        cardidlist = list(set(cardidlist))
        cardlist = model_mgr.get_models(Card, cardidlist, False, using=settings.DB_DEFAULT)
        if len(cardlist) != len(cardidlist):
            raise CabaretError(u'キャストが見つかりませんでした', CabaretError.Code.NOT_DATA)
        
        try:
            wrote_model_mgr = db_util.run_in_transaction(Handler.tr_write, v_player.id, cardidlist, confirmkey)
            wrote_model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
        
        url = UrlMaker.transfercomplete()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_CARD_NUM, len(cardidlist))
        
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    @staticmethod
    def tr_write(uid, cardidlist, confirmkey):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_add_cardstock(model_mgr, uid, cardidlist, confirmkey)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
