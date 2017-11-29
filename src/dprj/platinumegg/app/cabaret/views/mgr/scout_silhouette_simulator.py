# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.util.api import BackendApi, AppRandom
from platinumegg.app.cabaret.models.Player import Player, PlayerAp, PlayerExp, PlayerFriend
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventMaster, ScoutEventStageMaster
from platinumegg.app.cabaret.util.scout import ScoutEventGetCard, ScoutDropItemSelector
from platinumegg.app.cabaret.models.View import CardMasterView
from platinumegg.app.cabaret.util.alert import AlertCode
import settings
from defines import Defines

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Handler(AdminHandler):
    """スカウトシルエットのシミュレータ.
    """

    def process(self):
        if self.request.method == "POST":
            self.procPost()

        model_mgr = self.getModelMgr()

        scouteventmaster_list = model_mgr.get_mastermodel_all(ScoutEventMaster, order_by='-id', using=backup_db)

        self.html_param['scouteventmaster_list'] = scouteventmaster_list
        self.writeAppHtml('scout_silhouette_simulator')

    def procPost(self):
        """パラメータを受け取ってスカウトイベント情報を用意する.
        """
        model_mgr = self.getModelMgr()
        error_msg_list = []
        player = None
        stagemaster = None

        # スカウトイベントのマスターID.
        mid = self.__get_int_value('_mid')
        stgid = self.__get_int_value('_stgid')
        scouteventmaster = BackendApi.get_scouteventmaster(model_mgr, mid, using=backup_db)

        if scouteventmaster is None:
            error_msg_list.append(u'存在しないスカウトイベントです.%s' % mid)
        else:
            # ステージのマスターID
            if stgid < 1:
                error_msg_list.append(u'ステージIDは自然値で指定してください.')
            else:
                stagemaster = ScoutEventStageMaster.fetchValues(filters={'eventid': scouteventmaster.id, 'stage': stgid})
                if not stagemaster:
                    error_msg_list.append(u'存在しないステージマスターです.%s' % stgid)

        # ユーザーID
        uid = self.__get_int_value('_uid')
        if uid < 1:
            error_msg_list.append(u'ユーザーIDは自然値で指定してください.')
        else:
            # プレーヤー
            player = BackendApi.get_player(self, uid, [Player, PlayerAp, PlayerExp, PlayerFriend], using=backup_db)
            if not player:
                error_msg_list.append(u'保存しないユーザーです。%s' % uid)


        # 試験回数.
        cnt = self.__get_int_value('_cnt')
        if cnt < 1:
            error_msg_list.append(u'試験回数は自然数で指定してください.')
            # self.putAlertToHtmlParam(u'試験回数は自然数で指定してください.', AlertCode.ERROR)

        cnt = min(1000000, cnt)

        # set hmtl form values
        self.html_param['cur_scoutevent'] = scouteventmaster
        self.html_param['stgid'] = stgid
        self.html_param['uid'] = uid
        self.html_param['cnt'] = cnt

        if error_msg_list:
            self.putAlertToHtmlParam(u'<br/>'.join(error_msg_list), AlertCode.ERROR)
            return

        # 試験.
        self.__test_silhouette(scouteventmaster, stagemaster[0], player, cnt)

    def __test_silhouette(self, scouteventmaster, stagemaster, player, cnt):
        model_mgr = self.getModelMgr()
        silhouette_rate = []

        silhouette_dict = {}
        silhouette_dict['gold'] = {}
        silhouette_dict['silver'] = {}
        silhouette_dict['bronze'] = {}

        playdata = BackendApi.get_event_playdata(model_mgr, scouteventmaster.id, player.id, using=backup_db)

        dropitems = stagemaster.dropitems

        itemselector = ScoutDropItemSelector(player, stagemaster, 0)

        # the rate for each silhouette type
        gold_rate = 0
        silver_rate = 0
        bronze_rate = 0
        total_rate = 0

        # create dictionary that would be sent to the template
        for item in dropitems:
            rate = int(item['rate'])
            silhouette_type = item['silhouette']
            total_rate += rate

            cardid = int(item['master'])

            tmp_dict = {}
            tmp_dict[cardid] = {}
            tmp_dict[cardid]['name'] = model_mgr.get_model(CardMasterView, cardid, using=backup_db).name
            tmp_dict[cardid]['occurrences'] = 0
            tmp_dict[cardid]['rate'] = 0
            tmp_dict[cardid]['bonus_rate_s'] = float(item["rate"]) / sum(item['rate'] for item in dropitems) * 100

            silhouette_dict[silhouette_type].update(tmp_dict)
            if item['silhouette'] == 'gold':
                gold_rate += rate
            elif item['silhouette'] == 'silver':
                silver_rate += rate
            elif item['silhouette'] == 'bronze':
                bronze_rate += rate

        # execute scout `cnt` times and put save result
        silhouette_list = self.__execute_eventscout(model_mgr, player, stagemaster, playdata, cnt, itemselector)

        # number of gold, silver and bronze card chosen
        number_of_gold = 0
        number_of_silver = 0
        number_of_bronze = 0

        # 1. populate the dict that would be sent to the template
        # 2. count the number of gold, silver or bronze card chosen
        for item in silhouette_list:
            cardid = int(item.data['card'])
            silhouette_type = item.data['silhouette']

            silhouette_dict[silhouette_type][cardid]['occurrences'] += 1
            silhouette_dict[silhouette_type][cardid]['rate'] = float(silhouette_dict[silhouette_type][cardid]['occurrences']) / cnt * 100

            # count the number of gold, silver or bronze card chosen
            if item.data['silhouette'] == 'gold':
                number_of_gold += 1
            elif item.data['silhouette'] == 'silver':
                number_of_silver += 1
            elif item.data['silhouette'] == 'bronze':
                number_of_bronze += 1

        silhouette_rate.append({'name': 'gold (金)', 'occurrences': number_of_gold,
                                'rate': float(number_of_gold) / cnt * 100,
                                'bonus_rate_s': float(gold_rate) / total_rate * 100})

        silhouette_rate.append({'name': 'silver (銀)', 'occurrences': number_of_silver,
                                'rate': float(number_of_silver) / cnt * 100,
                                'bonus_rate_s': float(silver_rate) / total_rate * 100})

        silhouette_rate.append({'name': 'bronze (ブロンズ)', 'occurrences': number_of_bronze,
                                'rate': float(number_of_bronze) / cnt * 100,
                                'bonus_rate_s': float(bronze_rate) / total_rate * 100})

        # key rename
        silhouette_dict['gold (金)'] = silhouette_dict.pop('gold')
        silhouette_dict['silver (銀)'] = silhouette_dict.pop('silver')
        silhouette_dict['bronze (ブロンズ)'] = silhouette_dict.pop('bronze')


        def sortfun(sil_dict):
            return sil_dict[1]['bonus_rate_s'], sil_dict[1]['occurrences']

        self.html_param['silhouette_dict'] = silhouette_dict
        self.html_param['silhouette_rate'] = silhouette_rate

    def __execute_eventscout(self, model_mgr, player, stagemaster, playdata, cnt, itemselector):
        """イベントスカウトを実行.
        """

        data = []
        eventrate_total = stagemaster.eventrate_drop
        eventrate_total += stagemaster.eventrate_happening
        eventrate_total += stagemaster.eventrate_treasure
        eventrate_total += stagemaster.eventrate_gachapt
        eventrate_total += stagemaster.eventrate_lt_star

        rand = AppRandom()

        for _ in xrange(cnt):
            rand.setSeed(AppRandom.makeSeed())
            # select event (this types are defined in Defines.ScoutEventType)
            event = self.__select_event(eventrate_total, stagemaster.eventrate_drop, itemselector, rand)
            if event:
                playdata.result['event'] = [event]

                # get silhouette cards
                cardget_event = BackendApi.find_scout_event(playdata, Defines.ScoutEventType.GET_CARD)
                if cardget_event:
                    data.append(cardget_event)

        return data

    def __get_int_value(self, post_id):
        """Sanitize and return int value from post data
        """
        str_value = str(self.request.get(post_id) or 0)
        int_value = 0

        if str_value.isdigit():
            int_value = int(str_value)
        return int_value

    def __select_event(self, eventrate_total, eventrate_drop, itemselector, rand):
        """ScoutEventGetCardイベント選択.
        """
        if eventrate_total < 1:
            return None

        # カードがドロップ
        # シルエットが出るまで繰り返す
        while True:
            v = rand.getIntN(eventrate_total)

            if 0 <= v < eventrate_drop:
                data = itemselector.select()
                if data.itype == Defines.ItemType.CARD:
                    return ScoutEventGetCard.create(data.mid, silhouette=data.silhouette, heart=data.heart)


def main(request):
    return Handler.run(request)
