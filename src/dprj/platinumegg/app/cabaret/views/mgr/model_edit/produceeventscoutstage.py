# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AppModelForm, \
    AppModelChoiceField
from defines import Defines
from platinumegg.app.cabaret.models.Boss import BossMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import ProduceEventMaster,\
    ProduceEventScoutStageMaster
from platinumegg.app.cabaret.views.mgr.model_edit.eventstage import EventStageHandler


class Handler(EventStageHandler):
    """マスターデータの操作.
    """

    class Form(AppModelForm):
        class Meta:
            model = ProduceEventScoutStageMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )

        eventid = AppModelChoiceField(ProduceEventMaster, required=False, label=u'プロデュースベントマスターID')
        boss = AppModelChoiceField(BossMaster, required=False, label=u'ボス')
        earlybonus_text = AppModelChoiceField(TextMaster, required=False, label=u'早期クリアボーナス報酬文言')

    def setting_property(self):
        self.MODEL_LABEL = u'プロデュースイベント(ステージ)'

    def __valid_master(self, master):
        if not master.is_public:
            return

        self.valid_stagedata(master, ProduceEventMaster)

    def valid_insert(self, master):
        self.__valid_master(master)

    def valid_update(self, master):
        self.__valid_master(master)


def main(request):
    return Handler.run(request)
