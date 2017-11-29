# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.models.PlayerLog import PlayerLog
from defines import Defines
from platinumegg.app.cabaret.models.Area import AreaMaster
from platinumegg.lib.platform.api.objects import PeopleRequestData
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.lib.platform.api.request import ApiNames
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Scout import ScoutMaster
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventStageMaster
from platinumegg.app.cabaret.util.redisdb import FriendLogList
from platinumegg.app.cabaret.models.raidevent.RaidEventScout import RaidEventScoutStageMaster


class BaseGameLog(object):
    """ゲームログ.
    """
    def __init__(self, log_data=None):
        if log_data:
            self.id = getattr(log_data, 'id', 0)
            self.uid = log_data.uid
            self.logtype = log_data.logtype
            self.data = log_data.data
            self.ctime = log_data.ctime
        else:
            self.id = 0
            self.uid = 0
            self.logtype = 0
            self.data = {}
            self.ctime = OSAUtil.get_now()
        self.params = {}
        self.__db_data = log_data
    
    def getOption(self, key, default=None):
        return (self.__db_data.data or {}).get(key, default)
    
    @classmethod
    def makeData(cls, *args, **kwgs):
        """GameLogDataインスタンスを返す.
        """
        raise NotImplementedError
    
    def load_params(self, apphandler):
        """表示用に必要な情報をロード.
        """
        raise NotImplementedError
    
    def makeApiRequest(self, apphandler):
        """表示用に必要な情報をロード.
        """
        return None
    
    def apirequestCB(self, ret_data, reqkey, *args, **kwargs):
        """Apiリクエストのコールバック.
        """
        pass
    
    def makePersonApiRequest(self, apphandler, uid):
        """表示用に必要な情報をロード.
        """
        model_mgr = apphandler.getModelMgr()
        player = model_mgr.get_model(Player, uid, using=settings.DB_READONLY)
        if player is None:
            return None
        data = PeopleRequestData.createForPeople(player.dmmid)
        request = apphandler.osa_util.makeApiRequest(ApiNames.People, data)
        return request
    
    def load(self, apphandler):
        """表示用に必要な情報をロード.
        """
        # DBから引いてきたりする.
        self.load_params(apphandler)
        
        # Personとか欲しいはず.
        requests = self.makeApiRequest(apphandler)
        if requests:
            for key, request in requests.items():
                apphandler.addAppApiRequest(key, request, self.apirequestCB, reqkey=key)
    
#=================================================
# player.
class BattleReceiveWinLog(BaseGameLog):
    """バトルで挑まれて勝った.
    """
    def __init__(self, *args, **kwgs):
        BaseGameLog.__init__(self, *args, **kwgs)
    
    @staticmethod
    def makeData(uid, oid):
        log_data = PlayerLog(uid=uid, logtype=Defines.PlayerLogType.BATTLE_RECEIVE_WIN)
        log_data.data = {'oid':oid}
        return log_data
    
    def load_params(self, apphandler):
        self.params['url'] = apphandler.makeAppLinkUrl(UrlMaker.profile(self.getOption('oid', '')))
    
    def makeApiRequest(self, apphandler):
        """表示用に必要な情報をロード.
        """
        return {
            'BattleReceiveWinLog:%s:oid' % (self.id) : self.makePersonApiRequest(apphandler, self.getOption('oid', ''))
        }
    
    def apirequestCB(self, ret_data, reqkey, *args, **kwargs):
        """Apiリクエストのコールバック.
        """
        try:
            person = ret_data[reqkey].get()
            self.params['dmmid'] = person.id
            self.params['username'] = person.nickname
        except:
            self.params['dmmid'] = ''
            self.params['username'] = u'****'

class BattleReceiveLoseLog(BaseGameLog):
    """バトルで挑まれて負けた.
    """
    def __init__(self, *args, **kwgs):
        BaseGameLog.__init__(self, *args, **kwgs)
    
    @staticmethod
    def makeData(uid, oid):
        log_data = PlayerLog(uid=uid, logtype=Defines.PlayerLogType.BATTLE_RECEIVE_LOSE)
        log_data.data = {'oid':oid}
        return log_data
    
    def load_params(self, apphandler):
        self.params['url'] = apphandler.makeAppLinkUrl(UrlMaker.profile(self.getOption('oid', '')))
    
    def makeApiRequest(self, apphandler):
        """表示用に必要な情報をロード.
        """
        return {
            'BattleReceiveLoseLog:%s:oid' % (self.id) : self.makePersonApiRequest(apphandler, self.getOption('oid', ''))
        }
    
    def apirequestCB(self, ret_data, reqkey, *args, **kwargs):
        """Apiリクエストのコールバック.
        """
        try:
            person = ret_data[reqkey].get()
            self.params['dmmid'] = person.id
            self.params['username'] = person.nickname
        except:
            self.params['dmmid'] = ''
            self.params['username'] = u'****'

