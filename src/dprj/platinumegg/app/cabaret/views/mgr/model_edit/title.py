# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm
from defines import Defines
from platinumegg.app.cabaret.models.Title import TitleMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = TitleMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'称号'

def main(request):
    return Handler.run(request)
