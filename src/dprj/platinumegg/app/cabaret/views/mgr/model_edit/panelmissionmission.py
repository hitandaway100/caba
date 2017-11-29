# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.models.Mission import PanelMissionMissionMaster,\
    PanelMissionPanelMaster
from django.core.exceptions import ValidationError
from platinumegg.app.cabaret.util.mission import PanelMissionConditionExecuter
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = PanelMissionMissionMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'id',
            )
        panel = AppModelChoiceField(PanelMissionPanelMaster, required=False, label=u'パネルID')
        prize_text = AppModelChoiceField(TextMaster, required=False, label=u'報酬テキスト')
        
        def _valid_primary_key(self):
            panel = int(self.cleaned_data.get('panel'))
            number = int(self.cleaned_data.get('number'))
            if panel <= 0:
                raise ValidationError(u'panelは1以上を指定して下さい')
            elif number <= 0:
                raise ValidationError(u'numberは1以上を指定して下さい')
            return PanelMissionMissionMaster.makeID(panel, number)
    
    def __valid_master(self, master):
        master.id = PanelMissionMissionMaster.makeID(master.panel, master.number)
        
        if not master.is_public:
            return
        model_mgr = self.getModelMgr()
        
        prizes = master.prizes
        if len(prizes) != len(list(set(prizes))):
            raise ModelEditValidError(u'報酬が重複しています.panel=%d,number=%d' % (master.panel, master.number))
        
        prizelist = BackendApi.get_prizemaster_list(model_mgr, prizes)
        if len(prizes) != len(prizelist):
            raise ModelEditValidError(u'存在しない報酬が設定されています.panel=%d,number=%d' % (master.panel, master.number))
        
        try:
            PanelMissionConditionExecuter().validateMission(master)
        except CabaretError, err:
            raise ModelEditValidError(u'達成条件が不正です:%s.panel=%d,number=%d' % (err.value, master.panel, master.number))
    
    def setting_property(self):
        self.MODEL_LABEL = u'パネルミッションのミッション'
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)
    
    def valid_write_end(self):
        errors = []
        
        master_all = PanelMissionMissionMaster.fetchValues()
        master_all.sort(key=lambda x:x.id)
        
        panel = None
        number = 0
        for master in master_all:
            if panel != master.panel:
                if panel is not None:
                    if number < Defines.PANELMISSION_MISSIN_NUM_PER_PANEL:
                        # パネルが足りてない.
                        for n in xrange(number+1, Defines.PANELMISSION_MISSIN_NUM_PER_PANEL+1):
                            errors.append(u'不足:panel=%d, number=%d' % (panel, n))
                panel = master.panel
                number = 0
            
            if Defines.PANELMISSION_MISSIN_NUM_PER_PANEL < master.number:
                # パネルが余分.
                errors.append(u'余分:panel=%d, number=%d' % (panel, master.number))
            elif number == master.number:
                errors.append(u'重複:panel=%d, number=%d' % (panel, number))
            elif number != (master.number - 1):
                for n in xrange(number+1, master.number):
                    errors.append(u'不足:panel=%d, number=%d' % (panel, n))
            
            number = master.number
        
        if errors:
            raise ModelEditValidError('<br />'.join(errors))

def main(request):
    return Handler.run(request)

