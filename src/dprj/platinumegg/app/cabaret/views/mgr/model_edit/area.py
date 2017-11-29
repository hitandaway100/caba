# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.Area import AreaMaster
from defines import Defines
from platinumegg.app.cabaret.models.Boss import BossMaster
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.app.cabaret.util.api import BackendApi


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = AreaMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        schedule = AppModelChoiceField(ScheduleMaster, required=False, label=u'開催期間')
        boss = AppModelChoiceField(BossMaster, required=False, label=u'ボス')
    
    def setting_property(self):
        self.MODEL_LABEL = u'スカウトエリア'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        model_mgr = self.getModelMgr()
        bossid = master.boss
        boss = BackendApi.get_boss(model_mgr, bossid)
        if boss is None:
            raise ModelEditValidError(u'ボスが設定されていません.area=%d' % master.id)
        prizes = master.prizes
        if len(prizes) != len(list(set(prizes))):
            raise ModelEditValidError(u'報酬が重複しています.area=%d' % master.id)
        
        prizelist = BackendApi.get_prizemaster_list(model_mgr, prizes)
        if len(prizes) != len(prizelist):
            raise ModelEditValidError(u'存在しない報酬が設定されています.area=%d' % master.id)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)
    
    def valid_write_end(self):
        area_all = {}
        for area in AreaMaster.fetchValues():
            area_all[area.id] = area
        
        errors = []
        for area in area_all.values():
            if area.opencondition != 0 and area_all.get(area.opencondition) is None:
                errors.append(u'開放条件のエリアが存在しません, area=%d' % area.id)
            elif area.opencondition == area.id:
                errors.append(u'開放条件のエリアが自分自身です, area=%d' % area.id)
        if errors:
            raise ModelEditValidError('<br />'.join(errors))

def main(request):
    return Handler.run(request)
