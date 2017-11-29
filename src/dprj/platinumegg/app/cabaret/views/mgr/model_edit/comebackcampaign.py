# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.models.Present import PrizeMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.models.ComeBack import ComeBackCampaignMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = ComeBackCampaignMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'premium',
            )
        prizetext = AppModelChoiceField(TextMaster, required=False, label=u'報酬文言')
    
    def setting_property(self):
        self.MODEL_LABEL = u'カムバックキャンペーン'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        idx = 1
        prizeidlist = []
        while True:
            arr = master.get_prize(idx)
            idx += 1
            if arr is None:
                break
            elif not arr:
                raise ModelEditValidError(u'%d日目に報酬が設定されていません.id=%d' % (idx-1, master.id))
            prizeidlist.extend(arr)
            
        if not prizeidlist:
            raise ModelEditValidError(u'報酬が設定されていません.id=%d' % master.id)
        prizeidlist = list(set(prizeidlist))
        
        prizelist = PrizeMaster.getByKey(prizeidlist)
        if len(prizeidlist) != len(prizelist):
            raise ModelEditValidError(u'存在しない報酬が設定されています.id=%d' % master.id)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
