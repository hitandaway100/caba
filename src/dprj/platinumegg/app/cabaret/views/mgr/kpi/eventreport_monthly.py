# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """月別イベントレポート.
    """
    
    def getTitle(self):
        return u'月別イベントレポート'
    
    def getKpiName(self):
        return 'eventreport_monthly'

def main(request):
    return Handler.run(request)
