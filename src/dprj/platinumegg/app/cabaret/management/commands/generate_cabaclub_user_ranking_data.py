# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.redisdb import RedisModel, CabaClubRanking
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.util.apprandom import AppRandom
import settings


class Command(BaseCommand):
    """Generate cabaret club user ranking data.
    """

    def handle(self, *args, **options):

        print '======================================='
        print 'Generate cabaret club user ranking data'
        print '======================================='

        players = Player.fetchValues(using=settings.DB_READONLY)
        rand = AppRandom()
        redisdb = RedisModel.getDB()
        pipe = redisdb.pipeline()
        for player in players:
            sales = rand.getIntN(10000)
            CabaClubRanking.create("currentweek", player.id, sales).save(pipe)
            CabaClubRanking.create("lastweek", player.id, max(100, sales - 1500)).save(pipe)

        pipe.execute()

        print '================================'
        print 'all done...'
