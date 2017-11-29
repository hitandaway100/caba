# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.composition.base import CompositionHandler
from platinumegg.app.cabaret.models.Player import PlayerGold
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
import settings_sub
import urllib
from platinumegg.app.cabaret.models.Card import Card
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(CompositionHandler):
    """合成実行.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold]
    
    def procBench(self):
        v_player = self.getViewerPlayer()
        uid = v_player.id
        cardidlist = [Card.makeID(uid, i) for i in xrange(11, 21)]
        
        self.__baseid = cardidlist[0]
        self.__materialidlist = cardidlist[1:]
    
    def process(self):
        args = self.getUrlArgs('/compositiondo/')
        try:
            if settings_sub.IS_BENCH:
                requestkey = OSAUtil.makeSessionID()
            else:
                self.__baseid = int(args.get(0))
                self.__materialidlist = self.getMaterialIdList()
                requestkey = urllib.unquote(args.get(1))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        
        try:
            model_mgr = db_util.run_in_transaction(Handler.tr_write, v_player.id, self.__baseid, self.__materialidlist, requestkey)
            model_mgr.write_end()
        except CabaretError,e:
            if e.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                if settings_sub.IS_LOCAL:
                    raise CabaretError(u'合成できませんでした.%s' % CabaretError.getCodeString(e.code))
                url = UrlMaker.composition()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        url = UrlMaker.compositionanim()
        
        if settings_sub.IS_BENCH:
            self.response.set_status(200)
            self.response.send()
        else:
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    @staticmethod
    def tr_write(uid, basecardid, materialcardidlist, key):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_composition_do(model_mgr, uid, basecardid, materialcardidlist, key)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
