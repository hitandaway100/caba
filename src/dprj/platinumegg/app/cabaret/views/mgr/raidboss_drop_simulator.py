# -*- coding: utf-8 -*-

from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventMaster
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventMaster, ScoutEventStageMaster
from platinumegg.app.cabaret.models.raidevent.RaidEventScout import RaidEventScoutStageMaster
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.apprandom import AppRandom
import settings


class Handler(AdminHandler):
    """レイドボスのアイテムドロップのシミュレータ
    """

    def process(self):
        if self.request.method == 'POST':
            self.procPost()

        model_mgr = self.getModelMgr()

        raid_eventmaster_list = model_mgr.get_mastermodel_all(RaidEventMaster, order_by='-id', using=settings.DB_READONLY)
        scout_eventmaster_list = model_mgr.get_mastermodel_all(ScoutEventMaster, order_by='-id', using=settings.DB_READONLY)

        self.html_param['raid_eventmaster_list'] = raid_eventmaster_list
        self.html_param['scout_eventmaster_list'] = scout_eventmaster_list

        self.writeAppHtml('raidboss_drop_simulator')

    def procPost(self):
        """パラメータを受け取ってレイド情報を用意する.
        """
        model_mgr = self.getModelMgr()
        error_msg_list = []
        stagemaster = None

        raidmid = self.__get_int_value('_raidmid')
        scoutmid = self.__get_int_value('_scoutmid')
        stgid = self.__get_int_value('_stgid')
        cnt = self.__get_int_value('_cnt')

        if cnt < 1:
            error_msg_list.append(u'試験回数は自然数で指定してください.')

        cnt = min(1000000, cnt)

        self.html_param['stgid'] = stgid
        self.html_param['cnt'] = cnt

        # if both events (raid and scout) are chosen send error and return
        if raidmid and scoutmid:
            self.putAlertToHtmlParam(u'１つのイベントを選択してください', AlertCode.ERROR)
            return

        if raidmid:
            raideventmaster = BackendApi.get_raideventmaster(model_mgr, raidmid, using=settings.DB_READONLY)
            if raideventmaster is None:
                error_msg_list.append(u'存在しないレイドイベントです.id={}'.format(raidmid))
            else:
                # get the stage master of the raid event
                stagemaster = RaidEventScoutStageMaster.getValues(filters={'eventid': raideventmaster.id, 'stage': stgid},
                                                          using=settings.DB_READONLY)
                self.html_param['cur_raideventmaster'] = raideventmaster
        elif scoutmid:
            scouteventmaster = BackendApi.get_scouteventmaster(model_mgr, scoutmid, using=settings.DB_READONLY)
            if scouteventmaster is None:
                error_msg_list.append(u'保存しないスカウトイベントです. id={}'. format(scoutmid))
            else:
                # get the stage master of the scout event
                stagemaster = ScoutEventStageMaster.getValues(filters={'eventid': scouteventmaster.id, 'stage': stgid},
                                                              using=settings.DB_READONLY)
                self.html_param['cur_scouteventmaster'] = scouteventmaster
        else:
            error_msg_list.append(u'レイドイベントまたはスカウトイベントを選択してください')

        if stagemaster is None:
            error_msg_list.append(u'存在しないステージマスターです.id={}'.format(stgid))

        # if we have a list of errors print them and return
        if error_msg_list:
            self.putAlertToHtmlParam('<br/>'.join(error_msg_list), AlertCode.ERROR)
            return

        self.procExec(stagemaster, cnt)

    def procExec(self, stagemaster, cnt):
        """シミュレータの実行
        """
        def get_prize_names(model_mgr, prizeid_list, using=settings.DB_READONLY):
            prizelist = BackendApi.get_prizelist(model_mgr, prizeid_list, using=using)
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=using)
            prize_names = []

            for prizeitem in prizeinfo['listitem_list']:
                prize_names.append(prizeitem['smalltext'])

            return prize_names

        model_mgr = self.getModelMgr()

        data = {}
        happening_mids = [happening['mid'] for happening in stagemaster.happenings]
        raid_bosses = BackendApi.get_raid_masters(model_mgr, happening_mids)

        for mid, boss in raid_bosses.items():
            total_set_rate = sum([x['rate'] for x in boss.items])
            data[mid] = {}

            for prize in boss.items:
                prize_id = prize['id']
                tmp = {}
                tmp['occurrences'] = 0
                tmp['rate'] = float(prize['rate']) / total_set_rate * 100
                tmp['name'] = ' / '.join(get_prize_names(model_mgr, [prize_id]))
                data[mid][prize_id] = tmp

        for _ in xrange(cnt):
            for mid, boss in raid_bosses.items():
                prize_id = self.__choice_item(boss.items)
                # prize_id can be `None` if boss.items == [].
                # This means there is no drop down item for this boss
                if prize_id:
                    data[mid][prize_id]['occurrences'] += 1

        self.html_param['raid_bosses'] = raid_bosses
        self.html_param['item_drop_data'] = data


    def __get_int_value(self, post_id):
        """Sanitize and return int value from post data
        """
        str_value = str(self.request.get(post_id) or 0)
        int_value = 0

        if str_value.isdigit():
            int_value = int(str_value)

        return int_value

    def __choice_item(self, items):
        rate_total = sum([item.get('rate', 0) for item in items])
        v = AppRandom().getIntN(rate_total)
        for item in items:
            rate = item.get('rate', 0)
            v -= rate
            if rate > 0 and v <= 0:
                return item['id']


def main(request):
    return Handler.run(request)
