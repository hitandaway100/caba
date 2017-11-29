# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerFriend
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.views.application.friend.base import FriendHandler


class Handler(FriendHandler):
    """仲間Topページ.
    現在の仲間人数.
    仲間人数の上限.
    仲間申請相手検索へのURL.
    おまかせ申請へのURL
    プレイヤーリスト.
    次のページのURL.
    前のページのURL.
    タブ切り替えURL.
    引数:
        仲間 or 申請中 or 承認待ち.
        ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerFriend]
    
    def process(self):
        
        page = 0
        try:
            # 仲間 or 申請中 or 承認待ち.
            state = int(self.request.get(Defines.URLQUERY_STATE) or Defines.FriendState.ACCEPT)
            if not Defines.FriendState.NAMES.has_key(state):
                raise
            # ページ.
            page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
            er_code = int(self.request.get(Defines.URLQUERY_ERROR) or 0)
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        using = settings.DB_READONLY
        
        # プレイヤー情報.
        persons = BackendApi.get_dmmplayers(self, [v_player], using=settings.DB_READONLY, do_execute=False)
        
        self.putFriendNum()
        
        # プレイヤーリスト.
        offset = page * Defines.FRIEND_PAGE_CONTENT_NUM
        limit = Defines.BOX_PAGE_CONTENT_NUM + 1
        
        do_set_greet = False
        if state == Defines.FriendState.ACCEPT:
            playeridlist = BackendApi.get_friend_idlist(v_player.id, offset, limit, model_mgr, using)
            num_max = BackendApi.get_friend_num(v_player.id, model_mgr, using)
            htmlname = 'friend/friend'
            self.setFromPage(Defines.FromPages.FRIENDLIST)
            do_set_greet = True
        elif state == Defines.FriendState.SEND:
            playeridlist = BackendApi.get_friendrequest_send_idlist(v_player.id, offset, limit, model_mgr, using)
            num_max = BackendApi.get_friendrequest_send_num(v_player.id, model_mgr, using)
            htmlname = 'friend/requestlist'
            self.setFromPage(Defines.FromPages.FRIENDREQUEST)
        elif state == Defines.FriendState.RECEIVE:
            playeridlist = BackendApi.get_friendrequest_receive_idlist(v_player.id, offset, limit, model_mgr, using)
            num_max = BackendApi.get_friendrequest_receive_num(v_player.id, model_mgr, using)
            htmlname = 'friend/receivelist'
            self.setFromPage(Defines.FromPages.FRIENDRECEIVE)
        else:
            raise CabaretError(u'未実装です')
        
        playerlist = []
        has_next = False
        if playeridlist:
            if Defines.FRIEND_PAGE_CONTENT_NUM < len(playeridlist):
                has_next = True
                playeridlist = playeridlist[:Defines.FRIEND_PAGE_CONTENT_NUM]
            playerlist = self.getObjPlayerList(playeridlist, do_set_greet=do_set_greet)
        if not playerlist:
            self.execute_api()
        
        self.html_param['playerlist'] = playerlist
        
        #次のページのURL.
        urlbase = OSAUtil.addQuery(UrlMaker.friendlist(), Defines.URLQUERY_STATE, state)
        if has_next:
            self.html_param['url_page_next'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_PAGE, page+1))
        
        #前のページのURL.
        if 0 < page:
            self.html_param['url_page_prev'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_PAGE, page-1))
        
        self.html_param['cur_page'] = page + 1
        self.html_param['page_max'] = max(1, int((num_max + Defines.FRIEND_PAGE_CONTENT_NUM - 1) / Defines.FRIEND_PAGE_CONTENT_NUM))
        self.html_param['cur_topic'] = Defines.FriendState.TOPICS[state]
        
        # タブ切り替えURL.
        url = UrlMaker.friendlist()
        self.html_param['url_friendlist'] = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_STATE, Defines.FriendState.ACCEPT))
        self.html_param['url_requestlist'] = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_STATE, Defines.FriendState.SEND))
        self.html_param['url_receivelist'] = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_STATE, Defines.FriendState.RECEIVE))
        
        self.html_param['player'] = Objects.player(self, v_player, persons.get(v_player.dmmid))
        
        self.html_param['error_overlimit'] = er_code == CabaretError.Code.OVER_LIMIT
        self.html_param['error_nodata'] = er_code == CabaretError.Code.NOT_DATA
        
        #仲間申請相手検索へのURL.
        url = UrlMaker.friendsearch()
        self.html_param['url_friendsearch'] = self.makeAppLinkUrl(url)
        
        #おまかせ申請へのURL
        url = UrlMaker.friendrequest_auto()
        self.html_param['url_friendrequest_auto'] = self.makeAppLinkUrl(url)
        
        self.writeAppHtml(htmlname)
    

def main(request):
    return Handler.run(request)
