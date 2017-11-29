# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.models.Player import Player, PlayerLogin
from platinumegg.app.cabaret.util.redisdb import RedisModel, UserCardIdListSet,\
    CardKindListSet, EvolutionAlbumHkLevelListSet,\
    RaidHelpFriendData, FreeGachaLastTime, FriendAcceptNum, RaidCallFriendTime,\
    PresentIdListSet, TreasureListSet, PlayerLogListSet, LastViewArea,\
    RaidHelpSet, RaidLogNotificationSet, PlayerConfigData
import settings
from platinumegg.lib.opensocial.util import OSAUtil
import datetime
from defines import Defines

class Command(BaseCommand):
    """Redis内の不要なデータを消す.
    """
    def handle(self, *args, **options):
        
        uid_max = Player.max_value('id')
        
        now = OSAUtil.get_now()
        bordertime = now - datetime.timedelta(days=30)
        
        redisdb = RedisModel.getDB()
        for i in xrange(0, uid_max):
            uid = uid_max - i
            player_login = PlayerLogin.getByKey(uid, using=settings.DB_READONLY)
            if player_login is None or bordertime <= player_login.ltime:
                continue
            
            pipe = redisdb.pipeline()
            
            pipe.delete(UserCardIdListSet.makeKey(uid))
            pipe.delete(CardKindListSet.makeKey(uid))
            pipe.delete(EvolutionAlbumHkLevelListSet.makeKey(uid))
            
            FriendAcceptNum.create(uid).delete(pipe)
            
            FreeGachaLastTime.create(uid).delete(pipe)
            
            RaidHelpFriendData.create(uid).delete(pipe)
            RaidCallFriendTime.create(uid).delete(pipe)
            
            for topic in Defines.PresentTopic.RANGE:
                pipe.delete(PresentIdListSet.makeKey(uid, topic))
            
            for treasuretype in Defines.TreasureType.NAMES.keys():
                pipe.delete(TreasureListSet.makeKey(uid, treasuretype))
            
            pipe.delete(PlayerLogListSet.makeKey(uid))
            
            LastViewArea.create(uid).delete(pipe)
            
            pipe.delete(RaidHelpSet.makeKey(uid))
            
            pipe.delete(RaidLogNotificationSet.makeKey(uid))
            
            PlayerConfigData.create(uid).delete(pipe)
            
            pipe.execute()
            
            print '%s..DELETE' % uid
        
        print '================================'
        print 'all done'
