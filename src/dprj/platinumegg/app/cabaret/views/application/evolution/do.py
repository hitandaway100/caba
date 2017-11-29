# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.evolution.base import EvolutionHandler
from platinumegg.app.cabaret.models.Player import PlayerGold, PlayerDeck
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
import settings_sub
import urllib
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Card import Card


class Handler(EvolutionHandler):
    """進化合成実行.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold, PlayerDeck]
    
    def procBench(self):
        v_player = self.getViewerPlayer()
        uid = v_player.id
        self.__baseid = Card.makeID(uid, 11)
        self.__materialid = Card.makeID(uid, 12)
    
    def process(self):
        args = self.getUrlArgs('/evolutiondo/')
        try:
            if settings_sub.IS_BENCH:
                requestkey = OSAUtil.makeSessionID()
            else:
                self.__baseid = int(args.get(0))
                self.__materialid = self.getMaterialId()
                requestkey = urllib.unquote(args.get(1))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        
        try:
            model_mgr = db_util.run_in_transaction(Handler.tr_write, v_player, self.__baseid, self.__materialid, requestkey)
            model_mgr.write_end()
        except CabaretError,e:
            if e.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                if settings_sub.IS_LOCAL:
                    raise CabaretError(u'合成できませんでした.%s' % CabaretError.getCodeString(e.code))
                url = UrlMaker.evolution()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        url = UrlMaker.evolutionanim()
        if settings_sub.IS_BENCH:
            self.response.set_status(200)
            self.response.send()
        else:
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    @staticmethod
    def tr_write(v_player, basecardid, materialcardid, key):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_evolution_do(model_mgr, v_player, basecardid, materialcardid, key)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
