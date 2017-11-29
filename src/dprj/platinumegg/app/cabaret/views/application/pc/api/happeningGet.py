# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
from platinumegg.app.cabaret.models.Player import PlayerHappening
from platinumegg.app.cabaret.util.cabareterror import CabaretError

class Handler(HappeningHandler):
    """ハプニング取得.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerHappening]
    
    def process(self):
        # ハプニング情報.
        obj_happening = self.putHappeningInfo(do_get_end=True)
        if obj_happening is None:
            raise CabaretError(u'ハプニングが発生していません', CabaretError.Code.NOT_DATA)
        self.writeAppJson()
    
def main(request):
    return Handler.run(request)
