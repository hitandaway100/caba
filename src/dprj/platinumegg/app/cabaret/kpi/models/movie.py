# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.kpi.models.base import DailyHashKpiModel

class MovieViewCount(DailyHashKpiModel):
    """動画ごとの再生数.
    """
    
    def __init__(self, date, mid, cnt):
        DailyHashKpiModel.__init__(self, date)
        self.mid = mid
        self.cnt = cnt
    
class PcMovieViewCount(DailyHashKpiModel):
    """動画(PC)ごとの再生数.
    """
    
    def __init__(self, date, mid, cnt):
        DailyHashKpiModel.__init__(self, date)
        self.mid = mid
        self.cnt = cnt
    
