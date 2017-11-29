# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerRegist,\
    PlayerGold, PlayerTreasure
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.views.application.shop.base import ShopHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.Shop import ShopItemBuyData
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
import settings
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.platform.api.objects import PaymentPostRequestData,\
    PaymentData, PaymentItem
from platinumegg.lib.platform.api.request import ApiNames
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr


class Handler(ShopHandler):
    """ショップ実行.
    課金の場合は
        PaymentApiを呼んで課金レコードを作成.
    課金以外は
        通貨を消費して商品を付与.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGachaPt, PlayerRegist]
    
    def process(self):
        self.__args = self.getUrlArgs('/shopdo/')
        try:
            mid = int(self.__args.get(0))
            buynum = int(self.request.get(Defines.URLQUERY_NUMBER))
            if not (0 < buynum <= Defines.BUY_NUM_MAX):
                raise
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        self.set_masterid(mid)
        
        self.__now = OSAUtil.get_now()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        
        # 購入可能かをチェック.
        master = self.getShopMaster()
        buydata = self.getShopBuyData(True)
        if buydata is None:
            mgr = db_util.run_in_transaction(Handler.tr_write_buydata, v_player.id, master.id)
            mgr.write_end()
            buydata = mgr.get_wrote_model(ShopItemBuyData, ShopItemBuyData.makeID(v_player.id, master.id))
        
        model_mgr = self.getModelMgr()
        if not BackendApi.check_buyable_shopitem(model_mgr, v_player, master, buydata, buynum, self.__now, using=settings.DB_READONLY):
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'購入できない')
            url = UrlMaker.shop()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        if master.consumetype == Defines.ShopConsumeType.PAYMENT:
            self.proc_payment(master, buynum)
        else:
            self.proc_free(master, buynum)
    
    #========================================================================================
    # ゲーム内のパラメータを消費.
    def proc_free(self, master, buynum):
        """ゲーム内のパラメータを消費で購入.
        """
        req_confirmkey = self.__args.get(1)
        # 購入書き込み.
        v_player = self.getViewerPlayer()
        model_mgr = db_util.run_in_transaction(self.tr_buy, v_player.id, master, buynum, req_confirmkey)
        model_mgr.write_end()
        # 結果ページヘリダイレクト.
        url = UrlMaker.shopresult(master.id)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_NUMBER, buynum)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def tr_buy(self, uid, master, buynum, req_confirmkey):
        """購入書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_update_requestkey(model_mgr, uid, req_confirmkey)
        player = BackendApi.get_players(self, [uid], [PlayerRegist, PlayerGachaPt, PlayerGold, PlayerTreasure], model_mgr=model_mgr)[0]
        BackendApi.tr_shopbuy_free(model_mgr, player, master, buynum, self.__now)
        model_mgr.write_all()
        return model_mgr
    
    #========================================================================================
    # 課金.
    def proc_payment(self, master, buynum):
        """課金して購入.
        """
        # TODO:PC版は後で実装。今はここにきたらエラーを飛ばしとく.
        if self.is_pc:
            raise CabaretError(u'未実装')
        
        mid = master.id
        v_player = self.getViewerPlayer()
        # ここまで来たら購入出来るのが確定..
        if settings_sub.IS_LOCAL:
            # ローカル動作確認用に課金トランザクション情報を作成.
            paymentdata = PaymentData()
            paymentdata.paymentId = "%s%s" % (v_player.dmmid, OSAUtil.makeSessionID())
            paymentdata.status = PaymentData.Status.START
            
            item = PaymentItem()
            item.itemId = master.id
            item.quantity = buynum
            paymentdata.paymentItems = [item]
            
            url = UrlMaker.shoppay()
            url = OSAUtil.addQuery(url, 'paymentId', paymentdata.paymentId)
            url = OSAUtil.addQuery(url, Defines.URLQUERY_STATE, PaymentData.Status.COMPLETED)
            transactionUrl = self.makeAppLinkUrlRedirect(url)
        else:
            if self.osa_util.is_admin_access:
                # このアクセスは対処しなくてもいいでしょ..
                url = UrlMaker.shopresult(mid)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
            
            data = PaymentPostRequestData()
            data.callbackUrl = self.makeAppLinkUrl(UrlMaker.shoppay())
            data.finishPageUrl = self.makeAppLinkUrl(UrlMaker.shopresult(mid))
            data.message = master.text
            data.addItem(master.id, master.name, master.price, buynum, self.makeAppLinkUrlImg(master.thumb), master.text)
            
            request = self.osa_util.makeApiRequest(ApiNames.PaymentPost, data)
            self.addAppApiRequest('payment_start', request)
            
            ret_data = self.execute_api()
            
            paymentresult = ret_data['payment_start'].get()
            transactionUrl = paymentresult.transactionUrl
            
            # PostのレスポンスデータはUrlとステータスしか入ってない...
            item = PaymentItem()
            item.itemId = master.id
            item.quantity = buynum
            
            paymentdata = PaymentData()
            paymentdata.paymentId = paymentresult.paymentId
            paymentdata.status = paymentresult.status
            paymentdata.paymentItems = data._paymentItems
        
        mgr = db_util.run_in_transaction(Handler.tr_create_entry, v_player, paymentdata, self.__now)
        mgr.write_end()
        
        self.appRedirect(transactionUrl)
    
    @staticmethod
    def tr_create_entry(player, paymentdata, now):
        """課金レコードを作成.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_create_shoppaymententry(model_mgr, player, paymentdata, now)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
