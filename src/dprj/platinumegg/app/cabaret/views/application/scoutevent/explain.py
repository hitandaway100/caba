# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines


class Handler(ScoutHandler):
    """スカウトイベント説明ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        args = self.getUrlArgs('/sceventexplain/')
        str_eventid = str(args.get(0))
        ope = args.get(1)
        
        model_mgr = self.getModelMgr()
        eventmaster = None
        mid = None
        if str_eventid.isdigit():
            mid = int(str_eventid)
            eventmaster = BackendApi.get_scouteventmaster(model_mgr, mid, using=settings.DB_READONLY)
        
        if eventmaster is None:
            raise CabaretError(u'閲覧できないイベントです', CabaretError.Code.ILLEGAL_ARGS)
        
        # 開催中判定.
        cur_eventmaster = self.getCurrentScoutEvent(quiet=True)
        if cur_eventmaster and cur_eventmaster.id == mid:
            is_opened = True
        else:
            is_opened = False
        self.html_param['is_opened'] = is_opened
        
        # イベント情報.
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
        self.html_param['scoutevent'] = Objects.scouteventmaster(self, eventmaster, config)
        
        self.putEventTopic(mid, 'explain')
        
        self.html_param['current_topic'] = ope
        
        table = {
            'detail' : self.__proc_detail,
            'prizes' : self.__proc_prizes,
            'nomination' : self.__proc_nomination,
            'faq' : self.__proc_faq,
        }
        
        for k in table.keys():
            self.html_param['url_explain_%s' % k] = self.makeAppLinkUrl(UrlMaker.scoutevent_explain(mid, k))
        table.get(ope, self.__proc_detail)(eventmaster, is_opened)
    
    def writeHtml(self, eventmaster, htmlname):
        """HTML作成.
        """
        self.writeScoutEventHTML(htmlname, eventmaster)
    
    def __proc_detail(self, eventmaster, is_opened):
        """イベント概要.
        """
        model_mgr = self.getModelMgr()

        if is_opened:
            BackendApi.put_eventscout_earlybonusinfo(self, eventmaster)
            
            # イベント参加KPIを保存.
            v_player = self.getViewerPlayer()
            BackendApi.save_kpi_scoutevent_join(v_player.id, self.is_pc)

        tanzakucastmaster = BackendApi.get_scoutevent_tanzakumaster(model_mgr, eventmaster.id, 0, using=settings.DB_READONLY)

        self.html_param['is_open'] = { 'tanzaku': False }
        if tanzakucastmaster is not None:
            self.html_param['is_open']['tanzaku'] = True

        self.html_param['current_topic'] = 'detail'
        self.writeHtml(eventmaster, 'manual')
    
    def __proc_prizes(self, eventmaster, is_opened):
        """報酬.
        """
        urlbase = UrlMaker.scoutevent_explain(eventmaster.id, 'prizes')
        self.html_param['url_prizes_point'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'point'))
        self.html_param['url_prizes_ranking'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'ranking'))
        self.html_param['url_prizes_areabonus'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'areabonus'))
        self.html_param['url_prizes_producebonus'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'producebonus'))
        self.html_param['url_prizes_ranking_beginer'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'ranking_beginer'))
        
        tanzakumasterlist = BackendApi.get_scoutevent_tanzakumaster_by_eventid(self.getModelMgr(), eventmaster.id, using=settings.DB_READONLY)
        if tanzakumasterlist:
            # 短冊がある.
            self.html_param['url_prizes_performance'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'performance'))
        
        ctype = self.request.get(Defines.URLQUERY_CTYPE)
        
        self.html_param['current_prize'] = ctype
        
        if ctype == 'ranking':
            self.__proc_prizes_ranking(eventmaster, is_opened)
        elif ctype == 'ranking_beginer':
            self.__proc_prizes_ranking_beginer(eventmaster, is_opened)
        elif ctype == 'areabonus':
            self.__proc_prizes_areabonus(eventmaster, is_opened)
        elif ctype == 'producebonus':
            self.__proc_prizes_presentbonus(eventmaster, is_opened)
        elif ctype == 'performance':
            self.__proc_prizes_performance(eventmaster, is_opened)
        else:
            self.html_param['current_prize'] = 'point'
            self.__proc_prizes_point(eventmaster, is_opened)
    
    def __proc_prizes_areabonus(self, eventmaster, is_opened):
        """エリア達成報酬.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 現在のステージ.
        eventplaydata = BackendApi.get_event_playdata(model_mgr, eventmaster.id, uid, using=settings.DB_READONLY)
        cur_stagemaster = BackendApi.get_current_scouteventstage_master(model_mgr, eventmaster, eventplaydata, using=settings.DB_READONLY)
        
        # 報酬のあるステージ一覧.
        stagemasterlist = BackendApi.get_event_stagelist_filterby_bossprizes(model_mgr, eventmaster.id, using=settings.DB_READONLY)
        
        # 報酬.
        model_mgr = self.getModelMgr()
        
        # 全エリア.
        areaidlist = BackendApi.get_event_areaidlist(model_mgr, eventmaster.id, using=settings.DB_READONLY)
        areanum_cleared = areaidlist.index(cur_stagemaster.area) if cur_stagemaster.area in areaidlist else 0
        if eventplaydata and cur_stagemaster.stage < eventplaydata.stage:
            # 次のステージがなくてクリア済みのステージをプレイしているから今いるエリアはクリア扱いでいいはず.
            areanum_cleared += 1
        
        # 報酬.
        prizedatalist = []
        for stagemaster in stagemasterlist:
            prizeidlist = stagemaster.bossprizes
            if not prizeidlist:
                continue
            
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY)
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
            
            prizedatalist.append({
                'areaname' : stagemaster.areaname,
                'prizeinfo' : prizeinfo,
                'received' : stagemaster.area <= areanum_cleared,
            })
        self.html_param['areaprizelist'] = prizedatalist
        
        self.writeHtml(eventmaster, 'areabonus')
    
    def __proc_prizes_presentbonus(self, eventmaster, is_opened):
        """プロデュースプレゼント報酬.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 選択した項目.
        str_target_number = str(self.request.get(Defines.URLQUERY_CURRENT) or '')
        target_number = int(str_target_number) if str_target_number else None
        
        # 選択できる項目.
        masterlist = BackendApi.get_scoutevent_presentprizemaster_by_eventid(model_mgr, eventmaster.id, using=settings.DB_READONLY)
        
        # 現在のハート投入数.
        nums = BackendApi.get_scoutevent_presentnums_record(model_mgr, eventmaster.id, uid, get_instance=True, using=settings.DB_READONLY)
        
        # プルダウン項目.
        target_master = None
        obj_master_list = []
        for master in masterlist:
            if master.number == target_number:
                target_master = master
            obj_master_list.append(Objects.scoutevent_present_selectobj(self, master))
        self.html_param['scoutevent_present_selectobj'] = obj_master_list
        
        # 選択中の項目.
        target_master = target_master or masterlist[0]
        self.html_param['scoutevent_present_number'] = target_master.number
        
        # 報酬情報.
        prizedatalist = self.__make_pointprizelist(target_master.prizes, nums.get_num(target_master.number))
        self.html_param['pointprizelist'] = prizedatalist
        
        self.writeHtml(eventmaster, 'producebonus')
    
    def __proc_prizes_point(self, eventmaster, is_opened):
        """イベントポイント達成報酬.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 現在のスコア.
        scorerecord = BackendApi.get_scoutevent_scorerecord(model_mgr, eventmaster.id, uid, using=settings.DB_READONLY)
        cur_point = scorerecord.point_total if scorerecord else 0
        
        # 報酬.
        prizedatalist = self.__make_pointprizelist(eventmaster.pointprizes, cur_point)
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
    
    def __proc_prizes_performance(self, eventmaster, is_opened):
        """チップ投入の業績報酬.
        """
        model_mgr = self.getModelMgr()
        
        # 短冊キャスト一覧.
        tanzakucastmaster_list = BackendApi.get_scoutevent_tanzakumaster_by_eventid(model_mgr, eventmaster.id, using=settings.DB_READONLY)
        obj_tanzaku_list = []
        for tanzakucastmaster in tanzakucastmaster_list:
            prizelist = BackendApi.get_prizelist(model_mgr, tanzakucastmaster.prizes, using=settings.DB_READONLY)
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
            obj_tanzaku = Objects.scoutevent_tanzaku(self, tanzakucastmaster)
            obj_tanzaku['prize'] = prizeinfo
            obj_tanzaku_list.append(obj_tanzaku)
        self.html_param['scoutevent_tanzaku_list'] = obj_tanzaku_list
        
        self.writeHtml(eventmaster, 'performancebonus')
    
    def __proc_nomination(self, eventmaster, is_opened):
        """ご指名キャスト一覧.
        """
        model_mgr = self.getModelMgr()
        # 特効キャスト.
        specialcard_dict = dict(eventmaster.specialcard)
        midlist = specialcard_dict.keys()
        cardmasters = BackendApi.get_cardmasters(midlist, model_mgr, using=settings.DB_READONLY)
        
        obj_cardlist = []
        for mid, rate in eventmaster.specialcard:
            cardmaster = cardmasters.get(mid)
            if not cardmaster:
                continue
            obj = Objects.cardmaster(self, cardmaster)
            obj['specialpowup'] = rate
            obj_cardlist.append(obj)
        self.html_param['specialcardlist'] = obj_cardlist
        
        self.writeHtml(eventmaster, 'nominatecast')
    
    def __proc_faq(self, eventmaster, is_opened):
        """FAQ.
        """
        self.writeHtml(eventmaster, 'eventfaq')
    
    def __make_pointprizelist(self, prizes, cur_point):
        """イベントポイント達成報酬リスト作成.
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
