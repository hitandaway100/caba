# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from  platinumegg.app.cabaret.models.Player import PlayerDeck
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import time

class Command(BaseCommand):
    """
    Insert (update) the deck cost for current users
    """

    def handle(self, *args, **options):

        print "==============================="
        print "insert_user_deckcost"
        print "==============================="

        model_mgr = ModelRequestMgr()

        def calculate_deck_cost(uidlist):

            decks = BackendApi.get_decks(uidlist, using=settings.DB_READONLY)
            deckcost = {}
            for uid, deck in decks.items():
                cost = sum([x.master.cost for x in BackendApi.get_cards(deck.to_array())])
                deckcost[uid] = cost
            return deckcost

        limit = 1000
        offset = 0

        while True:
            playerdeck = PlayerDeck.fetchValues(limit=limit,offset=offset, using=settings.DB_DEFAULT)
            if not playerdeck:
                break

            playerdeck_dict = {p.id: p for p in playerdeck}
            player_deckcost = calculate_deck_cost(playerdeck_dict.keys())

            for uid, deck_cost in player_deckcost.items():
                player = playerdeck_dict[uid]
                player.deckcost = deck_cost
                model_mgr.set_save(player)
            offset += limit

            def tr_update():
                model_mgr.write_all()
                model_mgr.write_end()
                return model_mgr

            try:
                tmp_model_mgr = db_util.run_in_transaction(tr_update)
            except CabaretError, err:
                print "error ...%s" % err.value
                return

            tmp_model_mgr.write_end()

        print "==============================="
        print "insertion complete"
        print "==============================="
