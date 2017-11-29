# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """スカウトイベントポイント数.
    """
    
    def getTitle(self):
        return u'スカウトイベントポイント数'
    
    def getKpiName(self):
        return 'scouteventpoint'

def main(request):
    return Handler.run(request)
