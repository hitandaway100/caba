# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm
from platinumegg.app.cabaret.models.Infomation import InfomationMaster
from defines import Defines


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = InfomationMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'お知らせ'
    
    def is_editable(self):
        """リリース環境で編集可能フラグ.
        """
        return True

def main(request):
    return Handler.run(request)
