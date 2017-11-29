# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """バトルイベント獲得ポイント.
    """
    
    def getTitle(self):
        return u'バトルイベント獲得ポイント'
    
    def getKpiName(self):
        return 'battleeventpoint'

def main(request):
    return Handler.run(request)
