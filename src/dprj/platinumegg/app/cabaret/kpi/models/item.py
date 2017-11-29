# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.kpi.models.base import KpiModel

class ItemDistributionAmount(KpiModel):
    """アイテムの流通量.
    """
    
    @classmethod
    def makeKey(cls, mid, kind):
        return '%s_%s##%s' % (cls.__name__, kind, mid)
    
    def __init__(self, uid, mid, rnum, vnum):
        self.uid = uid
        self.mid = mid
        self.rnum = rnum
        self.vnum = vnum
    
    def _save(self, pipe):
        pipe.zadd(self.__class__.makeKey(self.mid, 'rnum'), self.uid, self.rnum)
        pipe.zadd(self.__class__.makeKey(self.mid, 'vnum'), self.uid, self.vnum)
    
    def _delete(self, pipe):
        pipe.zrem(self.__class__.makeKey(self.mid, 'rnum'), self.uid)
        pipe.zrem(self.__class__.makeKey(self.mid, 'vnum'), self.uid)
    
    @classmethod
    def aggregateByMasterId(cls, mid):
        """集計.
        """
        redisdb = cls.getDB()
        
        def getTotal(key):
            total = 0
            
            arr = redisdb.zrevrange(key, 0, 0, withscores=True, score_cast_func=long)
            if not arr:
                return total
            
            _, score = arr[0]
            while True:
                num = redisdb.zcount(key, score, score)
                total += int(score) * int(num)
                
                arr = redisdb.zrevrangebyscore(key, score - 1, 0, start=0, num=1, withscores=True, score_cast_func=long)
                if not arr:
                    break
                _, score = arr[0]
            return total
        
        vnum = getTotal(cls.makeKey(mid, 'vnum'))
        rnum = getTotal(cls.makeKey(mid, 'rnum'))
        
        return mid, vnum, rnum
