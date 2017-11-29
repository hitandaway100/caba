# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from platinumegg.app.cabaret.models.PlayerLevelExp import PlayerLevelExpMaster
from defines import Defines


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = PlayerLevelExpMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'プレイヤー経験値テーブル'
    
    def valid_write_end(self):
        master_all = {}
        for master in PlayerLevelExpMaster.fetchValues():
            master_all[master.level] = master
        
        errors = []
        for master in master_all.values():
            if master.level == 1:
                if master.exp != 0:
                    errors.append(u'レベル1は経験値を0に設定してください, level=%d' % master.level)
                continue
            pre = master_all.get(master.level - 1)
            if pre is None:
                errors.append(u'レベルが抜けています, level=%d' % (master.level - 1))
            elif master.exp <= pre.exp:
                errors.append(u'前のレベルの経験値よりも大きくありません, level=%d' % master.level)
        if errors:
            raise ModelEditValidError('<br />'.join(errors))

def main(request):
    return Handler.run(request)
