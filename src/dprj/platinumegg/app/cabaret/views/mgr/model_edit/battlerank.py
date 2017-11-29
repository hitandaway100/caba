# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from defines import Defines
from platinumegg.app.cabaret.models.Battle import BattleRankMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = BattleRankMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
    
    def setting_property(self):
        self.MODEL_LABEL = u'ランク'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        def checkprize(clumnprizes):
            datalist = []
            try:
                for v in clumnprizes:
                    data = BattleRankMaster.PrizeData(v)
                    if 0 < data.rate:
                        datalist.append(data)
                    self.checkPrize(master, data.prizes)
                if len(datalist) == 0:
                    raise ModelEditValidError(u'報酬が設定されていません.id=%d' % master.id)
            except ModelEditValidError:
                raise
            except:
                raise ModelEditValidError(u'報酬データに問題があります.id=%d' % master.id)
        checkprize(master.winprizes)
        checkprize(master.loseprizes)
        checkprize(master.rankupprizes)
        
        if master.win < 1:
            raise ModelEditValidError(u'連勝数が設定されていません.id=%d' % master.id)
        elif master.times < 1:
            raise ModelEditValidError(u'達成回数が設定されていません.id=%d' % master.id)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)
    
    def valid_write_end(self):
        model_all = {}
        for model in BattleRankMaster.fetchValues():
            model_all[model.id] = model
        
        errors = []
        if not model_all.has_key(1):
            errors.append(u'ランクが設定されていません, id=1')
        
        for model in model_all.values():
            if 1 < model.id and model_all.get(model.id - 1) is None:
                errors.append(u'ランクが設定されていません, id=%d' % (model.id - 1))
        if errors:
            raise ModelEditValidError('<br />'.join(errors))

def main(request):
    return Handler.run(request)
