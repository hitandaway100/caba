# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.util.redisdb import RedisModel, FriendListSet
from platinumegg.app.cabaret.util.api import BackendApi
from defines import Defines
from platinumegg.app.cabaret.models.Friend import Friend

class Command(BaseCommand):
    """Redis内のフレンド一覧を作りなおす.
    """
    def handle(self, *args, **options):
        redisdb = RedisModel.getDB()
        
        uid_max = Player.max_value('id')
        for i in xrange(0, uid_max):
            uid = uid_max - i
            
            changed = False
            for state in Defines.FriendState.NAMES.keys():
                friendlist = Friend.fetchValues(filters={'uid':uid,'state':state})
                cur_num = BackendApi._get_friend_num(uid, state)
                if cur_num == len(friendlist):
                    continue
                
                pipe = redisdb.pipeline()
                pipe.delete(FriendListSet.makeKey(uid, state))
                for friend in friendlist:
                    FriendListSet.create(uid, friend.fid, state, friend.ctime).save(pipe)
                pipe.execute()
                changed = True
            if changed:
                print '%s' % uid
        
        print '================================'
        print 'all done'
