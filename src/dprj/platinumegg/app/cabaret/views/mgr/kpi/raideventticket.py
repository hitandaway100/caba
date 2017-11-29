# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """日別イベント用チケット交換数.
    """
    def getTitle(self):
        return u'日別イベント用チケット交換数'
    
    def getKpiName(self):
        return 'raideventticket'

def main(request):
    return Handler.run(request)
