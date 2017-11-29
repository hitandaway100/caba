# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerGachaPt
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines


class Handler(AppHandler):
    """あいさつ実行.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGachaPt]
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        
        args = self.getUrlArgs('/greet/')
        oid = args.get(0, None)
        o_player = None
        if str(oid).isdigit():
            playerlist = BackendApi.get_players(self, [int(oid)], [], using=settings.DB_READONLY)
            if playerlist:
                o_player = playerlist[0]
        if o_player is None:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        point_pre = v_player.gachapt
        point_post = v_player.gachapt
        errcode = 0
        
        model_mgr = self.getModelMgr()
        is_friend = BackendApi.check_friend(v_player.id, o_player.id, model_mgr, using=settings.DB_READONLY)
        
        try:
            model_mgr = db_util.run_in_transaction(Handler.tr_write, v_player.id, o_player.id, is_friend)
            model_mgr.write_end()
            playergachapt = model_mgr.get_wrote_model(PlayerGachaPt, v_player.id)
            point_post = playergachapt.gachapt
        except CabaretError,e:
            if e.code in (CabaretError.Code.ALREADY_RECEIVED, CabaretError.Code.OVER_LIMIT):
                # 同じ相手へのあいさつは2時間に1度.
                # あいさつは1日に300回まで.
                errcode = e.code
            else:
                raise
        
        model_mgr = ModelRequestMgr()
        
        # 余分なあいさつ履歴を削除.
        BackendApi.delete_extra_greetlog(model_mgr, o_player.id)
        
        logdata = BackendApi.get_greetlog_last(model_mgr, v_player.id, o_player.id, using=settings.DB_READONLY)
        if logdata:
            logid = logdata.id
        else:
            logid = 0
        
        url = UrlMaker.greet_complete(o_player.id, errcode, point_pre, point_post, logid)
        url = self.makeAppLinkUrlRedirect(url)
        self.appRedirect(url)
    
    @staticmethod
    def tr_write(uid, oid, is_friend):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_greet(model_mgr, uid, oid, is_friend)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
