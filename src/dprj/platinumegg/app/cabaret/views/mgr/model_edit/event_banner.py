# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from platinumegg.app.cabaret.models.Infomation import EventBannerMaster
from defines import Defines


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = EventBannerMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'イベントバナー'
        self.valid_error_num = 0

    def __valid_master(self, master):
        if not master.is_public:
            return

        if self.valid_error_num < 10:
            for record in self.allmasters:
                if master.id == record.id:
                    self.valid_error_num += 1
                    raise ModelEditValidError(u'IDが重複しています.id={}'.format(master.id))

        self.__check_jumpto(master.id, master.jumpto)

    def __check_jumpto(self, masterid, jumpto):
        """jumpto のバリデーション"""
        if jumpto.find(' ') != -1:
            raise ModelEditValidError(u'jumpto のカラムに空白文字 (スペース) が入っています. eventbanner=%d' % masterid)

    def valid_insert(self, master):
        self.__valid_master(master)

    def valid_update(self, master):
        self.__valid_master(master)

    def allow_csv(self):
        return True

def main(request):
    return Handler.run(request)
