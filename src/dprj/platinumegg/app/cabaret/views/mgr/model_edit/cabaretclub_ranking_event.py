# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.app.cabaret.models.CabaretClubEvent import CabaClubRankEventMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler
from platinumegg.app.cabaret.views.mgr.model_edit import AppModelChoiceField
from platinumegg.app.cabaret.views.mgr.model_edit import AppModelForm
from platinumegg.app.cabaret.views.mgr.model_edit import ModelEditValidError


class Handler(AdminModelEditHandler):
    """マスターデータの操作."""

    class Form(AppModelForm):
        class Meta(object):
            model = CabaClubRankEventMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        rankingprize_text = AppModelChoiceField(TextMaster, required=False, label=u'ランキング報酬文言')

    def setting_property(self):
        self.MODEL_LABEL = u'経営ランキング(イベント)'

    def __valid_master(self, master):
        if not master.is_public:
            return

        if not isinstance(master.rankingprizes, list):
            raise ModelEditValidError(
                u'ランキング報酬のJsonが壊れています.cabaclubrankevent={}'.format(master.id)
            )

        for data in master.rankingprizes:
            diff = set(['prize', 'rank_min', 'rank_max']) - set(data.keys())
            if diff:
                raise ModelEditValidError(
                    u'ランキング報酬に想定外のデータが含まれています.cabaclubrankevent={}'.format(master.id)
                )
            self.checkPrize(master, data['prize'], u'ランキング報酬', u'cabaclubrankevent')

    def valid_insert(self, master):
        self.__valid_master(master)

    def valid_update(self, master):
        self.__valid_master(master)


def main(request):
    return Handler.run(request)
