# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError, AppModelChoiceField
from defines import Defines
from platinumegg.app.cabaret.models.battleevent.BattleEventPresent import BattleEventPresentContentMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.models.Present import PrizeMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = BattleEventPresentContentMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        prize_text = AppModelChoiceField(TextMaster, required=False, label=u'報酬文言')
    
    def setting_property(self):
        self.MODEL_LABEL = u'バトルイベント贈り物の中身'
    
    def __valid_master(self, master):
        
        if not master.is_public:
            return
        
        if not master.prizes:
            raise ModelEditValidError(u'報酬が設定されていません.battleeventpresentcontent:id=%d' % master.id)
        elif not isinstance(master.prizes, list):
            raise ModelEditValidError(u'報酬設定が壊れています.battleeventpresentcontent:id=%d' % master.id)
        
        prizeidlist = list(set(master.prizes))
        if len(prizeidlist) != len(master.prizes):
            raise ModelEditValidError(u'報酬が重複しています.battleeventpresentcontent:id=%d' % master.id)
        
        prizelist = PrizeMaster.getByKey(prizeidlist)
        if len(prizelist) != len(prizeidlist):
            raise ModelEditValidError(u'存在しない報酬が含まれています.battleeventpresentcontent:id=%d' % master.id)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
