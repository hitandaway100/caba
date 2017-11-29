# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
import datetime
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.redisdb import RedisModel,\
    BattleEventDailyRanking
from platinumegg.app.cabaret.util.redisbattleevent import BattleEventRankUidSet
import random
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventRank,\
    BattleEventGroup, BattleEventRankMaster, BattleEventGroupLog,\
    CurrentBattleEventConfig
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Player import PlayerExp

class Command(BaseCommand):
    """バトルイベント集計コマンド.
    """
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'battleevent_aggregate'
        print '================================'
        
        now = OSAUtil.get_now()
        
        model_mgr = ModelRequestMgr()
        is_battle_open = BackendApi.is_battleevent_battle_open(model_mgr, settings.DB_READONLY, now, do_check_emergency=False)
        
        if is_battle_open:
            # こっちは緊急で修復する場合..
            tomorrow = now
            now = tomorrow - datetime.timedelta(days=1)
        else:
            tomorrow = now + datetime.timedelta(days=1)
        
        config = BackendApi.get_current_battleeventconfig(model_mgr)
        if config.mid == 0:
            print 'イベントが設定されていません.'
            return
        elif now < config.starttime:
            print 'イベントが始まっていません.'
            return
        elif config.endtime <= now:
            print 'イベントが終わっています.'
            return
        elif is_battle_open and not config.is_emergency:
            print 'バトル中です.'
            return
        
        eventmaster = BackendApi.get_battleevent_master(model_mgr, config.mid, using=settings.DB_READONLY)
        if eventmaster is None:
            print 'イベントが見つかりません.'
            return
        print 'check eventmaster...OK'
        
        redisdb = RedisModel.getDB()
        ALREADY_KEY = "battleevent_aggregate:end"
        
        # 対象の日付(月).
        logintime = DateTimeUtil.toLoginTime(tomorrow)
        cdate = datetime.date(logintime.year, logintime.month, logintime.day)
        print cdate.strftime("Create %Y/%m/%d")
        
        str_cdate_pre = redisdb.get(ALREADY_KEY)
        if str_cdate_pre:
            dt = DateTimeUtil.strToDateTime(str_cdate_pre, "%Y%m%d")
            cdate_pre = datetime.date(dt.year, dt.month, dt.day)
            if cdate_pre == cdate:
                print "already..."
                return
        
        rankmaster_dict = dict([(master.id, master) for master in BattleEventRankMaster.fetchValues(filters={'eventid':config.mid}, fetch_deleted=True, using=settings.DB_READONLY)])
        
        print '================================'
        print 'check rankmax'
        rank_max = config.getRankMax(logintime)
        print 'rankmax=%s' % rank_max
        if rank_max is None:
            rankmaster_list = rankmaster_dict.values()
        else:
            rankmaster_list = [rankmaster for rankmaster in rankmaster_dict.values() if rankmaster.rank <= rank_max]
        if not rankmaster_list:
            print 'rank:all closed'
            return
        
        print '================================'
        print 'send groupranking prizes.'
        # 未受け取りのグループ内ランキング報酬を配布.
        BackendApi.battleevent_send_groupranking_prizes(eventmaster)
        
        print '================================'
        print 'reset daily ranking.'
        logintime_today = DateTimeUtil.toLoginTime(now)
        keylist = [BattleEventDailyRanking.makeKey(BattleEventDailyRanking.makeRankingId(logintime_today, config.mid, rankmaster.rank)) for rankmaster in rankmaster_dict.values()]
        if keylist:
            redisdb.delete(*keylist)
        
        offset = 0
        LIMIT = 500
        while True:
            grouplist = BattleEventGroupLog.fetchValues(filters={'eventid':config.mid, 'cdate':datetime.date(logintime_today.year, logintime_today.month, logintime_today.day)}, order_by='id', offset=offset, limit=LIMIT)
            if not grouplist:
                break
            offset += LIMIT
            
            for group in grouplist:
                rankmaster = rankmaster_dict.get(group.rankid)
                rankingid = BattleEventDailyRanking.makeRankingId(logintime_today, config.mid, rankmaster.rank)
                
                pipe = redisdb.pipeline()
                for userdata in group.userdata:
                    if 0 < userdata.point:
                        BattleEventDailyRanking.create(rankingid, userdata.uid, userdata.point).save(pipe)
                pipe.execute()
        
        print '================================'
        print 'close group.'
        while True:
            grouplist = BattleEventGroup.fetchValues(filters={'eventid':config.mid}, order_by='cdate', limit=500)
            if not grouplist or cdate <= grouplist[0].cdate:
                break
            
            for group in grouplist:
                if cdate <= group.cdate:
                    break
                
                eventrankmaster = rankmaster_dict[group.rankid]
                model_mgr = db_util.run_in_transaction(Command.tr_close, eventmaster, eventrankmaster, group.id, now, rank_max)
                model_mgr.write_end()
                
                print 'close %s' % group.id
        
        print '================================'
        print 'send rankingprizes.'
        date_today = datetime.date(logintime_today.year, logintime_today.month, logintime_today.day)
        rankmasterlist = rankmaster_dict.values()
        rankmasterlist.sort(key=lambda x:x.rank)
        for rankmaster in rankmasterlist:
            # 報酬を渡す.
            rankingid = BattleEventDailyRanking.makeRankingId(logintime_today, config.mid, rankmaster.rank)
            rankingprizes = rankmaster.rankingprizes
            textid = rankmaster.rankingprize_text
            
            for idx, data in enumerate(rankingprizes):
                prize_flag = (rankmaster.rank << 16) + idx
                pre_prize_flag = config.getDailyPrizeFlag(date_today)
                if prize_flag < pre_prize_flag:
                    print 'skip...%d' % idx
                    continue
                
                prizeidlist = data['prize']
                rank_min = data['rank_min']
                rank_max = data['rank_max']
                
                prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
                uidlist = []
                
                for rank in xrange(rank_min, rank_max+1):
                    data = BattleEventDailyRanking.fetchByRank(rankingid, rank, zero=False)
                    dic = dict(data)
                    uidlist.extend(dic.keys())
                    if len(set(uidlist)) != len(uidlist):
                        raise CabaretError(u'ランキング取得がなにかおかしい..%d' % rank)
                
                def tr():
                    model_mgr = ModelRequestMgr()
                    config = CurrentBattleEventConfig.getByKeyForUpdate(CurrentBattleEventConfig.SINGLE_ID)
                    if config.getDailyPrizeFlag(date_today) != pre_prize_flag:
                        raise CabaretError(u'整合が取れていないので終了します')
                    for uid in uidlist:
                        BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
                    config.daily_prize_flag = prize_flag + 1
                    config.daily_prize_date = date_today
                    model_mgr.set_save(config)
                    model_mgr.write_all()
                    return model_mgr, config
                try:
                    tmp_model_mgr, wrote_config = db_util.run_in_transaction(tr)
                except CabaretError, err:
                    print 'error...%s' % err.value
                    return
                
                print 'save end...%d' % idx
                
                tmp_model_mgr.write_end()
                print 'cache end...%d' % idx
                
                config = wrote_config
        
        print '================================'
        print 'save rank uid set.'
        if eventmaster.is_goukon:
            # 合コンイベントで新しいランクが増えていたら未参加ユーザーを対戦相手に割り振っておく.
            if rank_max and rank_max != config.getRankMax(logintime-datetime.timedelta(days=1)):
                BackendApi.save_battleevent_rankuidset_for_goukon(eventmaster.id, rankmaster_list, redisdb, using=settings.DB_DEFAULT)
        else:
            for rankmaster in rankmaster_dict.values():
                BackendApi.save_battleevent_rankuidset(rankmaster.eventid, rankmaster.rank)
        
        if not eventmaster.is_goukon:
            # 合コンイベントはグループを作らない.
            print '================================'
            print 'create group.'
            redisbattleevent = BattleEventRankUidSet.getDB()
            for rankmaster in rankmaster_dict.values():
                rediskey = BattleEventRankUidSet.makeKey(rankmaster.eventid, rankmaster.rank)
                
                data = redisbattleevent.zrevrange(rediskey, 0, 1, withscores=True, score_cast_func=RedisModel.value_to_int)
                if data:
                    level = data[0][1]
                    groupid = 0
                    while 0 < level:
                        uidlist = [RedisModel.value_to_int(uid) for uid in redisbattleevent.zrangebyscore(rediskey, level, level) if RedisModel.value_to_int(uid)]
                        if uidlist:
                            random.shuffle(uidlist)
                            model_mgr, group = db_util.run_in_transaction(Command.tr_create, groupid, eventmaster, rankmaster, uidlist, tomorrow)
                            model_mgr.write_end()
                            if group and not group.fixed:
                                groupid = group.id
                            else:
                                groupid = 0
                        level -= 1
            redisbattleevent = None
        
        # 完了フラグを立てておく.
        redisdb.set(ALREADY_KEY, cdate.strftime("%Y%m%d"))
        
        print '================================'
        print 'all done.'
    
    @staticmethod
    def tr_close(eventmaster, eventrankmaster, groupid, now, rank_max):
        """グループ閉鎖書き込み.
        """
        group = BattleEventGroup.getByKeyForUpdate(groupid)
        model_mgr = ModelRequestMgr()
        BackendApi.tr_battleevent_close_group(model_mgr, eventmaster, eventrankmaster, group, now, rank_max=rank_max)
        model_mgr.write_all()
        
        return model_mgr
    
    @staticmethod
    def tr_create(groupid, eventmaster, eventrankmaster, uidlist, tomorrow):
        """書き込み.
        """
        group = None
        if groupid:
            group = BattleEventGroup.getByKeyForUpdate(groupid)
        
        model_mgr = ModelRequestMgr()
        rankrecordlist = BattleEventRank.fetchByKeyForUpdate([BattleEventRank.makeID(uid, eventmaster.id) for uid in uidlist])
        playerexp_dict = BackendApi.get_model_dict(model_mgr, PlayerExp, uidlist)
        for rankrecord in rankrecordlist:
            if rankrecord.groups and BattleEventGroup.getByKey(rankrecord.groups):
                # すでに参加している.
                continue
            if group and group.fixed:
                group = None
            
            playerexp = playerexp_dict.get(rankrecord.uid)
            level = playerexp.level if playerexp else 1
            group = BackendApi.tr_battleevent_regist_group(model_mgr, eventrankmaster, rankrecord, False, group, level, tomorrow)
            print 'set group:%s => %s' % (rankrecord.uid, group.id)
        
        model_mgr.write_all()
        return model_mgr, group
