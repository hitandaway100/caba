# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerExp


class Handler(RaidEventBaseHandler):
    """レイドイベント説明ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerExp]
    
    def process(self):
        
        args = self.getUrlArgs('/raideventexplain/')
        str_eventid = str(args.get(0))
        ope = args.get(1)
        
        model_mgr = self.getModelMgr()
        eventmaster = None
        mid = None
        if str_eventid.isdigit():
            mid = int(str_eventid)
            eventmaster = BackendApi.get_raideventmaster(model_mgr, mid, using=settings.DB_READONLY)
        
        if eventmaster is None:
            raise CabaretError(u'閲覧できないイベントです', CabaretError.Code.ILLEGAL_ARGS)
        
        # 開催中判定.
        cur_eventmaster = self.getCurrentRaidEvent(quiet=True)
        if cur_eventmaster and cur_eventmaster.id == mid:
            is_opened = True
        else:
            is_opened = False
        self.html_param['is_opened'] = is_opened
        
        # イベント情報.
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        self.html_param['raidevent'] = Objects.raidevent(self, eventmaster, config)
        
        # スコア.
        v_player = self.getViewerPlayer()
        scorerecord = BackendApi.get_raidevent_scorerecord(model_mgr, eventmaster.id, v_player.id, using=settings.DB_READONLY)
        rank = BackendApi.get_raidevent_rank(eventmaster.id, v_player.id)
        self.html_param['raideventscore'] = Objects.raidevent_score(eventmaster, scorerecord, rank)
        
        self.putEventTopic(mid, 'explain')
        
        self.html_param['current_topic'] = ope
        
        table = {
            'detail' : self.__proc_detail,
            'prizes' : self.__proc_prizes,
            'nomination' : self.__proc_nomination,
            'faq' : self.__proc_faq,
        }
        for k in table.keys():
            self.html_param['url_explain_%s' % k] = self.makeAppLinkUrl(UrlMaker.raidevent_explain(mid, k))
        table.get(ope, self.__proc_detail)(eventmaster, is_opened)
    
    def __proc_detail(self, eventmaster, is_opened):
        """イベント概要.
        """
        self.html_param['current_topic'] = 'detail'
        
        self.putEventGachaUrl()
        
        is_gacha_opened = is_opened
        self.html_param['is_gacha_opened'] = is_gacha_opened
        
        if is_opened:
            BackendApi.put_eventscout_earlybonusinfo(self, eventmaster)
            
            # イベント参加のKPIを保存.
            v_player = self.getViewerPlayer()
            BackendApi.save_kpi_raidevent_join(v_player.id, self.is_pc)
        
        self.writeHtml(eventmaster, 'manual')
    
    def __proc_prizes(self, eventmaster, is_opened):
        """報酬.
        """
        urlbase = UrlMaker.raidevent_explain(eventmaster.id, 'prizes')
        self.html_param['url_prizes_destroy'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'destroy'))
        self.html_param['url_prizes_destroy_big'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'destroy_big'))
        self.html_param['url_prizes_ranking'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'ranking'))
        self.html_param['url_prizes_ranking_beginer'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'ranking_beginer'))
        
        ctype = self.request.get(Defines.URLQUERY_CTYPE)
        
        self.html_param['current_prize'] = ctype
        
        if ctype == 'ranking':
            self.__proc_prizes_ranking(eventmaster, is_opened)
        elif ctype == 'destroy_big':
            self.__proc_prizes_destroy_big(eventmaster, is_opened)
        elif ctype == 'ranking_beginer':
            self.__proc_prizes_ranking_beginer(eventmaster, is_opened)
        else:
            self.html_param['current_prize'] = 'destroy'
            self.__proc_prizes_destroy(eventmaster, is_opened)
    
    def __proc_prizes_destroy(self, eventmaster, is_opened):
        """討伐回数報酬.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 受け取りフラグ.
        flagrecord = BackendApi.get_raidevent_flagrecord(model_mgr, eventmaster.id, uid, using=settings.DB_READONLY)
        if flagrecord:
            flags = flagrecord.destroyprize_flags
        else:
            flags = {}
        
        # 報酬.
        prizedatalist = self.__make_destroyprizelist(eventmaster.destroyprizes, flags)
        self.html_param['destroyprizelist'] = prizedatalist
        
        self.writeHtml(eventmaster, 'successbonus')
    
    def __proc_prizes_destroy_big(self, eventmaster, is_opened):
        """討伐回数報酬(大ボス).
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 受け取りフラグ.
        flagrecord = BackendApi.get_raidevent_flagrecord(model_mgr, eventmaster.id, uid, using=settings.DB_READONLY)
        if flagrecord:
            flags = flagrecord.destroyprize_big_flags
        else:
            flags = {}
        
        # 報酬.
        prizedatalist = self.__make_destroyprizelist(eventmaster.destroyprizes_big, flags)
        self.html_param['destroyprizelist'] = prizedatalist
        
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
    
    def __proc_nomination(self, eventmaster, is_opened):
        """ご指名キャスト一覧.
        """
        model_mgr = self.getModelMgr()
        
        # イベントレイド.
        raidlist = BackendApi.get_raidevent_raidmaster_by_eventid(model_mgr, eventmaster.id, using=settings.DB_READONLY)
        
        # 特効カード.
        specialcard = {}
        for raid in raidlist:
            for mid, rate in raid.specialcard:
                specialcard[mid] = max(specialcard.get(mid, 0), rate)
        
        # 特効カードのマスター.
        midlist = specialcard.keys()
        cardmasters = BackendApi.get_cardmasters(midlist, model_mgr, using=settings.DB_READONLY)
        
        # 埋め込み用パラメータ作成.
        obj_cardlist = []
        for mid, cardmaster in cardmasters.items():
            rate = specialcard[mid]
            obj = Objects.cardmaster(self, cardmaster)
            obj['specialpowup'] = rate
            obj['specialtreasure'] = raidlist[0].specialcard_treasure[obj["rare_str"]][obj["hklevel"]-1]
            obj_cardlist.append(obj)
        obj_cardlist.sort(key=lambda x:(x['rare'] << 32)+(Defines.HKLEVEL_MAX - x['hklevel']), reverse=True)
        self.html_param['specialcardlist'] = obj_cardlist
        
        self.writeHtml(eventmaster, 'nominatecast')
    
    def __proc_faq(self, eventmaster, is_opened):
        """FAQ.
        """
        self.writeHtml(eventmaster, 'eventfaq')
    
    def __make_destroyprizelist(self, destroyprizes, flags):
        """討伐回数報酬リスト作成.
        """
        if isinstance(destroyprizes, list):
            destroyprizes_dict = dict(destroyprizes)
            repeat = []
        elif not isinstance(destroyprizes, dict):
            destroyprizes_dict = {}
            repeat = []
        else:
            destroyprizes_dict = dict(destroyprizes.get('normal') or [])
            repeat = destroyprizes.get('repeat') or []
        
        # 報酬.
        model_mgr = self.getModelMgr()
        
        # 報酬.
        prizedatalist = []
        for destroy, prizeidlist in destroyprizes_dict.items():
            if not prizeidlist:
                continue
            
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY)
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
            
            prizedatalist.append({
                'destroy' : destroy,
                'prizeinfo' : prizeinfo,
                'received' : destroy in flags,
            })
        
        for repeat_data in repeat:
            prizeidlist = repeat_data.get('prize')
            if not prizeidlist:
                continue
            
            destroy = max(1, repeat_data.get('min', 1))
            interval = max(1, repeat_data.get('interval', 1))
            
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY)
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
            
            prizedatalist.append({
                'destroy' : destroy,
                'prizeinfo' : prizeinfo,
                'received' : False,
                'interval':interval,
                'repeat':True,
            })
        
        prizedatalist.sort(key=lambda x:x['destroy'])
        return prizedatalist
    

def main(request):
    return Handler.run(request)
