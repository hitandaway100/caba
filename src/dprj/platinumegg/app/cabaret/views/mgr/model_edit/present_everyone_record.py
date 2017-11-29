# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from platinumegg.app.cabaret.models.PresentEveryone import PresentEveryoneMypageMaster,\
    PresentEveryoneRecord, PresentEveryoneLoginBonusMaster
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = PresentEveryoneRecord
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        
        def _valid_primary_key(self):
            return self.cleaned_data.get('date')
    
    def setting_property(self):
        self.MODEL_LABEL = u'予約済みの全プレ'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        model_mgr = self.getModelMgr()
        
        def checkMaster(master_cls, midlist):
            if len(midlist) != len(list(set(midlist))):
                raise ModelEditValidError(u'全プレが重複しています.id=%d' % master.date.strftime("%Y-%m-%d"))
            modellist = BackendApi.get_model_list(model_mgr, master_cls, midlist)
            if len(midlist) != len(modellist):
                raise ModelEditValidError(u'存在しない全プレが設定されています.id=%d' % master.date.strftime("%Y-%m-%d"))
        checkMaster(PresentEveryoneLoginBonusMaster, master.mid_loginbonus)
        checkMaster(PresentEveryoneMypageMaster, master.mid_mypage)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
