# -*- coding: utf-8 -*-
import random

class AppRandom:
    """ｱﾌﾟﾘ用乱数クラス.
    """
    RAND_MAX = 0xffff
    
    def __init__(self, seed = None):
        self._mulValue = int(69069)
        self._addValue = int(1)
        if seed != None:
            self.setSeed(int(seed))
        else:
            self.setSeed(AppRandom.makeSeed())
    
    def setSeed(self, value):
        value = value * self._mulValue % 0xffffffff
        self._seed = int(value)
        
    def getInt(self):
        self._seed = int(self._seed * self._mulValue + self._addValue) & 0x7fffffff
        ret = int(self._seed >> 16)
        return ret
    
    def getIntN(self, num):
        if 0 == num:
            return 0
        ret = self.getInt() % num
        return int(ret)
    
    def getIntS(self, vmin, vmax):
        size = vmax - vmin + 1
        return int(vmin + self.getIntN(size))
    
    @staticmethod
    def makeSeed():
        return int(random.random() * 65535)
