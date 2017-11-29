# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.platform.api.objects import PaymentData, MessageRequestData
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Player import PlayerDeck, PlayerGachaPt,\
    PlayerRegist, Player
from platinumegg.lib.opensocial.util import OSAUtil
import datetime
from platinumegg.app.cabaret.models.PaymentEntry import GachaPaymentEntry,\
    ShopPaymentEntry
import settings_sub
import settings
from platinumegg.app.cabaret.models.AppConfig import MessageQueue
from platinumegg.lib.platform.api.request import ApiNames


class Handler(AdminHandler):
    """非対応ページ.
    """
    
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 500
    
    def checkUser(self):
        # 認証.
        if settings_sub.IS_LOCAL:
            return
        elif self.request.remote_addr.startswith('10.116.41.'):
            return
        self.response.set_status(404)
        raise CabaretError(u'NotFound!!', CabaretError.Code.NOT_AUTH)
    
    def printLog(self, s):
        self.__logs.append('%s' % s)
    
    def process(self):
        
        self.__logs = []
        
        model_mgr = self.getModelMgr()
        appconfig = BackendApi.get_appconfig(model_mgr, using=settings.DB_READONLY)
        if appconfig.is_maintenance() and appconfig.is_platform_maintenance():
            # プラットフォーム側のメンテ中.
            self.printLog('platform maintenance.')
        else:
            ope = self.request.get('ope')
            f = getattr(self, 'proc_%s' % ope, None)
            if f:
                f()
            else:
                self.response.set_status(404)
            self.printLog('all done..')
        
        self.response.send('\n'.join(self.__logs))
    
    
    def proc_send_message(self):
        """メッセージの送信.
        """
        now = OSAUtil.get_now()
        model = MessageQueue.getValues(order_by='stime', using=settings.DB_READONLY)
        if model is None or now < model.stime:
            self.printLog('Not Found..')
            self.response.set_status(200)
            return
        
        obj = MessageRequestData()
        obj.title = model.title
        obj.body = model.body
