# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerExp, PlayerFriend, \
    PlayerDeck
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.present import PrizeData
from platinumegg.app.cabaret.models.UserLog import UserLogEvolution
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Item import ItemMaster
import settings

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Command(BaseCommand):
    """Transfer information of one player to another
    """

    def handle(self, *args, **options):
        if len(args) != 2:
            print "Wrong usage"
            print "Usage: 'python manage.py migrate_playerdata.py <dmmid1> <dmmid2>"
            return

        dmmidlist = [int(arg) for arg in args]
        old_dmmid, new_dmmid = dmmidlist

        model_mgr = ModelRequestMgr()

        playerdict = BackendApi.dmmid_to_appuid(None, dmmidlist, using=backup_db)
        old_uid = playerdict[old_dmmid]
        new_uid = playerdict[new_dmmid]

        player1 = BackendApi.get_player(self, old_uid, using=backup_db, model_mgr=model_mgr)
        player2 = BackendApi.get_player(self, new_uid, using=backup_db, model_mgr=model_mgr)

        def write_end(function, cls):
            try:
                tmp_model_mgr = db_util.run_in_transaction(function)
            except CabaretError, err:
                print "An error occured when tring to update %s", cls
                print "error...%s" % err.value
                return

            tmp_model_mgr.write_end()

        def migrate_cards(uid1, uid2):
            def tr_migrate_cards():
                print "migrating cards to uid : %d" % uid2
                model_mgr = ModelRequestMgr()
                player1_cardlist = BackendApi.get_card_list(uid1, arg_model_mgr=model_mgr, using=backup_db)
                cardidlist = [card.master.id for card in player1_cardlist]
                prizelist = [PrizeData.create(cardid=cardid, cardnum=1) for cardid in cardidlist]

                for prize in prizelist:
                    BackendApi.tr_add_prize(model_mgr, uid2, [prize], 0)
                    model_mgr.write_all()

                print "finished migrating cards"

                print "========================"
                print "Migrating album data"
                print "========================"
                userlog = UserLogEvolution.fetchValues(filters={'uid': uid1}, using=backup_db)
                cardidlist = [log.data['base']['mid'] for log in userlog]
                cardmasters = BackendApi.get_cardmasters(cardidlist, model_mgr, using=backup_db)
                print "ID of cards previously gotten through evolution (ハメ管理):", cardidlist

                # set card acquisition and album acquisition for these cards
                for _, master in cardmasters.items():
                    BackendApi.tr_set_cardacquisition(model_mgr, uid2, master)

                model_mgr.write_all()

                return model_mgr

            write_end(tr_migrate_cards, "Cards")

        def set_player_exp(player1, player2):
            def tr_recover_exp():
                model_mgr = ModelRequestMgr()
                new_player_exp = PlayerExp.getByKeyForUpdate(player2.id)
                new_player_exp.exp = 0
                print "Before | exp = %s, level = %s" % (new_player_exp.exp, new_player_exp.level)
                model_mgr.set_got_models([new_player_exp])
                model_mgr.set_got_models([model_cls.getByKeyForUpdate(player2.id) for model_cls in (PlayerDeck, PlayerAp, PlayerFriend)])
                BackendApi.tr_add_exp(model_mgr, player2, player1.exp)
                model_mgr.write_all()
                print "After  | exp = %s, level = %s" % (new_player_exp.exp, new_player_exp.level)
                return model_mgr

            write_end(tr_recover_exp, 'PlayerExp')

        def set_player_gold(user1, user2):
            def tr_recover_gold():
                model_mgr = ModelRequestMgr()
                print "Before | gold = %s" % user2.gold
                BackendApi.tr_add_gold(model_mgr, user2.id, user1.gold)
                model_mgr.write_all()
                print "After  | gold = %s" % user2.gold
                return model_mgr

            write_end(tr_recover_gold, 'PlayerGold')

        # Migrate player exp, level and hp
        print '================================'
        print 'Migrating experience, level and hp from player(uid: %d) to player(uid: %d)' % (old_uid, new_uid)
        set_player_exp(player1, player2)
        print 'Finished'

        # Migrating player gold count
        print '================================'
        print 'Migrating gold from player(uid: %d) to player(uid: %d)' % (old_uid, new_uid)
        set_player_gold(player1, player2)
        print 'Finished migrating gold'

        # Migrate player cards
        print '================================'
        print 'Migrating cards from player(uid: %d) to player(uid: %d)' % (old_uid, new_uid)
        migrate_cards(player1.id, player2.id)
        print 'Finished migrating cards'

        # Display player items
        print '================================'
        print 'Displaying player items from player(uid: %d)' % old_uid
        self.get_item_nums(model_mgr, old_uid, using=settings.DB_DEFAULT)
        print 'Finished displaying items'

        print '================================'
        print 'all done..'

    def get_item_nums(self, model_mgr, uid, using=settings.DB_DEFAULT):
        """
            Return the number of items a user of id <<uid>> has.
            A dictionary of {item_id:item_count} is returned
        """
        itemmasterlist = model_mgr.get_mastermodel_all(ItemMaster, using=using)
        itemdict = {}
        for item in itemmasterlist:
            itemdict[item.id] = item
        item_nums = BackendApi.get_item_nums(model_mgr, uid, itemdict.keys(), using=using)

        for itemid, num in item_nums.items():
            print "%s x%d%s" % (itemdict[itemid].name, num, itemdict[itemid].unit)

        return item_nums
