# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings

class Handler(AppHandler):
    """イベントバナー.
    """
    
    def process(self):
        eventbanners = BackendApi.get_eventbanners(self, using=settings.DB_READONLY)
        self.json_result_param['eventbanners'] = [Objects.eventbanner(self, banner) for banner in eventbanners]
        self.writeAppJson()
    
def main(request):
    return Handler.run(request)
