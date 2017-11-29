# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Infomation import PopupMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = PopupMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )

    def setting_property(self):
        self.MODEL_LABEL = u'ポップアップ'
        self.valid_error_num = 0

    def __valid_master(self, master):
        if not master.is_public:
            return

        model_mgr = self.getModelMgr()
        if master.banner:
            bannermaster = BackendApi.get_eventbanner(model_mgr, master.banner)
            if bannermaster is None:
                raise ModelEditValidError(u'存在しないバナーが設定されています.popup=%d' % master.id)

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
