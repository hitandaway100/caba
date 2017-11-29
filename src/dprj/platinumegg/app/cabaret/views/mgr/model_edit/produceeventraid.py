# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler, \
    AppModelForm, ModelEditValidError, AppModelChoiceField
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import ProduceEventMaster,\
    ProduceEventRaidMaster
from platinumegg.app.cabaret.models.Happening import RaidMaster
from platinumegg.app.cabaret.models.Card import CardMaster
from django.core.exceptions import ValidationError


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """

    class Form(AppModelForm):
        class Meta:
            model = ProduceEventRaidMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'id',
            )

        eventid = AppModelChoiceField(ProduceEventMaster, required=False, label=u'イベントマスターID')
        mid = AppModelChoiceField(RaidMaster, required=False, label=u'レイドマスターID')

        def _valid_primary_key(self):
            eventid = int(self.cleaned_data.get('eventid'))
            mid = int(self.cleaned_data.get('mid'))
            if eventid <= 0:
                raise ValidationError(u'eventidは1以上を指定して下さい')
            elif mid <= 0:
                raise ValidationError(u'midは1以上を指定して下さい')
            return ProduceEventRaidMaster.makeID(eventid, mid)

    def setting_property(self):
        self.MODEL_LABEL = u'プロデュースイベント用レイド'

    def __valid_master(self, master):
        master.id = ProduceEventRaidMaster.makeID(master.eventid, master.mid)

        if not master.is_public:
            return

        model_mgr = self.getModelMgr()

        if BackendApi.get_produce_event_master(model_mgr, master.eventid) is None:
            raise ModelEditValidError(u'存在しないイベントが設定されています.produceeventraid=%d,%d' % (master.eventid, master.mid))
        elif BackendApi.get_raid_master(model_mgr, master.mid) is None:
            raise ModelEditValidError(u'存在しないレイドが設定されています.produceeventraid=%d,%d' % (master.eventid, master.mid))

    def valid_insert(self, master):
        self.__valid_master(master)

    def valid_update(self, master):
        self.__valid_master(master)


def main(request):
    return Handler.run(request)
