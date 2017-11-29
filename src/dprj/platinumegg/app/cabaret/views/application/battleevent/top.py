# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import settings
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
import calendar


class Handler(BattleEventBaseHandler):
    """バトルイベントTOP.
    3パターンある.
    ・イベント開催中でバトル受付中.
    ・イベント開催中でバトルクローズ中.
    ・イベント終了済み.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def addExecuteApiWork(self, func, *args, **kwargs):
        self.__execute_end_worklist.append((func, args, kwargs))
    
    def executeApiWithWork(self):
        self.execute_api()
        for func, args, kwargs in self.__execute_end_worklist:
            func(*args, **kwargs)
        self.__execute_end_worklist = []
    
    def process(self):
        
        self.__execute_end_worklist = []
        
        model_mgr = self.getModelMgr()
        
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        
        args = self.getUrlArgs('/battleeventtop/')
        eventid = str(args.get(0))
        eventmaster = None
        
        if eventid and eventid.isdigit():
            eventid = int(eventid)
        elif config:
            eventid = config.mid
        
        if eventid:
            eventmaster = BackendApi.get_battleevent_master(model_mgr, eventid, using=settings.DB_READONLY)
        
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
            return
        
        self.__eventmaster = eventmaster
        eventid = eventmaster.id
        cur_eventmaster = self.getCurrentBattleEvent(quiet=True)
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        is_open = cur_eventmaster and eventid == cur_eventmaster.id
        
        self.setFromPage(Defines.FromPages.BATTLEEVENT, eventid)
        
        if is_open:
            # 開催中.
            if self.isBattleOpen():
                # バトルが開いている時.
                self.procOpened()
            else:
                # バトルが閉じている時.
                self.procBattleClosed()
            # イベント参加KPI保存.
            BackendApi.save_kpi_battleevent_join(uid, self.is_pc)
        else:
            self.procClosed()
        
        if self.response.isEnd:
            return
        
        self.html_param['player'] = Objects.player(self, v_player)
        
        # イベント情報.
        battleevent = Objects.battleevent(self, eventmaster)
        self.html_param['battleevent'] = battleevent

        # バトルチケットの使用期限
        if is_open:
            self.html_param['battle_ticket_expiry_date'] = self.get_battle_ticket_expiry_date(config.ticket_endtime)
        
        BackendApi.check_battleevent_piececollection_userdata_and_create(model_mgr, uid, eventid)
        self.html_param['allrarity_piece'] = self.create_piece_image_paths(uid, eventid)
        
        # トピック.
        self.putEventTopic(eventid)
        
        # バトル履歴.
        if not eventmaster.is_goukon:
            loglist = BackendApi.get_battleevent_battlelog_list(model_mgr, uid, limit=1, using=settings.DB_READONLY)
            if loglist:
                func_battleloginfo = BackendApi.make_battleevent_battleloginfo(self, loglist, do_execute=False)
                if func_battleloginfo:
                    def put_battleloginfo():
                        self.html_param['battleloglist'] = func_battleloginfo()
                    self.addExecuteApiWork(put_battleloginfo)
        
        # バトル履歴のリンク.
        self.html_param['url_battleevent_battlelog'] = self.makeAppLinkUrl(UrlMaker.battleevent_loglist())
        tradeshop_urlparam = OSAUtil.addQuery(UrlMaker.trade(), Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.TICKET)
        self.html_param['url_battleticket_trade'] = self.makeAppLinkUrl(tradeshop_urlparam)
        battleticket = BackendApi.get_additional_gachaticket_nums(model_mgr, v_player.id, [Defines.GachaConsumeType.GachaTicketType.BATTLE_TICKET], using=settings.DB_READONLY)
        if battleticket:
            battle_ticket_num = battleticket[Defines.GachaConsumeType.GachaTicketType.BATTLE_TICKET].num
        else:
            battle_ticket_num = 0
        self.html_param['battleticket'] = {
            'name': Defines.GachaConsumeType.NAMES[Defines.GachaConsumeType.BATTLE_TICKET],
            'num': battle_ticket_num,
            'unit': Defines.ItemType.UNIT[Defines.ItemType.ADDITIONAL_GACHATICKET],
        }

        # グループ履歴のリンク.
        self.html_param['url_battleevent_grouplog'] = self.makeAppLinkUrl(UrlMaker.battleevent_grouploglist(eventid))
        
        if not self.html_param.has_key('battleevent_rank'):
            # ランク情報がないのでデフォルトのを設定.
            if config.isFirstDay():
                rankmaster = BackendApi.get_battleevent_rankmaster(model_mgr, eventid, eventmaster.rankstart, using=settings.DB_READONLY)
            else:
                rankmaster = BackendApi.get_battleevent_rankmaster(model_mgr, eventid, eventmaster.rankbeginer, using=settings.DB_READONLY)
            self.html_param['battleevent_rank'] = Objects.battleevent_rank(self, None, rankmaster, None)
        
        self.executeApiWithWork()
        
        # 初心者フラグ.
        is_beginer = BackendApi.check_battleevent_beginer(model_mgr, uid, eventmaster, config, using=settings.DB_READONLY)
        self.html_param['is_beginer'] = is_beginer

        # ユーザーデータのチェック, カウントの取得
        user_cvictory_count = self.check_user_continue_victory_data(uid, eventid)
        self.put_user_continue_victory_data(user_cvictory_count)
        
        # ランキング.
        view_myrank = False
        view_beginer = self.request.get(Defines.URLQUERY_BEGINER) == "1"
        if not view_beginer or is_beginer:
            view_myrank = self.request.get(Defines.URLQUERY_FLAG) == "1"
        url_ranking = OSAUtil.addQuery(UrlMaker.battleevent_top(eventid), Defines.URLQUERY_FLAG, "0")
        url_myrank = OSAUtil.addQuery(UrlMaker.battleevent_top(eventid), Defines.URLQUERY_FLAG, "1")
        self.putRanking(uid, eventid, view_myrank, url_ranking, url_myrank, view_beginer=view_beginer)
        
        if eventmaster.is_goukon:
            self.writeAppHtml('gcevent/top')
        else:
            self.writeAppHtml('btevent/top')
    
    def procOpened(self):
        """開催中.
        """
        # ユーザの状態チェック.
        if not self.checkBattleEventUser(do_check_battle_open=False, do_check_emergency=False):
            return
        
        model_mgr = self.getModelMgr()
        eventid = self.__eventmaster.id
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        if BackendApi.check_battleevent_lead_scenario(model_mgr, uid, eventid, using=settings.DB_READONLY):
            # 中押し演出を見ていない.
            url = UrlMaker.battleevent_scenario()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return False
        
        # ランク情報.
        rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
        func_rankinfo = self.makeRankRecordObj(rankrecord, player_num=2, do_execute=False)
        
        # スコア情報.
        scorerecord = BackendApi.get_battleevent_scorerecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
        rank_beginer = BackendApi.get_battleevent_rank(eventid, uid, is_beginer=True)
        obj_scorerecord = self.makeScoreRecordObj(scorerecord, rank_beginer=rank_beginer)
        self.html_param['battleevent_score'] = obj_scorerecord
        
        if func_rankinfo:
            def put_rankinfo():
                obj_rankinfo = func_rankinfo()
                self.html_param['battleevent_rank'] = obj_rankinfo
                
                # グループ内ランキング報酬.
                prizeinfo = None
                if 0 < obj_scorerecord['point']:
                    grouprank = obj_rankinfo['grouprankingdata']['rank']
                    
                    rankmaster = BackendApi.get_battleevent_rankmaster(model_mgr, eventid, obj_rankinfo['rank'], using=settings.DB_READONLY)
                    if rankmaster:
                        prizeidlist = []
                        for data in rankmaster.group_rankingprizes:
                            if not data.get('prize') or not (data['rank_min'] <= grouprank <= data['rank_max']):
                                continue
                            prizeidlist.extend(data.get('prize'))
                        prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY)
                        prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
                self.html_param['prize'] = prizeinfo
            
            self.addExecuteApiWork(put_rankinfo)
        
        # グループの詳細へ.
        self.html_param['url_battleevent_group'] = self.makeAppLinkUrl(UrlMaker.battleevent_group())
        
        url = UrlMaker.battleevent_explain(eventid, 'prizes')
        self.html_param['url_prizes_group_ranking'] = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_CTYPE, 'group_ranking'))
        
        # バトルTOPへ.
        self.html_param['url_battleevent_opplist'] = self.makeAppLinkUrl(UrlMaker.battleevent_opplist())
    
    def procBattleClosed(self):
        """バトル終了.
        """
        # ユーザの状態チェック.
        if not self.checkBattleEventUser(do_check_battle_open=False, do_check_regist=False, do_check_emergency=False):
            return
        
        model_mgr = self.getModelMgr()
        eventid = self.__eventmaster.id
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # ランク情報.
        rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
        if rankrecord and rankrecord.groups:
            groupnum = len(rankrecord.groups)
            for i in xrange(groupnum):
                index = groupnum - (i + 1)
                func_rankinfo = self.makeRankRecordObj(rankrecord, groupid=rankrecord.groups[index], player_num=2, do_execute=False)
                if func_rankinfo:
                    def put_rankinfo():
                        self.html_param['battleevent_rank'] = func_rankinfo()
                    self.addExecuteApiWork(put_rankinfo)
                    break
        
        # スコア情報.
        scorerecord = BackendApi.get_battleevent_scorerecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
        self.html_param['battleevent_score'] = self.makeScoreRecordObj(scorerecord)
        
        # グループの詳細へ.
        self.html_param['url_battleevent_group'] = self.makeAppLinkUrl(UrlMaker.battleevent_group())
    
    def procClosed(self):
        """終了.
        """
        model_mgr = self.getModelMgr()
        eventid = self.__eventmaster.id
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # エピローグ.
        if BackendApi.check_battleevent_lead_epilogue(model_mgr, uid, eventid, using=settings.DB_READONLY):
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.battleevent_epilogue()))
            return
        
        # ランク情報.
        rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
        if rankrecord and rankrecord.groups:
            groupnum = len(rankrecord.groups)
            for i in xrange(groupnum):
                index = groupnum - (i + 1)
                func_rankinfo = self.makeRankRecordObj(rankrecord, groupid=rankrecord.groups[index], do_execute=False)
                if func_rankinfo:
                    def put_rankinfo():
                        self.html_param['battleevent_rank'] = func_rankinfo()
                    self.addExecuteApiWork(put_rankinfo)
                    break
        
        # スコア情報.
        scorerecord = BackendApi.get_battleevent_scorerecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
        self.html_param['battleevent_score'] = self.makeScoreRecordObj(scorerecord)

    def check_user_continue_victory_data(self, uid, eventid):
        """確認して無い場合は作成する."""
        return BackendApi.get_battleevent_continue_victory(self.getModelMgr(), uid, eventid, using=settings.DB_READONLY).count

    def put_user_continue_victory_data(self, cvictory_count):
        self.html_param['continue_victory_count'] = cvictory_count

    def create_piece_image_paths(self, uid, eventid):
        model_mgr = self.getModelMgr()
        userdata_list = BackendApi.get_user_piece_all_rarity_list(model_mgr, uid, eventid, using=settings.DB_READONLY)
        userdata_dict = dict([(userdata.rarity, userdata) for userdata in userdata_list])
        cardid_list = BackendApi.get_piececomplete_prize_card_list(eventid)
        cardmaster_dict = BackendApi.get_cardmasters(cardid_list)

        piecemaster_list = BackendApi.get_battleevent_piecemaster(model_mgr, eventid, using=settings.DB_READONLY)

        piece_data = []
        default_piece_numbers = dict.fromkeys(xrange(1, 10), False)
        for piecemaster in piecemaster_list:
            card = cardmaster_dict.get(piecemaster.complete_prize)
            userdata = userdata_dict.get(piecemaster.number)
            
            data = {
                'is_complete': userdata and userdata.is_complete_morethan_maxcount(piecemaster.complete_cnt_max),
                'rarity': piecemaster.name,
                'name': card.name,
                'complete_prize_name': piecemaster.complete_prize_name,
                'complete_cnt': userdata.complete_cnt
            }
            if userdata:
                for x in xrange(1, 10):
                    data[x] = getattr(userdata, 'piece_number{}'.format(x-1))
            else:
                data.update(default_piece_numbers)
            piece_data.append(data)
        return piece_data

    def get_battle_ticket_expiry_date(self, battleevent_endtime):
        """
            Return the expiry date of battle ticket
            Which is the last day of the current month in which
            the battle　event occurs

            Note: calendar.monthrange respects leap years
        """
        
        year = int(battleevent_endtime.strftime('%Y'))
        month = int(battleevent_endtime.strftime('%m'))
        # last_day = 20
#        last_day = calendar.monthrange(year, month)[1]
        day= int(battleevent_endtime.strftime('%d'))
        hour= int(battleevent_endtime.strftime('%H'))
        min= int(battleevent_endtime.strftime('%M'))
        expiry_date = str(month) + '/' + str('%02d' % day) + ' '+ str('%02d' % hour)+':'+ str('%02d' % min)
        return expiry_date

def main(request):
    return Handler.run(request)
