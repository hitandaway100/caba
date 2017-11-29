# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.util.api import BackendApi
from defines import Defines
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.redisdb import RedisModel

class Command(BaseCommand):
    """プレゼントをDBからRedisにとり直す.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'reload_presentidlist'
        print '================================'
        
        uid_max = Player.max_value('id')
        redisdb = RedisModel.getDB()
        pipe = redisdb.pipeline()
        model_mgr = ModelRequestMgr()
        
        for uid in xrange(1, uid_max+1):
            BackendApi._save_presentidlist(uid, model_mgr, using=settings.DB_READONLY, pipe=pipe)
            print '%s..end' % uid

        pipe.execute()
        print '================================'
        print 'all done'
