# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.lib.opensocial.util import OSAUtil
# from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.redisdb import RedisModel
import datetime
from defines import Defines
from platinumegg.app.cabaret.util.treasure import TreasureUtil
from platinumegg.app.cabaret.util.api import BackendApi
import settings

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Command(BaseCommand):
    """時間切れの宝箱を削除する.
    """
    def handle(self, *args, **options):
        
        starttime = OSAUtil.get_now()
        
        print '================================'
        print 'check_treasure_timeout'
        print '================================'
        
        for treasure_type in Defines.TreasureType.NAMES.keys():
            self.old_delete_record(treasure_type)
        
        diff = OSAUtil.get_now() - starttime
        sec = diff.days * 86400 + diff.seconds
        print 'time %d.%06d' % (sec, diff.microseconds)
    
    def old_delete_record(self, treasure_type):
        
        now = OSAUtil.get_now() - datetime.timedelta(seconds=60)    # 1分間猶予をもたせる.
        
        model_cls = TreasureUtil.get_model_cls(treasure_type)
        treasurelist = list(model_cls.all(using=backup_db).filter(etime__lt=now).values('id', 'uid').fetch(30000))
        print 'delete target num:%d' % len(treasurelist)
        
        if len(treasurelist) == 0:
            # 削除対象がない.
            print '---------------'
            print 'end...'
            return
        
        print 'delete...start'
        # redisから削除.
        redisdb = RedisModel.getDB()
        pipe = redisdb.pipeline()
        
        LIMIT = 500
        treasureidlist = []
        for data in treasurelist:
            BackendApi.remove_treasure(data['uid'], treasure_type, data['id'], pipe)
            treasureidlist.append(data['id'])
            
            if LIMIT <= len(treasureidlist):
                print 'delete from redis'
                pipe.execute()
                pipe = redisdb.pipeline()
                
                print 'delete from mysql'
                model_cls.all().filter(id__in=treasureidlist).delete()
                treasureidlist = []
        
        if treasureidlist:
            print 'delete from redis'
            pipe.execute()
            print 'delete from mysql'
            model_cls.all().filter(id__in=treasureidlist).delete()
        
        print 'delete...end'
        
        print '---------------'
        print 'all done.'
    

