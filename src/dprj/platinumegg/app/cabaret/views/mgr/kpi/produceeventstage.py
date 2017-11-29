# -*- coding: utf-8 -*-

from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler


class Handler(KpiHandler):
    """プロデュースイベントステージ分布.
    """
    def getTitle(self):
        return u'プロデュースイベントステージ分布'

    def getKpiName(self):
        return 'produceeventstage'


def main(request):
    return Handler.run(request)
