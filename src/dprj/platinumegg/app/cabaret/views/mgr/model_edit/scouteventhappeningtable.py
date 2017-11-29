# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventMaster,\
    ScoutEventHappeningTableMaster
from defines import Defines
from django.core.exceptions import ValidationError
from platinumegg.app.cabaret.util.scout import ScoutHappeningSelector
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = ScoutEventHappeningTableMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'id',
            )
        eventid = AppModelChoiceField(ScoutEventMaster, required=False, label=u'イベントマスターID')
        
        def _valid_primary_key(self):
            eventid = int(self.cleaned_data.get('eventid'))
            wday = int(self.cleaned_data.get('wday'))
            if eventid < 1:
                raise ValidationError(u'eventidは1以上を指定して下さい')
            elif not wday in Defines.WeekDay.LIST:
                raise ValidationError(u'曜日は0以上7未満で指定して下さい')
            return ScoutEventHappeningTableMaster.makeID(eventid, wday)
    
    def setting_property(self):
        self.MODEL_LABEL = u'スカウトイベント曜日別レイド発生設定'
    
    def __valid_master(self, master):
        master.id = ScoutEventHappeningTableMaster.makeID(master.eventid, master.wday)
        if not master.is_public:
            return
        
        try:
            ScoutHappeningSelector(None, master, master.happenings).validate()
        except CabaretError, err:
            raise ModelEditValidError('{}, eventid={},wday={}'.format(err.value, master.eventid, master.wday))
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
