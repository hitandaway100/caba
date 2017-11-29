# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.Shop import ShopItemMaster
from defines import Defines
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.app.cabaret.models.Item import ItemMaster
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = ShopItemMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        schedule = AppModelChoiceField(ScheduleMaster, required=False, label=u'期間')
    
    def setting_property(self):
        self.MODEL_LABEL = u'ショップの商品'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        try:
            prizelist = master.getItemList()
        except CabaretError, err:
            raise ModelEditValidError(err.value)
        
        model_mgr = self.getModelMgr()
        for prize in prizelist:
            if 0 < prize.cardid and model_mgr.get_model(CardMaster, prize.cardid) is None:
                raise ModelEditValidError(u'商品に存在しないカードが設定されています.prize=%d' % master.id)
            elif 0 < prize.itemid and model_mgr.get_model(ItemMaster, prize.itemid) is None:
                raise ModelEditValidError(u'商品に存在しないアイテムが設定されています.prize=%d' % master.id)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
