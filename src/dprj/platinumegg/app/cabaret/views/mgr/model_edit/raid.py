# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Happening import RaidMaster
import settings
from platinumegg.app.cabaret.models.Present import PrizeMaster
from platinumegg.app.cabaret.util.apprandom import AppRandom


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = RaidMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'レイドボス'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        model_mgr = self.getModelMgr()
        
        prizes = master.prizes
        if len(prizes) != len(list(set(prizes))):
            raise ModelEditValidError(u'報酬が重複しています.raid=%d' % master.id)
        prizelist = BackendApi.get_prizemaster_list(model_mgr, prizes)
        if len(prizes) != len(prizelist):
            raise ModelEditValidError(u'存在しない報酬が設定されています.raid=%d' % master.id)

        total_rate = sum([item['rate'] for item in master.items])
        if total_rate <= 0 and AppRandom.RAND_MAX <= total_rate:
            raise ModelEditValidError(u'確率が異常値です.raid={}'.format(master.id))
        prize_ids = [item['id'] for item in master.items]
        prizelist = model_mgr.get_models(PrizeMaster, prize_ids)
        if len(prize_ids) != len(prizelist):
            raise ModelEditValidError(u'存在しない報酬が設定されています.raid={}'.format(master.id))

        
        # 弱点属性をチェック.
        try:
            weakbonus = dict(master.weakbonus)
        except:
            raise ModelEditValidError(u'弱点属性の設定が不正です.raid=%d' % master.id)
        
        for k,v in weakbonus.items():
            if not k in Defines.CharacterType.LIST:
                raise ModelEditValidError(u'弱点属性に存在しない属性が設定されています.raid=%d' % master.id)
            elif not isinstance(v, (int, long)):
                raise ModelEditValidError(u'弱点属性の倍率は整数で指定してください.raid=%d' % master.id)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
