# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(GachaHandler):
    """引抜カード一覧ページ.
    """
    
    def process(self):
        
        args = self.getUrlArgs('/gachacardlist/')
        try:
            mid = int(args.get(0))
        except:
            raise CabaretError(u'表示できない引抜です', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        
        # マスターデータ.
        gachamaster = BackendApi.get_gachamaster(model_mgr, mid, using=settings.DB_READONLY)
        if gachamaster is None:
            raise CabaretError(u'表示できない引抜です', CabaretError.Code.ILLEGAL_ARGS)
        self.html_param['gacha_name'] = gachamaster.name
        
        # カード情報.
        info = BackendApi.make_gachabox_rateinfo(model_mgr, gachamaster, using=settings.DB_READONLY)
        self.html_param['gachacardlistinfo'] = info
        
        # 戻る.
        url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.TO_TOPIC[gachamaster.consumetype])
        self.html_param['url_back'] = self.makeAppLinkUrl(url)
        
        self.writeAppHtml('gacha/cardlist')

def main(request):
    return Handler.run(request)
