# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """ランクアップ人数.
    """
    
    def getTitle(self):
        return u'バトルランク達成数'
    
    def getKpiName(self):
        return 'rankup'

def main(request):
    return Handler.run(request)