class BattleWinLog(BaseGameLog):
    """バトルを挑んで勝った.
    """
    def __init__(self, *args, **kwgs):
        BaseGameLog.__init__(self, *args, **kwgs)
    
    @staticmethod
    def makeData(uid, oid):
        log_data = PlayerLog(uid=uid, logtype=Defines.PlayerLogType.BATTLE_WIN)
        log_data.data = {'oid':oid}
        return log_data
    
    def load_params(self, apphandler):
        self.params['url'] = apphandler.makeAppLinkUrl(UrlMaker.profile(self.getOption('oid', '')))
    
    def makeApiRequest(self, apphandler):
        """表示用に必要な情報をロード.
        """
        return {
            'BattleWinLog:%s:oid' % (self.id) : self.makePersonApiRequest(apphandler, self.getOption('oid', ''))
        }
    
    def apirequestCB(self, ret_data, reqkey, *args, **kwargs):
        """Apiリクエストのコールバック.
        """
        try:
            person = ret_data[reqkey].get()
            self.params['dmmid'] = person.id
            self.params['username'] = person.nickname
        except:
            self.params['dmmid'] = ''
            self.params['username'] = u'****'

class BattleLoseLog(BaseGameLog):
    """バトルを挑んで負けた.
    """
    def __init__(self, *args, **kwgs):
        BaseGameLog.__init__(self, *args, **kwgs)
    
    @staticmethod
    def makeData(uid, oid):
        log_data = PlayerLog(uid=uid, logtype=Defines.PlayerLogType.BATTLE_LOSE)
        log_data.data = {'oid':oid}
        return log_data
    
    def load_params(self, apphandler):
        self.params['url'] = apphandler.makeAppLinkUrl(UrlMaker.profile(self.getOption('oid', '')))
    
    def makeApiRequest(self, apphandler):
        """表示用に必要な情報をロード.
        """
        return {
            'BattleLoseLog:%s:oid' % (self.id) : self.makePersonApiRequest(apphandler, self.getOption('oid', ''))
        }
    
    def apirequestCB(self, ret_data, reqkey, *args, **kwargs):
        """Apiリクエストのコールバック.
        """
        try:
            person = ret_data[reqkey].get()
            self.params['dmmid'] = person.id
            self.params['username'] = person.nickname
        except:
            self.params['dmmid'] = ''
            self.params['username'] = u'****'

#=================================================
# friend.
class BossWinLog(BaseGameLog):
    """ボスに勝った.
    """
    def __init__(self, *args, **kwgs):
        BaseGameLog.__init__(self, *args, **kwgs)
    
    @classmethod
    def makeData(cls, uid, area):
        log_data = FriendLogList.create(0, uid, Defines.FriendLogType.BOSS_WIN, {'area':area})
        return log_data
    
    def load_params(self, apphandler):
        model_mgr = apphandler.getModelMgr()
        area = self.getOption('area')
        master = model_mgr.get_model(AreaMaster, area, using=settings.DB_READONLY)
        if master:
            self.params['area'] = master.name
        else:
            self.params['area'] = u'****'
        self.params['url'] = apphandler.makeAppLinkUrl(UrlMaker.profile(self.uid))
    
    def makeApiRequest(self, apphandler):
        """表示用に必要な情報をロード.
        """
        return {
            'BossWinLog:%s:uid' % (self.id) : self.makePersonApiRequest(apphandler, self.uid)
        }
    
    def apirequestCB(self, ret_data, reqkey, *args, **kwargs):
        """Apiリクエストのコールバック.
        """
        try:
            person = ret_data[reqkey].get()
            self.params['dmmid'] = person.id
            self.params['username'] = person.nickname
        except:
            self.params['dmmid'] = ''
            self.params['username'] = u'****'

