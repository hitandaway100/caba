# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError, AppModelChoiceField
from platinumegg.app.cabaret.models.Treasure import TreasureTableBronzeMaster, TreasureBronzeMaster
from defines import Defines
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = TreasureTableBronzeMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        schedule = AppModelChoiceField(ScheduleMaster, required=False, label=u'期間')
    
    def setting_property(self):
        self.MODEL_LABEL = u'宝箱テーブル(銅)'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        if not master.table:
            raise ModelEditValidError(u'テーブルが設定されていません:id=%d' % master.id)
        elif type(master.table) is not list:
            raise ModelEditValidError(u'テーブルはリスト形式で設定してください:id=%d' % master.id)
        elif len(master.table) != len(list(set(master.table))):
            raise ModelEditValidError(u'テーブルの内容が重複しています:id=%d' % master.id)
        
        model_mgr = self.getModelMgr()
        arr = model_mgr.get_models(TreasureBronzeMaster, master.table)
        if len(arr) != len(master.table):
            raise ModelEditValidError(u'存在しないまたは非公開の宝箱が設定されています:id=%d' % master.id)
        
        probability_total = 0
        for treasure in arr:
            probability_total += treasure.probability
        if probability_total == 0:
            raise ModelEditValidError(u'テーブルの宝箱の出現率が全て0です:id=%d' % master.id)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)
    
    def valid_delete(self, master):
        pass

def main(request):
    return Handler.run(request)
