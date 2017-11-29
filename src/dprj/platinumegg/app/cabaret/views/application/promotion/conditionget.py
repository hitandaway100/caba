# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.lib.strutil import StrUtil
from platinumegg.lib.pljson import Json


class Handler(AppHandler):
    """クロスプロモーション条件一覧取得ＡＰＩ.
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
        args = self.getUrlArgs('/promotionconditionget/')
        try:
            appname = args.get(0, '')
            requirement_idlist = [int(s) for s in args.get(1, '').split(',') if s.isdigit()]
        except:
            self.__sendErrorResponse(404)
            return
        
        model_mgr = self.getModelMgr()
        
        config = BackendApi.get_promotionconfig(model_mgr, appname, using=settings.DB_READONLY)
        if config is None:
            # アプリが存在しない.
            self.__sendErrorResponse(404)
            return
        
        if requirement_idlist:
            requirementlist = BackendApi.get_promotionrequirementmaster_list(model_mgr, appname, requirement_idlist, using=settings.DB_READONLY)
        else:
            # 全て検索.
            requirementlist = BackendApi.get_promotionrequirementmaster_all(model_mgr, appname, using=settings.DB_READONLY)
        
        json_obj = {}
        
        for requirement in requirementlist:
            text = requirement.text
            json_obj[str(requirement.id)] = text
        json_data = StrUtil.to_s(Json.encode(json_obj, ensure_ascii=False))
        
        self.response.set_status(200)
        self.osa_util.write_json_data(json_data)
        
#        self.response.set_header('Content-Type', 'application/json; charset=utf-8')
#        self.response.send(StrUtil.to_s(u'{"a":"あいうえお"}'))

def main(request):
    return Handler.run(request)

