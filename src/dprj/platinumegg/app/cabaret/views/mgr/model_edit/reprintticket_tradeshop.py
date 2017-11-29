# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError, AppModelChoiceField
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.models.ReprintTicketTradeShop import *
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster

class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = ReprintTicketTradeShopMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        card_id = AppModelChoiceField(CardMaster, required=False, label=u'カードID')
        reprintticket_trade_text = AppModelChoiceField(TextMaster, required=False, label=u'復刻チケット交換文言')
        schedule_id = AppModelChoiceField(ScheduleMaster, required=False, label=u'期間')

    def setting_property(self):
        self.MODEL_LABEL = u'復刻チケット交換所'
        self.valid_error_num = 0

    def __valid_master(self, master):
        if not master.is_public:
            return

        model_mgr = self.getModelMgr()
        if self.valid_error_num < 10:
            for record in self.allmasters:
                if master.id == record.id:
                    self.valid_error_num += 1
                    raise ModelEditValidError(u'IDが重複しています.id={}'.format(master.id))

    def valid_insert(self, master):
        self.__valid_master(master)

    def valid_update(self, master):
        self.__valid_master(master)

    def allow_csv(self):
        return True

def main(request):
    return Handler.run(request)
