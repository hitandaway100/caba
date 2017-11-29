# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.kpi.models.login import WeeklyLoginSet
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase

class Manager(KpiCSVBase):
    """プラットフォームごとのログイン数.
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        """プラットフォームごとのログイン数.
        """
        result = [[
            # SP版のみ.
            WeeklyLoginSet.countByPlatform(self.date, sp=True, pc=False),
            # PC版のみ.
            WeeklyLoginSet.countByPlatform(self.date, sp=False, pc=True),
            # 両方.
            WeeklyLoginSet.countByPlatform(self.date, sp=True, pc=True),
        ]]
        return result
