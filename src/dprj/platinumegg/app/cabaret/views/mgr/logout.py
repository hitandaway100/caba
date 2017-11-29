# -*- coding: utf-8 -*-
from django.contrib.auth import logout
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker

class Handler(AdminHandler):
    """ログアウト.
    """
    
    def process(self):
        logout(self.request.django_request)
        url = UrlMaker.login()
        self.appRedirect(self.makeAppLinkUrl(url))

def main(request):
    return Handler.run(request)
