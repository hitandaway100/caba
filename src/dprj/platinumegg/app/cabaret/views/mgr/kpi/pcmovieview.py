# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """動画再生回数(PC).
    """
    
    def getTitle(self):
        return u'動画再生回数(PC)'
    
    def getKpiName(self):
        return 'pcmovieview'

def main(request):
    return Handler.run(request)
