# -*- coding: utf-8 -*-


class BattleEventGroupUserData():
    """グループのユーザ情報.
    獲得ポイント,連勝数,名声ポイント,ランク変化
    """
    
    def __init__(self):
        self.uid = None
        self.point = 0
        self.win = 0
        self.fame = 0
        self.rankup = 0
        self.grouprank = 0
    
    @staticmethod
    def createByScoreRecord(scorerecord, grouprank=0, now=None):
        userdata = BattleEventGroupUserData()
        userdata.uid = scorerecord.uid
        userdata.point = scorerecord.getPointToday(now)
        userdata.win = scorerecord.getWinMaxToday(now)
        userdata.grouprank = grouprank
        return userdata
