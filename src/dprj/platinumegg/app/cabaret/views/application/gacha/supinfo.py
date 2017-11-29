# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import urllib
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
import settings
from platinumegg.app.cabaret.util.card import CardSet
from defines import Defines


class Handler(GachaHandler):
    """ステップアップガチャ説明.
    """
    
    def process(self):
        args = self.getUrlArgs('/gachasupinfo/')
        try:
            mid = int(args.get(0))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        
        self.writeAppHtml('gacha/supinfo')
    

def main(request):
    return Handler.run(request)
