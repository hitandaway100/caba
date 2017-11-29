# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerRegist, PlayerTutorial
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.lib.platform.api.objects import PaymentData


class Handler(AppHandler):
    """Topページ.
    Top画像.
    ユーザ登録済み.
    ->チュートリアル完了済み.
        - スライドバナー.
        - イベントバナー.
        - 更新情報.
        - top.html
    ->チュートリアル未完了.
        -> チュートリアル復帰用のURL.
        -> top_notregisterd.html
    ->ユーザ未登録.
        -> タイプ選択へのURL.
        -> top_notregisterd.html
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRegist, PlayerTutorial]
    
    def procMaintenance(self):
        """メンテナンス状態の操作.
        """
        model_mgr = self.getModelMgr()
        app_config = BackendApi.get_appconfig(model_mgr, using=settings.DB_READONLY)
        # person.
        self.html_param['is_emergency'] = app_config.is_emergency()
        self.html_param['stime'] = app_config.stime
        self.html_param['etime'] = app_config.etime
        self.writeAppHtml('maintenance')
    
    def checkBeforePublication(self):
        """公開チェック.
        """
        return True
    
#    def checkUserAgent(self):
#        """端末チェック.
#        """
#        model_mgr = self.getModelMgr()
#        preregist_config = BackendApi.get_preregistconfig(model_mgr, using=settings.DB_READONLY)
#        if preregist_config.is_before_publication():
#            return True
#        else:
#            return AppHandler.checkUserAgent(self)
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        
        self.setFromPage(None)
        
#        installed = False
        v_player = self.getViewerPlayer(quiet=True)
        if v_player is None:
            if not settings_sub.IS_DEV and self.osa_util.is_admin_access and self.osa_util.is_dbg_user:
                # これは作らない方がいい.
                raise CabaretError(u'このアクセスで新規登録は危険です', CabaretError.Code.ILLEGAL_ARGS)
            
            # 初回アクセス.
            preregist_config = BackendApi.get_preregistconfig(model_mgr, using=settings.DB_READONLY)
            preregist = preregist_config.is_before_publication() and self.check_support_terminal()
            v_player = BackendApi.install(self, preregist=preregist)
#            installed = True
        
        # Top画像.
        self.putTopImageUrl()
        
#        preregist_config = BackendApi.get_preregistconfig(model_mgr, using=settings.DB_READONLY)
#        if preregist_config.is_before_publication():
#            if not installed and not v_player.preregist and v_player.preregist != self.check_support_terminal():
#                def tr():
#                    model_mgr = ModelRequestMgr()
#                    player = model_mgr.get_model(Player, v_player.id)
#                    player.preregist = True
#                    model_mgr.set_save(player)
#                    model_mgr.write_all()
#                    return model_mgr, player
#                tmp, player = db_util.run_in_transaction(tr)
#                tmp.write_end()
#                v_player.setModel(player)
#            self.processPreRegist(v_player)
#        else:
        self.proceccPublication(v_player)
    
    def processTutorialCompleted(self):
        """チュートリアル完了済みのユーザー.
        """
        
        # 課金チェック.
        self.checkPayment()
        
        # スライドバナー.
        slidebanners = BackendApi.get_topbanners(self, using=settings.DB_READONLY)
        if slidebanners:
            obj_slidebanners = []
            for banner in slidebanners:
                obj_banner = Objects.topbanner(self, banner)
                if not obj_banner['is_external_link']:
                    # 外部リンクじゃない時だけにしておく.
                    obj_slidebanners.append(object)
            self.html_param['slidebanners'] = obj_slidebanners
        
        # イベントバナー.
        self.html_param['groups'] = BackendApi.get_tabeventbanners(self, using=settings.DB_READONLY)
        
        # 更新情報.
        if self.is_pc:
            infomations = BackendApi.get_infomation_all(self, using=settings.DB_READONLY)[:20]
            self.html_param['infomations'] = [Objects.infomation(self, infomation) for infomation in infomations]
        else:
            infomations, _ = BackendApi.get_infomations(self, 0, using=settings.DB_READONLY)
            if 0 < len(infomations):
                arr = []
                date_new = None
                for infomation in infomations[:2]:
                    obj = Objects.infomation(self, infomation)
                    date_new = date_new or obj['date']
                    obj['is_new'] = date_new == obj['date']
                    arr.append(obj)
                self.html_param['infomations'] = arr
        
        url = UrlMaker.mypage()
        self.html_param['url_enter'] = self.makeAppLinkUrl(url)
        
