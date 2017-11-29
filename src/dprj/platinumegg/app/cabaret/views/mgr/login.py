# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate, login
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.app.cabaret.util.url_maker import UrlMaker

class Handler(AdminHandler):
    """ログイン.
    """
    def checkUser(self):
        pass
    
    def process(self):
        
        username = self.request.get('_name', '')
        password = self.request.get('_pass', '')
        
        if self.request.method == 'POST':
            # 何か入力された.
            if self.loginApp(username, password):
                # ろぐいん成功.
                url = UrlMaker.index()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
            else:
                # ろぐいん失敗.
                self.putAlertToHtmlParam('ユーザー名かパスワードが違います', AlertCode.ERROR)
        
        url = UrlMaker.login()
        self.html_param['url_login'] = self.makeAppLinkUrl(url)
        self.writeAppHtml('login')
    
    def loginApp(self, username, password):
        """
        """
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request.django_request, user)
                return True
            else:
                return False
        else:
            return False

def main(request):
    return Handler.run(request)
