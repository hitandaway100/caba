# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AppModelForm,\
    AppModelChoiceField, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.util.scout import ScoutHappeningSelector
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Boss import BossMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.models.raidevent.RaidEventScout import RaidEventScoutStageMaster
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventMaster
from platinumegg.app.cabaret.views.mgr.model_edit.eventstage import EventStageHandler


class Handler(EventStageHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = RaidEventScoutStageMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        eventid = AppModelChoiceField(RaidEventMaster, required=False, label=u'レイドイベントマスターID')
        boss = AppModelChoiceField(BossMaster, required=False, label=u'ボス')
        earlybonus_text = AppModelChoiceField(TextMaster, required=False, label=u'早期クリアボーナス報酬文言')
    
    def setting_property(self):
        self.MODEL_LABEL = u'レイドイベント(ステージ)'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        self.valid_stagedata(master, RaidEventMaster)
        
        master.happenings_timebonus = master.happenings_timebonus or []
        master.happenings_big = master.happenings_big or []
        master.happenings_timebonus_big = master.happenings_timebonus_big or []
        try:
            ScoutHappeningSelector(None, master, happenings=master.happenings_timebonus).validate()
            ScoutHappeningSelector(None, master, happenings=master.happenings_big).validate()
            ScoutHappeningSelector(None, master, happenings=master.happenings_timebonus_big).validate()
        except CabaretError, err:
            raise ModelEditValidError('%s, happening=%d' % (err.value, master.id))
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
