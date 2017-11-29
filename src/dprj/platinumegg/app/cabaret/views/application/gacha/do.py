# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerRequest
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.lib.platform.api.objects import PaymentPostRequestData,\
    PaymentItem, PaymentData
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.platform.api.request import ApiNames
import urllib
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
import settings_sub
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.Gacha import GachaMaster
import settings


class Handler(GachaHandler):
    """引抜実行.
    課金の場合:
        PaymentApiを叩いて課金ページヘリダイレクト.
        ローカルの場合は偽造.
        管理者アクセスの時は結果画面へ.
    無料またはチケットの場合:
        ガチャ書き込み.
    """
    _benchMaster = None
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGachaPt, PlayerRequest]
    
    def procBench(self):
        if Handler._benchMaster is None:
            model_mgr = self.getModelMgr()
            master_all = model_mgr.get_mastermodel_all(GachaMaster, 'id')
            for master in master_all:
                if master.consumetype == Defines.GachaConsumeType.GACHAPT:
                    Handler._benchMaster = master
                    break
    
    def process(self):
        v_player = self.getViewerPlayer()
        
        args = self.getUrlArgs('/gachado/')
        try:
            if settings_sub.IS_BENCH:
                mid = Handler._benchMaster.id
                key = v_player.req_confirmkey
            else:
                mid = int(args.get(0))
                key = urllib.unquote(args.get(1))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        self.set_masterid(mid)
        
        self.__now = OSAUtil.get_now()
        
        if settings_sub.IS_BENCH:
            key = v_player.req_confirmkey
        
        if v_player.req_alreadykey == key:
            # 実行済み.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'実行済みです')
            url = UrlMaker.gacharesult(mid, key)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        elif v_player.req_confirmkey != key:
            # ブラウザバック等.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'キーが正しくありません')
            url = UrlMaker.gacha()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        model_mgr = self.getModelMgr()
        master = self.getGachaMaster()
        if not BackendApi.check_schedule(model_mgr, master.schedule):
            # 期限切れ.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'期限切れ')
            url = UrlMaker.gacha()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        if master.consumetype in Defines.GachaConsumeType.PAYMENT_TYPES and (not self.osa_util.is_admin_access or settings_sub.IS_LOCAL):
            if self.is_pc:
                self.procPc()
            else:
                self.procPayment()
        else:
            self.procFree()
    
    def procPc(self):
        def redirect_to_app(url):
            self.html_param['url_redirect'] = url
            self.writeAppHtml('gacha/do_redirect')
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        master = self.getGachaMaster()
        playcount = self.getGachaPlayCount()
        
        seatplaydata = self.getSeatPlayData()
        is_first = 0 < BackendApi.get_gacha_firstplay_restnum(master, playcount, self.__now, seatplaydata=seatplaydata)
        continuity = BackendApi.get_gacha_continuity_num(model_mgr, master, v_player, is_first)
        
        stock = BackendApi.get_gacha_stock(model_mgr, master, playcount, using=settings.DB_READONLY)
        if stock is not None and stock < 1:
            # これ以上引き抜けない.
            url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_GTYPE, Defines.GachaConsumeType.GTYPE_NAMES[master.consumetype])
            redirect_to_app(self.makeAppLinkUrlRedirect(url))
            return
        elif master.consumetype == Defines.GachaConsumeType.MINI_SEAT:
            # ミニシートは1周だけ.
            seatplaycount = self.getSeatPlayCount()
            if seatplaycount and 0 < seatplaycount.lap:
                url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_GTYPE, Defines.GachaConsumeType.GTYPE_NAMES[master.consumetype])
                redirect_to_app(self.makeAppLinkUrlRedirect(url))
                return
        elif not self.checkStep(master, playcount):
            url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_GTYPE, Defines.GachaConsumeType.GTYPE_NAMES[master.consumetype])
            redirect_to_app(self.makeAppLinkUrlRedirect(url))
            return
        
        if settings_sub.IS_LOCAL:
            # ローカル動作確認用に課金トランザクション情報を作成.
            paymentdata = PaymentData()
            paymentdata.paymentId = "%s%s" % (v_player.dmmid, OSAUtil.makeSessionID())
            paymentdata.status = PaymentData.Status.START
            
            item = PaymentItem()
            item.itemId = master.id
            item.quantity = 1
            paymentdata.paymentItems = [item]
            
            url = UrlMaker.gachapay()
            url = OSAUtil.addQuery(url, 'paymentId', paymentdata.paymentId)
            url = OSAUtil.addQuery(url, Defines.URLQUERY_STATE, PaymentData.Status.COMPLETED)
            transactionUrl = self.makeAppLinkUrlRedirect(url)
            
            mgr = db_util.run_in_transaction(Handler.tr_create_entry, v_player, paymentdata, continuity, self.__now)
            mgr.write_end()
            
            redirect_to_app(transactionUrl)
        else:
            price = BackendApi.get_consumevalue(master, continuity, is_first, playcount, seatplaydata=seatplaydata)
            self.html_param['sku_id'] = master.id
            self.html_param['price'] = price
            self.html_param['count'] = 1
            self.html_param['name'] = master.name
            self.html_param['description'] = master.text
            if self.is_pc:
                self.html_param['image_url'] = self.makeAppLinkUrlStatic('img/pc/'+master.pay_thumb_pc)
            else:
                self.html_param['image_url'] = self.makeAppLinkUrlImgMedium(master.pay_thumb)
            self.html_param['finish_page_url'] = self.makeAppLinkUrl(UrlMaker.gachaanim(master.id, v_player.req_confirmkey))
            
            self.writeAppHtml('gacha/do')
    
    def procPayment(self):
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        master = self.getGachaMaster()
        playcount = self.getGachaPlayCount()
        
        seatplaydata = self.getSeatPlayData()
        is_first = 0 < BackendApi.get_gacha_firstplay_restnum(master, playcount, self.__now, seatplaydata=seatplaydata)
        continuity = BackendApi.get_gacha_continuity_num(self.getModelMgr(), master, v_player, is_first)
        
        stock = BackendApi.get_gacha_stock(model_mgr, master, playcount, using=settings.DB_READONLY)
        if stock is not None and stock < 1:
            # これ以上引き抜けない.
            url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_GTYPE, Defines.GachaConsumeType.GTYPE_NAMES[master.consumetype])
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        elif master.consumetype == Defines.GachaConsumeType.MINI_SEAT:
            # ミニシートは1周だけ.
            seatplaycount = self.getSeatPlayCount()
            if seatplaycount and 0 < seatplaycount.lap:
                url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_GTYPE, Defines.GachaConsumeType.GTYPE_NAMES[master.consumetype])
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        elif not self.checkStep(master, playcount):
            url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_GTYPE, Defines.GachaConsumeType.GTYPE_NAMES[master.consumetype])
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # ここまで来たら購入出来るのが確定..
        if settings_sub.IS_LOCAL:
            # ローカル動作確認用に課金トランザクション情報を作成.
            paymentdata = PaymentData()
            paymentdata.paymentId = "%s%s" % (v_player.dmmid, OSAUtil.makeSessionID())
            paymentdata.status = PaymentData.Status.START
            
            item = PaymentItem()
            item.itemId = master.id
            item.quantity = 1
            paymentdata.paymentItems = [item]
            
            url = UrlMaker.gachapay()
            url = OSAUtil.addQuery(url, 'paymentId', paymentdata.paymentId)
            url = OSAUtil.addQuery(url, Defines.URLQUERY_STATE, PaymentData.Status.COMPLETED)
            transactionUrl = self.makeAppLinkUrlRedirect(url)
        else:
            kind = BackendApi.check_payment_lostrecords(v_player.id)
            if kind == 'gacha':
                modellist = BackendApi.get_gachapaymententry_list(v_player.id, False, 1, 0, using=settings.DB_READONLY)
                def updateGacha(paymentId, status):
                    if status == PaymentData.Status.COMPLETED:
                        # 購入書き込み.
                        self.writePlayPaymentGacha(paymentId)
                    elif status == PaymentData.Status.CANCEL:
                        # キャンセル書き込み.
                        self.writeGachaCancel(paymentId)
                    elif status == PaymentData.Status.TIMEOUT:
                        # タイムアウト書き込み.
                        self.writeGachaTimeout(paymentId)
                
                if modellist:
                    for model in modellist:
                        paymentId = model.id
                        status = BackendApi.get_restful_paymentrecord_status(self, paymentId)
                        updateGacha(paymentId, status)
                else:
                    BackendApi.delete_payment_lostrecords_flag(v_player.id)
            
            data = PaymentPostRequestData()
            data.callbackUrl = self.makeAppLinkUrl(UrlMaker.gachapay())
            data.finishPageUrl = self.makeAppLinkUrl(UrlMaker.gachaanim(master.id, v_player.req_confirmkey))
            data.message = master.text
            
            price = BackendApi.get_consumevalue(master, continuity, is_first, playcount, seatplaydata=seatplaydata)
            if self.is_pc:
                image_url = self.makeAppLinkUrlStatic('img/pc/'+master.pay_thumb_pc)
            else:
                image_url = self.makeAppLinkUrlImgMedium(master.pay_thumb)
            data.addItem(master.id, master.name, price, 1, image_url, master.text)
            
            request = self.osa_util.makeApiRequest(ApiNames.PaymentPost, data)
            self.addAppApiRequest('payment_start', request)
            
            ret_data = self.execute_api()
            
            paymentresult = ret_data['payment_start'].get()
            transactionUrl = paymentresult.transactionUrl
            
            # PostのレスポンスデータはUrlとステータスしか入ってない...
            item = PaymentItem()
            item.itemId = master.id
            item.quantity = 1
            
            paymentdata = PaymentData()
            paymentdata.paymentId = paymentresult.paymentId
            paymentdata.status = paymentresult.status
            paymentdata.paymentItems = data._paymentItems

        mgr = db_util.run_in_transaction(Handler.tr_create_entry, v_player, paymentdata, continuity, self.__now)
        mgr.write_end()
        
        self.appRedirect(transactionUrl)
    
    def procFree(self):
        
        v_player = self.getViewerPlayer()
        
        try:
            continuity = int(self.request.get(Defines.URLQUERY_NUMBER))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        result_code = self.writePlayGacha(self.__now, continuity)
        
        if settings_sub.IS_BENCH:
            self.response.set_status(200)
            self.response.send()
        elif result_code in (CabaretError.Code.OK, CabaretError.Code.ALREADY_RECEIVED):
            # 結果へ.
            url = UrlMaker.gachaanim(self.gachamaster_id, v_player.req_confirmkey)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        elif result_code in (CabaretError.Code.NOT_ENOUGH, CabaretError.Code.OVER_LIMIT):
            # ポイントが足りない.所持数オーバー.
            url = UrlMaker.gacharesult(self.gachamaster_id, v_player.req_confirmkey, result_code)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        else:
            url = UrlMaker.gacha()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
    
    @staticmethod
    def tr_create_entry(player, paymentdata, continuity, now):
        """課金レコードを作成.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_create_gachapaymententry(model_mgr, player, paymentdata, continuity, now)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
