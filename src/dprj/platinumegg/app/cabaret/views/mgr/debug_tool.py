# -*- coding: utf-8 -*-

import settings
import settings_sub

from django.core import management
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Player import Player,\
    PlayerExp, PlayerGold, PlayerAp, PlayerDeck, PlayerFriend,\
    PlayerGachaPt, PlayerTreasure, PlayerLogin, PlayerCard, PlayerKey, PlayerTradeShop
from platinumegg.app.cabaret.util.api import BackendApi
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.lib.opensocial.util import OSAUtil
import datetime
from platinumegg.app.cabaret.models.Greet import GreetPlayerData
from platinumegg.app.cabaret.models.Scout import ScoutMaster, ScoutPlayData
from platinumegg.app.cabaret.models.Happening import HappeningMaster, Happening,\
    RaidMaster, RaidDestroyCount
from platinumegg.app.cabaret.models.Item import ItemMaster, Item
from platinumegg.app.cabaret.models.Card import CardMaster, Card,\
    CardAcquisition, AlbumAcquisition, CardStock
from platinumegg.app.cabaret.util.present import PrizeData
from platinumegg.app.cabaret.util.redisdb import RedisModel, LastViewArea,\
    RaidEventRanking, ScoutEventRanking, BattleEventRanking,\
    ScoutEventRankingBeginer, RaidEventRankingBeginer, BattleEventRankingBeginer,\
    PopupResetTime, RankingGachaSingleRanking, RankingGachaTotalRanking,\
    PopupViewTime
from platinumegg.app.cabaret.models.Area import AreaPlayData
from platinumegg.app.cabaret.models.Battle import BattleRankMaster
from platinumegg.app.cabaret.util.happening import HappeningSet, HappeningUtil
from platinumegg.app.cabaret.util.treasure import TreasureUtil
from platinumegg.app.cabaret.models.Treasure import TreasureGoldMaster,\
    TreasureBronzeMaster, TreasureSilverMaster
from platinumegg.app.cabaret.util.rediscache import RedisCache,\
    RankingGachaWholePrizeQueueIdSet
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventMaster,\
    RaidEventScore, RaidEventFlags, RaidEventChampagne
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventMaster,\
    ScoutEventScore, ScoutEventStageMaster, ScoutEventPlayData,\
    ScoutEventPresentNum, ScoutEventTanzakuCastMaster, ScoutEventTanzakuCastData
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventMaster,\
    BattleEventScore, BattleEventRank, BattleEventBattleTime,\
    BattleEventScorePerRank, BattleEventPieceMaster, BattleEventPieceCollection
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusTimeLimitedMaster,\
    LoginBonusTimeLimitedData, LoginBonusSugorokuMaster,\
    LoginBonusSugorokuPlayerData
from platinumegg.app.cabaret.models.Trade import TradeMaster, TradePlayerData
from platinumegg.app.cabaret.models.TradeShop import TradeShopPlayerData
from platinumegg.app.cabaret.models.ReprintTicketTradeShop import ReprintTicketTradeShopPlayerData
from platinumegg.app.cabaret.models.SerialCampaign import SerialCode,\
    SerialCampaignMaster, SerialCount
from platinumegg.app.cabaret.models.Gacha import GachaMaster, GachaPlayCount,\
    GachaSeatMaster, GachaSeatTablePlayCount, GachaSeatPlayData,\
    RankingGachaMaster, RankingGachaWholeData, RankingGachaWholePrizeQueue,\
    RankingGachaScore, GachaBoxResetPlayerData
from platinumegg.app.cabaret.models.battleevent.BattleEventPresent import BattleEventPresentMaster,\
    BattleEventPresentContentMaster, BattleEventPresentCounts
from platinumegg.app.cabaret.models.Mission import PanelMissionPanelMaster,\
    PlayerPanelMission, PanelMissionData
from platinumegg.app.cabaret.models.raidevent.RaidCardMixer import RaidEventMaterialData,\
    RaidEventRecipeMaster, RaidEventMixData
from platinumegg.app.cabaret.models.raidevent.RaidEventScout import RaidEventScoutStageMaster,\
    RaidEventScoutPlayData
from platinumegg.app.cabaret.models.LevelUpBonus import LevelUpBonusPlayerData
from platinumegg.app.cabaret.models.CabaretClub import CabaClubScorePlayerData,\
    CabaClubStoreMaster, CabaClubEventMaster, CabaClubStorePlayerData,\
    CabaClubItemPlayerData, CabaClubScorePlayerDataWeekly
from platinumegg.lib.command import CommandUtil
from platinumegg.app.cabaret.util.cabaclub_store import CabaclubStoreSet
from datetime import timedelta
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import ProduceEventMaster, CurrentProduceEventConfig,\
    ProduceCastMaster, ProduceEventScore, PlayerEducation, ProduceEventScoutPlayData, ProduceEventScoutStageMaster

