# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.kpi.models.battleevent import BattleEventResult
from platinumegg.app.cabaret.kpi.csv.battleevent import BattleEventCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(BattleEventCSVBase):
    """バトルイベント結果.
    """
    def __init__(self, date, output_dir):
        BattleEventCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        idmax = Player.max_value('id', using=backup_db)
        if not idmax:
            return []
        
        str_date = self.date.strftime("%Y/%m/%d")
        
        LIMIT = 500
        datalist = []
        uid = 1
        while uid <= idmax:
            range_max = min(idmax + 1, uid+LIMIT)
            uidlist = range(uid, range_max)
            modellist = BattleEventResult.fetch(self.date, uidlist)
            for model in modellist:
                datalist.append((str_date, model.rank, model.uid, model.grouprank, model.point))
            uid += LIMIT
        return datalist
    
    def delete(self):
        BattleEventResult.delete(self.date)
