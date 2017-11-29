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
import settings


class Handler(LoginBonusHandler):
    """ログインボーナス書き込み.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        now = OSAUtil.get_now()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        
        # 累計ログインの設定.
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_totalloginbonusconfig(model_mgr, using=settings.DB_READONLY)
        mid = config.getCurrentMasterID(now)
        if mid:
            totallogintable = BackendApi.get_loginbonustimelimiteddaysmaster_day_table_by_timelimitedmid(model_mgr, mid, using=settings.DB_READONLY)
        else:
            totallogintable = {}

        # 実行.
        try:
            model_mgr, result = db_util.run_in_transaction(self.tr_write, v_player.id, now, config, totallogintable)
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                # 書き込み済み.
                if settings_sub.IS_LOCAL:
                    raise
                result = {}
            else:
                # うまく実行できない.
                if settings_sub.IS_DEV:
                    # マスターデータが正しくないとかあるだろうからそのチェック用.
                    raise
                # ここに来るのは不正アクセス等のユーザという想定.
                self.redirectToTop()
                return
        
        # 演出のURL.
        timelimited_result = result.get('timelimited')
        comeback = result.get('comeback')
        sugoroku_result = result.get('sugoroku')
        url = None
        if comeback:
            url = UrlMaker.comebackanim(comeback[0], True)
        elif sugoroku_result:
            url = self.makeUrlBySugorokuResult(sugoroku_result, True)
        elif timelimited_result:
            url = self.makeUrlByTimeLimitedResult(timelimited_result, True)
        if url is None:
            url = UrlMaker.loginbonusanim()
        
        # クエリをつける.
        if comeback: url = self.addComeBackResultQueryString(url, comeback)
        if timelimited_result: url = self.addTimeLimitedResultQueryString(url, timelimited_result)
        if sugoroku_result:  url = self.addSugorokuResultQueryString(url, sugoroku_result)
        
        if settings_sub.IS_BENCH:
            self.response.set_status(200)
            self.response.send()
        else:
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def tr_write(self, uid, now, config, totallogintable):
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_players(self, [uid], [PlayerExp], model_mgr=model_mgr)[0]
        result = BackendApi.tr_send_loginbonus(model_mgr, player, now, config, totallogintable, self.is_pc)
        model_mgr.write_all()
        return model_mgr, result

def main(request):
    return Handler.run(request)
