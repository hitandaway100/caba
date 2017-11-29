# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError, AppModelChoiceField
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.TradeShop import TradeShopMaster, TradeShopItemMaster
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster

class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = TradeShopMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        schedule = AppModelChoiceField(ScheduleMaster, required=False, label=u'期間')
    
    def setting_property(self):
        self.MODEL_LABEL = u'トレードショップ'

    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

    def __valid_master(self, master):
        model_mgr = self.getModelMgr()
        self.__check_schedule(model_mgr, master)
        self.__check_trade_shop_item_masetr_ids(model_mgr, master)

        model_mgr.write_all()

    def __check_schedule(self, model_mgr, master):
        model = model_mgr.get_model(ScheduleMaster, master.schedule)
        if model is None:
            raise ModelEditValidError(u'スケジュールに、存在しないIDが指定されています.id=%d' % master.id)

    def __check_trade_shop_item_masetr_ids(self, model_mgr, master):
        if not isinstance(master.trade_shop_item_master_ids, (list)):
            raise ModelEditValidError(u'trade_shop_item_master_idsのJsonが壊れています.id=%d' % master.id)

        for trade_shop_item_master_id in master.trade_shop_item_master_ids:
            model = model_mgr.get_model(TradeShopItemMaster, trade_shop_item_master_id)
            if model is None:
                raise ModelEditValidError(u'trade_shop_item_master_idsで指定されているidがTradeShopItemMasterに存在しません.id=%d' % master.id)


def main(request):
    return Handler.run(request)