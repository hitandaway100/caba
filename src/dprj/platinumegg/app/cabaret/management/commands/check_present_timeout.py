# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.models.Present import Present
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.redisdb import RedisModel
import datetime
import settings

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Command(BaseCommand):
    """時間切れのプレゼントを削除する.
    """
    def handle(self, *args, **options):
        
        starttime = OSAUtil.get_now()
        
        print '================================'
        print 'check_present_timeout'
        print '================================'
        
        now = OSAUtil.get_now() - datetime.timedelta(seconds=60)    # 1分間猶予をもたせる.
        presentlist = list(Present.all(using=backup_db).filter(limittime__lt=now).values('id','toid','itype').fetch(100000))
        
        print 'delete target num:%d' % len(presentlist)
        if len(presentlist) == 0:
            # 削除対象がない.
            print '---------------'
            print 'end...'
            return
        
        print 'delete...start'
        # redisから削除.
        redisdb = RedisModel.getDB()
        pipe = redisdb.pipeline()
        
        LIMIT = 500
        presentidlist = []
        for data in presentlist:
            BackendApi.remove_present(data['toid'], data['id'], data['itype'], pipe)
            presentidlist.append(data['id'])
            if LIMIT <= len(presentidlist):
                print 'delete...redis'
                pipe.execute()
                pipe = redisdb.pipeline()
                print 'delete...mysql'
                Present.all().filter(id__in=presentidlist).delete()
                presentidlist = []
                print 'delete...restart'
        
        if presentidlist:
            print 'delete...redis'
            pipe.execute()
            print 'delete...mysql'
            Present.all().filter(id__in=presentidlist).delete()
        
        print 'delete...end'
        
        print '---------------'
        print 'all done.'
        
        diff = OSAUtil.get_now() - starttime
        sec = diff.days * 86400 + diff.seconds
        print 'time %d.%06d' % (sec, diff.microseconds)

