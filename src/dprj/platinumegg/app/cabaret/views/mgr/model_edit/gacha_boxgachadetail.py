# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.Gacha import GachaMaster, GachaBoxGachaDetailMaster
from defines import Defines
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.app.cabaret.models.Present import PrizeMaster
#from platinumegg.app.cabaret.util.gacha import GachaBox, GachaMasterSet,\    GachaBoxGroup
from platinumegg.app.cabaret.util.cabareterror import CabaretError
#from platinumegg.app.cabaret.models.TradeShop import TradeShopMaster

class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = GachaBoxGachaDetailMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )

    def setting_property(self):
        self.MODEL_LABEL = u'BOXガチャ詳細設定'
        self.valid_error_num = 0

    def __valid_master(self, master):
        if master.allowreset_rarity and master.allowreset_cardidlist:
            raise ModelEditValidError(u'リセット可能レアリティとリセット可能キャストの両方が設定されています.gacha={}'.format(master.id))

def main(request):
    return Handler.run(request)
