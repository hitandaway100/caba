# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """大ボス討伐回数別ユーザー数.
    """
    def getTitle(self):
        return u'大ボス討伐回数別ユーザー数'
    
    def getKpiName(self):
        return 'raideventdestroybig'

def main(request):
    return Handler.run(request)
