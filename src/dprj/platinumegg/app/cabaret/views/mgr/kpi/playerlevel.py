# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """プレイヤーレベル分布.
    """
    
    def getTitle(self):
        return u'プレイヤーレベル分布'
    
    def getKpiName(self):
        return 'playerlevel'

def main(request):
    return Handler.run(request)
