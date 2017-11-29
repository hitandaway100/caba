# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.models.Scenario import ScenarioMaster


class Handler(AdminModelEditHandler):
    """シナリオ.
    """
    class Form(AppModelForm):
        class Meta:
            model = ScenarioMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'シナリオ'
        self.__wrote_numbers = []

    def valid_write_end(self):
        """書き込み後チェック.
        エラーの時はModelEditValidError.
        """
        for number in self.__wrote_numbers:
            thumb = None
            modellist = ScenarioMaster.fetchValues(['thumb'], dict(number=number))
            for model in modellist:
                if not model.thumb:
                    continue
                elif thumb and thumb != model.thumb:
                    raise ModelEditValidError(u'シナリオの演出画像の場所が一定になっていません.number={}'.format(number))
                thumb = model.thumb
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        if not master.bg:
            raise ModelEditValidError(u'背景画像が設定されていません.id=%d' % master.id)
        
        if not master.number in self.__wrote_numbers:
            self.__wrote_numbers.append(master.number)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
