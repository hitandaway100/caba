# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Happening import RaidPrizeDistributeQueue,\
    Happening, Raid
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util import db_util
import settings
import time
from platinumegg.lib.redis.client import Client
from platinumegg.lib.redis import config
from platinumegg.lib.dbg import DbgLogger
import settings_sub
from platinumegg.app.cabaret.util.happening import HappeningSet, RaidBoss
import os

class Command(BaseCommand):
    """レイド報酬を配布する.
    """
    def handle(self, *args, **options):
        
        starttime = OSAUtil.get_now()
        
        print '================================'
        print 'distribute_raidprize'
        print '================================'
        print 'start:%s' % starttime.strftime("%Y-%m-%d %H:%M:%S")
        
        LIMIT_PER_REQUEST = 100
        LOOP_NUM_MAX = 10000
        
        is_daemon = args and args[0] == '1'
        
        # wsgi.pyのタイムスタンプを記録.
        wsgi_py_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../wsgi.py'))
        wsgi_py_timestamp = os.stat(wsgi_py_file).st_mtime
        
        # wsgi.pyのタイムスタンプを確認.
        def check_timestamp():
            return os.stat(wsgi_py_file).st_mtime == wsgi_py_timestamp
        
        # pidの有無.
        def check_pid():
            if not is_daemon:
                return True
            elif os.path.exists('/var/run/distribute_raidprize.pid'):
                return True
            return False
        
        def tr_distribute(queue, happening, raidboss, help_prizelist):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_distribute_raid(model_mgr, queue, happening, raidboss, help_prizelist)
            model_mgr.write_all()
            return model_mgr
        
        model_mgr = ModelRequestMgr()
        client = Client.get(config.REDIS_LOG)
        key = 'distribute_raidprize_last_id'
        prev = str(client.get(key))
        prev = int(prev) if prev.isdigit() else 0
        
        loop = 0
        while loop < LOOP_NUM_MAX:
            if not check_timestamp():
                print 'server is updated!!'
                break
            elif not check_pid():
                print 'process killed!!'
                break
            
            loop += 1
            
            # 報酬のキューを取得.
            queuelist = RaidPrizeDistributeQueue.fetchValues(limit=LIMIT_PER_REQUEST, using=settings.DB_READONLY)
            if not queuelist:
                # ちょっと休憩.
                time.sleep(1)
                continue
            
            queue = queuelist[0]
            if queue.id == prev:
                # 遅延の可能性.
                time.sleep(1)
                continue
            
            delete_only_list = []
            for queue in queuelist:
                if not check_timestamp():
                    break
                elif not check_pid():
                    break
                
                # レイドを取得.
                happeningset = BackendApi.get_happening(model_mgr, queue.raidid, using=settings.DB_READONLY)
                raidboss = None
                help_prizelist = None
                if happeningset:
                    raidboss = BackendApi.get_raid(model_mgr, queue.raidid, using=settings.DB_READONLY, happening_eventvalue=happeningset.happening.event)
                    if not happeningset.happening.is_end():
                        happening = Happening.getByKey(queue.raidid, using=settings.DB_READONLY)
                        if not happening.is_end():
                            DbgLogger.write_error(u'distribute not end...queue=%s' % queue.id)
                            continue
                        happeningset = HappeningSet(happening, happeningset.master)
                        if raidboss:
                            raid = Raid.getByKey(queue.raidid, using=settings.DB_READONLY)
                            if raid:
                                raidboss = RaidBoss(raid, raidboss.master, raidboss.raideventraidmaster)
                    
                    if raidboss:
                        help_prizelist = BackendApi.get_prizelist(model_mgr, raidboss.master.helpprizes)
                if raidboss:
                    # 書き込み.
                    try:
                        db_util.run_in_transaction_custom_retries(0, tr_distribute, queue, happeningset.happening, raidboss, help_prizelist).write_end()
                    except Exception, err:
                        DbgLogger.write_error(u'distribute failure...queue=%s,%s' % (queue.id, err))
                        if settings_sub.IS_DEV:
                            raise
                else:
                    DbgLogger.write_error(u'distribute:raid is not found...raidid=%s' % queue.raidid)
                    delete_only_list.append(queue.id)
                prev = queue.id
            
            if delete_only_list:
                # 削除するだけのものを削除.
                RaidPrizeDistributeQueue.all().filter(id__in=delete_only_list).delete()
        
        client.set(key, prev)
        
        print '================================'
        print 'all end..'
        
        diff = OSAUtil.get_now() - starttime
        sec = diff.days * 86400 + diff.seconds
        print 'time %d.%06d' % (sec, diff.microseconds)
