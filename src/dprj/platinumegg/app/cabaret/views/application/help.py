# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler


class Handler(AppHandler):
    """ヘルプページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        self.writeAppHtml('help')

def main(request):
    return Handler.run(request)
