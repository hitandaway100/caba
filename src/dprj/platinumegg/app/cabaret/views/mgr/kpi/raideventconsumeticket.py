# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """日別イベントチケット消費数.
    """
    def getTitle(self):
        return u'日別イベントチケット消費数(=イベントガチャ回数)'
    
    def getKpiName(self):
        return 'raideventconsumeticket'

def main(request):
    return Handler.run(request)
