# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
import settings_sub


class Handler(AppHandler):
    """シリアルコードキャンペーンTopページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        # メッセージ.
        self.__msg = None
        
        model_mgr = self.getModelMgr()
        args = self.getUrlArgs('/serial_input/')
        
        # マスター.
        mid = args.getInt(0)
        master = None
        if mid:
            master = BackendApi.get_serialcampaign_master(model_mgr, mid, using=settings.DB_READONLY)
        if master is None:
            # 存在しないキャンペーン.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return
        elif not BackendApi.check_schedule(model_mgr, master.schedule, using=settings.DB_READONLY):
            # 期間外.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.serial_top(mid)))
            return
        
        self.html_param['serialcode'] = ''
        
        is_post = False
        if settings_sub.IS_LOCAL and self.request.get('_test'):
            # ローカルのテスト.
            is_post = bool(self.request.get(Defines.URLQUERY_SERIALCODE))
        else:
            is_post = self.request.method == 'POST'
        
        if is_post:
            self.__processPost(master)
        
        # 入力ページのURL.
        url = UrlMaker.serial_input(mid)
        self.html_param['url_input'] = self.makeAppLinkUrl(url)
        
        # エラーメッセージ.
        self.html_param['message'] = self.__msg
        
        self.writeAppHtml('serialcode/input')
    
    def __setMessage(self, msg):
        self.__msg = msg
    
    def __processPost(self, master):
        """シリアルコード入力プロセス.
        """
        serialcode = self.request.get(Defines.URLQUERY_SERIALCODE)
        if not serialcode:
            # 未入力.
            return
        
        self.html_param['serialcode'] = serialcode
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        mid = master.id
        
        # シリアルコード確認.
        serialcode_model = BackendApi.get_serialcode_by_serial(model_mgr, serialcode, using=settings.DB_READONLY)
        if serialcode_model is None or serialcode_model.mid != mid:
            self.__setMessage(u'シリアルコード入力に失敗しました。<br />シリアルコードをお確かめのうえ<br />再度ご入力をお願いします。')
            return
        elif serialcode_model.uid != 0:
            user = u'あなた' if serialcode_model.uid == uid else u'他のユーザー'
            self.__setMessage(u'入力したシリアルコードは<br />既に使用されています。<br />%sに<br />%sが使用しました。' % (serialcode_model.itime.strftime(u"%Y年%m月%d日 %H:%M"), user))
            return
        
        # 入力回数確認.
        if 0 < master.limit_pp:
            serial_count = BackendApi.get_serialcode_count_model(model_mgr, uid, mid, using=settings.DB_READONLY)
            if serial_count and master.limit_pp <= serial_count.cnt:
                self.__setMessage(u'シリアルコード入力に失敗しました。<br />シリアルコードの入力はお一人様につき%d回までとなっております。' % master.limit_pp)
                return
        
        # 書き込み.
        serialcodeid = serialcode_model.id
        try:
            db_util.run_in_transaction(Handler.tr_write, uid, master, serialcodeid, self.is_pc).write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                if err.value.find('Already') != -1:
                    # 自分じゃない誰かが使用した.
                    serialcode_model = BackendApi.get_serialcode_by_id(ModelRequestMgr(), serialcodeid)
                    self.__setMessage(u'入力したシリアルコードは既に使用されています。<br />%sに他のユーザーが使用しました。' % serialcode_model.itime.strftime("%Y/%m/%d %H:%M"))
                    return
            elif err.code == CabaretError.Code.OVER_LIMIT:
                self.__setMessage(u'シリアルコード入力に失敗しました。<br />シリアルコードの入力はお一人様につき%d回までとなっております。' % master.limit_pp)
                return
            else:
                raise
        self.__setMessage(u'シリアルコード入力に成功しました!<br />アイテムはプレゼントに送られています。')
    
    @staticmethod
    def tr_write(uid, master, serialcodeid, is_pc):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_input_serialcode(model_mgr, uid, master, serialcodeid, is_pc)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
