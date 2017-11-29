# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Happening import Happening, RaidLog, Raid,\
    RaidHelp
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.models.base.queryset import Query
from platinumegg.app.cabaret.models.Player import Player, PlayerHappening
from platinumegg.app.cabaret.util.redisdb import RaidLogListSet
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil

class Command(BaseCommand):
    """ハプニングを全て削除する.
    """
    def handle(self, *args, **options):
        
        model_mgr = ModelRequestMgr()
        starttime = OSAUtil.get_now()
        
        print '================================'
        print 'drop_happening_partition'
        print '================================'
        
        # クリア済みで受け取っていないハプニング.
        print '================================'
        print 'check raid:start'
        # クリア済みのレイドを全て終了させる.
        filters = {'state__in':[Defines.HappeningState.BOSS, Defines.HappeningState.CLEAR]}
        num = Happening.count(filters)
        print 'happenings %d' % num
        
        # メンテナンス確認.
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return
        print 'check maintenance...OK'
        
        # ターゲットのパーティション.
        partitionname = '%s01' % args[0]
        partition_date = DateTimeUtil.strToDateTime(partitionname, "%Y%m%d")
        filters['ctime__lt'] = partition_date
        
        offset = 0
        LIMIT = 200
        
        def tr_clear(happeningid):
            model_mgr = ModelRequestMgr()
            happening = Happening.getByKeyForUpdate(happeningid)
            raidboss = BackendApi.get_raid(model_mgr, happeningid)
            BackendApi.tr_happening_end(model_mgr, happening, raidboss)
            model_mgr.write_all()
            return model_mgr
        
        def tr_miss(happeningid):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_happening_missed(model_mgr, happeningid, force=True)
            model_mgr.write_all()
            return model_mgr
        
        while True:
            happeninglist = Happening.fetchValues(['id','state'], filters, limit=LIMIT, offset=offset)
            offset += LIMIT
            
            for happening in happeninglist:
                try:
                    if happening.state == Defines.HappeningState.CLEAR:
                        model_mgr = db_util.run_in_transaction(tr_clear, happening.id)
                    else:
                        model_mgr = db_util.run_in_transaction(tr_miss, happening.id)
                    model_mgr.write_end()
                except CabaretError, err:
                    if err.code == CabaretError.Code.ALREADY_RECEIVED:
                        pass
                    else:
                        raise
                print 'update %d end' % happening.id
            
            if len(happeninglist) < LIMIT:
                break
        
        print 'check raid:end'
        
        print '================================'
        print 'delete mysql'
        # MySQLから削除.
        delete_target_model_cls_list = (
            RaidLog,
            RaidHelp,
            Raid,
            Happening,
        )
        def tr():
            for model_cls in delete_target_model_cls_list:
                tablename = model_cls.get_tablename()
                Query.execute_update('ALTER TABLE `%s` DROP PARTITION `%s`' % (tablename, partitionname), [], False)
                print 'delete...%s' % tablename
        db_util.run_in_transaction(tr)
        
        print '================================'
        print 'delete redis'
        # Redisから削除.
        uid_max = Player.max_value('id')
        
        for uid in xrange(1, uid_max+1):
            playerhappening = PlayerHappening.getByKey(uid)
            if playerhappening is None:
                print 'none...%s' % uid
                continue
            # レイドログ.
            BackendApi._save_log_idlist(RaidLogListSet, 'uid', 'ctime', uid, ModelRequestMgr(), RaidLogListSet.NUM_MAX)
            # 救援依頼.
            BackendApi._save_raidhelpidlist(ModelRequestMgr(), uid)
            print 'delete redis...%s' % uid
        
        print '================================'
        print 'all end..'
        
        diff = OSAUtil.get_now() - starttime
        sec = diff.days * 86400 + diff.seconds
        print 'time %d.%06d' % (sec, diff.microseconds)
