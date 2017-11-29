# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler

class Handler(AdminHandler):
    """管理ツールトップページ.
    """
    
    def process(self):
        self.writeAppHtml('index')
    
def main(request):
    return Handler.run(request)
