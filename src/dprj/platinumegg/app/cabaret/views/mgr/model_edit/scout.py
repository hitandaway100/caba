# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.Scout import ScoutMaster
from defines import Defines
from platinumegg.app.cabaret.models.Area import AreaMaster
from platinumegg.app.cabaret.util.scout import ScoutDropItemSelector,\
    ScoutHappeningSelector
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = ScoutMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        area = AppModelChoiceField(AreaMaster, required=False, label=u'エリア')
    
    def setting_property(self):
        self.MODEL_LABEL = u'スカウト'
    
    def __valid_master(self, master):
        try:
            ScoutDropItemSelector(None, master, 0).validate()
            ScoutHappeningSelector(None, master).validate()
        except CabaretError, err:
            raise ModelEditValidError('%s, happening=%d' % (err.value, master.id))
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)
    
    def valid_write_end(self):
        master_all = {}
        for master in ScoutMaster.fetchValues():
            master_all[master.id] = master
        
        errors = []
        for master in master_all.values():
            if master.opencondition != 0 and master_all.get(master.opencondition) is None:
                errors.append(u'開放条件のスカウトが存在しません, scout=%d' % master.id)
            elif master.opencondition == master.id:
                errors.append(u'開放条件のスカウトが自分自身です, scout=%d' % master.id)
        if errors:
            raise ModelEditValidError('<br />'.join(errors))

def main(request):
    return Handler.run(request)
