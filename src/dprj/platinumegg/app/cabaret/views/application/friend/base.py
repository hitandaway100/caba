# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerFriend, PlayerExp
import settings
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.lib.opensocial.util import OSAUtil


class FriendHandler(AppHandler):
    """仲間関係.
    """
    def putFriendNum(self):
        v_player = self.getViewerPlayer()
        #現在の仲間人数.
        friendnum = BackendApi.get_friend_num(v_player.id, self.getModelMgr(), using=settings.DB_READONLY)
        self.html_param['friendnum'] = friendnum
        #仲間人数の上限.
        friendnummax = v_player.friendlimit
        self.html_param['friendnummax'] = friendnummax
        #申請できる数.
        receivenum = BackendApi.get_friendrequest_receive_num(v_player.id, self.getModelMgr(), using=settings.DB_READONLY)
        sendnum = BackendApi.get_friendrequest_send_num(v_player.id, self.getModelMgr(), using=settings.DB_READONLY)
        rest = max(0, friendnummax - (friendnum + receivenum + sendnum))
        self.html_param['restnum'] = rest
    
    def getObjPlayerList(self, playeridlist, do_execute=True, do_set_greet=False):
        arr = []
        if playeridlist:
            playerlist = BackendApi.get_players(self, playeridlist, [PlayerFriend, PlayerExp], using=settings.DB_READONLY)
            playerlist.sort(key=lambda x:playeridlist.index(x.id))
            
            persons = BackendApi.get_dmmplayers(self, playerlist, do_execute=False, using=settings.DB_READONLY)
            leaders = BackendApi.get_leaders(playeridlist, self.getModelMgr(), using=settings.DB_READONLY)
            
            model_mgr = self.getModelMgr()
            
            if do_set_greet:
                v_player = self.getViewerPlayer()
                greettimes = BackendApi.get_greettimes(model_mgr, v_player.id, playeridlist, using=settings.DB_READONLY)
            else:
                greettimes = {}
            
            friendnums = {}
            for playerid in playeridlist:
                friendnums[playerid] = BackendApi.get_friend_num(playerid, model_mgr, using=settings.DB_READONLY)
            
            now = OSAUtil.get_now()
            if do_execute:
                self.execute_api()
            for player in playerlist:
                gtime = greettimes.get(player.id)
                data = Objects.player(self, player, persons.get(player.dmmid), leaders.get(player.id))
                data['friendnum'] = friendnums.get(player.id, 0)
                data['greetflag'] = not BackendApi.check_greettime(gtime, now)
                arr.append(data)
        return arr
