# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """スカウトイベントチップ消費数.
    """
    
    def getTitle(self):
        return u'スカウトイベントチップ消費数'
    
    def getKpiName(self):
        return 'scouteventtipconsume'

def main(request):
    return Handler.run(request)
