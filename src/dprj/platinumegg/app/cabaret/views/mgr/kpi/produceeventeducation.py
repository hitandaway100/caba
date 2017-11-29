# -*- coding: utf-8 -*-

from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """プロデュースイベントレベル/ハート分布.
    """
    def getTitle(self):
        return u'プロデュースイベントレベル/ハート分布'

    def getKpiName(self):
        return 'produceeventeducation'


def main(request):
    return Handler.run(request)
