# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """レイドイベントステージ分布.
    """
    
    def getTitle(self):
        return u'レイドイベントステージ分布'
    
    def getKpiName(self):
        return 'raideventstage'

def main(request):
    return Handler.run(request)
