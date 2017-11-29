# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler


class Handler(AppHandler):
    """アクセス禁止.
    """
    def process(self):
        self.writeAppHtml('ban')
    
    def checkUser(self):
        pass
    def check_process_pre(self):
        return True

def main(request):
    return Handler.run(request)
