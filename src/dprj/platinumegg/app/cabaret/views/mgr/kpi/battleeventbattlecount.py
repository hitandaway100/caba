# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """バトルイベントバトル回数.
    """
    
    def getTitle(self):
        return u'バトルイベントバトル回数'
    
    def getKpiName(self):
        return 'battleeventbattlecount'

def main(request):
    return Handler.run(request)
