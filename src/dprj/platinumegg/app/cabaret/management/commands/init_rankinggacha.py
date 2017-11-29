# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.redisdb import RankingGachaSingleRanking, RankingGachaTotalRanking
import settings
from platinumegg.app.cabaret.models.Gacha import GachaMaster, RankingGachaScore,\
    RankingGachaClose, RankingGachaWholePrizeQueue, RankingGachaWholeData,\
    RankingGachaPlayLog
from platinumegg.app.cabaret.models.UserLog import UserLogRankingGachaWholePrize
from platinumegg.app.cabaret.models.base.queryset import Query
from platinumegg.app.cabaret.util.rediscache import RankingGachaWholePrizeQueueIdSet

class Command(BaseCommand):
    """ランキングガチャの初期化.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'init_rankinggacha'
        print '================================'
        
        model_mgr = ModelRequestMgr()
        
        now = OSAUtil.get_now()
        
        # メンテナンス確認.
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return
        print 'check maintenance...OK'
        
        print '================================'
        print 'check master'
        group = int(args[0])
        master_list = BackendApi.get_rankinggacha_master_by_group(model_mgr, group, using=settings.DB_READONLY)
        if not master_list:
            print u'ランキングガチャではありません'
            return
        boxidlist = [master.id for master in master_list]
        gachamaster_list = GachaMaster.fetchValues(filters={'boxid__in':boxidlist}, using=settings.DB_READONLY)
        gachamaster_list = [gachamaster.id for gachamaster in gachamaster_list if BackendApi.check_schedule(model_mgr, gachamaster.schedule, using=settings.DB_READONLY, now=now)]
        if gachamaster_list:
            print u'ガチャが開いています.id=%s' % gachamaster_list
            return
        print 'check master...OK'
        
        print '================================'
        print 'check flag'
        close_model_list = RankingGachaClose.getByKey(boxidlist)
        if len(close_model_list) != len(boxidlist):
            print u'未集計です.close_rankinggachaを実行してください'
            return
        print 'check flag...OK'
        
        print '================================'
        print 'delete redis'
        pipe = RankingGachaSingleRanking.getDB().pipeline()
        for boxid in boxidlist:
            pipe.delete(RankingGachaSingleRanking.makeKey(boxid), RankingGachaTotalRanking.makeKey(boxid))
        pipe.execute()
        
        print '================================'
        print 'delete mysql'
        limit = 500
        while True:
            recordlist = RankingGachaScore.fetchValues(filters={'mid__in':boxidlist}, limit=limit)
            def tr():
                model_mgr = ModelRequestMgr()
                for record in recordlist:
                    model_mgr.set_delete(record)
                model_mgr.write_all()
                return model_mgr
            db_util.run_in_transaction(tr).write_end()
            
            if len(recordlist) < limit:
                break
        
        delete_target_model_cls_list = (
            UserLogRankingGachaWholePrize,
            RankingGachaPlayLog,
        )
        def tr_delete_common():
            for model_cls in delete_target_model_cls_list:
                tablename = model_cls.get_tablename()
                query_string = "truncate table `%s`;" % tablename
                Query.execute_update(query_string, [], False)
                print 'delete...%s' % tablename
            
            model_mgr = ModelRequestMgr()
            for close_model in close_model_list:
                model_mgr.set_delete(close_model)
            
            for wholedata in RankingGachaWholeData.getByKey(boxidlist):
                model_mgr.set_delete(wholedata)
            
            for queue in RankingGachaWholePrizeQueue.fetchValues(filters={'boxid__in':boxidlist}):
                model_mgr.set_delete(queue)
            model_mgr.write_all()
            
            return model_mgr
        db_util.run_in_transaction(tr_delete_common).write_end()
        
        RankingGachaWholePrizeQueueIdSet.flush()
        
        print '================================'
        print 'all done..'
