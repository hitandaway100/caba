# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """ガチャユーザ情報.
    """
    
    def getTitle(self):
        return u'ガチャユーザ情報'
    
    def getKpiName(self):
        return 'gacha_userdata'

def main(request):
    return Handler.run(request)
