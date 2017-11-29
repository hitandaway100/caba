# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError, AppModelChoiceField
from defines import Defines
from platinumegg.app.cabaret.models.Gacha import GachaHeaderMaster, GachaMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = GachaHeaderMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        id = AppModelChoiceField(GachaMaster, required=False, label=u'ガチャID')
    
    def setting_property(self):
        self.MODEL_LABEL = u'引抜のヘッダー画像設定'
        self.html_param['Defines'] = Defines
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        if not isinstance(master.header, list):
            raise ModelEditValidError(u'headerのJSONが壊れています.master=%d' % master.id)
#        elif len(master.header) == 0:
#            raise ModelEditValidError(u'空のheaderが設定されています.master=%d' % master.id)
        
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)
    
def main(request):
    return Handler.run(request)
