# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.util.api import BackendApi, ModelRequestMgr
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventMaster, BattleEventRankMaster, \
    BattleEventPieceCollection, BattleEventPieceMaster
from platinumegg.app.cabaret.util.alert import AlertCode
import settings

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Handler(AdminHandler):
    """バトルパネルのシミュレーター
    """

    def process(self):
        if self.request.method == 'POST':
            self.procPost()

        model_mgr = ModelRequestMgr()
        battleeventmaster_list = model_mgr.get_mastermodel_all(BattleEventMaster, order_by='-id', using=backup_db)

        self.html_param['battleeventmaster_list'] = battleeventmaster_list
        self.writeAppHtml('battle_panel_simulator')

    def procPost(self):
        """パラメータを受け取ってバトルパネル情報を用意する.
        """
        model_mgr = self.getModelMgr()
        error_msg_list = []
        battleeventrankmaster = None

        # スカウトイベントのマスターID.
        mid = self.__get_int_value('_mid')
        battleeventrank_id = self.__get_int_value('_eventrankid')
        battleeventmaster = BackendApi.get_battleevent_master(model_mgr, mid, using=backup_db)

        if battleeventmaster is None:
            error_msg_list.append(u'存在しないバトルイベントです.%s' % mid)
        else:
            # バトルイベントランクマスターID
            if battleeventrank_id < 1:
                error_msg_list.append(u'バトルイベントランクIDは自然値で指定してください.')
            else:
                battleeventrankmaster = BattleEventRankMaster.fetchValues(
                    filters={'eventid': battleeventmaster.id, 'rank': battleeventrank_id})
                if not battleeventrankmaster:
                    error_msg_list.append(u'存在しないバトルイベントランクマスターです.%s' % battleeventrank_id)

        # 試験回数.
        cnt = self.__get_int_value('_cnt')
        if cnt < 1:
            error_msg_list.append(u'試験回数は自然数で指定してください.')

        cnt = min(1000000, cnt)

        # set hmtl form values
        self.html_param['cur_battleevent'] = battleeventmaster
        self.html_param['battleeventrank_id'] = battleeventrank_id
        self.html_param['cnt'] = cnt

        if error_msg_list:
            self.putAlertToHtmlParam(u'<br/>'.join(error_msg_list), AlertCode.ERROR)
            return

        # 試験.
        self.test_battle_panel(1, battleeventmaster, battleeventrankmaster[0], cnt)

    def test_battle_panel(self, uid, battleeventmaster, battleeventrankmaster, cnt):
        """バトルパネルテスト実行
        """

        eventid = battleeventmaster.id
        rarity_list = {x[0]:x[1] for x in battleeventrankmaster.rarity}

        battle_panel_dict = {}
        battle_panel_group_list = []

        piecemaster_list = BattleEventPieceMaster.fetchValues(filters={'eventid': eventid}, using=backup_db)

        for piecemaster in piecemaster_list:
            piece_id = piecemaster.number

            battle_panel_dict[piece_id] = {}
            battle_panel_dict[piece_id]['items'] = {}
            for idx in xrange(0, 9):
                tmp_dict = {}
                tmp_dict['occurrences'] = 0
                tmp_dict['rate'] = 0
                battle_panel_dict[piece_id]['items'][idx] = tmp_dict
            battle_panel_dict[piece_id]['prize_name'] = piecemaster.complete_prize_name

        for _ in xrange(cnt):
            rarity = BattleEventPieceCollection.select_rarity_box(battleeventrankmaster.rarity)
            userdata = BattleEventPieceCollection.get_or_create_instance(uid, eventid, rarity)

            get_piece = userdata.piece_or_item_drop()
            piece = get_piece.get('piece')

            battle_panel_dict[rarity]['items'][piece]['occurrences'] += 1
            battle_panel_dict[rarity]['items'][piece]['rate'] = \
                float(battle_panel_dict[rarity]['items'][piece]['occurrences']) / cnt * 100

        for piecemaster in piecemaster_list:
            piece_id = piecemaster.number
            occurrences = sum([x['occurrences'] for x in battle_panel_dict[piece_id]['items'].values()])
            tmp_dict = {}
            tmp_dict['id'] = piece_id
            tmp_dict['prize_name'] = piecemaster.complete_prize_name
            tmp_dict['occurrences'] = occurrences
            tmp_dict['rate'] = float(occurrences) / cnt * 100
            tmp_dict['bonus_rate_s'] = rarity_list[piece_id]

            battle_panel_group_list.append(tmp_dict)

        self.html_param['battle_panel_dict'] = battle_panel_dict
        self.html_param['battle_panel_group_list'] = sorted(battle_panel_group_list, key=lambda x:x['id'], reverse=True)
        self.html_param['total_set_rate'] = sum(rarity_list.values())

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
