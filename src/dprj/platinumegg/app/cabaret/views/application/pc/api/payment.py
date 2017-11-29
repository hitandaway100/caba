# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Shop import ShopItemBuyData
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
import settings
import settings_sub
from platinumegg.lib.platform.api.objects import PaymentGetRequestData, PaymentData, PaymentItem
from platinumegg.lib.platform.api.request import ApiNames
from platinumegg.lib.pljson import Json
from oauth import oauth


class Handler(AppHandler):
    """決済確認/結果を返す.
    """
    
    # SKU_IDの頭2字から、ショップ/ガチャを判定する
    PAYMENT_TYPE_SHOP  = 'SH'
    PAYMENT_TYPE_GACHA = 'GA'
    
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 500
    
    def checkUser(self):
        # 署名の検証を行う.
        #self.osa_util.checkOAuth()
        if settings_sub.IS_LOCAL:
            return
        
        try:
            if self.request.django_request.META.has_key('HTTP_AUTHORIZATION'):
                oauth_params = self.request.django_request.META['HTTP_AUTHORIZATION']
                headers = {}
                headers.update(self.request.django_request.META)
                headers['Authorization'] = oauth_params
                oauth_request = oauth.OAuthRequest.from_request(
                    self.request.method,
                    self.request.url,
                    headers = headers,
                    query_string = self.request.query_string
                )
                sig = oauth_request.get_parameter('oauth_signature')
                sig_build = oauth.OAuthSignatureMethod_HMAC_SHA1().build_signature(oauth_request, self.osa_util.consumer, None)
                self.osa_util.logger.trace('sig      :' + sig)
                self.osa_util.logger.trace('sig_build:' + sig_build)
                if sig == sig_build:
                    self.osa_util.logger.trace('sig_check_ok?:True')
                else:
                    self.osa_util.logger.trace('sig_check_ok?:False')
                    raise oauth.OAuthError('sig check error!!')
            else:
                raise CabaretError(u'署名を確認できません')
        except:
            raise CabaretError(u'署名を確認できません')
    
    def check_process_pre(self):
        return True
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def preprocess(self):
        AppHandler.preprocess(self)
        self.__shopmaster_id = None
        self.__shopmaster = None
        self.__buydata = None
        self.__gachamaster_id = None
        self.__playdata = None
        self.__playcount = None
        self.__gachamaster = None
        self.__gachamasterstep = None
    
    def process(self):
        procname = self.request.method
        table = {
            'POST' : self.procPost,
            'GET' : self.procGet,
        }
        proc = table.get(procname, None)
        if proc is None:
            # 不正リクエスト
            self.response.set_status(400)
            self.response.end()
        else:
            proc()
    
    def procPost(self):
        """ 決済確認.
        """
        # 決済情報の確認.
        if settings_sub.IS_LOCAL:
            sku_id = self.request.get('_sku_id')
            buynum = self.request.get('_count')
            v_player = self.getViewerPlayer()
            payment_id = "%s%s" % (v_player.dmmid, OSAUtil.makeSessionID())
        else:
            # JSONフォーマットで返ってくるので生のPOSTデータにアクセス
            #body = Json.decode(self.request.django_request.raw_post_data)
            body = Json.decode(self.request.django_request.body)
            self.json_param['ITEMS'] = body.get('ITEMS')
            self.json_param['PAYMENT_TYPE'] = body.get('PAYMENT_TYPE')
            self.json_param['PAYMENT_ID'] = body.get('PAYMENT_ID')
            self.json_param['ORDERER_TIME'] = body.get('ORDERER_TIME')
            
            sku_id = self.json_param['ITEMS'][0].get('SKU_ID')
            buynum = self.json_param['ITEMS'][0].get('COUNT')
            payment_id = self.json_param['PAYMENT_ID']
        
        # 'SH' or 'GA'
        data_type = sku_id[:2]
        mid = sku_id[2:]
        
        if data_type == Handler.PAYMENT_TYPE_SHOP:
            # ショップ
            self.procShopDo(mid, buynum, payment_id)
        elif data_type == Handler.PAYMENT_TYPE_GACHA:
            # ガチャ
            self.procGachaDo(mid, buynum, payment_id)
        else:
            raise CabaretError(u'存在しない商品です', CabaretError.Code.INVALID_MASTERDATA)
        
        if not self.response.isEnd:
            self.response.set_status(200)
            self.response.send('{"response_code":"OK"}')
    
    def set_shop_masterid(self, mid):
        self.__shopmaster_id = mid
        self.__shopmaster = None
        self.__buydata = None
    
    def getShopMaster(self):
        """マスターデータ.
        """
        if self.__shopmaster is None:
            model_mgr = self.getModelMgr()
            self.__shopmaster = BackendApi.get_shopmaster(model_mgr, self.__shopmaster_id, using=settings.DB_READONLY)
            if self.__shopmaster is None:
                raise CabaretError(u'存在しない商品です', CabaretError.Code.INVALID_MASTERDATA)
        return self.__shopmaster
    
    def getShopBuyData(self, blank=False):
        """購入情報.
        """
        if self.__buydata is None:
            v_player = self.getViewerPlayer()
            master = self.getShopMaster()
            model_mgr = self.getModelMgr()
            self.__buydata = BackendApi.get_shopbuydata(model_mgr, v_player.id, [master.id], using=settings.DB_READONLY).get(master.id)
            if self.__buydata is None and not blank:
                # 明らかに不正アクセス.
                raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        return self.__buydata
    
    def procShopDo(self, master_id, buy_count, payment_id):
        """ショップ実行.
        決済情報を確認して課金レコードを作成.
        """
        try:
            mid = int(master_id)
            buynum = int(buy_count)
            if not (0 < buynum <= Defines.BUY_NUM_MAX):
                raise
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        self.set_shop_masterid(mid)
        now = OSAUtil.get_now()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        
        # 購入可能かをチェック.
        master = self.getShopMaster()
        buydata = self.getShopBuyData(True)
        if buydata is None:
            mgr = db_util.run_in_transaction(Handler.tr_write_buydata, v_player.id, master.id)
            mgr.write_end()
            buydata = mgr.get_wrote_model(ShopItemBuyData, ShopItemBuyData.makeID(v_player.id, master.id))
        
        sku_id = '%s%s' % (Handler.PAYMENT_TYPE_SHOP, master_id)
        item = PaymentItem()
        item.itemId = sku_id
        item.unitPrice = master.price
        item.quantity = buynum
        self.checkPaymentRecord(payment_id, [item])
        if self.response.isEnd:
            return
        
        model_mgr = self.getModelMgr()
        if not BackendApi.check_buyable_shopitem(model_mgr, v_player, master, buydata, buynum, now, using=settings.DB_READONLY):
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'購入できない')
            # リダイレクトせずにステータス500を返す
            #url = UrlMaker.shop()
            #self.appRedirect(self.makeAppLinkUrlRedirect(url))
            self.response.clear()
            self.response.set_status(500)
            self.response.end()
            return
        
        # ここまで来たら購入出来るのが確定..
        item.itemId = master.id
        
        paymentdata = PaymentData()
        paymentdata.paymentId = payment_id
        paymentdata.status = PaymentData.Status.START
        paymentdata.paymentItems = [item]
        
        mgr = db_util.run_in_transaction(Handler.tr_create_entry_shop, v_player, paymentdata, now)
        mgr.write_end()
    
    @staticmethod
    def tr_write_buydata(uid, mid):
        """購入情報がないので用意.
        """
        model_mgr = ModelRequestMgr()
        ins = ShopItemBuyData.makeInstance(ShopItemBuyData.makeID(uid, mid))
        model_mgr.set_save(ins)
        model_mgr.write_all()
        return model_mgr    
    
    @staticmethod
    def tr_create_entry_shop(player, paymentdata, now):
        """課金レコードを作成.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_create_shoppaymententry(model_mgr, player, paymentdata, now)
        model_mgr.write_all()
        return model_mgr
    
    def set_gacha_masterid(self, mid):
        self.__gachamaster_id = mid
        self.__playdata = None
        self.__gachamaster = None
    
    @property
    def gachamaster_id(self):
        return self.__gachamaster_id
        
    
    def getGachaMaster(self):
        """マスターデータ.
        """
        if self.__gachamaster is None:
            model_mgr = self.getModelMgr()
            self.__gachamaster = BackendApi.get_gachamaster(model_mgr, self.gachamaster_id, using=settings.DB_READONLY)
            if self.__gachamaster is None:
                raise CabaretError(u'存在しないガチャです', CabaretError.Code.INVALID_MASTERDATA)
            
        return self.__gachamaster
    
    def getGachaMasterStep(self):
        """マスターデータ.
        """
        if self.__gachamasterstep is None:
            model_mgr = self.getModelMgr()
            master = self.getGachaMaster()
            if master.stepsid > 0:
                if master.stepsid != master.id:
                    self.__gachamasterstep = BackendApi.get_gachamaster(model_mgr, master.stepsid, using=settings.DB_READONLY)
                    if self.__gachamasterstep is None:
                        raise CabaretError(u'存在しないガチャです', CabaretError.Code.INVALID_MASTERDATA)
                else:
                    self.__gachamasterstep = master
            
        return self.__gachamasterstep
    
    def getGachaPlayCount(self):
        """プレイ回数.
        """
        if self.__playcount is None:
            v_player = self.getViewerPlayer()
            master = self.getGachaMaster()
            model_mgr = self.getModelMgr()
            if master.stepsid <= 0:
                self.__playcount = BackendApi.get_gachaplaycount(model_mgr, v_player.id, [master.id], using=settings.DB_READONLY, get_instance=True).get(master.id)
            else:
                master = self.getGachaMasterStep()
                self.__playcount = BackendApi.get_gachaplaycount(model_mgr, v_player.id, [master.id], using=settings.DB_READONLY, get_instance=True).get(master.id)
        return self.__playcount
    
    def procGachaDo(self, master_id, buy_count, payment_id):
        """ガチャ実行.
        決済情報を確認して課金レコードを作成.
        """
        try:
            mid = int(master_id)
#            buynum = int(buy_count)
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        self.set_gacha_masterid(mid)
        now = OSAUtil.get_now()
        
        # 基本的なチェックはここにくるまでに終わっている
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        master = self.getGachaMaster()
        playcount = self.getGachaPlayCount()
        
        seatplaydata = BackendApi.get_gachaseatmodels_by_gachamaster(model_mgr, v_player.id, master, do_get_result=False, using=settings.DB_READONLY).get('playdata')
        is_first = 0 < BackendApi.get_gacha_firstplay_restnum(master, playcount, now, seatplaydata=seatplaydata)
        continuity = BackendApi.get_gacha_continuity_num(model_mgr, master, v_player, is_first)
        price = BackendApi.get_consumevalue(master, continuity, is_first, playcount, seatplaydata=seatplaydata)
        
        stock = BackendApi.get_gacha_stock(model_mgr, master, playcount, using=settings.DB_READONLY)
        if stock is not None and stock < 1:
            # これ以上引き抜けない.
            self.response.clear()
            self.response.set_status(500)
            self.response.end()
            return
        
        sku_id = '%s%s' % (Handler.PAYMENT_TYPE_GACHA, master_id)
        item = PaymentItem()
        item.itemId = sku_id
        item.unitPrice = price
        item.quantity = 1
        self.checkPaymentRecord(payment_id, [item])
        if self.response.isEnd:
            return
        
        # ここまで来たら購入出来るのが確定..
        item.itemId = master.id
        
        paymentdata = PaymentData()
        paymentdata.paymentId = payment_id
        paymentdata.status = PaymentData.Status.START
        paymentdata.paymentItems = [item]
        
        mgr = db_util.run_in_transaction(Handler.tr_create_entry_gacha, v_player, paymentdata, continuity, now)
        mgr.write_end()
    
    @staticmethod
    def tr_create_entry_gacha(player, paymentdata, continuity, now):
        """課金レコードを作成.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_create_gachapaymententry(model_mgr, player, paymentdata, continuity, now)
        model_mgr.write_all()
        return model_mgr
    
    def procGet(self):
        """ 決済確定.
        """
        # payment_idの検証
        payment_id = self.request.get('payment_id')
        self.json_param['payment_id'] = payment_id
        
        if not settings_sub.IS_LOCAL:
            if not payment_id:
                raise CabaretError(u'paymentId is None')
            # APIで課金情報を取得.
            data = PaymentGetRequestData()
            data.paymentId = payment_id
            data.guid = self.osa_util.viewer_id
            
            request = self.osa_util.makeApiRequest(ApiNames.PaymentGet, data)
            self.addAppApiRequest('payment_check', request)
            ret_data = self.execute_api()
            paymentdata = ret_data['payment_check'].get()
            if paymentdata.status != PaymentData.Status.START:
                raise CabaretError(u"Illegal status")
        
        # 'SH' or 'GA'
        sku_id = paymentdata.paymentItems[0].itemId
        data_type = sku_id[:2]
        #mid = sku_id[2:]
        
        if data_type == Handler.PAYMENT_TYPE_SHOP:
            # ショップ
            self.procShopPay(payment_id)
        elif data_type == Handler.PAYMENT_TYPE_GACHA:
            # ガチャ
            self.procGachaPay(payment_id)
        else:
            raise CabaretError(u'存在しない商品です', CabaretError.Code.INVALID_MASTERDATA)
        
        # 署名付与
        # TODO
        
        self.response.set_status(200)
        response_body = '{"payment_id":"%s","response_code":"OK"}' % payment_id
        self.response.send(response_body)
    
    def procShopPay(self, payment_id):
        """ショップ実行.
        課金レコードを更新.
        """
        v_player = self.getViewerPlayer()
        
        # セッションを切っておく.
        #client = OSAUtil.get_cache_client()
        #client.delete(self.osa_util.viewer_id, namespace='session')
        #client.delete('payment_checked:%s' % v_player.id)
        
        model_mgr, _ = db_util.run_in_transaction(Handler.tr_update_entry_shop, v_player.id, payment_id)
        model_mgr.write_end()
    
    @staticmethod
    def tr_update_entry_shop(uid, paymentId):
        """課金レコードを作成.
        """
        model_mgr = ModelRequestMgr()
        entry = BackendApi.tr_update_shoppaymententry(model_mgr, uid, paymentId, PaymentData.Status.START)
        model_mgr.write_all()
        return model_mgr, entry
    
    def procGachaPay(self, payment_id):
        """ガチャ実行.
        課金レコードを更新.
        """
        v_player = self.getViewerPlayer()
        
        # セッションを切っておく.
        #client = OSAUtil.get_cache_client()
        #client.delete(self.osa_util.viewer_id, namespace='session')
        #client.delete('payment_checked:%s' % v_player.id)
        
        model_mgr, _ = db_util.run_in_transaction(Handler.tr_update_entry_gacha, v_player.id, payment_id)
        model_mgr.write_end()
    
    @staticmethod
    def tr_update_entry_gacha(uid, paymentId):
        """課金レコードを作成.
        """
        model_mgr = ModelRequestMgr()
        entry = BackendApi.tr_update_gachapaymententry(model_mgr, uid, paymentId, PaymentData.Status.START)
        model_mgr.write_all()
        return model_mgr, entry
    
    def processError(self, error_message):
        # なんかｴﾗｰ.
        self.osa_util.logger.error(error_message);
        self.response.clear()
        self.response.set_status(500)
        self.response.end()
    
    def processAppError(self, err):
        self.json_param['error'] = {
            'code' : err.code,
            'str_code' : CabaretError.getCodeString(err.code),
            'message' : err.value,
        }
        self.writeAppJson()
    
    def checkPaymentRecord(self, payment_id, buyitemlist):
        """課金レコードを確認.
        """
        def error(message):
            self.osa_util.logger.error(message);
            self.response.clear()
            self.response.set_status(500)
            self.response.end()
        
        record = BackendApi.get_restful_paymentrecord(self, payment_id)
        if record.userId != self.osa_util.viewer_id:
            error(u'Illiegal userId. payment_id=%s, %s vs %s' % (payment_id, record.userId, self.osa_util.viewer_id))
            return
        
        recorditems = list(record.paymentItems)
        recorditems.sort(key=lambda x:x.itemId)
        
        buyitemlist = list(buyitemlist)
        if len(buyitemlist) != len(recorditems):
            error(u'Illiegal number of item. payment_id=%s, %s vs %s' % (payment_id, len(buyitemlist), len(recorditems)))
            return
        
        for idx, recorditem in enumerate(recorditems):
            buyitem = buyitemlist[idx]
            if buyitem.itemId != recorditem.itemId:
                error(u'Illiegal itemId. payment_id=%s, %s vs %s' % (payment_id, buyitem.itemId, recorditem.itemId))
                return
            elif buyitem.quantity != recorditem.quantity:
                error(u'Illiegal quantity. payment_id=%s, %s vs %s' % (payment_id, buyitem.quantity, recorditem.quantity))
                return
            elif buyitem.unitPrice != recorditem.unitPrice:
                error(u'Illiegal price. payment_id=%s, %s vs %s' % (payment_id, buyitem.unitPrice, recorditem.unitPrice))
                return
    
def main(request):
    return Handler.run(request)
