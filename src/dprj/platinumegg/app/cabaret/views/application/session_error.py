# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.lib.opensocial.util import OSAUtil
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker


class Handler(AppHandler):
    """セッション切れ.
    """
    def process(self):
        if settings_sub.IS_DEV:
            self.html_param['dbg_print_log'] = OSAUtil.makeRequestInfo(self.request, '<br />',self.osa_util.init_time)
        
        self.html_param['url_session_callback'] = self.makeAppLinkUrl(UrlMaker.top(), add_frompage=False)
        
        self.html_param['is_dev'] = self.osa_util.is_dbg_user
        self.writeAppHtml('session_error')
    
    def checkUser(self):
        pass

def main(request):
    return Handler.run(request)
