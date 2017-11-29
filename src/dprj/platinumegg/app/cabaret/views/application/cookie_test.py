# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.lib import timezone
import datetime

class Handler(AppHandler):
    """Cookie試験.
    """
    
    def process(self):
        
        args = self.getUrlArgs('/cookie_test/')
        table = {
            'view' : self.procView,
            'write' : self.procWrite,
        }
        f = table.get(args.get(0)) or self.procView
        f()
    
    def procView(self):
        self.html_param['cookies'] = self.request.cookies
        self.html_param['url_exec'] = self.makeAppLinkUrl('/cookie_test/write')
        self.html_param['url_callback'] = self.makeAppLinkUrl('/cookie_test/view')
        self.osa_util.write_html('test/cookie_test.html', self.html_param)
    
    def procWrite(self):
        now = OSAUtil.get_now(timezone.TZ_UTC)
        self.response.set_cookie('hogehoge1', self.osa_util.viewer_id, expires=now+datetime.timedelta(days=1), domain='sba-netgame.dmm.com')
        self.response.set_cookie('hogehoge2', self.osa_util.viewer_id, expires=now+datetime.timedelta(days=1), domain='211.130.152.227')
        self.response.set_cookie('hogehoge3', self.osa_util.viewer_id, expires=now+datetime.timedelta(days=1), domain=self.request.domain)
        
        callback_url = self.request.get('callback_url')
        if not callback_url:
            # APIで呼ばれていないっぽい.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.top()))
        else:
            self.appRedirect(callback_url)
    
    def checkUser(self):
        pass

def main(request):
    return Handler.run(request)
