# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler

class Handler(AppHandler):
    """警告ページ.
    """
    
    def process(self):
        # 一応ユーザ確認.
        self.getViewerPlayer()
        self.writeAppHtml('warnpage')

def main(request):
    return Handler.run(request)
