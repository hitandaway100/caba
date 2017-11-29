# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError, AppModelChoiceField
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusTimeLimitedDaysMaster,\
    LoginBonusTimeLimitedMaster
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from django.core.exceptions import ValidationError


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = LoginBonusTimeLimitedDaysMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'id',
            )
        mid = AppModelChoiceField(LoginBonusTimeLimitedMaster, required=False, label=u'マスターID')
        
        def _valid_primary_key(self):
            day = int(self.cleaned_data.get('day'))
            mid = int(self.cleaned_data.get('mid'))
            if day <= 0:
                raise ValidationError(u'日数は1以上を指定して下さい')
            elif mid <= 0:
                raise ValidationError(u'マスターIDは1以上を指定して下さい')
            return LoginBonusTimeLimitedDaysMaster.makeID(mid, day)
    
    def setting_property(self):
        self.MODEL_LABEL = u'ロングログインボーナスの報酬設定'
    
    def __valid_master(self, master):
        master.id = LoginBonusTimeLimitedDaysMaster.makeID(master.mid, master.day)
        
        if not master.is_public:
            return
        
        model_mgr = self.getModelMgr()
        
        if model_mgr.get_model(LoginBonusTimeLimitedMaster, master.mid) is None:
            raise ModelEditValidError(u'存在しないマスターIDが設定されています.id=%d' % master.id)
        
        prizes = master.prizes
        if len(prizes) != len(list(set(prizes))):
            raise ModelEditValidError(u'報酬が重複しています.id=%d' % master.id)
        prizelist = BackendApi.get_prizemaster_list(model_mgr, prizes)
        if len(prizes) != len(prizelist):
            raise ModelEditValidError(u'存在しない報酬が設定されています.id=%d' % master.id)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
