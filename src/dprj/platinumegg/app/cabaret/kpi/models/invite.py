# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.kpi.models.base import DailyHashKpiModel

class InviteCount(DailyHashKpiModel):
    """日別招待数.
    """
    class TARGET:
        SEND = 'send'
        SUCCESS = 'suc'
        TUTOEND = 'tutoend'
    
    def __init__(self, date, target, cnt=None):
        DailyHashKpiModel.__init__(self, date)
        self.target = target
        self.cnt = cnt
