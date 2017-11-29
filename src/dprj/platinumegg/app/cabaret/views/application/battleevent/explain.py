# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.cabareterror import CabaretError

class Handler(BattleEventBaseHandler):
    """バトルイベント説明ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        args = self.getUrlArgs('/battleeventexplain/')
        eventid = args.getInt(0)
        ope = args.get(1)
        
        model_mgr = self.getModelMgr()
        eventmaster = None
        if eventid:
            eventmaster = BackendApi.get_battleevent_master(model_mgr, eventid, using=settings.DB_READONLY)
        
        if eventmaster is None:
            raise CabaretError(u'閲覧できないイベントです', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 開催中判定.
        cur_eventmaster = self.getCurrentBattleEvent(quiet=True)
        if cur_eventmaster and cur_eventmaster.id == eventid:
            is_opened = True
            do_check_loginbonus = not cur_eventmaster.is_goukon
            if not self.checkBattleEventUser(do_check_battle_open=False, do_check_regist=False, do_check_emergency=False, do_check_loginbonus=do_check_loginbonus):
                return
        else:
            is_opened = False
        self.html_param['is_opened'] = is_opened
        
        # イベント情報.
        self.html_param['battleevent'] = Objects.battleevent(self, eventmaster)
        
        # スコア.
        scorerecord = BackendApi.get_battleevent_scorerecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
        rank = BackendApi.get_battleevent_rank(eventid, uid)
        self.html_param['battleevent_score'] = Objects.battleevent_score(self, scorerecord, rank)
        
        self.putEventTopic(eventid, 'explain')
        
        self.html_param['current_topic'] = ope
        
        table = {
            'detail' : self.__proc_detail,
            'prizes' : self.__proc_prizes,
            'nomination' : self.__proc_nomination,
            'faq' : self.__proc_faq,
        }
        for k in table.keys():
            self.html_param['url_explain_%s' % k] = self.makeAppLinkUrl(UrlMaker.battleevent_explain(eventid, k))
        table.get(ope, self.__proc_detail)(eventmaster, is_opened)
    
    def writeHtml(self, eventmaster, htmlname):
        """HTML作成.
        """
        if eventmaster.is_goukon:
            self.writeAppHtml('gcevent/%s' % htmlname)
        else:
            self.writeAppHtml('btevent/%s' % htmlname)
    
    def __proc_detail(self, eventmaster, is_opened):
        """イベント概要.
        """
        if is_opened:
            # イベント参加KPI保存.
            v_player = self.getViewerPlayer()
            BackendApi.save_kpi_battleevent_join(v_player.id, self.is_pc)
        
        self.html_param['current_topic'] = 'detail'
        self.writeHtml(eventmaster, 'manual')
    
    def __proc_prizes(self, eventmaster, is_opened):
        """報酬.
        """
        urlbase = UrlMaker.battleevent_explain(eventmaster.id, 'prizes')
#        self.html_param['url_prizes_point'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'point'))
        self.html_param['url_prizes_ranking'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'ranking'))
        self.html_param['url_prizes_group_ranking'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'group_ranking'))
        self.html_param['url_prizes_battlepoint'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'battlepoint'))
        self.html_param['url_prizes_ranking_beginer'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'ranking_beginer'))
        
        ctype = self.request.get(Defines.URLQUERY_CTYPE)
        
        self.html_param['current_prize'] = ctype
        
        if ctype == 'ranking':
            self.__proc_prizes_ranking(eventmaster, is_opened)
        elif ctype == 'ranking_beginer':
            self.__proc_prizes_ranking_beginer(eventmaster, is_opened)
        elif ctype == 'battlepoint':
            self.__proc_prizes_battlepoint(eventmaster, is_opened)
        else:
            self.html_param['current_prize'] = 'group_ranking'
            self.__proc_prizes_group_ranking(eventmaster, is_opened)
#        else:
#            self.html_param['current_prize'] = 'point'
#            self.__proc_prizes_point(eventmaster, is_opened)
    
    def __proc_prizes_point(self, eventmaster, is_opened):
        """名声PT達成報酬.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 設定.
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        
        # ランク情報.
        rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventmaster.id, uid, using=settings.DB_READONLY)
        fame = 0
        if rankrecord:
            fame = rankrecord.getFamePoint(config)
        
        # 報酬.
        prizedatalist = self.__make_pointprizelist(eventmaster.pointprizes, fame)
        self.html_param['pointprizelist'] = prizedatalist
        
        self.writeHtml(eventmaster, 'successbonus')
    
    def __proc_prizes_ranking(self, eventmaster, is_opened):
        """ランキング報酬.
        """
        # 報酬.
        prizedatalist = self.make_rankingprizelist(eventmaster.rankingprizes)
        self.html_param['rankingprizelist'] = prizedatalist
        
        self.writeHtml(eventmaster, 'rankbonus')
    
    def __proc_prizes_ranking_beginer(self, eventmaster, is_opened):
        """新店舗ランキング報酬.
        """
        # 報酬.
        prizedatalist = self.make_rankingprizelist(eventmaster.beginer_rankingprizes)
        self.html_param['rankingprizelist'] = prizedatalist
        
        self.writeHtml(eventmaster, 'rankbonus')
    
    def __get_myrank(self, eventmaster):
        """自分の現在のランク.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        myrank = 1
        rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventmaster.id, uid, using=settings.DB_READONLY)
        if rankrecord:
            # 設定.
            config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
            myrank = rankrecord.getRank(config)
        return myrank
    
    def __get_selected_rank(self, eventmaster, myrank):
        """プルダウンメニューで選択したランク.
        """
        model_mgr = self.getModelMgr()
        
        str_target_rank = self.request.get(Defines.URLQUERY_CURRENT)
        target_rank = myrank
        if str(str_target_rank).isdigit():
            target_rank = int(str_target_rank)
        
        rankmaster = BackendApi.get_battleevent_rankmaster(model_mgr, eventmaster.id, target_rank, using=settings.DB_READONLY)
        battleevent_rank_selectobj = None
        if rankmaster is not None:
            # ランクが存在しない.
            battleevent_rank_selectobj = Objects.battleevent_rank_selectobj(self, rankmaster)
            self.html_param['battleevent_rank_number'] = target_rank
        self.html_param['battleevent_rank_selectobj'] = battleevent_rank_selectobj
        
        return rankmaster
    
    def __put_rankmaster_list_for_selectbox(self, eventmaster, myrank):
        """セレクトBOXにランク一覧を埋め込む.
        """
        model_mgr = self.getModelMgr()
        # マスターデータ.
        rankmasterlist = BackendApi.get_battleevent_rankmaster_by_eventid(model_mgr, eventmaster.id, using=settings.DB_READONLY)
        rankmasterlist.sort(key=lambda x:x.rank)
        
        obj_rankmasterlist = []
        for master in rankmasterlist:
            obj_rankmasterlist.append({
                'rank' : master.rank,
                'name' : master.name,
                'myrank' : myrank == master.rank,
            })
        self.html_param['rankmaster_list'] = obj_rankmasterlist
    
    def __proc_prizes_battlepoint(self, eventmaster, is_opened):
        """ランク別バトルポイント達成報酬.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 自分のランク.
        myrank = self.__get_myrank(eventmaster)
        
        # 選択したランク.
        rankmaster = self.__get_selected_rank(eventmaster, myrank)
        if rankmaster is None:
            # ランクが存在しない.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.battleevent_top(eventmaster.id)))
            return
        
        # セレクトBOX.
        self.__put_rankmaster_list_for_selectbox(eventmaster, myrank)
        
        # 現在のポイント.
        rankscorerecord = BackendApi.get_battleevent_score_per_rank_record(model_mgr, uid, eventmaster.id, rankmaster.rank, using=settings.DB_READONLY)
        point = rankscorerecord.point if rankscorerecord else 0
        self.html_param['point'] = point
        
        # 報酬.
        prizedatalist = self.__make_pointprizelist(rankmaster.battlepointprizes, point)
        self.html_param['pointprizelist'] = prizedatalist
        
        self.writeHtml(eventmaster, 'bpsuccessbonus')
    
    def __proc_prizes_group_ranking(self, eventmaster, is_opened):
        """ランク別ランキング報酬.
        """
        # 自分のランク.
        myrank = self.__get_myrank(eventmaster)
        
        # 選択したランク.
        rankmaster = self.__get_selected_rank(eventmaster, myrank)
        if rankmaster is None:
            # ランクが存在しない.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.battleevent_top(eventmaster.id)))
            return
        
        # セレクトBOX.
        self.__put_rankmaster_list_for_selectbox(eventmaster, myrank)
        
        # 報酬.
        prizedatalist = self.make_rankingprizelist(rankmaster.group_rankingprizes)
        self.html_param['rankingprizelist'] = prizedatalist
        
        self.writeHtml(eventmaster, 'daily_groupbonus')
    
    def __proc_nomination(self, eventmaster, is_opened):
        """ご指名キャスト一覧.
        """
        model_mgr = self.getModelMgr()
        # 特効キャスト.
        specialcard_dict = dict(eventmaster.specialcard)
        battleticket_rate = dict(eventmaster.battleticket_rate)

        midlist = specialcard_dict.keys()
        cardmasters = BackendApi.get_cardmasters(midlist, model_mgr, using=settings.DB_READONLY)
        
        obj_cardlist = []
        for mid, rate in eventmaster.specialcard:
            cardmaster = cardmasters.get(mid)
            if not cardmaster:
                continue
            obj = Objects.cardmaster(self, cardmaster)
            obj['specialpowup'] = rate
            ticket_rate = battleticket_rate.get(mid)

            if ticket_rate:
                obj['battleticket_rateup'] = ticket_rate
            obj_cardlist.append(obj)
        self.html_param['specialcardlist'] = obj_cardlist

        # 属性ボーナス.
        specialtype_dict = dict(eventmaster.specialtable)
        for rare in specialtype_dict.keys():
            arr = specialtype_dict[rare] + [100] * Defines.HKLEVEL_MAX
            specialtype_dict[rare] = arr[:Defines.HKLEVEL_MAX]

        self.html_param['specialtypedict'] = specialtype_dict
        
        self.writeHtml(eventmaster, 'nominatecast')
    
    def __proc_faq(self, eventmaster, is_opened):
        """FAQ.
        """
        self.writeHtml(eventmaster, 'eventfaq')
    
    def __make_pointprizelist(self, prizes, cur_point):
        """名声ポイント達成報酬リスト作成.
        """
        if isinstance(prizes, list):
            prizes_dict = dict(prizes)
            repeat = []
        elif not isinstance(prizes, dict):
            prizes_dict = {}
            repeat = []
        else:
            prizes_dict = dict(prizes.get('normal') or [])
            repeat = prizes.get('repeat') or []
        
        # 報酬.
        model_mgr = self.getModelMgr()
        
        # 報酬.
        prizedatalist = []
        for point, prizeidlist in prizes_dict.items():
            if not prizeidlist:
                continue
            
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY)
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
            
            prizedatalist.append({
                'point' : point,
                'prizeinfo' : prizeinfo,
                'received' : point <= cur_point,
            })
        
        for repeat_data in repeat:
            prizeidlist = repeat_data.get('prize')
            if not prizeidlist:
                continue
            
            point = max(1, repeat_data.get('min', 1))
            interval = max(1, repeat_data.get('interval', 1))
            
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY)
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
            
            prizedatalist.append({
                'point' : point,
                'prizeinfo' : prizeinfo,
                'received' : False,
                'interval':interval,
                'repeat':True,
            })
        
        prizedatalist.sort(key=lambda x:x['point'])
        return prizedatalist

def main(request):
    return Handler.run(request)
