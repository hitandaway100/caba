# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """バトルイベント獲得名声PT.
    """
    
    def getTitle(self):
        return u'バトルイベント獲得名声PT'
    
    def getKpiName(self):
        return 'battleeventfamepoint'

def main(request):
    return Handler.run(request)
