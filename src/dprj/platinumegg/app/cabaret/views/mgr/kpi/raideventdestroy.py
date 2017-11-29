# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """通常太客討伐回数別ユーザー数.
    """
    def getTitle(self):
        return u'通常太客討伐回数別ユーザー数'
    
    def getKpiName(self):
        return 'raideventdestroy'

def main(request):
    return Handler.run(request)
