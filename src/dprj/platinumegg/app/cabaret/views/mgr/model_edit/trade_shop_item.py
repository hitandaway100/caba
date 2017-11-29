# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError, AppModelChoiceField
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.TradeShop import TradeShopItemMaster, TradeShopMaster
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.models.Item import ItemMaster
from platinumegg.app.cabaret.models.Card import CardMaster

class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = TradeShopItemMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        pt_change_text = AppModelChoiceField(TextMaster, required=False, label=u'Pt交換文言')
    
    def setting_property(self):
        self.MODEL_LABEL = u'トレードショップアイテムマスター'

    def valid_insert(self, master):
        self.__valid_master(master)

    def valid_update(self, master):
        self.__valid_master(master)

    def __valid_master(self, master):
        model_mgr = self.getModelMgr()

        self.__valid_item_type_and_id(model_mgr, master)
        self.__valid_itemnum_and_stock(model_mgr, master)
        self.__valid_use_point(model_mgr, master)
        self.__valid_additional_ticket_id(model_mgr, master)

        model_mgr.write_all()

    def __valid_item_type_and_id(self, model_mgr, master):
        if master.itype == Defines.ItemType.ITEM:
            model = model_mgr.get_model(ItemMaster, master.itemid)
            if model is None:
                raise ModelEditValidError(u'アイテムIDに、ItemMasterに存在しないIDが指定されています.id=%d' % master.id)

        if master.itype == Defines.ItemType.CARD:
            model = model_mgr.get_model(CardMaster, master.itemid)
            if model is None:
                raise ModelEditValidError(u'アイテムIDに、CardMasterに存在しないIDが指定されています.id=%d' % master.id)

    def __valid_itemnum_and_stock(self, model_mgr, master):
        if master.itemnum <= 0:
            raise ModelEditValidError(u'「一回の交換で取得できる個数」の値が０以下です.id=%d' % master.id)

        if master.stock < 0:
            raise ModelEditValidError(u'「交換可能回数」の値がマイナスです.id=%d' % master.id)

    def __valid_use_point(self, model_mgr, master):
        if master.use_point < 0:
            raise ModelEditValidError(u'「交換する際に使うポイント」の値が、マイナスです.id=%d' % master.id)

    def __valid_additional_ticket_id(self, model_mgr, master):
        if master.itype == Defines.ItemType.ADDITIONAL_GACHATICKET:
            if master.additional_ticket_id == 0:
                raise ModelEditValidError(u'itemTypeが追加分ガチャチケットですが、追加ガチャチケット種別が指定されていません.id=%d' % master.id)



def main(request):
    return Handler.run(request)
