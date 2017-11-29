# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventMaster,\
    ScoutEventPresentPrizeMaster
from defines import Defines
from platinumegg.app.cabaret.models.Text import TextMaster
from django.core.exceptions import ValidationError


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = ScoutEventPresentPrizeMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'id',
            )
        eventid = AppModelChoiceField(ScoutEventMaster, required=False, label=u'イベントマスターID')
        prize_text = AppModelChoiceField(TextMaster, required=False, label=u'報酬文言')
        
        def _valid_primary_key(self):
            eventid = int(self.cleaned_data.get('eventid'))
            number = int(self.cleaned_data.get('number'))
            if eventid <= 0:
                raise ValidationError(u'eventidは1以上を指定して下さい')
            elif number < 0:
                raise ValidationError(u'numberは0以上を指定して下さい')
            return ScoutEventPresentPrizeMaster.makeID(eventid, number)
    
    def setting_property(self):
        self.MODEL_LABEL = u'スカウトイベントプレゼント報酬'
    
    def __valid_master(self, master):
        master.id = ScoutEventPresentPrizeMaster.makeID(master.eventid, master.number)
        
        if not master.is_public:
            return
        
        model_mgr = self.getModelMgr()
        
        eventmaster = model_mgr.get_model(ScoutEventMaster, master.eventid)
        if eventmaster is None:
            raise ModelEditValidError(u'イベントが存在しません.eventid=%s, number=%s' % (master.eventid, master.number))
        
        def checkPrize(prizeidlist, name):
            try:
                self.checkPrize(master, prizeidlist, name)
            except ModelEditValidError, err:
                raise ModelEditValidError(u'%s, eventid=%s, number=%s' % (err, master.eventid, master.number))
        master.prizes = master.prizes or []
        if not isinstance(master.prizes, (dict, list)):
            raise ModelEditValidError(u'ハートプレゼント報酬のJsonが壊れています.eventid=%s, number=%s' % (master.eventid, master.number))
        for prizeidlist in master.get_pointprizes().values():
            checkPrize(prizeidlist, u'ハートプレゼント報酬')
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
