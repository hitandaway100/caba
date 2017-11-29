# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
import settings_sub


class Handler(AppHandler):
    """ポップアップの閲覧フラグをたてる.
    """
    
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 500
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        args = self.getUrlArgs('/popupview/')
        mid = args.getInt(0)
        
        master = None
        if mid:
            model_mgr = self.getModelMgr()
            master = BackendApi.get_popupbanner(model_mgr, mid, using=settings.DB_READONLY)
        
        if not master:
            self.response.end()
            return
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 閲覧状態を更新.
        if not settings_sub.IS_LOCAL or self.request.get("_test"):
            BackendApi.update_popup_flag(uid, [mid])
        
        # ポップアップの情報を組み込む.
        self.json_result_param['popupbanner'] = Objects.popup(self, master)
        
        self.response.set_status(200)
        self.writeAppJson()

def main(request):
    return Handler.run(request)
