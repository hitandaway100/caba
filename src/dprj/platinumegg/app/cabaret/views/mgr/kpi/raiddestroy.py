# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """レイド討伐数.
    """
    def getTitle(self):
        return u'レイド討伐数'
    
    def getKpiName(self):
        return 'raiddestroy'

def main(request):
    return Handler.run(request)
