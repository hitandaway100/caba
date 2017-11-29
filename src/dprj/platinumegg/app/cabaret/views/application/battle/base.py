# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerFriend, PlayerExp
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.url_maker import UrlMaker


class BattleHandler(AppHandler):
    """PVP関係.
    """
    def preprocess(self):
        AppHandler.preprocess(self)
        self.__battleplayer = None
        self.__rankmaster = None
    
    def getBattlePlayer(self, get_instance=False, using=settings.DB_READONLY):
        """バトルのプレイヤー情報.
        """
        if self.__battleplayer is None:
            model_mgr = self.getModelMgr()
            v_player = self.getViewerPlayer()
            self.__battleplayer = BackendApi.get_battleplayer(model_mgr, v_player.id, get_instance=get_instance, using=using)
        return self.__battleplayer
    
    def getBattleRankMaster(self):
        """ランクのマスター.
        """
        if self.__rankmaster is None:
            model_mgr = self.getModelMgr()
            battleplayer = self.getBattlePlayer()
            if battleplayer:
                self.__rankmaster = BackendApi.get_battlerank(model_mgr, battleplayer.rank, using=settings.DB_READONLY)
        return self.__rankmaster
    
    def redirectToOppSelect(self):
        battleplayer = self.getBattlePlayer()
        post_cnt = (battleplayer.change_cnt + 1) if battleplayer else 0
        url = UrlMaker.battleoppselect(post_cnt)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def getObjPlayerList(self, playerlist):
        obj_list = []
        if playerlist:
            model_mgr = self.getModelMgr()
            
            persons = BackendApi.get_dmmplayers(self, playerlist, using=settings.DB_READONLY, do_execute=False)
            
            self.execute_api()
            
            for player in playerlist:
                
                deck = BackendApi.get_deck(player.id, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
                cardsetlist = BackendApi.get_cards(deck.to_array(), arg_model_mgr=model_mgr, using=settings.DB_READONLY)
                leader = cardsetlist[0]
                
                obj_player = Objects.player(self, player, persons.get(player.dmmid), leader)
                power_total = leader.power
                
                deckmember = []
                for cardset in cardsetlist[1:]:
                    obj_card = Objects.card(self, cardset)
                    power_total += obj_card['power']
                    deckmember.append(obj_card)
                obj_player['deckmember'] = deckmember
                obj_player['power_total'] = power_total
                obj_list.append(obj_player)
        return obj_list
    
    def getObjPlayerListByID(self, playeridlist):
        if not playeridlist:
            return []
        else:
            playerlist = BackendApi.get_players(self, playeridlist, [PlayerFriend, PlayerExp], using=settings.DB_READONLY)
            return self.getObjPlayerList(playerlist)
    
    def getObjPlayerListByBattleResult(self, uid, battleresultlist):
        if not battleresultlist:
            return []
        
        playeridlist = list(set([battleresult.oid if battleresult.uid==uid else battleresult.uid for battleresult in battleresultlist]))
        playerlist = BackendApi.get_players(self, list(set(playeridlist)), [PlayerFriend, PlayerExp], using=settings.DB_READONLY)
        obj_playerlist = self.getObjPlayerList(playerlist)
        
        obj_playerdict = {}
        for obj_player in obj_playerlist:
            pid = obj_player['id']
            obj_playerdict[pid] = obj_player
        
        arr = []
        for battleresult in battleresultlist:
            oid = battleresult.oid if battleresult.uid==uid else battleresult.uid
            obj_player = obj_playerdict.get(oid)
            if not obj_player:
                continue
            obj_player['receive'] = battleresult.uid != uid
            obj_player['btime'] = battleresult.ctime.strftime("%Y/%m/%d %H:%M:%S")
            arr.append(obj_player)
        return arr
