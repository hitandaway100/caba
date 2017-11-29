# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.app.cabaret.util.redisdb import CabaClubRanking
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.lib.opensocial.util import OSAUtil
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines

class Handler(CabaClubHandler):
    """キャバクラのランキング
    """

    CONTENT_NUM_PER_PAGE = 10

    def process(self):
        args = self.getUrlArgs('/cabaclubrank/')
        current_eventid = args.getInt(0)
        ope = args.get(1)
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()

        eventmaster = BackendApi.get_cabaclubrankeventmaster(model_mgr, current_eventid, using=settings.DB_READONLY)
        if eventmaster is None:
            url = self.makeAppLinkUrlRedirect(UrlMaker.cabaclubtop())
            self.appRedirect(url)
            return

        self.html_param['cabaclub_management_info'] = self.get_cabaclub_management_info(self.getModelMgr(), v_player.id, OSAUtil.get_now())
        self.html_param['url_cabaclubrank'] = self.makeAppLinkUrl(UrlMaker.cabaclubrank(eventmaster.id))
        self.html_param['url_explain_detail'] = self.makeAppLinkUrl(UrlMaker.cabaclubrank(eventmaster.id, 'detail'))
        self.html_param['url_explain_prizes'] = self.makeAppLinkUrl(UrlMaker.cabaclubrank(eventmaster.id, 'prizes'))
        self.html_param['eventmaster'] = eventmaster
        event_config = BackendApi.get_current_cabaclubrankeventconfig(model_mgr, using=settings.DB_READONLY)
        self.set_event_period(model_mgr, self.html_param, event_config)

        table = {
            'detail': self.__proc_detail,
            'prizes': self.__proc_prizes,
        }
        func = table.get(ope)
        if func:
            func(eventmaster)
            return

        page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
        is_view_myrank = int(self.request.get(Defines.URLQUERY_FLAG) or 0) == 1
        has_next = False

        if not CabaClubRanking.exists(current_eventid):
            # if ranking data isn't present in Redis
            # fetch the ranking data from the database and store it into Redis
            BackendApi.backup_ranking_data_into_redis(current_eventid)

        if is_view_myrank:
            # fetch user rank data from Redis DB
            player_rank_list = CabaClubRanking.get_user_rank_page(current_eventid, v_player.id, Handler.CONTENT_NUM_PER_PAGE)
        else:
            offset = page * Handler.CONTENT_NUM_PER_PAGE
            # fetch all players' rank data from Redis DB
            player_rank_list = CabaClubRanking.get_rankings(current_eventid, offset, Handler.CONTENT_NUM_PER_PAGE, page)

        # base url
        urlbase = UrlMaker.cabaclubrank(current_eventid)
        if player_rank_list:
            self.setFromPage(Defines.FromPages.CABACLUB_STORE, current_eventid)
            uidlist = [x['uid'] for x in player_rank_list]
            playerlist = BackendApi.get_players(self, uidlist=uidlist, using=settings.DB_READONLY)
            obj_player_dict = dict([(obj_player['id'], obj_player) for obj_player in self.getObjPlayerList(playerlist, uidlist)])

            for rank_info in player_rank_list:
                uid = rank_info['uid']
                obj_player = obj_player_dict.get(uid)
                if obj_player:
                    obj_player['is_me'] = uid == v_player.id
                    rank_info.update(obj_player)

            if not is_view_myrank:
                number_of_players = CabaClubRanking.get_number_of_players(eventid=current_eventid)
                self.putPagenation(UrlMaker.cabaclubrank(current_eventid), page, number_of_players, Handler.CONTENT_NUM_PER_PAGE)

                if Handler.CONTENT_NUM_PER_PAGE == len(player_rank_list):
                    has_next = True

                # Next page url
                if has_next:
                    self.html_param['url_page_next'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_PAGE, page + 1))

                # Previous page url
                if 0 < page:
                    self.html_param['url_page_prev'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_PAGE, page - 1))

        url_ranking = OSAUtil.addQuery(urlbase, Defines.URLQUERY_FLAG, "0")
        url_myrank = OSAUtil.addQuery(urlbase, Defines.URLQUERY_FLAG, "1")
        self.html_param['url_ranking'] = self.makeAppLinkUrl(url_ranking)
        self.html_param['url_myrank'] = self.makeAppLinkUrl(url_myrank)
        self.html_param['is_view_myrank'] = is_view_myrank
        self.html_param['player_rank_list'] = player_rank_list
        self.html_param['cabaclub_management_info'] = self.get_cabaclub_management_info(self.getModelMgr(), v_player.id, OSAUtil.get_now())
        self.writeAppHtml('cabaclub/rank')

    def __proc_detail(self, eventmaster):
        self.writeAppHtml('cabaclub/detail')

    def __proc_prizes(self, eventmaster):
        prizedatalist = self.make_rankingprizelist(eventmaster.rankingprizes)
        self.html_param['rankingprizelist'] = prizedatalist
        self.writeAppHtml('cabaclub/prizes')

    def getObjPlayerList(self, playerlist, uidlist):
        obj_list = []
        if playerlist:
            model_mgr = self.getModelMgr()

            persons = BackendApi.get_dmmplayers(self, playerlist, using=settings.DB_READONLY, do_execute=True)
            leaders = BackendApi.get_leaders(uidlist, arg_model_mgr=model_mgr, using=settings.DB_READONLY)

            for player in playerlist:
                obj_player = Objects.player(self, player, persons.get(player.dmmid), leaders[player.id])
                obj_list.append(obj_player)

        return obj_list


def main(request):
    return Handler.run(request)
