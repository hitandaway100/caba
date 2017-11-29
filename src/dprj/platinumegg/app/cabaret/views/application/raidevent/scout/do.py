# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Player import PlayerAp,\
    PlayerExp, PlayerFriend
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
import settings_sub
import urllib
from defines import Defines
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.app.cabaret.models.raidevent.RaidEventScout import RaidEventScoutPlayData


class Handler(RaidEventBaseHandler):
    """レイドイベントスカウト実行.
    引数:
        リクエストキー.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def redirectWithError(self, err):
        url = self.makeAppLinkUrlRedirect(UrlMaker.raidevent_top())
        self.appRedirect(url)
    
    def process(self):
        
        args = self.getUrlArgs('/raideventscoutdo/')
        try:
            scoutkey = urllib.unquote(args.get(1))
            str_flag_skip = self.request.get(Defines.URLQUERY_SKIP)
            if not str_flag_skip in ('1', '0'):
                str_flag_skip = None
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 演出スキップフラグ.
        if str_flag_skip:
            flag_skip = bool(int(str_flag_skip))
            BackendApi.set_scoutskip_flag(uid, flag_skip)
        else:
            flag_skip = BackendApi.get_scoutskip_flag(uid)
        
        model_mgr = self.getModelMgr()
        
        using = settings.DB_DEFAULT
        
        eventmaster = self.getCurrentRaidEvent()
        mid = eventmaster.id
        
        # プレイ情報.
        playdata = BackendApi.get_raideventstage_playdata(model_mgr, mid, uid, using=using)
        
        # マスターデータ.
        stagemaster = BackendApi.get_current_raideventstage_master(model_mgr, eventmaster, playdata, using)
        
        if scoutkey == playdata.alreadykey:
            champagnecall_started = bool(playdata.result.get('champagne'))
        else:
            # シャンパン.
            champagnecall_start = BackendApi.get_raidevent_is_champagnecall_start(model_mgr, v_player.id, using=using)
            champagnecall = not champagnecall_start and BackendApi.get_raidevent_is_champagnecall(model_mgr, v_player.id, using=using)
            
            # 実行.
            champagnecall_started = False
            try:
                model_mgr, playdata = db_util.run_in_transaction(self.tr_write, eventmaster, uid, stagemaster, scoutkey, champagnecall_start, champagnecall)
                model_mgr.write_end()
                champagnecall_started = bool(playdata.result.get('champagne'))
            except CabaretError, err:
                if err.code == CabaretError.Code.ALREADY_RECEIVED:
                    model_mgr.delete_models_from_cache(RaidEventScoutPlayData, [RaidEventScoutPlayData.makeID(uid, mid)])
                elif err.code == CabaretError.Code.OVER_LIMIT:
                    # これ以上実行できない.
                    url = UrlMaker.raidevent_top()
                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
                    return
                else:
                    # うまく実行できない.
                    if settings_sub.IS_DEV:
                        # マスターデータが正しくないとかあるだろうからそのチェック用.
                        raise
                    # ここに来るのは不正アクセス等のユーザという想定.
                    self.redirectWithError(CabaretError(u'閲覧できないエリアです', CabaretError.Code.ILLEGAL_ARGS))
                    return
        
        if flag_skip:
            url = UrlMaker.raidevent_scoutresultanim(stagemaster.id, scoutkey, 0)
        else:
            url = UrlMaker.raidevent_scoutanim(stagemaster.id, scoutkey)
        
        if settings_sub.IS_BENCH:
            self.response.end()
        else:
            if champagnecall_started:
                params = BackendApi.make_raidevent_champagnecall_effectparams(self, eventmaster, url)
                if params:
                    # シャンパン演出へ.
                    effectpath = 'raidevent/showtime/effect.html'
                    self.appRedirectToEffect(effectpath, params)
                    return
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def tr_write(self, eventmaster, uid, stagemaster, scoutkey, champagnecall_start, champagnecall):
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_player(self, uid, [PlayerAp, PlayerExp, PlayerFriend], model_mgr=model_mgr)
        playdata = BackendApi.tr_do_raidevent_scout(model_mgr, eventmaster, player, stagemaster, scoutkey, self.is_pc, handler=self, champagnecall_start=champagnecall_start, champagnecall=champagnecall)
        model_mgr.write_all()
        return model_mgr, playdata

def main(request):
    return Handler.run(request)
