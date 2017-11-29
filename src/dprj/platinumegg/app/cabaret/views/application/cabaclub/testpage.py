# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler


class Handler(AppHandler):
    """キャバクラシステムの動作テスト用.
    """
    def checkUser(self):
        pass
    def check_process_pre(self):
        return True
    
    def process(self):
        self.writeAppJson()

def main(request):
    return Handler.run(request)
