# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField
from platinumegg.app.cabaret.models.Trade import TradeMaster
from defines import Defines
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = TradeMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        schedule = AppModelChoiceField(ScheduleMaster, required=False, label=u'期間')
    
    def setting_property(self):
        self.MODEL_LABEL = u'秘宝交換'

def main(request):
    return Handler.run(request)
