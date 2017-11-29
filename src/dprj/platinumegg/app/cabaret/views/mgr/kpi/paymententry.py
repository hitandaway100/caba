# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """課金レコード.
    """
    
    def getTitle(self):
        return u'課金レコード'
    
    def getKpiName(self):
        return 'paymententry'

def main(request):
    return Handler.run(request)
