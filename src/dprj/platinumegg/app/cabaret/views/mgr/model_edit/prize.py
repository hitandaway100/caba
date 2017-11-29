# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.Present import PrizeMaster
from defines import Defines
from platinumegg.app.cabaret.models.Item import ItemMaster
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = PrizeMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        itemid = AppModelChoiceField(ItemMaster, required=False, label=u'アイテムID')
        cardid = AppModelChoiceField(CardMaster, required=False, label=u'カードID')
        eventticket_id = AppModelChoiceField(RaidEventMaster, required=False, label=u'レイドイベントID')
    
    def setting_property(self):
        self.MODEL_LABEL = u'報酬'
        self.valid_error_num = 0

    def __valid_master(self, master):
        if not master.is_public:
            return
        
        model_mgr = self.getModelMgr()
        
        if 0 < master.cardid and model_mgr.get_model(CardMaster, master.cardid) is None:
            raise ModelEditValidError(u'存在しないカードが設定されています.prize=%d' % master.id)
        elif 0 < master.itemid and model_mgr.get_model(ItemMaster, master.itemid) is None:
            raise ModelEditValidError(u'存在しないアイテムが設定されています.prize=%d' % master.id)
        
        if master.additional_ticket_id and master.additional_ticket_num:
            if not Defines.GachaConsumeType.GachaTicketType.NAMES.has_key(master.additional_ticket_id):
                raise ModelEditValidError(u'未実装の新規追加ガチャチケットが設定されています.prize=%d' % master.id)

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