class ScoutClearLog(BaseGameLog):
    """スカウトクリア.
    """
    def __init__(self, *args, **kwgs):
        BaseGameLog.__init__(self, *args, **kwgs)
    
    @classmethod
    def makeData(cls, uid, scout):
        log_data = FriendLogList.create(0, uid, Defines.FriendLogType.SCOUT_CLEAR,  {'scout':scout})
        return log_data
    
    def load_params(self, apphandler):
        model_mgr = apphandler.getModelMgr()
        scout = self.getOption('scout')
        scoutmaster = model_mgr.get_model(ScoutMaster, scout, using=settings.DB_READONLY)
        if scoutmaster:
            areamaster = model_mgr.get_model(AreaMaster, scoutmaster.area, using=settings.DB_READONLY)
            self.params['scout'] = u'%s%s' % (areamaster.name, scoutmaster.name)
        else:
            self.params['scout'] = u'****'
        self.params['url'] = apphandler.makeAppLinkUrl(UrlMaker.profile(self.uid))
    
    def makeApiRequest(self, apphandler):
        """表示用に必要な情報をロード.
        """
        return {
            'ScoutClearLog:%s:uid' % (self.id) : self.makePersonApiRequest(apphandler, self.uid)
        }
    
    def apirequestCB(self, ret_data, reqkey, *args, **kwargs):
        """Apiリクエストのコールバック.
        """
        try:
            person = ret_data[reqkey].get()
            self.params['dmmid'] = person.id
            self.params['username'] = person.nickname
        except:
            self.params['dmmid'] = ''
            self.params['username'] = u'****'

class EventBossWinLogBase(BaseGameLog):
    """イベントボスに勝った.
    """
    def __init__(self, *args, **kwgs):
        BaseGameLog.__init__(self, *args, **kwgs)
    
    @classmethod
    def getLogType(cls):
        raise NotImplementedError()
    
    def getStageMaster(self, model_mgr):
        raise NotImplementedError()
    
    @classmethod
    def makeData(cls, uid, stage):
        log_data = FriendLogList.create(0, uid, cls.getLogType(), {'stage':stage})
        return log_data
    
    def load_params(self, apphandler):
        model_mgr = apphandler.getModelMgr()
        master = self.getStageMaster(model_mgr)
        if master:
            self.params['area'] = master.areaname
        else:
            self.params['area'] = u'****'
        self.params['url'] = apphandler.makeAppLinkUrl(UrlMaker.profile(self.uid))
    
    def makeApiRequest(self, apphandler):
        """表示用に必要な情報をロード.
        """
        return {
            '{}:{}:uid'.format(self.__class__.__name__, self.id) : self.makePersonApiRequest(apphandler, self.uid)
        }
    
    def apirequestCB(self, ret_data, reqkey, *args, **kwargs):
        """Apiリクエストのコールバック.
        """
        try:
            person = ret_data[reqkey].get()
            self.params['dmmid'] = person.id
            self.params['username'] = person.nickname
        except:
            self.params['dmmid'] = ''
            self.params['username'] = u'****'

class EventBossWinLog(EventBossWinLogBase):
    """スカウトイベントボスに勝った.
    """
    def __init__(self, *args, **kwgs):
        EventBossWinLogBase.__init__(self, *args, **kwgs)
    
    @classmethod
    def getLogType(cls):
        return Defines.FriendLogType.EVENTBOSS_WIN
    
    def getStageMaster(self, model_mgr):
        stage = self.getOption('stage')
        master = model_mgr.get_model(ScoutEventStageMaster, stage, using=settings.DB_READONLY)
        return master

class RaidEventBossWinLog(EventBossWinLogBase):
    """レイドイベントボスに勝った.
    """
    def __init__(self, *args, **kwgs):
        EventBossWinLogBase.__init__(self, *args, **kwgs)
    
    @classmethod
    def getLogType(cls):
        return Defines.FriendLogType.RAIDEVENTBOSS_WIN
    
    def getStageMaster(self, model_mgr):
        stage = self.getOption('stage')
        master = model_mgr.get_model(RaidEventScoutStageMaster, stage, using=settings.DB_READONLY)
        return master

