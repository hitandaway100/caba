# -*- coding: utf-8 -*-
from platinumegg.lib.redis.client import Client
from platinumegg.lib.redis import config
import time
from platinumegg.app.cabaret.models.Infomation import InfomationMaster,\
    TopBannerMaster, EventBannerMaster, PopupMaster
from platinumegg.app.cabaret.models.PlayerLevelExp import PlayerLevelExpMaster
from platinumegg.app.cabaret.models.CardLevelExp import CardLevelExpMster
from platinumegg.app.cabaret.models.Area import AreaMaster
from defines import Defines
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.lib import timezone
import datetime
import cPickle
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventStageMaster


class RedisCache:
    """redisでキャッシュ.
    """
    @staticmethod
    def getDB():
        return Client.get(config.REDIS_CACHE)
    
    @staticmethod
    def pydate_to_dbtimestamp(pydate):
        dbdate = pydate.astimezone(timezone.TZ_DB).replace(tzinfo=None)
        return int(time.mktime(dbdate.timetuple()))
    
    @staticmethod
    def dbtimestamp_to_pydate(timestamp):
        dbdate = datetime.datetime.fromtimestamp(int(float(timestamp)))
        return dbdate.replace(tzinfo=timezone.TZ_DB).astimezone(timezone.TZ_DEFAULT)
    
    @classmethod
    def save(cls, *args, **kwargs):
        redisdb = cls.getDB()
        pipe = redisdb.pipeline()
        ret = cls._save(pipe, *args, **kwargs)
        pipe.execute()
        return ret
    
    @classmethod
    def flush(cls, pipe=None):
        do_execute = False
        if pipe is None:
            redisdb = cls.getDB()
            pipe = redisdb.pipeline()
            do_execute = True
        
        cls._flush(pipe)
        
        if do_execute:
            pipe.execute()
    
    @classmethod
    def exists(cls, *args, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def _save(cls, pipe, *args, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def _flush(cls, pipe):
        """関係するキャッシュを全て削除.
        """
        raise NotImplementedError

class InfomationIdListCacheBase(RedisCache):
    """お知らせのキャッシュ.
    """
    
    @classmethod
    def get_model_class(cls):
        raise NotImplementedError
    
    @classmethod
    def makeKey(cls):
        model_cls = cls.get_model_class()
        return '%s:idlist:cache' % model_cls.__name__
    
    @classmethod
    def exists(cls):
        redisdb = cls.getDB()
        return redisdb.exists(cls.makeKey())
    
    @classmethod
    def _save(cls, pipe, infomations, now):
        cache_endtime = None
        
        # 一度削除.
        cls.flush(pipe)
        
        arr = []
        
        key = cls.makeKey()
        for infomation in infomations:
            if now < infomation.stime:
                cache_endtime = min(cache_endtime or infomation.stime, infomation.stime)
                continue
            cache_endtime = min(cache_endtime or infomation.etime, infomation.etime)
            pipe.zadd(key, str(infomation.id), RedisCache.pydate_to_dbtimestamp(infomation.stime))
            
            arr.append(infomation)
        
        timelimit = 86400*30
        if cache_endtime is not None:
            delta = cache_endtime - now
            timelimit = delta.days * 86400 + delta.seconds
        pipe.expire(key, timelimit)
        
        return arr
    
    @classmethod
    def _flush(cls, pipe):
        pipe.delete(cls.makeKey())
    
    @classmethod
    def fetch(cls, start=0, end=-1):
        redisdb = cls.getDB()
        key = cls.makeKey()
        return redisdb.zrevrange(key, start, end)

class InfomationMasterIdListCache(InfomationIdListCacheBase):
    """お知らせ.
    """
    @classmethod
    def get_model_class(cls):
        return InfomationMaster

class TopBannerMasterIdListCache(InfomationIdListCacheBase):
    """トップページバナー.
    """
    @classmethod
    def get_model_class(cls):
        return TopBannerMaster

class EventBannerMasterIdListCache(InfomationIdListCacheBase):
    """イベントバナー.
    """
    @classmethod
    def get_model_class(cls):
        return EventBannerMaster

class PopupMasterIdListCache(InfomationIdListCacheBase):
    """ポップアップ.
    """
    @classmethod
    def get_model_class(cls):
        return PopupMaster

class LevelExpListCacheBase(RedisCache):
    """レベルと経験値のキャッシュ.
    """
    
    @classmethod
    def get_model_class(cls):
        raise NotImplementedError
    
    @classmethod
    def makeKey(cls):
        model_cls = cls.get_model_class()
        return '%s:idlist:cache' % model_cls.__name__
    
    @classmethod
    def exists(cls):
        redisdb = cls.getDB()
        return redisdb.exists(cls.makeKey())
    
    @classmethod
    def _save(cls, pipe, levelexplist):
        # 一度削除.
        cls.flush(pipe)
        key = cls.makeKey()
        for levelexp in levelexplist:
            pipe.zadd(key, levelexp.level, levelexp.exp)
    
    @classmethod
    def _flush(cls, pipe):
        pipe.delete(cls.makeKey())
    
    @classmethod
    def getByExp(cls, exp):
        redisdb = cls.getDB()
        key = cls.makeKey()
        levellist = redisdb.zrangebyscore(key, 0, exp)
        if len(levellist) == 0:
            level = None
        else:
            level = int(levellist[-1])
        return level
    
    @classmethod
    def maxLevel(cls):
        redisdb = cls.getDB()
        key = cls.makeKey()
        levels = redisdb.zrevrange(key, 0, 0)
        if levels:
            return int(levels[0])
        else:
            return 1

class PlayerLevelExpMasterListCache(LevelExpListCacheBase):
    """プレイヤーのレベルと経験値のキャッシュ.
    """
    @classmethod
    def get_model_class(cls):
        return PlayerLevelExpMaster

class CardLevelExpMsterListCache(LevelExpListCacheBase):
    """カードのレベルと経験値のキャッシュ.
    """
    @classmethod
    def get_model_class(cls):
        return CardLevelExpMster

class AreaScoutListCache(RedisCache):
    """エリアのスカウト一覧のキャッシュ.
    """
    @classmethod
    def makeKey(cls, areaid):
        return 'scoutidlist_by_area:%d' % areaid
    
    @classmethod
    def exists(cls, areaid):
        redisdb = cls.getDB()
        return redisdb.exists(cls.makeKey(areaid))
    
    @classmethod
    def _save(cls, pipe, areaid, scoutidlist):
        # 一度削除.
        key = cls.makeKey(areaid)
        pipe.delete(key)
        for scoutid in scoutidlist:
            pipe.sadd(key, scoutid)
    
    @classmethod
    def _flush(cls, pipe):
        for area in AreaMaster.fetchValues():
            pipe.delete(cls.makeKey(area.id))
    
    @classmethod
    def getScoutIdList(cls, areaid):
        redisdb = cls.getDB()
        key = cls.makeKey(areaid)
        return [int(str_id) for str_id in redisdb.smembers(key)]

class EventAreaStageListCache(RedisCache):
    """イベントエリアのステージ一覧のキャッシュ.
    """
    @classmethod
    def makeKey(cls, eventid, areaid):
        return 'eventstageidlist_by_area:%d:%d' % (eventid, areaid)
    
    @classmethod
    def exists(cls, eventid, areaid):
        redisdb = cls.getDB()
        return redisdb.exists(cls.makeKey(eventid, areaid))
    
    @classmethod
    def _save(cls, pipe, eventid, areaid, stageidlist):
        # 一度削除.
        key = cls.makeKey(eventid, areaid)
        pipe.delete(key)
        for stageid in stageidlist:
            pipe.sadd(key, stageid)
    
    @classmethod
    def _flush(cls, pipe):
        flags = {}
        for stagemaster in [ScoutEventStageMaster.fetchValues()]:
            key = cls.makeKey(stagemaster.eventid, stagemaster.area)
            if not flags.get(key):
                pipe.delete(key)
                flags[key] = True
    
    @classmethod
    def getStageIdList(cls, eventid, areaid):
        redisdb = cls.getDB()
        key = cls.makeKey(eventid, areaid)
        return [int(str_id) for str_id in redisdb.smembers(key)]

class AlbumList(RedisCache):
    """アルバム一覧.
    """
    @classmethod
    def makeKey(cls, ctype, rare):
        return 'albumlist:%s:%s' % (ctype, rare)
    
    @classmethod
    def exists(cls, ctype, rare):
        redisdb = cls.getDB()
        return redisdb.exists(cls.makeKey(ctype, rare))
    
    @classmethod
    def _save(cls, pipe, cardmaster_list):
        for cardmaster in cardmaster_list:
            if cardmaster.hklevel != 1 or cardmaster.ckind != Defines.CardKind.NORMAL:
                continue
            pipe.zadd(AlbumList.makeKey(Defines.CharacterType.ALL, Defines.Rarity.ALL), cardmaster.id, cardmaster.album)
            pipe.zadd(AlbumList.makeKey(Defines.CharacterType.ALL, cardmaster.rare), cardmaster.id, cardmaster.album)
            pipe.zadd(AlbumList.makeKey(cardmaster.ctype, Defines.Rarity.ALL), cardmaster.id, cardmaster.album)
            pipe.zadd(AlbumList.makeKey(cardmaster.ctype, cardmaster.rare), cardmaster.id, cardmaster.album)
    
    @classmethod
    def _flush(cls, pipe):
        """関係するキャッシュを全て削除.
        """
        pipe.delete(AlbumList.makeKey(Defines.CharacterType.ALL, Defines.Rarity.ALL))
        for ctype in Defines.CharacterType.NAMES.keys():
            pipe.delete(AlbumList.makeKey(ctype, Defines.Rarity.ALL))
            for rare in Defines.Rarity.NAMES.keys():
                pipe.delete(AlbumList.makeKey(Defines.CharacterType.ALL, rare))
                pipe.delete(AlbumList.makeKey(ctype, rare))
    
    @classmethod
    def get_cardid_by_albumid(cls, albumid):
        redisdb = cls.getDB()
        key = AlbumList.makeKey(Defines.CharacterType.ALL, Defines.Rarity.ALL)
        arr = redisdb.zrangebyscore(key, albumid, albumid)
        if arr:
            return int(arr[0])
        else:
            return None
    
    @classmethod
    def fetch(cls, ctype=Defines.CharacterType.ALL, rare=Defines.Rarity.ALL, offset=0, limit=-1):
        redisdb = cls.getDB()
        key = AlbumList.makeKey(ctype, rare)
        start = offset
        if limit == -1:
            end = '+inf'
        else:
            end = start + limit - 1
        masteridlist = redisdb.zrange(key, start, end)
        return [int(masterid) for masterid in masteridlist]
    
    @classmethod
    def length(cls, ctype=Defines.CharacterType.ALL, rare=Defines.Rarity.ALL):
        redisdb = cls.getDB()
        key = AlbumList.makeKey(ctype, rare)
        return redisdb.zcard(key)

class AlbumMemoriesSet(RedisCache):
    """思い出アルバム.
    """
    @classmethod
    def makeKey(cls, albumid):
        return 'albummemoriesset:%s' % albumid
    
    @classmethod
    def exists(cls, albumid):
        redisdb = cls.getDB()
        return redisdb.exists(cls.makeKey(albumid))
    
    @classmethod
    def _save(cls, pipe, albumid, memoriesmaster_list):
        key = AlbumMemoriesSet.makeKey(albumid)
        for memoriesmaster in memoriesmaster_list:
            pipe.sadd(key, memoriesmaster.id)
    
    @classmethod
    def _flush(cls, pipe):
        """関係するキャッシュを全て削除.
        """
        masterlist = CardMaster.fetchValues(['albumhklevel'])
        for master in masterlist:
            pipe.delete(AlbumMemoriesSet.makeKey(master.album))
    
    @classmethod
    def fetch(cls, albumid):
        redisdb = cls.getDB()
        key = AlbumMemoriesSet.makeKey(albumid)
        return [int(memoriesid) for memoriesid in redisdb.smembers(key)]

class LoginBonusAnimationSet(RedisCache):
    """ログインボーナス演出用データ.
    """
    KEY = 'LoginBonusAnimationSet'
    
    @classmethod
    def exists(cls, lday):
        return cls.get(lday) is not None
    
    @classmethod
    def _save(cls, pipe, lday, items):
        pipe.hset(LoginBonusAnimationSet.KEY, lday, cPickle.dumps(items))
    
    @classmethod
    def _flush(cls, pipe):
        """関係するキャッシュを全て削除.
        """
        pipe.delete(LoginBonusAnimationSet.KEY)
    
    @classmethod
    def get(cls, lday):
        redisdb = cls.getDB()
        data = redisdb.hget(LoginBonusAnimationSet.KEY, lday)
        items = None
        if data:
            try:
                items = cPickle.loads(data)
            except:
                pass
        return items

class LoginBonusTimeLimitedAnimationSet(RedisCache):
    """ログインボーナス演出用データ.
    """
    KEY = 'LoginBonusTimeLimitedAnimationSet'
    
    @classmethod
    def makeName(cls, mid, lday):
        return '%d##%d' % (mid, lday)
    
    @classmethod
    def exists(cls, mid, lday):
        return cls.get(mid, lday) is not None
    
    @classmethod
    def _save(cls, pipe, mid, lday, items):
        pipe.hset(cls.KEY, cls.makeName(mid, lday), cPickle.dumps(items))
    
    @classmethod
    def _flush(cls, pipe):
        """関係するキャッシュを全て削除.
        """
        pipe.delete(cls.KEY)
    
    @classmethod
    def get(cls, mid, lday):
        redisdb = cls.getDB()
        data = redisdb.hget(cls.KEY, cls.makeName(mid, lday))
        items = None
        if data:
            try:
                items = cPickle.loads(data)
            except:
                pass
        return items

class TotalLoginBonusAnimationSet(RedisCache):
    """累計ログインボーナス演出用データ.
    """
    KEY = 'TotalLoginBonusAnimationSet'
    
    @classmethod
    def makeName(cls, mid, lday):
        return '%d##%d' % (mid, lday)
    
    @classmethod
    def exists(cls, mid, lday):
        return cls.get(mid, lday) is not None
    
    @classmethod
    def _save(cls, pipe, mid, lday, items):
        pipe.hset(cls.KEY, cls.makeName(mid, lday), cPickle.dumps(items))
    
    @classmethod
    def _flush(cls, pipe):
        """関係するキャッシュを全て削除.
        """
        pipe.delete(cls.KEY)
    
    @classmethod
    def get(cls, mid, lday):
        redisdb = cls.getDB()
        data = redisdb.hget(cls.KEY, cls.makeName(mid, lday))
        items = None
        if data:
            try:
                items = cPickle.loads(data)
            except:
                pass
        return items

class GachaBoxCardListInfoSet(RedisCache):
    """ガチャで出現するカードの情報.
    """
    KEY = 'GachaBoxCardListInfoSet'
    
    @classmethod
    def exists(cls, boxid):
        return cls.get(boxid) is not None
    
    @classmethod
    def _save(cls, pipe, boxid, info):
        pipe.hset(cls.KEY, boxid, cPickle.dumps(info))
    
    @classmethod
    def _flush(cls, pipe):
        """関係するキャッシュを全て削除.
        """
        pipe.delete(cls.KEY)
    
    @classmethod
    def get(cls, boxid):
        redisdb = cls.getDB()
        data = redisdb.hget(cls.KEY, boxid)
        info = None
        if data:
            try:
                info = cPickle.loads(data)
            except:
                pass
        return info

class AlbumHkLevelSet(RedisCache):
    """アルバムハメ管理セット.
    """
    KEY = 'AlbumHkLevelSet'
    
    @classmethod
    def exists(cls, album, hklevel):
        return cls.get(album, hklevel) is not None
    
    @classmethod
    def _save(cls, pipe, album, hklevel, mid):
        pipe.hset(cls.KEY, CardMaster.makeAlbumHklevel(album, hklevel), mid)
    
    @classmethod
    def _flush(cls, pipe):
        """関係するキャッシュを全て削除.
        """
        pipe.delete(cls.KEY)
    
    @classmethod
    def get(cls, album, hklevel):
        redisdb = cls.getDB()
        mid = redisdb.hget(cls.KEY, CardMaster.makeAlbumHklevel(album, hklevel))
        if mid and str(mid).isdigit():
            mid = int(mid)
        else:
            mid = None
        return mid

class ScoutEventPresentPrizeNumberList(RedisCache):
    """イベント別ハートプレゼント報酬の通し番号のリスト.
    """
    KEY = 'ScoutEventPresentPrizeNumberList'
    
    @classmethod
    def exists(cls, eventid):
        return cls.get(eventid) is not None
    
    @classmethod
    def _save(cls, pipe, eventid, modellist):
        numberlist = [model.number for model in modellist]
        numberlist.sort()
        data = cPickle.dumps(numberlist)
        pipe.hset(cls.KEY, eventid, data)
    
    @classmethod
    def _flush(cls, pipe):
        """関係するキャッシュを全て削除.
        """
        pipe.delete(cls.KEY)
    
    @classmethod
    def get(cls, eventid):
        redisdb = cls.getDB()
        data = redisdb.hget(cls.KEY, eventid)
        numberlist = None
        if data:
            try:
                numberlist = cPickle.loads(data)
            except:
                pass
        return numberlist

class MoviePlayListUniqueNameSet(RedisCache):
    """動画とユニーク名のセット.
    """
    
    @classmethod
    def makeKey(cls):
        return cls.__name__
    
    @classmethod
    def exists(cls, uniquename):
        return cls.get(uniquename) is not None
    
    @classmethod
    def _save(cls, pipe, masterlist):
        data = dict([(master.filename, master.id) for master in masterlist])
        pipe.hmset(cls.makeKey(), data)
    
    @classmethod
    def _flush(cls, pipe):
        """関係するキャッシュを全て削除.
        """
        pipe.delete(cls.makeKey())
    
    @classmethod
    def get(cls, uniquename):
        redisdb = cls.getDB()
        mid = redisdb.hget(cls.makeKey(), uniquename)
        if mid and str(mid).isdigit():
            mid = int(mid)
        else:
            mid = None
        return mid
    
    @classmethod
    def fetch(cls, uniquename_list):
        redisdb = cls.getDB()
        midlist = redisdb.hmget(cls.makeKey(), uniquename_list)
        result = {}
        for idx, uniquename in enumerate(uniquename_list):
            mid = midlist[idx]
            if mid and str(mid).isdigit():
                mid = int(mid)
            else:
                mid = None
            if mid:
                result[uniquename] = mid
        return result

class MoviePlayListUniqueNameSetSp(MoviePlayListUniqueNameSet):
    """SP版動画とユニーク名のセット.
    """

class MoviePlayListUniqueNameSetPc(MoviePlayListUniqueNameSet):
    """PC版動画とユニーク名のセット.
    """

class RankingGachaWholePrizeQueueIdSet(RedisCache):
    """ランキングガチャの総計pt報酬キューのID.
    name
        id
    value
        id
    """
    
    @classmethod
    def makeKey(cls):
        return cls.__name__
    
    @classmethod
    def exists(cls):
        redisdb = cls.getDB()
        key = cls.makeKey()
        return redisdb.exists(key)
    
    @classmethod
    def __format(cls, pipe):
        key = cls.makeKey()
        pipe.delete(key)
        pipe.zadd(key, 0, 0)
    
    @classmethod
    def _save(cls, pipe, queuelist):
        cls.__format(pipe)
        key = cls.makeKey()
        for queue in queuelist:
            pipe.zadd(key, queue.id, queue.id)
    
    @classmethod
    def _flush(cls, pipe):
        """関係するキャッシュを全て削除.
        """
        pipe.delete(cls.makeKey())
    
    @classmethod
    def add(cls, queueid, pipe=None):
        """関係するキャッシュを全て削除.
        """
        redisdb = pipe or cls.getDB()
        redisdb.zadd(cls.makeKey(), queueid, queueid)
    
    @classmethod
    def fetch(cls, queueid):
        redisdb = cls.getDB()
        key = cls.makeKey()
        str_queueidlist = redisdb.zrangebyscore(key, queueid, "+inf")
        return [int(str_queueid) for str_queueid in str_queueidlist if str_queueid != '0']


class LoginbonusSugorokuMapSquaresIdList(RedisCache):
    """双六ログインボーナスのマップのマス情報.
    """
    
    @classmethod
    def makeKey(cls, mapid):
        return '{}:{}'.format(cls.__name__, mapid)
    
    @classmethod
    def makeKeyListKey(cls):
        return '{}:Keylist'.format(cls.__name__)
    
    @classmethod
    def exists(cls, mapid):
        redisdb = cls.getDB()
        key = cls.makeKey(mapid)
        return redisdb.exists(key)
    
    @classmethod
    def _save(cls, pipe, mapsquarelist):
        table = {}
        keylist_key = cls.makeKeyListKey()
        for mapsquare in mapsquarelist:
            arr = table[mapsquare.mid] = table.get(mapsquare.mid) or []
            arr.append(mapsquare.id)
        for mapid,arr in table.items():
            arr.sort()
            key = cls.makeKey(mapid)
            pipe.set(key, cPickle.dumps(arr))
            pipe.expire(key, 86400)
            pipe.sadd(keylist_key, key)
    
    @classmethod
    def _flush(cls, pipe):
        """関係するキャッシュを全て削除.
        """
        redisdb = cls.getDB()
        keylist_key = cls.makeKeyListKey()
        key_list = redisdb.smembers(keylist_key)
        if key_list:
            pipe.delete(*key_list)
        pipe.delete(keylist_key)
    
    @classmethod
    def get_squares_idlist(cls, mapid):
        redisdb = cls.getDB()
        key = cls.makeKey(mapid)
        str_squares_idlist = redisdb.get(key)
        if str_squares_idlist:
            return cPickle.loads(str_squares_idlist)
        else:
            return []

def flush_all():
    redisdb = RedisCache.getDB()
    redisdb.flushdb()
