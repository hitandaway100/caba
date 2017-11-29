# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """チュートリアル離脱状況.
    """
    
    def getTitle(self):
        return u'チュートリアル分布'
    
    def getKpiName(self):
        return 'tutorial'

def main(request):
    return Handler.run(request)
