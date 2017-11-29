# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.models.Player import PlayerRequest, PlayerExp
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines


class Handler(RaidEventBaseHandler):
    """レイドイベントTOP.
    イベント開催期間.
    説明とランキングのリンク.
    タイムボーナス情報.
    発生中のレイド情報.
    報酬受取り判定.
    救援(1件だけ).
    履歴(1件だけ).
    イベント秘宝所持数.
    討伐回数.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRequest, PlayerExp]
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        
        args = self.getUrlArgs('/raideventtop/')
        mid = str(args.get(0))
        eventmaster = None
        
        if mid and mid.isdigit():
            mid = int(mid)
        elif config:
            mid = config.mid
        
        if mid:
            eventmaster = BackendApi.get_raideventmaster(model_mgr, mid, using=settings.DB_READONLY)
        
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
            return
        
        cur_eventmaster = self.getCurrentRaidEvent(quiet=True)
        
        mid = eventmaster.id
        
        # 開催中判定.
        is_open = cur_eventmaster and cur_eventmaster.id == mid
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        scorerecord = BackendApi.get_raidevent_scorerecord(model_mgr, mid, uid, using=settings.DB_READONLY)
        flagrecord = BackendApi.get_raidevent_flagrecord(model_mgr, mid, uid, using=settings.DB_READONLY)
        
        # イベント情報.
        self.html_param['raidevent'] = Objects.raidevent(self, eventmaster, config)
        
        # 説明とランキングのリンク.
        self.putEventTopic(mid, 'top')
        
        if is_open:
            # 救援(1件だけ).
            func_raidhelp = self.putRaidHelpList(do_execute=False, limit=1)
            self.html_param['url_raidhelp_list'] = self.makeAppLinkUrl(UrlMaker.raidevent_helplist())
            
            # 履歴(1件だけ).
            raidlogidlist = BackendApi.get_raidlog_idlist(model_mgr, v_player.id, 0, 1, using=settings.DB_READONLY)
            raidloglist = BackendApi.get_raidlogs(model_mgr, raidlogidlist, using=settings.DB_READONLY).values()
            func_raidlog = BackendApi.put_list_raidlog_obj(self, raidloglist)
            self.html_param['url_raidloglist'] = self.makeAppLinkUrl(UrlMaker.raidloglist())
            
            # 発生中のレイド情報.
            happeningraidset = self.getHappeningRaidSet()
            happeningset = None
            if happeningraidset:
                happeningset = happeningraidset.happening
            if happeningset:
                # レイドがある.
                if (happeningset.happening.is_cleared() or happeningset.happening.is_missed_and_not_end()):
                    # 未確認の結果がある.
                    url = UrlMaker.raidresultanim(happeningset.id)
                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
                    return
                elif not happeningset.happening.is_end():
                    obj_happening = Objects.happening(self, happeningraidset)
                    obj_happening['url_battlepre'] = self.makeAppLinkUrl(UrlMaker.raidevent_battlepre())
                    self.html_param['happening'] = obj_happening
            
            # デッキ編成へのリンクを上書き.
            self.setFromPage(Defines.FromPages.RAIDEVENT)
            self.html_param['url_deck_raid'] = self.makeAppLinkUrl(UrlMaker.deck_raid())
        elif BackendApi.check_raidevent_lead_epilogue(model_mgr, uid, mid, using=settings.DB_READONLY):
            # EDを見ないといけない.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.raidevent_epilogue()))
            return
        
        # 報酬受取り判定.
        flag = False
        if scorerecord:
            if flagrecord is None:
                flagrecord = BackendApi.update_raideventflagrecord(model_mgr, eventmaster.id, uid, OSAUtil.get_datetime_max())
            if scorerecord.destroy and BackendApi.choice_raidevent_notfixed_destroy_prizeids(eventmaster, scorerecord.destroy, flagrecord, False):
                flag = True
            elif scorerecord.destroy_big and BackendApi.choice_raidevent_notfixed_destroy_prizeids(eventmaster, scorerecord.destroy_big, flagrecord, True):
                flag = True
        if flag:
            self.html_param['url_raidevent_prizereceive'] = self.makeAppLinkUrl(UrlMaker.raidevent_prizereceive_do(mid, v_player.req_confirmkey))
        
        # イベント秘宝所持数.
        # 討伐回数.
        rank = BackendApi.get_raidevent_rank(mid, uid)
        rank_beginer = BackendApi.get_raidevent_rank(mid, uid, is_beginer=True)
        self.html_param['raideventscore'] = Objects.raidevent_score(eventmaster, scorerecord, rank, rank_beginer)
        
        # イベントガチャのリンク.
        self.putEventGachaUrl()
        
        # 初心者フラグ.
        is_beginer = BackendApi.check_raidevent_beginer(model_mgr, uid, eventmaster, config, using=settings.DB_READONLY)
        self.html_param['is_beginer'] = is_beginer
        
        # ランキング.
        view_myrank = False
        view_beginer = self.request.get(Defines.URLQUERY_BEGINER) == "1"
        if not view_beginer or is_beginer:
            view_myrank = self.request.get(Defines.URLQUERY_FLAG) == "1"
        url_ranking = OSAUtil.addQuery(UrlMaker.raidevent_top(mid), Defines.URLQUERY_FLAG, "0")
        url_myrank = OSAUtil.addQuery(UrlMaker.raidevent_top(mid), Defines.URLQUERY_FLAG, "1")
        self.putRanking(uid, mid, view_myrank, url_ranking, url_myrank, view_beginer)
        
        # シャンパン.
        self.putChampagneData()
        
        # 素材.
        self.putMaterialHtml()
        
        # 交換所のURL.
        self.putRecipeUrl()
        
        if eventmaster.flag_dedicated_stage:
            # イベント専用ステージ情報.
            eventstageplaydata = BackendApi.get_raideventstage_playdata(model_mgr, mid, uid, using=settings.DB_READONLY)
            # 現在のステージ.
            cur_stagemaster = BackendApi.get_current_raideventstage_master(model_mgr, eventmaster, eventstageplaydata, using=settings.DB_READONLY)
            if cur_stagemaster is None:
                raise CabaretError(u'ステージが存在いません', CabaretError.Code.INVALID_MASTERDATA)
            
            # 現在のステージ情報.
            progress = eventstageplaydata.progress
            confirmkey = eventstageplaydata.confirmkey
            self.html_param['raideventstage'] = Objects.raidevent_stage(self, v_player, cur_stagemaster.stage, cur_stagemaster, progress, confirmkey)
            
            # イベント専用スカウトのTOPページへのリンク.
            self.html_param['url_raidevent_scouttop'] = self.makeAppLinkUrl(UrlMaker.raidevent_scouttop())
        
        self.execute_api()
        if is_open:
            if func_raidhelp:
                func_raidhelp()
            func_raidlog()
            
            # イベント参加のKPIを保存.
            BackendApi.save_kpi_raidevent_join(uid, self.is_pc)
        
        self.writeHtml(eventmaster, 'top')
    

def main(request):
    return Handler.run(request)
