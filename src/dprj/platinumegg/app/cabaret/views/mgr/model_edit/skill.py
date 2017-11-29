# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from platinumegg.app.cabaret.models.Skill import SkillMaster
from defines import Defines


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = SkillMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'サービス(スキル)'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        flag_end = False
        for number in xrange(1, SkillMaster.MULTI_SKILL_NUM_MAX):
            skilldata = master.get_skill(number)
            if skilldata is None:
                flag_end = True
            elif flag_end:
                raise ModelEditValidError(u'効果対象は左詰めで設定して下さい.skill=%d' % master.id)
        
        skilldata = master.get_skill(0)
        if skilldata is None:
            raise ModelEditValidError(u'効果対象は最低一つ設定して下さい.skill=%d' % master.id)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
