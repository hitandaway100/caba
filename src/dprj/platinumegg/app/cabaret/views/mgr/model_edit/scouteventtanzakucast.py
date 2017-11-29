# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventMaster,\
    ScoutEventTanzakuCastMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from defines import Defines
from django.core.exceptions import ValidationError


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = ScoutEventTanzakuCastMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'id',
            )
        eventid = AppModelChoiceField(ScoutEventMaster, required=False, label=u'イベントマスターID')
        prize_text = AppModelChoiceField(TextMaster, required=False, label=u'業績報酬テキスト')
        
        def _valid_primary_key(self):
            eventid = int(self.cleaned_data.get('eventid'))
            number = int(self.cleaned_data.get('number'))
            if eventid < 1:
                raise ValidationError(u'eventidは1以上を指定して下さい')
            elif not (0 <= number < 5):
                raise ValidationError(u'numberは0以上5未満で指定して下さい')
            return ScoutEventTanzakuCastMaster.makeID(eventid, number)
    
    def setting_property(self):
        self.MODEL_LABEL = u'スカウトイベント短冊キャスト･チップ'
    
    def __valid_master(self, master):
        master.id = ScoutEventTanzakuCastMaster.makeID(master.eventid, master.number)
        if not (0 <= master.number < 5):
            raise ModelEditValidError(u'numberは0以上5未満で指定して下さい')
        
        if not master.is_public:
            return
        
        def checkPrize(prizeidlist, name):
            if not isinstance(prizeidlist, list):
                raise ModelEditValidError(u'%sのJsonが壊れています.eventid=%s,number=%s' % (name, master.eventid, master.number))
            try:
                self.checkPrize(master, prizeidlist, name)
            except ModelEditValidError, err:
                raise ModelEditValidError(u'%s.eventid=%s,number=%s' % (err, name, master.eventid, master.number))
        checkPrize(master.prizes, u'業績報酬')
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
