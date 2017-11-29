# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.present import PrizeData, Present
#from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
import settings_sub
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.models.UserLog import UserLogPresentSend, UserLogPresentReceive
import settings
from defines import Defines

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Command(BaseCommand):
    """お詫びを一括配布.
    """
    def handle(self, *args, **options):
        print '================================'
        print 'send_owabi'
        print '================================'
        model_mgr = ModelRequestMgr()

        is_write = (args[0] if args else '0') == '1'
        print "write:%s" % is_write

        receivelogs = UserLogPresentReceive.fetchValues(filters={'ctime__gt': '2016-04-21 16:00:00', 'ctime__lt': '2016-04-21 16:20:00'}, using=backup_db)
        presentlist = []
        for log in receivelogs:
            presentdata = UserLogPresentSend.fetchValues(filters={'uid': log.uid, 'ctime__gt': '2016-04-21 15:00:00', 'ctime__lt': '2016-04-21 16:00:00'}, using=backup_db)
            for sendlog in presentdata:
                if log.presentid == sendlog.presentid and Defines.ItemType.ADDITIONAL_GACHATICKET == sendlog.itype:
                    print sendlog.itype, sendlog.ivalue, sendlog.inum
                    prizelist = [log.uid, [PrizeData.create(additional_ticket_id=sendlog.ivalue, additional_ticket_num=sendlog.inum)]]
                    presentlist.append(prizelist)
        self.send_owabi(presentlist, is_write)

    def send_owabi(self, presentlist, is_write):
        textid = 1000034
        for uid, prizelist in presentlist:
            if is_write:
                def tr(present):
                    model_mgr = ModelRequestMgr()
                    BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
                    model_mgr.write_all()
                    return model_mgr
                model_mgr = db_util.run_in_transaction(tr, prizelist)
            try:
                if is_write:
                    model_mgr.write_end()
                print uid
            except:
                print '%s...NG' % uid
        print '================================'
        print 'all done..'
