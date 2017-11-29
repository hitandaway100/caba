# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.models.CabaretClub import CabaClubMaster
from django import forms


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = CabaClubMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'cr_correction',
                'ctype_customer_correction',
                'ctype_proceeds_correction',
            )
        for attr, label in (('cr_correction', u'レアリティ補正'),):
            for rare in Defines.Rarity.LIST:
                exec u"{attr}_{name} = forms.IntegerField(label=u'{label}({name})', min_value=0)".format(attr=attr, label=label, name=Defines.Rarity.NAMES[rare].lower())
        for attr, label in (('ctype_customer_correction', u'属性集客補正'), ('ctype_proceeds_correction', u'属性売上補正')):
            for ctype in Defines.CharacterType.LIST:
                exec u"{attr}_{ctype} = forms.IntegerField(label=u'{label}({name})', min_value=0)".format(attr=attr, label=label, ctype=ctype, name=Defines.CharacterType.NAMES[ctype])
    
    def setting_property(self):
        self.MODEL_LABEL = u'キャバクラシステム'
    
    def __valid_master(self, master):
        # 報酬.
        if not isinstance(master.customer_prizes, list):
            raise ModelEditValidError(u'集客数達成報酬のJsonが壊れています.id=%d' % master.id)
        prizeidlist = []
        for arr in master.customer_prizes:
            if len(arr) != 2:
                raise ModelEditValidError(u'集客数達成報酬の中身が不正です.報酬IDと確率のペアで設定して下さい.id=%d' % master.id)
            prizeid, rate = arr
            prizeidlist.append(prizeid)
            if not isinstance(rate, (int, long)) or rate < 1:
                raise ModelEditValidError(u'集客数達成報酬の確率が不正です.id=%d' % master.id)
        self.checkPrize(master, prizeidlist, u'集客数達成報酬')
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
