# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.battle.base import BattleHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import settings_sub
from platinumegg.app.cabaret.models.Player import PlayerFriend, PlayerExp
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
import datetime
from defines import Defines
from collections import defaultdict
import math


class BattleEventBaseHandler(BattleHandler):
    """バトルイベントのベースハンドラ.
    """
    
    if settings_sub.IS_DEV:
        CONTENT_NUM_MAX_PER_PAGE = 2
    else:
        CONTENT_NUM_MAX_PER_PAGE = 10
    
    def preprocess(self):
        BattleHandler.preprocess(self)
        self.__current_event = None
        self.__current_event_flagrecord = None
        self.__current_event_scorerecord = None
        self.__current_event_rankrecord = None
        self.__current_event_group = None
        # イベントTopのURL.
        url = UrlMaker.battleevent_top()
        self.html_param['url_battleevent_top'] = self.makeAppLinkUrl(url)
    
    def processAppError(self, err):
        if err.code == CabaretError.Code.EVENT_CLOSED:
            url = UrlMaker.mypage()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        BattleHandler.processAppError(self, err)
    
    def getCurrentBattleEvent(self, quiet=False):
        """現在発生中のイベント.
        """
        if self.__current_event is None:
            model_mgr = self.getModelMgr()
            self.__current_event = BackendApi.get_current_battleevent_master(model_mgr, using=settings.DB_READONLY)
            if self.__current_event is None and not quiet:
                raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        return self.__current_event
    
    def isBattleOpen(self):
        """バトル開催中か.
        """
        if settings_sub.IS_LOCAL and self.request.get("_test"):
            return True
        model_mgr = self.getModelMgr()
        return BackendApi.is_battleevent_battle_open(model_mgr, using=settings.DB_READONLY)
    
    def checkBattleEventUser(self, do_check_opening=True, do_check_battle_open=True, do_check_regist=True, do_check_loginbonus=True, do_check_emergency=True):
        """ユーザーチェック.
        """
        model_mgr = self.getModelMgr()
        
        if do_check_opening:
            uid = self.getViewerPlayer().id
            cur_eventmaster = self.getCurrentBattleEvent(quiet=True)
            if cur_eventmaster:
                if BackendApi.check_battleevent_lead_opening(model_mgr, uid, cur_eventmaster.id, using=settings.DB_READONLY):
                    # オープニングを見ていない.
                    url = UrlMaker.battleevent_opening()
                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
                    return False
        
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        is_battleopen = self.isBattleOpen()
        
        if do_check_battle_open and not is_battleopen:
            # バトルが閉じている.
            url = UrlMaker.battleevent_top(config.mid)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return False
        elif do_check_emergency and config.is_emergency:
            # 緊急停止.
            url = UrlMaker.battleevent_top(config.mid)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return False
        else:
            cur_group = self.getCurrentBattleGroup(do_search_log=not is_battleopen)
            if do_check_regist and cur_group is None:
                # イベントに参加していない.
                if is_battleopen:
                    url = UrlMaker.battleevent_regist()
                else:
                    url = UrlMaker.battleevent_top(config.mid)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return False
            elif do_check_loginbonus:
                rankrecord = self.getCurrentBattleRankRecord()
                if rankrecord and rankrecord.isNeedUpdate(config):
                    url = UrlMaker.battleevent_loginbonus()
                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
                    return False
        return True
    
    def checkOpponentId(self, oid, revengeid=None, do_redirect=True, args=None):
        """対戦出来る相手なのかチェック.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        eventid = self.getCurrentBattleEvent().id
        
        oidlist = None
        if revengeid:
            revenge = BackendApi.get_battleevent_revenge(model_mgr, revengeid, using=settings.DB_READONLY)
            if revenge and uid == revenge.uid:
                oidlist = [revenge.oid]
        else:
            eventmaster = self.getCurrentBattleEvent()
            oidlist = BackendApi.get_battleevent_opponentidlist(model_mgr, eventmaster.id, uid, using=settings.DB_READONLY)
            if BackendApi._check_is_rival_strings(oid, eventid, args):
                if oid in oidlist:
                    oidlist.remove(oid)
                    oidlist.insert(0, oid)
                elif oid:
                    oidlist[0] = oid
            oidlist = BackendApi.filter_battleevent_opplist_by_battletime(model_mgr, uid, oidlist, using=settings.DB_READONLY)
        
        if oidlist and oid in oidlist:
            return True
        else:
            if do_redirect:
                target = 'revenge' if revengeid else 'lv'
                url = UrlMaker.battleevent_opplist(target)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return False
    
    def getCurrentBattleFlagRecord(self):
        """現在発生中のイベントのフラグレコードを取得.
        """
        if self.__current_event_flagrecord is None:
            model_mgr = self.getModelMgr()
            v_player = self.getViewerPlayer()
            current_event = self.getCurrentBattleEvent()
            self.__current_event_flagrecord = BackendApi.get_battleevent_flagrecord(model_mgr, current_event.id, v_player.id, using=settings.DB_READONLY)
        return self.__current_event_flagrecord
    
    def getCurrentBattleScoreRecord(self):
        """現在発生中のイベントの得点レコードを取得.
        """
        if self.__current_event_scorerecord is None:
            model_mgr = self.getModelMgr()
            v_player = self.getViewerPlayer()
            current_event = self.getCurrentBattleEvent()
            self.__current_event_scorerecord = BackendApi.get_battleevent_scorerecord(model_mgr, current_event.id, v_player.id, using=settings.DB_READONLY)
        return self.__current_event_scorerecord
    
    def getCurrentBattleRankMaster(self):
        """現在発生中のイベントのランクレコードを取得.
        """
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        eventmaster = self.getCurrentBattleEvent()
        rankrecord = self.getCurrentBattleRankRecord()
        rank = rankrecord.getRank(config)
        return BackendApi.get_battleevent_rankmaster(self.getModelMgr(), eventmaster.id, rank, using=settings.DB_READONLY)
    
    def getCurrentBattleRankRecord(self):
        """現在発生中のイベントのランクレコードを取得.
        """
        if self.__current_event_rankrecord is None:
            model_mgr = self.getModelMgr()
            v_player = self.getViewerPlayer()
            current_event = self.getCurrentBattleEvent()
            self.__current_event_rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, current_event.id, v_player.id, using=settings.DB_READONLY)
        return self.__current_event_rankrecord
    
    def getCurrentBattleGroup(self, do_search_log=False):
        """現在発生中のイベントで参加しているグループを取得.
        """
        if self.__current_event_group is None:
            basetime = DateTimeUtil.toLoginTime(OSAUtil.get_now())
            cdate = datetime.date(basetime.year, basetime.month, basetime.day)
            
            rankrecord = self.getCurrentBattleRankRecord()
            if rankrecord and rankrecord.groups:
                model_mgr = self.getModelMgr()
                groupid = rankrecord.groups[-1]
                group = BackendApi.get_battleevent_group(model_mgr, groupid, using=settings.DB_READONLY)
                if do_search_log and (group is None or group.cdate != cdate):
                    grouplog_dict = BackendApi.get_battleevent_grouplog_dict(model_mgr, rankrecord.groups, using=settings.DB_READONLY)
                    for groupid in rankrecord.groups[::1]:
                        group = grouplog_dict.get(groupid)
                        if group:
                            break
                self.__current_event_group = group
        return self.__current_event_group
    
    def makeRankRecordObj(self, rankrecord, groupid=None, logonly=False, player_num=0, do_execute=True, cdate_max=None):
        """ランク情報.
        """
        if cdate_max is None:
            basetime = DateTimeUtil.toLoginTime(OSAUtil.get_now())
            cdate_max = datetime.date(basetime.year, basetime.month, basetime.day)
        
        if groupid is None:
            groupid = rankrecord.groups[-1]
        
        model_mgr = self.getModelMgr()
        if logonly:
            # 履歴から.
            group = BackendApi.get_battleevent_grouplog(model_mgr, groupid, using=settings.DB_READONLY)
        else:
            group = BackendApi.get_battleevent_group(model_mgr, groupid, using=settings.DB_READONLY)
            if group is None:
                # 履歴から.
                group = BackendApi.get_battleevent_grouplog(model_mgr, groupid, using=settings.DB_READONLY)
        if group is None or cdate_max < group.cdate:
            return None
        
        now = OSAUtil.get_now()
        func_execute_end = BackendApi.make_battleevent_grouprankingdata(self, group, rankrecord.uid, now, do_execute, player_num, using=settings.DB_READONLY)
        
        rankid = group.rankid
        rankmaster = BackendApi.get_battleevent_rankmaster_byId(model_mgr, rankid, using=settings.DB_READONLY)
        
        def execute_end():
            rankingdata = func_execute_end if do_execute else func_execute_end()
            return Objects.battleevent_rank(self, rankrecord, rankmaster, group, rankingdata)
        
        if do_execute:
            return execute_end()
        else:
            return execute_end
    
    def makeScoreRecordObj(self, scorerecord, battleresult=None, rank_beginer=None):
        """ランク情報.
        """
        rank = None
        if scorerecord:
            rank = BackendApi.get_battleevent_rank(scorerecord.mid, scorerecord.uid)
        return Objects.battleevent_score(self, scorerecord, rank, battleresult, rank_beginer=rank_beginer)
    
    def getObjPlayerList(self, playerlist):
        obj_list = []
        if playerlist:
            model_mgr = self.getModelMgr()
            
            persons = BackendApi.get_dmmplayers(self, playerlist, using=settings.DB_READONLY, do_execute=False)
            
            self.execute_api()
            
            for player in playerlist:
                
                deck = BackendApi.get_deck(player.id, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
                cardsetlist = BackendApi.get_cards(deck.to_array(), arg_model_mgr=model_mgr, using=settings.DB_READONLY)
                leader = cardsetlist[0]
                
                obj_player = Objects.player(self, player, persons.get(player.dmmid), leader)
                power_total = leader.power
                
                deckmember = []
                for cardset in cardsetlist[1:]:
                    obj_card = Objects.card(self, cardset)
                    power_total += obj_card['power']
                    deckmember.append(obj_card)
                obj_player['deckmember'] = deckmember
                obj_player['power_total'] = power_total
                obj_list.append(obj_player)
        return obj_list
    
    def getObjPlayerListByID(self, playeridlist):
        if not playeridlist:
            return []
        else:
            playerlist = BackendApi.get_players(self, playeridlist, [PlayerFriend, PlayerExp], using=settings.DB_READONLY)
            return self.getObjPlayerList(playerlist)
    
    def putEventTopic(self, mid, cur_topic='top'):
        """eventbase.htmlのトピック用のパラメータを埋め込む.
        """
        self.html_param['cur_topic'] = cur_topic
        
        # イベントTopのURL.
        url = UrlMaker.battleevent_top(mid)
        self.html_param['url_battleevent_top'] = self.makeAppLinkUrl(url)
        
        # イベント説明のURL.
        url = UrlMaker.battleevent_explain(mid)
        self.html_param['url_battleevent_explain'] = self.makeAppLinkUrl(url)
        
        # ランキングのURL.
        url = UrlMaker.battleevent_ranking(mid)
        self.html_param['url_battleevent_ranking'] = self.makeAppLinkUrl(url)
        
        table = (
            'detail',
            'prizes',
            'nomination',
            'faq',
        )
        for k in table:
            self.html_param['url_explain_%s' % k] = self.makeAppLinkUrl(UrlMaker.battleevent_explain(mid, k))
        
        # 贈り物.
        if BackendApi.get_battleeventpresent_master_by_eventdid(self.getModelMgr(), mid, using=settings.DB_READONLY):
            self.html_param['url_battleevent_present'] = self.makeAppLinkUrl(UrlMaker.battleevent_present())
        
        # ガチャページ.
        url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_GTYPE, Defines.GachaConsumeType.GTYPE_NAMES[Defines.GachaConsumeType.OMAKE])
        self.html_param['url_battleevent_gacha'] = self.makeAppLinkUrl(url)
    
    def putRanking(self, uid, eventid, view_myrank, url_battleevent_ranking, url_battleevent_myrank, view_beginer=False):
        
        model_mgr = self.getModelMgr()
        
        page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
        
        if view_myrank:
            score = BackendApi.get_battleevent_score(eventid, uid)
            if score:
                # 自分のランクのページヘ.
                index = BackendApi.get_battleevent_rankindex(eventid, uid, is_beginer=view_beginer)
                offset = max(0, index - int((self.CONTENT_NUM_MAX_PER_PAGE+1) / 2))
                uidscoresetlist = BackendApi.fetch_uid_by_battleeventrank(eventid, self.CONTENT_NUM_MAX_PER_PAGE, offset, withrank=True, is_beginer=view_beginer)
            else:
                uidscoresetlist = []
        else:
            uidscoresetlist = self.getUidScoreSetList(eventid, page, is_beginer=view_beginer)
        
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
                obj_player['is_me'] = uid == player.id
                obj_playerlist.append(obj_player)
            obj_playerlist.sort(key=lambda x:x['event_score'], reverse=True)
        self.html_param['ranking_playerlist'] = obj_playerlist
        
        contentnum = BackendApi.get_battleevent_rankernum(eventid, is_beginer=view_beginer)
        
        self.html_param['is_view_myrank'] = view_myrank
        self.html_param['is_view_beginer'] = view_beginer
        
        self.html_param['url_battleevent_ranking'] = self.makeAppLinkUrl(url_battleevent_ranking) + "#ranking"
        self.html_param['url_battleevent_myrank'] = self.makeAppLinkUrl(url_battleevent_myrank) + "#ranking"
        self.html_param['url_battleevent_ranking_beginer'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_battleevent_ranking, Defines.URLQUERY_BEGINER, 1)) + "#ranking"
        self.html_param['url_battleevent_myrank_beginer'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_battleevent_myrank, Defines.URLQUERY_BEGINER, 1)) + "#ranking"
        
        url_base = OSAUtil.addQuery(url_battleevent_myrank if view_myrank else url_battleevent_ranking, Defines.URLQUERY_BEGINER, int(view_beginer))
        
        if not view_myrank:
            self.putPagenation(url_base, page, contentnum, self.CONTENT_NUM_MAX_PER_PAGE, "ranking")
    
    def getUidScoreSetList(self, eventid, page, is_beginer=False):
        offset = page * self.CONTENT_NUM_MAX_PER_PAGE
        limit = self.CONTENT_NUM_MAX_PER_PAGE
        uidscoresetlist = BackendApi.fetch_uid_by_battleeventrank(eventid, limit, offset, withrank=True, is_beginer=is_beginer)
        return uidscoresetlist

    def get_base_battle_ticket_num(self, data):
        if data['is_win']:
            return Defines.BATTLE_TICKET_WIN
        else:
            return Defines.BATTLE_TICKET_LOSE

    def get_player_battle_ticket_bonus(self, model_mgr, uid, ticket_num, eventmaster):
        # get player deck
        playerdeck = BackendApi.get_deck(uid, model_mgr, using=settings.DB_READONLY).to_array()
        # get player cards
        cards = BackendApi.get_cards(playerdeck)

        cardid_dict = defaultdict(int)  # default value for int is 0
        # the better the ハメ管理 value (hklevel colum on the database table) the higher the card id
        for card in cards:
            album = card.master.album
            if cardid_dict[album] < card.master.id:
                cardid_dict[album] = card.master.id

        rate_dict = {rate[0]: rate[1] for rate in eventmaster.battleticket_rate}

        percentages = [(rate_dict.get(x) / 100.0) for x in cardid_dict.values() if rate_dict.get(x)]

        bonus = ticket_num * sum(percentages)
        return int(math.ceil(bonus))
