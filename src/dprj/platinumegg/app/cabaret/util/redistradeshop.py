# -*- coding: utf-8 -*-
from platinumegg.lib.redis.client import Client
from platinumegg.lib.redis import config
from platinumegg.app.cabaret.util.redisdb import RedisModel, GameLogListBase
from platinumegg.app.cabaret.models.Player import PlayerTradeShop

class RedisPlayerTradeShopPoint(RedisModel):
  """PlayerのTradeShopのPoint
  """
  REDIS_KEY = 'playertradeshop_point##{}'
  @classmethod
  def create(cls, uid, value):
    ins = cls()
    ins.key = cls.REDIS_KEY.format(uid)
    ins.value = value
    return ins

  @classmethod
  def get(cls, uid):
    redisdb = RedisModel.getDB()
    return redisdb.get(cls.REDIS_KEY.format(uid))

  def _save(self, pipe=None):
    pipe.delete(self.key)
    pipe.set(self.key, self.value)
    pipe.expire(self.key, 3600)

class RedisTradeShopPlayerTradeCount(RedisModel):
  """プレイヤーのアイテム交換回数.
  """
  REDIS_KEY = 'tradeshoptradecount##{}'
  @classmethod
  def create(cls, tradeshopplayerdataid, value):
    ins = cls()
    ins.key = cls.REDIS_KEY.format(tradeshopplayerdataid)
    ins.value = value
    return ins

  @classmethod
  def get(cls, key):
    redisdb = RedisModel.getDB()
    strnum = redisdb.get(cls.REDIS_KEY.format(key))
    if strnum:
      return int(strnum)
    return None

  def _save(self, pipe=None):
    pipe.delete(self.key)
    pipe.set(self.key, self.value)
    pipe.expire(self.key, 3600)
