# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler


class Handler(AppHandler):
    """非対応ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def checkUser(self):
        pass
    
    def checkUserAgent(self):
        return True
    
    def process(self):
        self.writeAppHtml('no_support')

def main(request):
    return Handler.run(request)
