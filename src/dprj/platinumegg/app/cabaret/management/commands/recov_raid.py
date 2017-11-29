# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Happening import Raid, RaidMaster
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
import settings
from platinumegg.app.cabaret.util.happening import RaidBoss

class Command(BaseCommand):
    """壊れたレイドの修復.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'recov_raid'
        print '================================'
        
        model_mgr = ModelRequestMgr()
        
        target_date = DateTimeUtil.strToDateTime("20140217170000", "%Y%m%d%H%M%S")
        raidlist = Raid.fetchValues(fields=['id'], filters={'ctime__gte':target_date})
        
        master_all = dict([(master.id, master) for master in model_mgr.get_mastermodel_all(RaidMaster, using=settings.DB_READONLY)])
        
        for raid in raidlist:
            if raid.hp < 1:
                continue
            
            def tr(raidid):
                model_mgr = ModelRequestMgr()
                raid = Raid.getByKeyForUpdate(raidid)
                master = master_all[raid.mid]
                raidboss = RaidBoss(raid, master)
                pre_hp = raid.hp
                raid.hp = min(raidboss.get_maxhp(), raid.hp)
                model_mgr.set_save(raid)
                model_mgr.write_all()
                
                print "%s:%s=>%s" % (raid.id, pre_hp, raid.hp)
                
                return model_mgr
            db_util.run_in_transaction(tr, raid.id).write_end()
        
        print '================================'
        print 'all done..'
