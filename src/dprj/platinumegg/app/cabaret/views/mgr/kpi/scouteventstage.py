# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """スカウトイベントステージ分布.
    """
    
    def getTitle(self):
        return u'スカウトイベントステージ分布'
    
    def getKpiName(self):
        return 'scouteventstage'

def main(request):
    return Handler.run(request)
