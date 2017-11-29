# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """レイド失敗数.
    """
    def getTitle(self):
        return u'レイド失敗数'
    
    def getKpiName(self):
        return 'raidmiss'

def main(request):
    return Handler.run(request)
