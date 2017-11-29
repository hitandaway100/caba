# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """スカウトイベントポイント数.
    """
    
    def getTitle(self):
        return u'スカウトイベント消費ガチャPt'
    
    def getKpiName(self):
        return 'scouteventgachapointconsume'

def main(request):
    return Handler.run(request)
