# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """バトルイベントランク順位別獲得バトルPT.
    """
    
    def getTitle(self):
        return u'バトルイベントランク順位別獲得バトルPT'
    
    def getKpiName(self):
        return 'battleeventresult'

def main(request):
    return Handler.run(request)
