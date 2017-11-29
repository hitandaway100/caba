# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """スカウト完了.
    """
    
    def getTitle(self):
        return u'スカウト達成数'
    
    def getKpiName(self):
        return 'scoutcomplete'

def main(request):
    return Handler.run(request)
