# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler

class Handler(HappeningHandler):
    """救援依頼取得.
    """
    
    def process(self):
        
        self.putRaidHelpList()
        
        self.writeAppJson()
    
def main(request):
    return Handler.run(request)
