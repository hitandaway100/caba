# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusSugorokuMapMaster,\
    LoginBonusSugorokuMapSquaresMaster
from platinumegg.app.cabaret.models.Present import PrizeMaster
from django.core.exceptions import ValidationError


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = LoginBonusSugorokuMapSquaresMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'id',
            )
        def _valid_primary_key(self):
            mid = int(self.cleaned_data.get('mid'))
            number = int(self.cleaned_data.get('number'))
            if number <= 0:
                raise ValidationError(u'numberは1以上を指定して下さい')
            elif mid <= 0:
                raise ValidationError(u'midは1以上を指定して下さい')
            return LoginBonusSugorokuMapSquaresMaster.makeID(mid, number)
    
    def setting_property(self):
        self.MODEL_LABEL = u'双六ログインボーナスのマス'
    
    def __valid_master(self, master):
        if master.number < 1:
            raise ModelEditValidError(u'マップ番号は1以上で設定して下さい.マップ={},マス={}'.format(master.mid, master.number))
        model_mgr = self.getModelMgr()
        mapmaster = model_mgr.get_model(LoginBonusSugorokuMapMaster, master.mid)
        if mapmaster is None:
            raise ModelEditValidError(u'存在しないマップが設定されています.マップ={},マス={}'.format(master.mid, master.number))
        
        master.id = LoginBonusSugorokuMapSquaresMaster.makeID(master.mid, master.number)
        if not master.is_public:
            return
        prizelist = model_mgr.get_models(PrizeMaster, master.prize)
        if len(prizelist) != len(master.prize):
            raise ModelEditValidError(u'存在しない報酬が設定されています.マップ={},マス={}'.format(master.mid, master.number))
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)
    
    def valid_write_end(self):
        errors = []
        
        model_cls = self.Form.Meta.model
        master_all = model_cls.fetchValues()
        master_all.sort(key=lambda x:((x.mid<<32)+x.number))
        
        mid = None
        number = 0
        for master in master_all:
            if mid != master.mid:
                mid = master.mid
                number = 0
            if number == master.number:
                errors.append(u'重複:マップ={},マス={}'.format(master.mid, master.number))
            elif number != (master.number - 1):
                for n in xrange(number+1, master.stage):
                    errors.append(u'不足:マップ={},マス={}'.format(master.mid, n))
            number = master.number
        if errors:
            raise ModelEditValidError('<br />'.join(errors))

def main(request):
    return Handler.run(request)
