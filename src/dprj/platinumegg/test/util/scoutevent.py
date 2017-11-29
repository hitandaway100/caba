# -*- coding: utf-8 -*-
from platinumegg.test.dummy_factory import DummyType
from platinumegg.lib.opensocial.util import OSAUtil
import datetime
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi


class ScoutEventTestUtil():
    """スカウトイベントのテストのユーティリティ.
    """
    
    def __init__(self, apitest, event_args, eventstage_args):
        self.__apitest = apitest
        self.__event_args = event_args or {}
        self.__eventstage_args = eventstage_args or {}
        self.__config_pre = None
        
        eventmaster = self.create_dummy(DummyType.SCOUT_EVENT_MASTER, **self.__event_args)
        self.__eventmaster = eventmaster
        
        self.__players = {}
        self.__stages = {}
        
        self.__tanzakumasters = {}
        self.__tanzakudata = {}
    
    @property
    def eventmaster(self):
        return self.__eventmaster
    
    def create_dummy(self, *args, **kwargs):
        return self.__apitest.create_dummy(*args, **kwargs)
    
    def create_player(self, opening_viewed=True, score_args=None):
        player = self.create_dummy(DummyType.PLAYER)
        
        # 進行情報.
        playdata = self.create_dummy(DummyType.SCOUT_EVENT_PLAY_DATA, player.id, self.__eventmaster.id)
        
        # OPを閲覧済みに.
        vtime = OSAUtil.get_now() if opening_viewed else OSAUtil.get_datetime_min()
        flagrecord = self.create_dummy(DummyType.SCOUT_EVENT_FLAGS, player.id, self.__eventmaster.id, vtime)
        
        # スコア情報.
        score_args = score_args or {}
        scorerecord = self.create_dummy(DummyType.SCOUT_EVENT_SCORE, player.id, self.__eventmaster.id, **score_args)
        
        self.__players[player.id] = dict(player=player, playdata=playdata, flagrecord=flagrecord, scorerecord=scorerecord)
        
        return player
    
    def create_tanzakumaster(self, number, prizes=None, tanzaku=0, tip_rate=0, tip_quota=0):
        """短冊の用意.
        """
        self.__tanzakumasters[number] = self.create_dummy(DummyType.SCOUT_EVENT_TANZAKU_CAST_MASTER, self.__eventmaster.id, number, prizes, tanzaku, tip_rate, tip_quota)
        return self.__tanzakumasters[number]
    
    def create_tanzakudata(self, uid, current_cast=-1, tanzaku_nums=None, tip_nums=None):
        """短冊所持情報の用意.
        """
        self.__tanzakudata[uid] = self.create_dummy(DummyType.SCOUT_EVENT_TANZAKU_CAST_DATA, uid, self.__eventmaster.id, current_cast, tanzaku_nums, tip_nums)
        return self.__tanzakudata[uid]
    
    def __get_playerdata(self, uid, name):
        data = self.__players.get(uid)
        return data[name] if data else None
    
    def get_player(self, uid):
        return self.__get_playerdata(uid, 'player')
    
    def get_scoutplaydata(self, uid):
        return self.__get_playerdata(uid, 'playdata')
    
    def get_flagrecord(self, uid):
        return self.__get_playerdata(uid, 'flagrecord')
    
    def get_scorerecord(self, uid):
        return self.__get_playerdata(uid, 'scorerecord')
    
    def add_stage(self, stage, eventstage_args=None):
        args = dict(self.__eventstage_args)
        if eventstage_args:
            args.update(eventstage_args)
        stagemaster = self.create_dummy(DummyType.SCOUT_EVENT_STAGE_MASTER, eventid=self.eventmaster.id, stage=stage, **args)
        self.__stages[stage] = stagemaster
    
    def add_stages_by_maxnumber(self, stage_max, eventstage_args=None):
        for stage in xrange(1, stage_max+1):
            self.add_stage(stage, eventstage_args)
    
    def get_stage(self, stage):
        return self.__stages.get(stage)
    
    def execute_scout(self, uid):
        player = self.get_player(uid)
        playdata = self.get_scoutplaydata(uid)
        stagemaster = self.get_stage(playdata.stage)
        friend_num = BackendApi.get_friend_num(uid)
        
        model_mgr = ModelRequestMgr()
        BackendApi.tr_do_scoutevent_stage(model_mgr, self.eventmaster, player, stagemaster, playdata.confirmkey, False, friend_num, playdata.is_lovetime())
        model_mgr.write_all()
        model_mgr.write_end()
    
    def set_scoutevent_open(self):
        if self.__config_pre is None:
            # イベント発生中設定.
            config = BackendApi.get_current_scouteventconfig(ModelRequestMgr())
            self.__config_pre = {
                'mid' : config.mid,
                'starttime' : config.starttime,
                'endtime' : config.endtime,
            }
            now = OSAUtil.get_now()
            BackendApi.update_scouteventconfig(self.eventmaster.id, now, now + datetime.timedelta(days=1))
    
    def set_scoutevent_close(self):
        if self.__config_pre is None:
            return
        
        model_mgr = ModelRequestMgr()
        config = BackendApi.get_current_scouteventconfig(model_mgr)
        
        for k,v in self.__config_pre.items():
            setattr(config, k, v)
        
        model_mgr.set_save(config)
        model_mgr.write_all()
        model_mgr.write_end()
    