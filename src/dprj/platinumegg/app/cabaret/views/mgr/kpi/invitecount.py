# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """招待数.
    """
    
    def getTitle(self):
        return u'招待数'
    
    def getKpiName(self):
        return 'invitecount'

def main(request):
    return Handler.run(request)
