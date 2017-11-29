# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError, AppModelChoiceField
from platinumegg.app.cabaret.models.LevelUpBonus import LevelUpBonusMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from defines import Defines
from platinumegg.app.cabaret.models.Present import Present, PrizeMaster
from platinumegg.app.cabaret.util.api import BackendApi
import settings

class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = LevelUpBonusMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        levelupbonus_text = AppModelChoiceField(TextMaster, required=False, label=u'レベルアップ達成ボーナス報酬文言')

    def __valid_master(self, master):
        if not master.is_public:
            return
        model_mgr = self.getModelMgr()
        self.__check_prize_id(model_mgr, master)

    def __check_prize_id(self, model_mgr, master):
        prizemasterlist = BackendApi.get_prizemaster_list(model_mgr, master.prize_id, settings.DB_READONLY)
        columns = []
        for prizemaster in prizemasterlist:
            if prizemaster.goldkey != 0:
                columns.append(u"金の鍵")
            if prizemaster.silverkey != 0:
                columns.append(u"銀の鍵")
            if prizemaster.tanzaku_number != 0:
                columns.append(u"短冊")
            if prizemaster.gold != 0:
                columns.append(u"ゴールド")
            if prizemaster.gachapt != 0:
                columns.append(u"ガチャPT")
        if columns:
            self.__raise_ModelEditValidError(master.id,(u'報酬に「%s」を設定することはできません' % ",".join(columns)))

    def __raise_ModelEditValidError(self,master_id,message):
        raise ModelEditValidError(message + (' id=%d' % master_id))

    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

    def setting_property(self):
        self.MODEL_LABEL = u'レベルアップ報酬の設定'

def main(request):
    return Handler.run(request)
