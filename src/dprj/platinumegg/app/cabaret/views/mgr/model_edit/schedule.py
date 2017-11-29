# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from defines import Defines


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = ScheduleMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )

    def setting_property(self):
        self.MODEL_LABEL = u'スケジュール'
        self.valid_error_num = 0

    def __valid_master(self, master):
        if not master.is_public:
            return

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
