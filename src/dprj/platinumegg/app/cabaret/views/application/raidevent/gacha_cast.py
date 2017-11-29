# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from defines import Defines


class Handler(RaidEventBaseHandler):
    """レイドイベントガチャキャスト一覧ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        args = self.getUrlArgs('/raideventgachacast/')
        str_eventid = str(args.get(0))
        
        model_mgr = self.getModelMgr()
        eventmaster = None
        mid = None
        if str_eventid.isdigit():
            mid = int(str_eventid)
            eventmaster = BackendApi.get_raideventmaster(model_mgr, mid, using=settings.DB_READONLY)
        
        # TODO:ガチャ限女優を拾ってくる.
        
        # チケットガチャページのリンク.
        self.html_param['url_tryluck_ticket'] = self.makeAppLinkUrl(OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.TICKET))
        
        self.writeHtml(eventmaster, 'gacha_cast')
    

def main(request):
    return Handler.run(request)
