# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker


class Handler(AppHandler):
    """呼び戻す完了.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        args = self.getUrlArgs('/transferreturncomplete/')
        mid = args.getInt(0)
        num = args.getInt(1) or 0
        
        model_mgr = self.getModelMgr()
        cardmaster = None
        if mid:
            cardmaster = BackendApi.get_cardmasters([mid], arg_model_mgr=model_mgr, using=settings.DB_READONLY).get(mid)
        if cardmaster is None or not CardUtil.checkStockableMaster(cardmaster, raise_on_error=False):
            raise CabaretError(u'不正な遷移です.', CabaretError.Code.ILLEGAL_ARGS)
        
        # アルバムへのリンク.
        self.html_param['url_albumdetail'] = self.makeAppLinkUrl(UrlMaker.albumdetail(cardmaster.album))
        
        # カード情報.
        self.html_param['cardmaster'] = Objects.cardmaster(self, cardmaster)
        
        # 呼び戻した数.
        self.html_param['cardnum'] = num
        
        self.writeAppHtml('card/transferreturncomplete')

def main(request):
    return Handler.run(request)
