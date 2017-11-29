# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.lib.opensocial.util import OSAUtil
import datetime
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.CabaretClub import CabaClubStoreMaster,\
    CabaClubStorePlayerData, CabaClubScorePlayerDataWeekly
import settings
from platinumegg.app.cabaret.models.Player import PlayerTreasure
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabaclub_store import CabaclubStoreSet
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.dbg import DbgLogger
from platinumegg.app.cabaret.util.present import PrizeData
import math
from platinumegg.app.cabaret.util.redisdb import CabaClubRanking
import time

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Command(BaseCommand):
    """キャバクラシステムの毎週の集計.
    """
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'aggregate_cabaretclub_weekly'
        print '================================'
        
        last_week_starttime = BackendApi.to_cabaretclub_section_starttime(OSAUtil.get_now() - datetime.timedelta(days=7))
        
        str_year_and_week = args[0] if 0 < len(args) else None
        if str_year_and_week:
            week = int(str_year_and_week[4:])
            first_of_year = DateTimeUtil.strToDateTime("%s%02d" % (str_year_and_week[:4], Defines.CABARETCLUB_EVENT_DATE_CHANGE_TIME), "%Y%H")
            # 0週目.
            zero = BackendApi.to_cabaretclub_section_starttime(first_of_year)
            starttime = zero + datetime.timedelta(days=week * 7)
            if last_week_starttime < starttime:
                print u'未完了の週なので集計は行えません'
                return
        else:
            # 指定がない場合は前回の週.
            starttime = last_week_starttime
        print "target:%s" % starttime.strftime("%Y%W")
        endtime = BackendApi.to_cabaretclub_section_endtime(starttime)
        section_lasttime = endtime - datetime.timedelta(microseconds=1)

        model_mgr = ModelRequestMgr()
        self.update_eventconfig_previous_mid(model_mgr,starttime);
        
        # 店舗のマスターデータ.
        cabaclubstoremaster_dict = dict([(cabaclubstoremaster.id, cabaclubstoremaster) for cabaclubstoremaster in model_mgr.get_mastermodel_all(CabaClubStoreMaster, fetch_deleted=True, using=backup_db)])
        # ユーザIDの最大値.
        uid_max = PlayerTreasure.max_value('id', using=backup_db)
        for uid in xrange(1, uid_max + 1):
            # 所持している店舗.ここはreadonlyで大丈夫.
            store_list = CabaClubStorePlayerData.fetchByOwner(uid, using=settings.DB_READONLY)
            if store_list:
                # この週に更新された店舗数.
                update_store_cnt = 0
                # Activeな店舗を週の終了時間まですすめる.
                for store in store_list:
                    cabaclubstoremaster = cabaclubstoremaster_dict[store.mid]
                    if not store.is_open:
                        # 閉じるときに集計しているので必要なし.
                        if starttime <= store.utime:
                            update_store_cnt += 1
                        continue
                    store_set = CabaclubStoreSet(cabaclubstoremaster, store)
                    lasttime = min(section_lasttime, store_set.get_limit_time() - datetime.timedelta(microseconds=1))
                    if (lasttime - store.utime).total_seconds() < cabaclubstoremaster.customer_interval:
                        # 獲得時間が経過していないので更新する必要が無い.
                        if starttime <= store.utime:
                            update_store_cnt += 1
                        continue
                    def tr_advance_the_time(uid, cabaclubstoremaster, now):
                        """店舗の時間をすすめる.
                        """
                        model_mgr = ModelRequestMgr()
                        BackendApi.tr_cabaclubstore_advance_the_time_with_checkalive(model_mgr, uid, cabaclubstoremaster, now)
                        model_mgr.write_all()
                        model_mgr.write_end()
                    try:
                        db_util.run_in_transaction(tr_advance_the_time, uid, cabaclubstoremaster, lasttime)
                    except CabaretError, err:
                        if err.code == CabaretError.Code.ALREADY_RECEIVED:
                            # ユーザー自信が更新した可能性.
                            pass
                        else:
                            DbgLogger.write_error(err.value)
                            raise
                    update_store_cnt += 1
                if 0 < update_store_cnt:
                    # 売り上げに応じた名誉ポイントを配布.
                    def tr_send_point(uid, starttime):
                        """名誉ポイントの配布.
                        """
                        model_mgr = ModelRequestMgr()
                        scoredata_weekly = CabaClubScorePlayerDataWeekly.getByKeyForUpdate(CabaClubScorePlayerDataWeekly.makeID(uid, starttime))
                        if scoredata_weekly is None or scoredata_weekly.flag_aggregate:
                            return 0
                        # 配布する数を計算.
                        cabaclub_honor = int(math.ceil(scoredata_weekly.proceeds / 1000.0))
                        if 0 < cabaclub_honor:
                            # 報酬付与.
                            prizedata = PrizeData.create(cabaclub_honor=cabaclub_honor)
                            BackendApi.tr_add_prize(model_mgr, uid, [prizedata], Defines.TextMasterID.CABARETCLUB_WEEKLY_PRIZE)
                        # 重複防止.
                        scoredata_weekly.flag_aggregate = True
                        model_mgr.set_save(scoredata_weekly)
                        model_mgr.write_all()
                        model_mgr.write_end()
                        return cabaclub_honor
                    cabaclub_honor = db_util.run_in_transaction(tr_send_point, uid, starttime)
                    print '%s...honor=%d' % (uid, cabaclub_honor)
                else:
                    print '%s...not updated' % uid

        print(u'==================================================')
        print(u'check cabaclub event config...')

        target_time = BackendApi.to_cabaretclub_section_starttime(starttime + datetime.timedelta(days=7))
        event_config = BackendApi.get_current_cabaclubrankeventconfig(model_mgr, using=settings.DB_READONLY)

        if self.is_equal_day(event_config.starttime, target_time):
            # イベント開始日
            print(u'==================================================')
            print(u'delete last event cache...')
            self.delete_last_event_cache(event_config.mid)
        else:
            print(u'==================================================')
            print(u'today is not event start day, so not delete cache.')

        if self.is_equal_day(event_config.endtime, target_time):
            # イベント終了日
            print(u'==================================================')
            print(u'send cabaclub event ranking prize...')
            self.send_ranking_prizes(model_mgr)
        else:
            print(u'==================================================')
            print(u'today is not event end day, so not send ranking prize.')

        print '=================================================='
        print 'all done..'
        
    def update_eventconfig_previous_mid(self, model_mgr, starttime):
        target_time = BackendApi.to_cabaretclub_section_starttime(starttime + datetime.timedelta(days=7))
        event_config = BackendApi.get_current_cabaclubrankeventconfig(model_mgr, using=settings.DB_READONLY)
        if self.is_equal_day(event_config.endtime, target_time):
            # イベント終了日
            event_config.previous_mid = event_config.mid
            model_mgr.set_save(event_config)
            model_mgr.write_all()
            model_mgr.write_end()
            print "CurrentCabaClubRankEventConfigのprevious_midを更新しました"
            
    def send_ranking_prizes(self, model_mgr):
        """send ranking prizes to players
        """
        using = settings.DB_READONLY
        eventmaster = BackendApi.get_current_cabaclubrankeventmaster(model_mgr, using=using, check_schedule=False)
        if eventmaster is None:
            print u'経営イベントが設定されていません'
            return

        rankingprizes = eventmaster.rankingprizes
        if not rankingprizes:
            print u'There is no ranking prize for this cabaret club event'
            return

        # 経営ランキングの情報
        data = CabaClubRanking.get_rankings(eventmaster.id)
        if data is None:
            print u'ランキングのデータが存在しません'
            return
        
        for rankingprize in rankingprizes:
            rank_min = rankingprize['rank_min']
            rank_max = rankingprize['rank_max']
            prizeidlist = rankingprize['prize']

            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=using)
            # get user ids between rank_min and rank_max
            uidlist = [d['uid'] for d in data if rank_min <= d['rank'] <= rank_max]

            offset = 0
            limit = 100
            while self.sendPrize(model_mgr, uidlist[offset:offset+limit], prizelist, eventmaster.rankingprize_text):
                offset += limit

    def sendPrize(self, model_mgr, uidlist, prizelist, prize_text_id):
        if uidlist:
            def tr():
                for uid in uidlist:
                    print "sending to ....", uid
                    BackendApi.tr_add_prize(model_mgr, uid, prizelist, prize_text_id)
                model_mgr.write_all()
                return model_mgr

            try:
                tmp_model_mgr = db_util.run_in_transaction(tr)
            except CabaretError, err:
                print "An error occured when sending prizes to users"
                print 'error...%s' % err.value
                return

            tmp_model_mgr.write_end()
            time.sleep(0.15)
            return True

        return False

    def delete_last_event_cache(self, mid):
        redisdb = CabaClubRanking.getDB()
        keys = redisdb.keys(CabaClubRanking.makeKey('*'))
        pipe = redisdb.pipeline()
        pipe.delete(*keys)
        pipe.execute()

    def is_equal_day(self, datetime1, datetime2):
        ##月と日が同じなら
        return datetime1.strftime("%m%d") == datetime2.strftime("%m%d")