#         if settings_sub.IS_LOCAL:
#             self.html_param['slidebanners'] = [Objects.topbanner(self, topbanner)]
#             self.html_param['eventbanners'] = [Objects.eventbanner(self, eventbanner)]
#             self.html_param['infomation'] = [Objects.infomation(self, infomation)]
        # top.html
        self.writeAppHtml('top/top')
    
    def processTutorial(self):
        """チュートリアル中のユーザー.
        """
        # チュートリアル復帰用のURL.
        self.html_param['url_enter'] = self.makeAppLinkUrl(UrlMaker.tutorial())
        
        # top_notregisterd.html.
        self.writeAppHtml('top/top_notregisterd')
    
    def processNotRegistered(self):
        """未登録ユーザー.
        """
        # タイプ選択へのURL.
        self.html_param['url_enter'] = self.makeAppLinkUrl(UrlMaker.regist())
        
        # top_notregisterd.html.
        self.writeAppHtml('top/top_notregisterd')
    
    def proceccPublication(self, v_player):
        """公開中.
        """
        if v_player.getModel(PlayerRegist) is None:
            self.processNotRegistered()
            return
        player_tutorial = v_player.getModel(PlayerTutorial)
        if player_tutorial.tutorialstate == Defines.TutorialStatus.COMPLETED:
            # チュートリアル完了済み.
            self.processTutorialCompleted()
        else:
            # チュートリアル未完了.
            self.processTutorial()
    
    def processPreRegist(self, v_player):
        """事前登録.
        """
        if v_player.preregist:
            # 事前登録を受け付けた.
            person = BackendApi.get_dmmplayers(self, [v_player], using=settings.DB_READONLY, do_execute=True).get(v_player.dmmid)
            if person.userType in ('developer','Staff') or self.osa_util.is_dbg_user:
                # 関係者はそのままアプリ開始.
                self.proceccPublication(v_player)
            else:
                self.writeAppHtml('preregist/success')
        else:
            self.writeAppHtml('preregist/non_terminal')
    
    def putTopImageUrl(self):
        model_mgr = self.getModelMgr()
        
        # イベント.
        master = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY) \
                or BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY) \
                or BackendApi.get_current_battleevent_master(model_mgr, using=settings.DB_READONLY)
        
        if master and master.topimg:
            imgUrl = master.topimg
        else:
            imgUrl = '00/id_00_01/3rd_anniversary_sp_top.png'
        
        self.html_param['url_topimage'] = self.makeAppLinkUrlImg(imgUrl)
    
    def checkPayment(self):
        """課金レコードチェック.
        """
        v_player = self.getViewerPlayer()
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
                else:
                    # タイムアウト書き込み.
                    self.writeGachaTimeout(paymentId)
            update = updateGacha
        elif kind == 'shop':
            modellist = BackendApi.get_shoppaymententry_list(v_player.id, False, 1, 0, using=settings.DB_READONLY)
            def updateShop(paymentId, status):
                if status == PaymentData.Status.COMPLETED:
                    # 購入書き込み.
                    self.writeBuyItem(paymentId)
                elif status == PaymentData.Status.CANCEL:
                    # キャンセル書き込み.
                    self.writeBuyCancel(paymentId)
                else:
                    # タイムアウト書き込み.
                    self.writeBuyTimeOut(paymentId)
            update = updateShop
        else:
            return
        
        if not modellist:
            BackendApi.delete_payment_lostrecords_flag(v_player.id)
            return
        
        paymentId = modellist[0].id
        status = BackendApi.get_restful_paymentrecord_status(self, paymentId)
        update(paymentId, status)
    

def main(request):
    return Handler.run(request)
