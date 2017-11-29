# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerRegist,\
    PlayerGold, PlayerTreasure
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.views.application.shop.base import ShopHandler
from platinumegg.lib.platform.api.objects import PaymentData
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import settings_sub
from defines import Defines


class Handler(ShopHandler):
    """ショップ購入結果ページ.
    表示するもの:
        購入結果.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGachaPt, PlayerRegist, PlayerGold, PlayerTreasure]
    
    def check_process_pre(self):
        paymentId = self.request.get('paymentId')
        if paymentId:
            return True
        else:
            return ShopHandler.check_process_pre(self)
    
    def process(self):
        
        if not self.checkResult():
            return
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        self.html_param['player'] = Objects.player(self, v_player)
        
        # 購入した商品.
        self.html_param['shopitem'] = self.makeShopObj()
        
        master = self.getShopMaster()
        self.html_param['buy_num'] = self.__buy_num * master.inum0
        
        # 遷移元チェック.
        self.putFromBackPageLinkUrl()
        
        # 購入可能な商品.
#        self.putBuyableShopItemList()
        
        self.writeAppHtml('shop/buyresult')
    
    def checkResult(self):
        """購入結果をチェック.
        """
        self.__buy_num = 0
        
        args = self.getUrlArgs('/shopresult/')
        try:
            mid = int(args.get(0))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        self.set_masterid(mid)
        
        master = self.getShopMaster()
        if master.consumetype != Defines.ShopConsumeType.PAYMENT:
            self.__buy_num = int(self.request.get(Defines.URLQUERY_NUMBER))
            return True
        elif self.osa_util.is_admin_access and not settings_sub.IS_LOCAL:
            self.__buy_num = 1
            return True
        
        paymentId = self.request.get('paymentId')
        if not paymentId:
            raise CabaretError(u'購入情報がありません.', CabaretError.Code.ILLEGAL_ARGS)
        
        status = BackendApi.get_restful_paymentrecord_status(self, paymentId)
        
        if status == PaymentData.Status.COMPLETED:
            # 購入書き込み.
            entry = self.writeBuyItem(paymentId)
            self.__buy_num = entry.inum
            self.set_masterid(entry.iid)
            return True
        elif status == PaymentData.Status.CANCEL:
            # キャンセル書き込み.
            self.writeBuyCancel(paymentId)
            self.html_param['url_shop'] = self.makeAppLinkUrl(UrlMaker.shop())
            self.writeAppHtml('shop/cancel')
        elif status == PaymentData.Status.TIMEOUT:
            # キャンセル書き込み.
            self.writeBuyTimeOut(paymentId)
            self.html_param['url_shop'] = self.makeAppLinkUrl(UrlMaker.shop())
            self.writeAppHtml('shop/timeout')
        else:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        return False

def main(request):
    return Handler.run(request)
