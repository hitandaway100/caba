# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.models.Player import PlayerRegist, PlayerTutorial,\
    PlayerExp, PlayerGold, PlayerAp, PlayerDeck, PlayerFriend, PlayerGachaPt,\
    PlayerTreasure, PlayerLogin, PlayerComment, PlayerKey

class Handler(AppHandler):
    """プレイヤー情報を返す.
    """
    VIEWER_MODELS = (
        PlayerRegist,
        PlayerTutorial,
        PlayerExp,
        PlayerGold,
        PlayerAp,
        PlayerDeck,
        PlayerFriend,
        PlayerGachaPt,
        PlayerTreasure,
        PlayerLogin,
        PlayerComment,
        PlayerKey,
    )
    OTHERS_MODELS = (
        PlayerRegist,
        PlayerExp,
        PlayerDeck,
        PlayerFriend,
        PlayerLogin,
        PlayerComment,
    )
    
    def process(self):
        
        try:
            str_idlist = self.request.get(Defines.URLQUERY_ID, '').split(',')
            uidlist = list(set([int(str_id) for str_id in str_idlist if str_id.isdigit()]))
        except:
            uidlist = None
        
        v_player = self.getViewerPlayer()
        viewer_id = v_player.id
        
        playerlist = None
        if uidlist:
            tmp_uidlist = uidlist[:]
            playerlist = []
            
            if viewer_id in tmp_uidlist:
                # 自分自身.
                tmp_uidlist.remove(viewer_id)
                playerlist.append(BackendApi.get_players(self, [viewer_id], Handler.VIEWER_MODELS, using=settings.DB_READONLY)[0])
            # 他のプレイヤー.
            playerlist.extend(BackendApi.get_players(self, tmp_uidlist, Handler.OTHERS_MODELS, using=settings.DB_READONLY))
        
        if not playerlist:
            raise CabaretError(u'指定したプレイヤーが見つかりませんでした', CabaretError.Code.NOT_DATA)
        
        # リーダーカード.
        model_mgr = self.getModelMgr()
        leaders = BackendApi.get_leaders(uidlist, model_mgr, using=settings.DB_READONLY)
        
        # レスポンス用のオブジェクトに変換.
        obj_playerlist = [Objects.player(self, player, leader=leaders[player.id]) for player in playerlist]
        self.json_result_param['playerlist'] = obj_playerlist
        
        self.writeAppJson()
    
def main(request):
    return Handler.run(request)