class EventStageClearLogBase(BaseGameLog):
    """イベントスカウトクリア.
    """
    def __init__(self, *args, **kwgs):
        BaseGameLog.__init__(self, *args, **kwgs)
    
    @classmethod
    def getLogType(cls):
        raise NotImplementedError()
    
    def getStageMaster(self, model_mgr):
        raise NotImplementedError()
    
    @classmethod
    def makeData(cls, uid, stage):
        logtype = cls.getLogType()
        log_data = FriendLogList.create(0, uid, logtype, {'stage':stage})
        return log_data
    
    def load_params(self, apphandler):
        model_mgr = apphandler.getModelMgr()
        master = self.getStageMaster(model_mgr)
        if master:
            self.params['scout'] = u'%s%s' % (master.areaname, master.name)
        else:
            self.params['scout'] = u'****'
        self.params['url'] = apphandler.makeAppLinkUrl(UrlMaker.profile(self.uid))
    
    def makeApiRequest(self, apphandler):
        """表示用に必要な情報をロード.
        """
        return {
            '{}:{}:uid'.format(self.__class__.__name__, self.id) : self.makePersonApiRequest(apphandler, self.uid)
        }
    
    def apirequestCB(self, ret_data, reqkey, *args, **kwargs):
        """Apiリクエストのコールバック.
        """
        try:
            person = ret_data[reqkey].get()
            self.params['dmmid'] = person.id
            self.params['username'] = person.nickname
        except:
            self.params['dmmid'] = ''
            self.params['username'] = u'****'

class EventStageClearLog(EventStageClearLogBase):
    """スカウトイベントスカウトクリア.
    """
    def __init__(self, *args, **kwgs):
        EventStageClearLogBase.__init__(self, *args, **kwgs)
    
    @classmethod
    def getLogType(cls):
        return Defines.FriendLogType.EVENTSTAGE_CLEAR
    
    def getStageMaster(self, model_mgr):
        stage = self.getOption('stage')
        master = model_mgr.get_model(ScoutEventStageMaster, stage, using=settings.DB_READONLY)
        return master

class RaidEventStageClearLog(EventStageClearLogBase):
    """レイドイベントスカウトクリア.
    """
    def __init__(self, *args, **kwgs):
        EventStageClearLogBase.__init__(self, *args, **kwgs)
    
    @classmethod
    def getLogType(cls):
        return Defines.FriendLogType.RAIDEVENTSTAGE_CLEAR
    
    def getStageMaster(self, model_mgr):
        stage = self.getOption('stage')
        master = model_mgr.get_model(RaidEventScoutStageMaster, stage, using=settings.DB_READONLY)
        return master

PLAYERLOG_TABLE = {
    Defines.PlayerLogType.BATTLE_RECEIVE_WIN: BattleReceiveWinLog,
    Defines.PlayerLogType.BATTLE_RECEIVE_LOSE: BattleReceiveLoseLog,
    Defines.PlayerLogType.BATTLE_WIN: BattleWinLog,
    Defines.PlayerLogType.BATTLE_LOSE: BattleLoseLog,
}
FRIENDLOG_TABLE = {
    Defines.FriendLogType.BOSS_WIN: BossWinLog,
    Defines.FriendLogType.SCOUT_CLEAR: ScoutClearLog,
    Defines.FriendLogType.EVENTBOSS_WIN: EventBossWinLog,
    Defines.FriendLogType.EVENTSTAGE_CLEAR: EventStageClearLog,
    Defines.FriendLogType.RAIDEVENTBOSS_WIN: RaidEventBossWinLog,
    Defines.FriendLogType.RAIDEVENTSTAGE_CLEAR: RaidEventStageClearLog,
}
def getPlayerLogCls(logtype):
    return PLAYERLOG_TABLE.get(logtype, None)

def getFriendLogCls(logtype):
    return FRIENDLOG_TABLE.get(logtype, None)

def getGameLog(log_data):
    # ゲームログのタイプとクラスをマッピング.
    cls = None
    if isinstance(log_data, FriendLogList):
        func = getFriendLogCls
#    if isinstance(log_data, PlayerLog):
#        func = getPlayerLogCls
    if func:
        cls = func(log_data.logtype)
    if cls is None:
        raise CabaretError(u'未実装の%s:%s' % (log_data.__class__.__name__, log_data.logtype))
    return cls(log_data)

    
    