# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.kpi.models.base import DailyHashKpiModel

class ScoutCompleteCount(DailyHashKpiModel):
    """日別スカウトクリア人数.
    """
    
    def __init__(self, date, scoutid, score=None):
        DailyHashKpiModel.__init__(self, date)
        self.scoutid = scoutid
        self.score = score
