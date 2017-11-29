# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.lib.opensocial.util import OSAUtil
import datetime
from platinumegg.app.cabaret.models.Happening import Happening
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util import db_util
import settings
import time

class Command(BaseCommand):
    """終了したハプニングを削除する.
    """
    def handle(self, *args, **options):
        
        starttime = OSAUtil.get_now()
        
        print '================================'
        print 'delete_finished_happening'
        print '================================'
        
        # 有効期限.
        now = OSAUtil.get_now()
        limittime = now - datetime.timedelta(days=28, seconds=68400)
        
        def tr(happeninglist):
            model_mgr = ModelRequestMgr()
            idlist = []
            for happening in happeninglist:
                BackendApi.tr_delete_happening(model_mgr, happening.id)
                idlist.append(happening.id)
            model_mgr.write_all()
            return model_mgr, idlist
        
        TIMELIMIT = 7100
        LIMIT_PER_LOOP=50
        LOOP = 100000 / LIMIT_PER_LOOP
        del_num = 0
        for _ in xrange(LOOP):
            # 終了したハプニングを取得.
            happeninglist = Happening.fetchValues(['id'], {'etime__lt':limittime}, limit=LIMIT_PER_LOOP, using=settings.DB_DEFAULT)
            if not happeninglist:
                break
            model_mgr, idlist = db_util.run_in_transaction(tr, happeninglist)
            model_mgr.write_end()
            del_num += 1
            print 'delete %d end' % idlist
            
            time.sleep(0.1)
            
            diff = OSAUtil.get_now() - starttime
            sec = diff.days * 86400 + diff.seconds
            if TIMELIMIT <= sec:
                break
        
        print '================================'
        print 'all end..'
        print 'delete num = %d' % del_num
        
        diff = OSAUtil.get_now() - starttime
        sec = diff.days * 86400 + diff.seconds
        print 'time %d.%06d' % (sec, diff.microseconds)
