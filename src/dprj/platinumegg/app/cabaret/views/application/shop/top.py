# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerRegist,\
    PlayerGold, PlayerTreasure
from platinumegg.app.cabaret.util.api import Objects
from platinumegg.app.cabaret.views.application.shop.base import ShopHandler
from defines import Defines


class Handler(ShopHandler):
    """ショップTopページ.
    表示するもの:
        プレイヤー情報.
        購入可能な商品.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGachaPt, PlayerRegist, PlayerGold, PlayerTreasure]
    
    def process(self):
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        self.html_param['player'] = Objects.player(self, v_player)
        
        # 購入可能な商品.
        self.putBuyableShopItemList()
        
        self.html_param['num_key'] = Defines.URLQUERY_NUMBER
        
        self.writeAppHtml('shop/shop')

def main(request):
    return Handler.run(request)
