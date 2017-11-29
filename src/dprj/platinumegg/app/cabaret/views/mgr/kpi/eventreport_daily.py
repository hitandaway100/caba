# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """日別イベントレポート.
    """
    
    def getTitle(self):
        return u'日別イベントレポート'
    
    def getKpiName(self):
        return 'eventreport_daily'

def main(request):
    return Handler.run(request)
