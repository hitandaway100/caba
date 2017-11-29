# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Player import PlayerAp,\
    PlayerExp, PlayerFriend, PlayerRegist, PlayerRequest
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
import urllib


class Handler(HappeningHandler):
    """ハプニング実行書き込み.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRequest]
    
    def process(self):
        
        # 状態のチェック.
        happeningset = self.getHappening()
        if happeningset is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'ハプニングがありません', CabaretError.Code.ILLEGAL_ARGS)
            url = UrlMaker.happening()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        elif happeningset.happening.is_end() or happeningset.happening.is_cleared():
            # 終了済み.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'終了済みです', CabaretError.Code.NOT_DATA)
            url = UrlMaker.happeningend(happeningset.id)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        
        try:
            #if self.is_pc:
            #    confirmkey = v_player.req_confirmkey
            #else:
            #    args = self.getUrlArgs('/happeningdo/')
            #    confirmkey = urllib.unquote(args.get(0, ''))
            args = self.getUrlArgs('/happeningdo/')
            confirmkey = urllib.unquote(args.get(0, ''))
        except:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'確認用のキーがありません', CabaretError.Code.ILLEGAL_ARGS)
            url = UrlMaker.happening()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # ハプニング情報.
        master = happeningset.master
        
        # 実行.
        try:
            model_mgr = db_util.run_in_transaction(self.tr_write, v_player.id, master, confirmkey)
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                # 書き込み済み.
                pass
            elif err.code == CabaretError.Code.OVER_LIMIT:
                # ボス出現中.
                if settings_sub.IS_LOCAL:
                    raise CabaretError(u'超太客が出現しています', CabaretError.Code.OVER_LIMIT)
            elif err.code == CabaretError.Code.NOT_DATA:
                # 終了している.
                if settings_sub.IS_LOCAL:
                    raise CabaretError(u'この超太客は終了しました', CabaretError.Code.NOT_DATA)
                url = UrlMaker.happeningend(happeningset.id)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
            else:
                # うまく実行できない.
                if settings_sub.IS_DEV:
                    raise
                # ここに来るのは不正アクセス等のユーザという想定.
                url = self.makeAppLinkUrlRedirect(UrlMaker.happening())
                self.appRedirect(url)
                return
        
        # 結果へリダイレクト.
        url = self.makeAppLinkUrlRedirect(UrlMaker.happeninganim(confirmkey))
        self.appRedirect(url)
    
    def tr_write(self, uid, master, key):
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_players(self, [uid], [PlayerAp, PlayerRegist, PlayerExp, PlayerFriend], model_mgr=model_mgr)[0]
        BackendApi.tr_do_happening(model_mgr, player, master, key)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
