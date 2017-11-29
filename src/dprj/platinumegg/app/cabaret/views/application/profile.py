# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerLogin,\
    PlayerTutorial, PlayerExp, PlayerGold, PlayerAp, PlayerDeck, PlayerFriend,\
    PlayerGachaPt, PlayerComment
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines


class Handler(AppHandler):
    """プロフィールページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [
        ]
    
    def process(self):
        
        args = self.getUrlArgs('/profile/')
        owner_id = args.get(0, None)
        if owner_id is None or not str(owner_id).isdigit():
            raise CabaretError(u'表示するユーザIDが指定されていません.')
        
        v_player = self.getViewerPlayer()
        owner_id = int(owner_id)
        if owner_id == v_player.id:
            url = UrlMaker.mypage()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        clslist = [
            PlayerTutorial,
            PlayerExp,
            PlayerGold,
            PlayerAp,
            PlayerDeck,
            PlayerFriend,
            PlayerGachaPt,
            PlayerLogin,
            PlayerComment,
        ]
        playerlist = BackendApi.get_players(self, [owner_id], clslist, using=settings.DB_READONLY)
        o_player = None
        if 0 < len(playerlist):
            o_player = playerlist[0]
        
        if o_player is None or not o_player.is_tutorialend():
            raise CabaretError(u'このユーザIDは閲覧出来ません.')
        
        comments = self.readyProfileCommentRequest(o_player)
        
        self.putCardInfo(o_player)
        self.putFriendInfos(o_player)
        self.putBattleKOs(o_player)
        self.putRareLog(o_player)
        self.putGreetLog(o_player)
        
        persons = self.getDmmPlayerInfo(o_player)
        
        self.putIgnorelist(o_player)
        
        self.putPlayerInfo(o_player, persons.get(o_player.dmmid))
        self.putProfileComment(o_player, comments)

        if self.getFromPageName() == Defines.FromPages.CABACLUB_STORE:
            args = self.getFromPageArgs()
            mid = int(args[0]) if args and str(args[0]).isdigit() else None
            self.html_param['frompage_url'] = self.makeAppLinkUrlRedirect(UrlMaker.cabaclubrank(mid), add_frompage=False)
        
        self.writeAppHtml('profile')
    
    def putIgnorelist(self, o_player):
        """ブラックリストチェック.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        self.html_param['is_blacklist'] = not BackendApi.check_blacklist(self, v_player.id, o_player.id, model_mgr)
    
    def getDmmPlayerInfo(self, o_player):
        """プレイヤー情報.
        """
        return BackendApi.get_dmmplayers(self, [o_player], using=settings.DB_READONLY, do_execute=False)
    
    def putPlayerInfo(self, o_player, person):
        """プレイヤー情報.
        """
        self.html_param['player'] = Objects.player(self, o_player, person)
    
    def putCardInfo(self, o_player):
        """カードの情報.
        """
        model_mgr = self.getModelMgr()
        deck = BackendApi.get_deck(o_player.id, model_mgr, using=settings.DB_READONLY)
        leader = BackendApi.get_cards([deck.leader], model_mgr, using=settings.DB_READONLY)[0]
        # リーダー情報.
        self.html_param['leader'] = Objects.card(self, leader)
        
        cardlist = BackendApi.get_profile_newbie_cardlist(model_mgr, o_player.id, excludes=[deck.leader], using=settings.DB_READONLY)
        self.html_param['newbie_cardlist'] = [Objects.card(self, card) for card in cardlist]
    
    def putFriendInfos(self, o_player):
        """仲間関係の情報とか.
        """
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        # 仲間かどうか.
        self.html_param['is_friend'] = BackendApi.check_friend(v_player.id, o_player.id, model_mgr, using=settings.DB_READONLY)
        # 仲間申請中かどうか.
        self.html_param['did_send_friendrequest'] = BackendApi.check_friendrequest_send(v_player.id, o_player.id, model_mgr, using=settings.DB_READONLY)
        # 仲間申請を受けているかどうか.
        self.html_param['receive_friendrequest'] = BackendApi.check_friendrequest_receive(v_player.id, o_player.id, model_mgr, using=settings.DB_READONLY)
        # 仲間数.
        self.html_param['friend_num'] = BackendApi.get_friend_num(o_player.id, model_mgr, using=settings.DB_READONLY)
    
    def readyProfileCommentRequest(self, o_player):
        """コメント.
        """
        model_mgr = self.getModelMgr()
        comments = BackendApi.get_profile_comment(self, [o_player], model_mgr, do_execute=False)
        return comments
    
    def putProfileComment(self, o_player, comments):
        """コメント.
        """
        model = o_player.getModel(PlayerComment)
        comment = u''
        if model is not None:
            comments.get(model.commentid, comment)
        self.html_param['profilecomment'] = comment
    
    def putBattleKOs(self, o_player):
        """戦績.
        """
        model_mgr = self.getModelMgr()
        self.html_param['battlekos'] = BackendApi.get_battleKOs(o_player.id, model_mgr, using=settings.DB_READONLY)
    
    def putRareLog(self, o_player):
        """レアキャバ嬢獲得履歴.
        """
        model_mgr = self.getModelMgr()
        self.html_param['rarelog'] = BackendApi.get_rarelog(self, o_player.id, model_mgr, using=settings.DB_READONLY)
    
    def putGreetLog(self, o_player):
        """あいさつ履歴.
        """
        NUM = 2
        model_mgr = self.getModelMgr()
        self.html_param['greetlog_list'] = BackendApi.get_greetlog_list(self, o_player.id, limit=NUM, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
        self.html_param['url_greetlog'] = self.makeAppLinkUrl(UrlMaker.greetlog(o_player.id))

def main(request):
    return Handler.run(request)
