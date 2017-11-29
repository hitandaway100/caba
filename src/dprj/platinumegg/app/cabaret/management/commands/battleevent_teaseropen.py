# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
import datetime
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.redisdb import BattleEventRanking,\
    BattleEventDailyRanking, BattleEventRankingBeginer
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventRank,\
    BattleEventGroup, BattleEventRankMaster, BattleEventGroupLog,\
    BattleEventFlags, BattleEventScore, BattleEventRevenge, BattleEventBattleLog,\
    BattleEventGroupRankingPrize, BattleEventScorePerRank
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.redisbattleevent import RedisBattleEvent
from platinumegg.app.cabaret.models.base.queryset import Query
from platinumegg.app.cabaret.models.UserLog import UserLogBattleEventPresent
from platinumegg.app.cabaret.models.battleevent.BattleEventPresent import BattleEventPresentCounts,\
    BattleEventPresentData

class Command(BaseCommand):
    """バトルイベントティザー公開準備コマンド.
    """
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'battleevent_teaseropen'
        print '================================'
        
        now = OSAUtil.get_now()
        
        model_mgr = ModelRequestMgr()
        # メンテナンス確認.
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return
        print 'check maintenance...OK'
        
        config = BackendApi.get_current_battleeventconfig(model_mgr)
        if config.mid == 0:
            print 'Event is not set.'
            return
        elif config.starttime <= now:
            print 'Event has already beguns.'
            return
        eventmaster = BackendApi.get_battleevent_master(model_mgr, config.mid, using=settings.DB_READONLY)
        if eventmaster is None:
            print 'Event is not found.'
            return
        print 'check eventmaster...OK'
        
        rankmaster_dict = dict([(master.rank, master) for master in BattleEventRankMaster.fetchValues(filters={'eventid':config.mid}, fetch_deleted=True, using=settings.DB_READONLY)])
        eventrankmaster = rankmaster_dict.get(eventmaster.rankstart)
        if eventrankmaster is None:
            print 'BattleEventMaster.rankstart is not set.'
            return
        print 'check eventrankmaster...OK'
        
        print '================================'
        print 'delete battleeventdata.'
        # Redisのバトルイベント関係を削除.
        RedisBattleEvent.getDB().flushdb()
        print 'delete...redis'
        
        BattleEventRanking.getDB().delete(BattleEventRanking.makeKey(eventmaster.id))
        BattleEventRanking.getDB().delete(BattleEventRankingBeginer.makeKey(eventmaster.id))
        print 'delete...ranking'
        
        tmp_time = config.starttime
        while tmp_time < config.endtime:
            keys = [BattleEventDailyRanking.makeKey(BattleEventDailyRanking.makeRankingId(tmp_time, eventmaster.id, rankmaster.rank)) for rankmaster in rankmaster_dict.values()]
            BattleEventDailyRanking.getDB().delete(*keys)
            tmp_time += datetime.timedelta(days=1)
        print 'delete...daily_ranking'
        
        delete_target_model_cls_list = (
            BattleEventFlags,
            BattleEventRank,
            BattleEventScore,
            BattleEventGroup,
            BattleEventGroupLog,
            BattleEventRevenge,
            BattleEventBattleLog,
            BattleEventGroupRankingPrize,
            BattleEventScorePerRank,
            BattleEventPresentData,
            BattleEventPresentCounts,
            UserLogBattleEventPresent,
        )
        def tr():
            for model_cls in delete_target_model_cls_list:
                tablename = model_cls.get_tablename()
                query_string = "truncate table `%s`;" % tablename
                Query.execute_update(query_string, [], False)
                print 'delete...%s' % tablename
        db_util.run_in_transaction(tr)
        
        OSAUtil.get_cache_client().flush()
