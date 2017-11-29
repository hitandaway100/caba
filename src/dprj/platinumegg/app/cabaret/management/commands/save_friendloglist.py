# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.redisdb import FriendLogList,\
    FriendLogReserveList
from platinumegg.lib.opensocial.util import OSAUtil

class Command(BaseCommand):
    """フレンドの近況を対象ユーザーに配布.
    """
    def checkTime(self):
        """経過時間を確認.
        """
        diff = OSAUtil.get_now() - self.__start
        return diff.seconds <= 300
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'save_friendloglist'
        print '================================'
        
        self.__start = OSAUtil.get_now()
        redisdb = FriendLogList.getDB()
        
        print 'start'
        
        work_num = 0
        create_num = 0
        while self.checkTime():
            model = FriendLogReserveList.pop()
            if model is None:
                if FriendLogReserveList.get_num() < 1:
                    # 全て完了.
                    break
            if model.friendlist:
                pipe = redisdb.pipeline()
                for oid in model.friendlist:
                    model.logmodel.oid = oid
                    model.logmodel.save(pipe)
                pipe.execute()
                create_num += len(model.friendlist)
            work_num += 1
        
        print 'work:%s' % work_num
        print 'create:%s' % create_num
        
        print '================================'
        print 'all done..'
        
        timediff = OSAUtil.get_now() - self.__start
        print 'time=%s' % timediff.seconds
