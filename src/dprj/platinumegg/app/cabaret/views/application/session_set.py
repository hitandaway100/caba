# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler

class Handler(AppHandler):
    """セッションの設定.
    dmmのapiから呼ばれる.
    特に何もしない.
    """
    
    def process(self):
        
        callback_url = self.request.get('callback_url')
        if not callback_url:
            # APIで呼ばれていないっぽい.
            self.appRedirect(self.html_param['url_dmm_top'])
        else:
            self.appRedirect(callback_url)
    
    def checkUser(self):
        pass

def main(request):
    return Handler.run(request)
