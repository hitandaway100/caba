# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.AccessBonus import AccessBonusMaster,\
    LoginBonusMaster, LoginBonusTimeLimitedMaster,\
    LoginBonusTimeLimitedDaysMaster, LoginBonusSugorokuMaster,\
    LoginBonusSugorokuMapSquaresMaster, LoginBonusSugorokuMapMaster
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
import time
import datetime
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Card import CardMaster, CardSortMaster,\
    DefaultCardMaster
from platinumegg.app.cabaret.models.Item import ItemMaster
from platinumegg.app.cabaret.models.Boss import BossMaster
from platinumegg.app.cabaret.models.Area import AreaMaster
from platinumegg.app.cabaret.models.Scout import ScoutMaster
from platinumegg.app.cabaret.models.Happening import HappeningMaster, RaidMaster
from platinumegg.app.cabaret.models.Skill import SkillMaster
from platinumegg.app.cabaret.models.Infomation import InfomationMaster,\
    TopBannerMaster, EventBannerMaster, PopupMaster
from platinumegg.app.cabaret.models.Present import PrizeMaster
from platinumegg.app.cabaret.models.Memories import MemoriesMaster,\
    EventMovieMaster
from platinumegg.app.cabaret.models.Gacha import GachaMaster, GachaGroupMaster,\
    GachaBoxMaster, GachaSlideCastMaster, GachaStepupMaster, GachaSeatMaster,\
    GachaSeatTableMaster, GachaHeaderMaster, RankingGachaMaster, GachaBoxGachaDetailMaster
from platinumegg.app.cabaret.models.Shop import ShopItemMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.models.PresentEveryone import PresentEveryoneLoginBonusMaster,\
    PresentEveryoneMypageMaster
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.app.cabaret.models.PlayerLevelExp import PlayerLevelExpMaster
from platinumegg.app.cabaret.models.CardLevelExp import CardLevelExpMster
from platinumegg.lib.pljson import Json
from platinumegg.app.cabaret.util import db_util, rediscache
from platinumegg.app.cabaret.models.Tutorial import TutorialConfig
from platinumegg.app.cabaret.models.Battle import BattleRankMaster
from platinumegg.app.cabaret.models.Treasure import TreasureGoldMaster,\
    TreasureSilverMaster, TreasureBronzeMaster, TreasureTableBronzeMaster,\
    TreasureTableSilverMaster, TreasureTableGoldMaster
from platinumegg.app.cabaret.models.Trade import TradeMaster
from platinumegg.app.cabaret.models.TradeShop import TradeShopMaster, TradeShopItemMaster
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventRaidMaster,\
    RaidEventMaster
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventMaster,\
    ScoutEventStageMaster, ScoutEventPresentPrizeMaster,\
    ScoutEventTanzakuCastMaster, ScoutEventHappeningTableMaster,\
    ScoutEventRaidMaster
from platinumegg.app.cabaret.models.Invite import InviteMaster
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventMaster,\
    BattleEventRankMaster, BattleEventPieceMaster
from platinumegg.app.cabaret.models.SerialCampaign import SerialCampaignMaster
from platinumegg.app.cabaret.models.ComeBack import ComeBackCampaignMaster
from platinumegg.app.cabaret.models.battleevent.BattleEventPresent import BattleEventPresentMaster,\
    BattleEventPresentContentMaster
from platinumegg.app.cabaret.models.Mission import PanelMissionPanelMaster,\
    PanelMissionMissionMaster
from platinumegg.app.cabaret.models.promotion.csc import PromotionRequirementMasterCsc,\
    PromotionPrizeMasterCsc, PromotionConfigCsc
from platinumegg.app.cabaret.models.Scenario import ScenarioMaster
from platinumegg.app.cabaret.models.raidevent.RaidCardMixer import RaidEventMaterialMaster,\
    RaidEventRecipeMaster
from platinumegg.app.cabaret.models.raidevent.RaidEventScout import RaidEventScoutStageMaster
from platinumegg.app.cabaret.models.LevelUpBonus import LevelUpBonusMaster
from platinumegg.app.cabaret.models.ReprintTicketTradeShop import ReprintTicketTradeShopMaster
from platinumegg.app.cabaret.models.CabaretClub import CabaClubEventMaster,\
    CabaClubStoreMaster, CabaClubMaster
