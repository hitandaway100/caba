# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler

class Handler(KpiHandler):
    """バトルイベントピース取得数.
    """

    def getTitle(self):
        return u'バトルイベントピース取得数'

    def getKpiName(self):
        return 'battleeventpiececollect'

def main(request):
    return Handler.run(request)
