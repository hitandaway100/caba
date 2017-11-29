# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines


class Handler(AppHandler):
    """異動完了.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        keys = (
            Defines.URLQUERY_CARD_NUM,
        )
        try:
            for key in keys:
                self.html_param[key] = int(self.request.get(key, None))
        except:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        self.writeAppHtml('card/transfercomplete')

def main(request):
    return Handler.run(request)
