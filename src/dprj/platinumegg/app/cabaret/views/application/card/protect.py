# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.card.boxbase import BoxHandler
from defines import Defines
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.api import BackendApi
import settings
import settings_sub
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr


class Handler(BoxHandler):
    """カード保護.
    """
    def process(self):
        
        v_player = self.getViewerPlayer()
        
        flags = {}
        flags.update(self.loadCardIds(Defines.URLQUERY_ADD, True))
        flags.update(self.loadCardIds(Defines.URLQUERY_REM, False))
        
        if flags:
            cardsetlist = BackendApi.get_cards(flags.keys(), self.getModelMgr(), using=settings.DB_READONLY)
            tmp_flags = {}
            for cardset in cardsetlist:
                if v_player.id != cardset.card.uid:
                    del flags[cardset.id]
                    if settings_sub.IS_LOCAL:
                        raise CabaretError(u'不正なアクセス')
                    url = UrlMaker.cardbox()
                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
                    return
                tmp_flags[cardset.id] = flags[cardset.id]
            if tmp_flags:
                model_mgr = db_util.run_in_transaction(self.tr_write, tmp_flags)
                model_mgr.write_end()
        url = UrlMaker.cardbox()
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def loadCardIds(self, key, flag):
        flags = {}
        try:
            str_cardidlist = self.request.get(key, None)
            if str_cardidlist:
                flags = dict.fromkeys([int(str_cardid) for str_cardid in str_cardidlist.split(',') if str_cardid], flag)
        except:
            pass
        return flags
    
    def tr_write(self, flags):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_set_cardprotection(model_mgr, flags)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
