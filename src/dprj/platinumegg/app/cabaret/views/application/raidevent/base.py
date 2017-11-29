# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerExp
from platinumegg.app.cabaret.models.raidevent.RaidCardMixer import RaidEventMaterialData
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventChampagne
import settings_sub


class RaidEventBaseHandler(HappeningHandler):
    """レイドイベントのベースハンドラ.
    """
    
    if settings_sub.IS_DEV:
        CONTENT_NUM_MAX_PER_PAGE = 2
    else:
        CONTENT_NUM_MAX_PER_PAGE = 10
    
    def preprocess(self):
        HappeningHandler.preprocess(self)
        self.__current_event = None
        self.__current_event_flagrecord = None
        self.__current_event_scorerecord = None
        self.__current_ticket_event = None
    
    def processAppError(self, err):
        if err.code == CabaretError.Code.EVENT_CLOSED:
            url = UrlMaker.mypage()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        HappeningHandler.processAppError(self, err)
    
    def getCurrentRaidEvent(self, quiet=False):
        """現在発生中のイベント.
        """
        if self.__current_event is None:
            model_mgr = self.getModelMgr()
            self.__current_event = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
            if self.__current_event is None and not quiet:
                raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        return self.__current_event
    
    def getCurrentRaidTicketEvent(self, quiet=False):
        """現在チケット交換中のイベント.
        """
        if self.__current_ticket_event is None:
            if self.__current_event:
                self.__current_ticket_event = self.__current_event
            else:
                model_mgr = self.getModelMgr()
                self.__current_ticket_event = BackendApi.get_current_ticket_raideventmaster(model_mgr, using=settings.DB_READONLY)
                if self.__current_ticket_event is None and not quiet:
                    raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        return self.__current_ticket_event
    
    def getCurrentRaidFlagRecord(self):
        """現在発生中のイベントのフラグレコードを取得.
        """
        if self.__current_event_flagrecord is None:
            model_mgr = self.getModelMgr()
            v_player = self.getViewerPlayer()
            current_event = self.getCurrentRaidEvent()
            self.__current_event_flagrecord = BackendApi.get_raidevent_flagrecord(model_mgr, current_event.id, v_player.id, using=settings.DB_READONLY)
        return self.__current_event_flagrecord
    
    def getCurrentRaidScoreRecord(self):
        """現在発生中のイベントの得点レコードを取得.
        """
        if self.__current_event_scorerecord is None:
            model_mgr = self.getModelMgr()
            v_player = self.getViewerPlayer()
            current_event = self.getCurrentRaidEvent()
            self.__current_event_scorerecord = BackendApi.get_raidevent_scorerecord(model_mgr, current_event.id, v_player.id, using=settings.DB_READONLY)
        return self.__current_event_scorerecord
    
    def putEventTopic(self, mid, cur_topic='top'):
        """eventbase.htmlのトピック用のパラメータを埋め込む.
        """
        self.html_param['cur_topic'] = cur_topic
        
        # イベントTopのURL.
        url = UrlMaker.raidevent_top(mid)
        self.html_param['url_raidevent_top'] = self.makeAppLinkUrl(url)
        
        # イベント説明のURL.
        url = UrlMaker.raidevent_explain(mid)
        self.html_param['url_raidevent_explain'] = self.makeAppLinkUrl(url)
        
        # ランキングのURL.
        url = UrlMaker.raidevent_ranking(mid)
        self.html_param['url_raidevent_ranking'] = self.makeAppLinkUrl(url)
        
        arr = (
            'detail',
            'prizes',
            'nomination',
            'faq',
        )
        for k in arr:
            self.html_param['url_explain_%s' % k] = self.makeAppLinkUrl(UrlMaker.raidevent_explain(mid, k))
    
    def putEventGachaUrl(self):
        """イベントガチャのリンク.
        """
        url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.TICKET)
        self.html_param['url_gacha_event'] = self.makeAppLinkUrl(url)
    
    def putRanking(self, uid, mid, view_myrank, url_raidevent_ranking, url_raidevent_myrank, view_beginer=False):
        
        model_mgr = self.getModelMgr()
        
        page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
        
        if view_myrank:
            score = BackendApi.get_raidevent_score(mid, uid)
            if score:
                # 自分のランクのページヘ.
                index = BackendApi.get_raidevent_rankindex(mid, uid, is_beginer=view_beginer)
                offset = max(0, index - int((self.CONTENT_NUM_MAX_PER_PAGE+1) / 2))
                uidscoresetlist = BackendApi.fetch_uid_by_raideventrank(mid, self.CONTENT_NUM_MAX_PER_PAGE, offset, withrank=True, is_beginer=view_beginer)
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
        
        contentnum = BackendApi.get_raidevent_rankernum(mid, is_beginer=view_beginer)
        
        self.html_param['is_view_myrank'] = view_myrank
        self.html_param['is_view_beginer'] = view_beginer
        
        self.html_param['url_raidevent_ranking'] = self.makeAppLinkUrl(url_raidevent_ranking) + "#ranking"
        self.html_param['url_raidevent_myrank'] = self.makeAppLinkUrl(url_raidevent_myrank) + "#ranking"
        self.html_param['url_raidevent_ranking_beginer'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_raidevent_ranking, Defines.URLQUERY_BEGINER, 1)) + "#ranking"
        self.html_param['url_raidevent_myrank_beginer'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_raidevent_myrank, Defines.URLQUERY_BEGINER, 1)) + "#ranking"
        
        url_base = OSAUtil.addQuery(url_raidevent_myrank if view_myrank else url_raidevent_ranking, Defines.URLQUERY_BEGINER, int(view_beginer))
        
        if not view_myrank:
            self.putPagenation(url_base, page, contentnum, self.CONTENT_NUM_MAX_PER_PAGE, "ranking")
    
    def getUidScoreSetList(self, eventid, page, is_beginer=False):
        offset = page * self.CONTENT_NUM_MAX_PER_PAGE
        limit = self.CONTENT_NUM_MAX_PER_PAGE
        uidscoresetlist = BackendApi.fetch_uid_by_raideventrank(eventid, limit, offset, withrank=True, is_beginer=is_beginer)
        return uidscoresetlist
    
    def writeHtml(self, eventmaster, name):
        """HTML書き込み.
        """
        if not self.html_param.get('raidevent'):
            # raideventは必ず必要.
            model_mgr = self.getModelMgr()
            config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
            self.html_param['raidevent'] = Objects.raidevent(self, eventmaster, config)
        
        # HTML作成.
        self.writeAppHtml('raidevent/%s' % name)
    
    def getMaterialMasters(self):
        """イベント用の交換素材のマスターデータを取得.
        """
        dest = {}
        
        model_mgr = self.getModelMgr()
        eventmaster = self.getCurrentRaidTicketEvent(quiet=True)
        if not eventmaster:
            return dest
        materials = eventmaster.getMaterialDict()
        
        if not materials:
            return dest
        
        masterlist = BackendApi.get_raidevent_materialmaster_list(model_mgr, materials.values(), using=settings.DB_READONLY)
        masters = dict([(master.id, master) for master in masterlist])
        
        for i, mid in materials.items():
            master = masters.get(mid)
            if master:
                dest[i] = master
        
        return dest
    
    def getChampagneData(self):
        """シャンパン情報を取得.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        eventmaster = self.getCurrentRaidTicketEvent()
        uid = v_player.id
        
        data = None
        if 0 < eventmaster.champagne_num_max:
            data = BackendApi.get_raidevent_champagne(model_mgr, uid, using=settings.DB_READONLY)
        
        if data is None:
            data = RaidEventChampagne.makeInstance(uid)
        
        return data
    
    def putChampagneData(self):
        """シャンパン情報を取得.
        """
        v_player = self.getViewerPlayer()
        # レイドイベント.
        return BackendApi.put_raidevent_champagnedata(self, v_player.id, is_event_page=True)
    
    def getMaterialData(self, using=settings.DB_READONLY):
        """素材の所持情報を取得.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        data = BackendApi.get_raidevent_materialdata(model_mgr, uid, using=using)
        if data is None:
            data = RaidEventMaterialData.makeInstance(uid)
        
        return data
    
    def putMaterialHtml(self):
        """素材情報をHTMLに埋め込む.
        """
        obj_material_dict = {}
        
        material_masters = self.getMaterialMasters()
        if material_masters:
            eventmaster = self.getCurrentRaidTicketEvent()
            eventid = eventmaster.id
            
            materialdata = self.getMaterialData()
            for idx, master in material_masters.items():
                num = materialdata.getMaterialNum(eventid, idx)
                obj_material_dict[idx] = Objects.raidevent_material(self, master, num)
        
        self.html_param['raidevent_materials'] = obj_material_dict
        
        return obj_material_dict
    
    def getRecipeTradeNum(self, include_all=False):
        """交換数を取得.
        """
        str_trade_num = str(self.request.get(Defines.URLQUERY_NUMBER))
        if include_all:
            trade_num = -1
            min_value = 0
        else:
            trade_num = 0
            min_value = 1
        
        if str_trade_num.isdigit():
            trade_num = int(str_trade_num)
        
        if trade_num < min_value:
            url = UrlMaker.raidevent_recipe_list()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
        
        return trade_num
    
    def putRecipeUrl(self):
        """交換所のURLを埋め込む.
        """
        if self.getMaterialMasters():
            url = UrlMaker.raidevent_recipe_list()
            self.html_param['url_raidevent_recipelist'] = self.makeAppLinkUrl(url)
    
    def makeStageObj(self, stagemaster, playdata, cur_stagenumber, bossattack=False):
        """ステージ情報作成.
        """
        v_player = self.getViewerPlayer()
        if playdata.stage > stagemaster.stage:
            progress = stagemaster.execution
        else:
            progress = playdata.progress
        obj_stage = Objects.raidevent_stage(self, v_player, cur_stagenumber, stagemaster, progress, playdata.confirmkey, bossattack=bossattack)
        return obj_stage
    
