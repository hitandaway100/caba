# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
import datetime
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerTutorial
from platinumegg.app.cabaret.util.redisdb import RedisModel, BattleEventRanking,\
    BattleEventDailyRanking, BattleEventRankingBeginer
from defines import Defines
import random
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventRank,\
    BattleEventGroup, BattleEventRankMaster, BattleEventGroupLog,\
    BattleEventFlags, BattleEventScore, BattleEventRevenge, BattleEventBattleLog,\
    BattleEventGroupRankingPrize
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.redisbattleevent import RedisBattleEvent
from platinumegg.app.cabaret.models.base.queryset import Query
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.battleevent.BattleEventPresent import BattleEventPresentData,\
    BattleEventPresentCounts
from platinumegg.app.cabaret.models.UserLog import UserLogBattleEventPresent

class Command(BaseCommand):
    """バトルイベント開始準備コマンド.
    """
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'battleevent_preparation'
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
        
        # 対象の日付(月).
        logintime = DateTimeUtil.toLoginTime(now)
        cdate = datetime.date(logintime.year, logintime.month, logintime.day)
        print cdate.strftime("Create %Y/%m/%d")
        
        if not eventmaster.is_goukon:
            print '================================'
            print 'delete battleeventdata.'
            # Redisのバトルイベント関係を削除.
            RedisBattleEvent.getDB().flushdb()
            print 'delete...redis'
            
            BattleEventRanking.getDB().delete(BattleEventRanking.makeKey(eventmaster.id))
            BattleEventRankingBeginer.getDB().delete(BattleEventRankingBeginer.makeKey(eventmaster.id))
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
        
        redisdb = RedisModel.getDB()
        
        if eventmaster.is_goukon:
            self.__proc_goukon(model_mgr, redisdb, config, eventmaster, rankmaster_dict, now, logintime, cdate)
        else:
            self.__proc_normal(model_mgr, redisdb, config, eventmaster, rankmaster_dict, now, logintime, cdate)
    
    def __proc_goukon(self, model_mgr, redisdb, config, eventmaster, rankmaster_dict, now, logintime, cdate):
        """合コンイベント.
        ランクのレコードがあったらグループに割り当てる.
        """
        print 'start for goukon'
        
        print '================================'
        print 'check rankmax'
        rank_max = config.getRankMax(now)
        print 'rankmax=%s' % rank_max
        # 初日公開分のランク.
        if rank_max is None:
            rankmaster_list = rankmaster_dict.values()
        else:
            rankmaster_list = [rankmaster for rankmaster in rankmaster_dict.values() if rankmaster.rank <= rank_max]
        if not rankmaster_list:
            print 'rank:all closed'
            return
        
        print '================================'
        print 'allocate start.'
        LIMIT = 1000
        uid_offset = 1
        filters = {
            'mid' : eventmaster.id,
        }
        def tr(uid, target_rank):
            model_mgr = ModelRequestMgr()
            playerexp = BackendApi.get_model(model_mgr, PlayerExp, uid)
            BackendApi.tr_battleevent_regist_group_for_user(model_mgr, config, eventmaster, uid, playerexp.level, rankmaster_list, target_rank=target_rank, skip_matching=True)
            model_mgr.write_all()
            return model_mgr
        
        while True:
            filters.update(uid__gte=uid_offset)
            rankrecordlist = BattleEventRank.fetchValues(filters=filters, order_by='uid', limit=LIMIT)
            if not rankrecordlist:
                break
            
            for rankrecord in rankrecordlist:
                try:
                    db_util.run_in_transaction(tr, rankrecord.uid, rankrecord.rank).write_end()
                    print '%d...OK' % rankrecord.uid
                except CabaretError, err:
                    if err.code == CabaretError.Code.ALREADY_RECEIVED:
                        print '%d...ALREADY' % rankrecord.uid
                    else:
                        print '%d...ERR(%d)' % (rankrecord.uid, err.code)
                except Exception, err:
                    print '%d...ERR(%s)' % err
                uid_offset = max(uid_offset, rankrecord.uid+1)
        
        print '================================'
        print 'save rankuidset.'
        # 対戦相手検索用にチュートリアル完了済みのユーザを全てを仮割り当て.
        BackendApi.save_battleevent_rankuidset_for_goukon(eventmaster.id, rankmaster_list, redisdb, using=settings.DB_DEFAULT)
        
        print '================================'
        print 'all done.'
    
    def __proc_normal(self, model_mgr, redisdb, config, eventmaster, rankmaster_dict, now, logintime, cdate):
        """通常のバトルイベント.
        """
        eventrankmaster = rankmaster_dict.get(eventmaster.rankstart)
        
        print 'start for normal'
        
        print '================================'
        print 'save level.'
        rediskey = "battleevent_preparation"
        redisdb.delete(rediskey)
        
        uid = PlayerExp.max_value('id')
        LIMIT = 500
        while 0 < uid:
            pipe = redisdb.pipeline()
            
            uidlist = range(max(0, uid - LIMIT) + 1, uid + 1)
            playerexplist = PlayerExp.getByKey(uidlist, using=settings.DB_READONLY)
            tutorialend_uid_list = [model.id for model in PlayerTutorial.getByKey(uidlist, using=settings.DB_READONLY) if model.tutorialstate == Defines.TutorialStatus.COMPLETED]
            for playerexp in playerexplist:
                if not playerexp.id in tutorialend_uid_list:
                    continue
                pipe.zadd(rediskey, playerexp.id, playerexp.level)
            
            pipe.execute()
            uid -= LIMIT
        
        print '================================'
        print 'allocate start.'
        data = redisdb.zrevrange(rediskey, 0, 1, withscores=True, score_cast_func=RedisModel.value_to_int)
        if data:
            level = data[0][1]
            groupid = 0
            while 0 < level:
                uidlist = [RedisModel.value_to_int(uid) for uid in redisdb.zrangebyscore(rediskey, level, level) if RedisModel.value_to_int(uid)]
                if uidlist:
                    random.shuffle(uidlist)
                    model_mgr, group = db_util.run_in_transaction(Command.tr_write, groupid, eventmaster, eventrankmaster, uidlist, now)
                    model_mgr.write_end()
                    if group and not group.fixed:
                        groupid = group.id
                    else:
                        groupid = 0
                level -= 1
        
        print '================================'
        print 'save rankuidset.'
        for rankmaster in rankmaster_dict.values():
            print "eventid=%s, rank=%s" % (rankmaster.eventid, rankmaster.rank)
            BackendApi.save_battleevent_rankuidset(rankmaster.eventid, rankmaster.rank)
        
        # 後片付け.
        redisdb.delete(rediskey)
        
        print '================================'
        print 'all done.'
    
    @staticmethod
    def tr_write(groupid, eventmaster, eventrankmaster, uidlist, now):
        """書き込み.
        """
        group = None
        if groupid:
            group = BattleEventGroup.getByKeyForUpdate(groupid)
        
        model_mgr = ModelRequestMgr()
        playerexp_dict = BackendApi.get_model_dict(model_mgr, PlayerExp, uidlist)
        for uid in uidlist:
            if group and group.fixed:
                group = None
            rankrecord = BattleEventRank.makeInstance(BattleEventRank.makeID(uid, eventmaster.id))
            rankrecord.rank_next = eventrankmaster.rank
            rankrecord.rank = rankrecord.rank_next
            rankrecord.fame = 0
            rankrecord.fame_next = 0
            rankrecord.groups = []
            playerexp = playerexp_dict.get(uid)
            level = playerexp.level if playerexp else 1
            group = BackendApi.tr_battleevent_regist_group(model_mgr, eventrankmaster, rankrecord, False, group, level, now)
            print '%s => %s' % (rankrecord.uid, group.id)
        
        model_mgr.write_all()
        return model_mgr, group
