# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """アイテム流通量.
    """
    
    def getTitle(self):
        return u'アイテム流通量'
    
    def getKpiName(self):
        return 'item'

def main(request):
    return Handler.run(request)
