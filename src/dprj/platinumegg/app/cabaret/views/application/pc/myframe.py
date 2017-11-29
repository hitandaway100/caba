# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
import urllib


class Handler(AppHandler):
    """PC版のマイページワイヤーフレーム.
    """
    
    def process(self):
        self.setFromPage(None)
        
        self.putBanner()
        self.putInfomations()
        
        url = self.request.get('contents');
        self.html_param['url_contents'] = urllib.unquote(url)
        if self.request.get('op') == 'true':
            self.html_param['is_tutorial'] = True
        self.writeAppHtml('myframe')
    
    def putBanner(self):
        """バナー.
        """
        # イベント.
        eventbanners = BackendApi.get_eventbanners(self, using=settings.DB_READONLY)
        self.html_param['eventbanners'] = [Objects.eventbanner(self, banner) for banner in eventbanners]
    
    def putInfomations(self):
        """更新情報.
        """
        # 更新情報.
        infomations, _ = BackendApi.get_infomations(self, 0, using=settings.DB_READONLY)
        if 0 < len(infomations):
            arr = []
            date_new = None
            for infomation in infomations[:8]:
                obj = Objects.infomation(self, infomation)
                date_new = date_new or obj['date']
                obj['is_new'] = date_new == obj['date']
                arr.append(obj)
            self.html_param['infomations'] = arr
    

def main(request):
    return Handler.run(request)