from platinumegg.app.cabaret.models.CabaretClubEvent import CabaClubRankEventMaster
from platinumegg.app.cabaret.models.Title import TitleMaster
from platinumegg.app.cabaret.models.GachaExplain import GachaExplainMaster
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import ProduceEventMaster, \
    ProduceEventScoutStageMaster, ProduceEventRaidMaster, ProduceCastMaster

class MasterData:
    """マスターデータ一覧の置き場所に困ったのでここに.
    """
    MASTER_NUM_MAX = 89
    (
        CARD_MASTER,
        CARD_SORT_MASTER,
        ITEM_MASTER,
        BOSS_MASTER,
        AREA_MASTER,
        SCOUT_MASTER,
        RAID_MASTER,
        HAPPENING_MASTER,
        SKILL_MASTER,
        INFOMATION_MASTER,
        TOP_BANNER_MASTER,
        EVENT_BANNER_MASTER,
        POPUP_MASTER,
        LOGIN_BONUS_MASTER,
        LOGIN_BONUS_TIMELIMITED_MASTER,
        LOGIN_BONUS_TIMELIMITED_DAYS_MASTER,
        LOGIN_BONUS_SUGOROKU_MAP_MASTER,
        LOGIN_BONUS_SUGOROKU_MAP_SQUARES_MASTER,
        LOGIN_BONUS_SUGOROKU_MASTER,
        ACCESS_BONUS_MASTER,
        PRIZE_MASTER,
        MEMORIES_MASTER,
        EVENT_MOVIE_MASTER,
        GACHA_BOX_MASTER,
        GACHA_GROUP_MASTER,
        GACHA_SEAT_TABLE_MASTER,
        GACHA_SEAT_MASTER,
        RANKING_GACHA_MASTER,
        GACHA_MASTER,
        GACHA_BOX_GACHA_DETAIL_MASTER,
        SHOP_ITEM_MASTER,
        TEXT_MASTER,
        PRESENT_EVERYONE_LOGINBONUS_MASTER,
        PRESENT_EVERYONE_MYPAGE_MASTER,
        SCHEDULE_MASTER,
        PLAYER_LEVEL_EXP_MASTER,
        CARD_LEVEL_EXP_MASTER,
        DEFAULT_CARD_MASTER,
        TUTORIAL_CONFIG,
        BATTLE_RANK_MASTER,
        TREASURE_TABLE_GOLD_MASTER,
        TREASURE_GOLD_MASTER,
        TREASURE_TABLE_SILVER_MASTER,
        TREASURE_SILVER_MASTER,
        TREASURE_TABLE_BRONZE_MASTER,
        TREASURE_BRONZE_MASTER,
        TRADE_MASTER,
        TRADE_SHOP_MASTER,
        TRADE_SHOP_ITEM_MASTER,
        RAID_EVENT_MASTER,
        RAID_EVENT_RAID_MASTER,
        RAID_EVENT_MATERIAL_MASTER,
        RAID_EVENT_RECIPE_MASTER,
        RAID_EVENT_SCOUT_STAGE_MASTER,
        SCOUT_EVENT_MASTER,
        SCOUT_EVENT_STAGE_MASTER,
        SCOUT_EVENT_PRESENT_PRIZE_MASTER,
        SCOUT_EVENT_TANZAKU_CAST_MASTER,
        SCOUT_EVENT_HAPPENING_TABLE_MASTER,
        SCOUT_EVENT_RAID_MASTER,
        INVITE_MASTER,
        BATTLE_EVENT_MASTER,
        BATTLE_EVENT_PIECE_MASTER,
        BATTLE_EVENT_RANK_MASTER,
        BATTLE_EVENT_PRESENT_MASTER,
        BATTLE_EVENT_PRESENT_CONTENT_MASTER,
        GACHA_STEPUP_MASTER,
        GACHA_SLIDE_CAST_MASTER,
        GACHA_HEADER_MASTER,
        PROMOTION_CONFIG_CSC,
        PROMOTION_PRIZE_MASTER_CSC,
        PROMOTION_REQUIREMENT_MASTER_CSC,
        SERIAL_CAMPAIGN_MASTER,
        COME_BACK_CAMPAIGN_MASTER,
        PANEL_MISSION_PANEL_MASTER,
        PANEL_MISSION_MISSION_MASTER,
        SCENARIO_MASTER,
        LEVELUPBONUS_MASTER,
        REPRINTTICKETTRADESHOPMASTER,
        CABA_CLUB_MASTER,
        CABA_CLUB_EVENT_MASTER,
        CABA_CLUB_STORE_MASTER,
        CABA_CLUB_RANK_EVENT_MASTER,
        TITLE_MASTER,
        GACHA_EXPLAIN_MASTER,
        PRODUCE_EVENT_MASTER,
        PRODUCE_EVENT_SCOUT_STAGE_MASTER,
        PRODUCE_EVENT_RAID_MASTER,
        PRODUCE_CAST_MASTER,
    ) = range(MASTER_NUM_MAX)
    
    CLASSES = {
        CARD_MASTER:CardMaster,
        CARD_SORT_MASTER:CardSortMaster,
        ITEM_MASTER:ItemMaster,
        BOSS_MASTER:BossMaster,
        AREA_MASTER:AreaMaster,
        SCOUT_MASTER:ScoutMaster,
        RAID_MASTER:RaidMaster,
        HAPPENING_MASTER:HappeningMaster,
        SKILL_MASTER:SkillMaster,
        INFOMATION_MASTER:InfomationMaster,
        TOP_BANNER_MASTER:TopBannerMaster,
        EVENT_BANNER_MASTER:EventBannerMaster,
        POPUP_MASTER:PopupMaster,
        LOGIN_BONUS_MASTER:LoginBonusMaster,
        LOGIN_BONUS_TIMELIMITED_MASTER:LoginBonusTimeLimitedMaster,
        LOGIN_BONUS_TIMELIMITED_DAYS_MASTER:LoginBonusTimeLimitedDaysMaster,
        LOGIN_BONUS_SUGOROKU_MAP_MASTER:LoginBonusSugorokuMapMaster,
        LOGIN_BONUS_SUGOROKU_MAP_SQUARES_MASTER:LoginBonusSugorokuMapSquaresMaster,
        LOGIN_BONUS_SUGOROKU_MASTER:LoginBonusSugorokuMaster,
        ACCESS_BONUS_MASTER:AccessBonusMaster,
        PRIZE_MASTER:PrizeMaster,
        MEMORIES_MASTER:MemoriesMaster,
        EVENT_MOVIE_MASTER:EventMovieMaster,
        GACHA_MASTER:GachaMaster,
        RANKING_GACHA_MASTER:RankingGachaMaster,
        GACHA_SEAT_TABLE_MASTER:GachaSeatTableMaster,
        GACHA_SEAT_MASTER:GachaSeatMaster,
        GACHA_GROUP_MASTER:GachaGroupMaster,
        GACHA_BOX_MASTER:GachaBoxMaster,
        GACHA_BOX_GACHA_DETAIL_MASTER:GachaBoxGachaDetailMaster,
        SHOP_ITEM_MASTER:ShopItemMaster,
        TEXT_MASTER:TextMaster,
        PRESENT_EVERYONE_LOGINBONUS_MASTER:PresentEveryoneLoginBonusMaster,
        PRESENT_EVERYONE_MYPAGE_MASTER:PresentEveryoneMypageMaster,
        SCHEDULE_MASTER:ScheduleMaster,
        PLAYER_LEVEL_EXP_MASTER:PlayerLevelExpMaster,
        CARD_LEVEL_EXP_MASTER:CardLevelExpMster,
        DEFAULT_CARD_MASTER:DefaultCardMaster,
        TUTORIAL_CONFIG:TutorialConfig,
        BATTLE_RANK_MASTER:BattleRankMaster,
        TREASURE_TABLE_GOLD_MASTER:TreasureTableGoldMaster,
        TREASURE_GOLD_MASTER:TreasureGoldMaster,
        TREASURE_TABLE_SILVER_MASTER:TreasureTableSilverMaster,
        TREASURE_SILVER_MASTER:TreasureSilverMaster,
        TREASURE_TABLE_BRONZE_MASTER:TreasureTableBronzeMaster,
        TREASURE_BRONZE_MASTER:TreasureBronzeMaster,
        TRADE_MASTER:TradeMaster,
        TRADE_SHOP_MASTER:TradeShopMaster,
        TRADE_SHOP_ITEM_MASTER:TradeShopItemMaster,
        RAID_EVENT_MASTER : RaidEventMaster,
        RAID_EVENT_RAID_MASTER : RaidEventRaidMaster,
        RAID_EVENT_MATERIAL_MASTER : RaidEventMaterialMaster,
        RAID_EVENT_RECIPE_MASTER : RaidEventRecipeMaster,
        RAID_EVENT_SCOUT_STAGE_MASTER : RaidEventScoutStageMaster,
        SCOUT_EVENT_MASTER : ScoutEventMaster,
        SCOUT_EVENT_STAGE_MASTER : ScoutEventStageMaster,
        SCOUT_EVENT_PRESENT_PRIZE_MASTER : ScoutEventPresentPrizeMaster,
        SCOUT_EVENT_TANZAKU_CAST_MASTER : ScoutEventTanzakuCastMaster,
        SCOUT_EVENT_HAPPENING_TABLE_MASTER : ScoutEventHappeningTableMaster,
        SCOUT_EVENT_RAID_MASTER : ScoutEventRaidMaster,
        INVITE_MASTER : InviteMaster,
        BATTLE_EVENT_MASTER : BattleEventMaster,
        BATTLE_EVENT_PIECE_MASTER : BattleEventPieceMaster,
        BATTLE_EVENT_RANK_MASTER : BattleEventRankMaster,
        BATTLE_EVENT_PRESENT_MASTER : BattleEventPresentMaster,
        BATTLE_EVENT_PRESENT_CONTENT_MASTER : BattleEventPresentContentMaster,
        GACHA_STEPUP_MASTER : GachaStepupMaster,
        GACHA_SLIDE_CAST_MASTER : GachaSlideCastMaster,
        GACHA_HEADER_MASTER : GachaHeaderMaster,
        PROMOTION_CONFIG_CSC:PromotionConfigCsc,
        PROMOTION_PRIZE_MASTER_CSC:PromotionPrizeMasterCsc,
        PROMOTION_REQUIREMENT_MASTER_CSC:PromotionRequirementMasterCsc,
        SERIAL_CAMPAIGN_MASTER : SerialCampaignMaster,
        COME_BACK_CAMPAIGN_MASTER : ComeBackCampaignMaster,
        PANEL_MISSION_PANEL_MASTER : PanelMissionPanelMaster,
        PANEL_MISSION_MISSION_MASTER : PanelMissionMissionMaster,
        SCENARIO_MASTER : ScenarioMaster,
        LEVELUPBONUS_MASTER : LevelUpBonusMaster,
        REPRINTTICKETTRADESHOPMASTER : ReprintTicketTradeShopMaster,
        CABA_CLUB_MASTER : CabaClubMaster,
        CABA_CLUB_EVENT_MASTER : CabaClubEventMaster,
        CABA_CLUB_STORE_MASTER : CabaClubStoreMaster,
        CABA_CLUB_RANK_EVENT_MASTER : CabaClubRankEventMaster,
        TITLE_MASTER : TitleMaster,
        GACHA_EXPLAIN_MASTER:GachaExplainMaster,
        PRODUCE_EVENT_MASTER : ProduceEventMaster,
        PRODUCE_EVENT_SCOUT_STAGE_MASTER : ProduceEventScoutStageMaster,
        PRODUCE_EVENT_RAID_MASTER : ProduceEventRaidMaster,
        PRODUCE_CAST_MASTER : ProduceCastMaster,
    }
    # クライアントに送るもの.
    USE_CLIENT = (
    )
    
    
    @staticmethod
    def __makeEditVersionKey():
        return 'MasterData:masterEditVersion'
    
    @staticmethod
    def getEditCacheVersion():
        """マスターデータを編集した時のバージョンキー.
        マスターデータを編集したらインクリメントする.
        init_gameで差分データを渡すときに新しくならないので...
        """
        client = OSAUtil.get_cache_client()
        version = client.get(MasterData.__makeEditVersionKey())
        if version is None:
            return 0
        return int(version)
    
    @staticmethod
    def incrementEditCacheVersion():
        client = OSAUtil.get_cache_client()
        client.set(MasterData.__makeEditVersionKey(), MasterData.getEditCacheVersion() + 1)
        # マスターデータもリロード..
        rediscache.flush_all()
    
    @staticmethod
    def getLastUpdateVersion(model_mgr=None):
        # 現時点で最後に更新した時間の数値を返す.
        memcache_key = 'getLastUpdateVersion:%s' % MasterData.getEditCacheVersion()
        client = OSAUtil.get_cache_client()
        last_update_version = client.get(memcache_key)
        
        model_mgr = model_mgr or ModelRequestMgr()
        
        if last_update_version is None:
            update_time = OSAUtil.get_datetime_min()
            last_update = update_time
            for kls in [MasterData.CLASSES[i] for i in MasterData.USE_CLIENT]:
                for obj in model_mgr.get_mastermodel_all(kls, fetch_deleted=True):
                    edit_time = getattr(obj, Defines.MASTER_EDITTIME_COLUMN)
                    if MasterData.is_update(last_update, edit_time):
                        if last_update < edit_time:
                            last_update = edit_time
            last_update_version = MasterData.toMasterVersion(last_update)
            client.set(memcache_key, last_update_version)
        return last_update_version
    
    @staticmethod
    def is_update(update_time, edit_time):
        # 更新されたデータか.
        if update_time < edit_time:
            return True
        elif update_time == OSAUtil.get_datetime_min():
            return True
        else:
            return False
        
    @staticmethod
    def toMasterVersion(dtime):
        # 時間をクライアントバージョンに.
        return int(time.mktime(dtime.timetuple()))
    
    @staticmethod
    def toEditTime(master_version):
        # クライアントバージョンを編集時間に.
        return datetime.datetime.fromtimestamp(master_version)
    
    @staticmethod
    def update_from_json(jsonstr):
        """JSONからマスターデータに保存.
        """
        data = Json.decode(jsonstr)
        
        model_mgr = ModelRequestMgr()
        modellist = []
        for cls_id in xrange(MasterData.MASTER_NUM_MAX):
            model_cls = MasterData.CLASSES.get(cls_id)
            if model_cls is None:
                raise CabaretError("Not Found:%d" % cls_id, CabaretError.Code.INVALID_MASTERDATA)
            
            clsname = model_cls.__name__
            arr = data.get(clsname) or []
            
            for dic in arr:
                ins = model_cls()
                for k,v in dic.items():
                    setattr(ins, k, v)
                model_mgr.set_save(ins)
                modellist.append(ins)
        
        def tr():
            model_mgr.write_all()
        db_util.run_in_transaction_custom_retries(0, tr)
        model_mgr.write_end()
        
        MasterData.incrementEditCacheVersion()
        
        return modellist
    
    @staticmethod
    def to_json(model_cls_list=None):
        """マスターデータをJsonに.
        """
        if model_cls_list is None:
            model_cls_list = [MasterData.CLASSES[i] for i in xrange(MasterData.MASTER_NUM_MAX)]
        
        data = {}
        for model_cls in model_cls_list:
            modellist = model_cls.fetchValues(fetch_deleted=True)
            columnnames = model_cls.get_column_names()
            
            arr = []
            for model in modellist:
                dic = {}
                for columnname in columnnames:
                    dic[columnname] = getattr(model, columnname)
                try:
                    Json.encode(dic)
                except:
                    print model_cls.__name__
                    print dic
                    raise
                arr.append(dic)
            data[model_cls.__name__] = arr
        return Json.encode(data)
