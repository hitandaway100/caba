# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import settings_sub
from platinumegg.app.cabaret.util.cabareterror import CabaretError

class Handler(AppHandler):
    """ティザーページ.
    """
    def process(self):
        model_mgr = self.getModelMgr()
        args = self.getUrlArgs('/teaser/')
        eventbanner_id = args.getInt(0)
        
        eventbanner = None
        if eventbanner_id:
            eventbanner = BackendApi.get_eventbanner(model_mgr, eventbanner_id, using=settings.DB_READONLY)
        
        if eventbanner is None or not eventbanner.has_teaser:
            # 表示できない.
            if settings_sub.IS_DEV:
                raise CabaretError(u'指定したイベントバナーにはティザーの設定がされていません', CabaretError.Code.NOT_DATA)
            self.redirectToTop()
            return
        
        self.html_param['evenbanner'] = Objects.eventbanner(self, eventbanner)
        
        self.writeAppHtml('teaser_info')

def main(request):
    return Handler.run(request)
