# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerDeck,\
    PlayerRequest, PlayerGold, PlayerTreasure, PlayerCrossPromotion
from platinumegg.app.cabaret.models.Gacha import GachaBoxGachaDetailMaster
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import urllib
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
import settings
from platinumegg.app.cabaret.util.card import CardSet
from platinumegg.app.cabaret.util.gacha import GachaBox
from defines import Defines
from platinumegg.app.cabaret.util.present import PresentSet
from platinumegg.app.cabaret.models.View import CardMasterView
from platinumegg.app.cabaret.models.GachaExplain import GachaExplainMaster
from platinumegg.app.cabaret.util.redistradeshop import RedisPlayerTradeShopPoint

class Handler(GachaHandler):
    """引抜結果.
    """

    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGachaPt, PlayerDeck, PlayerRequest, PlayerGold, PlayerTreasure]

    def process(self):
        args = self.getUrlArgs('/gacharesult/')
        try:
            mid = int(args.get(0))
            key = urllib.unquote(args.get(1))
            code = int(args.get(2) or 0)
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        self.set_masterid(mid)

        self.__now = OSAUtil.get_now()

        v_player = self.getViewerPlayer()

        self.html_param['player'] = Objects.player(self, v_player)

        if code != 0:
            # エラーで引抜できなかった.
            self.procGachaError(code)
            return

        if v_player.req_alreadykey != key:
            # 結果が見当たらない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'結果を出せない')
            url = UrlMaker.gacha()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return

        gachamaster = self.getGachaMaster()
        playdata = self.getGachaPlayData()
        model_mgr = self.getModelMgr()

        CONTENT_NUM_PER_PAGE = 10
        PAGING_CONTENT_NUM = CONTENT_NUM_PER_PAGE + 2

        # 獲得したカード.
        resultlist = playdata.result['result'] if isinstance(playdata.result, dict) else playdata.result

        if PlayerCrossPromotion.is_session(): # if we are in a cross promotion event
            self.ssr_card_crosspromotion(v_player, resultlist)

        result_num = len(resultlist)
        page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
        if PAGING_CONTENT_NUM < result_num:
            # 結果が多いのでページング.
            url = UrlMaker.gacharesult(mid, key, code)
            self.putPagenation(url, page, result_num, CONTENT_NUM_PER_PAGE)

            start = page * CONTENT_NUM_PER_PAGE
            end = start + CONTENT_NUM_PER_PAGE
            self.html_param['is_paging'] = True
        else:
            start = 0
            end = result_num

        cardidlist = [data['id'] for data in resultlist[start:end]]
        cardmasters = BackendApi.get_cardmasters(cardidlist, model_mgr, using=settings.DB_READONLY)
        obj_cardlist = []
        point_single = 0
        sellprice_total = 0
        sellprice_treasure_total = 0
        sell_num = 0
        for idx, data in enumerate(resultlist):
            point = data['point']
            obj_card = None
            if start <= idx < end:
                master = cardmasters[data['id']]
                card = BackendApi.create_card_by_master(master)
                cardset = CardSet(card, master)
                obj_card = Objects.card(self, cardset, is_new=data['is_new'])
                obj_card['point'] = point
                obj_cardlist.append(obj_card)
            sellprice = data.get('sellprice', 0)
            sellprice_treasure = data.get('sellprice_treasure', 0)
            point_single += point
            if data.get('autosell'):
                if obj_card:
                    obj_card['autosell'] = True
                    obj_card['sellprice'] = sellprice
                    obj_card['sellprice_treasure'] = sellprice_treasure
                sell_num += 1
                sellprice_total += sellprice
                sellprice_treasure_total += sellprice_treasure

        point_total = 0
        if gachamaster.consumetype == Defines.GachaConsumeType.RANKING:
            rankingmaster = BackendApi.get_rankinggacha_master(model_mgr, gachamaster.boxid, using=settings.DB_READONLY)
            if rankingmaster and rankingmaster.is_support_totalranking:
                point_total = BackendApi.get_rankinggacha_total_score(playdata.mid, v_player.id)
        elif gachamaster.consumetype == Defines.GachaConsumeType.SR_SSR_PROBABILITY_UP or gachamaster.consumetype == Defines.GachaConsumeType.PTCHANGE:
            #トレードショップが開いていたら
            if gachamaster.trade_shop_master_id is not None and 0 < gachamaster.trade_shop_master_id:
                try:
                    lottery_point = int(args.get(3))
                except:
                    raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
                self.html_param['lottery_point'] = lottery_point
                self.html_param['user_point'] = BackendApi.get_tradeshop_userpoint(model_mgr, v_player.id)

        if gachamaster.consumetype in {Defines.GachaConsumeType.FIXEDSR, Defines.GachaConsumeType.STEPUP, Defines.GachaConsumeType.STEPUP2} and 0 < gachamaster.rarity_fixed_num:
            if page == 0:
                self.html_param['is_rarity_fixed'] = True
                self.html_param['rarity_fixed_cardlist'] = obj_cardlist[:gachamaster.rarity_fixed_num]
                self.html_param['cardlist'] = obj_cardlist[gachamaster.rarity_fixed_num:]
            else:
                self.html_param['is_rariry_fixed'] = False
                self.html_param['rarity_fixed_cardlist'] = obj_cardlist
                self.html_param['cardlist'] = obj_cardlist
        else:
            self.html_param['cardlist'] = obj_cardlist

        self.html_param['gacha_result_unique_name'] = gachamaster.unique_name
        self.html_param['point_single'] = point_single
        self.html_param['point_total'] = point_total
        self.html_param['_card_num'] = sell_num
        self.html_param['_gold_add'] = sellprice_total
        self.html_param['_ckt'] = sellprice_treasure_total
        self.html_param['url_tradeshop'] = self.makeAppLinkUrl(UrlMaker.tradeshop())
        # 引き抜きガチャチケット消費数.
        self.html_param['gacha_ticket_cost'] = Defines.GACHA_TICKET_COST_NUM

        # 開催中のガチャ情報.
        topic = Defines.GachaConsumeType.TO_TOPIC.get(gachamaster.consumetype)
        self.putOpenGachaList(topic, gachamaster)

        # シート情報.
        seatinfo = BackendApi.make_gachaseatinfo(self, v_player.id, gachamaster, result=True, using=settings.DB_READONLY)
        self.html_param['gachaseatinfo'] = seatinfo

        # おまけ等.
        omakelist = []
        if seatinfo and seatinfo['last']:
            omakelist.append('%s%s' % (seatinfo['last']['name'], seatinfo['last']['numtext']))
        if isinstance(playdata.result, dict) and playdata.result.get('omake'):
            prizelist = BackendApi.get_prizelist(model_mgr, playdata.result['omake'], using=settings.DB_READONLY)
            presentlist = BackendApi.create_present_by_prize(model_mgr, v_player.id, prizelist, 0, using=settings.DB_READONLY, do_set_save=False)
            presentsetlist = PresentSet.presentToPresentSet(model_mgr, presentlist, using=settings.DB_READONLY)
            for presentset in presentsetlist:
                omakelist.append('%s%s' % (presentset.itemname, presentset.numtext_with_x))
        self.html_param['omakelist'] = omakelist

        seatPlayData = self.__get_seatPlayData_only_firstRound_and_last(model_mgr, v_player.id, gachamaster)
        if seatPlayData:
            for i, seat in enumerate(seatinfo["list"]):
                if seat == None:
                    continue
                if i == seatPlayData.last:
                    seat["last"] = True
                else:
                    seat["last"] = False
            itemhash = seatinfo["list"][seatPlayData.last]
            omakelist[0] = '%s%s' % (itemhash['name'], itemhash['numtext'])

        boxgachaprizes = []
        # 条件付きリセット可能BOXガチャの引き切り報酬
        if gachamaster.consumetype in {Defines.GachaConsumeType.LIMITED_RESET_BOX, Defines.GachaConsumeType.EVENTTICKET}:
            boxgacha = GachaBox(gachamaster, playdata)
            if boxgacha.is_empty:
                boxdetail = model_mgr.get_model(GachaBoxGachaDetailMaster, gachamaster.id, using=settings.DB_READONLY)
                prizelist = BackendApi.get_prizemaster_list(model_mgr, boxdetail.prizelist)
                presentlist = BackendApi.create_present_by_prize(model_mgr, v_player.id, prizelist, 0, using=settings.DB_READONLY, do_set_save=False)
                presentsetlist = PresentSet.presentToPresentSet(model_mgr, presentlist, using=settings.DB_READONLY)
                for presentset in presentsetlist:
                    boxgachaprizes.append('%s%s' % (presentset.itemname, presentset.numtext_with_x))
                self.html_param['boxgachaprizes'] = boxgachaprizes
        # ガチャ確率 UP の場合最後に引いたガチャをサジェストする
        if gachamaster.consumetype in {Defines.GachaConsumeType.SR_SSR_PROBABILITY_UP,
                                       Defines.GachaConsumeType.FIXEDSR,
                                       Defines.GachaConsumeType.PTCHANGE,
                                       Defines.GachaConsumeType.NEWSTORE_SUPPORT_PREMIUM}:
            self.put_gacha_probability(gachamaster)

        self.html_param['explain_text'] = self.html_param["gachadata"].values()[0]['explain_text']
        self.writeAppHtml('gacha/result')

    def __get_seatPlayData_only_firstRound_and_last(self, model_mgr, uid, gachamaster):
        seatmodels = self.getSeatModels(True)
        seatplaydata = seatmodels.get('playdata')
        playcount = seatmodels.get('playcount')

        if seatplaydata is not None and playcount is not None and seatplaydata.is_first() and 0 < playcount.lap:
            tableid = gachamaster.seattableid
            tablemaster = BackendApi.get_gachaseattablemaster(model_mgr, tableid, using=settings.DB_DEFAULT)
            oldlap_mid = tablemaster.getSeatId(playcount.lap)
            playdata = BackendApi.get_gachaseatplaydata(model_mgr, uid, [oldlap_mid], get_instance=True, using=settings.DB_DEFAULT).get(oldlap_mid)
            return playdata
        else:
            return None

    def procGachaError(self, code):
        if code == CabaretError.Code.NOT_ENOUGH:
            # 足りない..
            self.writeAppHtml('gacha/error_not_enough')
        elif code == CabaretError.Code.OVER_LIMIT:
            # 足りない..
            self.writeAppHtml('gacha/error_overlimit')
        else:
            # その他エラー.
            raise CabaretError(u'引抜に失敗しました.', code)

    def put_gacha_probability(self, gachamaster):
        self.html_param['lastgacha_unique_name'] = gachamaster.unique_name

    def ssr_card_crosspromotion(self, player, resultlist):
        """ If the player acquires an SSR card add the player to the PlayerCrossPromotion table
            and set is_acquired_ssr_card to True (i.e 1)
        """
        model_mgr = self.getModelMgr()
        idlist = [result['id'] for result in resultlist]
        cardmasterviews = CardMasterView.fetchValues(filters={'id__in': idlist})
        rarity_set = set([view.rare for view in cardmasterviews])

        if Defines.Rarity.SPECIALSUPERRARE in rarity_set:
            player_crosspromo = model_mgr.get_model(PlayerCrossPromotion, player.id)
            if player_crosspromo is None or not player_crosspromo.is_acquired_ssr_card:
                def forUpdate(model, inserted):
                    model.is_acquired_ssr_card = True
                model_mgr.add_forupdate_task(PlayerCrossPromotion, player.id, forUpdate)

        model_mgr.write_all()
        model_mgr.write_end()


def main(request):
    return Handler.run(request)
