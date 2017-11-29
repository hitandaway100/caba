# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError, AppModelChoiceField
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventMaster
from platinumegg.app.cabaret.models.raidevent.RaidCardMixer import RaidEventRecipeMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = RaidEventRecipeMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        eventid = AppModelChoiceField(RaidEventMaster, required=False, label=u'イベントID')
    
    def setting_property(self):
        self.MODEL_LABEL = u'レイドイベント交換所アイテム'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        elif master.itemnum < 1:
            raise ModelEditValidError(u'アイテム個数が設定されていません.recipe=%d' % master.id)
        
        model_mgr = self.getModelMgr()
        
        itype = master.itype
        if not Defines.ItemType.TRADE_TYPES.has_key(itype):
            raise ModelEditValidError(u'指定できないitypeです.recipe=%d' % master.id)
        
        if itype == Defines.ItemType.ITEM:                   # アイテム.
            itemmaster = BackendApi.get_itemmaster(model_mgr, master.itemid)
            if itemmaster is None:
                raise ModelEditValidError(u'存在しないアイテムが設定されています.recipe=%d' % master.id)
        elif itype == Defines.ItemType.CARD:                   # カード.
            cardmaster = BackendApi.get_cardmasters([master.itemid], model_mgr).get(master.itemid)
            if cardmaster is None:
                raise ModelEditValidError(u'存在しないキャストが設定されています.recipe=%d' % master.id)
        elif itype == Defines.ItemType.EVENT_GACHATICKET:      # イベントガチャチケット.
            eventmaster = BackendApi.get_raideventmaster(model_mgr, master.itemid)
            if eventmaster is None or eventmaster.id != master.eventid:
                raise ModelEditValidError(u'イベントガチャチケットのイベントIDが不正です.recipe=%d' % master.id)
        elif itype == Defines.ItemType.ADDITIONAL_GACHATICKET:      # 追加分ガチャチケット.
            Defines.GachaConsumeType.ADDITIONAL_TICKETS
            eventmaster = BackendApi.get_raideventmaster(model_mgr, master.itemid)
            if eventmaster is None or eventmaster.id != master.eventid:
                raise ModelEditValidError(u'イベントガチャチケットのイベントIDが不正です.recipe=%d' % master.id)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
