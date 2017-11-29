# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from platinumegg.app.cabaret.models.Treasure import TreasureGoldMaster
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = TreasureGoldMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'宝箱(金)'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        try:
            model_mgr = ModelRequestMgr()
            BackendApi.create_present(model_mgr, 0, 1, master.itype, master.ivalue1, master.ivalue2, do_set_save=False)
        except CabaretError, err:
            raise ModelEditValidError(u'%s:id=%d' % (err.value, master.id))
        except Exception, err:
            raise ModelEditValidError(u'%s:%d' % (err, master.id))
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
