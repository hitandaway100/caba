# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerGold


class Handler(AppHandler):
    """カード売却完了.
    表示するもの:
        売却した枚数.
        売却金額の合計.
        所持金.
        売却後の所持金.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold]
    
    def process(self):
        
        keys = (
            Defines.URLQUERY_GOLD,
            Defines.URLQUERY_GOLDADD,
            Defines.URLQUERY_GOLDPRE,
            Defines.URLQUERY_CARD_NUM,
            Defines.URLQUERY_CABAKING,
            Defines.URLQUERY_CABAKINGPRE,
        )
        try:
            for key in keys:
                self.html_param[key] = int(self.request.get(key, None))
        except:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        self.writeAppHtml('card/sellcomplete')

def main(request):
    return Handler.run(request)
