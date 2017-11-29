# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from platinumegg.app.cabaret.models.Gacha import GachaSeatMaster
from defines import Defines
from platinumegg.app.cabaret.models.Present import PrizeMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = GachaSeatMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'premium',
            )
#        textid = AppModelChoiceField(TextMaster, required=False, label=u'報酬文言')
#        prize_0 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID0')
#        prize_1 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID1')
#        prize_2 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID2')
#        prize_3 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID3')
#        prize_4 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID4')
#        prize_5 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID5')
#        prize_6 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID6')
#        prize_7 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID7')
#        prize_8 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID8')
#        prize_9 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID9')
#        prize_10 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID10')
#        prize_11 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID11')
#        prize_12 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID12')
#        prize_13 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID13')
#        prize_14 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID14')
#        prize_15 = AppModelChoiceField(PrizeMaster, required=False, label=u'報酬ID15')
    
    def setting_property(self):
        self.MODEL_LABEL = u'引き抜きシート'
        self.valid_error_num = 0
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        idx = 0
        prizeidlist = []
        while True:
            prizeid = master.getPrizeId(idx)
            idx += 1
            
            if prizeid is None:
                break
            
            weight = master.getWeight(idx)
            if not prizeid or not weight:
                continue
            prizeidlist.append(prizeid)
            
        if not prizeidlist:
            raise ModelEditValidError(u'報酬が設定されていません.seat=%d' % master.id)
        prizeidlist = list(set(prizeidlist))
        
        prizelist = PrizeMaster.getByKey(prizeidlist)
        if len(prizeidlist) != len(prizelist):
            raise ModelEditValidError(u'存在しない報酬が設定されています.seat=%d' % master.id)

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
