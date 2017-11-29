# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.Happening import HappeningMaster, RaidMaster
from defines import Defines
from platinumegg.app.cabaret.util.scout import ScoutDropItemSelector
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = HappeningMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        boss = AppModelChoiceField(RaidMaster, required=False, label=u'レイドボス')
    
    def setting_property(self):
        self.MODEL_LABEL = u'ハプニング'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        model_mgr = self.getModelMgr()
        try:
            selector = ScoutDropItemSelector(None, master, 0)
            selector.validate()
        except CabaretError, err:
            raise ModelEditValidError('%s, happening=%d' % (err.value, master.id))
        
        raid = model_mgr.get_model(RaidMaster, master.boss)
        if raid is None:
            raise ModelEditValidError(u'存在しないレイドが設定されています.happening=%d' % master.id)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
