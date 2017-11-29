# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusTimeLimitedMaster
from defines import Defines
from platinumegg.app.cabaret.models.Text import TextMaster

class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = LoginBonusTimeLimitedMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        textid = AppModelChoiceField(TextMaster, required=False, label=u'報酬テキストID')
    
    def setting_property(self):
        self.MODEL_LABEL = u'ロングログインボーナス'
    

def main(request):
    return Handler.run(request)
