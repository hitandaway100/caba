# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.Gacha import GachaBoxResetPlayerData
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Command(BaseCommand):
    def handle(self, *args, **options):
        print '================================'
        print 'reset player is_get_targetrarity'
        print '================================'


        resetdata = GachaBoxResetPlayerData.fetchValues(using=backup_db)
        resetdata_uid = [reset.id for reset in resetdata]

        playerlist= Player.fetchValues(using=backup_db, excludes={'id__in': resetdata_uid})

        users = [player for player in playerlist if player.id not in resetdata_uid]

        # update is_get_targetrarity
        try:
            db_util.run_in_transaction(self.tr_update, resetdata)
        except CabaretError, err:
            print 'error...{}'.format(err.value)

        # add users that were not previously in GachaBoxResetPlayerData
        # add set their is_get_targetrarity to True
        try:
            db_util.run_in_transaction(self.tr_write, users)
        except CabaretError, err:
            print 'error...{}'.format(err.value)

        print "all done."
        print '================================'

    def tr_update(self, resetdata):
        model_mgr = ModelRequestMgr()

        def forUpdate(instance, inserted):
            instance.is_get_targetrarity = True

        for data in resetdata:
            model_mgr.add_forupdate_task(GachaBoxResetPlayerData, data.id, forUpdate)

        model_mgr.write_all()
        model_mgr.write_end()

    def tr_write(self, users):
        model_mgr = ModelRequestMgr()
        for user in users:
            ins = GachaBoxResetPlayerData.makeInstance(user.id)
            ins.is_get_targetrarity = True
            model_mgr.set_save(ins)
        model_mgr.write_all()
        model_mgr.write_end()
