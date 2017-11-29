# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
import os


class Handler(AppHandler):
    """PC版の決済サービステスト用.
    """
    def process(self):
        self.osa_util.write_html('test/pc_payment_test.html', self.html_param)
    
    
def main(request):
    return Handler.run(request)
