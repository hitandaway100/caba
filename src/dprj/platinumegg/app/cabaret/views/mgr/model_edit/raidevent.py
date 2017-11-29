# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError, AppModelChoiceField
from defines import Defines
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.util.scout import ScoutHappeningSelector


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = RaidEventMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        rankingprize_text = AppModelChoiceField(TextMaster, required=False, label=u'ランキング報酬文言')
        destroyprize_text = AppModelChoiceField(TextMaster, required=False, label=u'討伐回数報酬文言')
        joinprize_text = AppModelChoiceField(TextMaster, required=False, label=u'イベント開始報酬文言')
        beginer_rankingprize_text = AppModelChoiceField(TextMaster, required=False, label=u'初心者ランキング報酬文言')
    
    def setting_property(self):
        self.MODEL_LABEL = u'レイドイベント'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        def checkRaidTable(table, errmessage):
            try:
                ScoutHappeningSelector(None, None, table).validate()
            except:
                raise ModelEditValidError(errmessage)
        checkRaidTable(master.raidtable, u'レイド出現テーブルが正しくありません.%d' % master.id)
        checkRaidTable(master.raidtable_timebonus, u'タイムボーナスレイド出現テーブルが正しくありません.%d' % master.id)
        checkRaidTable(master.raidtable_big, u'大ボス出現後のレイド出現テーブルが正しくありません.%d' % master.id)
        checkRaidTable(master.raidtable_timebonus_big, u'大ボス出現後のタイムボーナスレイド出現テーブルが正しくありません.%d' % master.id)
        
        if not isinstance(master.rankingprizes, list):
            raise ModelEditValidError(u'ランキング報酬のJsonが壊れています.raidevent=%d' % master.id)
        for data in master.rankingprizes:
            diff = set(['prize','rank_min','rank_max']) - set(data.keys())
            if diff:
                raise ModelEditValidError(u'ランキング報酬に想定外のデータが含まれています.raidevent=%d' % master.id)
            self.checkPrize(master, data['prize'], u'ランキング報酬', u'raidevent')
        
        master.beginer_rankingprizes = master.beginer_rankingprizes or []
        if not isinstance(master.beginer_rankingprizes, list):
            raise ModelEditValidError(u'初心者ランキング報酬のJsonが壊れています.raidevent=%d' % master.id)
        for data in master.beginer_rankingprizes:
            diff = set(['prize','rank_min','rank_max']) - set(data.keys())
            if diff:
                raise ModelEditValidError(u'初心者ランキング報酬に想定外のデータが含まれています.raidevent=%d' % master.id)
            self.checkPrize(master, data['prize'], u'初心者ランキング報酬', u'raidevent')
        
        if not isinstance(master.destroyprizes, (dict, list)):
            raise ModelEditValidError(u'討伐回数報酬のJsonが壊れています.raidevent=%d' % master.id)
        for prizeidlist in master.get_destroyprizes().values():
            self.checkPrize(master, prizeidlist, u'討伐回数報酬', u'raidevent')
        
        if not isinstance(master.destroyprizes_big, (dict, list)):
            raise ModelEditValidError(u'大ボス討伐回数報酬のJsonが壊れています.raidevent=%d' % master.id)
        for prizeidlist in master.get_destroyprizes_big().values():
            self.checkPrize(master, prizeidlist, u'大ボス討伐回数報酬', u'raidevent')
        
        if not isinstance(master.joinprizes, list):
            raise ModelEditValidError(u'イベント開始報酬のJsonが壊れています.raidevent=%d' % master.id)
        self.checkPrize(master, master.joinprizes, u'イベント開始報酬', u'raidevent')
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
