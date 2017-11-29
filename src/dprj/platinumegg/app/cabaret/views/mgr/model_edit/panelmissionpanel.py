# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.models.Mission import PanelMissionPanelMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = PanelMissionPanelMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        prize_text = AppModelChoiceField(TextMaster, required=False, label=u'報酬テキスト')
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        model_mgr = self.getModelMgr()
        
        prizes = master.prizes
        if len(prizes) != len(list(set(prizes))):
            raise ModelEditValidError(u'報酬が重複しています.master=%d' % master.id)
        
        prizelist = BackendApi.get_prizemaster_list(model_mgr, prizes)
        if len(prizes) != len(prizelist):
            raise ModelEditValidError(u'存在しない報酬が設定されています.master=%d' % master.id)
        
        # ミッション確認.
        if len(BackendApi.get_panelmission_missionmaster_by_panelid(model_mgr, master.id)) != Defines.PANELMISSION_MISSIN_NUM_PER_PANEL:
            raise ModelEditValidError(u'ミッション数が足りません.panelmissionmissionmasterを設定してください.master=%d' % master.id)
    
    def setting_property(self):
        self.MODEL_LABEL = u'パネルミッションのパネル'
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)
    
    def valid_write_end(self):
        mid = 0
        for model in PanelMissionPanelMaster.fetchValues(order_by='id'):
            if mid != (model.id - 1):
                raise ModelEditValidError(u'IDが1から始まる連番になっていません')
            mid = model.id

def main(request):
    return Handler.run(request)

