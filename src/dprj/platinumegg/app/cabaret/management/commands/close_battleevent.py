# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.redisdb import RedisModel,\
    BattleEventRanking, BattleEventDailyRanking, BattleEventRankingBeginer
from platinumegg.app.cabaret.models.battleevent.BattleEvent import CurrentBattleEventConfig,\
    BattleEventGroup, BattleEventRankMaster, BattleEventScore,\
    BattleEventGroupLog, BattleEventPieceCollection
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
import datetime

class Command(BaseCommand):
    """バトルイベント終了処理.
    """
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'close_battleevent'
        print '================================'
        
        now = OSAUtil.get_now()
        
        model_mgr = ModelRequestMgr()
        redisdb = RedisModel.getDB()
        
        config = BackendApi.get_current_battleeventconfig(model_mgr)
        eventmaster = BackendApi.get_battleevent_master(model_mgr, config.mid)
        if eventmaster is None:
            print u'イベントが設定されていません'
            return
        print 'check eventmaster...OK'
        
        # イベント設定.
        if now < config.endtime:
            print u'イベントがまだ終了していません'
            return
        print 'check event endtime...OK'
        
        # メンテナンス確認.
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return
        print 'check maintenance...OK'
        
        rankmaster_dict = dict([(master.id, master) for master in BattleEventRankMaster.fetchValues(filters={'eventid':config.mid}, fetch_deleted=True, using=settings.DB_READONLY)])
        
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
            if not grouplist:
                break
            
            for group in grouplist:
                eventrankmaster = rankmaster_dict[group.rankid]
                model_mgr = db_util.run_in_transaction(Command.tr_close, eventmaster, eventrankmaster, group.id, now)
                model_mgr.write_end()
                print 'close %s' % group.id
        
        print '================================'
        print 'send daily ranking prizes.'
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
        for rankmaster in rankmaster_dict.values():
            BackendApi.save_battleevent_rankuidset(rankmaster.eventid, rankmaster.rank)
        
        print '================================'
        print 'update ranking:start'
        # ランキングを更新.
        offset = 0
        limit = 1000
        while True:
            recordlist = BattleEventScore.fetchValues(['uid','point_total'], filters={'mid':config.mid}, limit=limit, offset=offset)
            
            pipe = BattleEventRanking.getDB().pipeline()
            for record in recordlist:
                BattleEventRanking.create(config.mid, record.uid, record.point_total).save(pipe)
                if BackendApi.check_battleevent_beginer(ModelRequestMgr(), record.uid, eventmaster, config, now, using=settings.DB_READONLY):
                    BattleEventRankingBeginer.create(config.mid, record.uid, record.point_total).save(pipe)
            pipe.execute()
            
            if len(recordlist) < limit:
                break
            offset += limit
        print 'update ranking:end'
        
        # 報酬を渡す.
        def sendRankingPrize(ranking_cls, rankingprizes, textid, att_prize_flag):
            for idx, data in enumerate(rankingprizes):
                if idx < getattr(config, att_prize_flag):
                    print 'skip...%d' % idx
                    continue
                
                prizeidlist = data['prize']
                rank_min = data['rank_min']
                rank_max = data['rank_max']
                
                prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
                uidlist = []
                
                for rank in xrange(rank_min, rank_max+1):
                    data = ranking_cls.fetchByRank(eventmaster.id, rank, zero=False)
                    dic = dict(data)
                    uidlist.extend(dic.keys())
                    if len(set(uidlist)) != len(uidlist):
                        raise CabaretError(u'ランキング取得がなにかおかしい..%d' % rank)
                
                def tr():
                    model_mgr = ModelRequestMgr()
                    config = CurrentBattleEventConfig.getByKeyForUpdate(CurrentBattleEventConfig.SINGLE_ID)
                    if getattr(config, att_prize_flag) != idx:
                        raise CabaretError(u'整合が取れていないので終了します')
                    for uid in uidlist:
                        BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
                    setattr(config, att_prize_flag, idx + 1)
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

                setattr(config, att_prize_flag, getattr(wrote_config, att_prize_flag))

        # プラチナ欠片.
        def sendPlatinumGift(eventid, prizelist_data, limit, offset):
            """
            Send platinum pieces (プラチナ欠片) to players
            The number of platinum pieces to send depends on the number of slot gotten
            For example: If 4 slots gotten, send 4 platinum pieces. Else if, 7 send 7 platinum pieces and so on.
            """
            # プラチナ rarity is 4
            piece_collection = BattleEventPieceCollection.fetchValues(filters={'eventid': eventid, 'rarity': 4}, limit=limit, offset=offset, using=settings.DB_DEFAULT)
            if len(piece_collection) <= 0:
                return None
            piecemaster_dict = {master.uid: master for master in piece_collection}
            platinum_piece_data = {}
            for key, value in piecemaster_dict.items():
                # if the user completed the platinum panel, continue
                if value.is_complete_morethan_maxcount(1):
                    piecemaster_dict.pop(key)
                    continue
                platinum_piece_num = 0
                for i in xrange(1, 10):
                    if getattr(value, 'piece_number{}'.format(i - 1)):
                        platinum_piece_num += 1
                platinum_piece_data[value.uid] = platinum_piece_num

            gift_text = 236

            def tr():
                model_mgr = ModelRequestMgr()
                config = CurrentBattleEventConfig.getByKeyForUpdate(CurrentBattleEventConfig.SINGLE_ID)
                for uid, num in platinum_piece_data.items():
                    if num == 0:
                        continue

                    if 0 < num < 9:
                        BackendApi.tr_add_prize(model_mgr, uid, prizelist_data[num], gift_text)
                #     BackendApi.tr_add_platinum_piece(model_mgr, uid, num)

                #     piece = piecemaster_dict[uid]
                #     # update the platinum piece slots (piece_number0 ~ piece_number8) to False
                #     for index in xrange(1, 10):
                #         setattr(piece, "piece_number{}".format(index - 1), False)
                #     # update complete_cnt to 0 for precaution
                #     setattr(piece, "complete_cnt", 0)
                #     # add for update
                #     model_mgr.set_save(piece)

                # model_mgr.set_save(config)
                model_mgr.write_all()
                model_mgr.write_end()
                return model_mgr, config

            try:
                tmp_model_mgr, wrote_config = db_util.run_in_transaction(tr)
            except CabaretError, err:
                print 'error...%s' % err.value
                return

            tmp_model_mgr.write_end()
            return True


        print '================================'
        print 'send prizes:start'
        sendRankingPrize(BattleEventRanking, eventmaster.rankingprizes, eventmaster.rankingprize_text, 'prize_flag')
        
        print '================================'
        print 'send beginerprizes:start'
        sendRankingPrize(BattleEventRankingBeginer, eventmaster.beginer_rankingprizes, eventmaster.beginer_rankingprize_text, 'beginer_prize_flag')

        print '================================'
        print 'send platinum pieces'
        limit = 1000
        offset = 0

        prizelist_data = {
            0: None,
            1: BackendApi.get_prizelist(model_mgr, [410406]),
            2: BackendApi.get_prizelist(model_mgr, [410407]),
            3: BackendApi.get_prizelist(model_mgr, [410408]),
            4: BackendApi.get_prizelist(model_mgr, [410409]),
            5: BackendApi.get_prizelist(model_mgr, [410410]),
            6: BackendApi.get_prizelist(model_mgr, [410411]),
            7: BackendApi.get_prizelist(model_mgr, [410412]),
            8: BackendApi.get_prizelist(model_mgr, [410413]),
        }
        while sendPlatinumGift(config.mid, prizelist_data,limit=limit, offset=offset):
            offset += limit

        print '================================'
        print 'all done.'

    @staticmethod
    def tr_close(eventmaster, eventrankmaster, groupid, now):
        """グループ閉鎖書き込み.
        """
        group = BattleEventGroup.getByKeyForUpdate(groupid)
        model_mgr = ModelRequestMgr()
        BackendApi.tr_battleevent_close_group(model_mgr, eventmaster, eventrankmaster, group, now, do_send_famebonus=True)
        model_mgr.write_all()
        
        return model_mgr
