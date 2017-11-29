# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerDeck,\
    PlayerFriend


class Handler(AppHandler):
    """アイテムリスト.
    表示するもの.
        アイテム名.
        個数(単位つき).
        アイテム説明.
        使用確認へのURL.
        サムネイルのURL.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerDeck, PlayerFriend]
    
    def process(self):
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        
        # 所持アイテム情報取得.
        itemlist = BackendApi.get_item_list(self, v_player, using=settings.DB_READONLY)
        
        # アイテムリストを取得.
        self.html_param['item_list'] = itemlist
        self.writeAppHtml('item/itemlist')

def main(request):
    return Handler.run(request)
