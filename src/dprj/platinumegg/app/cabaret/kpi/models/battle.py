# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.kpi.models.base import DailyHashKpiModel

class BattleRankupCount(DailyHashKpiModel):
    """日別ランク別ランクアップ者数.
    """
    
    def __init__(self, date, rank, score=None):
        DailyHashKpiModel.__init__(self, date)
        self.rank = rank
        self.score = score

class BattleRankPlayCount(DailyHashKpiModel):
    """日別ランク別プレイ回数.
    """
    
    def __init__(self, date, rank, score=None):
        DailyHashKpiModel.__init__(self, date)
        self.rank = rank
        self.score = score
