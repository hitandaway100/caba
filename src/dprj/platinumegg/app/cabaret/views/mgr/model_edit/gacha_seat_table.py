# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.Gacha import GachaSeatMaster,\
    GachaSeatTableMaster
from defines import Defines


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = GachaSeatTableMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'premium',
            )
        seatid = AppModelChoiceField(GachaSeatMaster, required=False, label=u'シートID')
    
    def setting_property(self):
        self.MODEL_LABEL = u'引き抜きシートテーブル'
        self.valid_error_num = 0

    def __valid_master(self, master):
        if not master.is_public:
            return
        
        if master.seatid and GachaSeatMaster.getByKey(master.seatid) is None:
            raise ModelEditValidError(u'存在しないシートが設定されています.seattable=%d' % master.id)
        try:
            seatidlist = list(set(dict(master.specialseat).values()))
        except:
            raise ModelEditValidError(u'specialseatが壊れています.seattable=%d' % master.id)
        if len(seatidlist) != len(GachaSeatMaster.getByKey(seatidlist)):
            raise ModelEditValidError(u'存在しないシートが設定されています.seattable=%d' % master.id)

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
