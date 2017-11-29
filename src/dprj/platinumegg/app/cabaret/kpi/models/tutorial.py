# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.kpi.models.base import DailySortedSetKpiModel

class TutorialQuit(DailySortedSetKpiModel):
    """各チュートリアルステップの人数の集計.
    """
    
    def __init__(self, date, uid, tutorialstate):
        DailySortedSetKpiModel.__init__(self, date)
        self.uid = uid
        self.tutorialstate = tutorialstate
    
    def _save(self, pipe):
        pipe.zadd(self.key, self.uid, self.tutorialstate)
    
    def _delete(self, pipe):
        pipe.zrem(self.key, self.uid)
    
