# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm
from platinumegg.app.cabaret.models.Text import TextMaster
from defines import Defines


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = TextMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'テキスト文言'
        self.html_param['Defines'] = Defines
    
    def get_index_template_name(self):
        return 'model_edit/textmaster'

def main(request):
    return Handler.run(request)
