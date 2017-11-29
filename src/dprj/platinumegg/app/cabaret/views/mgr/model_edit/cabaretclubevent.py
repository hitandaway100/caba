# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm
from defines import Defines
from platinumegg.app.cabaret.models.CabaretClub import CabaClubEventMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = CabaClubEventMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'キャバクラの発生イベント'
    
    def __valid_master(self, master):
        # 発生イベント.
        if master.ua_cost == 0:
            master.ua_cost = master.seconds * 10 / 60
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
