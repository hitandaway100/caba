# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerDeck,\
    PlayerAp, PlayerFriend
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util import db_util

class Command(BaseCommand):
    """壊れた経験値を修復.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'recov_exp'
        print '================================'
        
        uid = int(args[0])
        exp = int(args[1])
        
        def tr():
            model_mgr = ModelRequestMgr()
            player = BackendApi.get_player(None, uid, [], model_mgr=model_mgr)
            player_exp = PlayerExp.getByKeyForUpdate(uid)
            player_exp.exp = 0
            model_mgr.set_got_models([player_exp])
            model_mgr.set_got_models([model_cls.getByKeyForUpdate(uid) for model_cls in (PlayerDeck, PlayerAp, PlayerFriend)])
            
            BackendApi.tr_add_exp(model_mgr, player, exp)
            model_mgr.write_all()
            
            print "level=%s,exp=%s" % (player_exp.level, player_exp.exp)
            
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        print '================================'
        print 'all done..'
