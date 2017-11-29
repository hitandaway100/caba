# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """期間限定ガチャを回した人のリーダー.
    """
    
    def getTitle(self):
        return u'期間限定ガチャを回した人のリーダー.'
    
    def getKpiName(self):
        return 'paymentgacha_leaderdata'

def main(request):
    return Handler.run(request)