class Handler(AdminHandler):
    """デバッグ機能.
    """
    
    class ChangeParams:
        """パラメータ変更.
        """
        (
            EXP,
            LEVEL,
            HP,
            GOLD,
            GACHA_PT,
            RAREOVERTICKET,
            MEMORIESTICKET,
            TRYLUCKTICKET,
            GACHATICKET,
            CABARETKING,
            DEMIWORLD,
            AP,
            BP,
            AP_MAX,
            DECKCAPACITY_LV,
            DECKCAPACITY_SCOUT,
            CARDLIMIT_LV,
            CARDLIMIT_ITEM,
            FRIENDLIMIT,
            CONTINUITY_DAYS,
            PLAY_DAYS,
            GOLDKEY,
            SILVERKEY,
            TOTAL_LDAYS,
            SPECIAL_MONEY,
            HONOR_POINT,
        ) = range(26)
        PARAMS = {
            EXP : {'table':PlayerExp, 'column':'exp'},
            LEVEL : {'table':PlayerExp, 'column':'level'},
            HP : {'table':PlayerExp, 'column':'hp'},
            GOLD : {'table':PlayerGold, 'column':'gold'},
            GACHA_PT : {'table':PlayerGachaPt, 'column':'gachapt'},
            RAREOVERTICKET : {'table':PlayerGachaPt, 'column':'rareoverticket'},
            MEMORIESTICKET : {'table':PlayerGachaPt, 'column':'memoriesticket'},
            TRYLUCKTICKET : {'table':PlayerGachaPt, 'column':'tryluckticket'},
            GACHATICKET : {'table':PlayerGachaPt, 'column':'gachaticket'},
            CABARETKING : {'table':PlayerTreasure, 'column':'cabaretking'},
            AP : {'table':PlayerAp, 'column':'ap'},
            BP : {'table':PlayerAp, 'column':'bp'},
            AP_MAX : {'table':PlayerAp, 'column':'apmax'},
            DECKCAPACITY_LV : {'table':PlayerDeck, 'column':'deckcapacitylv'},
            DECKCAPACITY_SCOUT : {'table':PlayerDeck, 'column':'deckcapacityscout'},
            CARDLIMIT_LV : {'table':PlayerDeck, 'column':'cardlimitlv'},
            CARDLIMIT_ITEM : {'table':PlayerDeck, 'column':'cardlimititem'},
            FRIENDLIMIT : {'table':PlayerFriend, 'column':'friendlimit'},
            CONTINUITY_DAYS : {'table':PlayerLogin, 'column':'ldays'},
            PLAY_DAYS : {'table':PlayerLogin, 'column':'pdays'},
            GOLDKEY : {'table':PlayerKey, 'column':'goldkey'},
            SILVERKEY : {'table':PlayerKey, 'column':'silverkey'},
            TOTAL_LDAYS : {'table':PlayerLogin, 'column':'tldays_view'},
            SPECIAL_MONEY : {'table':CabaClubScorePlayerData, 'column':'money'},
            HONOR_POINT : {'table':CabaClubScorePlayerData, 'column':'point'},
        }
    class CardChangeParams:
        """カードのパラメータ変更.
        """
        (
            EXP,
            LEVEL,
            SKILLLEVEL,
            TAKEOVER,
        ) = range(4)
        PARAMS = {
            EXP : {'column':'exp'},
            LEVEL : {'column':'level'},
            SKILLLEVEL : {'column':'skilllevel'},
            TAKEOVER : {'column':'takeover'},
        }
    
    def process(self):
        # リクエストに合わせて関数をコールする
        method = self.request.get('method', None)
        func = getattr(self, '_proc_%s' % method, None)
        
        if func:
            if not settings_sub.IS_DEV:
                self.putAlertToHtmlParam(u'本番環境では使えない', alert_code=AlertCode.ERROR)
            else:
                if settings_sub.IS_LOCAL:
                    print '========== execute:%s ==========' % method
                func()
        
        self.__debug_init()
        self.writeAppHtml('debug_tool')
    
    # 初期化.
    def __debug_init(self):
        now = OSAUtil.get_now()
        
        # 対象プレイヤー選択
        players = []
        for player in Player.fetchValues(fields=['id','dmmid'], order_by='id', using=settings.DB_READONLY):
            players.append({
                'id':player.id,
                'dmmid':player.dmmid,
            })
        
        model_mgr = self.getModelMgr()
        def makeObjMasterList(model_cls, filter_func=None):
            modellist = model_mgr.get_mastermodel_all(model_cls, model_cls.get_primarykey_column(), using=settings.DB_READONLY)
            if filter_func:
                modellist = [model for model in modellist if filter_func(model)]
            return modellist
        
        # スカウト.
        self.html_param['scoutlist'] = makeObjMasterList(ScoutMaster)
        
        # ハプニング.
        self.html_param['happeninglist'] = makeObjMasterList(HappeningMaster)
        self.html_param['raidlist'] = makeObjMasterList(RaidMaster)
        
        # アイテム.
        self.html_param['itemlist'] = makeObjMasterList(ItemMaster)
        
        # 宝箱.
        self.html_param['treasurelist_gold'] = makeObjMasterList(TreasureGoldMaster)
        self.html_param['treasurelist_silver'] = makeObjMasterList(TreasureSilverMaster)
        self.html_param['treasurelist_bronze'] = makeObjMasterList(TreasureBronzeMaster)
        
        # 秘宝交換.
        self.html_param['trademaster_list'] = makeObjMasterList(TradeMaster)
        
        # カード.
        cardlist = makeObjMasterList(CardMaster)
        self.html_param['cardlist'] = cardlist
        
        # アルバム.
        self.html_param['albumlist'] = [card for card in cardlist if (card.albumhklevel & 0xffffffff) == 1]
        
        # バトルランク.
        self.html_param['battleranklist'] = makeObjMasterList(BattleRankMaster)
        
        # タイプ.
        self.html_param['ctype'] = Defines.CharacterType.NAMES.items()
        
        # アイテムタイプ.
        self.html_param['ItemType'] = Defines.ItemType
        
        # ログインボーナス.
        self.html_param['loginbonuslist'] = makeObjMasterList(LoginBonusTimeLimitedMaster)
        
        # パネルミッション.
        self.html_param['panellist'] = makeObjMasterList(PanelMissionPanelMaster)
        
        # イベント.
        self.html_param['raidevent'] = makeObjMasterList(RaidEventMaster)
        self.html_param['scoutevent'] = makeObjMasterList(ScoutEventMaster)
        self.html_param['battleevent'] = makeObjMasterList(BattleEventMaster)
        self.html_param['produceevent'] = makeObjMasterList(ProduceEventMaster)
        
        # 現在のレイドイベント.
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        raideventmaster = BackendApi.get_raideventmaster(model_mgr, config.mid, using=settings.DB_READONLY)
        cur_raidevent_materials = {}
        cur_raidevent_recipe_list = []
        if raideventmaster:
            materials = raideventmaster.getMaterialDict()
            material_masters = dict([(master.id, master) for master in BackendApi.get_raidevent_materialmaster_list(model_mgr, materials.values(), using=settings.DB_READONLY)])
            cur_raidevent_materials = dict([(k, material_masters[v]) for k,v in materials.items() if material_masters.get(v)])
            # レシピ.
            recipeidlist = BackendApi.get_raidevent_recipeid_by_eventid(model_mgr, raideventmaster.id, using=settings.DB_READONLY)
            cur_raidevent_recipe_list = BackendApi.get_raidevent_recipemaster_list(model_mgr, recipeidlist, using=settings.DB_READONLY)
        
        self.html_param['cur_raidevent_recipe_list'] = cur_raidevent_recipe_list
        self.html_param['cur_raidevent_materials'] = cur_raidevent_materials
        self.html_param['cur_raidevent'] = raideventmaster
        
        # 現在のスカウトイベント.
        scouteventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY, check_schedule=False)
        tanzaku_master_list = None
        if scouteventmaster:
            # 短冊.
            tanzaku_master_list = BackendApi.get_scoutevent_tanzakumaster_by_eventid(model_mgr, scouteventmaster.id, using=settings.DB_READONLY)
        self.html_param['cur_scoutevent'] = scouteventmaster
        self.html_param['cur_tanzaku_master_list'] = tanzaku_master_list
        
        # 現在のバトルイベント.
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        battleeventmaster = BackendApi.get_battleevent_master(model_mgr, config.mid, using=settings.DB_READONLY)
        cur_battleevent_piecelist = []
        if battleeventmaster:
            cur_battleevent_piecelist = BackendApi.get_battleevent_piecemaster(model_mgr, battleeventmaster.id, using=settings.DB_READONLY)
        self.html_param['cur_battleevent_piecelist'] = cur_battleevent_piecelist
        self.html_param['cur_battleevent'] = battleeventmaster

        # 現在のプロデュースイベント.
        config = BackendApi.get_current_produce_event_config(model_mgr, using=settings.DB_READONLY)
        produceeventmaster = BackendApi.get_produce_event_master(model_mgr, config.mid, using=settings.DB_READONLY)
        self.html_param['cur_produceevent'] = produceeventmaster
        
        # ガチャ.
        gachalist = makeObjMasterList(GachaMaster, filter_func=lambda x:(x.stepid==0 or x.id==x.stepsid) and BackendApi.check_schedule(model_mgr, x.schedule, using=settings.DB_READONLY, now=now))
        self.html_param['gachalist'] = gachalist
        
        # ランキングガチャ.
        boxidlist = list(set([gacha.boxid for gacha in gachalist if gacha.consumetype == Defines.GachaConsumeType.RANKING]))
        self.html_param['rankinggachalist'] = makeObjMasterList(RankingGachaMaster, filter_func=lambda x:x.id in boxidlist)
        
        # シリアルコード.
        self.html_param['serialcampaignlist'] = makeObjMasterList(SerialCampaignMaster)
        
        # バトルイベント贈り物.
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        self.html_param['battleeventpresentlist'] = makeObjMasterList(BattleEventPresentMaster, filter_func=lambda x:x.eventid == config.mid)
        self.html_param['battleeventpresentcontentlist'] = makeObjMasterList(BattleEventPresentContentMaster)
        
        # 双六ログインボーナス.
        self.html_param['loginbonussugorokulist'] = makeObjMasterList(LoginBonusSugorokuMaster)
        
        # キャバクラ店舗.
        self.html_param['cabaclubstorelist'] = makeObjMasterList(CabaClubStoreMaster)
        # キャバクラ店舗の発生イベント.
        self.html_param['cabaclubeventlist'] = makeObjMasterList(CabaClubEventMaster)
        
        self.html_param['players'] = players
        self.html_param['change_params'] = [(k, data['table'].get_field(data['column']).verbose_name) for k,data in Handler.ChangeParams.PARAMS.items()]
        self.html_param['card_change_params'] = [(k, Card.get_field(data['column']).verbose_name) for k,data in Handler.CardChangeParams.PARAMS.items()]
        
        self.html_param['now'] = now.strftime("%Y-%m-%d %H:%M:%S")
        self.html_param['datetime_now'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.html_param['cabaclub_week'] = BackendApi.to_cabaretclub_section_starttime(now)
        self.html_param['cabaclub_last_week'] = BackendApi.to_cabaretclub_section_starttime(now) - datetime.timedelta(days=7)
        
        self.html_param['Defines'] = Defines
    
    def __check_request_userid(self, uid):
        """ユーザーID確認.
        """
        try:
            
            uid = int(uid)
        except:
            self.putAlertToHtmlParam(u'指定したIDが不正です. id=%s' % uid , alert_code=AlertCode.ERROR)
            return None
        player = Player.getByKey(uid)
        if player is None:
            self.putAlertToHtmlParam(u'存在しないプレイヤーです. id=%s' % uid , alert_code=AlertCode.ERROR)
            return None
        return player.id
    
    def __check_master_id(self, model_cls, mid, blank=False):
        """マスターID確認.
        """
        try:
            mid = int(mid)
        except:
            if not blank:
                self.putAlertToHtmlParam(u'指定したマスターIDが不正です. id=%s' % mid , alert_code=AlertCode.ERROR)
            return None
        model_mgr = self.getModelMgr()
        master = model_mgr.get_model(model_cls, mid, using=settings.DB_READONLY)
        if master is None and not blank:
            self.putAlertToHtmlParam(u'存在しないマスターデータです. id=%s' % mid , alert_code=AlertCode.ERROR)
            return None
        return master
    
    def __check_intvalue(self, value, min_value=0, max_value=None):
        """数値確認.
        """
        if not value:
            self.putAlertToHtmlParam(u'値を入力して下さい', alert_code=AlertCode.ERROR)
            return None
        elif not value.isdigit():
            self.putAlertToHtmlParam(u'値に数字を入力して下さい', alert_code=AlertCode.ERROR)
            return None
        v = int(value)
        if v < min_value:
            self.putAlertToHtmlParam(u'値には%d以上の数字を入力して下さい' % min_value, alert_code=AlertCode.ERROR)
            return None
        elif max_value is not None and max_value < v:
            self.putAlertToHtmlParam(u'値には%d以下の数字を入力して下さい' % max_value, alert_code=AlertCode.ERROR)
            return None
        return v
    
    def __check_card_id(self, cardid):
        """カードID確認.
        """
        try:
            cardid = int(cardid)
        except:
            self.putAlertToHtmlParam(u'指定したカードIDが不正です. id=%s' % cardid , alert_code=AlertCode.ERROR)
            return None
        model_mgr = self.getModelMgr()
        cardsetlist = BackendApi.get_cards([cardid], model_mgr, using=settings.DB_READONLY)
        if not cardsetlist:
            self.putAlertToHtmlParam(u'存在しないカードです. id=%s' % cardid , alert_code=AlertCode.ERROR)
            return None
        return cardsetlist[0]
    
    def __check_datetime(self, str_datetime, format_string="%Y-%m-%d %H:%M:%S"):
        """日付確認.
        """
        try:
            dest = datetime.datetime.strptime(str_datetime, format_string)
        except:
            self.putAlertToHtmlParam(u'指定した日付が不正です. %sの形式で指定して下さい' % format_string, alert_code=AlertCode.ERROR)
            return None
        return dest
    
    def _proc_create_player(self):
        """プレイヤー作成.
        """
        dmmid = self.request.get('_dmmid')
        if not dmmid:
            self.putAlertToHtmlParam(u'DMMIDを指定してください.' , alert_code=AlertCode.ERROR)
            return
        
        uid = BackendApi.dmmid_to_appuid(self, [dmmid]).get(dmmid)
        if uid:
            self.putAlertToHtmlParam(u'このIDのユーザーはすでに存在しています. id=%s' % dmmid , alert_code=AlertCode.ERROR)
            return
        
        player_type = self.request.get('_ctype')
        if not player_type or not player_type.isdigit() or not Defines.CharacterType.NAMES.has_key(int(player_type)):
            self.putAlertToHtmlParam(u'指定できないタイプです. id=%s' % player_type , alert_code=AlertCode.ERROR)
            return
        
        player_type = int(player_type)
        
        def tr_create():
            model_mgr = ModelRequestMgr()
            ins = Player()
            ins.dmmid = dmmid
            model_mgr.set_save(ins)
            model_mgr.write_all()
            return model_mgr
        
        def tr_reqist():
            model_mgr = ModelRequestMgr()
            uid = BackendApi.dmmid_to_appuid(self, [dmmid]).get(dmmid)
            BackendApi.tr_regist_player(model_mgr, uid, player_type)
            model_mgr.write_all()
            return model_mgr
        
        def tr_tutoend():
            model_mgr = ModelRequestMgr()
            uid = BackendApi.dmmid_to_appuid(self, [dmmid]).get(dmmid)
            player = BackendApi.get_players(self, [uid], model_mgr=model_mgr)[0]
            BackendApi.tr_tutorialend(model_mgr, player, False)
            model_mgr.write_all()
            return model_mgr
        
        try:
            for func in (tr_create, tr_reqist, tr_tutoend):
                model_mgr = db_util.run_in_transaction(func)
                model_mgr.write_end()
            uid = BackendApi.dmmid_to_appuid(self, [dmmid]).get(dmmid)
            self.putAlertToHtmlParam(u'プレイヤーを作成しました. DMMID=%s, ID=%s' % (dmmid, uid), alert_code=AlertCode.SUCCESS)
        except CabaretError, e:
            self.putAlertToHtmlParam(u'作成に失敗しました. %s' % e, alert_code=AlertCode.ERROR)
    
    def _proc_delete_player(self):
        """プレイヤー削除.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        def tr():
            model_mgr0 = ModelRequestMgr()
            BackendApi.tr_delete_friend_all(model_mgr0, uid)
            model_mgr0.write_all()
            model_mgr0.write_end()
            
            model_mgr1 = ModelRequestMgr()
            BackendApi.tr_delete_player(model_mgr1, uid)
            model_mgr1.write_all()
            return model_mgr0, model_mgr1
        model_mgr0, model_mgr1 = db_util.run_in_transaction(tr)
        model_mgr0.write_end()
        model_mgr1.write_end()
        
        self.putAlertToHtmlParam(u'プレイヤーを削除しました. id=%s' % uid , alert_code=AlertCode.SUCCESS)
    
    def _proc_recovery_ap(self):
        """体力･気力全回復.
        """
        str_uid = self.request.get('_uid')
        if str_uid == "all":
            playeraplist = PlayerAp.fetchValues(['id'])
        else:
            uid = self.__check_request_userid(str_uid)
            if uid is None:
                return
            
            player = PlayerAp.getByKey(uid)
            if player is None:
                self.putAlertToHtmlParam(u'未登録のプレイヤーです. id=%s' % uid , alert_code=AlertCode.ERROR)
                return
            playeraplist = [player]
        
        uidlist = [player.id for player in playeraplist]
        def tr():
            model_mgr = ModelRequestMgr()
            playerlist = BackendApi.get_players(self, uidlist, [PlayerFriend], model_mgr=model_mgr)
            
            now = OSAUtil.get_now()
            
            def forUpdateTask(model, inserted, player):
                player.setModel(model)
                player.set_ap(player.get_ap_max())
                player.set_bp(player.get_bp_max())
                player.aprtime = now
                player.bprtime = now
            
            for player in playerlist:
                model_mgr.add_forupdate_task(PlayerAp, player.id, forUpdateTask, player)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        self.putAlertToHtmlParam(u'体力と気力を回復しました. id=%s' % str_uid , alert_code=AlertCode.SUCCESS)
    
    def _proc_change_player_parameter(self):
        """パラメータ変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        param_type = self.request.get('_param_type')
        value = self.__check_intvalue(self.request.get('_value'))
        if value is None:
            return
        elif not param_type or not param_type.isdigit() or not Handler.ChangeParams.PARAMS.has_key(int(param_type)):
            self.putAlertToHtmlParam(u'変更するパラメータの指定が不正です. %s' % param_type , alert_code=AlertCode.ERROR)
            return
        
        param_type = int(param_type)
        value = min(int(value), Defines.VALUE_MAX)
        
        paramdata = Handler.ChangeParams.PARAMS[param_type]
        
        def tr_write(model_cls, columnname, value):
            model_mgr = ModelRequestMgr()
            
            player = BackendApi.get_players(self, [uid], model_mgr=model_mgr)[0]
            if param_type == Handler.ChangeParams.EXP:
                player.exp = 0
                BackendApi.tr_add_exp(model_mgr, player, value)
            elif param_type == Handler.ChangeParams.LEVEL:
                playerexp = BackendApi.get_playerlevelexp_bylevel(value, model_mgr)
                if playerexp is None:
                    raise CabaretError(u'プレイヤーレベルが存在しません.')
                player.exp = 0
                BackendApi.tr_add_exp(model_mgr, player, playerexp.exp)
            elif param_type == Handler.ChangeParams.AP:
                player.set_ap(value)
                value = player.get_ap()
                model_mgr.set_save(player.getModel(PlayerAp))
            elif param_type == Handler.ChangeParams.BP:
                player.set_bp(value)
                value = player.get_bp()
                model_mgr.set_save(player.getModel(PlayerAp))
            elif param_type == Handler.ChangeParams.CABARETKING:
                player.cabaretking = value
                player.demiworld = 0
                model_mgr.set_save(player.getModel(PlayerTreasure))
            elif param_type == Handler.ChangeParams.TOTAL_LDAYS:
                config = BackendApi.get_current_totalloginbonusconfig(model_mgr)
                player.tlmid = config.getCurrentMasterID()
                player.tldays_view = value
                table = BackendApi.get_loginbonustimelimiteddaysmaster_day_table_by_timelimitedmid(model_mgr, player.tlmid)
                if table:
                    daymax = max(table.keys())
                    player.tldays = value % daymax
                model_mgr.set_save(player.getModel(PlayerLogin))
            elif param_type == Handler.ChangeParams.SPECIAL_MONEY:
                def forUpdate(model, *args, **kwargs):
                    model.money = value
                model_mgr.add_forupdate_task(CabaClubScorePlayerData, uid, forUpdate)
            elif param_type == Handler.ChangeParams.HONOR_POINT:
                def forUpdate(model, *args, **kwargs):
                    model.point = value
                model_mgr.add_forupdate_task(CabaClubScorePlayerData, uid, forUpdate)
            else:
                def forUpdateTask(model, inserted):
                    setattr(model, columnname, value)
                model_mgr.add_forupdate_task(model_cls, uid, forUpdateTask)
            model_mgr.write_all()
            return model_mgr, value
        try:
            # DB反映
            model_mgr, value = db_util.run_in_transaction(tr_write, paramdata['table'], paramdata['column'], value)
            model_mgr.write_end()
        except CabaretError, e:
            self.putAlertToHtmlParam(e.getHtml(True), alert_code=AlertCode.ERROR)
            return
        
        fieldname = paramdata['table'].get_field(paramdata['column']).verbose_name
        self.putAlertToHtmlParam(u'ユーザーID:%dの%sを%dに変更しました.' % (uid, fieldname, value), alert_code=AlertCode.SUCCESS)
    
    def _proc_set_logintime(self):
        """ログインボーナス受け取り時間変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        str_time = self.request.get('_value')
        try:
            lbtime = DateTimeUtil.strToDateTime(str_time, "%Y-%m-%d %H:%M:%S")
        except:
            self.putAlertToHtmlParam(u'日付を読み取れませんでした.%s' % str_time, alert_code=AlertCode.ERROR)
        
        def tr(uid, lbtime):
            model_mgr = ModelRequestMgr()
            model = PlayerLogin.getByKeyForUpdate(uid)
            model.lbtime = lbtime
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, uid, lbtime).write_end()
        
        self.putAlertToHtmlParam(u'ユーザーID:%dのログインボーナス受け取り時間を変更しました.' % uid, alert_code=AlertCode.SUCCESS)
    
    def _proc_reset_loginbonus(self):
        """ログインボーナスをもう一度.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        continuity = bool(int(self.request.get('_continuity') or 0))
        if continuity:
            lbtime = DateTimeUtil.toLoginTime(OSAUtil.get_now() - datetime.timedelta(days=1))
            str_continuity = u'有効'
        else:
            lbtime = DateTimeUtil.toLoginTime(OSAUtil.get_now() - datetime.timedelta(days=2))
            str_continuity = u'無効'
        
        def tr():
            model_mgr = ModelRequestMgr()
            playerlogin = PlayerLogin.getByKeyForUpdate(uid)
            playerlogin.lbtime = lbtime
            model_mgr.set_save(playerlogin)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'ユーザーID:%dがログインボーナスを受け取れるようになりました.連続ログイン=%s' % (uid, str_continuity), alert_code=AlertCode.SUCCESS)
    
    def _proc_update_longloginbonus(self):
        """ロングログインボーナスをもう一度.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        master = self.__check_master_id(LoginBonusTimeLimitedMaster, self.request.get('_mid'))
        if master is None:
            return
        mid = master.id
        days = self.__check_intvalue(self.request.get('_days'))
        lbtime = DateTimeUtil.toLoginTime(OSAUtil.get_now() - datetime.timedelta(days=1))
        
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.days = days
                model.mid = mid
                model.lbtltime = lbtime
            model_mgr.add_forupdate_task(LoginBonusTimeLimitedData, LoginBonusTimeLimitedData.makeID(uid, mid), forUpdate)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'ユーザーID:%dがロングログインボーナスを受け取れるようになりました.' % uid, alert_code=AlertCode.SUCCESS)
    
    def _proc_reset_loginbonus_sugoroku(self):
        """双六ログインボーナスをもう一度.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        master = self.__check_master_id(LoginBonusSugorokuMaster, self.request.get('_mid'))
        if None in (uid, master):
            return
        lap = self.__check_intvalue(self.request.get('_lap'), 0)
        lose_turns = self.__check_intvalue(self.request.get('_lose_turns'), 0)
        
        def tr():
            model_mgr = ModelRequestMgr()
            model = model_mgr.get_model(LoginBonusSugorokuPlayerData, LoginBonusSugorokuPlayerData.makeID(uid, master.id), get_instance=True)
            if lap is not None:
                model.lap = lap
            # 周回数からマップ番号を取得.
            mapid = master.getMapIDByLap(model.lap)
            # マップに存在するマスを取得.
            squares_master_list = BackendApi.get_loginbonus_sugoroku_map_squares_master_by_mapid(model_mgr, mapid)
            if not squares_master_list:
                self.putAlertToHtmlParam(u'双六のマップにマスが設定されていません', alert_code=AlertCode.ERROR)
                raise CabaretError()
            loc = self.request.get('_loc')
            if loc:
                loc = self.__check_intvalue(self.request.get('_loc'), 1, squares_master_list[-1].number)
                if loc is None:
                    raise CabaretError()
                model.loc = loc
            if lose_turns is not None:
                model.lose_turns = lose_turns
            model.ltime = DateTimeUtil.toLoginTime(OSAUtil.get_now() - datetime.timedelta(days=1))
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr
        try:
            model_mgr = db_util.run_in_transaction(tr)
            model_mgr.write_end()
        except CabaretError:
            return
        self.putAlertToHtmlParam(u'ユーザーID:{}が双六ログインボーナスを受け取れるようになりました'.format(uid), alert_code=AlertCode.SUCCESS)
    
    def _proc_reset_levelupbonus_playerdata(self):
        """レベルアップ達成ボーナスのリセット.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        mid = Defines.LEVELUP_BONUS_VERSION
        p_key = LevelUpBonusPlayerData.makeID(uid, mid)

        if uid is None:
            return

        model_mgr = ModelRequestMgr()
        playerdata = BackendApi.get_model(model_mgr, LevelUpBonusPlayerData, p_key)
        playerdata.last_prize_level = 0

        def tr(playerdata, p_key):
            model_mgr = ModelRequestMgr()
            model_mgr.get_model_forupdate(LevelUpBonusPlayerData, p_key)
            model_mgr.set_save(playerdata)
            model_mgr.write_all()
            model_mgr.write_end()
        db_util.run_in_transaction(tr, playerdata, p_key)

        self.putAlertToHtmlParam(u'ユーザーID:{}のレベルアップ達成ボーナス受け取りをリセットしました.'.format(uid), alert_code=AlertCode.SUCCESS)

    def _proc_greet_count(self):
        """あいさつ回数変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        value = self.__check_intvalue(self.request.get('_value'))
        if value is None:
            return
        
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.today = value
                model.ltime = OSAUtil.get_now()
            model_mgr.add_forupdate_task(GreetPlayerData, uid, forUpdate)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'ユーザーID:%dの本日あいさつ回数を%d回にしました' % (uid, value), alert_code=AlertCode.SUCCESS)
    
    def _proc_greet_do(self):
        """あいさつを行う.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        oid = self.__check_request_userid(self.request.get('_oid'))
        if uid is None:
            return
        
        if uid == oid:
            self.putAlertToHtmlParam(u'同じユーザーに対して挨拶は行えません', alert_code=AlertCode.ERROR)
            return
        
        def tr(uid, oid):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_greet(model_mgr, uid, oid, False)
            model_mgr.write_all()
            return model_mgr
        
        errcode = 0
        try:
            model_mgr = db_util.run_in_transaction(tr, uid, oid)
            model_mgr.write_end()
        except CabaretError,e:
            if e.code in (CabaretError.Code.ALREADY_RECEIVED, CabaretError.Code.OVER_LIMIT):
                # 同じ相手へのあいさつは2時間に1度.
                # あいさつは1日に300回まで.
                errcode = e.code
                
                if errcode == CabaretError.Code.ALREADY_RECEIVED:
                    self.putAlertToHtmlParam(u"同じ相手には2時間に1度だけです", alert_code=AlertCode.ERROR)
                elif errcode == CabaretError.Code.OVER_LIMIT:
                    self.putAlertToHtmlParam(u"挨拶は1日%d回までです" % Defines.GREET_COUNT_MAX_PER_DAY, alert_code=AlertCode.ERROR)
                
                return
            else:
                return
            
        
        self.putAlertToHtmlParam(u'ユーザーID:%dが ユーザーID:%dに対して挨拶を行いました' % (uid, oid), alert_code=AlertCode.SUCCESS)
    
    def _proc_add_card(self):
        """カード付与.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(CardMaster, self.request.get('_mid'))
        if master is None:
            return
        
        level = self.__check_intvalue(self.request.get('_level'))
        if not level:
            return
        
        level = min(max(1, level), master.maxlevel)
        
        def tr():
            model_mgr = ModelRequestMgr()
            playercard = PlayerCard.getByKeyForUpdate(uid)
            BackendApi.tr_create_card(model_mgr, playercard, master.id, level=level)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'ユーザーID:%dにカード:%s(ID:%d)をレベル:%dで付与しました' % (uid, master.name, master.id, level), alert_code=AlertCode.SUCCESS)
    
    def _proc_change_card_status(self):
        """カードのステータスの変更.
        """
        cardset = self.__check_card_id(self.request.get('_card'))
        
        param_type = self.request.get('_param_type')
        value = self.__check_intvalue(self.request.get('_value'))
        if value is None:
            return
        
        if not param_type or not param_type.isdigit() or not Handler.CardChangeParams.PARAMS.has_key(int(param_type)):
            self.putAlertToHtmlParam(u'変更するパラメータの指定が不正です. %s' % param_type , alert_code=AlertCode.ERROR)
            return
        
        param_type = int(param_type)
        value = int(value)
        
        paramdata = Handler.CardChangeParams.PARAMS[param_type]
        
        def tr_write(cardid, columnname, value):
            model_mgr = ModelRequestMgr()
            
            cardset = BackendApi.get_cards([cardid], model_mgr, forupdate=True)[0]
            if param_type == Handler.CardChangeParams.EXP:
                cardset.card.exp = 0
                BackendApi.tr_add_cardexp(model_mgr, cardset, value)
                model_mgr.set_save(cardset.card)
            elif param_type == Handler.CardChangeParams.LEVEL:
                cardexp = BackendApi.get_cardlevelexp_bylevel(value, model_mgr)
                if cardexp is None:
                    raise CabaretError(u'カードレベルが存在しません.')
                cardset.card.exp = 0
                BackendApi.tr_add_cardexp(model_mgr, cardset, cardexp.exp)
                model_mgr.set_save(cardset.card)
            else:
                if param_type == Handler.CardChangeParams.SKILLLEVEL:
                    value = min(max(value, 1), Defines.SKILLLEVEL_MAX)
                setattr(cardset.card, columnname, value)
                model_mgr.set_save(cardset.card)
            model_mgr.write_all()
            return model_mgr
        try:
            # DB反映
            model_mgr = db_util.run_in_transaction(tr_write, cardset.id, paramdata['column'], value)
            model_mgr.write_end()
        except CabaretError, e:
            self.putAlertToHtmlParam(e.getHtml(True), alert_code=AlertCode.ERROR)
            return
        
        fieldname = Card.get_field(paramdata['column']).verbose_name
        self.putAlertToHtmlParam(u'カードID:%dの%sを%dに変更しました.' % (cardset.id, fieldname, value), alert_code=AlertCode.SUCCESS)
    
    def _proc_card_acquisition(self):
        """カード取得フラグを操作.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(CardMaster, self.request.get('_mid'))
        if master is None:
            return
        flag = bool(int(self.request.get('_flag')))
        maxlevel = None
        if flag:
            maxlevel = self.request.get('_level')
            if not maxlevel or not maxlevel.isdigit() or int(maxlevel) < 1:
                self.putAlertToHtmlParam(u'レベルは1以上の数値で指定してください', alert_code=AlertCode.ERROR)
                return
            maxlevel = int(maxlevel)
        
        def tr_create(mid):
            model_mgr = ModelRequestMgr()
            master = BackendApi.get_cardmasters([mid], model_mgr).get(mid)
            BackendApi.tr_set_cardacquisition(model_mgr, uid, master, maxlevel)
            model_mgr.write_all()
            return model_mgr
        
        def tr_delete(mid):
            model_mgr = ModelRequestMgr()
            model = model_mgr.get_model(CardAcquisition, CardAcquisition.makeID(uid, mid))
            if model:
                model_mgr.set_delete(model)
            model_mgr.write_all()
            return model_mgr
        
        if flag:
            model_mgr = db_util.run_in_transaction(tr_create, master.id)
            model_mgr.write_end()
            self.putAlertToHtmlParam(u'ユーザーID:%dのカード:%s(ID:%d)を取得済みに変更しました' % (uid, master.name, master.id), alert_code=AlertCode.SUCCESS)
        else:
            model_mgr = db_util.run_in_transaction(tr_delete, master.id)
            model_mgr.write_end()
            self.putAlertToHtmlParam(u'ユーザーID:%dのカード:%s(ID:%d)を未取得にしました' % (uid, master.name, master.id), alert_code=AlertCode.SUCCESS)
    
    def _proc_set_all_card_acquisition(self):
        """カード取得フラグを全取得.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        model_mgr = self.getModelMgr()
        masterlist = model_mgr.get_mastermodel_all(CardMaster, using=settings.DB_READONLY)
        
        def tr(uid, masterlist):
            model_mgr = ModelRequestMgr()
            for master in masterlist:
                if master.pubstatus != Defines.PublishStatus.PUBLIC:
                    # 開発環境のみ公開も除外.
                    continue
                mid = master.id
                ins = CardAcquisition.makeInstance(CardAcquisition.makeID(uid, mid))
                ins.maxlevel = master.maxlevel
                model_mgr.set_save(ins)
                
                if master.hklevel == 1:
                    ins = AlbumAcquisition.makeInstance(AlbumAcquisition.makeID(uid, master.album))
                    model_mgr.set_save(ins)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr, uid, masterlist)
        model_mgr.write_end()
        self.putAlertToHtmlParam(u'ユーザID:%dのカード取得フラグを全て取得済みにしました.' % uid, alert_code=AlertCode.SUCCESS)
    
    def _proc_flush_card_acquisition(self):
        """カード取得フラグを全削除.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        def tr():
            model_mgr = ModelRequestMgr()
            for model in CardAcquisition.fetchByOwner(uid, using=settings.DB_DEFAULT):
                model_mgr.set_delete(model)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        self.putAlertToHtmlParam(u'ユーザID:%dのカード取得フラグを全て削除しました.' % uid, alert_code=AlertCode.SUCCESS)
    
    def _proc_album_acquisition(self):
        """アルバム取得フラグを操作.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(CardMaster, self.request.get('_mid'))
        if master is None:
            return
        flag = bool(int(self.request.get('_flag')))
        
        def tr_create(mid):
            model_mgr = ModelRequestMgr()
            master = BackendApi.get_cardmasters([mid], model_mgr).get(mid)
            BackendApi.tr_set_cardacquisition(model_mgr, uid, master)
            model_mgr.write_all()
            return model_mgr
        
        def tr_delete(mid):
            model_mgr = ModelRequestMgr()
            master = BackendApi.get_cardmasters([mid], model_mgr).get(mid)
            model = model_mgr.get_model(AlbumAcquisition, AlbumAcquisition.makeID(uid, master.album))
            if model:
                model_mgr.set_delete(model)
            model_mgr.write_all()
            return model_mgr
        
        albumid = int(master.albumhklevel>>32)
        if flag:
            model_mgr = db_util.run_in_transaction(tr_create, master.id)
            model_mgr.write_end()
            self.putAlertToHtmlParam(u'ユーザーID:%dのキャスト名鑑:%s(ID:%d)を取得済みに変更しました' % (uid, master.name, albumid), alert_code=AlertCode.SUCCESS)
        else:
            model_mgr = db_util.run_in_transaction(tr_delete, master.id)
            model_mgr.write_end()
            self.putAlertToHtmlParam(u'ユーザーID:%dのキャスト名鑑:%s(ID:%d)を未取得にしました' % (uid, master.name, albumid), alert_code=AlertCode.SUCCESS)
    
    def _proc_flush_album_acquisition(self):
        """アルバム取得フラグを全削除.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        def tr():
            model_mgr = ModelRequestMgr()
            for model in AlbumAcquisition.fetchByOwner(uid, using=settings.DB_DEFAULT):
                model_mgr.set_delete(model)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        self.putAlertToHtmlParam(u'ユーザID:%dのキャスト名鑑取得フラグを全て削除しました.' % uid, alert_code=AlertCode.SUCCESS)
    
    def _proc_cardstock(self):
        """異動数操作.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(CardMaster, self.request.get('_mid'))
        if master is None:
            return
        value = self.__check_intvalue(self.request.get('_value'), 0)
        if value is None:
            return
        
        def tr_create(uid, album, value):
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.num = value
            model_mgr.add_forupdate_task(CardStock, CardStock.makeID(uid, album), forUpdate)
            model_mgr.write_all()
            return model_mgr
        
        def tr_delete(uid, album):
            model_mgr = ModelRequestMgr()
            model = model_mgr.get_model(CardStock, CardStock.makeID(uid, album))
            if model:
                model_mgr.set_delete(model)
            model_mgr.write_all()
            return model_mgr
        
        albumid = int(master.albumhklevel>>32)
        if 0 < value:
            model_mgr = db_util.run_in_transaction(tr_create, uid, albumid, value)
            model_mgr.write_end()
        else:
            model_mgr = db_util.run_in_transaction(tr_delete, uid, albumid)
            model_mgr.write_end()
        self.putAlertToHtmlParam(u'ユーザーID:%dのキャスト:%s(ID:%d)の異動数を%dにしました' % (uid, master.name, master.id, value), alert_code=AlertCode.SUCCESS)
    
    def _proc_update_gacha_playcount(self):
        """ガチャのプレイ回数を変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(GachaMaster, self.request.get('_mid'))
        if master is None:
            return
        value = self.__check_intvalue(self.request.get('_value'))
        if value is None:
            return
        
        def tr(uid, mid, cnt):
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.cnt = cnt
                model.ptime = max(DateTimeUtil.toLoginTime(OSAUtil.get_now()), model.ptime)
                model.cnttotal = cnt
            model_mgr.add_forupdate_task(GachaPlayCount, GachaPlayCount.makeID(uid, mid), forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, uid, master.id, value).write_end()
        
        self.putAlertToHtmlParam(u'ユーザID:%dの%sのプレイ回数を%dにしました.' % (uid, master.name, value), alert_code=AlertCode.SUCCESS)
    
    def _proc_reset_gacha_box(self):
        """ガチャのBOXをリセット
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(GachaMaster, self.request.get('_mid'))
        if master is None:
            return
        
        def tr(uid, box_id):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_reset_gachaboxplaydata(model_mgr, uid, box_id)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, uid, master.boxid).write_end()
        
        self.putAlertToHtmlParam(u'ユーザID:%dの%sのBOXをリセットしました.' % (uid, master.name), alert_code=AlertCode.SUCCESS)
    
    def _proc_update_gacha_step(self):
        """ガチャのステップ数を変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(GachaMaster, self.request.get('_mid'))
        if master is None:
            return
        elif master.stepid == 0 or master.id != master.stepsid:
            self.putAlertToHtmlParam(u'このガチャはステップ変更の対象ではありません.id=%d' % master.id, alert_code=AlertCode.ERROR)
            return
        
        value = self.__check_intvalue(self.request.get('_value'))
        if value is None:
            return
        
        model_mgr = self.getModelMgr()
        setpupmaster = BackendApi.get_gachastepupmaster(model_mgr, master.stepid, using=settings.DB_READONLY)
        value = min(setpupmaster.stepmax, value)
        
        def tr(uid, mid, step):
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.step = step
                model.ptime = max(DateTimeUtil.toLoginTime(OSAUtil.get_now()), model.ptime)
                model.steptotal = step
            model_mgr.add_forupdate_task(GachaPlayCount, GachaPlayCount.makeID(uid, mid), forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, uid, master.id, value).write_end()
        
        self.putAlertToHtmlParam(u'ユーザID:%dの%sのステップ数を%dにしました.' % (uid, master.name, value), alert_code=AlertCode.SUCCESS)
    
    def _proc_update_gacha_sheet_state(self):
        """シートの状態を変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(GachaMaster, self.request.get('_mid'))
        if master is None:
            return
        elif master.seattableid == 0:
            self.putAlertToHtmlParam(u'このガチャはシート変更の対象ではありません.id=%d' % master.id, alert_code=AlertCode.ERROR)
            return
        
        str_value = str(self.request.get('_value'))
        value = None
        if str_value:
            if str_value.isdigit():
                value = max(0, int(str_value))
            else:
                self.putAlertToHtmlParam(u'周回数は0以上の数値で入力してください.id=%d' % master.id, alert_code=AlertCode.ERROR)
                return
        
        # シートの状態.
        tmp = GachaSeatMaster.makeInstance(0)
        flags = {}
        idx = 0
        allend = True
        while tmp.getPrizeId(idx) is not None:
            flags[idx] = self.request.get("sheet%d" % idx) == "1"
            if not flags[idx]:
                allend = False
            idx += 1
        if allend:
            flags = {}
        
        def tr(uid, master, lap, flags):
            model_mgr = ModelRequestMgr()
            
            tableid = master.seattableid
            tablemaster = BackendApi.get_gachaseattablemaster(model_mgr, tableid)
            
            # 周回数.
            playcount = BackendApi.get_gachaseattableplaycount(model_mgr, uid, [tableid]).get(tableid)
            if playcount is None:
                playcount = GachaSeatTablePlayCount.makeInstance(GachaSeatTablePlayCount.makeID(uid, tableid))
            else:
                playcount = GachaSeatTablePlayCount.getByKeyForUpdate(GachaSeatTablePlayCount.makeID(uid, tableid))
            if lap is not None:
                playcount.lap = lap
            model_mgr.set_save(playcount)
            
            # シートの状態.
            seat_mid = tablemaster.getSeatId(playcount.lap+1)
            seatmaster = BackendApi.get_gachaseatmaster(model_mgr, seat_mid)
            if seatmaster is not None:
                playdata = BackendApi.get_gachaseatplaydata(model_mgr, uid, [seat_mid]).get(seat_mid)
                if playdata is None:
                    playdata = GachaSeatPlayData.makeInstance(GachaSeatPlayData.makeID(uid, seat_mid))
                else:
                    playdata = GachaSeatPlayData.getByKeyForUpdate(GachaSeatPlayData.makeID(uid, seat_mid))
                
                playdata.clearFlags()
                for idx, flag in flags.items():
                    playdata.setFlag(idx, flag)
                model_mgr.set_save(playdata)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, uid, master, value, flags).write_end()
        
        self.putAlertToHtmlParam(u'ユーザID:%dの%sのシートの状態を変更しました.' % (uid, master.name), alert_code=AlertCode.SUCCESS)
    
    def _proc_update_rankinggacha_wholepoint(self):
        """ランキングガチャの総計Ptを変更.
        """
        master = self.__check_master_id(RankingGachaMaster, self.request.get('_mid'))
        if master is None:
            return
        value = self.__check_intvalue(self.request.get('_value'))
        if value is None:
            return
        
        def tr(master, value):
            model_mgr = ModelRequestMgr()
            # 総計ポイントを変更.
            model = RankingGachaWholeData.getByKey(master.id)
            if model is None:
                model = RankingGachaWholeData.makeInstance(master.id)
            
            if value < model.point:
                # 初回Ptを操作.
                scoredatalist = RankingGachaScore.fetchValues(filters={'mid':master.id, 'firstpoint__gt':value})
                for scoredata in scoredatalist:
                    scoredata.firstpoint = value
                    model_mgr.set_save(scoredata)
                
                # キューを削除.
                queuelist = RankingGachaWholePrizeQueue.fetchValues(filters={'boxid':master.id, 'point__gt':value})
                for queue in queuelist:
                    model_mgr.set_delete(queue)
            elif model.point < value:
                # 差分の報酬のキューを積む.
                table = master.get_wholeprizes(point_min=model.point+1, point_max=value)
                keys = table.keys()
                keys.sort()
                for key in keys:
                    if model.point < key <= value and table[key]:
                        queue = RankingGachaWholePrizeQueue()
                        queue.boxid = master.id
                        queue.point = key
                        queue.prizes = table[key]
                        model_mgr.set_save(queue)
            
            model.point = value
            model_mgr.set_save(model)
            
            def writeEnd():
                RankingGachaWholePrizeQueueIdSet.flush()
            model_mgr.add_write_end_method(writeEnd)
            
            model_mgr.write_all()
            return model_mgr
        
        db_util.run_in_transaction(tr, master, value).write_end()
        
        self.putAlertToHtmlParam(u'総計Ptを変更しました.' , alert_code=AlertCode.SUCCESS)
    
    def __update_rankinggacha_singlepoint(self, is_single):
        """ランキングガチャのPtを変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return False
        master = self.__check_master_id(RankingGachaMaster, self.request.get('_mid'))
        if master is None:
            return False
        value = self.__check_intvalue(self.request.get('_value'), min_value=1)
        if value is None:
            return False
        
        def tr(att, ranking, uid, master, value):
            model_mgr = ModelRequestMgr()
            
            scoreid = RankingGachaScore.makeID(uid, master.id)
            scoredata = RankingGachaScore.getByKey(scoreid)
            if scoredata is None:
                scoredata = RankingGachaScore.makeInstance(scoreid)
                # 総計ポイント.
                wholedata = RankingGachaWholeData.getByKey(master.id)
                if wholedata:
                    scoredata.firstpoint = wholedata.point
            setattr(scoredata, att, value)
            model_mgr.set_save(scoredata)
            
            if ranking:
                def writeEnd():
                    ranking.create(master.id, uid, value).save()
                model_mgr.add_write_end_method(writeEnd)
            
            model_mgr.write_all()
            return model_mgr
        
        ranking = None
        if is_single:
            att = 'single'
            ranking = RankingGachaSingleRanking
        else:
            att = 'total'
            if master.is_support_totalranking:
                ranking = RankingGachaTotalRanking
        
        db_util.run_in_transaction(tr, att, ranking, uid, master, value).write_end()
        
        return True
    
    def _proc_update_rankinggacha_singlepoint(self):
        """ランキングガチャの単発Ptを変更.
        """
        is_success = self.__update_rankinggacha_singlepoint(True)
        if is_success:
            self.putAlertToHtmlParam(u'単発Ptを変更しました.' , alert_code=AlertCode.SUCCESS)
    
    def _proc_update_rankinggacha_totalpoint(self):
        """ランキングガチャの累計Ptを変更.
        """
        is_success = self.__update_rankinggacha_singlepoint(False)
        if is_success:
            self.putAlertToHtmlParam(u'累計Ptを変更しました.' , alert_code=AlertCode.SUCCESS)

    def _proc_update_playertradeshop_point(self):
        """所持交換ポイントの変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return False
        value = self.__check_intvalue(self.request.get('_value'), min_value=1)
        if value is None:
            return False

        model_mgr = ModelRequestMgr()
        player_trade_shop = BackendApi.find_or_create_instance_PlayerTradeShop(model_mgr, uid , None)

        def tr_write(playerdata):
            playerdata.point = value
            model_mgr.set_save(playerdata)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr_write, player_trade_shop).write_end()

        self.putAlertToHtmlParam(u'所持交換ポイントを変更しました.' , alert_code=AlertCode.SUCCESS)

    def _proc_reset_tradeshopplayerdata(self):
        """交換回数の初期化.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return False

        model_mgr = ModelRequestMgr()
        playerdatalist = TradeShopPlayerData.fetchValues(filters={'uid':uid}, using=settings.DB_DEFAULT)

        def tr_write(playerdatalist):
            for data in playerdatalist:
                data.cnt = 0
                model_mgr.set_save(data)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr_write, playerdatalist).write_end()

        self.putAlertToHtmlParam(u'uid: {} の交換記録を初期化しました.'.format(uid), alert_code=AlertCode.SUCCESS)

    def _proc_reset_reprintticket_tradeshopplayerdata(self):
        """復刻チケット交換回数の初期化.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return False

        model_mgr = ModelRequestMgr()
        playerdatalist = ReprintTicketTradeShopPlayerData.fetchValues(filters={'uid':uid}, using=settings.DB_DEFAULT)

        def tr_write(playerdatalist):
            for data in playerdatalist:
                data.cnt = 0
                model_mgr.set_save(data)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr_write, playerdatalist).write_end()

        self.putAlertToHtmlParam(u'uid: {} の交換記録を初期化しました.'.format(uid), alert_code=AlertCode.SUCCESS)


    def _proc_delete_rankinggacha_score(self):
        """ランキングガチャの累計Ptを変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(RankingGachaMaster, self.request.get('_mid'))
        if master is None:
            return
        
        def tr(uid, master):
            model_mgr = ModelRequestMgr()
            
            scoredata = RankingGachaScore.getByKey(RankingGachaScore.makeID(uid, master.id))
            if scoredata:
                model_mgr.set_delete(scoredata)
                
                def writeEnd():
                    RankingGachaSingleRanking.create(master.id, uid, 0).delete()
                    RankingGachaTotalRanking.create(master.id, uid, 0).delete()
                model_mgr.add_write_end_method(writeEnd)
            
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, uid, master).write_end()
        
        self.putAlertToHtmlParam(u'未プレイ状態に変更しました.' , alert_code=AlertCode.SUCCESS)
    
    def _proc_send_present(self):
        """プレゼントを送信.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        value = self.request.get('_value')
        
        try:
            itype = int(self.request.get('_itype'))
        except:
            self.putAlertToHtmlParam(u'不正なアイテムタイプです.' , alert_code=AlertCode.ERROR)
            return
        
        try:
            inum = int(self.request.get('_num', '1'))
            if inum < 1:
                raise CabaretError()
            
            present_num = int(self.request.get('_present_num', '1'))
            if present_num < 1:
                raise CabaretError()
        except:
            self.putAlertToHtmlParam(u'個数と回数は自然数で入力してください.' , alert_code=AlertCode.ERROR)
            return
        
        if itype in (Defines.ItemType.GOLD, Defines.ItemType.GACHA_PT, Defines.ItemType.RAREOVERTICKET, 
                     Defines.ItemType.MEMORIESTICKET, Defines.ItemType.TRYLUCKTICKET, Defines.ItemType.GACHATICKET,
                     Defines.ItemType.PLATINUM_PIECE, Defines.ItemType.CRYSTAL_PIECE):
            value = int(value)
            if value < 1:
                self.putAlertToHtmlParam(u'値が不正です.%d' % value, alert_code=AlertCode.ERROR)
                return
            keys = {
                Defines.ItemType.GOLD : 'gold',
                Defines.ItemType.GACHA_PT : 'gachapt',
                Defines.ItemType.RAREOVERTICKET : 'rareoverticket',
                Defines.ItemType.MEMORIESTICKET : 'memoriesticket',
                Defines.ItemType.TRYLUCKTICKET : 'ticket',
                Defines.ItemType.GACHATICKET : 'gachaticket',
                Defines.ItemType.PLATINUM_PIECE : 'platinum_piece_num',
                Defines.ItemType.CRYSTAL_PIECE : 'crystal_piece_num',
            }
            args = {
                keys[itype] : value
            }
            prize = PrizeData.create(**args)
        elif itype == Defines.ItemType.CARD:
            master = self.__check_master_id(CardMaster, value)
            if master is None:
                return
            prize = PrizeData.create(cardid=master.id, cardnum=inum)
        elif itype == Defines.ItemType.ITEM:
            master = self.__check_master_id(ItemMaster, value)
            if master is None:
                return
            prize = PrizeData.create(itemid=master.id, itemnum=inum)
        elif itype == Defines.ItemType.EVENT_GACHATICKET:
            master = self.__check_master_id(RaidEventMaster, value)
            if master is None:
                return
            prize = PrizeData.create(eventticket_id=master.id, eventticket_num=inum)
        elif itype == Defines.ItemType.ADDITIONAL_GACHATICKET:
            prize = PrizeData.create(additional_ticket_id=int(value), additional_ticket_num=inum)
        else:
            self.putAlertToHtmlParam(u'未対応のタイプです.%d' % itype, alert_code=AlertCode.ERROR)
            return
        
        def tr(prizelist):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, 0)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr, [prize]*present_num)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'ユーザID:%dにプレゼントを送信しました.' % uid, alert_code=AlertCode.SUCCESS)
    
    def _proc_flush_present(self):
        """プレゼントを全削除.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        idlist = BackendApi.get_present_idlist(uid)
        
        def tr(presentidlist):
            model_mgr = ModelRequestMgr()
            
            presentlist = BackendApi.get_presents(presentidlist, model_mgr)
            redis_present_list = []
            for present in presentlist:
                redis_present_list.append((present.id, present.present.itype))
                model_mgr.set_delete(present.present)
            def writeEnd():
                redisdb = RedisModel.getDB()
                pipe = redisdb.pipeline()
                for presentid, itype in redis_present_list:
                    BackendApi.remove_present(uid, presentid, itype, pipe)
                pipe.execute()
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr, idlist)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'ユーザID:%dのプレゼントを削除しました.' % uid, alert_code=AlertCode.SUCCESS)
    
    def _proc_change_itemnum(self):
        """アイテム所持数変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(ItemMaster, self.request.get('_mid'))
        if master is None:
            return
        num = self.request.get('_num') or ""
        if not num.isdigit() or int(num) < 0:
            self.putAlertToHtmlParam(u'所持数は0以上の数値を指定してください.', alert_code=AlertCode.ERROR)
            return
        num = int(num)
        is_pay = bool(int(self.request.get('_pay') or '0'))
        str_pay = u'課金分' if is_pay else u'無料分'
        
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                if is_pay:
                    model.rnum = num
                else:
                    model.vnum = num
            model_mgr.add_forupdate_task(Item, Item.makeID(uid, master.id), forUpdate)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'ユーザID:%dの%sの%s所持数を%dにしました.' % (uid, master.name, str_pay, num), alert_code=AlertCode.SUCCESS)
    
    def _proc_add_treasure(self):
        """宝箱付与.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        treasure_type = int(self.request.get('_type'))
        
        master_cls = TreasureUtil.get_master_cls(treasure_type)
        master = self.__check_master_id(master_cls, self.request.get('_mid'))
        if master is None:
            return
        
        num = self.request.get('_num') or ""
        if not num.isdigit() or int(num) < 1:
            self.putAlertToHtmlParam(u'付与数は1以上の数値を指定してください.', alert_code=AlertCode.ERROR)
            return
        num = int(num)
        
        def tr():
            model_mgr = ModelRequestMgr()
            for _ in xrange(num):
                BackendApi.tr_add_treasure(model_mgr, uid, treasure_type, master.id)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'ユーザーID:%dに%s(ID:%d)を%d個付与しました' % (uid, Defines.TreasureType.NAMES.get(treasure_type), master.id, num), alert_code=AlertCode.SUCCESS)
    
    def _proc_update_trade_cnt(self):
        """秘宝交換回数変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        master = self.__check_master_id(TradeMaster, self.request.get('_mid'))
        if master is None:
            return
        elif master.stock == 0:
            self.putAlertToHtmlParam(u'交換回数を変更できない秘宝交換です.', alert_code=AlertCode.ERROR)
            return
        
        num = self.request.get('_num') or ""
        if not num.isdigit() or int(num) < 0:
            self.putAlertToHtmlParam(u'付与数は0以上の数値を指定してください.', alert_code=AlertCode.ERROR)
            return
        num = int(num)
        
        def tr():
            model_mgr = ModelRequestMgr()
            ins = TradePlayerData.makeInstance(TradePlayerData.makeID(uid, master.id))
            ins.cnt = num
            model_mgr.set_save(ins)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'ユーザーID:%dの交換ID:%dの交換回数を%dにしました' % (uid, master.id, num), alert_code=AlertCode.SUCCESS)
    
    def _proc_change_scoutclearflag(self):
        """スカウトのクリアフラグをたてる.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(ScoutMaster, self.request.get('_mid'))
        if master is None:
            return
        
        model_mgr = self.getModelMgr()
        def searchArea(areaid):
            scoutidlist = []
            areaidlist = []
            if 0 < areaid:
                areaidlist.append(areaid)
                area = BackendApi.get_area(model_mgr, areaid)
                if area:
                    scoutidlist.extend(BackendApi.get_scoutidlist_by_area(model_mgr, areaid))
                    if 0 < area.opencondition:
                        aidlist, sidlist = searchArea(area.opencondition)
                        areaidlist.extend(aidlist)
                        scoutidlist.extend(sidlist)
            return areaidlist, scoutidlist
        def searchScout(scout):
            arr = [scout.id]
            if 0 < scout.opencondition:
                prevscout = model_mgr.get_model(ScoutMaster, scout.opencondition)
                if prevscout:
                    arr.extend(searchScout(prevscout))
            return arr
        area = BackendApi.get_area(model_mgr, master.area)
        areaidlist, scoutidlist = searchArea(area.opencondition)
        scoutidlist.extend(searchScout(master))
        scoutidlist = list(set(scoutidlist))
        
        def tr(uid, areaidlist, scoutidlist):
            model_mgr = ModelRequestMgr()
            
            # エリアのクリアフラグ.
            def forUpdateArea(model, inserted):
                pass
            for areaid in areaidlist:
                model_mgr.add_forupdate_task(AreaPlayData, AreaPlayData.makeID(uid, areaid), forUpdateArea)
            
            # スカウトのクリアフラグ.
            def forUpdateScout(model, inserted):
                master = model_mgr.get_model(ScoutMaster, model.mid)
                model.progress = max(master.execution, model.progress)
            for scoutid in scoutidlist:
                model_mgr.add_forupdate_task(ScoutPlayData, ScoutPlayData.makeID(uid, scoutid), forUpdateScout)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr, uid, areaidlist, scoutidlist)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'%sまでのクリアフラグを立てました.' % master.name, alert_code=AlertCode.SUCCESS)
    
    def _proc_flush_scoutclearflag(self):
        """スカウトのクリアフラグを消す.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        def tr():
            model_mgr = ModelRequestMgr()
            
            # エリアのクリアフラグ.
            for model in AreaPlayData.fetchByOwner(uid):
                model_mgr.set_delete(model)
            
            # スカウトのクリアフラグ.
            for model in ScoutPlayData.fetchByOwner(uid):
                model_mgr.set_delete(model)
            
            def writeEnd():
                LastViewArea.create(uid).delete()
            model_mgr.add_write_end_method(writeEnd)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'クリアフラグを全て消しました.', alert_code=AlertCode.SUCCESS)
    
    def __happeningend(self, uid):
        """ハプニング終了.
        """
        model_mgr = self.getModelMgr()
        happeningid = BackendApi.get_current_happeningid(model_mgr, uid)
        
        happeningset = None
        if happeningid:
            happeningset = BackendApi.get_happening(model_mgr, happeningid)
        
        if happeningset and not happeningset.happening.is_end():
            def tr():
                model_mgr = ModelRequestMgr()
                happening = model_mgr.get_model_forupdate(Happening, happeningid)
                happening.etime = OSAUtil.get_now()
                happeningset = HappeningSet(happening, BackendApi.get_happeningmaster(model_mgr, happening.mid))
                BackendApi.tr_happening_missed(model_mgr, happeningset.id)
                model_mgr.set_save(happening)
                model_mgr.write_all()
                return model_mgr
            model_mgr = db_util.run_in_transaction(tr)
            model_mgr.write_end()
    
    def _proc_happeningstart(self):
        """ハプニングを発生させる.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(HappeningMaster, self.request.get('_mid'))
        if master is None:
            return
        raideventmaster = self.__check_master_id(RaidEventMaster, self.request.get('_event'), blank=True)
        if raideventmaster is None:
            raideventid = 0
        else:
            raideventid = raideventmaster.id
        
        champagne = self.request.get('_champagne') == '1'
        
        # 一度終了させる.
        self.__happeningend(uid)
        
        def tr():
            model_mgr = ModelRequestMgr()
            playerexp = BackendApi.get_model(model_mgr, PlayerExp, uid)
            BackendApi.tr_create_happening(model_mgr, uid, master.id, playerexp.level, eventvalue=HappeningUtil.make_raideventvalue(raideventid), champagne=champagne)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'ハプニング:%sを発生させました.' % master.name, alert_code=AlertCode.SUCCESS)
    
    def _proc_happeningend(self):
        """ハプニングを終了させる.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        self.__happeningend(uid)
        
        self.putAlertToHtmlParam(u'ハプニングを終了させました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_raidstart(self):
        """発生中のハプニングにレイドを発生させる.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        model_mgr = self.getModelMgr()
        happeningid = BackendApi.get_current_happeningid(model_mgr, uid)
        
        happeningset = None
        if happeningid:
            happeningset = BackendApi.get_happening(model_mgr, happeningid)
        
        champagne = self.request.get('_champagne') == '1'
        
        if happeningset and not happeningset.happening.is_end():
            raidboss = BackendApi.get_raid(model_mgr, happeningid)
            if not raidboss:
                def tr():
                    model_mgr = ModelRequestMgr()
                    happening = Happening.getByKeyForUpdate(happeningset.id)
                    happening.progress = happeningset.master.execution
                    BackendApi.tr_create_raid(model_mgr, happeningset.master, happening, champagne=champagne)
                    model_mgr.set_save(happening)
                    model_mgr.write_all()
                    return model_mgr
                model_mgr = db_util.run_in_transaction(tr)
                model_mgr.write_end()
            
            self.putAlertToHtmlParam(u'レイドを発生させました.', alert_code=AlertCode.SUCCESS)
        else:
            self.putAlertToHtmlParam(u'まずハプニングを発生させてください.', alert_code=AlertCode.ERROR)
    
    def _proc_change_raiddestroycnt(self):
        """レイド接客成功回数を変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(RaidMaster, self.request.get('_mid'))
        if master is None:
            return
        value = self.__check_intvalue(self.request.get('_value'))
        if value is None:
            return
        
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.cnt = value
            model_mgr.add_forupdate_task(RaidDestroyCount, RaidDestroyCount.makeID(uid, master.id), forUpdate)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'%sの接客成功回数を%sに変更しました.' % (master.name, value), alert_code=AlertCode.SUCCESS)
    
    def _delete_friendstate(self, uid, oid):
        """フレンドの状態を削除.
        """
        model_mgr = self.getModelMgr()
        func = None
        args = None
        if BackendApi.check_friend(uid, oid, model_mgr):
            func = BackendApi.tr_delete_friend
            args = uid, oid
        elif BackendApi.check_friendrequest_send(uid, oid, model_mgr):
            func = BackendApi.tr_delete_friendrequest
            args = uid, oid
        elif BackendApi.check_friendrequest_receive(uid, oid, model_mgr):
            func = BackendApi.tr_delete_friendrequest
            args = oid, uid
        else:
            return
        def tr(func, args):
            model_mgr = ModelRequestMgr()
            func(model_mgr, *args)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr, func, args)
        model_mgr.write_end()
    
    def _proc_delete_friendstate(self):
        """フレンドの状態を削除.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        oid = self.__check_request_userid(self.request.get('_oid'))
        if uid is None or oid is None:
            self.putAlertToHtmlParam(u'ユーザーが存在しません.', alert_code=AlertCode.ERROR)
            return
        
        self._delete_friendstate(uid, oid)
        
        self.putAlertToHtmlParam(u'フレンド・フレンド申請を削除しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_change_friendstate(self):
        """フレンドの状態を変更する.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        oid = self.__check_request_userid(self.request.get('_oid'))
        state = self.request.get(Defines.URLQUERY_STATE) or ''
        if uid is None or oid is None:
            self.putAlertToHtmlParam(u'ユーザーが存在しません.', alert_code=AlertCode.ERROR)
            return
        elif uid == oid:
            self.putAlertToHtmlParam(u'同一ユーザーを指定しないでください.', alert_code=AlertCode.ERROR)
            return
        elif not state or not state.isdigit() or not int(state) in (Defines.FriendState.ACCEPT, Defines.FriendState.SEND):
            self.putAlertToHtmlParam(u'フレンド状態が正しくありません.', alert_code=AlertCode.ERROR)
            return
        
        state = int(state)
        
        # まず削除.
        self._delete_friendstate(uid, oid)
        
        player, o_player = BackendApi.get_players(self, [uid, oid], [PlayerFriend])
        
        def tr_request(player, o_player):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_friendrequest(model_mgr, player, o_player)
            model_mgr.write_all()
            return model_mgr
        
        def tr_accept(uid, oid):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_friend(model_mgr, uid, oid)
            model_mgr.write_all()
            return model_mgr
        
        # 申請する.
        try:
            model_mgr = db_util.run_in_transaction(tr_request, player, o_player)
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.OVER_LIMIT:
                self.putAlertToHtmlParam(u'フレンド上限を超えています.', alert_code=AlertCode.ERROR)
                return
        
        if state == Defines.FriendState.ACCEPT:
            # フレンドにする.
            model_mgr = db_util.run_in_transaction(tr_accept, oid, uid)
            model_mgr.write_end()
            self.putAlertToHtmlParam(u'フレンドにしました.', alert_code=AlertCode.SUCCESS)
        else:
            self.putAlertToHtmlParam(u'フレンド申請しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_change_battlerank(self):
        """ランク情報を変更する.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            self.putAlertToHtmlParam(u'ユーザーが存在しません.', alert_code=AlertCode.ERROR)
            return
        rankmaster = self.__check_master_id(BattleRankMaster, self.request.get('_rank'))
        if rankmaster is None:
            return
        try:
            win = int(self.request.get('_win'))
            times = int(self.request.get('_times'))
        except:
            self.putAlertToHtmlParam(u'連勝数とノルマ達成回数は数字で指定してください.', alert_code=AlertCode.ERROR)
            return
        
        model_mgr = self.getModelMgr()
        battleplayer = BackendApi.get_battleplayer(model_mgr, uid, get_instance=True)
        battleplayer.rank = rankmaster.id
        battleplayer.win_continuity = win
        battleplayer.times = times
        
        model_mgr = ModelRequestMgr()
        model_mgr.set_save(battleplayer)
        model_mgr.write_all()
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'ランク情報を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_set_battleopponent_change_count(self):
        """対戦相手変更回数を設定.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            self.putAlertToHtmlParam(u'ユーザーが存在しません.', alert_code=AlertCode.ERROR)
            return
        try:
            cnt = int(self.request.get('_cnt'))
        except:
            self.putAlertToHtmlParam(u'変更回数は数字で指定してください.', alert_code=AlertCode.ERROR)
            return
        
        model_mgr = self.getModelMgr()
        battleplayer = BackendApi.get_battleplayer(model_mgr, uid, get_instance=True)
        battleplayer.change_cnt = cnt
        battleplayer.rankopplist = []
        if battleplayer.opponent:
            battleplayer.rankopplist.append(battleplayer.opponent)
        
        model_mgr = ModelRequestMgr()
        model_mgr.set_save(battleplayer)
        model_mgr.write_all()
        model_mgr.write_end()
        
        self.putAlertToHtmlParam(u'対戦相手変更回数を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_change_raideventdata(self):
        """イベントレイドのパラメータを操作.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(RaidEventMaster, self.request.get('_mid'))
        if master is None:
            return
        value = self.__check_intvalue(self.request.get('_value'))
        if value is None:
            return
        target = self.request.get('_target')
        
        def tr():
            model_mgr = ModelRequestMgr()
            
            scorerecord = BackendApi.get_raidevent_scorerecord(model_mgr, master.id, uid)
            if scorerecord is None:
                scorerecord = RaidEventScore.makeInstance(RaidEventScore.makeID(uid, master.id))
            setattr(scorerecord, target, value)
            model_mgr.set_save(scorerecord)
            if target == 'point_total':
                def writeEnd():
                    RaidEventRanking.create(master.id, uid, scorerecord.point_total).save()
                    if BackendApi.check_raidevent_beginer(model_mgr, uid, master, using=settings.DB_READONLY):
                        RaidEventRankingBeginer.create(master.id, uid, scorerecord.point_total).save()
                model_mgr.add_write_end_method(writeEnd)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        self.putAlertToHtmlParam(u'レイドイベントのパラメータを変更しました.%s=%s' % (target, value), alert_code=AlertCode.SUCCESS)
    
    def _proc_set_champagne_call(self):
        """SHOWTIME切り替え.
        """
        model_mgr = self.getModelMgr()
        
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        is_champagne_call = self.request.get('_flag') == '1'
        
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        eventid = config.mid
        eventmaster = BackendApi.get_raideventmaster(model_mgr, eventid, using=settings.DB_READONLY)
        
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                now = OSAUtil.get_now()
                if is_champagne_call:
                    model.setStartChampagneCall(eventid, eventmaster.champagne_time, now)
                else:
                    model.etime = now
            model_mgr.add_forupdate_task(RaidEventChampagne, uid, forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        self.putAlertToHtmlParam(u'レイドイベントのSHOWTIME状態を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_set_champagne_num(self):
        """シャンパン数を変更.
        """
        model_mgr = self.getModelMgr()
        
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        value = self.__check_intvalue(self.request.get('_value'))
        if value is None:
            return
        
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        eventid = config.mid
        
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.setChampagneNum(eventid, value)
            model_mgr.add_forupdate_task(RaidEventChampagne, uid, forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        self.putAlertToHtmlParam(u'レイドイベントのシャンパン数を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_set_material_num(self):
        """素材数を変更.
        """
        model_mgr = self.getModelMgr()
        
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        nums = {}
        for i in xrange(Defines.RAIDEVENT_MATERIAL_KIND_MAX):
            value = self.__check_intvalue(self.request.get('_value%d' % i))
            if value is None:
                return
            nums[i] = value
        
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        eventid = config.mid
        
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                for k,v in nums.items():
                    model.setMaterialNum(eventid, k, v)
            model_mgr.add_forupdate_task(RaidEventMaterialData, uid, forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        self.putAlertToHtmlParam(u'レイドイベントの贈り物数を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_set_material_trade_num(self):
        """交換所の贈り物交換回数を変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(RaidEventRecipeMaster, self.request.get('_mid'))
        if master is None:
            return
        cnt = self.__check_intvalue(self.request.get('_value'))
        if cnt is None:
            return
        def tr():
            model_mgr = ModelRequestMgr()
            mixdata = BackendApi.get_raidevent_mixdata(model_mgr, uid, master.id)
            if mixdata is None:
                mixdata = RaidEventMixData.makeInstance(RaidEventMixData.makeID(uid, master.id))
            mixdata.setCount(master.eventid, cnt)
            model_mgr.set_save(mixdata)
            model_mgr.write_all()
            model_mgr.write_end()
        db_util.run_in_transaction(tr)
        
        self.putAlertToHtmlParam(u'レイドイベントの贈り物回数を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_change_opening(self):
        """オープニング閲覧フラグを操作.
        """
        model_mgr = self.getModelMgr()
        
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(RaidEventMaster, self.request.get('_mid'))
        if master is None:
            return
        flag_op = self.request.get('_flag_op') == '1'
        flag_ep = self.request.get('_flag_ep') == '1'
        
        mid = master.id
        opvtime = None
        epvtime = None
        if flag_op:
            opvtime = OSAUtil.get_now()
        else:
            opvtime = OSAUtil.get_datetime_min()
        
        if flag_ep:
            epvtime = opvtime
        else:
            epvtime = OSAUtil.get_datetime_min()
        
        if flag_op or flag_ep:
            BackendApi.update_raideventflagrecord(model_mgr, mid, uid, opvtime=opvtime, epvtime=epvtime)
        else:
            model_mgr = self.getModelMgr()
            flagrecord = BackendApi.get_raidevent_flagrecord(model_mgr, mid, uid)
            if flagrecord is not None:
                BackendApi.update_raideventflagrecord(model_mgr, mid, uid, opvtime=opvtime, epvtime=epvtime)
        
        self.putAlertToHtmlParam(u'シナリオ閲覧フラグを変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_change_boss_ec(self):
        """大ボス出現閲覧フラグを操作.
        """
        model_mgr = self.getModelMgr()
        
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(RaidEventMaster, self.request.get('_mid'))
        if master is None:
            return
        flag = self.request.get('_flag') == '1'
        
        mid = master.id
        if flag:
            BackendApi.update_raideventunwillingflagrecord(mid, uid, bigbosstime=OSAUtil.get_now())
        else:
            model_mgr = self.getModelMgr()
            flagrecord = BackendApi.get_raidevent_unwillingflagrecord(model_mgr, mid, uid)
            if flagrecord is not None:
                BackendApi.update_raideventunwillingflagrecord(mid, uid, bigbosstime=OSAUtil.get_datetime_min())
        
        self.putAlertToHtmlParam(u'大ボス出現閲覧フラグを変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_change_timebonus(self):
        """タイムボーナス閲覧フラグを操作.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(RaidEventMaster, self.request.get('_mid'))
        if master is None:
            return
        
        model_mgr = self.getModelMgr()
        mid = master.id
        flagrecord = BackendApi.get_raidevent_flagrecord(model_mgr, mid, uid)
        if flagrecord is not None:
            BackendApi.update_raideventflagrecord(model_mgr, mid, uid, tbvtime=OSAUtil.get_datetime_min())
        
        self.putAlertToHtmlParam(u'タイムボーナス閲覧フラグを変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_change_destroyprize(self):
        """報酬受取りフラグを操作.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(RaidEventMaster, self.request.get('_mid'))
        if master is None:
            return
        value = self.__check_intvalue(self.request.get('_value'))
        if value is None:
            return
        big = self.request.get('_big') == '1'
        if big:
            prizes = dict(master.destroyprizes_big)
            target = 'destroyprize_flags'
        else:
            prizes = dict(master.destroyprizes)
            target = 'destroyprize_big_flags'
        
        flags = []
        for d in prizes.keys():
            if d <= value:
                flags.append(d)
        
        def tr():
            model_mgr = ModelRequestMgr()
            mid = master.id
            flagrecord = BackendApi.get_raidevent_flagrecord(model_mgr, mid, uid)
            if flagrecord is None:
                flagrecord = RaidEventFlags.makeInstance(RaidEventFlags.makeID(uid, mid))
            setattr(flagrecord, target, flags)
            model_mgr.set_save(flagrecord)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        self.putAlertToHtmlParam(u'報酬受取りフラグを変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_change_raideventstage(self):
        """レイドイベントのステージ情報変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(RaidEventMaster, self.request.get('_mid'))
        if master is None:
            return
        value = self.__check_intvalue(self.request.get('_value'))
        if value is None:
            return
        
        target = self.request.get('_target')
        if target == 'stage':
            self.__change_eventstage_stagenumber(RaidEventScoutStageMaster, RaidEventScoutPlayData, master.id, uid, value)
        elif target == 'progress':
            self.__change_eventstage_progress(RaidEventScoutStageMaster, RaidEventScoutPlayData, master.id, uid, value)

    def _proc_change_raideventscore(self):
        """レイドイベントのパラメータ変更.
        """
        model_mgr = ModelRequestMgr()
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return

        mid = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY).mid
        target = self.request.get('_target')
        if target is None:
            return

        value = self.__check_intvalue(self.request.get('_value'))
        if target is None:
            return

        record = model_mgr.get_model(RaidEventScore, RaidEventScore.makeID(uid, mid), using=settings.DB_DEFAULT)
        if record is not None:
            if target == 'point':
                record.point = value
            elif target == 'point_total':
                record.point_total = value
            elif target == 'destroy':
                record.destroy = value
            elif target == 'destroy_big':
                record.destroy_big = value
            model_mgr.set_save(record)
            model_mgr.write_all()
            model_mgr.write_end()
        else:
            self.putAlertToHtmlParam(u'現在開催中のイベントデータが存在しません.uid={}'.format(uid), alert_code=AlertCode.ERROR)

    def _proc_change_scouteventscore(self):
        """スカウトイベントのパラメータを変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        master = self.__check_master_id(ScoutEventMaster, self.request.get('_mid'))
        value = self.__check_intvalue(self.request.get('_value'))
        if uid is None or master is None or value is None:
            return
        
        target = self.request.get('_target')
        if target == "point":
            def tr():
                model_mgr = ModelRequestMgr()
                def forUpdate(model, inserted):
                    model.point = value
                    model.point_total = value
                model_mgr.add_forupdate_task(ScoutEventScore, ScoutEventScore.makeID(uid, master.id), forUpdate)
                
                def writeEnd():
                    ScoutEventRanking.create(master.id, uid, value).save()
                    if BackendApi.check_scoutevent_beginer(model_mgr, uid, master, using=settings.DB_READONLY):
                        ScoutEventRankingBeginer.create(master.id, uid, value).save()
                model_mgr.add_write_end_method(writeEnd)
                
                model_mgr.write_all()
                return model_mgr
            db_util.run_in_transaction(tr).write_end()
            self.putAlertToHtmlParam(u'獲得電話番号を変更しました.point=%s' % value, alert_code=AlertCode.SUCCESS)
        elif target == "stage":
            self.__change_eventstage_stagenumber(ScoutEventStageMaster, ScoutEventPlayData, master.id, uid, value)
        elif target == "progress":
            self.__change_eventstage_progress(ScoutEventStageMaster, ScoutEventPlayData, master.id, uid, value)
        elif target == "producepoint":
            def tr():
                model_mgr = ModelRequestMgr()
                def forUpdate(model, inserted):
                    model.point = value
                model_mgr.add_forupdate_task(ScoutEventPresentNum, ScoutEventPresentNum.makeID(uid, master.id), forUpdate)
                model_mgr.write_all()
                return model_mgr
            db_util.run_in_transaction(tr).write_end()
            self.putAlertToHtmlParam(u'現在の所持ハート数を変更しました.', alert_code=AlertCode.SUCCESS)
        elif target == "gachapoint":
            def tr():
                model_mgr = ModelRequestMgr()
                def forUpdate(model, inserted):
                    model.point_gacha = value
                model_mgr.add_forupdate_task(ScoutEventScore, ScoutEventScore.makeID(uid, master.id), forUpdate)
                model_mgr.write_all()
                return model_mgr
            db_util.run_in_transaction(tr).write_end()
            self.putAlertToHtmlParam(u'現在の所持カカオ数を変更しました.', alert_code=AlertCode.SUCCESS)
        elif target == "tip":
            def tr():
                model_mgr = ModelRequestMgr()
                def forUpdate(model, inserted):
                    model.tip = value
                model_mgr.add_forupdate_task(ScoutEventScore, ScoutEventScore.makeID(uid, master.id), forUpdate)
                model_mgr.write_all()
                return model_mgr
            db_util.run_in_transaction(tr).write_end()
            self.putAlertToHtmlParam(u'現在の所持チップ数を変更しました.', alert_code=AlertCode.SUCCESS)
        else:
            self.putAlertToHtmlParam(u'未対応の操作です.', alert_code=AlertCode.ERROR)
        
    def _proc_set_scoutevent_fever(self):
        """フィーバーを設定.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        master = self.__check_master_id(ScoutEventMaster, self.request.get('_mid'))
        value = self.__check_intvalue(self.request.get('_value'))
        if uid is None or master is None or value is None:
            return
        
        fever_end_time = OSAUtil.get_now() + datetime.timedelta(seconds=value)
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.feveretime = fever_end_time
            model_mgr.add_forupdate_task(ScoutEventPlayData, ScoutEventPlayData.makeID(uid, master.id), forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        self.putAlertToHtmlParam(u'フィーバー残り時間を設定しました.', alert_code=AlertCode.SUCCESS)
        
    def _proc_reset_scoutevent_presentnum(self):
        """スカウトイベントプレゼント数をリセット.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        master = self.__check_master_id(ScoutEventMaster, self.request.get('_mid'))
        if uid is None or master is None:
            return
        
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.nums = {}
            model_mgr.add_forupdate_task(ScoutEventPresentNum, ScoutEventPresentNum.makeID(uid, master.id), forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        self.putAlertToHtmlParam(u'プレゼント数をリセットしました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_change_scoutevent_opening(self):
        """オープニング閲覧フラグを操作.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(ScoutEventMaster, self.request.get('_mid'))
        if master is None:
            return
        flag_op = self.request.get('_flag_op') == '1'
        flag_ep = self.request.get('_flag_ep') == '1'
        
        mid = master.id
        opvtime = None
        epvtime = None
        if flag_op:
            opvtime = OSAUtil.get_now()
        else:
            opvtime = OSAUtil.get_datetime_min()
        
        if flag_ep:
            epvtime = opvtime
        else:
            epvtime = OSAUtil.get_datetime_min()
        
        if flag_op or flag_ep:
            BackendApi.update_scouteventflagrecord(mid, uid, opvtime=opvtime, epvtime=epvtime)
        else:
            model_mgr = self.getModelMgr()
            flagrecord = BackendApi.get_scoutevent_flagrecord(model_mgr, mid, uid)
            if flagrecord is not None:
                BackendApi.update_scouteventflagrecord(mid, uid, opvtime=opvtime, epvtime=epvtime)
        
        self.putAlertToHtmlParam(u'シナリオ閲覧フラグを変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_set_lovetime(self):
        """逢引ラブタイム状態変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        eventmaster = self.__check_master_id(ScoutEventMaster, self.request.get('_mid'))
        if eventmaster is None:
            return
        
        is_lovetime = self.request.get('_flag') == '1'
        
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                now = OSAUtil.get_now()
                if is_lovetime:
                    model.set_lovetime(now, eventmaster.lovetime_timelimit)
                else:
                    model.lovetime_etime = now
            model_mgr.add_forupdate_task(ScoutEventPlayData, ScoutEventPlayData.makeID(uid, eventmaster.id), forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        self.putAlertToHtmlParam(u'スカウトイベントの逢引ラブタイム状態を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_set_star(self):
        """星の数を変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        eventmaster = self.__check_master_id(ScoutEventMaster, self.request.get('_mid'))
        if eventmaster is None:
            return
        
        star = self.__check_intvalue(self.request.get('_num'), max_value=eventmaster.lovetime_star - 1)
        if star is None:
            return
        
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.star = star
            model_mgr.add_forupdate_task(ScoutEventPlayData, ScoutEventPlayData.makeID(uid, eventmaster.id), forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        self.putAlertToHtmlParam(u'スカウトイベントの星の所持数を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_set_tanzaku(self):
        """短冊の所持数を変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        eventmaster = self.__check_master_id(ScoutEventMaster, self.request.get('_mid'))
        if eventmaster is None:
            return
        
        tanzaku_number = self.__check_intvalue(self.request.get('_tanzaku'))
        if tanzaku_number is None:
            return
        
        tanzakumaster = self.__check_master_id(ScoutEventTanzakuCastMaster, ScoutEventTanzakuCastMaster.makeID(eventmaster.id, tanzaku_number))
        if tanzakumaster is None:
            return
        
        num = self.__check_intvalue(self.request.get('_num'))
        
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.set_tanzaku(tanzaku_number, num)
            model_mgr.add_forupdate_task(ScoutEventTanzakuCastData, ScoutEventTanzakuCastData.makeID(uid, eventmaster.id), forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        self.putAlertToHtmlParam(u'スカウトイベントの短冊の所持数を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_set_tip(self):
        """チップ投入数を変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        eventmaster = self.__check_master_id(ScoutEventMaster, self.request.get('_mid'))
        if eventmaster is None:
            return
        
        tanzaku_number = self.__check_intvalue(self.request.get('_tanzaku'))
        if tanzaku_number is None:
            return
        
        tanzakumaster = self.__check_master_id(ScoutEventTanzakuCastMaster, ScoutEventTanzakuCastMaster.makeID(eventmaster.id, tanzaku_number))
        if tanzakumaster is None:
            return
        
        num = self.__check_intvalue(self.request.get('_num'))
        
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.set_tip(tanzaku_number, num)
            model_mgr.add_forupdate_task(ScoutEventTanzakuCastData, ScoutEventTanzakuCastData.makeID(uid, eventmaster.id), forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        self.putAlertToHtmlParam(u'スカウトイベントのチップの投入数を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_reset_battleevent_status(self):
        model_mgr = ModelRequestMgr()
        if self.__check_maintenance_mode(model_mgr) and self.__check_battleevent_before_start():
            management.call_command('battleevent_preparation')
            self.putAlertToHtmlParam(u'バトルイベントをやりなおせるように状態を初期化しました', AlertCode.SUCCESS)

    def _proc_reset_battleevent_loginbonus(self):
        """バトルイベントのログインボーナスを未受け取り状態にする.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(BattleEventMaster, self.request.get('_mid'))
        if master is None:
            return
        
        fame = self.__check_intvalue(self.request.get('_fame'))
        fame_add = self.__check_intvalue(self.request.get('_fame_add'))
        if fame_add is None:
            fame_add = 0
        
        def tr():
            model_mgr = ModelRequestMgr()
            
            def forUpdate(model, insert):
                if insert:
                    raise CabaretError(u'イベントに参加してから設定してください', CabaretError.Code.NOT_DATA)
                model.fame = fame if fame is not None else model.fame
                model.fame_next = model.fame + fame_add
                model.utime = OSAUtil.get_datetime_min()
            model_mgr.add_forupdate_task(BattleEventRank, BattleEventRank.makeID(uid, master.id), forUpdate)
            model_mgr.write_all()
            return model_mgr
        try:
            db_util.run_in_transaction(tr).write_end()
        except CabaretError, err:
            self.putAlertToHtmlParam(err.value, AlertCode.ERROR)
            return
        self.putAlertToHtmlParam(u'バトルイベントログインボーナスを受け取れるようにしました', AlertCode.SUCCESS)
    
    def _proc_set_battleevent_battletime(self):
        """バトルイベントの対戦時間を変更する.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        oid = self.__check_request_userid(self.request.get('_oid'))
        if oid is None:
            return
        str_date = self.request.get("_date")
        btime = datetime.datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S")
        
        def tr():
            model_mgr = ModelRequestMgr()
            model = BattleEventBattleTime.makeInstance(BattleEventBattleTime.makeID(uid, oid))
            model.btime = btime
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        
        self.putAlertToHtmlParam(u'バトルイベントの対戦時間を更新しました', AlertCode.SUCCESS)
    
    def _proc_change_battleevent_opening(self):
        """オープニング閲覧フラグを操作.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(BattleEventMaster, self.request.get('_mid'))
        if master is None:
            return
        flag_op = self.request.get('_flag_op') == '1'
        flag_ep = self.request.get('_flag_ep') == '1'
        
        mid = master.id
        
        opvtime = None
        epvtime = None
        if flag_op:
            opvtime = OSAUtil.get_now()
        else:
            opvtime = OSAUtil.get_datetime_min()
        
        if flag_ep:
            epvtime = opvtime
        else:
            epvtime = OSAUtil.get_datetime_min()
        
        if flag_op or flag_ep:
            BackendApi.update_battleevent_flagrecord(mid, uid, opvtime=opvtime, epvtime=epvtime)
        else:
            model_mgr = self.getModelMgr()
            flagrecord = BackendApi.get_battleevent_flagrecord(model_mgr, mid, uid)
            if flagrecord is not None:
                BackendApi.update_battleevent_flagrecord(mid, uid, opvtime=opvtime, epvtime=epvtime)
        
        self.putAlertToHtmlParam(u'シナリオ閲覧フラグを変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_change_battleeventscore(self):
        """バトルイベントのパラメータを変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        master = self.__check_master_id(BattleEventMaster, self.request.get('_mid'))
        value = self.__check_intvalue(self.request.get('_value'))
        if uid is None or master is None or value is None:
            return
        
        target = self.request.get('_target')
        if target == "point":
            def tr():
                model_mgr = ModelRequestMgr()
                
                def forUpdate(model, insert):
                    model.point = value
                    model.ltime = OSAUtil.get_now()
                model_mgr.add_forupdate_task(BattleEventScore, BattleEventScore.makeID(uid, master.id), forUpdate)
                
                model_mgr.write_all()
                return model_mgr
            db_util.run_in_transaction(tr).write_end()
            self.putAlertToHtmlParam(u'本日バトルPTを%dに設定しました' % value, AlertCode.SUCCESS)
        elif target == "point_total":
            def tr():
                model_mgr = ModelRequestMgr()
                
                def forUpdate(model, insert):
                    model.point_total = value
                model_mgr.add_forupdate_task(BattleEventScore, BattleEventScore.makeID(uid, master.id), forUpdate)
                
                def writeEnd():
                    BattleEventRanking.create(master.id, uid, value).save()
                    if BackendApi.check_battleevent_beginer(model_mgr, uid, master, using=settings.DB_READONLY):
                        BattleEventRankingBeginer.create(master.id, uid, value).save()
                model_mgr.add_write_end_method(writeEnd)
                
                model_mgr.write_all()
                return model_mgr
            db_util.run_in_transaction(tr).write_end()
            self.putAlertToHtmlParam(u'総バトルPTを%dに設定しました' % value, AlertCode.SUCCESS)
        elif target == "point_rank":
            record = BackendApi.get_battleevent_rankrecord(self.getModelMgr(), master.id, uid, using=settings.DB_READONLY)
            if record is None:
                self.putAlertToHtmlParam(u'バトルイベント未参加のユーザーは変更できません', AlertCode.ERROR)
            else:
                def tr():
                    model_mgr = ModelRequestMgr()
                    
                    def forUpdate(model, insert):
                        model.point = value
                    p_key = BattleEventScorePerRank.makeID(uid, BattleEventScorePerRank.makeMid(master.id, record.rank))
                    model_mgr.add_forupdate_task(BattleEventScorePerRank, p_key, forUpdate)
                    model_mgr.write_all()
                    return model_mgr
                db_util.run_in_transaction(tr).write_end()
                self.putAlertToHtmlParam(u'現在のランクのバトルPTを%dに設定しました' % value, AlertCode.SUCCESS)
        elif target == "fame":
            def tr():
                model_mgr = ModelRequestMgr()
                
                def forUpdate(model, insert):
                    if insert:
                        raise CabaretError(u'イベントに参加してから設定してください', CabaretError.Code.NOT_DATA)
                    model.fame = value
                    model.fame_next = value
                model_mgr.add_forupdate_task(BattleEventRank, BattleEventRank.makeID(uid, master.id), forUpdate)
                model_mgr.write_all()
                return model_mgr
            try:
                db_util.run_in_transaction(tr).write_end()
            except CabaretError, err:
                self.putAlertToHtmlParam(err.value, AlertCode.ERROR)
                return
            self.putAlertToHtmlParam(u'名声PTを%dに設定しました' % value, AlertCode.SUCCESS)
    
    def _proc_set_battleevent_present(self):
        """バトルイベント贈り物変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        presentmaster = self.__check_master_id(BattleEventPresentMaster, self.request.get('_present'))
        contentmaster = self.__check_master_id(BattleEventPresentContentMaster, self.request.get('_content'))
        point = self.__check_intvalue(self.request.get('_point'), max_value=0xffffffff)
        
        if uid is None or presentmaster is None or contentmaster is None or point is None:
            return
        
        def tr(uid, presentmaster, contentmaster):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_battleeventpresent_set_present(model_mgr, uid, presentmaster, contentmaster=contentmaster)
            
            userdata = BackendApi.get_battleeventpresent_pointdata(model_mgr, uid, presentmaster.eventid)
            userdata.point = point
            model_mgr.set_save(userdata)
            
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, uid, presentmaster, contentmaster).write_end()
        
        self.putAlertToHtmlParam(u'現在の贈り物を変更しました', AlertCode.SUCCESS)
    
    def _proc_set_battleevent_present_count(self):
        """バトルイベント贈り物出現数変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        presentmaster = self.__check_master_id(BattleEventPresentMaster, self.request.get('_present'))
        count = self.__check_intvalue(self.request.get('_count'))
        
        if uid is None or presentmaster is None or count is None:
            return
        
        def tr(uid, presentmaster, count):
            model_mgr = ModelRequestMgr()
            def forUpdateCount(model, inserted):
                model.cnt = min(count, 0xff)
            model_mgr.add_forupdate_task(BattleEventPresentCounts, BattleEventPresentCounts.makeID(uid, presentmaster.number), forUpdateCount)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, uid, presentmaster, count).write_end()
        
        self.putAlertToHtmlParam(u'%sの贈り物出現回数を%s回に変更しました' % (presentmaster.name, count), AlertCode.SUCCESS)
    
    def _proc_set_battleevent_piece_collection(self):
        """バトルイベントピース獲得状況の変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        piecemaster = self.__check_master_id(BattleEventPieceMaster, self.request.get('_mid'))
        if uid is None or piecemaster is None:
            return
        
        test_ins = BattleEventPieceCollection()
        flags = {}
        cnt = 0
        while True:
            attr = 'piece_number{}'.format(cnt)
            if not hasattr(test_ins, attr):
                break
            flags[attr] = self.request.get(attr) == "1"
            cnt += 1
        
        def tr(uid, piecemaster, flags):
            model_mgr = ModelRequestMgr()
            def forUpdateCount(model, inserted):
                for k,v in flags.items():
                    setattr(model, k, v)
            model_mgr.add_forupdate_task(BattleEventPieceCollection, BattleEventPieceCollection.makeID(uid, piecemaster.eventid, piecemaster.number), forUpdateCount)
            model_mgr.write_all()
            model_mgr.write_end()
        db_util.run_in_transaction(tr, uid, piecemaster, flags)
        
        self.putAlertToHtmlParam(u'{}のピース獲得状況を変更しました'.format(piecemaster.name), AlertCode.SUCCESS)
    
    def _proc_set_battleevent_piece_complete_cnt(self):
        """バトルイベントピースコンプ回数.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        piecemaster = self.__check_master_id(BattleEventPieceMaster, self.request.get('_mid'))
        count = self.__check_intvalue(self.request.get('_count'), max_value=piecemaster.complete_cnt_max) if piecemaster else None
        
        if uid is None or piecemaster is None or count is None:
            return
        
        def tr(uid, piecemaster, count):
            model_mgr = ModelRequestMgr()
            def forUpdateCount(model, inserted):
                model.complete_cnt = count
            model_mgr.add_forupdate_task(BattleEventPieceCollection, BattleEventPieceCollection.makeID(uid, piecemaster.eventid, piecemaster.number), forUpdateCount)
            model_mgr.write_all()
            model_mgr.write_end()
        db_util.run_in_transaction(tr, uid, piecemaster, count)
        
        self.putAlertToHtmlParam(u'{}のコンプリート回数を{}回に変更しました'.format(piecemaster.name, count), AlertCode.SUCCESS)
    
    def _proc_reset_serialcode(self):
        """シリアルコードを再入力できるようにする.
        """
        model_mgr = self.getModelMgr()
        
        # シリアルコード.
        serialcode = self.request.get('_code') or ''
        serialcode_model = None
        if serialcode:
            serialcode_model = BackendApi.get_serialcode_by_serial(model_mgr, serialcode, using=settings.DB_READONLY)
        if serialcode_model is None:
            self.putAlertToHtmlParam(u'存在しないシリアルコードです.%s' % serialcode, AlertCode.ERROR)
            return
        
        def tr(serialcodeid):
            model_mgr = ModelRequestMgr()
            serialcode = SerialCode.getByKeyForUpdate(serialcodeid)
            serialcode.uid = 0
            serialcode.itime = OSAUtil.get_datetime_min()
            serialcode.is_pc = False
            model_mgr.set_save(serialcode)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, serialcode_model.id).write_end()
        
        self.putAlertToHtmlParam(u'再入力可能になりました..%s' % serialcode, AlertCode.SUCCESS)
    
    def _proc_update_serialcount(self):
        """シリアルコード入力回数を変更.
        """
        # ユーザ.
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        # マスター.
        master = self.__check_master_id(SerialCampaignMaster, self.request.get('_mid'))
        if not master:
            return
        
        # 回数.
        cnt = self.__check_intvalue(self.request.get('_count'))
        if cnt is None:
            return
        
        def tr(uid, mid, cnt):
            model_mgr = ModelRequestMgr()
            serialcount = SerialCount.makeInstance(SerialCount.makeID(uid, mid))
            serialcount.cnt = cnt
            model_mgr.set_save(serialcount)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, uid, master.id, cnt).write_end()
        
        self.putAlertToHtmlParam(u'シリアルコードの入力回数を変更しました.', AlertCode.SUCCESS)
    
    def _proc_update_current_panel(self):
        """現在のパネルを変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        # マスター.
        master = self.__check_master_id(PanelMissionPanelMaster, self.request.get('_mid'))
        if not master:
            return
        
        def tr(uid, mid):
            model_mgr = ModelRequestMgr()
            
            now = OSAUtil.get_now()
            
            # プレイヤー情報.
            player = PlayerPanelMission.makeInstance(uid)
            player.panel = mid
            player.cleared = mid - 1
            model_mgr.set_save(player)
            
            # クリア済みの進行情報を作成.
            for panelid in xrange(1, mid):
                ins = PanelMissionData.makeInstance(PanelMissionData.makeID(uid, panelid))
                for number in xrange(1, Defines.PANELMISSION_MISSIN_NUM_PER_PANEL+1):
                    ins.set_data(number, cnt=99, etime=now, rtime=now)
                model_mgr.set_save(ins)
            
            for ins in PanelMissionData.fetchValues(filters={'uid':uid, 'mid__gte':mid}):
                model_mgr.set_delete(ins)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, uid, master.id).write_end()
        
        self.putAlertToHtmlParam(u'進行中のパネルを変更しました.', AlertCode.SUCCESS)
    
    def _proc_update_panelmission(self):
        """進行中のパネルの状態を変更.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        
        # パネルの状態.
        states = {}
        allend = True
        for number in xrange(1, Defines.PANELMISSION_MISSIN_NUM_PER_PANEL+1):
            states[number] = int(self.request.get("sheet%d" % number))
            if states[number] != 2:
                allend = False
        if allend:
            states = {}
        
        def tr(uid):
            model_mgr = ModelRequestMgr()
            
            now = OSAUtil.get_now()
            
            # プレイヤー情報.
            player = PlayerPanelMission.getByKey(uid)
            panelid = player.panel if player else 1
            
            # 進行情報.
            ins = PanelMissionData.getInstanceByKey(PanelMissionData.makeID(uid, panelid))
            for number in xrange(1, Defines.PANELMISSION_MISSIN_NUM_PER_PANEL+1):
                missiondata = ins.get_data(number)
                rtime = missiondata['rtime']
                etime = missiondata['etime']
                
                state = states.get(number, 0)
                if state == 1:
                    if now < etime or rtime <= now:
                        missiondata['cnt'] = 99
                        missiondata['rtime'] = OSAUtil.get_datetime_max()
                        missiondata['etime'] = now
                elif state == 2:
                    if now < rtime or now < etime:
                        missiondata['cnt'] = 99
                        missiondata['rtime'] = now
                        missiondata['etime'] = now
                else:
                    if etime <= now:
                        missiondata['cnt'] = 0
                    missiondata['rtime'] = OSAUtil.get_datetime_max()
                    missiondata['etime'] = OSAUtil.get_datetime_max()
                ins.set_data(number, **missiondata)
            model_mgr.set_save(ins)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, uid).write_end()
        
        self.putAlertToHtmlParam(u'進行中のパネルの達成状況を変更しました.', AlertCode.SUCCESS)
    
    def _proc_change_servertime(self):
        """サーバ時間を変更する.
        """
        str_date = self.request.get("_date")
        target_date = datetime.datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S")
        datetime_now = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        
        timediff = target_date - datetime_now
        OSAUtil.set_now_diff(int(timediff.total_seconds()))
        
        BackendApi.update_infomations(self, using=settings.DB_READONLY)
        BackendApi.update_topbanners(self, using=settings.DB_READONLY)
        BackendApi.update_eventbanners(self, using=settings.DB_READONLY)
        BackendApi.update_popupbanners(self, using=settings.DB_READONLY)
        BackendApi.get_cabaretclub_current_master(self.getModelMgr(), target_date, using=settings.DB_READONLY, reflesh=True)
        
        # サーバ時間変更しましたログ.
        redisdb = RedisCache.getDB()
        redisdb.lpush('ServerTimeUpdateLog', '%s##%s##%s' % (self.request.remote_addr, str_date, timediff))
        
        # ポップアップ時間.
        self.__repair_popup_resettime()
        
        self.html_param['server_nowtime'] = target_date
        self.html_param['datetime_weekly'] = BackendApi.to_cabaretclub_section_starttime(target_date)
        
        self.putAlertToHtmlParam(u'サーバ時間を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_reset_servertime(self):
        """サーバ時間を戻す.
        """
        OSAUtil.set_now_diff(0)
        
        now = OSAUtil.get_now()
        BackendApi.update_infomations(self, using=settings.DB_READONLY)
        BackendApi.update_topbanners(self, using=settings.DB_READONLY)
        BackendApi.update_eventbanners(self, using=settings.DB_READONLY)
        BackendApi.update_popupbanners(self, using=settings.DB_READONLY)
        BackendApi.get_cabaretclub_current_master(self.getModelMgr(), now, using=settings.DB_READONLY, reflesh=True)
        
        # サーバ時間変更しましたログ.
        redisdb = RedisCache.getDB()
        redisdb.lpush('ServerTimeUpdateLog', '%s##reset' % self.request.remote_addr)
        
        # ポップアップ時間.
        self.__repair_popup_resettime()
        
        self.html_param['server_nowtime'] = now
        self.html_param['datetime_weekly'] = BackendApi.to_cabaretclub_section_starttime(now)
        
        self.putAlertToHtmlParam(u'サーバ時間を現在時刻に戻しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_delete_popuovtime(self):
        """ポップアップの閲覧時間を削除.
        """
        uid_max = Player.max_value('id', using=settings.DB_READONLY)
        keys = []
        for uid in xrange(1, uid_max+1):
            keys.append(PopupViewTime.makeKey(uid))
            if 50 < len(keys):
                PopupViewTime.getDB().delete(*keys)
                keys = []
        if keys:
            PopupViewTime.getDB().delete(*keys)
        self.putAlertToHtmlParam(u'ポップアップの最終閲覧時間を削除.', alert_code=AlertCode.SUCCESS)
    
    def __repair_popup_resettime(self):
        """ポップアップのリセット時間を修復.
        """
        popupreset_model = PopupResetTime.get()
        now = OSAUtil.get_now()
        if popupreset_model and now < popupreset_model.rtime:
            popupreset_model.rtime = now
            popupreset_model.save()
    
    def __change_eventstage_stagenumber(self, stagemaster_cls, playdata_cls, eventid, uid, stage):
        """イベントスカウトの現在ステージを変更.
        """
        stagemaster = stagemaster_cls.getValues(filters={'eventid':eventid,'stage':stage}, using=settings.DB_READONLY)
        if stagemaster is None:
            self.putAlertToHtmlParam(u'ステージが存在しません.stage={}'.format(stage), alert_code=AlertCode.ERROR)
            return
        
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.stage = stage
                model.cleared = max(0, stage - 1)
                model.progress = min(model.progress, stagemaster.execution)
            model_mgr.add_forupdate_task(playdata_cls, playdata_cls.makeID(uid, eventid), forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        self.putAlertToHtmlParam(u'現在のステージを変更しました.stage={}'.format(stage), alert_code=AlertCode.SUCCESS)
        
    def __change_eventstage_progress(self, stagemaster_cls, playdata_cls, eventid, uid, progress):
        """イベントスカウトの現在ステージの進行度を変更.
        """
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                stagemaster = stagemaster_cls.getValues(filters={'eventid':eventid,'stage':max(model.stage, 1)}, using=settings.DB_READONLY)
                model.progress = min(stagemaster.execution, progress)
            model_mgr.add_forupdate_task(playdata_cls, playdata_cls.makeID(uid, eventid), forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        self.putAlertToHtmlParam(u'現在のステージの進行度を変更しました.', alert_code=AlertCode.SUCCESS)

    def __check_maintenance_mode(self, model_mgr):
        if BackendApi.get_appconfig(model_mgr).is_maintenance():
            return True
        else:
            raise CabaretError(u'メンテナンスモードではありません。メンテナンスモードに切り替えてから実行して下さい。')

    def __check_battleevent_before_start(self):
        model_mgr = ModelRequestMgr()
        config = BackendApi.get_current_battleeventconfig(model_mgr)
        if OSAUtil.get_now() < config.starttime:
            return True
        else:
            raise CabaretError(u'サーバの時間がバトルイベントの開始前になっていません。サーバの時間をイベントの開始前に設定して下さい。')
    
    def _proc_cabaclub_aggregate(self):
        """店舗の集計実行.
        """
        week = self.__check_intvalue(self.request.get('week'))
        if not week:
            return
        cmd = CommandUtil.makeCommandString('python2.7' if settings_sub.IS_LOCAL else '/usr/local/bin/python2.7', ['manage.py', 'aggregate_cabaretclub_weekly', str(week)], workdir=Defines.PROJECT_DIR)
        logtext = CommandUtil.execute([cmd], log=False)
        if logtext:
            self.putAlertToHtmlParam(logtext, alert_code=AlertCode.ERROR)
        else:
            self.putAlertToHtmlParam(u'集計を実行しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_cabaclub_reset_aggregate_flag(self):
        """店舗の集計フラグをリセット.
        """
        week = self.__check_intvalue(self.request.get('week'))
        if not week:
            return
        CabaClubScorePlayerDataWeekly.all().filter(week=week).update(flag_aggregate=False, view_result=False)
        diff = OSAUtil.get_now_diff()
        client = OSAUtil.get_cache_client()
        client.flush()
        OSAUtil.set_now_diff(diff)
        
        self.putAlertToHtmlParam(u'店舗の集計フラグをリセットしました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_cabaclub_all_cancel(self):
        """キャバクラ 全店舗キャンセル.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        model_mgr = self.getModelMgr()
        master_list = BackendApi.get_cabaretclub_store_master_all(model_mgr, using=settings.DB_READONLY)
        def tr(uid, master_list, now):
            model_mgr = ModelRequestMgr()
            midlist = [master.id for master in master_list]
            storeplayerdata_dict = BackendApi.get_cabaretclub_storeplayerdata_dict(model_mgr, uid, midlist)
            for master in master_list:
                playerdata = storeplayerdata_dict.get(master.id)
                if playerdata and CabaclubStoreSet(master, playerdata).is_alive(now):
                    BackendApi.tr_cabaclubstore_cancel(model_mgr, uid, master, now)
            model_mgr.write_all()
            model_mgr.write_end()
        db_util.run_in_transaction(tr, uid, master_list, OSAUtil.get_now())
        
        self.putAlertToHtmlParam(u'店舗を全て解約しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_set_cabaclub_store_params(self):
        """キャバクラ 店舗の設定.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        storemaster = self.__check_master_id(CabaClubStoreMaster, self.request.get('_mid'))
        limit_time = self.__check_datetime(self.request.get('_limit_time'))
        is_open = self.request.get('_is_open')
        scoutman = self.__check_intvalue(self.request.get('_scoutman'))
        eventmaster = self.__check_master_id(CabaClubEventMaster, self.request.get('_eventid'))
        event_time = self.__check_datetime(self.request.get('_event_time'))
        ua_flag = self.request.get('_ua_flag')
        update_time = self.__check_datetime(self.request.get('_update_time'))
        if None in (uid, storemaster):
            # 必須項目がない.
            return
        
        def tr(uid, storemaster, limit_time, is_open, scoutman, eventmaster, event_time, ua_flag, update_time):
            """書き込み.
            """
            model_mgr = ModelRequestMgr()
            def forUpdate(model, *args, **kwargs):
                if limit_time:
                    model.ltime = limit_time
                if is_open:
                    model.is_open = is_open == "1"
                if scoutman is not None:
                    model.scoutman_add = scoutman
                if eventmaster is not None:
                    model.event_id = eventmaster.id
                if event_time:
                    model.etime = event_time
                model.ua_flag = ua_flag == "1"
                if update_time:
                    model.utime = update_time
            model_mgr.add_forupdate_task(CabaClubStorePlayerData, CabaClubStorePlayerData.makeID(uid, storemaster.id), forUpdate)
            model_mgr.write_all()
            model_mgr.write_end()
        db_util.run_in_transaction(tr, uid, storemaster, limit_time, is_open, scoutman, eventmaster, event_time, ua_flag, update_time)
        
        self.putAlertToHtmlParam(u'店舗情報を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_set_cabaclub_preferential(self):
        """キャバクラ 優待券配布の設定.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        itemmaster = self.__check_master_id(ItemMaster, self.request.get('_mid'))
        limit_time = self.__check_datetime(self.request.get('_limit_time'))
        if None in (uid, itemmaster, limit_time):
            return
        elif itemmaster.id not in (Defines.ItemEffect.CABACLUB_PREFERENTIAL,):
            return
        def tr(uid, itemmaster, limit_time):
            """書き込み.
            """
            model_mgr = ModelRequestMgr()
            def forUpdate(model, *args, **kwargs):
                model.preferential_id = itemmaster.id
                model.preferential_time = limit_time
            model_mgr.add_forupdate_task(CabaClubItemPlayerData, uid, forUpdate)
            model_mgr.write_all()
            model_mgr.write_end()
        db_util.run_in_transaction(tr, uid, itemmaster, limit_time)
        self.putAlertToHtmlParam(u'優待券配布状態を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_set_cabaclub_barrier(self):
        """キャバクラ バリアアイテムの設定.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        itemmaster = self.__check_master_id(ItemMaster, self.request.get('_mid'))
        limit_time = self.__check_datetime(self.request.get('_limit_time'))
        if None in (uid, itemmaster, limit_time):
            return
        elif itemmaster.id not in (Defines.ItemEffect.CABACLUB_BARRIER,):
            return
        def tr(uid, itemmaster, limit_time):
            """書き込み.
            """
            model_mgr = ModelRequestMgr()
            def forUpdate(model, *args, **kwargs):
                model.barrier_id = itemmaster.id
                model.barrier_time = limit_time
            model_mgr.add_forupdate_task(CabaClubItemPlayerData, uid, forUpdate)
            model_mgr.write_all()
            model_mgr.write_end()
        db_util.run_in_transaction(tr, uid, itemmaster, limit_time)
        self.putAlertToHtmlParam(u'バリアアイテム仕様状態を変更しました.', alert_code=AlertCode.SUCCESS)
    
    def _proc_set_cabaclub_weekly_score(self):
        """キャバクラ 週間スコア情報の設定.
        """
        uid = self.__check_request_userid(self.request.get('_uid'))
        customer = self.__check_intvalue(self.request.get('_customer'))
        proceeds = self.__check_intvalue(self.request.get('_proceeds'))
        if None in (uid, customer, proceeds):
            return
        
        target_time = BackendApi.to_cabaretclub_section_starttime(OSAUtil.get_now())
        def tr(uid, target_time, customer, proceeds):
            """書き込み.
            """
            model_mgr = ModelRequestMgr()
            def forUpdate(model, *args, **kwargs):
                model.customer = customer
                model.proceeds = proceeds
            model_mgr.add_forupdate_task(CabaClubScorePlayerDataWeekly, CabaClubScorePlayerDataWeekly.makeID(uid, target_time), forUpdate)
            model_mgr.write_all()
            model_mgr.write_end()
        db_util.run_in_transaction(tr, uid, target_time, customer, proceeds)
        self.putAlertToHtmlParam(u'週間スコア情報を変更しました.', alert_code=AlertCode.SUCCESS)

    def _proc_boxgacha_reset(self):
        """BOXガチャリセット回数の初期化
        """
        model_mgr = ModelRequestMgr()
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            self.putAlertToHtmlParam(u'メンテナンスモードにしてください', alert_code=AlertCode.ERROR)
            return
        cmd = CommandUtil.makeCommandString('python2.7' if settings_sub.IS_LOCAL else '/usr/local/bin/python2.7', ['manage.py', 'init_boxgachadetail'], workdir=Defines.PROJECT_DIR)
        logtext = CommandUtil.execute([cmd], log=False)
        if logtext:
            self.putAlertToHtmlParam(logtext, alert_code=AlertCode.ERROR)
        else:
            self.putAlertToHtmlParam(u'BOXガチャリセット回数を初期化しました.', AlertCode.SUCCESS)

    def _proc_exe_agre_caba_batch(self):
        """キャバクラ 売り上げ集計バッチの実行.
        """
        def get_batch_section_lasttime():
            """バッチで確認する時間の境界."""
            now = OSAUtil.get_now()
            basetime = DateTimeUtil.toBaseTime(now, now.hour)
            return basetime - timedelta(microseconds=1)

        cmd = CommandUtil.makeCommandString('python2.7' if settings_sub.IS_LOCAL else '/usr/local/bin/python2.7', ['manage.py', 'aggregate_cabaretclub_batch'], workdir=Defines.PROJECT_DIR)
        logtext = CommandUtil.execute([cmd], log=False)
        if logtext:
            self.putAlertToHtmlParam(logtext, alert_code=AlertCode.ERROR)
        else:
            self.putAlertToHtmlParam(u'{0}の時点での売り上げを更新しました.'.format(get_batch_section_lasttime().strftime('%Y-%m-%d %H:%M:%S')), alert_code=AlertCode.SUCCESS)

    def _proc_cabaclub_rankevent_exe_reset_player_sales(self):
        """キャバクラランクイベント 本日の総売上のリセット.
        """
        cmd = CommandUtil.makeCommandString('python2.7' if settings_sub.IS_LOCAL else '/usr/local/bin/python2.7', ['manage.py', 'reset_cabaclub_player_sales'], workdir=Defines.PROJECT_DIR)
        logtext = CommandUtil.execute([cmd], log=False)
        if logtext:
            self.putAlertToHtmlParam(logtext, alert_code=AlertCode.ERROR)
        else:
            self.putAlertToHtmlParam(u'本日の総売上をリセットしました.', alert_code=AlertCode.SUCCESS)
        
    def _proc_reset_boxgacha(self):
        uid = self.__check_request_userid(self.request.get('_uid'))
        resetcount = self.__check_intvalue(self.request.get('_resetcount'))
        if None in (uid, resetcount):
            return

        def tr(uid, resetcount):
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.resetcount = resetcount
            model_mgr.add_forupdate_task(GachaBoxResetPlayerData, uid, forUpdate)
            model_mgr.write_all()
            model_mgr.write_end()
        db_util.run_in_transaction(tr, uid, resetcount)
        self.putAlertToHtmlParam(u'リセット回数を変更しました.', alert_code=AlertCode.SUCCESS)

    def _proc_touch_wsgi(self):
        """システムの再起動
        """
        cmd = CommandUtil.makeCommandString('touch', ["wsgi.py"], workdir=Defines.PROJECT_DIR)
        CommandUtil.execute([cmd], log=False)
        self.putAlertToHtmlParam(u'システムを再起動しました', AlertCode.SUCCESS)

    def _proc_change_produceeventscore(self):
        """プロデュースイベントのステータス変更
        """
        model_mgr = ModelRequestMgr()
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return

        current_produce_config = BackendApi.get_current_produce_event_config(model_mgr)
        if current_produce_config is None:
            return

        value = self.__check_intvalue(self.request.get('_value'))
        if value is None:
            return
        target = self.request.get('_target')
        
        def tr(uid, mid):
            model_mgr2 = ModelRequestMgr()
            player_education = BackendApi.get_player_education(model_mgr2, uid, mid)
            setattr(player_education, target, value)
            model_mgr2.set_save(player_education)
            model_mgr2.write_all()
            model_mgr2.write_end()

        db_util.run_in_transaction(tr, uid, current_produce_config.mid)
        
        self.putAlertToHtmlParam(u'レイドイベントのパラメータを変更しました.%s=%s' % (target, value), alert_code=AlertCode.SUCCESS)

    def _proc_change_produceevent_opening(self):
        """ オープニング閲覧フラグを操作.
        """
        model_mgr = self.getModelMgr()

        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        master = self.__check_master_id(ProduceEventMaster, self.request.get('_mid'))
        if master is None:
            return
        flag_op = self.request.get('_flag_op') == '1'
        flag_ep = self.request.get('_flag_ep') == '1'

        mid = master.id
        opvtime = None
        epvtime = None
        if flag_op:
            opvtime = OSAUtil.get_now()
        else:
            opvtime = OSAUtil.get_datetime_min()
        if flag_ep:
            epvtime = OSAUtil.get_now()
        else:
            epvtime = OSAUtil.get_datetime_min()

        if flag_op or flag_ep:
            BackendApi.update_produceevenflagrecord(mid, uid, opvtime=opvtime, epvtime=epvtime)
        else:
            model_mgr = self.getModelMgr()
            flagrecord = BackendApi.get_produceevent_flagrecord(model_mgr, mid, uid, using=settings.DB_READONLY)
            if flagrecord is not None:
                BackendApi.update_produceevenflagrecord(mid, uid, opvtime=opvtime, epvtime=epvtime)

        self.putAlertToHtmlParam(u'シナリオ閲覧フラグを変更しました.', alert_code=AlertCode.SUCCESS)
        
    def _proc_change_produceeventstage(self):
        """プロデュースイベントのステージ情報変更.
        """
        model_mgr = ModelRequestMgr()
        uid = self.__check_request_userid(self.request.get('_uid'))
        if uid is None:
            return
        current_produce_config = BackendApi.get_current_produce_event_config(model_mgr)
        if current_produce_config is None:
            return
        value = self.__check_intvalue(self.request.get('_value'))
        if value is None:
            return
        
        target = self.request.get('_target')
        if target == 'stage':
            self.__change_eventstage_stagenumber(ProduceEventScoutStageMaster, ProduceEventScoutPlayData, current_produce_config.mid, uid, value)
        elif target == 'progress':
            self.__change_eventstage_progress(ProduceEventScoutStageMaster, ProduceEventScoutPlayData, current_produce_config.mid, uid, value)

    def _proc_exec_close_produceevent(self):
        """プロデュースイベントのクローズ処理.
        """
        cmd = CommandUtil.makeCommandString('python2.7' if settings_sub.IS_LOCAL else '/usr/local/bin/python2.7', ['manage.py', 'close_produceevent'], workdir=Defines.PROJECT_DIR)
        logtext = CommandUtil.execute([cmd], log=False)
        
        if logtext:
            self.putAlertToHtmlParam(logtext, alert_code=AlertCode.ERROR)
        else:
            self.putAlertToHtmlParam(u'クローズ処理を実行しました.', alert_code=AlertCode.SUCCESS)

def main(request):
    return Handler.run(request)
