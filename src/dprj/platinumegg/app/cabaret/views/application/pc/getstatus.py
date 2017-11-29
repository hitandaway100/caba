# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerLogin, PlayerRegist,\
    PlayerTutorial, PlayerExp, PlayerGold, PlayerAp, PlayerDeck, PlayerFriend,\
    PlayerGachaPt, PlayerRequest
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from defines import Defines


class Handler(AppHandler):
    """PC版のマイページワイヤーフレームのコンテンツ更新用.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [
            PlayerRegist,
            PlayerTutorial,
            PlayerExp,
            PlayerGold,
            PlayerAp,
            PlayerDeck,
            PlayerFriend,
            PlayerGachaPt,
            PlayerLogin,
            PlayerRequest,
        ]
    
    def process(self):
        v_player = self.getViewerPlayer(quiet=True)
        if v_player is None or v_player.getModel(PlayerTutorial) is None or v_player.tutorialstate != Defines.TutorialStatus.COMPLETED:
            # チュートリアル中.
            self.response.set_status(404)
            self.response.end()
            return
        
        self.putCardInfo()
        self.putFriendNum()
        self.putPlayerInfo()
        
        self.writeAppJson()
    
    def putPlayerInfo(self):
        """プレイヤー情報.
        """
        v_player = self.getViewerPlayer()
        person = BackendApi.get_dmmplayers(self, [v_player], using=settings.DB_READONLY).get(v_player.dmmid)
        self.json_param['player'] = Objects.player(self, v_player, person)
    
    def putCardInfo(self):
        """カードの情報.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        deck = BackendApi.get_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
        cardlist = BackendApi.get_cards(deck.to_array(), model_mgr, using=settings.DB_READONLY)
        
        # 接客力の合計.
        power_total = 0
        for card in cardlist:
            power_total += card.power
        self.json_param['power_total'] = power_total
        
        # デッキのカードをランダムで表示.
        #disp_members = cardlist[:]
        #random.shuffle(disp_members)
        #cardset = disp_members[0]
        #self.json_param['card'] = Objects.card(self, cardset, deck)
        
        # カード枚数.
        self.json_param['card_num'] = BackendApi.get_cardnum(v_player.id, model_mgr, using=settings.DB_READONLY)
    
    def putFriendNum(self):
        """フレンド数.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        friend_num = BackendApi.get_friend_num(v_player.id, model_mgr, using=settings.DB_READONLY)
        self.json_param['friend_num'] = friend_num
    
def main(request):
    return Handler.run(request)
