# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """ユーザー毎の秘宝獲得数.
    """
    def getTitle(self):
        return u'ユーザー毎の秘宝獲得数'
    
    def getKpiName(self):
        return 'raideventpoint'

def main(request):
    return Handler.run(request)
