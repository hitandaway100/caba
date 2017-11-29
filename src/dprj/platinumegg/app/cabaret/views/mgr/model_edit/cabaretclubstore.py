# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.models.CabaretClub import CabaClubEventMaster,\
    CabaClubStoreMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = CabaClubStoreMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'キャバクラ店舗'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        # 発生イベント.
        if not isinstance(master.events, list):
            raise ModelEditValidError(u'発生イベントは[[イベントID,発生率],...]という形式で設定して下さい.id={}'.format(master.id))
        event_dict = dict(master.events)
        if len(event_dict) != len(master.events):
            raise ModelEditValidError(u'発生イベントが重複しています.id={}'.format(master.id))
        for k,v in event_dict.items():
            if not isinstance(v, (int, long)) or v < 1:
                raise ModelEditValidError(u'イベント発生率は自然数で入力して下さい.id={},eventid={}'.format(master.id, k))
        model_mgr = self.getModelMgr()
        eventmaster_list = model_mgr.get_models(CabaClubEventMaster, event_dict.keys())
        if len(eventmaster_list) != len(event_dict):
            raise ModelEditValidError(u'発生イベントに存在しないイベントが含まれています.id={}'.format(master.id))
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
