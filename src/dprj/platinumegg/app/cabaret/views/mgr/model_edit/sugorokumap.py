# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusSugorokuMapMaster
from platinumegg.app.cabaret.models.Present import PrizeMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = LoginBonusSugorokuMapMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'双六ログインボーナスのマップ'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        model_mgr = self.getModelMgr()
        prizelist = model_mgr.get_models(PrizeMaster, master.prize)
        if len(prizelist) != len(master.prize):
            raise ModelEditValidError(u'存在しない達成済み報酬が設定されています.map={},{}'.format(master.id))
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