#        urldata = urlparse(self.url_cgi)
#        url = '%s://%s%s' % (urldata.scheme, settings_sub.WEB_GLOBAL_HOST, urldata.path)
#        url = self.osa_util.makeLinkUrl(self.addTimeStamp(url + UrlMaker.top()))
        obj._urls = {
#            'touch' : url
        }
        obj.title = model.title
        
        def tr(model):
            model_mgr = ModelRequestMgr()
            model_mgr.set_delete(model)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, model).write_end()
        
        LIMIT = 500
        RECIPIENTS_NUM_MAX = 20
        THREAD_NUM_MAX = 20
        uidmax = Player.max_value('id', using=settings.DB_READONLY) or 0
        uid = 1
        cnt = 0
        recipients = []
        
        def send():
            if recipients:
                obj.recipients = recipients
                request = self.osa_util.makeApiRequest(ApiNames.Message, obj)
                self.addAppApiRequest('message%s' % cnt, request)
        
        while uid <= uidmax:
            uid_start = uid
            uid_end = uid + LIMIT
            playerlist = Player.fetchValues(filters={'id__gte' : uid_start, 'id__lt' : uid_end}, using=settings.DB_READONLY)
            
            for player in playerlist:
                recipients.append(player.dmmid)
                if RECIPIENTS_NUM_MAX == len(recipients):
                    send()
                    self.printLog('send %s' % recipients)
                    cnt += 1
                    recipients = []
                    if THREAD_NUM_MAX <= cnt:
                        data = self.execute_api()
                        if settings_sub.IS_DEV:
                            try:
                                for k in data.keys():
                                    data[k].get()
                            except Exception, err:
                                self.printLog('faild...%s' % err)
                        cnt = 0
            uid = uid_end
        send()
        
        self.response.set_status(200)
    
    def proc_payment_gacha(self):
        """課金ガチャチェック.
        """
        model_mgr = self.getModelMgr()
        
        limittime = OSAUtil.get_now() - datetime.timedelta(seconds=2400)    # 30分でタイムアウトになるそうなので40分ほど余裕をもたせれば問題ないはず.
        entrylist = list(GachaPaymentEntry.all().filter(state=PaymentData.Status.START, ctime__lt=limittime).values('id','uid').fetch(60))
        for entry in entrylist:
            self.printLog('Start id=%s' % entry['id'])
            try:
                player = model_mgr.get_model(Player, entry['uid'], using=settings.DB_READONLY)
                if not player:
                    raise CabaretError('Player not found..')
                record = BackendApi.get_restful_paymentrecord(self, entry['id'], player.dmmid)
            except CabaretError, err:
                self.printLog('Api Error!! id=%s, %s' % (entry['id'], err.value))
                continue
            except Exception, err:
                self.printLog('Api Error!! id=%s, %s' % (entry['id'], err.message))
                continue
            try:
                self.updateGacha(entry, record)
            except CabaretError, err:
                self.printLog('Update Error!! id=%s, %s' % (entry['id'], err.value))
                continue
            except Exception, err:
                self.printLog('Update Error!! id=%s, %s' % (entry['id'], err.message))
                continue
        
        filters = {
            'state' : PaymentData.Status.CREATE,
            'ctime__lt' : limittime,
        }
        def tr():
            model_mgr = ModelRequestMgr()
            entrylist = GachaPaymentEntry.fetchValues(filters=filters, limit=60)
            for entry in entrylist:
                model_mgr.set_delete(entry)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        self.response.set_status(200)
    
    def proc_payment_shop(self):
        """アイテム購入チェック.
        """
        model_mgr = self.getModelMgr()
        
        limittime = OSAUtil.get_now() - datetime.timedelta(seconds=2400)    # 30分でタイムアウトになるそうなので40分ほど余裕をもたせれば問題ないはず.
        entrylist = list(ShopPaymentEntry.all().filter(state=PaymentData.Status.START, ctime__lt=limittime).values('id','uid').fetch(60))
        for entry in entrylist:
            self.printLog('Start id=%s' % entry['id'])
            try:
                player = model_mgr.get_model(Player, entry['uid'], using=settings.DB_READONLY)
                if not player:
                    raise CabaretError('Player not found..')
                record = BackendApi.get_restful_paymentrecord(self, entry['id'], player.dmmid)
                self.updateShop(entry, record)
            except:
                self.printLog('Error!! id=%s' % entry['id'])
        
        filters = {
            'state' : PaymentData.Status.CREATE,
            'ctime__lt' : limittime,
        }
        def tr():
            model_mgr = ModelRequestMgr()
            entrylist = ShopPaymentEntry.fetchValues(filters=filters, limit=60)
            for entry in entrylist:
                model_mgr.set_delete(entry)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        self.response.set_status(200)
    
    def updateGacha(self, entry, record):
        if record.status == PaymentData.Status.COMPLETED:
            # 購入書き込み.
            is_pc = False
            if not str(record.paymentItems[0].itemId).isdigit():
                is_pc = True
            self.writePlayPaymentGacha(entry, is_pc)
        elif record.status == PaymentData.Status.CANCEL:
            # キャンセル書き込み.
            self.writeGachaCancel(entry)
        elif record.status == PaymentData.Status.TIMEOUT:
            # タイムアウト書き込み.
            self.writeGachaTimeout(entry)
    
    def updateShop(self, entry, record):
        if record.status == PaymentData.Status.COMPLETED:
            # 購入書き込み.
            is_pc = False
            if not str(record.paymentItems[0].itemId).isdigit():
                is_pc = True
            self.writeBuyItem(entry, is_pc)
        elif record.status == PaymentData.Status.CANCEL:
            # キャンセル書き込み.
            self.writeBuyCancel(entry)
        else:
            # タイムアウト書き込み.
            self.writeBuyTimeOut(entry)
    
    def writePlayPaymentGacha(self, entry, is_pc):
        """課金ガチャプレイ書き込み.
        """
        uid = entry['uid']
        paymentId = entry['id']
        
        playerconfigdata = BackendApi.get_playerconfigdata(uid)
        
        try:
            model_mgr = db_util.run_in_transaction(self.__tr_write_playgacha_pay, uid, paymentId, is_pc, playerconfigdata.autosell_rarity)
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
    
    def __tr_write_playgacha_pay(self, uid, paymentId, is_pc, autosell_rarity):
        model_mgr = ModelRequestMgr()
        players = BackendApi.get_players(self, [uid], [PlayerDeck], model_mgr=model_mgr)
        if players:
            BackendApi.tr_play_gacha_pay(model_mgr, players[0], paymentId, is_pc, do_update_key=False, autosell_rarity=autosell_rarity)
            model_mgr.write_all()
        return model_mgr
    
    def writeGachaCancel(self, entry):
        """課金ガチャキャンセル書き込み.
        """
        try:
            model_mgr = db_util.run_in_transaction(self.__tr_write_gacha_cancel, entry['uid'], entry['id'])
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
    
    def __tr_write_gacha_cancel(self, uid, paymentId):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_gacha_cancel(model_mgr, uid, paymentId)
        model_mgr.write_all()
        return model_mgr
    
    def writeGachaTimeout(self, entry):
        """課金ガチャキャンセル書き込み.
        """
        try:
            model_mgr = db_util.run_in_transaction(self.__tr_write_gacha_timeout, entry['uid'], entry['id'])
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
    
    def __tr_write_gacha_timeout(self, uid, paymentId):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_gacha_timeout(model_mgr, uid, paymentId)
        model_mgr.write_all()
        return model_mgr
    
    def writeBuyItem(self, entry, is_pc):
        """購入書き込み.
        """
        try:
            model_mgr = db_util.run_in_transaction(self.__tr_write_buyitem, entry['uid'], entry['id'], is_pc)
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
    
    def __tr_write_buyitem(self, uid, paymentId, is_pc):
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_players(self, [uid], [PlayerRegist, PlayerGachaPt], model_mgr=model_mgr)[0]
        entry = BackendApi.tr_shopbuy(model_mgr, player, paymentId, is_pc)
        model_mgr.write_all()
        return model_mgr, entry
    
    def writeBuyCancel(self, entry):
        """キャンセル書き込み.
        """
        try:
            model_mgr = db_util.run_in_transaction(self.__tr_buy_cancel, entry['uid'], entry['id'])
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
    
    def __tr_buy_cancel(self, uid, paymentId):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_shopcancel(model_mgr, uid, paymentId)
        model_mgr.write_all()
        return model_mgr
    
    def writeBuyTimeOut(self, entry):
        """期限切れ書き込み.
        """
        try:
            model_mgr = db_util.run_in_transaction(self.__tr_buy_timeout, entry['uid'], entry['id'])
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
    
    def __tr_buy_timeout(self, uid, paymentId):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_shoptimeout(model_mgr, uid, paymentId)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
