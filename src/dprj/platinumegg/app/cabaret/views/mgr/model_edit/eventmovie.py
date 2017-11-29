# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.models.Memories import EventMovieMaster
from platinumegg.app.cabaret.util.api import BackendApi


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = EventMovieMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'イベント動画'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        model_mgr = self.getModelMgr()
        
        if not BackendApi.get_movieplaylist_dict_by_uniquename(model_mgr, [master.sp]):
            raise ModelEditValidError(u'SP用の動画が存在しません.eventmovie=%d, filename=%s' % (master.id, master.sp))
        elif not BackendApi.get_pcmovieplaylist_dict_by_uniquename(model_mgr, [master.pc]):
            raise ModelEditValidError(u'PC用の動画が存在しません.eventmovie=%d, filename=%s' % (master.id, master.pc))
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
