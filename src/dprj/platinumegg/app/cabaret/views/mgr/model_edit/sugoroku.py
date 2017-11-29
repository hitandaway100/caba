# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusSugorokuMaster,\
    LoginBonusSugorokuMapMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = LoginBonusSugorokuMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'双六ログインボーナス'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        model_mgr = self.getModelMgr()
        maps = model_mgr.get_models(LoginBonusSugorokuMapMaster, master.maps)
        if len(maps) != len(master.maps):
            raise ModelEditValidError(u'存在しないマップが設定されています.sugoroku={}'.format(master.id))
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
