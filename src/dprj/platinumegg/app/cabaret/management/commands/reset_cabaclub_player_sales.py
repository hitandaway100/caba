# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.CabaretClubEvent import CabaClubEventRankMaster
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Command(BaseCommand):
    """
        This command is used to reset the players' sales (proceeds) for the day to 0
        It is run everyday at 12PM using a cron job
        cron jobs are found at /etc/crontab at the server side
    """

    def handle(self, *args, **options):
        print '================================'
        print 'reset_cabaclub_player_sales'
        print '================================'

        model_mgr = ModelRequestMgr()
        modellist = CabaClubEventRankMaster.fetchValues(using=backup_db)

        offset = 0
        limit = 1000

        while modellist[offset:offset+limit]:
            try:
                db_util.run_in_transaction(self.tr_update, model_mgr, modellist[offset:offset+limit])
            except CabaretError, err:
                print('{}...NG'.format(err.value))

            offset += limit

        print "all done."
        print '================================'

    def tr_update(self, model_mgr, modellist):
        if modellist:
            def forUpdate(model, inserted):
                model.today_proceeds = 0

            for data in modellist:
                model_mgr.add_forupdate_task(CabaClubEventRankMaster, data.id, forUpdate)

            model_mgr.write_all()
            model_mgr.write_end()
