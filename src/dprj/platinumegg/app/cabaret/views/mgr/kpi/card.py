# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """カード流通量.
    """
    
    def getTitle(self):
        return u'カード流通量'
    
    def getKpiName(self):
        return 'card'

def main(request):
    return Handler.run(request)
