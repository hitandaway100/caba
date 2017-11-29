# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AppModelForm,\
    AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventStageMaster,\
    ScoutEventMaster
from defines import Defines
from platinumegg.app.cabaret.models.Boss import BossMaster
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Memories import EventMovieMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.views.mgr.model_edit.eventstage import EventStageHandler


class Handler(EventStageHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = ScoutEventStageMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        eventid = AppModelChoiceField(ScoutEventMaster, required=False, label=u'スカウトイベントマスターID')
        boss = AppModelChoiceField(BossMaster, required=False, label=u'ボス')
        movie = AppModelChoiceField(EventMovieMaster, required=False, label=u'イベント動画ID')
        earlybonus_text = AppModelChoiceField(TextMaster, required=False, label=u'早期クリアボーナス報酬文言')
    
    def setting_property(self):
        self.MODEL_LABEL = u'スカウトイベント(ステージ)'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        self.valid_stagedata(master, ScoutEventMaster)
        
        model_mgr = self.getModelMgr()
        
        master.bustup = master.bustup or []
        if not isinstance(master.bustup, list):
            raise ModelEditValidError(u'バストアップ画像は画像URLのリストで設定してください.stage=%d' % master.id)
        for bustup in master.bustup:
            if isinstance(bustup, (str, unicode)):
                continue
            raise ModelEditValidError(u'バストアップ画像は画像URLのリストで設定してください.stage=%d' % master.id)
        
        if master.movie:
            moviemaster = BackendApi.get_eventmovie_master(model_mgr, master.movie)
            if moviemaster is None:
                raise ModelEditValidError(u'存在しない動画が設定されています.stage=%d' % master.id)
        
        if 0 < master.eventrate_gachapt:
            if master.gachaptmin < 1 or master.gachaptmax < 1:
                raise ModelEditValidError(u'専用ガチャのポイントが設定されていません.stage=%d' % master.id)
            elif master.gachaptmax < master.gachaptmin:
                raise ModelEditValidError(u'専用ガチャポイントの最大値が最小値よりも小さくなっています.stage=%d' % master.id)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
