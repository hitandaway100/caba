# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """プラットフォーム別DAU.
    """
    
    def getTitle(self):
        return u'プラットフォーム別DAU'
    
    def getKpiName(self):
        return 'platform_uu'

def main(request):
    return Handler.run(request)
