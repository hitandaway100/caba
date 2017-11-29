# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.Invite import InviteMaster
from defines import Defines
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = InviteMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        schedule = AppModelChoiceField(ScheduleMaster, required=False, label=u'期間')
    
    def setting_property(self):
        self.MODEL_LABEL = u'招待'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        if not isinstance(master.prizes, (dict, list)):
            raise ModelEditValidError(u'報酬のJsonが壊れています.invite=%d' % master.id)
        for prizeidlist in master.get_prizes().values():
            self.checkPrize(master, prizeidlist, u'招待報酬', u'invite')
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
