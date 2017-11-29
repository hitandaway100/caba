# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerExp
from platinumegg.lib.opensocial.util import OSAUtil
import settings_sub


class ScoutHandler(AppHandler):
    """スカウトのハンドラ.
    """
    
    if settings_sub.IS_DEV:
        CONTENT_NUM_MAX_PER_PAGE = 2
    else:
        CONTENT_NUM_MAX_PER_PAGE = 10
    
    def preprocess(self):
        AppHandler.preprocess(self)
        self.html_param['url_scoutevent_top'] = self.makeAppLinkUrl(UrlMaker.scoutevent_top())
        self.html_param['url_scoutevent_scouttop'] = self.makeAppLinkUrl(UrlMaker.scoutevent())
        self.html_param['url_sp_gacha'] = self.makeAppLinkUrl('/gacha?_gtype=stepup')
    
    def processAppError(self, err):
        if err.code == CabaretError.Code.EVENT_CLOSED:
            url = UrlMaker.mypage()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        AppHandler.processAppError(self, err)
    
    def writeScoutEventHTML(self, htmlname, eventmaster):
        prefix = 'produceevent' if eventmaster.is_produce else 'scoutevent'
        self.writeAppHtml('%s/%s' % (prefix, htmlname))
    
    def getCurrentScoutEvent(self, quiet=False, do_check_schedule=True):
        """現在開催中のスカウトイベント.
        """
        model_mgr = self.getModelMgr()
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY, check_schedule=do_check_schedule)
        if not quiet and eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        return eventmaster
    
    def getScoutEventFlagRecord(self, eventid=None):
        """スカウトイベントのフラグ関係のレコード.
        """
        if eventid is None:
            cur_event = self.getCurrentScoutEvent()
            if cur_event is None:
                return None
            eventid = cur_event.id
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        return BackendApi.get_scoutevent_flagrecord(model_mgr, eventid, v_player.id, using=settings.DB_READONLY)
    
    def makeStageObj(self, stagemaster, playdata, stageid, bossattack=False):
        """ステージ情報作成.
        """
        v_player = self.getViewerPlayer()
        if playdata.stage > stagemaster.stage:
            progress = stagemaster.execution
        else:
            progress = playdata.progress
        obj_stage = Objects.scoutevent(self, v_player, stageid, stagemaster, progress, playdata.confirmkey, bossattack)
        return obj_stage

    def putEventTopic(self, mid, cur_topic='top'):
        """eventbase.htmlのトピック用のパラメータを埋め込む.
        """
        self.html_param['cur_topic'] = cur_topic
        
        # スカウトマップのURL.
        url = UrlMaker.scouteventareamap()
        self.html_param['url_areamap'] = self.makeAppLinkUrl(url)
        
        # イベントTopのURL.
        url = UrlMaker.scoutevent_top(mid)
        self.html_param['url_scoutevent_top'] = self.makeAppLinkUrl(url)
        
        # イベント説明のURL.
        url = UrlMaker.scoutevent_explain(mid)
        self.html_param['url_scoutevent_explain'] = self.makeAppLinkUrl(url)
        
        # ランキングのURL.
        url = UrlMaker.scoutevent_ranking(mid)
        self.html_param['url_scoutevent_ranking'] = self.makeAppLinkUrl(url)
        
        # イベント動画ページのURL.
        eventmaster = BackendApi.get_scouteventmaster(self.getModelMgr(), mid, using=settings.DB_READONLY)
        if eventmaster and eventmaster.is_produce:
            eventstagemasterlist = BackendApi.get_event_stage_by_stagenumber(self.getModelMgr(), mid, using=settings.DB_READONLY)
            if eventstagemasterlist:
                url = UrlMaker.scoutevent_movie()
                self.html_param['url_eventmovie_top'] = self.makeAppLinkUrl(url)
        
        # イベント動画ページのURL.
        url = UrlMaker.scouteventproduce()
        self.html_param['url_scoutevent_produce'] = self.makeAppLinkUrl(url)
        
        arr = (
            'detail',
            'prizes',
            'nomination',
            'faq',
        )
        for k in arr:
            self.html_param['url_explain_%s' % k] = self.makeAppLinkUrl(UrlMaker.scoutevent_explain(mid, k))
        
        url = UrlMaker.scouteventcastnomination()
        self.html_param['url_scoutevent_castnomination'] = self.makeAppLinkUrl(url)
        
        url = UrlMaker.scouteventtiptrade()
        self.html_param['url_scoutevent_tiptrade'] = self.makeAppLinkUrl(url)
    
    def putEventPoint(self, mid, uid, playdata):
        """獲得イベントポイントの埋め込み.
        """
        model_mgr = self.getModelMgr()
        points = playdata.result.get('point') or (0, 0, 0)

        if len(points) == 2:
            point, pointeffect = points
            successpoint = 0
        elif len(points) == 3:
            point, pointeffect, successpoint = points

        self.osa_util.logger.trace('%s,%s' % (point, pointeffect))
        scorerecord = BackendApi.get_scoutevent_scorerecord(model_mgr, mid, uid, using=settings.DB_READONLY)
        self.html_param['eventscore'] = Objects.scoutevent_score(scorerecord, point, pointeffect, successpoint)
    
    def putRanking(self, uid, mid, view_myrank, url_scoutevent_ranking, url_scoutevent_myrank, view_beginer=False):
        
        model_mgr = self.getModelMgr()
        
        page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
        
        if view_myrank:
            score = BackendApi.get_scoutevent_score(mid, uid)
            if score:
                # 自分のランクのページヘ.
                index = BackendApi.get_scoutevent_rankindex(mid, uid, is_beginer=view_beginer)
                offset = max(0, index - int((self.CONTENT_NUM_MAX_PER_PAGE+1) / 2))
                uidscoresetlist = BackendApi.fetch_uid_by_scouteventrank(mid, self.CONTENT_NUM_MAX_PER_PAGE, offset, withrank=True, is_beginer=view_beginer)
            else:
                uidscoresetlist = []
        else:
            uidscoresetlist = self.getUidScoreSetList(mid, page, is_beginer=view_beginer)
        
        obj_playerlist = []
        
        if uidscoresetlist:
            uidscoreset = dict(uidscoresetlist)
            
            playerlist = BackendApi.get_players(self, uidscoreset.keys(), [PlayerExp], using=settings.DB_READONLY)
            persons = BackendApi.get_dmmplayers(self, playerlist, using=settings.DB_READONLY, do_execute=False)
            
            leaders = BackendApi.get_leaders(uidscoreset.keys(), arg_model_mgr=model_mgr, using=settings.DB_READONLY)
            
            self.execute_api()
            
            for player in playerlist:
                obj_player = Objects.player(self, player, persons.get(player.dmmid), leaders.get(player.id))
                score, rank = uidscoreset[player.id]
                obj_player['event_score'] = score
                obj_player['event_rank'] = rank
                obj_playerlist.append(obj_player)
            obj_playerlist.sort(key=lambda x:x['event_score'], reverse=True)
        self.html_param['ranking_playerlist'] = obj_playerlist
        
        contentnum = BackendApi.get_scoutevent_rankernum(mid, is_beginer=view_beginer)
        
        self.html_param['is_view_myrank'] = view_myrank
        self.html_param['is_view_beginer'] = view_beginer
        
        self.html_param['url_scoutevent_ranking'] = self.makeAppLinkUrl(url_scoutevent_ranking) + "#ranking"
        self.html_param['url_scoutevent_myrank'] = self.makeAppLinkUrl(url_scoutevent_myrank) + "#ranking"
        self.html_param['url_scoutevent_ranking_beginer'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_scoutevent_ranking, Defines.URLQUERY_BEGINER, 1)) + "#ranking"
        self.html_param['url_scoutevent_myrank_beginer'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_scoutevent_myrank, Defines.URLQUERY_BEGINER, 1)) + "#ranking"
        
        url_base = OSAUtil.addQuery(url_scoutevent_myrank if view_myrank else url_scoutevent_ranking, Defines.URLQUERY_BEGINER, int(view_beginer))
        
        if not view_myrank:
            self.putPagenation(url_base, page, contentnum, self.CONTENT_NUM_MAX_PER_PAGE, "ranking")
    
    def getUidScoreSetList(self, eventid, page, is_beginer=False):
        offset = page * self.CONTENT_NUM_MAX_PER_PAGE
        limit = self.CONTENT_NUM_MAX_PER_PAGE
        uidscoresetlist = BackendApi.fetch_uid_by_scouteventrank(eventid, limit, offset, withrank=True, is_beginer=is_beginer)
        return uidscoresetlist
    
    def putGachaData(self):
        """スカウトイベント専用ガチャ情報を埋め込む.
        """
        model_mgr = self.getModelMgr()
        
        eventmaster = BackendApi.get_current_present_scouteventmaster(model_mgr, using=settings.DB_READONLY)
        if eventmaster is None:
            return
        
        gachamasterlist = BackendApi.get_playablegacha_list_by_consumetype(model_mgr, Defines.GachaConsumeType.SCOUTEVENT, using=settings.DB_READONLY, now=OSAUtil.get_now())
        
        # ガチャ情報埋め込み.
        BackendApi.put_gachahtmldata(self, gachamasterlist, topic=Defines.GachaConsumeType.GachaTopTopic.SCOUTEVENT, do_put_rare_log=False)

