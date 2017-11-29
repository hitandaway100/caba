# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.Memories import MemoriesMaster,\
    MoviePlayList, VoicePlayList, PcMoviePlayList
from defines import Defines
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.app.cabaret.util.api import BackendApi
import settings
import settings_sub

class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = MemoriesMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        cardid = AppModelChoiceField(CardMaster, required=False, label=u'カードのID')
    
    def setting_property(self):
        self.MODEL_LABEL = u'思い出アルバム'
        
        playlist_all = BackendApi.get_movieplaylist_all(self.getModelMgr(), using=settings.DB_READONLY)
        self.html_param['movieplaylist_all'] = playlist_all
        
        playlist_all = BackendApi.get_pcmovieplaylist_all(self.getModelMgr(), using=settings.DB_READONLY)
        self.html_param['pcmovieplaylist_all'] = playlist_all
        
        playlist_all = BackendApi.get_voiceplaylist_all(self.getModelMgr(), using=settings.DB_READONLY)
        self.html_param['voiceplaylist_all'] = playlist_all

        self.valid_error_num = 0

    def __valid_master(self, master):
        if not master.is_public:
            return
        elif CardMaster.getValuesByKey(master.cardid) is None:
            raise ModelEditValidError(u'思いで開放に必要なカードが存在しません.id=%d, card=%d' % (master.id, master.cardid))
        if master.contenttype == Defines.MemoryContentType.MOVIE and not settings_sub.IS_LOCAL and not settings_sub.IS_DEV:
            if not str(master.contentdata).isdigit() or not MoviePlayList.getByKey(int(master.contentdata)):
                raise ModelEditValidError(u'存在しない動画が設定されています.id=%d' % master.id)
        if master.contenttype == Defines.MemoryContentType.MOVIE_PC and not settings_sub.IS_LOCAL and not settings_sub.IS_DEV:
            if not str(master.contentdata).isdigit() or not PcMoviePlayList.getByKey(int(master.contentdata)):
                raise ModelEditValidError(u'存在しない動画が設定されています.id=%d' % master.id)
        if master.contenttype == Defines.MemoryContentType.VOICE and not settings_sub.IS_LOCAL:
            if not str(master.contentdata).isdigit() or not VoicePlayList.getByKey(int(master.contentdata)):
                raise ModelEditValidError(u'存在しない音声が設定されています.id=%d' % master.id)

        if self.valid_error_num < 10:
            for record in self.allmasters:
                if master.id == record.id:
                    self.valid_error_num += 1
                    raise ModelEditValidError(u'IDが重複しています.id={}'.format(master.id))
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)
    
    def get_index_template_name(self):
        return 'model_edit/memories'

    def allow_csv(self):
        return True

def main(request):
    return Handler.run(request)
