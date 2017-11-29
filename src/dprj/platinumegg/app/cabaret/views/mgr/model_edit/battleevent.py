# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.Text import TextMaster
from defines import Defines
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventMaster
from platinumegg.app.cabaret.models.Card import CardMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = BattleEventMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        rankingprize_text = AppModelChoiceField(TextMaster, required=False, label=u'ランキング報酬文言')
        pointprize_text = AppModelChoiceField(TextMaster, required=False, label=u'名声ポイント報酬文言')
        beginer_rankingprize_text = AppModelChoiceField(TextMaster, required=False, label=u'初心者ランキング報酬文言')
    
    def setting_property(self):
        self.MODEL_LABEL = u'バトルイベント'
    
    def __valid_master(self, master):
        if not (1 <= master.id <= 0xffffff):
            raise ModelEditValidError(u'イベントのマスターIDが不正です.battleevent=%d' % master.id)
        
        if not master.is_public:
            return
        
        if not isinstance(master.rankingprizes, list):
            raise ModelEditValidError(u'ランキング報酬のJsonが壊れています.battleevent=%d' % master.id)
        for data in master.rankingprizes:
            diff = set(['prize','rank_min','rank_max']) - set(data.keys())
            if diff:
                raise ModelEditValidError(u'ランキング報酬に想定外のデータが含まれています.battleevent=%d' % master.id)
            self.checkPrize(master, data['prize'], u'ランキング報酬', 'battleevent')
        
        master.beginer_rankingprizes = master.beginer_rankingprizes or []
        if not isinstance(master.beginer_rankingprizes, list):
            raise ModelEditValidError(u'新店舗ランキング報酬のJsonが壊れています.battleevent=%d' % master.id)
        for data in master.beginer_rankingprizes:
            diff = set(['prize','rank_min','rank_max']) - set(data.keys())
            if diff:
                raise ModelEditValidError(u'新店舗ランキング報酬に想定外のデータが含まれています.battleevent=%d' % master.id)
            self.checkPrize(master, data['prize'], u'新店舗ランキング報酬', 'battleevent')
        
        if not isinstance(master.pointprizes, (dict, list)):
            raise ModelEditValidError(u'名声ポイント達成報酬のJsonが壊れています.battleevent=%d' % master.id)
        for prizeidlist in master.get_pointprizes().values():
            self.checkPrize(master, prizeidlist, u'名声ポイント達成報酬', 'battleevent')
        
        try:
            specialtable = dict(master.specialtable)
        except:
            raise ModelEditValidError(u'特効倍率テーブルが壊れています.battleevent=%d' % master.id)
        diff = set(specialtable.keys()) - set(Defines.Rarity.NAMES.keys())
        if diff:
            raise ModelEditValidError(u'特効倍率テーブルに存在しないレア度が含まれています.battleevent=%d' % master.id)
        
        for arr in specialtable.values():
            if not isinstance(arr, list):
                raise ModelEditValidError(u'特効倍率テーブルが壊れています.battleevent=%d' % master.id)
            
            for v in arr:
                if not isinstance(v, (int, long)):
                    raise ModelEditValidError(u'特効倍率テーブルが壊れています.battleevent=%d' % master.id)
        
        specialcard = dict(master.specialcard)
        midlist = specialcard.keys()
        if len(midlist) != len(master.specialcard):
            raise ModelEditValidError(u'特効キャストが重複しています.battleeventraid=%d' % master.id)
        elif len(CardMaster.getByKey(midlist)) != len(midlist):
            raise ModelEditValidError(u'存在しないキャストが特効に設定されています.battleeventraid=%d' % master.id)
        
        dest = []
        for mid, _ in master.specialcard:
            arr = specialcard.get(mid)
            if isinstance(arr, (int, long)):
                arr = [arr]
            
            if not isinstance(arr, list) or len(arr) < 1:
                raise ModelEditValidError(u'特効キャストテーブルが壊れています.battleevent=%d' % master.id)
            for v in arr:
                if not isinstance(v, (int, long)):
                    raise ModelEditValidError(u'特効キャストテーブルが壊れています.battleevent=%d' % master.id)
            dest.append([mid, arr])
        master.specialcard = dest
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
