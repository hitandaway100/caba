# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
import settings_sub
from platinumegg.app.cabaret.models.Player import PlayerConsumePoint,\
    PlayerHappening
from platinumegg.app.cabaret.models.PaymentEntry import GachaPaymentEntry,\
    ShopPaymentEntry
from platinumegg.lib.platform.api.objects import PaymentData
from platinumegg.app.cabaret.models.Gacha import GachaConsumePoint
from platinumegg.app.cabaret.util import db_util
import settings

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Command(BaseCommand):
    """プレイヤーのガチャ別生涯課金額を取り直すコマンド.
    """
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'reload_gachaplayerconsumepoint'
        print '================================'
        
        model_mgr = ModelRequestMgr()
        
        # メンテモードでやって欲しい.
        appconfig = BackendApi.get_appconfig(model_mgr, using=backup_db)
        if not settings_sub.IS_DEV and not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return
        
        # ユーザIDの最大値.
        uid_max = PlayerHappening.max_value('id', 0, using=backup_db)
        
        qs_field = "iid,SUM(price*inum)"
        qs_where = "WHERE uid=:1 and state=%s group by iid" % PaymentData.Status.COMPLETED
        
        for uid in xrange(1, uid_max+1):
            # 課金レコードを集計.
            gacha_point_table = dict([(int(iid), int(point)) for iid,point in GachaPaymentEntry.sql(qs_where, uid).fetch(qs_field)])
            shop_point_table = dict([(int(iid), int(point)) for iid,point in ShopPaymentEntry.sql(qs_where, uid).fetch(qs_field)])
            gacha_point = sum(gacha_point_table.values())
            shop_point = sum(shop_point_table.values())
            total = gacha_point + shop_point
            
            if total < 1:
                print '%s...zero' % uid
                continue
            elif PlayerHappening.getByKey(uid, using=backup_db) is None:
                print '%s...none' % uid
                continue
            
            # プレイヤーデータに保存.
            def tr(uid, gacha_point_table, total):
                model_mgr = ModelRequestMgr()
                if gacha_point_table:
                    for iid,point in gacha_point_table.items():
                        if point < 1:
                            continue
                        def forUpdateGacha(model, inserted, point):
                            model.point = point
                        model_mgr.add_forupdate_task(GachaConsumePoint, GachaConsumePoint.makeID(uid, iid), forUpdateGacha, point)
                
                # 生涯課金額.
                def forUpdatePlayerConsumePoint(model, inserted, total):
                    model.point_total = total
                model_mgr.add_forupdate_task(PlayerConsumePoint, uid, forUpdatePlayerConsumePoint, total)
                
                model_mgr.write_all()
                return model_mgr
            db_util.run_in_transaction(tr, uid, gacha_point_table, total).write_end()
            
            print '%s...g:%s,s:%s' % (uid, gacha_point, shop_point)
        
        print '================================'
        print 'all done...'
