# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings


class Handler(AppHandler):
    """クロスプロモーション条件チェックＡＰＩ.
    """
    
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 500
    
    def processError(self, error_message):
        self.response.set_status(500)
        self.response.end()
    
    def __sendErrorResponse(self, status):
        self.response.set_status(status)
        self.response.end()
    
    def checkUser(self):
        pass
    
    def check_process_pre(self):
        return True
    
    def process(self):
        args = self.getUrlArgs('/promotioncheck/')
        try:
            appname = args.get(0, '')
            dmmid = args.get(1, '')
            requirement_idlist = [int(s) for s in args.get(2, '').split(',') if s.isdigit()]
        except:
            self.__sendErrorResponse(404)
            return
        
        model_mgr = self.getModelMgr()
        
        config = BackendApi.get_promotionconfig(model_mgr, appname, using=settings.DB_READONLY)
        if config is None:
            # アプリが存在しない.
            self.__sendErrorResponse(404)
            return
        
        # ユーザーの存在確認.
        uid = None
        if dmmid:
            uid = BackendApi.dmmid_to_appuid(self, [dmmid], using=settings.DB_READONLY).get(dmmid, None)
        if uid is None:
            self.__sendErrorResponse(404)
            return
        
        if requirement_idlist:
            requirementlist = BackendApi.get_promotionrequirementmaster_list(model_mgr, appname, requirement_idlist, using=settings.DB_READONLY)
        else:
            # 全て検索.
            requirementlist = BackendApi.get_promotionrequirementmaster_all(model_mgr, appname, using=settings.DB_READONLY)
        
        if not requirementlist:
            self.__sendErrorResponse(404)
            return
        
        json_obj = {}
        
        for requirement in requirementlist:
            flag = BackendApi.check_promotionrequirement(self, uid, requirement)
            json_obj[str(requirement.id)] = 'true' if flag else 'false' # PHPの方々は文字列にして欲しいらしいのでもう文字列で統一.
        
        self.response.set_status(200)
        self.osa_util.write_json_obj(json_obj)

def main(request):
    return Handler.run(request)

