# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.produce_event.base import ProduceEventBaseHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.redisdb import ProduceEventRanking
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerExp
from platinumegg.app.cabaret.models.View import CardMasterView

class Handler(ProduceEventBaseHandler):
    """プロデュースイベント説明ページ.
    ・ルールページ
    ・報酬ページ
    ・ランキングページ
    """

    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerExp]

    def process(self):

        args = self.getUrlArgs('/produceeventexplain/')
        mid = args.getInt(0)
        ope = args.get(1)

        model_mgr = self.getModelMgr()
        eventmaster = None

        if mid:
            eventmaster = BackendApi.get_produce_event_master(model_mgr, mid, using=settings.DB_READONLY)

        if eventmaster is None:
            raise CabaretError(u'閲覧できないイベントです', CabaretError.Code.ILLEGAL_ARGS)

        # 開催中判定.
        cur_eventmaster = self.getCurrentProduceEvent(quiet=True)
        is_opened = cur_eventmaster and cur_eventmaster.id == mid

        self.html_param['is_opened'] = is_opened

        # イベント情報.
        config = BackendApi.get_current_produce_event_config(model_mgr, using=settings.DB_READONLY)
        self.html_param['produceevent'] = Objects.produceevent(self, eventmaster, config)

        v_player = self.getViewerPlayer()

        self.putEventTopic(mid, 'explain')

        self.html_param['current_topic'] = ope

        table = {
            'detail': self.__proc_detail,
            'prizes': self.__proc_prizes,
            'nominatecast' : self.__proc_nominatecast,
            'ranking': self.__proc_ranking,
        }
        
        for k in table.keys():
            self.html_param['url_produceevent_explain_%s' % k] = self.makeAppLinkUrl(UrlMaker.produceevent_explain(mid, k))
        self.html_param['shop_url'] = self.makeAppLinkUrl(UrlMaker.shop())
        
        table.get(ope, self.__proc_detail)(eventmaster, is_opened)

    def __proc_detail(self, eventmaster, is_opened):
        """イベント概要.
        """
        model_mgr = self.getModelMgr()
        self.html_param['current_topic'] = 'detail'
        item_master = BackendApi.get_itemmaster(model_mgr, eventmaster.changeitem, using=settings.DB_READONLY)
        if item_master:
            self.html_param['change_item'] = Objects.itemmaster(self, item_master)
        self.writeAppHtml('produce_event/detail')

    def __proc_prizes_request_process(self, model_mgr, eventmaster, produce_castmasters):
        urlbase = UrlMaker.produceevent_explain(eventmaster.id, 'prizes')
        self.html_param['url_ranking_prizes'] = self.makeAppLinkUrl(
            OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'ranking'))
        self.html_param['url_point_prizes'] = self.makeAppLinkUrl(
            OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'point'))
            
        url_level_prizes = []
        for produce_castmaster in produce_castmasters:
            card_master = produce_castmaster.get_card(model_mgr, using=settings.DB_READONLY)
            card_master_view = BackendApi.get_model(model_mgr, CardMasterView, card_master.id, using=settings.DB_READONLY)
            rare = card_master_view.rare
            base =  OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, 'level')
            last =  OSAUtil.addQuery(base, Defines.URLQUERY_CKIND, rare)
            url_level_prizes.append({"rare":rare,"url":self.makeAppLinkUrl(last)})
        self.html_param['url_level_prizes'] = url_level_prizes
        
    def __proc_prizes_response_process(self, model_mgr, eventmaster, produce_castmasters, is_opened):
        ctype = self.request.get(Defines.URLQUERY_CTYPE)
        self.html_param['current_prize'] = ctype
        self.html_param['current_kind'] = self.request.get(Defines.URLQUERY_CKIND)

        if ctype == 'ranking':
            self.__proc_prizes_ranking(eventmaster, is_opened)
        elif ctype == 'point':
            self.__proc_prizes_point(eventmaster, is_opened)
        elif ctype == 'level':
            current_rare = int(self.html_param['current_kind'])
            current_produce_castmaster = self.__find_produce_castmaster(model_mgr, produce_castmasters, current_rare)
            self.__proc_prizes_level(eventmaster.id, current_produce_castmaster, is_opened)
        else:
            self.html_param['current_prize'] = 'point'
            self.__proc_prizes_point(eventmaster, is_opened)

    def __proc_prizes(self, eventmaster, is_opened):
        """イベントの報酬
        """
        produce_castmasters = eventmaster.get_produce_castmasters(using=settings.DB_READONLY)
        model_mgr = self.getModelMgr()

        self.__proc_prizes_request_process(model_mgr, eventmaster, produce_castmasters)
        self.__proc_prizes_response_process(model_mgr, eventmaster, produce_castmasters, is_opened)

    def __find_produce_castmaster(self, model_mgr, produce_castmasters, current_rare):
        for produce_castmaster in produce_castmasters:
            card_master = produce_castmaster.get_card(model_mgr, using=settings.DB_READONLY)
            card_master_view = BackendApi.get_model(model_mgr, CardMasterView, card_master.id, using=settings.DB_READONLY)
            if card_master_view.rare == current_rare:
                return produce_castmaster
        raise CabaretError(u'レア度に対応するProduceCastMasterが存在しません', CabaretError.Code.ILLEGAL_ARGS)

    def __proc_prizes_ranking(self, eventmaster, is_opened):
        """ランキング報酬
        """
        # 報酬
        prizedatalist = self.make_rankingprizelist(eventmaster.rankingprizes)
        self.html_param['rankingprizelist'] = prizedatalist

        self.writeAppHtml('produce_event/rankprizes')

    def __proc_prizes_point(self, eventmaster, is_opened):
        """イベントポイント達成報酬
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()

        # 現在のプレーヤーのスコア
        scorerecord = BackendApi.get_produceevent_scorerecord(model_mgr, eventmaster.id, v_player.id, using=settings.DB_READONLY)
        cur_point = scorerecord.point if scorerecord else 0
        
        prizedatalist = self.make_pointprizelist(eventmaster.pointprizes, cur_point)
        self.html_param['pointprizelist'] = prizedatalist

        self.writeAppHtml('produce_event/pointprizes')

    def __proc_prizes_level(self, eventmaster_id, produce_castmaster, is_opened):
        """教育レベル達成報酬
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
            
        # 現在のプレーヤーのスコア
        player_education = BackendApi.get_player_education(model_mgr, v_player.id, eventmaster_id, using=settings.DB_READONLY)
        prizeinfo = self.make_prizeinfo(produce_castmaster, player_education)

        self.html_param['levelprizelist'] = prizeinfo

        self.writeAppHtml('produce_event/levelprizes')

    def get_prizedata_instance_list(self, model_mgr, lvprizes):
        lists = {}
        for id_hash in lvprizes:
            prizes = BackendApi.get_prizelist(model_mgr, id_hash["prize"], using=settings.DB_READONLY)
            lists[id_hash["level"]] = prizes
        return lists

    def make_prizeinfo(self, produce_castmaster, player_education):
        """[{'level':1,'prizedata':{}},...]
        """
        model_mgr = self.getModelMgr()
        prizes_hash = self.get_prizedata_instance_list(model_mgr, produce_castmaster.lvprizes)
        if player_education.cast_order > produce_castmaster.order:
            player_level = produce_castmaster.max_education_level
        elif player_education.cast_order < produce_castmaster.order:
            player_level = 0
        elif player_education.cast_order == produce_castmaster.order:
            player_level = player_education.level

        prizehash_list = []
        for k,v in prizes_hash.items():
            is_received = k <= player_level
            
            prizehash_list.append({
                "level": k,
                "prizeinfo": BackendApi.make_prizeinfo(self, v, using=settings.DB_READONLY),
                "is_received": is_received,
            })

        return prizehash_list

    def __proc_nominatecast(self, eventmaster, is_opened):
        """特効キャスト一覧.
        """
        model_mgr = self.getModelMgr()
        
        # 特効カードのマスター.
        specialcard = dict(eventmaster.specialcard)
        midlist = specialcard.keys()
        cardmasters = BackendApi.get_cardmasters(midlist, model_mgr, using=settings.DB_READONLY)
        
        # 埋め込み用パラメータ作成.
        obj_cardlist = []
        for mid, cardmaster in cardmasters.items():
            rate = specialcard[mid]
            obj = Objects.cardmaster(self, cardmaster)
            obj['specialpowup'] = rate
            obj_cardlist.append(obj)
        obj_cardlist.sort(key=lambda x:(x['rare'] << 32)+(Defines.HKLEVEL_MAX - x['hklevel']), reverse=True)
        self.html_param['specialcardlist'] = obj_cardlist
        
        self.writeHtml(eventmaster, 'nominatecast')

    def __proc_ranking(self, eventmaster, is_opened):
        """イベントランキング.
        """
        is_myrank = bool(int(self.request.get(Defines.URLQUERY_FLAG, '0')))
        self.html_param['is_myrank'] = is_myrank

        mid = eventmaster.id

        if not ProduceEventRanking.exists(mid):
            BackendApi.backup_produce_event_ranking_data_into_redis(mid)

        if is_myrank:
            self.html_param['ranking_playerlist'] = self.putMyRanking(mid)
            self.html_param['url_ranking'] = self.makeAppLinkUrl(UrlMaker.produceevent_explain(mid, 'ranking'))
        else:
            self.html_param['ranking_playerlist'] = self.putRanking(mid)
            self.html_param['url_myrank'] = self.makeAppLinkUrl(OSAUtil.addQuery(UrlMaker.produceevent_explain(mid, 'ranking'), Defines.URLQUERY_FLAG, '1'))

        self.html_param['current_topic'] = 'ranking'
        self.writeAppHtml('produce_event/ranking')

    def putRanking(self, mid):
        page = int(self.request.get(Defines.URLQUERY_PAGE, 0))

        offset = page * self.CONTENT_NUM_MAX_PER_PAGE
        limit = self.CONTENT_NUM_MAX_PER_PAGE
        uidscoresetlist = BackendApi.fetch_uid_by_produceeventrank(mid, limit, offset, withrank=True)

        url_base = UrlMaker.produceevent_explain(mid, 'ranking')
        contentnum = BackendApi.get_produceevent_rankernum(mid)
        self.putPagenation(url_base, page, contentnum, self.CONTENT_NUM_MAX_PER_PAGE)

        return self.get_obj_playerlist(uidscoresetlist)

    def putMyRanking(self, mid):
        v_player = self.getViewerPlayer()

        uid = v_player.id

        score = BackendApi.get_produceevent_score(mid, uid)
        if score is None:
            return []

        index = BackendApi.get_produceevent_rankindex(mid, uid)
        offset = max(0, index-int((self.CONTENT_NUM_MAX_PER_PAGE+1)/2))
        uidscoresetlist = BackendApi.fetch_uid_by_produceeventrank(mid, self.CONTENT_NUM_MAX_PER_PAGE, offset, withrank=True)

        return self.get_obj_playerlist(uidscoresetlist)

    def get_obj_playerlist(self, uidscoresetlist):
        model_mgr = self.getModelMgr()

        obj_playerlist = []

        uidscoreset = dict(uidscoresetlist)
        uidscoreset_keys = uidscoreset.keys()

        playerlist = BackendApi.get_players(self, uidscoreset_keys, using=settings.DB_READONLY)
        persons = BackendApi.get_dmmplayers(self, playerlist, using=settings.DB_READONLY, do_execute=False)
        self.execute_api()

        leaders = BackendApi.get_leaders(uidscoreset_keys, arg_model_mgr=model_mgr, using=settings.DB_READONLY)

        for player in playerlist:
            obj_player = Objects.player(self, player, persons.get(player.dmmid), leaders.get(player.id))
            score, rank = uidscoreset[player.id]
            obj_player['event_score'] = score
            obj_player['event_rank'] = rank
            obj_playerlist.append(obj_player)
        obj_playerlist.sort(key=lambda x: x['event_score'], reverse=True)
        return obj_playerlist


def main(request):
    return Handler.run(request)
