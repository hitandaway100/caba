# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.modelgroup import ModelGroupBase
from platinumegg.app.cabaret.models.Player import Player, PlayerRegist,\
    PlayerTutorial, PlayerExp, PlayerGold, PlayerAp, PlayerDeck, PlayerFriend,\
    PlayerGachaPt, PlayerTreasure, PlayerScout, PlayerCard, PlayerLogin,\
    PlayerComment, PlayerKey, PlayerHappening, PlayerRequest, PlayerTradeShop
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.opensocial.util import OSAUtil
import datetime



class ModelPlayer(ModelGroupBase):
    """Player
    """
    class Meta:
        BASE_MODEL = Player
        MODELS = (
            PlayerRegist,
            PlayerTutorial,
            PlayerExp,
            PlayerGold,
            PlayerAp,
            PlayerDeck,
            PlayerFriend,
            PlayerGachaPt,
            PlayerTreasure,
            PlayerScout,
            PlayerCard,
            PlayerLogin,
            PlayerComment,
            PlayerHappening,
            PlayerKey,
            PlayerRequest,
            PlayerTradeShop,
        )
    def __init__(self, model_list=None):
        ModelGroupBase.__init__(self, model_list)
    
    def is_tutorialend(self):
        model = self.getModel(PlayerTutorial)
        if model and model.tutorialstate == Defines.TutorialStatus.COMPLETED:
            return True
        else:
            return False
    
    def __get_ap_max(self, ap_column_name):
        AP_MAX_CNAME = PlayerAp.AP_MAX_COLUMN_BASE % ap_column_name
        playerap = self.getModel(PlayerAp)
        
        if ap_column_name == PlayerAp.BP_COLUMN_NAME:
            # これはそのまま.
            return getattr(playerap, AP_MAX_CNAME)
        playerfriend = self.getModel(PlayerFriend)
        if playerap is None or playerfriend is None:
            raise CabaretError(u'行動力を操作するときはPlayerApとPlayerFriendをロードしてください.')
        return getattr(playerap, AP_MAX_CNAME) + playerfriend.friendnum
    
    def __reflect_ap_base(self, ap_column_name):
        """行動力を反映.
        時間と共に増えてゆく.
        """
        playerap = self.getModel(PlayerAp)
        if playerap is None:
            raise CabaretError(u'行動力を操作するときはPlayerApとPlayerFriendをロードしてください.')
        
        AP_CNAME = ap_column_name
        AP_TIME_CNAME = PlayerAp.AP_TIME_COLUMN_BASE % ap_column_name
        AP_RECOVE_TIME = PlayerAp.AP_RECOVE_TIME_TABLE.get(AP_CNAME, None)
        if AP_RECOVE_TIME is None:
            raise CabaretError(u'undfined AP_RECOVE_TIME:%s' % AP_CNAME)
        
        now = OSAUtil.get_now()
        ap = getattr(playerap, AP_CNAME)
        ap_time = getattr(playerap, AP_TIME_CNAME)
        ap_max = self.__get_ap_max(ap_column_name)
        
        delta = now - ap_time
        diff_sec = delta.days * 86400 + delta.seconds
        reduce_v = diff_sec / AP_RECOVE_TIME # 増やす量.
        
        wrote_ap = min(ap_max, max(0, ap + reduce_v))
        setattr(playerap, AP_CNAME, wrote_ap)
        reduce_real = wrote_ap - ap # 実際に増えた量.
        
        if wrote_ap == ap_max:
            setattr(playerap, AP_TIME_CNAME, now)
        else:
            add_sec = AP_RECOVE_TIME * reduce_real
            setattr(playerap, AP_TIME_CNAME, ap_time + datetime.timedelta(seconds=add_sec))
    
    def __add_ap_base(self, ap_column_name, add_num):
        """行動力を追加.
        """
        ap = self._get_ap_base(ap_column_name)
        return self._set_ap_base(ap_column_name, ap + add_num)
    
    def _set_ap_base(self, ap_column_name, set_num):
        """行動力を設定.
        """
        self.__reflect_ap_base(ap_column_name)
        
        AP_CNAME = ap_column_name
        AP_TIME_CNAME = PlayerAp.AP_TIME_COLUMN_BASE % ap_column_name
        
        ap_max = self.__get_ap_max(ap_column_name)
        
        setattr(self, AP_CNAME, max(0, min(ap_max, set_num)))
        return [AP_CNAME, AP_TIME_CNAME]
    
    def _get_ap_timediff(self, ap_column_name, now=None):
        now = now or OSAUtil.get_now()
        
        AP_TIME_CNAME = PlayerAp.AP_TIME_COLUMN_BASE % ap_column_name
        ap = self._get_ap_base(ap_column_name)
        ap_max = self.__get_ap_max(ap_column_name)
        if ap_max <= ap:
            return 0
        else:
            AP_RECOVE_TIME = PlayerAp.AP_RECOVE_TIME_TABLE.get(ap_column_name, 0)
            ap_time = getattr(self, AP_TIME_CNAME)
            maxtime = ap_time + datetime.timedelta(seconds=AP_RECOVE_TIME * (ap_max - ap))
            td = maxtime - now
            return td.days * 86400 + td.seconds
    
    def _get_ap_base(self, ap_column_name):
        self.__reflect_ap_base(ap_column_name)
        return getattr(self, ap_column_name)
    
    def add_ap(self, add_num):
        return self.__add_ap_base(PlayerAp.AP_COLUMN_NAME, add_num)
    def set_ap(self, set_num):
        return self._set_ap_base(PlayerAp.AP_COLUMN_NAME, set_num)
    def get_ap(self):
        return self._get_ap_base(PlayerAp.AP_COLUMN_NAME)
    def get_ap_max(self):
        return self.__get_ap_max(PlayerAp.AP_COLUMN_NAME)
    def get_ap_timediff(self, now=None):
        return self._get_ap_timediff(PlayerAp.AP_COLUMN_NAME, now)
    def add_bp(self, add_num):
        return self.__add_ap_base(PlayerAp.BP_COLUMN_NAME, add_num)
    def set_bp(self, set_num):
        return self._set_ap_base(PlayerAp.BP_COLUMN_NAME, set_num)
    def get_bp(self):
        return self._get_ap_base(PlayerAp.BP_COLUMN_NAME)
    def get_bp_max(self):
        return self.__get_ap_max(PlayerAp.BP_COLUMN_NAME)
    def get_bp_timediff(self, now=None):
        return self._get_ap_timediff(PlayerAp.BP_COLUMN_NAME, now)
    @property
    def bpmax(self):
        playerap = self.getModel(PlayerAp)
        return playerap.bpmax
    
    @property
    def deckcapacity(self):
        return self.getModel(PlayerDeck).deckcapacity
    @property
    def cardlimit(self):
        return self.getModel(PlayerDeck).cardlimit
    
    def is_beginer(self, now=None):
        """初心者か.
        """
        now = now or OSAUtil.get_now()
        chacktime = self.etime + Defines.BEGINER_TIME
        if now <= chacktime:
            return True
    
    def get_cabaretking_num(self):
        return self.getModel(PlayerTreasure).get_cabaretking_num()
