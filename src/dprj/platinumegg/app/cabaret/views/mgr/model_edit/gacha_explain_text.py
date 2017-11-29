# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.GachaExplain import GachaExplainMaster
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = GachaExplainMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )

    def setting_property(self):
        self.MODEL_LABEL = u'ガチャの説明テキスト設定'
        self.valid_error_num = 0

    def allow_csv(self):
        return True


def main(request):
    return Handler.run(request)
