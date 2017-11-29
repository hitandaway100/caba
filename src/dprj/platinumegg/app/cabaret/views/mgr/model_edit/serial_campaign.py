# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.models.SerialCampaign import SerialCampaignMaster
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Text import TextMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = SerialCampaignMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        schedule = AppModelChoiceField(ScheduleMaster, required=False, label=u'入力可能期間')
        prize_text = AppModelChoiceField(TextMaster, required=False, label=u'報酬文言')
    
    def setting_property(self):
        self.MODEL_LABEL = u'シリアルキャンペーン'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        model_mgr = self.getModelMgr()
        
        def checkPrize(prizeidlist, name):
            if len(prizeidlist) != len(list(set(prizeidlist))):
                raise ModelEditValidError(u'%sが重複しています.id=%d' % (name, master.id))
            prizelist = BackendApi.get_prizemaster_list(model_mgr, prizeidlist)
            if len(prizeidlist) != len(prizelist):
                raise ModelEditValidError(u'%sに存在しない報酬が設定されています.id=%d' % (name, master.id))
        
        if not isinstance(master.prizes, list):
            raise ModelEditValidError(u'報酬のJsonが壊れています.id=%d' % master.id)
        
        checkPrize(master.prizes, u'シリアルコードの報酬')
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
