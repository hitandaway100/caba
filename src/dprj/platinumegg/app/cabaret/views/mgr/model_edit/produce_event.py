# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import ProduceEventMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler
from platinumegg.app.cabaret.views.mgr.model_edit import AppModelChoiceField
from platinumegg.app.cabaret.views.mgr.model_edit import AppModelForm
from platinumegg.app.cabaret.views.mgr.model_edit import ModelEditValidError
from platinumegg.app.cabaret.util.scout import ScoutHappeningSelector
from platinumegg.app.cabaret.models.Item import ItemMaster

class Handler(AdminModelEditHandler):
    """マスターデータの操作."""

    class Form(AppModelForm):
        class Meta(object):
            model = ProduceEventMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        rankingprize_text = AppModelChoiceField(TextMaster, required=False, label=u'報酬文言')
        pointprize_text = AppModelChoiceField(TextMaster, required=False, label=u'報酬文言')
        useitem = AppModelChoiceField(ItemMaster, required=False, label=u'超接客で使用するアイテムID')
        changeitem = AppModelChoiceField(ItemMaster, required=False, label=u'専用アイテムと交換するためのアイテムID')

    def setting_property(self):
        self.MODEL_LABEL = u'プロデュース(イベント)'

    def __valid_master(self, master):
        if not master.is_public:
            return

        def checkRaidTable(table, errmessage):
            try:
                ScoutHappeningSelector(None, None, table).validate()
            except:
                raise ModelEditValidError(errmessage)

        if not isinstance(master.rankingprizes, list):
            raise ModelEditValidError(
                u'ランキング報酬のJsonが壊れています.produceevent={}'.format(master.id)
            )
        if not isinstance(master.raidtable, list):
            raise ModelEditValidError(
                u'レイド出現テーブルのJsonが壊れています.produceevent={}'.format(master.id)
            )
        if not isinstance(master.raidtable_big, list):
            raise ModelEditValidError(
                u'大ボス出現後レイド出現テーブルのJsonが壊れています.produceevent={}'.format(master.id)
            )
        if not isinstance(master.raidtable_full, list):
            raise ModelEditValidError(
                u'レイド出現テーブル(全力探索)のJsonが壊れています.produceevent={}'.format(master.id)
            )
        if not isinstance(master.raidtable_big_full, list):
            raise ModelEditValidError(
                u'大ボス出現後レイド出現テーブル(全力探索)のJsonが壊れています.produceevent={}'.format(master.id)
            )

        if not isinstance(master.pointprizes, (dict, list)):
            raise ModelEditValidError(u'ポイント達成報酬のJsonが壊れています.produceevent=%d' % master.id)
        for prizeidlist in master.pointprizes.values()[0]:
            self.checkPrize(master, prizeidlist[1], u'ポイント達成報酬', 'produceevent')

        checkRaidTable(master.raidtable, u'レイド出現テーブルが正しくありません.%d' % master.id)
        checkRaidTable(master.raidtable_big, u'大ボス出現後レイド出現テーブルが正しくありません.%d' % master.id)
        checkRaidTable(master.raidtable_full, u'レイド出現テーブル(全力探索)が正しくありません.%d' % master.id)
        checkRaidTable(master.raidtable_big_full, u'大ボス出現後レイド出現テーブル(全力探索)が正しくありません.%d' % master.id)

        for data in master.rankingprizes:
            diff = set(['prize', 'rank_min', 'rank_max']) - set(data.keys())
            if diff:
                raise ModelEditValidError(
                    u'ランキング報酬に想定外のデータが含まれています.produceevent={}'.format(master.id)
                )
            self.checkPrize(master, data['prize'], u'ランキング報酬', u'produceevent')

    def valid_insert(self, master):
        self.__valid_master(master)

    def valid_update(self, master):
        self.__valid_master(master)


def main(request):
    return Handler.run(request)
