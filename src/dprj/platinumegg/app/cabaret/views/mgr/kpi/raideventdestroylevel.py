# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """超太客Lv別討伐回数.
    """
    def getTitle(self):
        return u'超太客Lv別討伐回数'
    
    def getKpiName(self):
        return 'raideventdestroylevel'

def main(request):
    return Handler.run(request)
