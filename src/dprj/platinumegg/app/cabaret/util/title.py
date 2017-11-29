# -*- coding: utf-8 -*-
import datetime
from platinumegg.app.cabaret.models.Title import TitlePlayerData
from platinumegg.lib.opensocial.util import OSAUtil

class TitleSet:
    """称号.
    """
    def __init__(self, master, playerdata):
        self.__master = master
        self.__playerdata = playerdata or TitlePlayerData.makeInstance(0)
    
    @property
    def master(self):
        return self.__master
    @property
    def playerdata(self):
        return self.__playerdata
    
    def get_limit_time(self):
        """称号の有効期限.
        """
        return self.playerdata.stime + datetime.timedelta(days=self.master.days)
    
    def is_alive(self, now=None):
        """称号が有効か.
        """
        now = now or OSAUtil.get_now()
        return now < self.get_limit_time()
