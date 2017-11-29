# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerFriend, PlayerExp
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.views.application.friend.base import FriendHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util import db_util
import settings_sub


class Handler(FriendHandler):
    """仲間申請.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerFriend, PlayerExp]
    
    def process(self):
        args = self.getUrlArgs('/friendrequest/')
        procname = args.get(0)
        table = {
            'auto' : self.procAuto,
            'yesno' : self.procYesno,
            'do' : self.procDo,
            'complete' : self.procComplete,
        }
        f = table.get(procname)
        if not f:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        
        self.putFriendNum()
        
        f(v_player, args)
    
    def procAuto(self, v_player, args):
        """一括送信.
        """
        def redirectWithError(err_code):
            fromname = self.getFromPageName()
            url = UrlMaker.friendlist()
            url = OSAUtil.addQuery(url, Defines.URLQUERY_ERROR, err_code)
            if fromname == Defines.FromPages.FRIENDREQUEST:
                url = OSAUtil.addQuery(url, Defines.URLQUERY_STATE, Defines.FriendState.SEND)
            elif fromname == Defines.FromPages.FRIENDRECEIVE:
                url = OSAUtil.addQuery(url, Defines.URLQUERY_STATE, Defines.FriendState.RECEIVE)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
        
        rest = self.html_param['restnum']
        limit = min(Defines.FRIEND_PAGE_CONTENT_NUM, rest)
        if limit == 0:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'これ以上申請出来ません', CabaretError.Code.OVER_LIMIT)
            else:
                redirectWithError(CabaretError.Code.OVER_LIMIT)
                return
        
        model_mgr = self.getModelMgr()
        ignorelist = [v_player.id]
        ignorelist.extend(BackendApi.get_friend_idlist(v_player.id, arg_model_mgr=model_mgr, using=settings.DB_READONLY))
        ignorelist.extend(BackendApi.get_friendrequest_send_idlist(v_player.id, arg_model_mgr=model_mgr, using=settings.DB_READONLY))
        ignorelist.extend(BackendApi.get_friendrequest_receive_idlist(v_player.id, arg_model_mgr=model_mgr, using=settings.DB_READONLY))
        
        level_min, level_max = BackendApi.get_friendcandidate_range(v_player.level)
        playeridlist = BackendApi.serch_playerid_bylevel(level_min, level_max, limit + 20, ignorelist, model_mgr)
        
        o_player_list = BackendApi.get_players(self, playeridlist, [PlayerFriend], using=settings.DB_READONLY, model_mgr=model_mgr)
        
        ok_list = []
        for o_player in o_player_list:
            friend_num = BackendApi.get_friend_num(o_player.id, model_mgr, using=settings.DB_READONLY)
            if o_player.friendlimit <= friend_num:
                continue
            friend_num += BackendApi.get_friendrequest_send_num(o_player.id, model_mgr, using=settings.DB_READONLY)
            if o_player.friendlimit <= friend_num:
                continue
            friend_num += BackendApi.get_friendrequest_receive_num(o_player.id, model_mgr, using=settings.DB_READONLY)
            if o_player.friendlimit <= friend_num:
                continue
            ok_list.append(o_player.id)
            if limit <= len(ok_list):
                break
        
        if len(ok_list) == 0:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'見つかりませんでした', CabaretError.Code.NOT_DATA)
            else:
                redirectWithError(CabaretError.Code.NOT_DATA)
                return
        
        str_playeridlist = ','.join([str(playerid) for playerid in ok_list])
        url = UrlMaker.friendrequest_do()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_USERID, str_playeridlist)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def procYesno(self, v_player, args):
        """申請確認.
        """
        try:
            # 相手のID.
            fid = int(args.get(1))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        playerlist = self.getObjPlayerList([fid])
        if len(playerlist) == 0:
            raise CabaretError(u'存在しないプレイヤーです', CabaretError.Code.NOT_DATA)
        player = playerlist[0]
        
        url = UrlMaker.friendrequest_do()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_USERID, fid)
        player['url_friendrequest_send'] = self.makeAppLinkUrl(url)
        self.html_param['player'] = player
        
        #フレンド検索URL.
        lvgrp = int(Defines.LevelGroup.LV01_09)
        url = OSAUtil.addQuery(UrlMaker.friendsearch(), Defines.URLQUERY_LEVELGROUP, lvgrp)
        self.html_param['url_search'] = self.makeAppLinkUrl(url)
        
        self.writeAppHtml('friend/sendyesno')
    
    def procDo(self, v_player, args):
        """申請書き込み.
        """
        try:
            # 相手のID.
            strfidlist = self.request.get(Defines.URLQUERY_USERID)
            fidlist = list(set([int(fid) for fid in strfidlist.split(',')]))
            if Defines.FRIEND_PAGE_CONTENT_NUM < len(fidlist):
                # これは不正でしょう.
                raise CabaretError()
        except:
            raise CabaretError(u'送信できないプレイヤーです', CabaretError.Code.ILLEGAL_ARGS)
        
        o_playerlist = BackendApi.get_players(self, fidlist, [PlayerFriend], using=settings.DB_READONLY)
        if len(o_playerlist) == 0:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'見つかりませんでした', CabaretError.Code.NOT_DATA)
            else:
                fromname = self.getFromPageName()
                url = UrlMaker.friendlist()
                url = OSAUtil.addQuery(url, Defines.URLQUERY_ERROR, CabaretError.Code.NOT_DATA)
                if fromname == Defines.FromPages.FRIENDREQUEST:
                    url = OSAUtil.addQuery(url, Defines.URLQUERY_STATE, Defines.FriendState.SEND)
                elif fromname == Defines.FromPages.FRIENDRECEIVE:
                    url = OSAUtil.addQuery(url, Defines.URLQUERY_STATE, Defines.FriendState.RECEIVE)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        
        try:
            db_util.run_in_transaction(Handler.tr_write, v_player, o_playerlist)
        except:
            BackendApi.delete_friendidlistset(v_player.id)
            raise
        
        # リダイレクト.
        url = UrlMaker.friendrequest_complete()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_USERID, ','.join([str(o_player.id) for o_player in o_playerlist]))
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def procComplete(self, v_player, args):
        """申請完了.
        """
        try:
            # 相手のID.
            strfidlist = self.request.get(Defines.URLQUERY_USERID)
            fidlist = [int(fid) for fid in strfidlist.split(',')]
            if Defines.FRIEND_PAGE_CONTENT_NUM < len(fidlist):
                # これは不正でしょう.
                raise
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        self.html_param['playerlist'] = self.getObjPlayerList(fidlist)
        
        self.writeAppHtml('friend/sendcomplete')
    
    @staticmethod
    def tr_write(v_player, o_playerlist):
        """送信書き込み.
        """
        model_mgr = ModelRequestMgr()
        for o_player in o_playerlist:
            BackendApi.tr_add_friendrequest(model_mgr, v_player, o_player)
        model_mgr.write_all()
        model_mgr.write_end()
        return model_mgr
    
    

def main(request):
    return Handler.run(request)
