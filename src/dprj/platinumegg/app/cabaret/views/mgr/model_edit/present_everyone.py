# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField
from platinumegg.app.cabaret.models.PresentEveryone import PresentEveryoneLoginBonusMaster
from defines import Defines
from platinumegg.app.cabaret.models.Text import TextMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = PresentEveryoneLoginBonusMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        textid = AppModelChoiceField(TextMaster, required=False, label=u'プレゼントの文言')
    
    def setting_property(self):
        self.MODEL_LABEL = u'全プレ(ログインボーナス受け取り時)'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        self.checkPrize(master, master.prizes)
        for prizes in master.prizes_daily.values():
            self.checkPrize(master, prizes, u'日別報酬')
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
