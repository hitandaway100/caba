# -*- coding: utf-8 -*-
import settings
from defines import Defines
from platinumegg.app.cabaret.kpi.models.tutorial import TutorialQuit
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(KpiCSVBase):
    """チュートリアル分布.
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        data = TutorialQuit.aggregate(self.date)
        if not data:
            return None
        statelist = list(Defines.TutorialStatus.NAMES.keys())
        statelist.sort()
        result = [(Defines.TutorialStatus.NAMES.get(state, state), data.get(state, 0)) for state in statelist]
        return result
    
    def delete(self):
        TutorialQuit.deleteByDate(self.date)
