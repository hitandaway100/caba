# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Player import PlayerScout, PlayerAp,\
    PlayerExp, PlayerRegist, PlayerFriend, PlayerDeck
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.views.application.scout.base import ScoutHandler
import settings_sub
from defines import Defines
from platinumegg.app.cabaret.models.Scout import ScoutPlayData
import urllib


class Handler(ScoutHandler):
    """スカウト実行.
    引数:
        実行するスカウトID.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def redirectWithError(self, err):
        if self.is_pc:
            raise err
        else:
            url = self.makeAppLinkUrlRedirect(UrlMaker.scout())
            self.appRedirect(url)
    
    def process(self):
        try:
            # スカウトID.
            args = self.getUrlArgs('/scoutdo/')
            scoutid = int(args.get(0)) or None
            scoutkey = urllib.unquote(args.get(1) or '')
            str_flag_skip = self.request.get(Defines.URLQUERY_SKIP)
            if not str_flag_skip in ('1', '0'):
                str_flag_skip = None
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        
        # 演出スキップフラグ.
        if str_flag_skip:
            flag_skip = bool(int(str_flag_skip))
            BackendApi.set_scoutskip_flag(v_player.id, flag_skip)
        else:
            flag_skip = BackendApi.get_scoutskip_flag(v_player.id)
        
        model_mgr = self.getModelMgr()
        
        using = settings.DB_DEFAULT
        
        # マスターデータ.
        scoutmaster = None
        if scoutid:
            scoutmasterlist = BackendApi.get_scouts(model_mgr, [scoutid], using)
            scoutmaster = scoutmasterlist[0] if scoutmasterlist else None
        if scoutmaster is None:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        areamaster = BackendApi.get_area(model_mgr, scoutmaster.area, using)
        if areamaster is None:
            self.redirectWithError(CabaretError(u'閲覧できないエリアです', CabaretError.Code.ILLEGAL_ARGS))
            return
        
        # 遊べるかを確認.
        if not BackendApi.check_scout_playable(model_mgr, scoutmaster, v_player, using):
            # クリア条件を満たしていない.
            self.redirectWithError(CabaretError(u'閲覧できないエリアです', CabaretError.Code.ILLEGAL_ARGS))
            return
        
        if not scoutkey:
            scoutkey = BackendApi.get_scoutkey(model_mgr, v_player.id, scoutmaster.id, using)
        
        # SHOWTIME確認.
        raideventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=using)
        if raideventmaster is None or raideventmaster.flag_dedicated_stage:
            champagnecall_start = False
            champagnecall = False
        else:
            champagnecall_start = BackendApi.get_raidevent_is_champagnecall_start(model_mgr, v_player.id, using=using)
            champagnecall = not champagnecall_start and BackendApi.get_raidevent_is_champagnecall(model_mgr, v_player.id, using=using)

        # 実行.
        champagnecall_started = False
        try:
            model_mgr, playdata = db_util.run_in_transaction(self.tr_write, v_player.id, scoutmaster, scoutkey, champagnecall, champagnecall_start)
            model_mgr.write_end()
            champagnecall_started = bool(playdata.result.get('champagne'))
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                model_mgr.delete_models_from_cache(ScoutPlayData, [ScoutPlayData.makeID(v_player.id, scoutmaster.id)])
            else:
                # うまく実行できない.
                if settings_sub.IS_DEV:
                    # マスターデータが正しくないとかあるだろうからそのチェック用.
                    raise
                # ここに来るのは不正アクセス等のユーザという想定.
                self.redirectWithError(CabaretError(u'閲覧できないエリアです', CabaretError.Code.ILLEGAL_ARGS))
                return
        
        if flag_skip:
            url = UrlMaker.scoutresultanim(scoutmaster.id, scoutkey, 0)
        else:
            url = UrlMaker.scoutanim(scoutmaster.id, scoutkey)
        if settings_sub.IS_BENCH:
            self.response.end()
        else:
            if champagnecall_started:
                params = BackendApi.make_raidevent_champagnecall_effectparams(self, raideventmaster, url)
                if params:
                    # シャンパン演出へ.
                    effectpath = 'raidevent/showtime/effect.html'
                    self.appRedirectToEffect(effectpath, params)
                    return
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def tr_write(self, uid, scoutmaster, scoutkey, champagnecall, champagnecall_start):
        model_mgr = ModelRequestMgr(loginfo=self.addloginfo)
        player = BackendApi.get_players(self, [uid], [PlayerAp, PlayerScout, PlayerRegist, PlayerExp, PlayerFriend, PlayerDeck], model_mgr=model_mgr)[0]
        playdata = BackendApi.tr_do_scout(model_mgr, player, scoutmaster, scoutkey, champagnecall=champagnecall, champagnecall_start=champagnecall_start)
        model_mgr.write_all()
        return model_mgr, playdata

def main(request):
    return Handler.run(request)
