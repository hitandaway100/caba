# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField
from platinumegg.app.cabaret.models.PresentEveryone import PresentEveryoneMypageMaster
from defines import Defines
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = PresentEveryoneMypageMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        schedule = AppModelChoiceField(ScheduleMaster, required=False, label=u'開催期間')
        textid = AppModelChoiceField(TextMaster, required=False, label=u'プレゼントの文言')
    
    def setting_property(self):
        self.MODEL_LABEL = u'全プレ(マイページアクセス時)'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        self.checkPrize(master, master.prizes)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
