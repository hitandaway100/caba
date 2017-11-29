# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Player import PlayerAp,\
    PlayerExp, PlayerFriend
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler
import settings_sub
import urllib
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventPlayData
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(ScoutHandler):
    """スカウト実行.
    引数:
        実行するスカウトID.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def redirectWithError(self, err):
        url = self.makeAppLinkUrlRedirect(UrlMaker.scoutevent())
        self.appRedirect(url)
    
    def process(self):
        
        args = self.getUrlArgs('/sceventdo/')
        try:
            scoutkey = urllib.unquote(args.get(1))
            str_flag_skip = self.request.get(Defines.URLQUERY_SKIP)
            if not str_flag_skip in ('1', '0'):
                str_flag_skip = None
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        self.addloginfo('getViewerPlayer')
        v_player = self.getViewerPlayer()
        
        # 演出スキップフラグ.
        self.addloginfo('str_flag_skip:%s' % str_flag_skip)
        if str_flag_skip:
            flag_skip = bool(int(str_flag_skip))
            BackendApi.set_scoutskip_flag(v_player.id, flag_skip)
        else:
            flag_skip = BackendApi.get_scoutskip_flag(v_player.id)
        
        model_mgr = self.getModelMgr()
        
        using = settings.DB_DEFAULT
        
        self.addloginfo('getCurrentScoutEvent')
        eventmaster = self.getCurrentScoutEvent()
        mid = eventmaster.id
        
        # プレイ情報.
        self.addloginfo('get_event_playdata')
        playdata = BackendApi.get_event_playdata(model_mgr, mid, v_player.id, using)
        
        # マスターデータ.
        self.addloginfo('stagemaster')
        stagemaster = BackendApi.get_current_scouteventstage_master(model_mgr, eventmaster, playdata, using)
        
        # イベントを実行したフレンド数.
        self.addloginfo('friend_num')
        friend_num = BackendApi.get_num_event_play_friend(model_mgr, mid, v_player, OSAUtil.get_now())
        
        # 逢引タイム.
        lovetime = playdata and playdata.is_lovetime()
        
        # 実行.
        scout_playdata_id = ScoutEventPlayData.makeID(v_player.id, eventmaster.id)
        try:
            self.addloginfo('write')
            model_mgr = db_util.run_in_transaction(self.tr_write, eventmaster, v_player.id, stagemaster, scoutkey, friend_num, lovetime)
            self.addloginfo('model_mgr.write_end()')
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                model_mgr.delete_models_from_cache(ScoutEventPlayData, [ScoutEventPlayData.makeID(v_player.id, mid)])
            elif err.code == CabaretError.Code.OVER_LIMIT:
                # これ以上実行できない.
                url = UrlMaker.scoutevent()
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
        
        self.addloginfo('write end')
        
        playdata = model_mgr.get_wrote_model(ScoutEventPlayData, scout_playdata_id, ScoutEventPlayData.getByKey, scout_playdata_id)
        
        if flag_skip:
            if playdata.result.get('feverstart'):
                # フィーバー演出
                url = UrlMaker.scouteventfever(stagemaster.id, scoutkey)
            elif playdata.result.get('lovetime_start'):
                # フィーバー演出
                url = UrlMaker.scouteventlovetime(stagemaster.id, scoutkey)
            else:
                url = UrlMaker.scouteventresultanim(stagemaster.id, scoutkey, 0)
        else:
            url = UrlMaker.scouteventanim(stagemaster.id, scoutkey)
        
        if settings_sub.IS_BENCH:
            self.response.end()
        else:
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def tr_write(self, eventmaster, uid, stagemaster, scoutkey, friend_num, lovetime):
        model_mgr = ModelRequestMgr()
        self.addloginfo('get_players')
#        player = BackendApi.get_players(self, [uid], [PlayerAp, PlayerRegist, PlayerExp, PlayerFriend, PlayerDeck], model_mgr=model_mgr)[0]
        player = BackendApi.get_player(self, uid, [PlayerAp, PlayerExp, PlayerFriend], model_mgr=model_mgr)
        BackendApi.tr_do_scoutevent_stage(model_mgr, eventmaster, player, stagemaster, scoutkey, self.is_pc, friend_num, lovetime=lovetime, handler=self)
        model_mgr.write_all()
        self.addloginfo('write_all end')
        return model_mgr

def main(request):
    return Handler.run(request)
