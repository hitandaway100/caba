# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.api import OSAUtil, ModelRequestMgr
from platinumegg.app.cabaret.util.redisdb import RedisModel, CabaClubRanking
from platinumegg.app.cabaret.models.CabaretClub import CabaClubScorePlayerDataWeekly
from datetime import datetime
import settings

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Command(BaseCommand):
    """
        This command retrieves last week (prior to current date)
        ranking data from the database
    """

    def handle(self, *args, **options):
        print '=================================================='
        print 'cabaclub_lastweek_rankingdata_backup'
        print '=================================================='

        model_mgr = ModelRequestMgr()
        currentdate = OSAUtil.get_now()
        currentyear = datetime.strftime(currentdate, '%Y')
        currentweek = datetime.strftime(currentdate, '%W')
        lastweek = int(currentweek) - 1

        cabaclub_week = int(currentyear + str(lastweek))

        print "saving ranking data from week %d to RedisDB" % cabaclub_week

        # get last week ranking data
        weekly_data = CabaClubScorePlayerDataWeekly.fetchValues(filters={'week': cabaclub_week}, using=backup_db)

        # Backup player proceeds (sales) data to Redis DB
        def write_end():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            for weekly_model in weekly_data:
                CabaClubRanking.create('lastweek', weekly_model.uid, weekly_model.proceeds).save(pipe)
            pipe.execute()

        model_mgr.add_write_end_method(write_end)
        model_mgr.write_end()

        print '=================================================='
        print 'all done...'
