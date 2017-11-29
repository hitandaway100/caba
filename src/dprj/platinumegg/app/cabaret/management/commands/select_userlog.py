# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
from platinumegg.app.cabaret.models.UserLog import *
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.models.Player import Player

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Command(BaseCommand):
    """お詫びを一括配布.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'select_userlog'
        print '================================'
        
        target = args[0]
        model_cls = self.getModelClass(target)
        
        str_ctime_min = args[1]
        ctime_min = DateTimeUtil.strToDateTime(str_ctime_min, "%Y-%m-%d %H:%M:%S")
        
        getter = eval(args[2])
        
        LIMIT = 3000
        uid_max = Player.max_value('id', using=backup_db)
        
        for uid in xrange(1, uid_max+1):
            filters = {'uid':uid, 'ctime__gte':ctime_min}
            offset = 0
            num = 0
            while True:
                modellist = model_cls.fetchValues(filters=filters, order_by='ctime', limit=LIMIT, offset=offset, using=backup_db)
                if not modellist:
                    break
                offset += len(modellist)
                
                for model in modellist:
                    num += getter(model)
            if num:
                print '%d,%d' % (uid, num)
        
        print '================================'
        print 'all done..'
    
    def getModelClass(self, name):
        return globals().get(name, None)
