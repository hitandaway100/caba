# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.models.Player import PlayerRequest, PlayerExp,\
    PlayerDeck
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(ScoutHandler):
    """スカウトイベントTOP.
    イベント開催期間.
    説明とランキングのリンク.
    フィーバー情報.
    イベントポイント所持数.
    現在のステージ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRequest, PlayerExp, PlayerDeck]
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
        
        args = self.getUrlArgs('/sceventtop/')
        mid = str(args.get(0))
        eventmaster = None
        
        if mid and mid.isdigit():
            mid = int(mid)
        elif config:
            mid = config.mid
        
        if mid:
            eventmaster = BackendApi.get_scouteventmaster(model_mgr, mid, using=settings.DB_READONLY)
        
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
            return
        
        mid = eventmaster.id
        
        # 開催中判定.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        if BackendApi.check_scoutevent_lead_opening(model_mgr, uid, mid, using=settings.DB_READONLY):
            # OPを見ていない.
            url = UrlMaker.scoutevent_opening()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        elif BackendApi.check_scoutevent_lead_epilogue(model_mgr, uid, mid, using=settings.DB_READONLY):
            # イベントEDを見ないといけない.
            url = UrlMaker.scoutevent_epilogue()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        eventplaydata = BackendApi.get_event_playdata(model_mgr, mid, uid, using=settings.DB_READONLY)
        scorerecord = BackendApi.get_scoutevent_scorerecord(model_mgr, mid, uid, using=settings.DB_READONLY)
        
        # 現在のステージ.
        stagemaster = BackendApi.get_current_scouteventstage_master(model_mgr, eventmaster, eventplaydata, using=settings.DB_READONLY)
        
        # 全エリア.
        areaidlist = BackendApi.get_event_areaidlist(model_mgr, mid, using=settings.DB_READONLY)
        areanum_total = len(areaidlist)
        areanum_cleared = areaidlist.index(stagemaster.area) if stagemaster.area in areaidlist else 0
        if stagemaster.stage < eventplaydata.stage:
            # 次のステージがなくてクリア済みのステージをプレイしているから今いるエリアはクリア扱いでいいはず.
            areanum_cleared += 1
        
        # 自分の順位.
        rank = BackendApi.get_scoutevent_rank(mid, uid)
        rank_beginer = BackendApi.get_scoutevent_rank(mid, uid, is_beginer=True)
        
        # イベント情報.
        obj_scouteventmaster = Objects.scouteventmaster(self, eventmaster, config)
        self.html_param['scoutevent'] = obj_scouteventmaster
        is_opened = obj_scouteventmaster['is_opened']
        
        # ステージ情報.
        progress = eventplaydata.progress
        confirmkey = eventplaydata.confirmkey
        self.html_param['scouteventstage'] = Objects.scoutevent(self, v_player, stagemaster.stage, stagemaster, progress, confirmkey)
        
        # フィーバー.
        self.html_param['scouteventfever'] = Objects.scoutevent_fever(eventplaydata)
        
        # スコア.
        self.html_param['scouteventscore'] = Objects.scoutevent_score(scorerecord)
        
        # イベントデータ.
        self.html_param['scouteventdata'] = Objects.scoutevent_data(scorerecord, areanum_cleared, areanum_total, rank, rank_beginer=rank_beginer)
        
        # 説明とランキングのリンク.
        self.putEventTopic(mid, 'top')
        
        # 初心者フラグ.
        is_beginer = BackendApi.check_scoutevent_beginer(model_mgr, uid, eventmaster, config, using=settings.DB_READONLY)
        self.html_param['is_beginer'] = is_beginer
        
        # ランキング.
        view_myrank = False
        view_beginer = self.request.get(Defines.URLQUERY_BEGINER) == "1"
        if not view_beginer or is_beginer:
            view_myrank = self.request.get(Defines.URLQUERY_FLAG) == "1"
        url_ranking = OSAUtil.addQuery(UrlMaker.scoutevent_top(mid), Defines.URLQUERY_FLAG, "0")
        url_myrank = OSAUtil.addQuery(UrlMaker.scoutevent_top(mid), Defines.URLQUERY_FLAG, "1")
        self.putRanking(uid, mid, view_myrank, url_ranking, url_myrank, view_beginer=view_beginer)
        
        # 短冊情報.
        BackendApi.put_scoutevent_tanzakudata(self, uid, check_schedule=False)
        
        if is_opened:
            # イベント参加KPIを保存.
            BackendApi.save_kpi_scoutevent_join(uid, self.is_pc)
        
        # ガチャ.
        self.putGachaData()
        
        self.writeScoutEventHTML('top', eventmaster)
    

def main(request):
    return Handler.run(request)
