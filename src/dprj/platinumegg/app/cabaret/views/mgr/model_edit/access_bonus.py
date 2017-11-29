# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from platinumegg.app.cabaret.models.AccessBonus import AccessBonusMaster
from defines import Defines
from django.core.exceptions import ValidationError
from platinumegg.app.cabaret.util.api import BackendApi

class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = AccessBonusMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        def _valid_primary_key(self):
            p_key = self.Meta.model.get_primarykey_column()
            p_value = self.cleaned_data.get(p_key)
            if p_value < 0:
                raise ValidationError(u'%sは0以上を指定して下さい' % p_key)
            return p_value
    
    def setting_property(self):
        self.MODEL_LABEL = u'アクセスボーナス'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        model_mgr = self.getModelMgr()
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

def main(request):
    return Handler.run(request)
