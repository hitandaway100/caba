# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerFriend, PlayerExp
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.views.application.friend.base import FriendHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util import db_util
from defines import Defines


class Handler(FriendHandler):
    """仲間申請承認 or 拒否.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerFriend, PlayerExp]
    
    def process(self):
        args = self.getUrlArgs('/friendreceive/')
        procname = args.get(0)
        fid = args.get(1)
        accept = args.get(2)
        table = {
            'yesno' : self.procYesno,
            'do' : self.procDo,
            'complete' : self.procComplete,
        }
        f = table.get(procname)
        if not f or not fid.isdigit() or not accept in ('0', '1'):
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        fid = int(fid)
        accept = bool(int(accept))
        
        v_player = self.getViewerPlayer()
        
        self.putFriendNum()
        
        f(v_player, fid, accept)
    
    def procYesno(self, v_player, fid, accept):
        """承認・拒否確認.
        """
        model_mgr = self.getModelMgr()
        uid = v_player.id
        
        if not BackendApi.check_friendrequest_receive(uid, fid, model_mgr, using=settings.DB_READONLY):
            raise CabaretError(u'フレンド申請を受け取っていません', CabaretError.Code.NOT_DATA)
        
        playerlist = self.getObjPlayerList([fid])
        if len(playerlist) == 0:
            raise CabaretError(u'存在しないプレイヤーです', CabaretError.Code.NOT_DATA)
        
        player = playerlist[0]
        self.html_param['player'] = playerlist[0]
        
        if accept:
            player['url_friendrequest_accept'] = self.makeAppLinkUrl(UrlMaker.friendreceive_do(fid, True))
            self.writeAppHtml('friend/acceptyesno')
        else:
            player['url_friendrequest_veto'] = self.makeAppLinkUrl(UrlMaker.friendreceive_do(fid, False))
            self.writeAppHtml('friend/vetoyesno')
    
    def procDo(self, v_player, fid, accept):
        """承認・拒否書き込み.
        """
        o_playerlist = BackendApi.get_players(self, [fid], [PlayerFriend], using=settings.DB_READONLY)
        if len(o_playerlist) == 0:
            raise CabaretError(u'存在しないプレイヤーです', CabaretError.Code.NOT_DATA)
        
        try:
            db_util.run_in_transaction(Handler.tr_write, v_player, o_playerlist[0], accept)
        except:
            BackendApi.delete_friendidlistset(v_player.id)
            raise
        
        # リダイレクト.
        url = UrlMaker.friendreceive_complete(fid, accept)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def procComplete(self, v_player, fid, accept):
        """承認・拒否完了.
        """
        
        obj_playerlist = self.getObjPlayerList([fid])
        
        if len(obj_playerlist) == 0:
            raise CabaretError(u'存在しないプレイヤーです', CabaretError.Code.NOT_DATA)
        self.html_param['player'] = obj_playerlist[0]
        
        if accept:
            self.writeAppHtml('friend/acceptcomplete')
        else:
            self.writeAppHtml('friend/vetocomplete')
    
    @staticmethod
    def tr_write(v_player, o_player, accept):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        if accept:
            BackendApi.tr_add_friend(model_mgr, v_player.id, o_player.id)
        else:
            BackendApi.tr_delete_friendrequest(model_mgr, o_player.id, v_player.id)
        model_mgr.write_all()
        model_mgr.write_end()
        return model_mgr
    
    

def main(request):
    return Handler.run(request)
