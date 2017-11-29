# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.util.api import BackendApi
from defines import Defines
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Friend import Friend

class Command(BaseCommand):
    """フレンドリストをとり直す.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'reload_friendlist'
        print '================================'
        
        uid_max = Player.max_value('id')
        
        for uid in xrange(1, uid_max+1):
            if Friend.getValues(filters={'uid':uid}, using=settings.DB_READONLY) is None:
                print '%s..none' % uid
                continue
            
            for state in Defines.FriendState.NAMES.keys():
                BackendApi._save_friendidlist(uid, state, ModelRequestMgr(), using=settings.DB_READONLY)
            
            print '%s..end' % uid
        
        print '================================'
        print 'all done'
