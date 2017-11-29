# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.models.Card import DefaultCardMaster, CardMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = DefaultCardMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        leader = AppModelChoiceField(CardMaster, required=False, label=u'リーダー')
    
    def setting_property(self):
        self.MODEL_LABEL = u'ユーザー登録時に持っているカード'
    
    def valid_write_end(self):
        master_all = {}
        for master in DefaultCardMaster.fetchValues(filters={'ctype__in':Defines.CharacterType.NAMES.keys()}):
            master_all[master.ctype] = master
        
        card_all = {}
        for card in CardMaster.fetchValues():
            card_all[card.id] = card
        
        errors = []
        for ctype, name in Defines.CharacterType.NAMES.items():
            master = master_all.get(ctype)
            if master is None:
                continue
            if card_all.get(master.leader) is None:
                errors.append(u'タイプ:%sの初期リーダーカードが存在しません' % name)
            for mid in master.members:
                if card_all.get(mid) is None:
                    errors.append(u'タイプ:%sの初期デッキに存在しないカードが含まれています' % name)
            for mid in master.box:
                if card_all.get(mid) is None:
                    errors.append(u'タイプ:%sの初期BOXカードに存在しないカードが含まれています' % name)
        if errors:
            raise ModelEditValidError('<br />'.join(errors))

def main(request):
    return Handler.run(request)
