# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.views.application.loginbonus.base import LoginBonusHandler
from platinumegg.app.cabaret.models.Player import PlayerExp
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(LoginBonusHandler):
    """期間別ログインボーナス書き込み.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        
        # 実行.
        try:
            model_mgr, result = db_util.run_in_transaction(self.tr_write, v_player.id, OSAUtil.get_now())
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                # 書き込み済み.
                if settings_sub.IS_LOCAL:
                    raise
                result = []
            else:
                # うまく実行できない.
                if settings_sub.IS_DEV:
                    # マスターデータが正しくないとかあるだろうからそのチェック用.
                    raise
                # ここに来るのは不正アクセス等のユーザという想定.
                self.redirectToTop()
                return
        
        # 演出へリダイレクト.
        url = None
        if result:
            url = self.makeUrlByTimeLimitedResult(result, False)
            if url:
                url = self.addTimeLimitedResultQueryString(url, result)
        
        if url is None:
            url = UrlMaker.mypage()
        
        if settings_sub.IS_BENCH:
            self.response.set_status(200)
            self.response.send()
        else:
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def tr_write(self, uid, now):
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_players(self, [uid], [PlayerExp], model_mgr=model_mgr)[0]
        result = BackendApi.tr_send_loginbonustimelimited(model_mgr, player, now)
        model_mgr.write_all()
        return model_mgr, result

def main(request):
    return Handler.run(request)
