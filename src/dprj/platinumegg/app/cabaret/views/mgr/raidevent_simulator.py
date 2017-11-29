# -*- coding: utf-8 -*-

from collections import Counter

import settings
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventMaster
from platinumegg.app.cabaret.models.raidevent.RaidEventScout import RaidEventScoutStageMaster
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.scout import ScoutHappeningSelector
from platinumegg.app.cabaret.views.adminhandler import AdminHandler


class Handler(AdminHandler):
    """レイドイベントのシミュレータ"""

    def process(self):
        if self.request.method == 'POST':
            self.procPost()

        model_mgr = self.getModelMgr()

        eventmasters = model_mgr.get_mastermodel_all(RaidEventMaster, order_by='-id', using=settings.DB_READONLY)
        self.html_param['eventmasters'] = eventmasters

        self.writeAppHtml('raidevent_simulator')

    def procPost(self):
        """パラメータを受け取ってレイドイベント情報を用意する.
        """
        model_mgr = self.getModelMgr()

        mid = self.__get_int_value('mid')
        stgid = self.__get_int_value('stgid')
        cnt = self.__get_int_value('cnt')

        cnt = min(1000000, cnt)

        eventmaster = BackendApi.get_raideventmaster(model_mgr, mid, using=settings.DB_READONLY)
        if eventmaster is None:
            self.putAlertToHtmlParam(u'存在しないレイドイベントです.id={}'.format(mid), AlertCode.ERROR)
            return None

        stagemaster = RaidEventScoutStageMaster.getValues(filters={'eventid': eventmaster.id, 'stage': stgid},
                                                          using=settings.DB_READONLY)
        if stagemaster is None:
            self.putAlertToHtmlParam(u'存在しないステージマスターです.id={}'.format(stgid), AlertCode.ERROR)
            return None

        self.html_param['cur_eventmaster'] = eventmaster
        self.html_param['_stgid'] = stgid
        self.html_param['_cnt'] = cnt

        self.procExec(stagemaster, cnt)

    def procExec(self, stagemaster, cnt):
        """シミュレータの実行"""
        model_mgr = self.getModelMgr()

        data = []

        happenings_data = sorted(stagemaster.happenings, key=lambda k: k['mid'])
        happening_mids = [happening['mid'] for happening in stagemaster.happenings]
        happening_bosses = BackendApi.get_raid_masters(model_mgr, happening_mids)
        happeningselector = ScoutHappeningSelector(None, stagemaster)

        happening_counter = Counter()
        for _ in range(cnt):
            happening = happeningselector.select()
            happening_counter[happening.mid] += 1

        self.html_param['total_rate'] = sum(happening_counter.values())

        for happening in happenings_data:
            mid = happening['mid']

            tmp = {}
            tmp['mid'] = mid
            tmp['occurrences'] = happening_counter[mid]
            tmp['boss_name'] = happening_bosses[mid].name
            tmp['rate'] = happening['rate']

            data.append(tmp)

        # sort data by rate and then by occurrences
        data = sorted(data, key=lambda x: (x['rate'], x['occurrences']), reverse=True)

        self.html_param['happenings_data'] = data

    def __get_int_value(self, post_id):
        """Sanitize and return int value from post data
        """
        str_value = str(self.request.get(post_id) or 0)
        int_value = 0

        if str_value.isdigit():
            int_value = int(str_value)
        return int_value


def main(request):
    return Handler.run(request)
