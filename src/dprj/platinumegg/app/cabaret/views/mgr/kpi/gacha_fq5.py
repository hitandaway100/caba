# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """課金ガチャFQ5.
    """
    
    def getTitle(self):
        return u'課金ガチャFQ5'
    
    def getKpiName(self):
        return 'gacha_fq5'

def main(request):
    return Handler.run(request)
