# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.app.cabaret.models.Tutorial import TutorialConfig
from platinumegg.app.cabaret.models.Area import AreaMaster
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.treasure import TreasureUtil
from platinumegg.app.cabaret.models.Memories import MemoriesMaster

TreasureMaster = TreasureUtil.get_master_cls(Defines.TreasureType.TUTORIAL_TREASURETYPE)

class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = TutorialConfig
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
#        compositioncard = AppModelChoiceField(CardMaster, required=False, label=u'教育の素材で使用するカード')
        scoutdropcard = AppModelChoiceField(CardMaster, required=False, label=u'スカウトでドロップするカード')
        scoutarea = AppModelChoiceField(AreaMaster, required=False, label=u'チュートリアルのスカウトエリア')
        treasure = AppModelChoiceField(TreasureMaster, required=False, label=u'チュートリアルの宝箱')
        memories = AppModelChoiceField(MemoriesMaster, required=False, label=u'チュートリアルの思い出アルバム')
        pcmemories = AppModelChoiceField(MemoriesMaster, required=False, label=u'チュートリアルの思い出アルバム(PC)')
    
    def setting_property(self):
        self.MODEL_LABEL = u'チュートリアルの設定'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        model_mgr = self.getModelMgr()
        
        if master.scoutdropcard == 0 or model_mgr.get_model(CardMaster, master.scoutdropcard) is None:
            raise ModelEditValidError(u'スカウトでドロップするカードが存在しません.ctype=%d' % master.ctype)
        elif master.scoutarea == 0 and model_mgr.get_model(AreaMaster, master.scoutarea) is None:
            raise ModelEditValidError(u'エリアが存在しません.ctype=%d' % master.ctype)
        
        prizes = master.prizes
        if len(prizes) != len(list(set(prizes))):
            raise ModelEditValidError(u'報酬が重複しています.ctype=%d' % master.ctype)
        prizelist = BackendApi.get_prizemaster_list(model_mgr, prizes)
        if len(prizes) != len(prizelist):
            raise ModelEditValidError(u'存在しない報酬が設定されています.ctype=%d' % master.ctype)
        
        if master.treasure == 0 or model_mgr.get_model(TreasureMaster, master.treasure) is None:
            raise ModelEditValidError(u'スカウトでドロップする宝箱が存在しません.ctype=%d' % master.ctype)
        
        if master.memories == 0 or model_mgr.get_model(MemoriesMaster, master.memories) is None:
            raise ModelEditValidError(u'スカウトで閲覧する思い出アルバムが存在しません.ctype=%d' % master.ctype)
        
        if master.pcmemories == 0 or model_mgr.get_model(MemoriesMaster, master.pcmemories) is None:
            raise ModelEditValidError(u'スカウトで閲覧する思い出アルバムが存在しません.ctype=%d' % master.ctype)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
