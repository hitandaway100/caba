# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler


class Handler(ScoutHandler):
    """スカウトイベントキャスト指名(チップ投入結果).
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        args = self.getUrlArgs('/sceventtippopulatecomplete/')
        tanzaku_number = args.getInt(0)
        tip_num = args.getInt(1)
        if not tip_num or tip_num < 1:
            # チップ数が不正.
            url = UrlMaker.scoutevent_top()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=using)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        mid = eventmaster.id
        
        # 短冊のマスターデータ.
        tanzakumaster = BackendApi.get_scoutevent_tanzakumaster(model_mgr, mid, tanzaku_number, using=settings.DB_READONLY)
        if tanzakumaster is None:
            # 存在しない短冊.
            url = UrlMaker.scoutevent_top()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        self.html_param['scoutevent'] = Objects.scouteventmaster(self, eventmaster, None)
        self.html_param['scoutevent_tanzaku'] = Objects.scoutevent_tanzaku(self, tanzakumaster)
        self.html_param['tip_add'] = tip_num
        
        # トピック.
        self.putEventTopic(mid)
        
        self.writeScoutEventHTML('tip_populate_complete', eventmaster)

def main(request):
    return Handler.run(request)
