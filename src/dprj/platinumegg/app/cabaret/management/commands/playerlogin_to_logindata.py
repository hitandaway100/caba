# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Player import PlayerLoginTimeLimited
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusTimeLimitedData

class Command(BaseCommand):
    """ロングログインボーナスを移行.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'playerlogin_to_logindata'
        print '================================'
        
        uidmax = PlayerLoginTimeLimited.max_value('id')
        
        for uid in xrange(1, uidmax+1):
            playerlogin = PlayerLoginTimeLimited.getByKey(uid)
            if playerlogin and playerlogin.mid:
                data_id = LoginBonusTimeLimitedData.makeID(uid, playerlogin.mid)
                timelimiteddata = LoginBonusTimeLimitedData.getByKey(data_id)
                if timelimiteddata is None:
                    def tr():
                        model_mgr = ModelRequestMgr()
                        ins = LoginBonusTimeLimitedData.makeInstance(data_id)
                        ins.days = playerlogin.days
                        ins.lbtltime = playerlogin.lbtltime
                        model_mgr.set_save(ins)
                        model_mgr.write_all()
                        return model_mgr
                    db_util.run_in_transaction(tr).write_end()
                    print '%s...insert' % uid
                    continue
            print '%s...none' % uid
        
        print '================================'
        print 'all done..'
