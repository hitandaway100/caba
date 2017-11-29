# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerLogin, PlayerRegist,\
    PlayerTutorial, PlayerExp, PlayerGold, PlayerAp, PlayerDeck, PlayerFriend,\
    PlayerGachaPt, PlayerRequest, PlayerDXPWallConversion
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.dxp import DXPAPI
import random
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
import settings_sub
from platinumegg.app.cabaret.util.mission import PanelMissionConditionExecuter
from platinumegg.app.cabaret.util.happening import HappeningUtil
from platinumegg.app.cabaret.models.LevelUpBonus import LevelUpBonusMaster, LevelUpBonusPlayerData
from collections import namedtuple
from platinumegg.app.cabaret.models.UserLog import UserLogLevelUpBonus

class Handler(AppHandler):
    """マイページ.
    表示するもの.
        プレイヤー情報.
        リーダーカードの情報.
        カード所持数.
        フレンド数.
        フレンド申請件数.
        無料ガチャを引けるか.
        プレゼント件数.
        フレンドの近況.
        フレンド承認されたか.
        行動履歴.
        あいさつ履歴.
        バナー.
    書き込み.
        フレンド数.
        DXPコンバージョン.
        DXPインセンティブ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [
            PlayerRegist,
            PlayerTutorial,
            PlayerExp,
            PlayerGold,
            PlayerAp,
            PlayerDeck,
            PlayerFriend,
            PlayerGachaPt,
            PlayerLogin,
            PlayerRequest,
        ]
    
    @classmethod
    def doUpdateLoginTime(cls):
        return True
    
    def process(self):
        self.setFromPage(None)
        
        model_mgr = self.getModelMgr()
        
        v_player = self.getViewerPlayer()
        if not BackendApi.check_loginbonus_received(v_player.getModel(PlayerLogin)):
            if not settings_sub.IS_BENCH:
                # ログインボーナスを受け取っていない.
                url = UrlMaker.loginbonus()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        elif BackendApi.check_lead_loginbonustimelimited(model_mgr, v_player.id):
            if not settings_sub.IS_BENCH:
                # ロングログインボーナスを受け取っていない.
                url = UrlMaker.loginbonustimelimiteddo()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        elif BackendApi.check_lead_loginbonus_sugoroku(model_mgr, v_player.id):
            if not settings_sub.IS_BENCH:
                # 双六ログインボーナスを受け取っていない.
                url = UrlMaker.loginbonussugorokudo()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        elif BackendApi.check_raidevent_lead_opening(model_mgr, v_player.id, using=settings.DB_READONLY):
            if not settings_sub.IS_BENCH and not (settings_sub.IS_LOCAL and self.request.get('_test')):
                # イベントOPを見ないといけない.
                url = UrlMaker.raidevent_opening()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        elif BackendApi.check_raidevent_lead_bigboss(model_mgr, v_player.id, using=settings.DB_READONLY):
            if not settings_sub.IS_BENCH and not (settings_sub.IS_LOCAL and self.request.get('_test')):
                # 大ボス演出を見ないといけない.
                url = UrlMaker.raidevent_bigboss()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        elif BackendApi.check_raidevent_lead_epilogue(model_mgr, v_player.id, using=settings.DB_READONLY):
            if not settings_sub.IS_BENCH and not (settings_sub.IS_LOCAL and self.request.get('_test')):
                # イベントEDを見ないといけない.
                url = UrlMaker.raidevent_epilogue()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        elif BackendApi.check_scoutevent_lead_opening(model_mgr, v_player.id, using=settings.DB_READONLY):
            if not settings_sub.IS_BENCH and not (settings_sub.IS_LOCAL and self.request.get('_test')):
                # イベントOPを見ないといけない.
                url = UrlMaker.scoutevent_opening()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        elif BackendApi.check_scoutevent_lead_epilogue(model_mgr, v_player.id, using=settings.DB_READONLY):
            if not settings_sub.IS_BENCH and not (settings_sub.IS_LOCAL and self.request.get('_test')):
                # イベントEDを見ないといけない.
                url = UrlMaker.scoutevent_epilogue()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        elif BackendApi.check_battleevent_lead_opening(model_mgr, v_player.id, using=settings.DB_READONLY):
            if not settings_sub.IS_BENCH and not (settings_sub.IS_LOCAL and self.request.get('_test')):
                # イベントOPを見ないといけない.
                url = UrlMaker.battleevent_opening()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        elif BackendApi.check_battleevent_lead_scenario(model_mgr, v_player.id, using=settings.DB_READONLY):
            if not settings_sub.IS_BENCH and not (settings_sub.IS_LOCAL and self.request.get('_test')):
                # 中押し演出を見ていない.
                url = UrlMaker.battleevent_scenario()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return False
        elif BackendApi.check_battleevent_lead_epilogue(model_mgr, v_player.id, using=settings.DB_READONLY):
            if not settings_sub.IS_BENCH and not (settings_sub.IS_LOCAL and self.request.get('_test')):
                # イベントエピローグを見ないといけない.
                url = UrlMaker.battleevent_epilogue()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        elif BackendApi.check_produceevent_lead_opening(model_mgr, v_player.id, using=settings.DB_READONLY):
            if not settings_sub.IS_BENCH and not (settings_sub.IS_LOCAL and self.request.get('_test')):
                # イベントOPを見ないといけない.
                url = UrlMaker.produceevent_opening()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        elif BackendApi.check_produceevent_lead_epilogue(model_mgr, v_player.id, using=settings.DB_READONLY):
            if not settings_sub.IS_BENCH and not (settings_sub.IS_LOCAL and self.request.get('_test')):
                # イベントEDを見ないといけない.
                url = UrlMaker.produceevent_epilogue()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        elif BackendApi.check_cabaclub_lead_resultanim(model_mgr, v_player.id, OSAUtil.get_now(), using=settings.DB_READONLY):
            if not settings_sub.IS_BENCH and not (settings_sub.IS_LOCAL and self.request.get('_test')):
                # 店舗結果演出へ.
                self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubresultanim(), add_frompage=False))
                return
        
        self.__news_num = 0
        
        self.checkPanelMission()
        if self.response.isEnd:
            return
        
        self.procRankingGacha()
        self.checkPresentEveryone()
        self.checkLevelUpBonus()
        self.putCardInfo()
        self.putFriendNum()
        self.putFriendRequestNum()
        self.putFreeGachaFlag()
        self.putPresentNum()
        self.putFriendLog()
        self.putFriendAcceptNum()
        self.putProduceInfo()
        self.putHappeningInfo()
        self.prepareRaidLog()
        self.putInfomations()
        self.putGreetLog()
        self.putBanner()
        self.putCabaClubInfo()
        self.putTitleInfo()
        self.putPlayerInfo()
        self.putRaidLog()
        
        self.checkPaymentRecord()
        
        self.tradeScoutGum()
        
        if self.is_active_dxp():
            self.check_offerwall(model_mgr, v_player)

        self.html_param['news_num'] = self.__news_num
        
        self.html_param['profile_tag'] = self.makeProfileTag(v_player.id)
        
        self.html_param['url_infospace'] = u'%s#infospace' % self.makeAppLinkUrl(UrlMaker.mypage())
        
        if self.is_active_dxp() and not self.is_pc:
            self.html_param['url_offerwall'] = DXPAPI(is_rel=self.is_rel).offerwall_url(self.app_id, v_player.dmmid)
            self.html_param['url_offerwallR18'] = DXPAPI(is_rel=self.is_rel,is_R18=True).offerwall_url(self.app_id, v_player.dmmid)
        print DXPAPI(is_rel=self.is_rel).offerwall_url(self.app_id, v_player.dmmid)
        print DXPAPI(is_rel=self.is_rel,is_R18=True).offerwall_url(self.app_id, v_player.dmmid)
        self.putPopupBanner()
        
        self.writeAppHtml('mypage')

    def check_offerwall(self, model_mgr, v_player):
        # DXP OfferWall.
        dxpdata = BackendApi.get_model(model_mgr, PlayerDXPWallConversion, v_player.id, using=settings.DB_READONLY)
        if self.check_incentive(dxpdata, v_player.level) and dxpdata.is_received is False:
            
            # incentive を設定する.
            dxpapi = DXPAPI(is_rel=self.is_rel)
            conversion_id = dxpapi.get_wall_conversion(self.app_id, v_player.dmmid)

            if dxpdata.is_set_conversion is False and conversion_id:
                set_conversion_result = dxpapi.set_wall_conversion(conversion_id)
            elif dxpdata.is_set_conversion:
                set_conversion_result = dxpdata.is_set_conversion
            else:
                set_conversion_result = False
            
            if dxpdata.is_set_incentive is False:
                set_incentive_result = self.set_incentive(dxpapi, conversion_id)
            elif dxpdata.is_set_incentive:
                set_incentive_result = dxpdata.is_set_incentive
            else:
                set_incentive_result = False

            incentive_ok = None
            if (dxpdata.is_set_incentive or set_incentive_result) and \
               dxpdata.is_prize_incentive is False:
                incentive_ok = self.get_incentive(dxpapi, self.app_id, v_player.dmmid)

            if incentive_ok is not None:
                db_util.run_in_transaction(self.tr_incentive, v_player.id, set_conversion_result, set_incentive_result, incentive_ok)
            elif incentive_ok is None and (dxpdata.is_set_conversion or set_incentive_result) \
                and dxpdata.is_received is False:
                db_util.run_in_transaction(self.tr_incentive, v_player.id, set_conversion_result, set_incentive_result, True)

    def procRankingGacha(self):
        """ランキングガチャ.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 受け取った総計pt報酬IDを取得.
        wholeprize_data = BackendApi.get_rankinggacha_wholeprize_data(model_mgr, uid, using=settings.DB_READONLY)
        if wholeprize_data is None:
            # Noneなら終了.
            return
        
        # 受け取った総計pt報酬IDより大きいIDの配布用キューを取得.
        queueid = wholeprize_data.queueid
        queuelist = BackendApi.get_rankinggacha_wholeprize_queue_not_received(model_mgr, queueid, using=settings.DB_READONLY)
        if not queuelist:
            # 無ければ終了.
            return
        
        # 配布用キューのboxIDからboxを初めてプレイした時の総計ptを取得.
        boxidlist = list(set([queue.boxid for queue in queuelist]))
        scoredata_dict = BackendApi.get_rankinggacha_scoredata_dict(model_mgr, uid, boxidlist, using=settings.DB_READONLY)
        
        # 配布用キューの中から総計ptが初めてプレイした時の総計pt以上のものを抽出.
        queuelist = [queue for queue in queuelist if scoredata_dict.get(queue.boxid) and scoredata_dict[queue.boxid].firstpoint <= queue.point]
        
        # ランキングガチャマスターを取得. -> dict.
        rankingmaster_dict = BackendApi.get_rankinggacha_master_dict(model_mgr, boxidlist, using=settings.DB_READONLY)
        
        try:
            db_util.run_in_transaction(Handler.__tr_write_rankinggacha_wholeprize_receive, uid, queuelist, rankingmaster_dict).write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
    
    @staticmethod
    def __tr_write_rankinggacha_wholeprize_receive(uid, queuelist, rankingmaster_dict):
        """総計pt報酬受け取り
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_rankinggacha_receive_wholeprize(model_mgr, uid, queuelist, rankingmaster_dict)
        model_mgr.write_all()
        return model_mgr
    
    def putPopupBanner(self):
        """ポップアップの埋め込み.
        """
        v_player = self.getViewerPlayer()
        uid = v_player.id
        popupbanner_list = BackendApi.get_popupbanners(self, uid, using=settings.DB_READONLY)
        
        obj_popupbanner_list = [Objects.popup(self, popupbanner)['url_flag'] for popupbanner in popupbanner_list]
        self.html_param['popupbanner_list'] = obj_popupbanner_list
    
    def checkPresentEveryone(self):
        """全プレ確認.
        """
        now = OSAUtil.get_now()
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        masterlist = BackendApi.get_presenteveryone_list_formypage(model_mgr, using=settings.DB_READONLY, now=now)
        if masterlist:
#            player_regist=v_player.getModel(PlayerRegist)
#            schedulemaster = BackendApi.get_schedule_master(model_mgr, masterlist[0].schedule, using=settings.DB_READONLY)
#            starttime, endtime = BackendApi.get_schedule_start_end_time(schedulemaster)
#            if starttime < player_regist.ctime:
#                return   
            flagmodels = BackendApi.get_presenteveryone_mypage_receiveflags(model_mgr, v_player.id, [master.id for master in masterlist], using=settings.DB_READONLY)
            target_masterlist = [master for master in masterlist if not BackendApi.check_presenteveryone_received(master, flagmodels.get(master.id), now)]
            if target_masterlist:
                try:
                    model_mgr = db_util.run_in_transaction(Handler.tr_write_presenteveryone, v_player, masterlist, now, v_player.req_confirmkey)
                    model_mgr.write_end()
                except CabaretError, err:
                    if err.code == CabaretError.Code.ALREADY_RECEIVED:
                        pass
                    else:
                        raise

    def checkLevelUpBonus(self):
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        midlist = BackendApi.get_levelupbonus_master(model_mgr, Defines.LEVELUP_BONUS_VERSION, using=settings.DB_DEFAULT)
        levelupbonus_masters = BackendApi.get_model_list(model_mgr, LevelUpBonusMaster, midlist, using=settings.DB_DEFAULT)

        key = LevelUpBonusPlayerData.makeID(v_player.id, Defines.LEVELUP_BONUS_VERSION)
        playerdata = model_mgr.get_model(LevelUpBonusPlayerData, key)
        if playerdata is None:
            playerdata = LevelUpBonusPlayerData.createInstance(key)

        levelup_bonus_logs = []
        prizelistdata = []
        PrizelistData = namedtuple('PrizelistData', ('prizelist', 'text'))
        for levelupbonus_master in levelupbonus_masters:
            if playerdata.last_prize_level < levelupbonus_master.level and levelupbonus_master.level <= v_player.level:
                prizelist = BackendApi.get_prizelist(model_mgr, levelupbonus_master.prize_id, using=settings.DB_READONLY)
                prizelistdata.append(PrizelistData(prizelist, levelupbonus_master.levelupbonus_text))
                levelup_bonus_logs.append(UserLogLevelUpBonus.create(v_player.id, levelupbonus_master.version, levelupbonus_master.prize_id, levelupbonus_master.level))
                playerdata.last_prize_level = levelupbonus_master.level

        db_util.run_in_transaction(self.__checkLevelUpBonus_tr_write, prizelistdata, levelup_bonus_logs, playerdata)

    def __checkLevelUpBonus_tr_write(self, prizelistdata, levelup_bonus_logs, playerdata):
        model_mgr = ModelRequestMgr()

        for prizelist_data in prizelistdata:
            BackendApi.tr_add_prize(model_mgr, playerdata.uid, prizelist_data.prizelist, prizelist_data.text)
        for levelup_prize_log in levelup_bonus_logs:
            model_mgr.set_save(levelup_prize_log)
        model_mgr.set_save(playerdata)

        model_mgr.write_all()
        model_mgr.write_end()

    def checkPanelMission(self):
        """パネルミッション確認.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        now = OSAUtil.get_now()
        
        # ミッション情報.
        missionplaydata = BackendApi.get_current_panelmission_data(model_mgr, uid, using=settings.DB_READONLY)
        if missionplaydata is None:
            # 全て終わっている.
            return
        
        panel = missionplaydata.mid
        
        # マイページで確認するミッション.
        mission_executer = PanelMissionConditionExecuter()
        
        # 更新確認.
        is_update = BackendApi.check_lead_update_panelmission(model_mgr, v_player, panel, now, mission_executer, using=settings.DB_READONLY)
        
        if is_update:
            try:
                model_mgr = db_util.run_in_transaction(self.tr_write_panelmission, uid, panel, mission_executer, v_player.req_confirmkey, now)
                model_mgr.write_end()
            except:
                return
            if not (settings_sub.IS_LOCAL and self.request.get('_test')):
                # 演出へリダイレクト.
                url = UrlMaker.panelmissionanim(panel)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    @staticmethod
    def tr_write_panelmission(uid, panel, mission_executer, confirmkey, now):
        """パネルミッション書き込み.
        """
        model_mgr = ModelRequestMgr()
        
        if mission_executer.isNeedCheck():
            # 達成書き込み.
            BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer, now)
        # 報酬書き込み.
        BackendApi.tr_receive_panelmission(model_mgr, uid, panel, confirmkey, now)
        
        model_mgr.write_all()
        
        return model_mgr
    
    @staticmethod
    def tr_write_presenteveryone(uid, masterlist, now, confirmkey):
        """全プレ書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_receive_presenteveryone(model_mgr, uid, masterlist, now, confirmkey)
        model_mgr.write_all()
        return model_mgr
    
    def putInfomations(self):
        """お知らせ.
        """
        infomations, _ = BackendApi.get_infomations(self, 0, using=settings.DB_READONLY)
        if 0 < len(infomations):
            arr = []
            date_new = None
            for infomation in infomations[:2]:
                obj = Objects.infomation(self, infomation)
                date_new = date_new or obj['date']
                obj['is_new'] = date_new == obj['date']
                arr.append(obj)
            self.html_param['infomations'] = arr
    
    def putPlayerInfo(self):
        """プレイヤー情報.
        """
        v_player = self.getViewerPlayer()
        person = BackendApi.get_dmmplayers(self, [v_player], using=settings.DB_READONLY).get(v_player.dmmid)
        self.html_param['player'] = Objects.player(self, v_player, person)
    
    def putCardInfo(self):
        """カードの情報.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        deck = BackendApi.get_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
        cardlist = BackendApi.get_cards(deck.to_array(), model_mgr, using=settings.DB_READONLY)
        
        # 接客力の合計.
        power_total = 0
        for card in cardlist:
            power_total += card.power
        self.html_param['power_total'] = power_total
        
        # デッキのカードをランダムで表示.
        disp_members = cardlist[:]
        random.shuffle(disp_members)
        cardset = disp_members[0]
        self.html_param['card'] = Objects.card(self, cardset, deck)
        
        # カード枚数.
        self.html_param['card_num'] = BackendApi.get_cardnum(v_player.id, model_mgr, using=settings.DB_READONLY)
    
    def putFriendNum(self):
        """フレンド数.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        friend_num = BackendApi.get_friend_num(v_player.id, model_mgr, using=settings.DB_READONLY)
        self.html_param['friend_num'] = friend_num
        if friend_num != v_player.friendnum:
            def tr():
                model_mgr = ModelRequestMgr()
                playerfriend = model_mgr.get_model(PlayerFriend, v_player.id)
                playerfriend.friendnum = friend_num
                model_mgr.set_save(playerfriend)
                model_mgr.write_all()
                return model_mgr, playerfriend
            model_mgr, playerfriend = db_util.run_in_transaction(tr)
            model_mgr.write_end()
            v_player.setModel(playerfriend)
        
    
    def putFriendRequestNum(self):
        """フレンド申請件数.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        num = BackendApi.get_friendrequest_receive_num(v_player.id, model_mgr, using=settings.DB_READONLY)
        self.html_param['friendrequest_num'] = num
        if 0 < num:
            self.__news_num += 1
        url = OSAUtil.addQuery(UrlMaker.friendlist(), Defines.URLQUERY_STATE, Defines.FriendState.RECEIVE)
        self.html_param['url_friendrequest_receive'] = self.makeAppLinkUrl(url)
    
    def putFreeGachaFlag(self):
        """無料ガチャを引けるか.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        lasttime = BackendApi.get_freegachalasttime(v_player.id, model_mgr, using=settings.DB_READONLY)
        if not DateTimeUtil.judgeSameDays(OSAUtil.get_now(), lasttime):
            self.html_param['free_gacha'] = 1
            self.__news_num += 1
            url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.FREE)
            self.html_param['url_gacha'] = self.makeAppLinkUrl(url)
    
    def putPresentNum(self):
        """プレゼント件数.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        num = BackendApi.get_present_num(v_player.id, model_mgr, using=settings.DB_READONLY)
        self.html_param['present_num'] = num
        if 0 < num:
            self.__news_num += 1
    
    def putFriendLog(self):
        """フレンドの近況.
        """
        NUM = 2
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        self.html_param['friendlog_list'] = BackendApi.get_friendlog_list(self, v_player.id, limit=NUM, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
    
    def putFriendAcceptNum(self):
        """フレンド承認された数.
        """
        v_player = self.getViewerPlayer()
        num = BackendApi.get_friendaccept_num(v_player.id, using=settings.DB_READONLY)
        BackendApi.delete_friendaccept_num(v_player.id, using=settings.DB_READONLY)
        self.html_param['friendaccept_num'] = num
        if 0 < num:
            self.__news_num += 1

    def putProduceInfo(self):
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        cur_eventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=settings.DB_READONLY)
        current_happening = BackendApi.get_current_producehappening(model_mgr, v_player.id, using=settings.DB_READONLY)
        is_open = cur_eventmaster and current_happening and current_happening.happening.state == Defines.HappeningState.BOSS

        self.html_param['produce_happeninginfo'] = {
            'is_open' : is_open,
            'url' : self.makeAppLinkUrl(UrlMaker.produceevent_top()),
        }

    def putHappeningInfo(self):
        """ハプニングとレイドの発生チェック.
        """
        model_mgr = self.getModelMgr()
        cur_eventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
        
        v_player = self.getViewerPlayer()
        # 自分の.
        cur_happeningset = BackendApi.get_current_happening(model_mgr, v_player.id, using=settings.DB_READONLY)
        if cur_happeningset and not cur_happeningset.happening.is_end():
            is_event = cur_eventmaster and cur_eventmaster.id == HappeningUtil.get_raideventid(cur_happeningset.happening.event)
            happeninginfo = None
            timellimit = None
            if cur_happeningset.happening.is_cleared():
                # クリア済み.
                happeninginfo = 'cleared'
                if is_event:
                    url = UrlMaker.raidresultanim(cur_happeningset.happening.id)
                else:
                    url = UrlMaker.raidend(cur_happeningset.happening.id)
                self.__news_num += 1
            elif cur_happeningset.happening.is_boss_appeared():
                # レイド発生中.
                happeninginfo = 'bossappeared'
                if is_event:
                    url = UrlMaker.raidevent_battlepre()
                else:
                    url = UrlMaker.happening()
                timellimit = Objects.timelimit(cur_happeningset.happening.etime, OSAUtil.get_now())
            else:
                # ハプニング中.
                happeninginfo = 'open'
                url = UrlMaker.happening()
                timellimit = Objects.timelimit(cur_happeningset.happening.happening.etime, OSAUtil.get_now())
            self.html_param['happeninginfo'] = {
                'info' : happeninginfo,
                'timelimit' : timellimit,
                'url' : self.makeAppLinkUrl(url),
                'is_event' : is_event,
            }
        
        # 救援.
        helpnum = BackendApi.get_raidhelp_num(model_mgr, v_player.id, using=settings.DB_READONLY, nummax=Defines.RAIDHELP_LIST_MAXLENGTH)
        if cur_eventmaster:
            url = None
            if 0 < helpnum:
                raidhelpidlist = BackendApi.get_raidhelpidlist(model_mgr, v_player.id, limit=min(5, helpnum), offset=0, using=settings.DB_READONLY)
                if raidhelpidlist:
                    raidhelplist = BackendApi.get_raidhelplist(model_mgr, raidhelpidlist, using=settings.DB_READONLY)
                    helpnum = len(raidhelplist)
                    if helpnum == 1:
                        url = UrlMaker.raidhelpdetail(raidhelplist[0].raidid)
                else:
                    helpnum = 0
            if url is None:
                url = OSAUtil.addQuery(UrlMaker.raidevent_helplist(), Defines.URLQUERY_FLAG, '_mypage')
            is_event_opened = True
        else:
            url = UrlMaker.happening()
            is_event_opened = False
        self.html_param['raidhelpnuminfo'] = {
            'num' : helpnum,
            'url' : self.makeAppLinkUrl(url),
        }
        self.html_param['is_event_opened'] = is_event_opened
        
        # 救援成功通知.
        if BackendApi.get_raidlog_notification_num(v_player.id):
            # 救援成功したらしい.
            self.html_param['raidhelp_notification'] = True
            self.__news_num += 1
    
    def prepareRaidLog(self):
        """レイド履歴.
        """
        NUM = 2
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        raidlogidlist = BackendApi.get_raidlog_idlist(model_mgr, v_player.id, 0, NUM, using=settings.DB_READONLY)
        raidloglist = BackendApi.get_raidlogs(model_mgr, raidlogidlist, using=settings.DB_READONLY).values()
        cb = BackendApi.put_list_raidlog_obj(self, raidloglist)
        self.__raidlog_callback = cb
    
    def putRaidLog(self):
        """レイド履歴.
        """
        self.__raidlog_callback()
    
    def checkPaymentRecord(self):
        """課金履歴.
        """
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        kind = BackendApi.check_payment_lostrecords(uid)
        if kind in ('gacha', 'shop'):
            # 課金履歴へのリンク.
            url = OSAUtil.addQuery(UrlMaker.support_paymentlist(), '_kind', kind)
            self.html_param['url_recov_payment'] = self.makeAppLinkUrl(url)
            self.__news_num += 1
    
    def putGreetLog(self):
        """あいさつ履歴.
        """
        NUM = 2
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        # 余分なあいさつ履歴を削除.
        BackendApi.delete_extra_greetlog(model_mgr, v_player.id)
        
        self.html_param['greetlog_list'] = BackendApi.get_greetlog_list(self, v_player.id, limit=NUM, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
    
    def putBanner(self):
        """バナー.
        """
        # スライドバナー.
        slidebanners = BackendApi.get_topbanners(self, using=settings.DB_READONLY)
        obj_slidebanners = []
        for banner in slidebanners:
            obj_banner = Objects.topbanner(self, banner)
            if not obj_banner['is_external_link']:
                # 外部リンクじゃない時だけにしておく.
                obj_slidebanners.append(obj_banner)
        self.html_param['slidebanners'] = obj_slidebanners
        
        # イベント.
        self.html_param['groups'] = BackendApi.get_tabeventbanners(self, using=settings.DB_READONLY)
    
    def putCabaClubInfo(self):
        """経営情報.
        """
        model_mgr = self.getModelMgr()
        if not BackendApi.get_cabaretclub_store_master_all(model_mgr, using=settings.DB_READONLY):
            # 店舗が無い.
            self.html_param['cabaclub_notfound'] = True
            return
        
        now = OSAUtil.get_now()
        # ユーザID取得.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # まず更新.
        BackendApi.update_cabaretclubstore(model_mgr, uid, now)
        # 店舗のイベント発生情報.
        BackendApi.put_cabaretclub_eventinfo(self, uid, now, using=settings.DB_READONLY)
    
    def putTitleInfo(self):
        """称号情報を設定.
        """
        model_mgr = self.getModelMgr()
        now = OSAUtil.get_now()
        # ユーザID取得.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # 称号.
        titleset = BackendApi.get_current_title_set(model_mgr, uid, now, using=settings.DB_READONLY)
        if titleset:
            self.html_param['title'] = Objects.title(self, titleset.master, titleset.playerdata, now=now)
    
    def tradeScoutGum(self):
        """スカウトガム交換.
        """
        model_mgr = self.getModelMgr()
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY)
        if eventmaster is not None:
            return
        v_player = self.getViewerPlayer()
        mid = Defines.ItemEffect.SCOUT_GUM
        num = BackendApi.get_item_nums(model_mgr, v_player.id, [mid], using=settings.DB_READONLY).get(mid, 0)
        if num <= 0:
            return
        
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY, check_schedule=False)
        if eventmaster is None:
            return
        elif eventmaster.gumtradeitem == 0:
            return
        
        def tr_gum():
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_item(model_mgr, v_player.id, eventmaster.gumtradeitem, num)
            BackendApi.tr_add_item(model_mgr, v_player.id, mid, -num, do_check_mission=False)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr_gum)
        model_mgr.write_end()

    def check_incentive(self, dxpdata, level):
        if dxpdata is not None:
            condition = Defines.DXP.get_incentive_level <= level
        else:
            condition = None
        return condition

    def set_incentive(self, dxpapi, conversion_id):
        result = None
        if conversion_id:
            result = dxpapi.set_incentive(conversion_id)

        if result is None:
            result = False
        return result

    def get_incentive(self, dxpapi, app_id, dmm_id):
        try:
            result = dxpapi.get_icentive(app_id, dmm_id)
        except:
            result = None
        return result

    def tr_incentive(self, uid, is_set_conversion, is_set_incentive, is_prize_incentive):
        model_mgr = ModelRequestMgr()

        def forUpdateIncentive(model, inserted, is_received):
            model.is_set_conversion = is_set_conversion
            model.is_set_incentive = is_set_incentive
            model.is_prize_incentive = is_prize_incentive
            model.is_received = is_received

        if is_set_conversion and is_set_incentive and is_prize_incentive:
            prizelist = BackendApi.get_prizelist(model_mgr, [Defines.DXP.insentive_prize_masterid])
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, Defines.DXP.textid)
            is_received = True
        else:
            is_received = False

        model_mgr.add_forupdate_task(PlayerDXPWallConversion, uid, forUpdateIncentive, is_received)
        model_mgr.write_all()
        model_mgr.write_end()

def main(request):
    return Handler.run(request)
