# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """バトルイベント参加率.
    """
    
    def getTitle(self):
        return u'バトルイベント参加率'
    
    def getKpiName(self):
        return 'battleeventjoin'

def main(request):
    return Handler.run(request)
