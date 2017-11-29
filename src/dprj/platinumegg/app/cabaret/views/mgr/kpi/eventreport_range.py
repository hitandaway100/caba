# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """期間別イベントレポート.
    """
    
    def getTitle(self):
        return u'期間別イベントレポート'
    
    def getKpiName(self):
        return 'eventreport_range'

def main(request):
    return Handler.run(request)
