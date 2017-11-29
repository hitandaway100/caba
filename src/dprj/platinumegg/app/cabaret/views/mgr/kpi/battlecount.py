# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """バトル対戦回数.
    """
    
    def getTitle(self):
        return u'バトル対戦回数'
    
    def getKpiName(self):
        return 'battlecount'

def main(request):
    return Handler.run(request)
