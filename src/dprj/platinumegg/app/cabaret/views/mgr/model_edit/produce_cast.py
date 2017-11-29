# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import ProduceEventMaster, ProduceCastMaster
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler
from platinumegg.app.cabaret.views.mgr.model_edit import AppModelChoiceField
from platinumegg.app.cabaret.views.mgr.model_edit import AppModelForm
from platinumegg.app.cabaret.views.mgr.model_edit import ModelEditValidError
from platinumegg.app.cabaret.models.Text import TextMaster

class Handler(AdminModelEditHandler):
    """マスターデータの操作."""

    class Form(AppModelForm):
        class Meta(object):
            model = ProduceCastMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        event_id = AppModelChoiceField(ProduceEventMaster, required=False, label=u'イベントID')
        produce_cast = AppModelChoiceField(CardMaster, required=False, label=u'キャストID')
        complete_prizetext = AppModelChoiceField(TextMaster, required=False, label=u'コンプリート時にプレゼントする際の文言')
        lvprize_text = AppModelChoiceField(TextMaster, required=False, label=u'教育Lv達成報酬文言')
        
    def setting_property(self):
        self.MODEL_LABEL = u'プロデュースキャスト'

    def __valid_master(self, master):
        if not master.is_public:
            return

        if not isinstance(master.lvprizes, list):
            raise ModelEditValidError(u'教育LV達成報酬のJsonが壊れています.id=%d' % master.id)
        for data in master.lvprizes:
            diff = set(['prize','level']) - set(data.keys())
            if diff:
                raise ModelEditValidError(u'教育LV達成報酬に想定外のデータが含まれています.id=%d' % master.id)
            self.checkPrize(master, data['prize'], u'教育LV達成報酬', u'produceevent')

    def valid_insert(self, master):
        self.__valid_master(master)

    def valid_update(self, master):
        self.__valid_master(master)


def main(request):
    return Handler.run(request)
