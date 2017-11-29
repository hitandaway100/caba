# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings


class Handler(GachaHandler):
    """PC版メンテナンスページ.
    """
    
    def checkMaintenance(self):
        """メンテナンスチェック.
        """
        return True
    
    def checkUser(self):
        pass
    
    def process(self):
        model_mgr = self.getModelMgr()
        app_config = BackendApi.get_appconfig(model_mgr, using=settings.DB_READONLY)
        self.html_param['is_maintenance'] = app_config.is_maintenance()
        self.html_param['is_emergency'] = app_config.is_emergency()
        self.html_param['stime'] = app_config.stime
        self.html_param['etime'] = app_config.etime
        self.writeAppHtml('pc_maintenance')

def main(request):
    return Handler.run(request)
