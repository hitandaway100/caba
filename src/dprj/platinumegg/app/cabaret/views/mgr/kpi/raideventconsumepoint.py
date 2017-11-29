# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """ユーザー別消費秘宝数.
    """
    def getTitle(self):
        return u'ユーザー別消費秘宝数'
    
    def getKpiName(self):
        return 'raideventconsumepoint'

def main(request):
    return Handler.run(request)
