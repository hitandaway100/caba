# -*- coding: utf-8 -*-
from platinumegg.lib.redis.client import Client
from platinumegg.lib.redis import config
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
import datetime
import time
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.lib.pljson import Json
from platinumegg.app.cabaret.models.PlayerLog import PlayerLog
from platinumegg.app.cabaret.models.Greet import GreetLog
import cPickle
from platinumegg.app.cabaret.models.Player import PlayerExp
import random
from platinumegg.app.cabaret.models.Card import Card, CardMaster
from platinumegg.app.cabaret.models.Happening import RaidLog
from platinumegg.lib import timezone
import os
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusTimeLimitedMaster
import settings_sub


class RedisModel:
    """redis用モデル.
    """
    @staticmethod
    def value_to_int(v):
        if type(v) in (int, long, float):
            return int(v)
        elif v is None:
            return None
        parsed_v = None
        try:
            exec "parsed_v=%s" % v
            return int(parsed_v)
        except:
            return None
    
    @staticmethod
    def pydate_to_dbtimestamp(pydate):
        dbdate = pydate.astimezone(timezone.TZ_DB).replace(tzinfo=None)
        return int(time.mktime(dbdate.timetuple()))
    
    @staticmethod
    def dbtimestamp_to_pydate(timestamp):
        dbdate = datetime.datetime.fromtimestamp(int(float(timestamp)))
        return dbdate.replace(tzinfo=timezone.TZ_DB).astimezone(timezone.TZ_DEFAULT)
    
    @classmethod
    def getDB(cls):
        return Client.get(config.REDIS_DEFAULT)
    
    @classmethod
    def create(cls, *args, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def get(cls, *args, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def fetch(cls, *args, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def exists(cls, *args, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def set_ttl(cls, key, sec=2592000, pipe=None):
        if pipe is None:
            cls.getDB().expire(key, sec)
        else:
            pipe.expire(key, sec)
    
    @classmethod
    def save_many(cls, modellist, pipe=None):
        if pipe is None:
            redisdb = cls.getDB()
            pipe = redisdb.pipeline()
            for model in modellist:
                model.save(pipe)
            pipe.execute()
        else:
            for model in modellist:
                model.save(pipe)
    
    def validate(self):
        return None
    
    def _save(self, pipe):
        raise NotImplementedError
    
    def _delete(self, pipe):
        raise NotImplementedError
    
    def save(self, pipe=None):
        errmessage = self.validate()
        if errmessage:
            raise CabaretError('%s:%s' % (self.__class__.__name__, errmessage))
        elif pipe is None:
            redisdb = self.__class__.getDB()
            pipe = redisdb.pipeline()
            self._save(pipe)
            pipe.execute()
        else:
            self._save(pipe)
    
    def delete(self, pipe=None):
        if pipe is None:
            redisdb = self.__class__.getDB()
            pipe = redisdb.pipeline()
            self._delete(pipe)
            pipe.execute()
        else:
            self._delete(pipe)

#=============================================================
class DMMPlayerAssociate(RedisModel):
    """DMMIDとのヒモ付.
    """
    KEY = "DMMIDtoAPPUID"
    dmmid = None
    uid = None
    
    @classmethod
    def create(cls, dmmid, uid=None):
        ins = DMMPlayerAssociate()
        ins.uid = RedisModel.value_to_int(uid)
        ins.dmmid = dmmid
        return ins
    
    @classmethod
    def get(cls, dmmid):
        redisdb = RedisModel.getDB()
        uid = redisdb.hget(DMMPlayerAssociate.KEY, dmmid)
        if uid is None:
            return None
        else:
            return DMMPlayerAssociate.create(dmmid, uid)
    
    @classmethod
    def fetch(cls, dmmidlist):
        redisdb = RedisModel.getDB()
        uidlist = redisdb.hmget(DMMPlayerAssociate.KEY, dmmidlist)
        arr = []
        for i in xrange(len(dmmidlist)):
            ins = DMMPlayerAssociate.create(dmmidlist[i], uidlist[i])
            arr.append(ins)
        return arr
    
    @classmethod
    def exists(cls, dmmid):
        return cls.get(dmmid) is not None
    
    @classmethod
    def save_many(cls, modellist, pipe=None):
        hmap = {}
        for model in modellist:
            hmap[model.dmmid] = model.uid
        if not hmap:
            return
        elif pipe is None:
            redisdb = RedisModel.getDB()
            redisdb.hmset(DMMPlayerAssociate.KEY, hmap)
        else:
            pipe.hmset(DMMPlayerAssociate.KEY, hmap)
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        return None
    
    def _save(self, pipe):
        pipe.hset(DMMPlayerAssociate.KEY, self.dmmid, self.uid)
    
    def _delete(self, pipe):
        pipe.hdel(DMMPlayerAssociate.KEY, self.dmmid)

class LevelGroupSet(RedisModel):
    """レベル帯とユーザID.
    """
    KEY_BASE = 'SerchIndex:levelgroup:%s'
    
    levelgroup = None
    uid = None
    
    @classmethod
    def create(cls, uid, levelgroup):
        ins = LevelGroupSet()
        ins.uid = RedisModel.value_to_int(uid)
        ins.levelgroup = levelgroup
        return ins
    
    @classmethod
    def createByLevel(cls, uid, level):
        levelgroup = None
        if level < 10:
            levelgroup = Defines.LevelGroup.LV01_09
        elif 10 <= level < 20:
            levelgroup = Defines.LevelGroup.LV10_19
        elif 20 <= level < 40:
            levelgroup = Defines.LevelGroup.LV20_39
        elif 40 <= level < 60:
            levelgroup = Defines.LevelGroup.LV40_59
        else:
            levelgroup = Defines.LevelGroup.LV60_OVER
        return LevelGroupSet.create(uid, levelgroup)
    
    @staticmethod
    def makeKey(levelgroup):
        return LevelGroupSet.KEY_BASE % levelgroup
    
    @staticmethod
    def recordnum(levelgroup):
        redisdb = LevelGroupSet.getDB()
        return redisdb.scard(LevelGroupSet.makeKey(levelgroup))
    
    @staticmethod
    def fetch_random(levelgroup, num=1):
        redisdb = LevelGroupSet.getDB()
        arr = [LevelGroupSet.create(uid, levelgroup) for uid in redisdb.srandmember(LevelGroupSet.makeKey(levelgroup), num)]
        return arr
    
    @classmethod
    def exists(cls, levelgroup):
        redisdb = LevelGroupSet.getDB()
        return redisdb.exists(LevelGroupSet.makeKey(levelgroup))
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        return None
    
    def _save(self, pipe):
        pipe.sadd(LevelGroupSet.makeKey(self.levelgroup), self.uid)
    
    def _delete(self, pipe):
        pipe.srem(LevelGroupSet.makeKey(self.levelgroup), self.uid)

class LevelSet(RedisModel):
    """レベルとユーザID.
    """
    KEY_BASE = 'SerchIndex:level:%s'
    
    level = None
    uid = None
    
    @classmethod
    def create(cls, uid, level):
        ins = LevelSet()
        ins.uid = RedisModel.value_to_int(uid)
        ins.level = level
        return ins
    
    @staticmethod
    def makeKey(level):
        return LevelSet.KEY_BASE % level
    
    @staticmethod
    def recordnum(level):
        redisdb = LevelSet.getDB()
        return redisdb.scard(LevelGroupSet.makeKey(level))
    
    @staticmethod
    def fetch_random(level, num=1):
        redisdb = LevelSet.getDB()
        arr = [LevelSet.create(uid, level) for uid in redisdb.srandmember(LevelSet.makeKey(level), num)]
        return arr
    
    @classmethod
    def exists(cls, level):
        redisdb = LevelSet.getDB()
        return redisdb.exists(LevelSet.makeKey(level))
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        return None
    
    def _save(self, pipe):
        pipe.sadd(LevelSet.makeKey(self.level), self.uid)
    
    def _delete(self, pipe):
        pipe.srem(LevelSet.makeKey(self.level), self.uid)

class LoginTimeSet(RedisModel):
    """ログイン時間のセット.
    """
    KEY = 'SerchIndex:logintime'
    
    uid = None
    ltime = None
    
    @classmethod
    def create(cls, uid, ltime=None):
        ins = LoginTimeSet()
        ins.uid = RedisModel.value_to_int(uid)
        ins.ltime = ltime
        return ins
    
    @classmethod
    def get(cls, uid):
        redisdb = RedisModel.getDB()
        ltime = redisdb.zscore(LoginTimeSet.KEY, uid)
        if ltime is None:
            return None
        else:
            return LoginTimeSet.create(uid, RedisModel.dbtimestamp_to_pydate(ltime))
    
    @classmethod
    def fetch(cls, ltime_min, ltime_max):
        redisdb = RedisModel.getDB()
        i_ltime_min = RedisModel.pydate_to_dbtimestamp(ltime_min)
        i_ltime_max = RedisModel.pydate_to_dbtimestamp(ltime_max)
        arr = redisdb.zrangebyscore(LoginTimeSet.KEY, i_ltime_min, i_ltime_max)
        return [cls.value_to_int(v) for v in arr]
    
    @classmethod
    def fetchRandom(cls, num, ltime_min, ltime_max, ignore=None):
        ignore = ignore or []
        
        redisdb = RedisModel.getDB()
        
        i_ltime_min = RedisModel.pydate_to_dbtimestamp(ltime_min)
        i_ltime_max = RedisModel.pydate_to_dbtimestamp(ltime_max)
        
        num_max = redisdb.zcount(LoginTimeSet.KEY, i_ltime_min, i_ltime_max)
        request_num = min(num + len(ignore), num_max)
        offset_min = 0
        offset_max = max(offset_min, num_max - num)
        offset = random.randint(offset_min, offset_max)
        
        arr = redisdb.zrevrangebyscore(LoginTimeSet.KEY, i_ltime_max, i_ltime_min, offset, request_num)
        uidlist = []
        for str_uid in arr:
            uid = RedisModel.value_to_int(str_uid)
            if uid in ignore:
                continue
            uidlist.append(uid)
            if num <= len(uidlist):
                break
        return uidlist
    
    @classmethod
    def exists(cls, uid):
        return cls.get(uid) is not None
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        return None
    
    def _save(self, pipe):
        timestamp = 0
        if self.ltime is not None:
            timestamp = RedisModel.pydate_to_dbtimestamp(self.ltime)
        pipe.zadd(LoginTimeSet.KEY, self.uid, int(timestamp))
    
    def _delete(self, pipe):
        pipe.zrem(LoginTimeSet.KEY, self.uid)

class LoginTimeCloneSet(RedisModel):
    """ログイン時間のセット.
    """
    KEY = 'SerchIndex:logintime:Clone'
    
    @classmethod
    def update(cls):
        redisdb = RedisModel.getDB()
        redisdb.zunionstore(cls.KEY, [LoginTimeSet.KEY], 'MIN')
    
    @classmethod
    def fetchByRange(cls, ltime_min, ltime_max, limit=500, offset=0):
        redisdb = RedisModel.getDB()
        
        i_ltime_min = RedisModel.pydate_to_dbtimestamp(ltime_min)
        i_ltime_max = RedisModel.pydate_to_dbtimestamp(ltime_max)
        
        arr = redisdb.zrevrangebyscore(cls.KEY, i_ltime_max, i_ltime_min, offset, limit)
        uidlist = [RedisModel.value_to_int(str_uid) for str_uid in arr]
        return uidlist

class BattleLevelSet(RedisModel):
    """レベルごとのユーザーのセット.
    """
    KEY = "battle_levelset"
    
    uid = None
    level = None
    
    @classmethod
    def create(cls, uid, level=0):
        ins = cls()
        ins.uid = RedisModel.value_to_int(uid)
        ins.level = RedisModel.value_to_int(level)
        return ins
    
    @classmethod
    def exists(cls, uid):
        redisdb = RedisModel.getDB()
        return redisdb.zscore(cls.KEY, uid) is not None
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.level is None:
            return 'level is None.'
        return None
    
    def _save(self, pipe):
        pipe.zadd(BattleLevelSet.KEY, self.uid, self.level)
    
    def _delete(self, pipe):
        pipe.zrem(BattleLevelSet.KEY, self.uid)
    
    @staticmethod
    def fetchRandom(num, level_min=1, level_max="+inf", excludes=None):
        """レベルの範囲でランダムに取得.
        """
        if num < 1:
            return []
        
        CHOICE_NUM_MAX = 10000
        
        excludes = excludes or []
        neednum = num + len(excludes)
        
        redisdb = RedisModel.getDB()
        nummax = BattleLevelSet.get_num(level_min, level_max)
        if nummax <= neednum:
            uidlist = redisdb.zrangebyscore(BattleLevelSet.KEY, level_min, level_max, score_cast_func=int)
            arr = [BattleLevelSet.create(uid) for uid in uidlist[:num] if not int(uid) in excludes]
        else:
            choice_nummax = min(CHOICE_NUM_MAX, nummax)
            start = random.randrange(max(0, nummax - choice_nummax) + 1)
            end = start + choice_nummax
            indexes = range(start, end)
            random.shuffle(indexes)
            
            if level_min <= 1:
                offset = 0
            else:
                offset = BattleLevelSet.get_num(1, level_min - 1)
            arr = []
            for i in indexes[:neednum]:
                if num <= len(arr):
                    break
                data = redisdb.zrange(BattleLevelSet.KEY, offset+i, offset+i)
                if data:
                    uid = int(data[0])
                    if not uid in excludes:
                        arr.append(BattleLevelSet.create(uid))
        return arr
    
    @staticmethod
    def get_num(level_min=1, level_max="+inf"):
        """レベルの範囲で件数を取得.
        """
        redisdb = RedisModel.getDB()
        return redisdb.zcount(BattleLevelSet.KEY, level_min, level_max) or 0

class UserCardIdListSet(RedisModel):
    """カード.
    """
    
    KEY_BASE = 'UserCardIdListSet:%s'
    
    uid = None
    cardid = None
    
    @classmethod
    def makeKey(cls, uid):
        return cls.KEY_BASE % uid
    
    @classmethod
    def create(cls, uid, cardid):
        ins = cls()
        ins.uid = RedisModel.value_to_int(uid)
        ins.cardid = RedisModel.value_to_int(cardid)
        return ins
    
    @classmethod
    def fetch_id(cls, uid):
        if not cls.get_num(uid):
            return []
        
        redisdb = RedisModel.getDB()
        key = cls.makeKey(uid)
        return [RedisModel.value_to_int(cardid) for cardid in redisdb.smembers(key)]
    
    @classmethod
    def get_num(cls, uid):
        redisdb = RedisModel.getDB()
        key = cls.makeKey(uid)
        return redisdb.scard(key) or 0
    
    def _save(self, pipe):
        key = self.__class__.makeKey(self.uid)
        pipe.sadd(key, self.cardid)
    
    def _delete(self, pipe):
        pipe.srem(self.__class__.makeKey(self.uid), self.cardid)

class EvolutionAlbumHkLevelListSet(RedisModel):
    """カードのアルバムとハメ管理のセット.
    """
    KEY_BASE = 'EvolutionAlbumHkLevelListSet:%s'
    
    uid = None
    cardid = None
    albumhklevel = None
    
    @classmethod
    def create(cls, uid, cardid, albumhklevel):
        ins = cls()
        ins.uid = RedisModel.value_to_int(uid)
        ins.cardid = RedisModel.value_to_int(cardid)
        ins.albumhklevel = RedisModel.value_to_int(albumhklevel)
        return ins
    
    @staticmethod
    def makeKey(uid):
        return EvolutionAlbumHkLevelListSet.KEY_BASE % uid
    
    @classmethod
    def exists(cls, uid):
        redisdb = RedisModel.getDB()
        return redisdb.exists(cls.makeKey(uid))
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.cardid is None:
            return 'cardid is None.'
        elif self.albumhklevel is None:
            return 'albumhklevel is None.'
        return None
    
    @classmethod
    def count_evolution_ablenum(cls, uid, album, hklevel):
        """同じアルバムで進化に使える数を調べたい.
        """
        if not cls.exists(uid):
            return None
        
        redisdb = RedisModel.getDB()
        key = cls.makeKey(uid)
        
        albumhklevel_min = CardMaster.makeAlbumHklevel(album, 1)
        albumhklevel_max = CardMaster.makeAlbumHklevel(album, hklevel)
        
        return redisdb.zcount(key, albumhklevel_min, albumhklevel_max)
    
    def _save(self, pipe):
        key = EvolutionAlbumHkLevelListSet.makeKey(self.uid)
        pipe.zadd(key, self.cardid, self.albumhklevel)
    
    def _delete(self, pipe):
        pipe.zrem(EvolutionAlbumHkLevelListSet.makeKey(self.uid), self.cardid)

class CardKindListSet(RedisModel):
    """カードの種類のセット.
    """
    KEY_BASE = 'CardKindListSet:%s'
    
    uid = None
    cardid = None
    kind = None
    rare = None
    
    @classmethod
    def create(cls, uid, cardid, kind, rare):
        ins = cls()
        ins.uid = RedisModel.value_to_int(uid)
        ins.cardid = RedisModel.value_to_int(cardid)
        ins.kind = RedisModel.value_to_int(kind)
        ins.rare = RedisModel.value_to_int(rare)
        
        return ins
    
    @staticmethod
    def makeKey(uid):
        return CardKindListSet.KEY_BASE % uid
    
    @classmethod
    def exists(cls, uid):
        redisdb = RedisModel.getDB()
        return redisdb.exists(cls.makeKey(uid))
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.cardid is None:
            return 'cardid is None.'
        elif self.kind is None:
            return 'kind is None.'
        elif self.rare is None:
            return 'rare is None.'
        return None
    
    @staticmethod
    def rarekind_to_score(kind, rare):
        return (kind << 4) + rare
    @staticmethod
    def score_to_rarekind(score):
        score = RedisModel.value_to_int(score)
        if score:
            kind = int(score >> 4)
            rare = int(score & 15)
        else:
            kind = None
            rare = None
        return kind, rare
    
    @classmethod
    def fetch_by_kind(cls, uid, kind, rare=None, limit=None, offset=0):
        """種類を指定してカードのIDを取得.
        """
        if not cls.exists(uid):
            return None
        
        redisdb = RedisModel.getDB()
        key = cls.makeKey(uid)
        
        if rare is None:
            min_value = cls.rarekind_to_score(kind, Defines.Rarity.NORMAL)
            max_value = cls.rarekind_to_score(kind, Defines.Rarity.RARITY_MAX)
        else:
            min_value = cls.rarekind_to_score(kind, rare)
            max_value = min_value
        
        if limit is None:
            arr = redisdb.zrangebyscore(key, min_value, max_value, withscores=True, score_cast_func=long)[offset:]
        else:
            arr = redisdb.zrangebyscore(key, min_value, max_value, start=offset, num=limit, withscores=True, score_cast_func=long)
        
        return [cls.create(uid, cardid, *cls.score_to_rarekind(v)) for cardid, v in arr]
    
    @classmethod
    def count_by_kind(cls, uid, kind, rare=None):
        """種類を指定してカードのIDを取得.
        """
        redisdb = RedisModel.getDB()
        key = cls.makeKey(uid)
        
        if rare is None:
            min_value = cls.rarekind_to_score(kind, Defines.Rarity.NORMAL)
            max_value = cls.rarekind_to_score(kind, Defines.Rarity.RARITY_MAX)
        else:
            min_value = cls.rarekind_to_score(kind, rare)
            max_value = min_value
        
        return redisdb.zcount(key, min_value, max_value)
    
    def _save(self, pipe):
        pipe.zadd(CardKindListSet.makeKey(self.uid), self.cardid, self.rarekind_to_score(self.kind, self.rare))
    
    def _delete(self, pipe):
        pipe.zrem(CardKindListSet.makeKey(self.uid), self.cardid)

class FriendListSet(RedisModel):
    """仲間一覧のセット.
    """
    KEY_BASE = "friend_idlist:%s:%s"
    uid = None
    fid = None
    state = None
    ctime = None
    
    @classmethod
    def create(cls, uid, fid, state, ctime=None):
        ins = FriendListSet()
        ins.uid = RedisModel.value_to_int(uid)
        ins.fid = RedisModel.value_to_int(fid)
        ins.state = RedisModel.value_to_int(state)
        ins.ctime = ctime
        return ins
    
    @staticmethod
    def makeKey(uid, state):
        return FriendListSet.KEY_BASE % (uid, state)
    
    @classmethod
    def get(cls, uid, fid, state):
        redisdb = RedisModel.getDB()
        ctime = redisdb.zscore(FriendListSet.makeKey(uid, state), fid)
        if ctime is None:
            return None
        else:
            return FriendListSet.create(uid, fid, state, RedisModel.dbtimestamp_to_pydate(ctime))
    
    @classmethod
    def fetch(cls, uid, state, offset=0, limit=None):
        redisdb = RedisModel.getDB()
        key = FriendListSet.makeKey(uid, state)
        if not redisdb.exists(key):
            return []
        
        start = offset
        end = -1
        if 0 < limit:
            end = start + limit - 1
        
        key = FriendListSet.makeKey(uid, state)
        return [FriendListSet.create(uid, fid, state) for fid in redisdb.zrevrange(key, start, end)]
    
    @staticmethod
    def get_num(uid, state):
        redisdb = RedisModel.getDB()
        key = FriendListSet.makeKey(uid, state)
        if not redisdb.exists(key):
            return None
        return redisdb.zcard(key)
    
    @classmethod
    def exists(cls, uid, fid, state):
        return FriendListSet.get(uid, fid, state) is not None
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.fid is None:
            return 'fid is None.'
        elif self.state is None:
            return 'state is None.'
        return None
    
    def _save(self, pipe):
        timestamp = 0
        if self.ctime is not None:
            timestamp = RedisModel.pydate_to_dbtimestamp(self.ctime)
        pipe.zadd(FriendListSet.makeKey(self.uid, self.state), self.fid, int(timestamp))
    
    def _delete(self, pipe):
        pipe.zrem(FriendListSet.makeKey(self.uid, self.state), self.fid)

class FriendAcceptNum(RedisModel):
    """仲間承認してくれた数.
    """
    KEY = 'friendaccept_num'
    
    uid = None
    num = None
    
    @classmethod
    def create(cls, uid, num=0):
        ins = FriendAcceptNum()
        ins.uid = RedisModel.value_to_int(uid)
        ins.num = RedisModel.value_to_int(num)
        return ins
    
    @classmethod
    def get(cls, uid):
        redisdb = RedisModel.getDB()
        num = redisdb.hget(FriendAcceptNum.KEY, uid) or 0
        return FriendAcceptNum.create(uid, num)
    
    @classmethod
    def incr(cls, uid, num=1, pipe=None):
        do_execute = False
        if pipe is None:
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            do_execute = True
        pipe.hincrby(FriendAcceptNum.KEY, uid, num)
        if do_execute:
            pipe.execute()
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.num is None:
            return 'num is None.'
        return None
    
    def _save(self, pipe):
        pipe.hset(FriendAcceptNum.KEY, self.uid, self.num)
    
    def _delete(self, pipe):
        pipe.hdel(FriendAcceptNum.KEY, self.uid)

class FreeGachaLastTime(RedisModel):
    """無料ガチャを最後に回した時間.
    """
    KEY = 'freegachalasttime'
    uid = None
    ltime = None
    
    @classmethod
    def create(cls, uid, ltime=None):
        ins = FreeGachaLastTime()
        ins.uid = RedisModel.value_to_int(uid)
        ins.ltime = ltime
        return ins
    
    @classmethod
    def get(cls, uid):
        redisdb = RedisModel.getDB()
        ltime = redisdb.hget(FreeGachaLastTime.KEY, uid)
        if ltime is not None:
            ltime = RedisModel.dbtimestamp_to_pydate(ltime)
        return FreeGachaLastTime.create(uid, ltime)
    
    @classmethod
    def fetch(cls, uidlist):
        redisdb = RedisModel.getDB()
        ltimelist = redisdb.hmget(DMMPlayerAssociate.KEY, uidlist)
        arr = []
        for i in xrange(len(uidlist)):
            ltime = ltimelist[i]
            if ltime is not None:
                ltime = RedisModel.dbtimestamp_to_pydate(ltime)
            ins = FreeGachaLastTime.create(uidlist[i], ltime)
            arr.append(ins)
        return arr
    
    @classmethod
    def exists(cls, uid):
        return cls.get(uid).ltime is not None
    
    @classmethod
    def save_many(cls, modellist, pipe=None):
        hmap = {}
        for model in modellist:
            hmap[model.uid] = RedisModel.pydate_to_dbtimestamp(model.ltime)
        if not hmap:
            return
        elif pipe is None:
            redisdb = RedisModel.getDB()
            redisdb.hmset(FreeGachaLastTime.KEY, hmap)
        else:
            pipe.hmset(FreeGachaLastTime.KEY, hmap)
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.ltime is None:
            return 'ltime is None.'
        return None
    
    def _save(self, pipe):
        pipe.hset(FreeGachaLastTime.KEY, self.uid, RedisModel.pydate_to_dbtimestamp(self.ltime))
    
    def _delete(self, pipe):
        pipe.hdel(FreeGachaLastTime.KEY, self.uid)

class RareLogList(RedisModel):
    """レアキャバ嬢獲得履歴.
    """
    KEY_BASE = 'gachararelog:%s'
    NUM_MAX = 10
    
    gacha_id = None
    gacha_boxid = None
    uid = None
    mid = None
    ctime = None
    
    @classmethod
    def makeKey(cls, gacha_boxid):
        return cls.KEY_BASE % gacha_boxid
    
    @classmethod
    def create(cls, gacha_boxid, gacha_id, uid, mid, ctime=None):
        ins = RareLogList()
        ins.gacha_id = RedisModel.value_to_int(gacha_id)
        ins.gacha_boxid = RedisModel.value_to_int(gacha_boxid)
        ins.uid = RedisModel.value_to_int(uid)
        ins.mid = RedisModel.value_to_int(mid)
        ins.ctime = ctime or OSAUtil.get_now()
        return ins
    
    @classmethod
    def fetch(cls, gacha_boxid, limit=1, offset=0):
        redisdb = RedisModel.getDB()
        datalist = redisdb.lrange(cls.makeKey(gacha_boxid), offset, limit)
        return [RareLogList.from_db_data(str_json) for str_json in datalist]
    
    @classmethod
    def save_many(cls, modellist, pipe=None):
        if not modellist:
            return
        
        items = {}
        for model in modellist:
            key = cls.makeKey(model.gacha_boxid)
            arr = items[key] = items.get(key) or []
            arr.append(model.to_db_data())
        
        if pipe is None:
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            for key,arr in items.items():
                pipe.lpush(key, *arr)
                pipe.ltrim(key, 0, RareLogList.NUM_MAX)
            pipe.execute()
        else:
            for key,arr in items.items():
                pipe.lpush(key, *arr)
                pipe.ltrim(key, 0, RareLogList.NUM_MAX)
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.mid is None:
            return 'mid is None.'
        elif self.ctime is None:
            return 'ctime is None.'
        elif self.gacha_id is None:
            return 'gacha_id is None.'
        elif self.gacha_boxid is None:
            return 'gacha_boxid is None.'
        return None
    
    def _save(self, pipe):
        key = self.makeKey(self.gacha_boxid)
        pipe.lpush(key, self.to_db_data())
        pipe.ltrim(key, 0, RareLogList.NUM_MAX)
    
    @staticmethod
    def from_db_data(str_json):
        data = Json.decode(str_json)
        return RareLogList.create(data['boxid'], data['gachaid'], data['uid'], data['mid'], data['time'])
    def to_db_data(self):
        return Json.encode({'uid':self.uid,'mid':self.mid,'time':self.ctime,'boxid':self.gacha_boxid,'gachaid':self.gacha_id})

class PresentIdListSet(RedisModel):
    """届いているプレゼントのIDのセット.
    """
    KEY_BASE = 'presentidlist:%s:%d'
    
    uid = None
    presentid = None
    ctime = None
    topic = None
    
    @classmethod
    def create(cls, uid, presentid, topic=Defines.PresentTopic.ALL, ctime=None):
        ins = PresentIdListSet()
        ins.uid = RedisModel.value_to_int(uid)
        ins.presentid = RedisModel.value_to_int(presentid)
        ins.topic = RedisModel.value_to_int(topic)
        ins.ctime = ctime
        return ins
    
    @staticmethod
    def makeKey(uid, topic):
        return PresentIdListSet.KEY_BASE % (uid, topic)
    
    @classmethod
    def fetch(cls, uid, topic, offset=0, limit=None, desc=True):
        if not PresentIdListSet.exists(uid, topic):
            return []
        
        redisdb = RedisModel.getDB()
        
        start = offset
        end = -1
        if limit and 0 < limit:
            end = start + limit - 1
        key = PresentIdListSet.makeKey(uid, topic)
        if desc:
            idlist = redisdb.zrevrange(key, start, end)
        else:
            idlist = redisdb.zrange(key, start, end)
        return [PresentIdListSet.create(uid, presentid, topic) for presentid in idlist]
    
    @staticmethod
    def get_presentnum(uid, topic=Defines.PresentTopic.ALL):
        if PresentIdListSet.exists(uid, topic):
            redisdb = RedisModel.getDB()
            return redisdb.zcard(PresentIdListSet.makeKey(uid, topic))
        else:
            return None
    
    @classmethod
    def exists(cls, uid, topic):
        redisdb = RedisModel.getDB()
        return redisdb.exists(PresentIdListSet.makeKey(uid, topic))
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.presentid is None:
            return 'presentid is None.'
        elif self.ctime is None:
            return 'ctime is None.'
        elif self.topic is None:
            return 'topic is None.'
        return None
    
    def _save(self, pipe):
        pipe.zadd(PresentIdListSet.makeKey(self.uid, self.topic), self.presentid, RedisModel.pydate_to_dbtimestamp(self.ctime))
    
    def _delete(self, pipe):
        pipe.zrem(PresentIdListSet.makeKey(self.uid, Defines.PresentTopic.ALL), self.presentid)
        if self.topic != Defines.PresentTopic.ALL:
            pipe.zrem(PresentIdListSet.makeKey(self.uid, self.topic), self.presentid)

class GameLogListBase(RedisModel):
    """行動履歴系のログ.
    """
    KEY_BASE = '%sidlist:%s'
    if settings_sub.IS_DEV:
        NUM_MAX = 5
    else:
        NUM_MAX = 50
    
    uid = None
    logid = None
    ctime = None
    
    @classmethod
    def get_modelclass(cls):
        raise NotImplementedError
    
    @classmethod
    def create(cls, uid, logid, ctime=None):
        ins = cls()
        ins.uid = cls.value_to_int(uid)
        ins.logid = cls.value_to_int(logid)
        ins.ctime = ctime
        return ins
    
    @classmethod
    def makeKey(cls, uid):
        model_cls = cls.get_modelclass()
        return cls.KEY_BASE % (model_cls.__name__, uid)
    
    @classmethod
    def fetch(cls, uid, offset=0, limit=None):
        if not cls.exists(uid):
            return []
        
        redisdb = cls.getDB()
        
        start = offset
        end = -1
        if 0 < limit:
            end = start + limit - 1
        key = cls.makeKey(uid)
        return [cls.create(uid, logid) for logid in redisdb.zrevrange(key, start, end)]
    
    @classmethod
    def exists(cls, uid):
        redisdb = cls.getDB()
        return redisdb.exists(cls.makeKey(uid))
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.logid is None:
            return 'logid is None.'
        elif self.ctime is None:
            return 'ctime is None.'
        return None
    
    def _save(self, pipe):
        key = self.__class__.makeKey(self.uid)
        redisdb = self.__class__.getDB()
        num = redisdb.zcard(key)
        if self.NUM_MAX <= num:
            pipe.zremrangebyrank(key, 0, num - self.NUM_MAX)
        pipe.zadd(key, self.logid, self.__class__.pydate_to_dbtimestamp(self.ctime))
    
    def _delete(self, pipe):
        pipe.zrem(self.__class__.makeKey(self.uid), self.logid)

class PlayerLogListSet(GameLogListBase):
    """プレイヤーの行動履歴.
    """
    @classmethod
    def get_modelclass(cls):
        return PlayerLog
    
    @staticmethod
    def get_num(uid):
        redisdb = RedisModel.getDB()
        key = PlayerLogListSet.makeKey(uid)
        if not redisdb.exists(key):
            return None
        return redisdb.zcard(key)

class GreetLogListSet(GameLogListBase):
    """あいさつ履歴.
    """
    @classmethod
    def get_modelclass(cls):
        return GreetLog
    
    @staticmethod
    def get_num(uid):
        redisdb = RedisModel.getDB()
        key = GreetLogListSet.makeKey(uid)
        if not redisdb.exists(key):
            return None
        return redisdb.zcard(key)

class FriendLogReserveList(RedisModel):
    """仲間の行動履歴登録予約.
    """
    KEY = "FriendLogReserveList"
    friendlist = None
    logmodel = None
    
    @classmethod
    def getDB(cls):
        return Client.get(config.REDIS_LOG)
    
    @classmethod
    def create(cls, friendlist, logmodel):
        ins = cls()
        ins.friendlist = friendlist
        ins.logmodel = logmodel
        return ins
    
    @classmethod
    def to_python(cls, dbdata):
        try:
            obj = cPickle.loads(dbdata)
            friendlist, logmodel_dbdata = obj
            logmodel = FriendLogList.to_python(0, logmodel_dbdata)
        except:
            return None
        ins = cls.create(friendlist, logmodel)
        return ins
    
    @classmethod
    def get_num(cls):
        redisdb = cls.getDB()
        return redisdb.llen(cls.KEY)
    
    @classmethod
    def pop(cls):
        redisdb = cls.getDB()
        dbdata = redisdb.rpop(cls.KEY)
        if not dbdata:
            return None
        return cls.to_python(dbdata)
    
    def _save(self, pipe):
        obj = (self.friendlist, self.logmodel.to_dbdata())
        try:
            dbdata = cPickle.dumps(obj)
        except:
            return
        pipe.lpush(self.KEY, dbdata)
    

class FriendLogList(RedisModel):
    """仲間の行動履歴.
    """
    KEY_BASE = 'FriendLogList:%s'
    NUM_MAX = Defines.PLAYERLOG_NUM_MAX
    
    @classmethod
    def getDB(cls):
        return Client.get(config.REDIS_LOG)
    
    oid = None  # ログを受け取った人.
    uid = None  # ログを発信した人.
    ctime = None
    logtype = None
    data = None
    
    @classmethod
    def create(cls, oid, uid, logtype, data, ctime=None):
        ins = cls()
        ins.uid = RedisModel.value_to_int(uid)
        ins.oid = RedisModel.value_to_int(oid)
        ins.ctime = ctime or OSAUtil.get_now()
        ins.logtype = RedisModel.value_to_int(logtype)
        ins.data = data or {}
        return ins
    
    @classmethod
    def to_python(cls, oid, dbdata):
        try:
            obj = cPickle.loads(dbdata)
            uid, logtype, strctime, data = obj
            ctime = DateTimeUtil.strToDateTime(strctime, "%Y%m%d%H%M%S")
        except:
            return None
        return cls.create(oid, uid, logtype, data, ctime)
    
    def to_dbdata(self):
        strctime = self.ctime.strftime("%Y%m%d%H%M%S")
        obj = (self.uid, self.logtype, strctime, self.data)
        return cPickle.dumps(obj)
    
    @classmethod
    def makeKey(cls, oid):
        return cls.KEY_BASE % oid
    
    @classmethod
    def fetch(cls, oid, offset=0, limit=None):
        key = cls.makeKey(oid)
        redisdb = cls.getDB()
        
        limit = cls.NUM_MAX if limit is None else limit
        start = offset
        end = min(start + limit, cls.NUM_MAX) - 1
        
        result = []
        for dbdata in redisdb.lrange(key, start, end):
            model = cls.to_python(oid, dbdata)
            if model is None:
                continue
            result.append(model)
        return result
    
    @classmethod
    def get_num(cls, oid):
        key = cls.makeKey(oid)
        redisdb = cls.getDB()
        return min(cls.NUM_MAX, redisdb.llen(key))
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.oid is None:
            return 'oid is None.'
        elif self.ctime is None:
            return 'ctime is None.'
        elif self.logtype is None:
            return 'logtype is None.'
        elif self.data is None:
            return 'data is None.'
        return None
    
    def _save(self, pipe):
        key = self.makeKey(self.oid)
        dbdata = self.to_dbdata()
        
        self.set_ttl(key, pipe=pipe)
        pipe.lpush(key, dbdata)
        pipe.ltrim(key, 0, self.NUM_MAX)

class LastViewArea(RedisModel):
    """最後に閲覧したエリア.
    """
    KEY = 'lastview_areaid'
    uid = None
    areaid = None
    
    @classmethod
    def create(cls, uid, areaid=None):
        ins = LastViewArea()
        ins.uid = RedisModel.value_to_int(uid)
        ins.areaid = areaid
        return ins
    
    @classmethod
    def get(cls, uid):
        redisdb = RedisModel.getDB()
        areaid = redisdb.hget(LastViewArea.KEY, uid)
        if areaid is None:
            return None
        else:
            return LastViewArea.create(uid, areaid)
    
    @classmethod
    def fetch(cls, uidlist):
        redisdb = RedisModel.getDB()
        areaidlist = redisdb.hmget(LastViewArea.KEY, uidlist)
        arr = []
        for i in xrange(len(uidlist)):
            ins = LastViewArea.create(uidlist[i], areaidlist[i])
            arr.append(ins)
        return arr
    
    @classmethod
    def exists(cls, uid):
        return cls.get(uid) is not None
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.areaid is None:
            return 'areaid is None.'
        return None
    
    def _save(self, pipe):
        pipe.hset(LastViewArea.KEY, self.uid, self.areaid)
    
    def _delete(self, pipe):
        pipe.hdel(LastViewArea.KEY, self.uid)

class BossResultData(RedisModel):
    """ボスとの対戦結果.
    """
    KEY_BASE = 'bossresultdata:%d'
    
    uid = None
    data = None
    
    @classmethod
    def create(cls, uid, data=None):
        ins = BossResultData()
        ins.uid = RedisModel.value_to_int(uid)
        ins.data = data
        return ins
    
    @staticmethod
    def makeKey(uid):
        return BossResultData.KEY_BASE % uid
    
    @classmethod
    def get(cls, uid):
        redisdb = RedisModel.getDB()
        data = redisdb.get(BossResultData.makeKey(uid))
        if data:
            return BossResultData.from_db_data(uid, data)
        else:
            return None
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.data is None:
            return 'data is None.'
        return None
    
    def _save(self, pipe):
        pipe.set(BossResultData.makeKey(self.uid), self.to_db_data())
    def _delete(self, pipe):
        pipe.delete(BossResultData.makeKey(self.uid))
    
    @staticmethod
    def from_db_data(uid, strdata):
        data = cPickle.loads(strdata)
        return BossResultData.create(uid, data)
    def to_db_data(self):
        strdata = cPickle.dumps(self.data)
        return strdata

class RaidHelpSet(RedisModel):
    """レイドの救援要請.
    """
    KEY_BASE = 'raidhelpset:%d'
    
    uid = None
    raidhelpid = None
    etime = None
    
    @classmethod
    def create(cls, uid, raidhelpid, etime=None):
        ins = cls()
        ins.uid = RedisModel.value_to_int(uid)
        ins.raidhelpid = RedisModel.value_to_int(raidhelpid)
        ins.etime = etime
        return ins
    
    @classmethod
    def makeKey(cls, uid):
        return cls.KEY_BASE % uid
    
    @classmethod
    def exists(cls, uid):
        redisdb = RedisModel.getDB()
        return redisdb.exists(cls.makeKey(uid))
    
    @classmethod
    def refresh(cls, uid):
        """セットをリフレッシュ.
        """
        redisdb = RedisModel.getDB()
        timestamp = RedisModel.pydate_to_dbtimestamp(OSAUtil.get_now())
        redisdb.zremrangebyscore(RaidHelpSet.makeKey(uid), '-inf', timestamp)
    
    @classmethod
    def fetch(cls, uid, limit=None, offset=0):
        """範囲検索.
        """
        redisdb = RedisModel.getDB()
        start = offset
        if limit:
            end = offset + limit
        else:
            end = -1
        return [cls.create(uid, raidhelpid) for raidhelpid in redisdb.zrevrange(RaidHelpSet.makeKey(uid), start, end, score_cast_func=int)]
    
    @classmethod
    def get_num(cls, uid):
        """件数.
        """
        redisdb = RedisModel.getDB()
        return redisdb.zcard(RaidHelpSet.makeKey(uid))
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.raidhelpid is None:
            return 'raidhelpid is None.'
        elif self.etime is None:
            return 'etime is None.'
        return None
    
    def _save(self, pipe):
        timestamp = 0
        if self.etime is not None:
            timestamp = RedisModel.pydate_to_dbtimestamp(self.etime)
        pipe.zadd(RaidHelpSet.makeKey(self.uid), self.raidhelpid, int(timestamp))
    def _delete(self, pipe):
        pipe.zrem(RaidHelpSet.makeKey(self.uid), self.raidhelpid)

class RaidHelpFriendData(RedisModel):
    """レイドで呼ぶフレンド.
    """
    KEY = 'RaidHelpFriendData'
    
    uid = None
    raidid = None
    
    # カードのステータスも保持しておく.
    card = None
    
    @classmethod
    def create(cls, uid, raidid=0, card=None):
        ins = cls()
        ins.uid = uid
        ins.raidid = raidid
        ins.card = card
        return ins
    
    @classmethod
    def exists(cls, uid):
        redisdb = RedisModel.getDB()
        jsonstr = redisdb.hget(RaidHelpFriendData.KEY, uid)
        return bool(jsonstr)
    
    @classmethod
    def get(cls, uid):
        """ユーザー指定で取得.
        """
        redisdb = RedisModel.getDB()
        jsonstr = redisdb.hget(RaidHelpFriendData.KEY, uid)
        data = None
        if jsonstr:
            try:
                data = Json.decode(jsonstr)
            except:
                pass
        if not data:
            return None
        
        cardid = data.get('cardid')
        card = None
        if cardid:
            card = Card()
            card.id = data.get('cardid')
            card.uid = data.get('uid')
            card.mid = data.get('mid')
            card.level = data.get('level')
            card.skilllevel = data.get('skilllevel')
            card.takeover = data.get('takeover')
        
        return RaidHelpFriendData.create(uid, data.get('raidid'), card)
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.raidid is None:
            return 'raidid is None.'
        return None
    
    def _save(self, pipe):
        data = {
            'raidid' : self.raidid,
        }
        if self.card:
            data.update({
                'cardid' : self.card.id,
                'uid' : self.card.uid,
                'mid' : self.card.mid,
                'level' : self.card.level,
                'skilllevel' : self.card.skilllevel,
                'takeover' : self.card.takeover,
            })
        jsonstr = Json.encode(data)
        pipe.hset(RaidHelpFriendData.KEY, self.uid, jsonstr)
    
    def _delete(self, pipe):
        pipe.hdel(RaidHelpFriendData.KEY, self.uid)

class RaidCallFriendTime(RedisModel):
    """レイドでフレンドを呼んだ時間.
    """
    KEY = 'RaidCallFriendTime'
    
    uid = None
    helptime = None
    
    @classmethod
    def create(cls, uid, helptime=None):
        ins = cls()
        ins.uid = RedisModel.value_to_int(uid)
        ins.helptime = helptime
        return ins
    
    @classmethod
    def get(cls, uid):
        redisdb = RedisModel.getDB()
        helptime = redisdb.hget(RaidCallFriendTime.KEY, uid)
        if helptime is None:
            return None
        else:
            return RaidCallFriendTime.create(uid, RedisModel.dbtimestamp_to_pydate(helptime))
    
    @classmethod
    def exists(cls, uid):
        return cls.get(uid) is not None
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.helptime is None:
            return 'helptime is None.'
        return None
    
    def _save(self, pipe):
        timestamp = RedisModel.pydate_to_dbtimestamp(self.helptime)
        pipe.hset(RaidCallFriendTime.KEY, self.uid, int(timestamp))
    
    def _delete(self, pipe):
        pipe.hdel(RaidCallFriendTime.KEY, self.uid)

class RaidLogListSet(GameLogListBase):
    """レイド履歴.
    """
    @classmethod
    def get_modelclass(cls):
        return RaidLog
    
    @staticmethod
    def get_num(uid):
        redisdb = RedisModel.getDB()
        key = RaidLogListSet.makeKey(uid)
        if not redisdb.exists(key):
            return None
        return redisdb.zcard(key)

class RaidLogNotificationSet(RedisModel):
    """レイド討伐通知.
    """
    KEY_BASE = 'RaidLogNotificationSet%s'
    
    uid = None
    raidlogid = None
    ctime = None
    
    @classmethod
    def makeKey(cls, uid):
        return cls.KEY_BASE % uid
    
    @classmethod
    def create(cls, uid, raidlogid, ctime=None):
        ins = cls()
        ins.uid = uid
        ins.raidlogid = raidlogid
        ins.ctime = ctime or OSAUtil.get_now()
        return ins
    
    @classmethod
    def exists(cls, uid):
        redisdb = RedisModel.getDB()
        return redisdb.exists(cls.makeKey(uid))
    
    @classmethod
    def fetch(cls, uid, limit=10, offset=0):
        """ユーザー指定で取得.
        """
        redisdb = RedisModel.getDB()
        key = cls.makeKey(uid)
        raidlogidlist = redisdb.zrange(key, offset, offset + limit - 1)
        arr = []
        for raidlogid in raidlogidlist:
            v = RedisModel.value_to_int(raidlogid) or raidlogid
            arr.append(v)
        return arr
    
    @classmethod
    def get_num(cls, uid):
        """通知数を取得.
        """
        redisdb = RedisModel.getDB()
        key = cls.makeKey(uid)
        return redisdb.zcard(key)
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.raidlogid is None:
            return 'raidlogid is None.'
        elif self.ctime is None:
            return 'ctime is None.'
        return None
    
    def _save(self, pipe):
        key = RaidLogNotificationSet.makeKey(self.uid)
        pipe.zadd(key, self.raidlogid, RedisModel.pydate_to_dbtimestamp(self.ctime))
    
    def _delete(self, pipe):
        key = RaidLogNotificationSet.makeKey(self.uid)
        pipe.zrem(key, self.raidlogid)

class TreasureListSet(RedisModel):
    """宝箱一覧.
    """
    KEY_BASE = 'TreasureListSet:%d:%d'
    
    uid = None
    treasuretype = None
    treasureid = None
    ctime = None
    
    @classmethod
    def create(cls, uid, treasuretype, treasureid=None, ctime=None):
        ins = cls()
        ins.uid = RedisModel.value_to_int(uid)
        ins.treasuretype = RedisModel.value_to_int(treasuretype)
        ins.treasureid = RedisModel.value_to_int(treasureid)
        ins.ctime = ctime
        return ins
    
    @classmethod
    def makeKey(cls, uid, treasuretype):
        return cls.KEY_BASE % (uid, treasuretype)
    @property
    def key(self):
        return self.makeKey(self.uid, self.treasuretype)
    
    @classmethod
    def fetch(cls, uid, treasuretype, offset=0, limit=None):
        if not cls.exists(uid, treasuretype):
            return []
        
        redisdb = RedisModel.getDB()
        
        key = cls.makeKey(uid, treasuretype)
        start = offset
        end = -1
        if limit and 0 < limit:
            end = start + limit - 1
        return [cls.create(uid, treasuretype, treasureid) for treasureid in redisdb.zrange(key, start, end)]
    
    @classmethod
    def exists(cls, uid, treasuretype):
        redisdb = RedisModel.getDB()
        return redisdb.exists(cls.makeKey(uid, treasuretype))
    
    @classmethod
    def get_num(cls, uid, treasuretype):
        if cls.exists(uid, treasuretype):
            redisdb = RedisModel.getDB()
            return redisdb.zcard(cls.makeKey(uid, treasuretype))
        else:
            return None
    
    def validate(self):
        if self.uid is None:
            return 'uid is None.'
        elif self.treasuretype is None:
            return 'treasuretype is None.'
        elif self.treasureid is None:
            return 'treasureid is None.'
        elif self.ctime is None:
            return 'ctime is None.'
        return None
    
    def _save(self, pipe):
        timestamp = RedisModel.pydate_to_dbtimestamp(self.ctime)
        pipe.zadd(self.key, self.treasureid, int(timestamp))
    
    def _delete(self, pipe):
        pipe.zrem(self.key, self.treasureid)

class MemoriesSession(RedisModel):
    """思い出アルバムのセッション.
    """
    KEY_BASE = 'MemoriesSession:%s'
    
    session = None
    uid = None
    mid = None
    ttl = None
    
    @classmethod
    def create(cls, uid, mid, session, ttl=86400):
        ins = cls()
        ins.session = session
        ins.uid = RedisModel.value_to_int(uid)
        ins.mid = RedisModel.value_to_int(mid)
        ins.ttl = ttl
        return ins
    
    @classmethod
    def makeKey(cls, session):
        return cls.KEY_BASE % session
    
    @staticmethod
    def get(session):
        redisdb = RedisModel.getDB()
        key = MemoriesSession.makeKey(session)
        v = RedisModel.value_to_int(redisdb.get(key))
        if v:
            uid = int(v >> 32)
            mid = int(v & 0xffffffff)
            return MemoriesSession.create(uid, mid, session)
        else:
            return None
    
    def _save(self, pipe):
        key = MemoriesSession.makeKey(self.session)
        v = (self.uid << 32) + self.mid
        pipe.set(key, v)
        # 有効期限もつけておく.
        if 0 < self.ttl:
            pipe.expire(key, self.ttl)
    
    def _delete(self, pipe):
        key = MemoriesSession.makeKey(self.session)
        pipe.delete(key)

#=============================================================
# イベント.
class RankingSetBase(RedisModel):
    """ランキング.
    """
    rankingid = None
    uid = None
    score = None
    
    @classmethod
    def makeKey(cls, rankingid):
        return '%s##%s' % (cls.__name__, rankingid)
    
    @classmethod
    def create(cls, rankingid, uid, score):
        ins = cls()
        ins.rankingid = RedisModel.value_to_int(rankingid)
        ins.uid = RedisModel.value_to_int(uid)
        ins.score = RedisModel.value_to_int(score)
        return ins
    
    @classmethod
    def saveScore(cls, rankingid, uid, score, pipe=None):
        """スコアを保存.
        """
        cls.create(rankingid, uid, score).save(pipe)
    
    @classmethod
    def getScore(cls, rankingid, uid):
        """スコアを取得.
        """
        redisdb = RedisModel.getDB()
        key = cls.makeKey(rankingid)
        return RedisModel.value_to_int(redisdb.zscore(key, uid))
    
    @classmethod
    def getRank(cls, rankingid, uid):
        """順位を取得.
        """
        score = cls.getScore(rankingid, uid)
        return cls.getRankByScore(rankingid, score)
    
    @classmethod
    def getRankByScore(cls, rankingid, score):
        """スコアから順位を取得.
        """
        if not score:
            return None
        # 自分よりスコアが多い人数+1.
        redisdb = RedisModel.getDB()
        key = cls.makeKey(rankingid)
        higher_num = redisdb.zcount(key, score+1, '+inf') or 0
        return higher_num + 1
    
    @classmethod
    def getCountByScore(cls, rankingid, score):
        """同じスコアの人数を取得.
        """
        if not score:
            return None
        # 自分よりスコアが多い人数+1.
        redisdb = RedisModel.getDB()
        key = cls.makeKey(rankingid)
        num = redisdb.zcount(key, score, score) or 0
        return num
    
    @classmethod
    def getIndex(cls, rankingid, uid):
        """順位ではなくインデクスを取得.
        """
        redisdb = RedisModel.getDB()
        key = cls.makeKey(rankingid)
        return redisdb.zrevrank(key, uid)
    
    @classmethod
    def getRankerNum(cls, rankingid):
        """ランキング登録者数.
        """
        redisdb = RedisModel.getDB()
        key = cls.makeKey(rankingid)
        return redisdb.zcard(key)
    
    @classmethod
    def fetch(cls, rankingid, offset, limit):
        """範囲取得.
        """
        redisdb = RedisModel.getDB()
        key = cls.makeKey(rankingid)
        data = redisdb.zrevrange(key, offset, offset+limit-1, True, RedisModel.value_to_int)
        return [(RedisModel.value_to_int(uid), score) for uid,score in data if score is not None]
    
    @classmethod
    def fetchByRank(cls, rankingid, rank, zero=True):
        """順位からユーザーを取得.
        """
        redisdb = RedisModel.getDB()
        key = cls.makeKey(rankingid)
        
        offset = rank - 1
        arr = cls.fetch(rankingid, offset, 1)
        if not arr:
            return []
        
        _, score = arr[0]
        if score < 1 and not zero:
            # スコア0は対象にしない.
            return []
        
        tmprank = cls.getRankByScore(rankingid, score)
        if rank != tmprank:
            # この順位はいない.
            return []
        
        # 同じ順位の人数.
        num = redisdb.zcount(key, score, score)
        if num == 1:
            return arr
        
        return cls.fetch(rankingid, offset, num)
    
    def _save(self, pipe):
        pipe.zadd(self.__class__.makeKey(self.rankingid), self.uid, self.score)
    
    def _delete(self, pipe):
        pipe.zrem(self.__class__.makeKey(self.rankingid), self.uid)

class RaidEventRanking(RankingSetBase):
    """レイドイベントのランキングデータ.
    """

class RaidEventRankingBeginer(RankingSetBase):
    """レイドイベントの新店舗ランキングデータ.
    """

class ScoutEventRanking(RankingSetBase):
    """スカウトイベントのランキングデータ.
    """

class ScoutEventRankingBeginer(RankingSetBase):
    """スカウトイベントの新店舗ランキングデータ.
    """

class BattleEventRanking(RankingSetBase):
    """バトルイベントのランキングデータ.
    """

class BattleEventRankingBeginer(RankingSetBase):
    """バトルイベントの新店舗ランキングデータ.
    """

class BattleEventDailyRanking(RankingSetBase):
    """バトルイベントの日別ランキングデータ.
    """
    @classmethod
    def makeRankingId(cls, logintime, eventid, rank):
        return '%s#%s#%s' % (eventid, rank, logintime.strftime('%Y%m%d'))

class ProduceEventRanking(RankingSetBase):
    """プロデュースイベントのランキングデータ.
    """

    @classmethod
    def exists(cls, eventid):
        redisdb = cls.getDB()
        return redisdb.exists(cls.makeKey(eventid))

class RankingGachaSingleRanking(RankingSetBase):
    """単発ランキングガチャポイントのランキングデータ.
    """

class RankingGachaTotalRanking(RankingSetBase):
    """累計ランキングガチャポイントのランキングデータ.
    """

class SubProcessPid(RedisModel):
    """pid管理.
    """
    name = None
    pid = None
    
    @classmethod
    def create(cls, name, pid):
        ins = cls()
        ins.name = name
        ins.pid = RedisModel.value_to_int(pid)
        return ins
    
    @classmethod
    def get(cls, name):
        redisdb = RedisModel.getDB()
        key = cls.__name__
        pid = redisdb.hget(key, name)
        model = None
        if pid is not None:
            model = cls.create(name, pid)
            try:
                os.kill(model.pid, 0)
            except:
                # 終了済み.
                model = None
        return model
    
    @classmethod
    def exists(cls, name):
        return cls.get(name) is not None
    
    def validate(self):
        if self.name is None:
            return 'name is None.'
        elif self.pid is None:
            return 'pid is None.'
        return None
    
    def _save(self, pipe):
        pipe.hset(self.__class__.__name__, self.name, self.pid)
    
    def _delete(self, pipe):
        pipe.hdel(self.__class__.__name__, self.name)


class ScoutFlag(RedisModel):
    """スカウトのフラグ
    """
    uid = None
    flag = None

    @classmethod
    def create(cls, uid, flag):
        ins = cls()
        ins.uid = RedisModel.value_to_int(uid)
        ins.flag = RedisModel.value_to_int(flag)
        return ins

    @classmethod
    def get(cls, uid):
        redisdb = RedisModel.getDB()
        key = cls.__name__
        flag = RedisModel.value_to_int(redisdb.hget(key, uid))
        return cls.create(uid, flag)

    @classmethod
    def set(cls, uid, flag, pipe=None):
        model = cls.create(uid, flag)
        if model.flag:
            model.save(pipe)
        else:
            model.delete(pipe)
        return model

    def _save(self, pipe):
        pipe.hset(self.__class__.__name__, self.uid, bool(self.flag))

    def _delete(self, pipe):
        pipe.hdel(self.__class__.__name__, self.uid)


class ScoutSkipFlag(RedisModel):
    """スカウト演出スキップフラグ.
    """
    uid = None
    flag = None
    
    @classmethod
    def create(cls, uid, flag):
        ins = cls()
        ins.uid = RedisModel.value_to_int(uid)
        ins.flag = RedisModel.value_to_int(flag)
        return ins
    
    @classmethod
    def get(cls, uid):
        redisdb = RedisModel.getDB()
        key = cls.__name__
        flag = RedisModel.value_to_int(redisdb.hget(key, uid))
        return cls.create(uid, flag)
    
    @classmethod
    def set(cls, uid, flag, pipe=None):
        model = cls.create(uid, flag)
        if model.flag:
            model.save(pipe)
        else:
            model.delete(pipe)
        return model
    
    def _save(self, pipe):
        pipe.hset(self.__class__.__name__, self.uid, bool(self.flag))
    
    def _delete(self, pipe):
        pipe.hdel(self.__class__.__name__, self.uid)


class ScoutSearchFlag(ScoutFlag):
    """全力探索フラグ"""

class PlayerLastHappeningType(RedisModel):
    """ユーザごとの最後に発生したハプニングの種別.
    """
    uid = None
    htype = None
    
    @classmethod
    def create(cls, uid, htype):
        ins = cls()
        ins.uid = RedisModel.value_to_int(uid)
        ins.htype = htype
        return ins
    
    @classmethod
    def createFromScout(cls, uid):
        return cls.create(uid, 'scout')
    
    @classmethod
    def createFromScoutEvent(cls, uid):
        return cls.create(uid, 'scoutevent')
    
    @classmethod
    def createFromRaidEventScout(cls, uid):
        return cls.create(uid, 'raideventscout')

    @classmethod
    def createFromProduceEventScout(cls, uid):
        return cls.create(uid, 'produceeventscout')
    
    @classmethod
    def get(cls, uid):
        redisdb = cls.getDB()
        key = cls.__name__
        htype = redisdb.hget(key, uid)
        if htype:
            return cls.create(uid, htype)
        else:
            return None
    
    def _save(self, pipe):
        pipe.hset(self.__class__.__name__, self.uid, self.htype)
    
    def _delete(self, pipe):
        pipe.hdel(self.__class__.__name__, self.uid)
    
    @property
    def is_scout(self):
        return self.htype == 'scout'
    
    @property
    def is_scoutevent(self):
        return self.htype == 'scoutevent'

class PlayerConfigData(RedisModel):
    """ユーザのコンフィグ情報.
    """
    uid = None
    data = None
    
    @classmethod
    def create(cls, uid, data=None):
        ins = cls()
        ins.uid = RedisModel.value_to_int(uid)
        ins.data = data or {}
        return ins
    
    @classmethod
    def makeKey(cls, uid):
        return '%s:%s' % (cls.__name__, uid)
    
    @classmethod
    def get(cls, uid):
        redisdb = cls.getDB()
        key = cls.makeKey(uid)
        data = redisdb.hgetall(key)
        return cls.create(uid, data)
    
    def _save(self, pipe):
        if self.data:
            pipe.hmset(self.makeKey(self.uid), self.data)
    
    def _delete(self, pipe):
        pipe.delete(self.makeKey(self.uid))
    
    def setData(self, autosell):
        self.data.update({
            'autosell' : autosell,
        })
    
    @property
    def autosell_rarity(self):
        autosell = str(self.data.get('autosell'))
        autosell = int(autosell) if autosell.isdigit() else -1
        if not autosell in Defines.Rarity.AUTO_SELL:
            autosell = -1
        return autosell

class LoginBonusFixationDataHash(RedisModel):
    """日付別ログインボーナスの受取り情報.
    演出表示用.サポート用の履歴はMySQLのUserLogにある.
    31日経過で揮発.
    key:
        ユーザID+マスターID
    name:
        日付(日)
    value:
        受け取った時間(%Y%m%d%H%M%S)
    """
    TTL = 31 * 86400
    DT_DORMAT = "%Y%m%d%H%M%S"
    uid = None
    mid = None
    day = None
    ltime = None
    
    @classmethod
    def create(cls, uid, mid, day, ltime=None):
        ins = cls()
        ins.uid = RedisModel.value_to_int(uid)
        ins.mid = RedisModel.value_to_int(mid)
        ins.day = RedisModel.value_to_int(day)
        ins.ltime = ltime or OSAUtil.get_now()
        return ins
    
    @classmethod
    def makeKey(cls, uid, mid):
        return '%s:%s:%s' % (cls.__name__, uid, mid)
    
    @classmethod
    def fetchAll(cls, uid, mid, min_time=None):
        redisdb = cls.getDB()
        key = cls.makeKey(uid, mid)
        data = redisdb.hgetall(key) or {}
        dest = {}
        for k,v in data.items():
            model = cls.create(uid, mid, k, DateTimeUtil.strToDateTime(v, cls.DT_DORMAT))
            if min_time and model.ltime < min_time:
                continue
            dest[model.day] = model
        return dest
    
    def _save(self, pipe):
        key = self.makeKey(self.uid, self.mid)
        pipe.hmset(key, {self.day:self.ltime.strftime(self.DT_DORMAT)})
        self.set_ttl(key, sec=self.TTL, pipe=pipe)
    
    def _delete(self, pipe):
        key = self.makeKey(self.uid, self.mid)
        pipe.delete(key)

class PopupResetTime(RedisModel):
    """ポップアップの閲覧のリセット時間.
    """
    DT_DORMAT = "%Y%m%d%H%M%S"
    rtime = None
    
    @classmethod
    def create(cls, rtime=None):
        ins = cls()
        ins.rtime = rtime or OSAUtil.get_datetime_min()
        return ins
    
    @classmethod
    def makeKey(cls):
        return cls.__name__
    
    @classmethod
    def get(cls):
        redisdb = cls.getDB()
        key = cls.makeKey()
        str_date = redisdb.get(key)
        rtime = DateTimeUtil.strToDateTime(str_date, cls.DT_DORMAT) if str_date else OSAUtil.get_datetime_min()
        model = cls.create(rtime)
        return model
    
    def _save(self, pipe):
        key = self.makeKey()
        pipe.set(key, self.rtime.strftime(self.DT_DORMAT))
    
    def _delete(self, pipe):
        key = self.makeKey(self.uid)
        pipe.delete(key)

class PopupViewTime(RedisModel):
    """ポップアップの閲覧時間.
    """
    TTL = 1 * 86400
    DT_DORMAT = "%Y%m%d%H%M%S"
    uid = None
    midlist = None
    vtime = None
    
    @classmethod
    def create(cls, uid, midlist=None, vtime=None):
        ins = cls()
        ins.uid = RedisModel.value_to_int(uid)
        ins.midlist = midlist or []
        ins.vtime = vtime or OSAUtil.get_datetime_min()
        return ins
    
    @classmethod
    def makeKey(cls, uid):
        return '%s:%s' % (cls.__name__, uid)
    
    @classmethod
    def get(cls, uid):
        redisdb = cls.getDB()
        key = cls.makeKey(uid)
        str_data = redisdb.get(key)
        if str_data:
            data = cPickle.loads(str_data)
        else:
            data = {}
        str_date = data.get('vtime')
        vtime = DateTimeUtil.strToDateTime(str_date, cls.DT_DORMAT) if str_date else OSAUtil.get_datetime_min()
        model = cls.create(uid, data.get('midlist'), vtime)
        return model
    
    def _save(self, pipe):
        if not self.midlist:
            return
        
        key = self.makeKey(self.uid)
        data = {
            'midlist' : self.midlist,
            'vtime' : self.vtime.strftime(self.DT_DORMAT),
        }
        pipe.set(key, cPickle.dumps(data))
        self.set_ttl(key, sec=self.TTL, pipe=pipe)
    
    def _delete(self, pipe):
        key = self.makeKey(self.uid)
        pipe.delete(key)
    
    def get_viewed_midlist(self, resettime, lbtime=None):
        """閲覧済みか.
        """
        if self.vtime < resettime:
            return []
        
        lbtime = lbtime or DateTimeUtil.toLoginTime(OSAUtil.get_now())
        if self.vtime < lbtime:
            return []
        else:
            return self.midlist

class CabaClubLastViewedStore(RedisModel):
    """キャバクラ経営で最後に見た店舗ID.
    """
    uid = None
    mid = None
    
    @classmethod
    def create(cls, uid, mid):
        ins = cls()
        ins.uid = uid
        ins.mid = mid
        return ins
    
    @classmethod
    def makeKey(cls, uid):
        return '{}:{}'.format(cls.__name__, uid)
    
    @classmethod
    def get(cls, uid):
        redisdb = cls.getDB()
        key = cls.makeKey(uid)
        mid = int(redisdb.get(key) or 0)
        return CabaClubLastViewedStore.create(uid, mid) if mid else None
    
    def _save(self, pipe):
        key = self.makeKey(self.uid)
        pipe.set(key, self.mid)
    
    def _delete(self, pipe):
        key = self.makeKey(self.uid)
        pipe.delete(key)

class CabaClubRecentlyViewedTime(RedisModel):
    """キャバクラ経営で店舗を最後に見た時間.
    """
    uid = None
    mid = None
    vtime = None
    
    @classmethod
    def create(cls, uid, mid, vtime=None):
        ins = cls()
        ins.uid = uid
        ins.mid = mid
        ins.vtime = vtime
        return ins
    
    @classmethod
    def makeKey(cls, uid):
        return '{}:{}'.format(cls.__name__, uid)
    
    @classmethod
    def get(cls, uid, mid):
        redisdb = cls.getDB()
        key = cls.makeKey(uid)
        str_vtime = redisdb.hget(key, mid) or None
        return CabaClubRecentlyViewedTime.create(uid, mid, DateTimeUtil.strToDateTime(str_vtime)) if str_vtime else None
    
    @classmethod
    def fetch(cls, uid):
        redisdb = cls.getDB()
        key = cls.makeKey(uid)
        data = redisdb.hgetall(key)
        dest = {}
        for str_mid, str_vtime in data.items():
            mid = int(str_mid)
            dest[mid] = CabaClubRecentlyViewedTime.create(uid, mid, DateTimeUtil.strToDateTime(str_vtime))
        return dest
    
    def _save(self, pipe):
        key = self.makeKey(self.uid)
        pipe.hset(key, self.mid, DateTimeUtil.dateTimeToStr(self.vtime))
    
    def _delete(self, pipe):
        key = self.makeKey(self.uid)
        pipe.hdel(key, self.mid)

class CabaClubRanking(RedisModel):
    """キャバクラの週ごとランキング
    """
    eventid = None
    uid = None
    sales = None

    @classmethod
    def create(cls, eventid, uid, sales):
        ins = cls()
        ins.eventid = RedisModel.value_to_int(eventid)
        ins.uid = RedisModel.value_to_int(uid)
        ins.sales = RedisModel.value_to_int(sales)
        return ins

    @classmethod
    def makeKey(cls, eventid):
        # 例: CabaclubRanking##32 - 経営イベント32号のランキング
        return '{}##{}'.format(cls.__name__, eventid)

    @classmethod
    def get(cls, eventid, uid):
        redisdb = cls.getDB()
        key = cls.makeKey(eventid)
        sales = redisdb.hget(key, uid) or None
        return CabaClubRanking.create(eventid, uid, sales) if sales else None

    @classmethod
    def fetch(cls, eventid, max_score, min_score, offset=None, limit=None, withscores=False):
        redisdb = cls.getDB()
        key = cls.makeKey(eventid)
        dest = []
        data = redisdb.zrevrangebyscore(key, max_score, min_score, start=offset, num=limit, withscores=withscores)
        if data:
            dest = []
            for str_uid, str_sales in data:
                dest.append((int(str_uid), int(str_sales)))
        return dest

    @classmethod
    def get_rank(cls, eventid, score):
        redisdb = cls.getDB()
        key = cls.makeKey(eventid)
        str_min = str(score)
        return redisdb.zcount(key, "(" + str_min, '+inf') + 1

    @classmethod
    def get_number_of_players(cls, eventid):
        redisdb = cls.getDB()
        key = cls.makeKey(eventid)
        return redisdb.zcard(key)

    @classmethod
    def get_user_rank_page(cls, eventid, uid, page_num_content):
        redisdb = cls.getDB()
        key = cls.makeKey(eventid)
        user_position = redisdb.zrevrank(key, uid)

        # there is a possibility where the user has no ranking data
        if user_position is None:
            return

        page = user_position / page_num_content
        offset = page * page_num_content

        return CabaClubRanking.get_rankings(eventid, offset, page_num_content, page)

    @classmethod
    def get_rankings(cls, eventid, offset=0, limit=-1, page=0):
        sortedset_players = CabaClubRanking.fetch(eventid=eventid,
                                                  max_score='+inf',
                                                  min_score='0',
                                                  offset=offset,
                                                  limit=limit,
                                                  withscores=True)
        if len(sortedset_players) == 0:
            return None

        rankings = []
        first_sortedset_player = sortedset_players[0]
        current_score = first_sortedset_player[1]
        current_rank = CabaClubRanking.get_rank(eventid=eventid, score=current_score)

        for idx, (uid, score) in enumerate(sortedset_players):
            obj_player = {}
            obj_player['uid'] = uid
            obj_player['sales'] = score
            if current_score != score:
                current_rank = idx + (page * limit) + 1
                current_score = score
            obj_player['rank'] = current_rank
            rankings.append(obj_player)

        return rankings

    @classmethod
    def migrate_ranking_data(cls, from_sorted_set, to_sorted_set):
        redisdb = cls.getDB()
        from_key = cls.makeKey(from_sorted_set)
        to_key = cls.makeKey(to_sorted_set)

        # delete last week's ranking data
        redisdb.delete(to_key)

        # backup this week's ranking data to last week
        redisdb.zunionstore(to_key, [from_key])

    @classmethod
    def exists(cls, eventid):
        redisdb = cls.getDB()
        return redisdb.exists(cls.makeKey(eventid))

    def _save(self, pipe):
        key = self.makeKey(self.eventid)
        pipe.zadd(key, self.uid, self.sales)

    def _delete(self, pipe):
        key = self.makeKey(self.eventid)
        pipe.zrem(key, self.uid)

#=============================================================
def delete_by_user(player):
    """ユーザID指定で削除.
    """
    redisdb = RedisModel.getDB()
    pipe = redisdb.pipeline()
    
    DMMPlayerAssociate.create(player.dmmid, player.id).delete(pipe)
    
    if player.getModel(PlayerExp):
        for levelgroup in Defines.LevelGroup.NAMES.keys():
            LevelGroupSet.create(player.id, levelgroup).delete(pipe)
        for lv in xrange(1, player.level+1):
            LevelSet.create(player.id, lv).delete(pipe)
    
    BattleLevelSet.create(player.id).delete(pipe)
    
    LoginTimeSet.create(player.id).delete(pipe)
    
    delete_card_by_uid(player.id, pipe)
    
    for state in Defines.FriendState.NAMES.keys():
        for friend in FriendListSet.fetch(player.id, state):
            for state in Defines.FriendState.NAMES.keys():
                f = FriendListSet.get(friend.fid, friend.uid, state)
                if f:
                    f.delete(pipe)
            friend.delete(pipe)
    
    FriendAcceptNum.create(player.id).delete(pipe)
    
    FreeGachaLastTime.create(player.id).delete(pipe)
    
    keys = redisdb.keys(RareLogList.makeKey('*'))
    if keys:
        pipe.delete(*keys)
    
    RaidHelpFriendData.create(player.id).delete(pipe)
    RaidCallFriendTime.create(player.id).delete(pipe)
    
    for topic in Defines.PresentTopic.RANGE:
        pipe.delete(PresentIdListSet.makeKey(player.id, topic))
    
    for treasuretype in Defines.TreasureType.NAMES.keys():
        pipe.delete(TreasureListSet.makeKey(player.id, treasuretype))
    
    pipe.delete(PlayerLogListSet.makeKey(player.id))
    
    LastViewArea.create(player.id).delete(pipe)
    
    pipe.delete(RaidHelpSet.makeKey(player.id))
    
    pipe.delete(RaidLogNotificationSet.makeKey(player.id))
    
    PlayerConfigData.create(player.id).delete(pipe)
    
    keys = [LoginBonusFixationDataHash.makeKey(player.id, master.id) for master in LoginBonusTimeLimitedMaster.fetchValues(['id'], filters={'lbtype':Defines.LoginBonusTimeLimitedType.FIXATION}, fetch_deleted=True)]
    pipe.delete(*keys)
    
    PopupViewTime.create(player.id).delete(pipe)
    
    CabaClubLastViewedStore.create(player.id, 0).delete(pipe)
    pipe.delete(CabaClubRecentlyViewedTime.makeKey(player.id))
    
    pipe.execute()
    
    FriendLogList.getDB().delete(FriendLogList.makeKey(player.id))

def delete_card_by_uid(uid, pipe=None):
    """ユーザーのカード情報を削除.
    """
    local_pipe = None
    if not pipe:
        redisdb = RedisModel.getDB()
        local_pipe = redisdb.pipeline()
        pipe = local_pipe
    
    pipe.delete(UserCardIdListSet.makeKey(uid))
    pipe.delete(CardKindListSet.makeKey(uid))
    pipe.delete(EvolutionAlbumHkLevelListSet.makeKey(uid))
    
    if local_pipe:
        local_pipe.execute()

def delete_raidevent(eventid, uid=None, pipe=None):
    """レイドイベント削除.
    """
    local_pipe = None
    if not pipe:
        redisdb = RedisModel.getDB()
        local_pipe = redisdb.pipeline()
        pipe = local_pipe
    
    if uid:
        RaidEventRanking.create(eventid, uid, 0).delete(pipe)
        RaidEventRankingBeginer.create(eventid, uid, 0).delete(pipe)
    else:
        pipe.delete(RaidEventRanking.makeKey(eventid))
        pipe.delete(RaidEventRankingBeginer.makeKey(eventid))
    
    if local_pipe:
        local_pipe.execute()

def delete_scoutevent(eventid, uid=None, pipe=None):
    """スカウトイベント削除.
    """
    local_pipe = None
    if not pipe:
        redisdb = RedisModel.getDB()
        local_pipe = redisdb.pipeline()
        pipe = local_pipe
    
    if uid:
        ScoutEventRanking.create(eventid, uid, 0).delete(pipe)
        ScoutEventRankingBeginer.create(eventid, uid, 0).delete(pipe)
    else:
        pipe.delete(ScoutEventRanking.makeKey(eventid))
        pipe.delete(ScoutEventRankingBeginer.makeKey(eventid))
    
    if local_pipe:
        local_pipe.execute()

def delete_battleevent(eventid, uid=None, pipe=None):
    """バトルイベント削除.
    """
    local_pipe = None
    if not pipe:
        redisdb = RedisModel.getDB()
        local_pipe = redisdb.pipeline()
        pipe = local_pipe
    
    if uid:
        BattleEventRanking.create(eventid, uid, 0).delete(pipe)
        BattleEventRankingBeginer.create(eventid, uid, 0).delete(pipe)
    else:
        pipe.delete(BattleEventRanking.makeKey(eventid))
        pipe.delete(BattleEventRankingBeginer.makeKey(eventid))
    
    if local_pipe:
        local_pipe.execute()
