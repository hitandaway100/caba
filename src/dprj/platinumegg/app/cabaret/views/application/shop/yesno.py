# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerRegist,\
    PlayerGold, PlayerTreasure, PlayerRequest
from platinumegg.app.cabaret.util.api import Objects
from platinumegg.app.cabaret.views.application.shop.base import ShopHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(ShopHandler):
    """ショップ購入確認ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGachaPt, PlayerRegist, PlayerGold, PlayerTreasure, PlayerRequest]
    
    def process(self):
        args = self.getUrlArgs('/shopyesno/')
        try:
            mid = int(args.get(0))
            buy_num = int(self.request.get(Defines.URLQUERY_NUMBER))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        self.html_param['player'] = Objects.player(self, v_player)
        self.set_masterid(mid)
        master = self.getShopMaster()
        if master is None or master.consumetype == Defines.ShopConsumeType.PAYMENT:
            # 不正な遷移.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.shop()))
            return
        # 購入する数.
        self.html_param['buy_num'] = buy_num
        # 購入する商品.
        self.html_param['shopitem'] = self.makeShopObj()
        # 購入するURL.
        url = UrlMaker.shopdo(mid, v_player.req_confirmkey)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_NUMBER, buy_num)
        self.html_param['url_buy'] = self.makeAppLinkUrl(url)
        # 遷移元チェック.
        self.putFromBackPageLinkUrl()
        
        self.writeAppHtml('shop/yesno')

def main(request):
    return Handler.run(request)
