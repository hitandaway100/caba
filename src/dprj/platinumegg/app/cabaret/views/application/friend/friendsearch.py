# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerFriend
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.views.application.friend.base import FriendHandler


class Handler(FriendHandler):
    """仲間相手検索.
    現在の仲間人数.
    仲間人数の上限.
    プレイヤー一覧.
    更新URL.
    引数:
         レベル帯.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerFriend]
    
    def process(self):
        
        try:
            # レベル帯.
            lvgrp = int(self.request.get(Defines.URLQUERY_LEVELGROUP) or Defines.LevelGroup.LV01_09)
            if not Defines.LevelGroup.NAMES.has_key(lvgrp):
                raise
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        self.putFriendNum()
        
        #プレイヤー一覧.
        ignorelist = [v_player.id]
        ignorelist.extend(BackendApi.get_friend_idlist(v_player.id, arg_model_mgr=model_mgr, using=settings.DB_READONLY))
        ignorelist.extend(BackendApi.get_friendrequest_send_idlist(v_player.id, arg_model_mgr=model_mgr, using=settings.DB_READONLY))
        ignorelist.extend(BackendApi.get_friendrequest_receive_idlist(v_player.id, arg_model_mgr=model_mgr, using=settings.DB_READONLY))
        playeridlist = BackendApi.serch_playerid_bylevelgroup(lvgrp, Defines.FRIEND_PAGE_CONTENT_NUM, ignorelist, model_mgr)
        playerlist = None
        if playeridlist:
            playerlist = self.getObjPlayerList(playeridlist)
        
        self.html_param['playerlist'] = playerlist or []
        
        #更新URL.
        url = OSAUtil.addQuery(UrlMaker.friendsearch(), Defines.URLQUERY_LEVELGROUP, lvgrp)
        self.html_param['url_reload'] = self.makeAppLinkUrl(url)
        
        # select.
        self.html_param['LevelGroup'] = Defines.LevelGroup.NAMES.items()
        
        # 選択中のグループ.
        self.html_param[Defines.URLQUERY_LEVELGROUP] = lvgrp
        
        self.writeAppHtml('friend/search')
    

def main(request):
    return Handler.run(request)
