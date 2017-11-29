# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError, AppModelChoiceField
from defines import Defines
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.models.Gacha import RankingGachaMaster,\
    GachaBoxMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = RankingGachaMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        id = AppModelChoiceField(GachaBoxMaster, required=False, label=u'ID(BoxID)')
        singleprize_text = AppModelChoiceField(TextMaster, required=False, label=u'単発ランキング報酬文言')
        totalprize_text = AppModelChoiceField(TextMaster, required=False, label=u'累計ランキング報酬文言')
        totalprize_text = AppModelChoiceField(TextMaster, required=False, label=u'累計ランキング報酬文言')
        totalprize_text = AppModelChoiceField(TextMaster, required=False, label=u'累計ランキング報酬文言')
        wholeprize_text = AppModelChoiceField(TextMaster, required=False, label=u'総計pt報酬文言')
        wholewinprize_text = AppModelChoiceField(TextMaster, required=False, label=u'総計pt勝利報酬文言')
    
    def setting_property(self):
        self.MODEL_LABEL = u'ランキングガチャ'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        # ボックスの存在確認.
        boxmaster = GachaBoxMaster.getByKey(master.id)
        if boxmaster is None:
            raise ModelEditValidError(u'ランキング対象のBOXが見つかりません.master=%d' % master.id)
        
        # 報酬確認.
        def checkRankingPrize(prizes, name):
            if not isinstance(prizes, list):
                raise ModelEditValidError(u'%sのJsonが壊れています.rankinggacha=%d' % (name, master.id))
            for data in prizes:
                diff = set(['prize','rank_min','rank_max']) - set(data.keys())
                if diff:
                    raise ModelEditValidError(u'%s報酬に想定外のデータが含まれています.rankinggacha=%d' % (name, master.id))
                self.checkPrize(master, data['prize'], name, u'rankinggacha')
        checkRankingPrize(master.singleprizes, u'単発ランキング報酬')
        checkRankingPrize(master.totalprizes, u'累計ランキング報酬')
        
        if master.wholeprizes:
            for prizeidlist in master.get_wholeprizes().values():
                self.checkPrize(master, prizeidlist, u'総計Pt達成報酬', u'rankinggacha')
        if master.wholewinprizes:
            self.checkPrize(master, master.wholewinprizes, u'総計Pt勝利報酬', u'rankinggacha')
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
