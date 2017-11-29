# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings

class Handler(AppHandler):
    """お知らせ一覧.
    """
    
    def process(self):
        infomations = BackendApi.get_infomation_all(self, using=settings.DB_READONLY)
        self.json_result_param['infomations'] = [Objects.infomation(self, infomation) for infomation in infomations]
        self.writeAppJson()
    
def main(request):
    return Handler.run(request)
