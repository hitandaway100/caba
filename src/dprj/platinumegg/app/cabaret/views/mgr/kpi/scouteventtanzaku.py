# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """スカウトイベント短冊獲得数.
    """
    
    def getTitle(self):
        return u'スカウトイベント短冊獲得数'
    
    def getKpiName(self):
        return 'scouteventtanzaku'

def main(request):
    return Handler.run(request)
