# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """動画再生回数.
    """
    
    def getTitle(self):
        return u'動画再生回数'
    
    def getKpiName(self):
        return 'movieview'

def main(request):
    return Handler.run(request)
