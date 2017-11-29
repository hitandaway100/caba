# -*- coding: utf-8 -*-
from platinumegg.lib.strutil import StrUtil
from platinumegg.app.cabaret.models.Card import CardMaster, CardSortMaster,\
    DefaultCardMaster, CardAcquisition, AlbumAcquisition, CardDeleted, CardStock
from platinumegg.app.cabaret.models.Item import ItemMaster, Item
from defines import Defines
from platinumegg.app.cabaret.models.Player import Player, PlayerCard
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.player import ModelPlayer
from platinumegg.app.cabaret.models.Infomation import InfomationMaster,\
    TopBannerMaster, EventBannerMaster, PopupMaster
from platinumegg.app.cabaret.models.PlayerLevelExp import PlayerLevelExpMaster
from platinumegg.app.cabaret.models.CardLevelExp import CardLevelExpMster
from platinumegg.app.cabaret.models.Boss import BossMaster
from platinumegg.app.cabaret.models.Scout import ScoutMaster, ScoutPlayData
from platinumegg.app.cabaret.models.Area import AreaMaster, AreaPlayData
from platinumegg.app.cabaret.models.Happening import HappeningMaster,\
    Happening, RaidMaster, Raid
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Present import PrizeMaster
from platinumegg.app.cabaret.models.Gacha import GachaMaster, GachaGroupMaster,\
    GachaPlayData, GachaBoxMaster, RankingGachaMaster, RankingGachaWholeData,\
    RankingGachaWholePrizeQueue, RankingGachaScore, RankingGachaWholePrizeData
from platinumegg.app.cabaret.util.gacha import GachaBoxGroup, GachaMasterSet
from platinumegg.app.cabaret.models.Shop import ShopItemMaster, ShopItemBuyData
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusMaster,\
    AccessBonusMaster, LoginBonusTimeLimitedMaster,\
    LoginBonusTimeLimitedDaysMaster, LoginBonusSugorokuMaster,\
    LoginBonusSugorokuMapMaster, LoginBonusSugorokuMapSquaresMaster,\
    LoginBonusSugorokuPlayerData
from platinumegg.app.cabaret.models.Memories import MemoriesMaster
from platinumegg.app.cabaret.models.Tutorial import TutorialConfig
from platinumegg.app.cabaret.util.rediscache import PlayerLevelExpMasterListCache,\
    CardLevelExpMsterListCache, RankingGachaWholePrizeQueueIdSet
from platinumegg.app.cabaret.models.PaymentEntry import ShopPaymentEntry,\
    GachaPaymentEntry
from platinumegg.app.cabaret.models.Battle import BattleRankMaster, BattlePlayer
from platinumegg.app.cabaret.models.Treasure import TreasureGoldMaster,\
    TreasureSilverMaster, TreasureBronzeMaster, TreasureGold, TreasureSilver, TreasureBronze,\
    TreasureTableGoldMaster, TreasureTableSilverMaster,\
    TreasureTableBronzeMaster
from platinumegg.app.cabaret.models.Trade import TradeMaster
import datetime
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventMaster,\
    RaidEventRaidMaster, RaidEventScore, RaidEventFlags, RaidEventChampagne
from platinumegg.app.cabaret.models.Invite import InviteMaster, InviteData,\
    Invite
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventMaster,\
    ScoutEventStageMaster, ScoutEventScore, ScoutEventPlayData, ScoutEventFlags,\
    ScoutEventPresentPrizeMaster, ScoutEventPresentNum, ScoutEventRaidMaster,\
    ScoutEventTanzakuCastMaster, ScoutEventTanzakuCastData,\
    ScoutEventHappeningTableMaster
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventMaster,\
    BattleEventRankMaster, BattleEventScore, BattleEventFlags, BattleEventRank,\
    BattleEventGroupLog
from platinumegg.app.cabaret.util.battleevent import BattleEventGroupUserData
from platinumegg.app.cabaret.models.promotion.koihime import PromotionPrizeMasterKoihime,\
    PromotionRequirementMasterKoihime, PromotionDataKoihime,\
    PromotionConfigKoihime
from platinumegg.app.cabaret.models.SerialCampaign import SerialCampaignMaster,\
    SerialCode, SerialCount
from platinumegg.app.cabaret.models.ComeBack import ComeBackCampaignMaster,\
    ComeBackCampaignData
from platinumegg.app.cabaret.models.battleevent.BattleEventPresent import BattleEventPresentContentMaster,\
    BattleEventPresentMaster, BattleEventPresentData, BattleEventPresentCounts
from platinumegg.app.cabaret.models.Mission import PanelMissionPanelMaster,\
    PanelMissionMissionMaster, PlayerPanelMission, PanelMissionData
from platinumegg.app.cabaret.models.Scenario import ScenarioMaster
from platinumegg.app.cabaret.models.raidevent.RaidCardMixer import RaidEventRecipeMaster,\
    RaidEventMixData, RaidEventMaterialMaster, RaidEventMaterialData
from platinumegg.app.cabaret.util.redisdb import RankingGachaSingleRanking,\
    RankingGachaTotalRanking
from platinumegg.app.cabaret.models.raidevent.RaidEventScout import RaidEventScoutStageMaster,\
    RaidEventScoutPlayData
from platinumegg.app.cabaret.models.CabaretClub import CabaClubMaster,\
    CabaClubEventMaster, CabaClubStoreMaster, CabaClubStorePlayerData,\
    CabaClubCastPlayerData, CabaClubItemPlayerData, CabaClubScorePlayerData,\
    CabaClubScorePlayerDataWeekly
from platinumegg.app.cabaret.models.Title import TitleMaster, TitlePlayerData

class DummyType:
    NUM_MAX = 117
    (
        PLAYER,
        CARD,
        CARD_MASTER,
        ITEM,
        ITEM_MASTER,
        INFOMATION_MASTER,
        TOP_BANNER_MASTER,
        EVENT_BANNER_MASTER,
        POPUP_MASTER,
        DEFAULT_CARD_MASTER,
        PLAYER_LEVEL_EXP_MASTER,
        CARD_LEVEL_EXP_MASTER,
        AREA_MASTER,
        AREA_PLAY_DATA,
        SCOUT_MASTER,
        SCOUT_PLAY_DATA,
        BOSS_MASTER,
        RAID_MASTER,
        HAPPENING_MASTER,
        HAPPENING,
        RAID,
        PRIZE_MASTER,
        GACHA_MASTER,
        GACHA_GROUP_MASTER,
        GACHA_PLAY_DATA,
        SHOP_ITEM_MASTER,
        SHOP_ITEM_BUY_DATA,
        LOGIN_BONUS_MASTER,
        ACCESS_BONUS_MASTER,
        LOGIN_BONUS_TIME_LIMITED_MASTER,
        LOGIN_BONUS_TIME_LIMITED_DAYS_MASTER,
        LOGIN_BONUS_SUGOROKU_MASTER,
        LOGIN_BONUS_SUGOROKU_MAP_MASTER,
        LOGIN_BONUS_SUGOROKU_MAP_SQUARES_MASTER,
        LOGIN_BONUS_SUGOROKU_PLAYER_DATA,
        MEMORIES_MASTER,
        CARD_ACQUISITION,
        ALBUM_ACQUISITION,
        TUTORIAL_CONFIG,
        SHOP_PAYMENT_ENTRY,
        GACHA_PAYMENT_ENTRY,
        BATTLE_RANK_MASTER,
        BATTLE_PLAYER,
        TREASURE_TABLE_GOLD_MASTER,
        TREASURE_TABLE_SILVER_MASTER,
        TREASURE_TABLE_BRONZE_MASTER,
        TREASURE_GOLD_MASTER,
        TREASURE_SILVER_MASTER,
        TREASURE_BRONZE_MASTER,
        TREASURE_GOLD,
        TREASURE_SILVER,
        TREASURE_BRONZE,
        TRADE_MASTER,
        RAID_EVENT_MASTER,
        RAID_EVENT_RAID_MASTER,
        RAID_EVENT_SCORE,
        RAID_EVENT_FLAGS,
        RAID_EVENT_CHAMPAGNE,
        RAID_EVENT_RECIPE_MASTER,
        RAID_EVENT_MIX_DATA,
        RAID_EVENT_MATERIAL_MASTER,
        RAID_EVENT_MATERIAL_DATA,
        RAID_EVENT_SCOUT_STAGE_MASTER,
        RAID_EVENT_SCOUT_PLAY_DATA,
        INVITE_MASTER,
        INVITE_DATA,
        INVITE,
        SCOUT_EVENT_MASTER,
        SCOUT_EVENT_STAGE_MASTER,
        SCOUT_EVENT_PLAY_DATA,
        SCOUT_EVENT_SCORE,
        SCOUT_EVENT_FLAGS,
        SCOUT_EVENT_PRESENT_PRIZE_MASTER,
        SCOUT_EVENT_PRESENT_NUM,
        SCOUT_EVENT_RAID_MASTER,
        SCOUT_EVENT_TANZAKU_CAST_MASTER,
        SCOUT_EVENT_TANZAKU_CAST_DATA,
        SCOUT_EVENT_HPPENING_TABLE_MASTER,
        BATTLE_EVENT_MASTER,
        BATTLE_EVENT_RANK_MASTER,
        BATTLE_EVENT_SCORE,
        BATTLE_EVENT_FLAGS,
        BATTLE_EVENT_RANK,
        BATTLE_EVENT_GROUP_LOG,
        BATTLE_EVENT_PRESENT_CONTENT_MASTER,
        BATTLE_EVENT_PRESENT_MASTER,
        BATTLE_EVENT_PRESENT_DATA,
        BATTLE_EVENT_PRESENT_COUNTS,
        PROMOTION_CONFIG_KOIHIME,
        PROMOTION_PRIZE_MASTER_KOIHIME,
        PROMOTION_REQUIREMENT_MASTER_KOIHIME,
        PROMOTION_DATA_KOIHIME,
        SERIAL_CAMPAIGN_MASTER,
        SERIAL_CODE,
        SERIAL_COUNT,
        COME_BACK_CAMPAIGN_MASTER,
        COME_BACK_CAMPAIGN_DATA,
        CARD_STOCK,
        PANEL_MISSION_PANEL_MASTER,
        PANEL_MISSION_MISSION_MASTER,
        PLAYER_PANEL_MISSION,
        PANEL_MISSION_DATA,
        EVENT_SCENARIO_MASTER,
        RANKING_GACHA_MASTER,
        RANKING_GACHA_SCORE,
        RANKING_GACHA_WHOLE_PRIZE_QUEUE,
        RANKING_GACHA_WHOLE_PRIZE_DATA,
        CABA_CLUB_MASTER,
        CABA_CLUB_EVENT_MASTER,
        CABA_CLUB_STORE_MASTER,
        CABA_CLUB_STORE_PLAYER_DATA,
        CABA_CLUB_CAST_PLAYER_DATA,
        CABA_CLUB_ITEM_PLAYER_DATA,
        CABA_CLUB_SCORE_PLAYER_DATA,
        CABA_CLUB_SCORE_PLAYER_DATA_WEEKLY,
        TITLE_MASTER,
        TITLE_PLAYER_DATA,
    ) = range(NUM_MAX)
    
class DummyFactory:
    """
    ダミーデータを作ってくれるクラス.
    シングルトンで使う.
    テスト中、ダミーデータ作って最後に全部一気に消したいので作った.
    dummy_factory = DummyFactory()
    ■作成.
        dummy_factory.create_dummy(DummyType)
    ■全て削除.
        dummy_factory.remove_dummy_all()
    """
    
    def __init__(self):
        self.__created_dummys = {}
    
    def __add_dummy_id(self, dummy_type, pkey):
        if pkey is None:
            return
        if dummy_type not in self.__created_dummys:
            self.__created_dummys[dummy_type] = []
        self.__created_dummys[dummy_type].append(pkey)
    
    @staticmethod
    def __get_dummy_kls(dummy_type):
        """クラス名取得.
        データ生成クラスの名前はDummyTypeの定数名のcamel case + 'Dummy'.
        例:
            ALIEN_MASTER -> AlienMasterDummy
        """
        kls_name = ''
        for const_name, v in DummyType.__dict__.items():
            if v == dummy_type:
                kls_name = StrUtil.toCamelCase(const_name) + 'Dummy'
        return globals()[kls_name]
    
    def create_dummy(self, dummy_type, *args, **kwgs):
        """ダミーデータ作る.
        """
        kls = DummyFactory.__get_dummy_kls(dummy_type)
        d = kls(self)
        ret = d.create(*args, **kwgs)
        self.__add_dummy_id(dummy_type, d.get_id())
        return ret
    
    def remove_dummy_all(self):
        """作成したダミーデータ全部削除.
        """
        for dummy_type in xrange(DummyType.NUM_MAX):
            id_list = self.__created_dummys.get(dummy_type, None)
            if id_list is not None:
                kls = DummyFactory.__get_dummy_kls(dummy_type)
                for pkey in id_list:
                    kls.remove(pkey)


def _getDummyID(model_kls):
    # ダミーモデルのID作る。
    # 最大のID+1.
    field = model_kls.get_primarykey_column()
    return int(model_kls.max_value(field, 0)) + 1


class BaseDummy:
    """
    ダミーデータを取得して返す.
    データ作ったらset_id(id)で消す時に必要なIDをセットする.
    """
    def __init__(self, dummyfactory):
        self.__id = None
        self._df = dummyfactory
    def set_id(self, pkey):
        self.__id = pkey
    def get_id(self):
        if self.__id is None:
            print u'ダミーのIDがセットされていません'
        return self.__id
    @classmethod
    def create(cls, **kwargs):
        raise NotImplementedError
    @classmethod
    def remove(cls, pkey):
        raise NotImplementedError

#===========================================================================
# ▼ここからそれぞれのダミーデータ作成・削除のクラス定義.
#===========================================================================
class PlayerDummy(BaseDummy):
    """プレイヤー.
    """
    
    def create(self, **kwargs):
        
        regist = kwargs.pop('regist', True)
        tutoend = kwargs.pop('tutoend', regist) and regist
        
        uid = _getDummyID(Player)
        
        player = Player(id=uid)
        player.dmmid = u'%s' % uid
        player.save()
        model_player = ModelPlayer([player])
        
        if regist:
            # 経験値情報とか必要.
            if not PlayerLevelExpMaster.getByKey(1):
                self._df.create_dummy(DummyType.PLAYER_LEVEL_EXP_MASTER, level=1)
            if not CardLevelExpMster.getByKey(1):
                self._df.create_dummy(DummyType.CARD_LEVEL_EXP_MASTER, level=1)
            if not DefaultCardMaster.getByKey(Defines.CharacterType.TYPE_001):
                leader = self._df.create_dummy(DummyType.CARD_MASTER, maxlevel=99)
                self._df.create_dummy(DummyType.DEFAULT_CARD_MASTER, Defines.CharacterType.TYPE_001, leader=leader.id)
                self._df.create_dummy(DummyType.MEMORIES_MASTER, id=leader.id)
                self._df.create_dummy(DummyType.CARD_ACQUISITION, uid, id=leader.id)
                self._df.create_dummy(DummyType.ALBUM_ACQUISITION, uid, id=leader.id)
            
            model_mgr = ModelRequestMgr()
            p = BackendApi.tr_regist_player(model_mgr, uid, Defines.CharacterType.TYPE_001)
            model_mgr.write_all()
            model_mgr.write_end()
            for model_cls in ModelPlayer.Meta.MODELS:
                model = p.getModel(model_cls)
                if model:
                    model_player.setModel(model)
        if tutoend:
            model_mgr = ModelRequestMgr()
            p = BackendApi.tr_tutorialend(model_mgr, model_player, False)
            model_mgr.write_all()
            model_mgr.write_end()
            # プレイヤーを取り直す.
            for model_cls in ModelPlayer.Meta.MODELS:
                model = model_mgr.get_model(model_cls, model_player.id)
                if model:
                    model_player.setModel(model)
        
        if kwargs:
            for k,v in kwargs.items():
                setattr(model_player, k, v)
            
            model_mgr = ModelRequestMgr()
            for model_cls in ModelPlayer.Meta.MODELS:
                model = model_player.getModel(model_cls)
                if model:
                    model_mgr.set_save(model)
            model_mgr.write_all()
            model_mgr.write_end()
        
        self.set_id(uid)
        return model_player
    
    @classmethod
    def remove(cls, pkey):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_delete_friend_all(model_mgr, pkey)
        model_mgr.write_all()
        model_mgr.write_end()
        
        model_mgr = ModelRequestMgr()
        BackendApi.tr_delete_player(model_mgr, pkey)
        model_mgr.write_all()
        model_mgr.write_end()

class CardMasterDummy(BaseDummy):
    """カードのマスターデータ.
    """
    
    def create(self, **kwargs):
        
        mid = _getDummyID(CardMaster)
        
        master = CardMaster(id=mid)
        sortmaster = CardSortMaster(id=mid)
        sortmaster.ctype = Defines.CharacterType.TYPE_001
        sortmaster.rare = kwargs.get('rare', 0)
        sortmaster.album = kwargs.get('album', mid)
        sortmaster.hklevel = kwargs.get('hklevel', 1)
        
        master.gtype = kwargs.get('gtype', Defines.CardGrowthType.BALANCE)
        master.cost = kwargs.get('cost', 0)
        master.basepower = kwargs.get('basepower', 0)
        master.maxpower = kwargs.get('maxpower', 0)
        master.maxlevel = kwargs.get('maxlevel', 1)
        master.skill = kwargs.get('skill', 0)
        master.albumhklevel = (sortmaster.album << 32) + sortmaster.hklevel
        master.basematerialexp = kwargs.get('basematerialexp', 0)
        master.maxmaterialexp = kwargs.get('maxmaterialexp', 0)
        master.baseprice = kwargs.get('baseprice', 100)
        master.maxprice = kwargs.get('maxprice', 100)
        master.evolcost = kwargs.get('evolcost', 0)
        
        master.save()
        sortmaster.save()
        
        self.set_id(mid)
        return master
    
    @classmethod
    def remove(cls, pkey):
        m = CardMaster.getByKey(pkey)
        if m:
            m.delete()
    
class CardDummy(BaseDummy):
    """カード.
    """
    
    def create(self, player, master, **kwargs):
        
        playercard = player.getModel(PlayerCard)
        model_mgr = ModelRequestMgr()
        cardset = BackendApi.tr_create_card(model_mgr, playercard, master.id).get('card')
        model_mgr.write_all()
        model_mgr.write_end()
        
        self.set_id(cardset.id)
        return cardset.card
    
    @classmethod
    def remove(cls, pkey):
        m = CardDeleted.getByKey(pkey)
        if m:
            m.delete()
    
class ItemMasterDummy(BaseDummy):
    """アイテムのマスターデータ.
    """
    
    def create(self, mid=Defines.ItemEffect.ACTION_ALL_RECOVERY, evalue=0, **kwargs):
        
        pkey = mid
        
        ins = ItemMaster.getValuesByKey(pkey)
        if not ins:
            ins = ItemMaster(id=pkey)
            ins.name = u'drink %d' % pkey
            ins.text = u'detail %d' % pkey
            ins.thumb = 'img/b1.png'
            ins.unit = u'p'
            self.set_id(pkey)
        ins.evalue = evalue
        ins.save()
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ItemMaster.getByKey(pkey)
        if m:
            m.delete()
    
class ItemDummy(BaseDummy):
    """アイテム.
    """
    
    def create(self, player, master, **kwargs):
        
        pkey = Item.makeID(player.id, master.id)
        
        ins = Item(id=pkey)
        ins.uid = player.id
        ins.mid = master.id
        ins.rnum = kwargs.get('rnum', 0)
        ins.vnum = kwargs.get('vnum', 0)
        ins.save()
        
        self.set_id(pkey)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        pass
    
class InfomationMasterDummy(BaseDummy):
    """お知らせ.
    """
    
    def create(self, **kwargs):
        
        pkey = _getDummyID(InfomationMaster)
        
        ins = InfomationMaster(id=pkey)
        ins.title = u'タイトル %d' % pkey
        ins.body = u'本文 %d' % pkey
        ins.etime = OSAUtil.get_datetime_max()
        ins.save()
        
        self.set_id(pkey)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = InfomationMaster.getByKey(pkey)
        if m:
            m.delete()

class TopBannerMasterDummy(BaseDummy):
    """トップページのバナー.
    """
    
    def create(self, **kwargs):
        
        pkey = _getDummyID(TopBannerMaster)
        
        ins = TopBannerMaster(id=pkey)
        ins.name = u'名前 %d' % pkey
        ins.jumpto = '/'
        ins.imageurl = 'img/b1.png'
        ins.priority = 0
        ins.etime = OSAUtil.get_datetime_max()
        ins.save()
        
        self.set_id(pkey)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = TopBannerMaster.getByKey(pkey)
        if m:
            m.delete()

class EventBannerMasterDummy(BaseDummy):
    """イベントのバナー.
    """
    
    def create(self, **kwargs):
        
        pkey = _getDummyID(EventBannerMaster)
        
        ins = EventBannerMaster(id=pkey)
        ins.name = u'名前 %d' % pkey
        ins.comment = u'コメント %d' % pkey
        ins.jumpto = '/'
        ins.imageurl = 'img/b1.png'
        ins.priority = 0
        ins.etime = OSAUtil.get_datetime_max()
        ins.save()
        
        self.set_id(pkey)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = EventBannerMaster.getByKey(pkey)
        if m:
            m.delete()

class PopupMasterDummy(BaseDummy):
    """ポップアップのバナー.
    """
    
    def create(self, banner=None):
        
        ins_id = _getDummyID(PopupMaster)
        
        ins = PopupMaster(id=ins_id)
        ins.name = u'名前 %d' % ins_id
        ins.name = u'タイトル %d' % ins_id
        ins.imageurl = 'img/b1.png'
        ins.priority = 0
        ins.etime = OSAUtil.get_datetime_max()
        ins.banner = banner.id if banner else 0
        ins.bannerflag = 0 < ins.banner
        ins.save()
        
        self.set_id(ins_id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = PopupMaster.getByKey(pkey)
        if m:
            m.delete()

class DefaultCardMasterDummy(BaseDummy):
    """初期カード情報.
    """
    def create(self, ctype, leader, members=None, box=None):
        
        ins = DefaultCardMaster.getValuesByKey(ctype)
        
        if not ins:
            ins = DefaultCardMaster(ctype=ctype)
            self.set_id(ctype)
        
        ins.leader = leader
        ins.members = members or []
        ins.box = box or []
        ins.save()
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = DefaultCardMaster.getByKey(pkey)
        if m:
            m.delete()

class PlayerLevelExpMasterDummy(BaseDummy):
    """プレイヤー経験値情報.
    """
    def create(self, level, exp=None, ap=None, bp=None, hp=None, deckcapacity=None, cardlimit=None, friendlimit=None):
        ins = PlayerLevelExpMaster.getValuesByKey(level)
        
        if not ins:
            ins = PlayerLevelExpMaster(level=level)
            self.set_id(level)
        ins.exp = exp or (level-1) * 100
        ins.ap = ap or level
        ins.hp = hp or level
        ins.deckcapacitylv = deckcapacity or level
        ins.cardlimit = cardlimit or level
        ins.friendlimit = friendlimit or level
        ins.save()
        
        PlayerLevelExpMasterListCache.getDB().delete(PlayerLevelExpMasterListCache.makeKey())
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = PlayerLevelExpMaster.getByKey(pkey)
        if m:
            m.delete()

class CardLevelExpMasterDummy(BaseDummy):
    """カード経験値情報.
    """
    def create(self, level, exp=None):
        ins = CardLevelExpMster.getValuesByKey(level)
        if not ins:
            ins = CardLevelExpMster(level=level)
            self.set_id(level)
        ins.exp = exp if exp is not None else (level * 100)
        ins.save()
        
        CardLevelExpMsterListCache.getDB().delete(CardLevelExpMsterListCache.makeKey())
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = CardLevelExpMster.getByKey(pkey)
        if m:
            m.delete()

class AreaMasterDummy(BaseDummy):
    """エリア.
    """
    def create(self, bossid, opencondition=0):
        mid = _getDummyID(AreaMaster)
        
        ins = AreaMaster(id=mid)
        ins.boss = bossid
        ins.opencondition = opencondition
        ins.save()
        
        self.set_id(mid)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = AreaMaster.getByKey(pkey)
        if m:
            m.delete()

class AreaPlayDataDummy(BaseDummy):
    """エリアプレイ情報.
    """
    def create(self, uid, areaid, clevel=1):
        
        ins = AreaPlayData.makeInstance(AreaPlayData.makeID(uid, areaid))
        ins.clevel = clevel
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = AreaPlayData.getByKey(pkey)
        if m:
            m.delete()

class ScoutMasterDummy(BaseDummy):
    """スカウト.
    """
    def create(self, area, execution=5, dropitems=[], exp=1, goldmin=1, goldmax=1, opencondition=0, apcost=0, happenings=[], treasuregold=0, treasuresilver=0, treasurebronze=0):
        mid = _getDummyID(ScoutMaster)
        
        ins = ScoutMaster(id=mid)
        ins.area = area.id
        ins.execution = execution
        ins.dropitems = dropitems
        ins.exp = exp
        ins.goldmin = goldmin
        ins.goldmax = goldmax
        ins.opencondition = opencondition
        ins.apcost = apcost
        ins.happenings = happenings
        ins.treasuregold = treasuregold
        ins.treasuresilver = treasuresilver
        ins.treasurebronze = treasurebronze
        ins.eventrate_drop = 1 if dropitems else 0
        ins.eventrate_happening = 1 if happenings else 0
        ins.eventrate_treasure = 1 if ins.treasuregold or ins.treasuresilver or ins.treasurebronze else 0
        ins.save()
        
        self.set_id(mid)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ScoutMaster.getByKey(pkey)
        if m:
            m.delete()

class ScoutPlayDataDummy(BaseDummy):
    """スカウト.
    """
    def create(self, uid, mid, progress=0):
        ins = ScoutPlayData.makeInstance(ScoutPlayData.makeID(uid, mid))
        ins.progress = progress
        ins.alreadykey = OSAUtil.makeSessionID()
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ScoutPlayData.getByKey(pkey)
        if m:
            m.delete()

class BossMasterDummy(BaseDummy):
    """ボス.
    """
    def create(self):
        
        mid = _getDummyID(BossMaster)
        ins = BossMaster(id=mid)
        ins.name = u'BossDummy:%d' % mid
        ins.commentappear = u'・・・だれだ！'
        ins.commentwin = u'オメェの勝ちだ！'
        ins.commentlose = u'オラの勝ちだ！'
        ins.hp = 100
        ins.apcost = 1
        ins.attack = 10
        ins.defense = 10
        ins.save()
        self.set_id(mid)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = BossMaster.getByKey(pkey)
        if m:
            m.delete()

class RaidMasterDummy(BaseDummy):
    """レイド.
    """
    def create(self, bpcost=20, bpcost_strong=50, hp=100, defense=1, prizes=None, helpprizes=None, cabaretking=0, demiworld=0):
        
        mid = _getDummyID(RaidMaster)
        ins = RaidMaster(id=mid)
        ins.name = u'BossDummy:%d' % mid
        ins.commentappear = u'・・・だれだ！'
        ins.commentwin = u'オメェの勝ちだ！'
        ins.commentlose = u'オラの勝ちだ！'
        ins.thumb = u'Thumbnail'
        ins.bpcost = bpcost
        ins.bpcost_strong = bpcost_strong
        ins.hpbase = hp
        ins.hpgrowth = 0
        ins.defensebase = defense
        ins.defensegrowth = 0
        ins.prizes = prizes or []
        ins.helpprizes = helpprizes or []
        ins.cabaretkingbase = cabaretking
        ins.cabaretkinggrowth = 0
        ins.demiworldbase = demiworld
        ins.demiworldgrowth = 0
        ins.save()
        self.set_id(mid)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RaidMaster.getByKey(pkey)
        if m:
            m.delete()

class HappeningMasterDummy(BaseDummy):
    """ハプニングのマスター.
    """
    def create(self, raidid, timelimit=86400, execution=5, items=None, exp=1, goldmin=1, goldmax=1, opencondition=0, apcost=0):
        mid = _getDummyID(HappeningMaster)
        
        ins = HappeningMaster(id=mid)
        ins.boss = raidid
        ins.execution = execution
        ins.items = items or []
        ins.exp = exp
        ins.goldmin = goldmin
        ins.goldmax = goldmax
        ins.apcost = apcost
        ins.timelimit = timelimit
        ins.save()
        
        self.set_id(mid)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = HappeningMaster.getByKey(pkey)
        if m:
            m.delete()

class HappeningDummy(BaseDummy):
    """ハプニング情報.
    """
    def create(self, uid, mid, progress=0, etime=None, state=Defines.HappeningState.ACTIVE, level=1, eventid=0):
        etime = etime or OSAUtil.get_now() + datetime.timedelta(days=1)
        
        model_mgr = ModelRequestMgr()
        ins = BackendApi.tr_create_happening(model_mgr, uid, mid, level, eventvalue=eventid)
        ins.progress = progress
        ins.etime = etime
        ins.state = state
        model_mgr.write_all()
        model_mgr.write_end()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = Happening.getByKey(pkey)
        if m:
            m.delete()

class RaidDummy(BaseDummy):
    """レイド情報.
    """
    def create(self, player, happeningmaster, happening, level=None, hp=None):
        model_mgr = ModelRequestMgr()
        raidboss = BackendApi.tr_create_raid(model_mgr, happeningmaster, happening)
        ins = raidboss.raid
        if level is not None:
            ins.level = level
        if hp is not None:
            ins.hp = hp
        model_mgr.write_all()
        model_mgr.write_end()
        
        self.set_id(ins.id)
        
        return raidboss
    
    @classmethod
    def remove(cls, pkey):
        m = Raid.getByKey(pkey)
        if m:
            m.delete()

class PrizeMasterDummy(BaseDummy):
    """報酬情報.
    """
    def create(self, gold=0, gachapt=0, item=None, itemnum=1, card=None, cardnum=1):
        mid = _getDummyID(PrizeMaster)
        
        ins = PrizeMaster(id=mid)
        ins.gold = gold
        ins.gachapt = gachapt
        ins.itemid = 0
        if item:
            ins.itemid = item.id
            ins.itemnum = itemnum
        if card:
            ins.cardid = card.id
            ins.cardnum = cardnum
        ins.save()
        
        self.set_id(mid)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = PrizeMaster.getByKey(pkey)
        if m:
            m.delete()

class GachaMasterDummy(BaseDummy):
    """ガチャマスター情報.
    """
    def create(self, box=[], bonus=[], continuity=1, consumetype=Defines.GachaConsumeType.GACHAPT, consumevalue=0, firsttimetype=Defines.GachaFirsttimeType.NONE, firststock=0, firstcontinuity=0, consumefirstvalue=0):
        mid = _getDummyID(GachaMaster)
        boxid = _getDummyID(GachaBoxMaster)
        
        boxmaster = GachaBoxMaster(id=boxid)
        boxmaster.name = 'GachaBoxMaster:%d' % boxid
        boxmaster.box = box
        boxmaster.save()
        
        ins = GachaMaster(id=mid)
        ins.unique_name = 'GachaMaster:%d' % mid
        ins.boxid = boxid
        ins.bonus = bonus
        
        ins.continuity = continuity
        ins.consumetype = consumetype
        ins.consumevalue = consumevalue
        ins.firsttimetype = firsttimetype
        ins.firststock = firststock
        ins.firstcontinuity = firstcontinuity or continuity
        ins.consumefirstvalue = consumefirstvalue or consumevalue
        
        ins.save()
        
        self.set_id(mid)
        
        return GachaMasterSet(ins, boxmaster)
    
    @classmethod
    def remove(cls, pkey):
        m = GachaMaster.getByKey(pkey)
        if m:
            box = GachaBoxMaster.getByKey(m.boxid)
            if box:
                box.delete()
            m.delete()

class GachaGroupMasterDummy(BaseDummy):
    """ガチャグループマスター情報.
    """
    def create(self, table=[]):
        mid = _getDummyID(GachaGroupMaster)
        
        ins = GachaGroupMaster(id=mid)
        ins.name = 'GachaGroupMaster:%d' % mid
        ins.table = table
        
        # 確認.
        GachaBoxGroup(ins).validate()
        
        ins.save()
        
        self.set_id(mid)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = GachaGroupMaster.getByKey(pkey)
        if m:
            m.delete()

class GachaPlayDataDummy(BaseDummy):
    """ガチャグループマスター情報.
    """
    def create(self, uid, mid):
        
        ins = GachaPlayData.makeInstance(GachaPlayData.makeID(uid, mid))
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = GachaPlayData.getByKey(pkey)
        if m:
            m.delete()

class ShopItemMasterDummy(BaseDummy):
    """商品マスター情報.
    """
    def create(self, itype0, iid0, inum0, itype1=0, iid1=0, inum1=0, itype2=0, iid2=0, inum2=0, stock=0):
        mid = _getDummyID(ShopItemMaster)
        
        ins = ShopItemMaster(id=mid)
        ins.name = 'ShopItemMaster:%d' % mid
        ins.text = 'ShopItemMaster:%d' % mid
        ins.stock = stock
        
        ins.itype0 = itype0
        ins.iid0 = iid0
        ins.inum0 = inum0
        
        ins.itype1 = itype1
        ins.iid1 = iid1
        ins.inum1 = inum1
        
        ins.itype2 = itype2
        ins.iid2 = iid2
        ins.inum2 = inum2
        
        ins.save()
        
        self.set_id(mid)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ShopItemMaster.getByKey(pkey)
        if m:
            m.delete()

class ShopItemBuyDataDummy(BaseDummy):
    """商品購入情報.
    """
    def create(self, uid, mid):
        
        ins = ShopItemBuyData.makeInstance(ShopItemBuyData.makeID(uid, mid))
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ShopItemBuyData.getByKey(pkey)
        if m:
            m.delete()

class LoginBonusMasterDummy(BaseDummy):
    """連続ログインボーナスマスターデータ.
    """
    def create(self, day=1, prizes=None):
        
        ins = LoginBonusMaster.getValuesByKey(day)
        if not ins:
            ins = LoginBonusMaster(day=day)
            self.set_id(day)
        ins.prizes = prizes or []
        ins.save()
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = LoginBonusMaster.getByKey(pkey)
        if m:
            m.delete()

class AccessBonusMasterDummy(BaseDummy):
    """アクセスボーナスマスターデータ.
    """
    def create(self, day=0, prizes=None):
        
        ins = AccessBonusMaster.getValuesByKey(day)
        if not ins:
            ins = AccessBonusMaster(day=day)
            self.set_id(day)
        ins.prizes = prizes or []
        ins.save()
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = AccessBonusMaster.getByKey(pkey)
        if m:
            m.delete()

#        LOGIN_BONUS_TIMELIMITED_DAYS_MASTER,
class LoginBonusTimeLimitedMasterDummy(BaseDummy):
    """ロングログインボーナスマスターデータ.
    """
    def create(self):
        
        mid = _getDummyID(LoginBonusTimeLimitedMaster)
        ins = LoginBonusTimeLimitedMaster.makeInstance(mid)
        self.set_id(mid)
        ins.save()
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = LoginBonusTimeLimitedMaster.getByKey(pkey)
        if m:
            m.delete()

class LoginBonusTimeLimitedDaysMasterDummy(BaseDummy):
    """ロングログインボーナスマスターデータ.
    """
    def create(self, mid, day, prizes):
        
        ins = LoginBonusTimeLimitedDaysMaster.makeInstance(LoginBonusTimeLimitedDaysMaster.makeID(mid, day))
        ins.mid = mid
        ins.day = day
        ins.prizes = prizes
        self.set_id(ins.id)
        ins.save()
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = LoginBonusTimeLimitedDaysMaster.getByKey(pkey)
        if m:
            m.delete()

class MemoriesMasterDummy(BaseDummy):
    """思い出アルバムのマスターデータ.
    """
    def create(self, **kwargs):
        
        mid = kwargs.get('id', _getDummyID(MemoriesMaster))
        
        ins = MemoriesMaster(id=mid)
        ins.name = u'名前 %d' % ins.id
        ins.text = u'テキスト %d' % ins.id
        ins.thumb = kwargs.get('thumb', 'img/b1.png')
        ins.contenttype = kwargs.get('contenttype', 0)
        ins.contentdata = u'コンテンツデータ %d' % ins.id
        ins.cardid = mid
        
        ins.save()
        
        self.set_id(mid)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = MemoriesMaster.getByKey(pkey)
        if m:
            m.delete()

class CardAcquisitionDummy(BaseDummy):
    """思い出アルバムの解放フラグデータ.
    """
    def create(self, uid, **kwargs):
        
        mid = kwargs.get('id', _getDummyID(CardAcquisition))
        
        ins = CardAcquisition(CardAcquisition.makeID(uid, mid))
        ins.uid = uid
        ins.mid = mid
        ins.new = 0
        
        ins.save()
        
        self.set_id(mid)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = MemoriesMaster.getByKey(pkey)
        if m:
            m.delete()

class AlbumAcquisitionDummy(BaseDummy):
    """思い出アルバムの解放フラグデータ.
    """
    def create(self, uid, **kwargs):
        
        mid = kwargs.get('id', _getDummyID(AlbumAcquisition))
        
        ins = AlbumAcquisition(AlbumAcquisition.makeID(uid, mid))
        ins.uid = uid
        ins.mid = mid
        
        ins.save()
        
        self.set_id(mid)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = MemoriesMaster.getByKey(pkey)
        if m:
            m.delete()

class TutorialConfigDummy(BaseDummy):
    """チュートリアルの設定.
    """
    def create(self, ptype, scoutareaid, scoutdropcardid, prizes=None):
        
        ins = TutorialConfig.getValuesByKey(ptype)
        if not ins:
            ins = TutorialConfig(ptype=ptype)
            self.set_id(ptype)
        ins.scoutarea = scoutareaid
        ins.scoutdropcard = scoutdropcardid
        ins.prizes = prizes or []
        ins.save()
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = TutorialConfig.getByKey(pkey)
        if m:
            m.delete()

class ShopPaymentEntryDummy(BaseDummy):
    """ショップの課金情報.
    """
    def create(self, uid, shopmasterid, buynum, state):
        
        ins = ShopPaymentEntry()
        ins.id = '%s%s' % (uid, OSAUtil.makeSessionID())
        ins.uid = uid
        ins.iid = shopmasterid
        ins.inum = buynum
        ins.price = 100
        ins.state = state
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ShopPaymentEntry.getByKey(pkey)
        if m:
            m.delete()

class GachaPaymentEntryDummy(BaseDummy):
    """ガチャの課金情報.
    """
    def create(self, uid, masterid, state, continuity):
        
        ins = GachaPaymentEntry()
        ins.id = '%s%s' % (uid, OSAUtil.makeSessionID())
        ins.uid = uid
        ins.iid = masterid
        ins.inum = 1
        ins.price = 100
        ins.state = state
        ins.continuity = continuity
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = GachaPaymentEntry.getByKey(pkey)
        if m:
            m.delete()

class BattleRankMasterDummy(BaseDummy):
    """ランク.
    """
    def create(self, win=1, times=1, winprizes=None, loseprizes=None, rankupprizes=None, goldkeyrate_base=0, goldkeyrate_up=0):
        
        ins = BattleRankMaster()
        ins.id = _getDummyID(BattleRankMaster)
        ins.region = u'ダミー地方:%d' % ins.id
        ins.town = u'ダミー街:%d' % ins.id
        ins.text = u'ダミーです'
        ins.win = win
        ins.times = times
        ins.winprizes = winprizes or []
        ins.loseprizes = loseprizes or []
        ins.rankupprizes = rankupprizes or []
        ins.goldkeyrate_base = goldkeyrate_base
        ins.goldkeyrate_up = goldkeyrate_up
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = BattleRankMaster.getByKey(pkey)
        if m:
            m.delete()

class BattlePlayerDummy(BaseDummy):
    """バトルのプレイヤー情報.
    """
    def create(self, uid, rank=1, oid=0, win=0, times=0, change_cnt=0, rankopplist=None, lpvtime=None):
        ins = BattlePlayer()
        ins.id = uid
        ins.rank = rank
        ins.win_continuity = win
        ins.times = times
        ins.opponent = oid
        ins.change_cnt = 0
        ins.rankopplist = rankopplist or []
        ins.lpvtime = lpvtime or OSAUtil.get_datetime_max()
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = BattlePlayer.getByKey(pkey)
        if m:
            m.delete()

class TreasureTableMasterBaseDummy(BaseDummy):
    """宝箱出現テーブルマスタ.
    """
    @classmethod
    def get_model_cls(cls):
        raise NotImplementedError
    
    def create(self, table=None, schedule=0):
        model_cls = self.get_model_cls()
        
        ins = model_cls()
        ins.id = _getDummyID(model_cls)
        ins.name = u'Dummy:%d' % ins.id
        ins.thumb = 'common/move_size.png'
        ins.table = table or []
        ins.schedule = schedule
        ins.save()
        
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = cls.get_model_cls().getByKey(pkey)
        if m:
            m.delete()
    
class TreasureTableGoldMasterDummy(TreasureTableMasterBaseDummy):
    """金の宝箱出現テーブルマスタ.
    """
    @classmethod
    def get_model_cls(cls):
        return TreasureTableGoldMaster

class TreasureTableSilverMasterDummy(TreasureTableMasterBaseDummy):
    """銀の宝箱出現テーブルマスタ.
    """
    @classmethod
    def get_model_cls(cls):
        return TreasureTableSilverMaster

class TreasureTableBronzeMasterDummy(TreasureTableMasterBaseDummy):
    """銅の宝箱出現テーブルマスタ.
    """
    @classmethod
    def get_model_cls(cls):
        return TreasureTableBronzeMaster

class TreasureGoldMasterDummy(BaseDummy):
    """宝箱マスタ.
    """
    def create(self, itype=1, ivalue1=1, ivalue2=1, probability=100):
        ins = TreasureGoldMaster()
        ins.id = _getDummyID(TreasureGoldMaster)
        ins.itype = itype
        ins.ivalue1 = ivalue1
        ins.ivalue2 = ivalue2
        ins.probability = probability
        
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = TreasureGoldMaster.getByKey(pkey)
        if m:
            m.delete()

class TreasureSilverMasterDummy(BaseDummy):
    """宝箱マスタ.
    """
    def create(self, itype=1, ivalue1=1, ivalue2=1, probability=100):
        ins = TreasureSilverMaster()
        ins.id = _getDummyID(TreasureSilverMaster)
        ins.itype = itype
        ins.ivalue1 = ivalue1
        ins.ivalue2 = ivalue2
        ins.probability = probability
        
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = TreasureSilverMaster.getByKey(pkey)
        if m:
            m.delete()

class TreasureBronzeMasterDummy(BaseDummy):
    """宝箱マスタ.
    """
    def create(self, itype=1, ivalue1=1, ivalue2=1, probability=100):
        ins = TreasureBronzeMaster()
        ins.id = _getDummyID(TreasureBronzeMaster)
        ins.itype = itype
        ins.ivalue1 = ivalue1
        ins.ivalue2 = ivalue2
        ins.probability = probability
        
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = TreasureBronzeMaster.getByKey(pkey)
        if m:
            m.delete()

class TreasureGoldDummy(BaseDummy):
    """宝箱(金)プレイヤー所持情報.
    """
    def create(self, uid, mid, timelimit=60 * 60):
        ins = TreasureGold()
        ins.id = _getDummyID(TreasureGold)
        ins.uid = uid
        ins.mid = mid
        ins.ctime = OSAUtil.get_now()
        ins.etime = ins.ctime + datetime.timedelta(seconds=timelimit)
        
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = TreasureGold.getByKey(pkey)
        if m:
            m.delete()

class TreasureSilverDummy(BaseDummy):
    """宝箱(銀)プレイヤー所持情報.
    """
    def create(self, uid, mid, timelimit=60 * 60):
        ins = TreasureSilver()
        ins.id = _getDummyID(TreasureSilver)
        ins.uid = uid
        ins.mid = mid
        ins.ctime = OSAUtil.get_now()
        ins.etime = ins.ctime + datetime.timedelta(seconds=timelimit)
        
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = TreasureSilver.getByKey(pkey)
        if m:
            m.delete()

class TreasureBronzeDummy(BaseDummy):
    """宝箱(銅)プレイヤー所持情報.
    """
    def create(self, uid, mid, timelimit=60 * 60):
        ins = TreasureBronze()
        ins.id = _getDummyID(TreasureBronze)
        ins.uid = uid
        ins.mid = mid
        ins.ctime = OSAUtil.get_now()
        ins.etime = ins.ctime + datetime.timedelta(seconds=timelimit)
        
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = TreasureBronze.getByKey(pkey)
        if m:
            m.delete()

class TradeMasterDummy(BaseDummy):
    """秘宝交換マスタ 情報.
    """
    def create(self, itype, itemid, itemnum, rate_cabaretking, rate_demiworld):
        ins = TradeMaster()
        ins.id = _getDummyID(TradeMaster)
        ins.itype = itype
        ins.itemid = itemid
        ins.itemnum = itemnum
        ins.rate_cabaretking = rate_cabaretking
        ins.rate_demiworld = rate_demiworld
        
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = TradeMaster.getByKey(pkey)
        if m:
            m.delete()

class RaidEventMasterDummy(BaseDummy):
    """レイドイベントマスタ.
    """
    def create(self, raidtable, raidtable_timebonus=None, rankingprizes=None, destroyprizes=None, pointratio=0, pointprize_text=0, destroyprize_text=0, op=0, ed=0, champagne_num_max=0, champagne_time=0, materiallist=None, flag_dedicated_stage=False):
        ins = RaidEventMaster()
        ins.id = _getDummyID(RaidEventMaster)
        ins.name = u'RaidEventMaster:%s' % ins.id
        ins.htmlname = 'dummyevent'
        ins.effectname = 'dummyevent'
        ins.raidtable = raidtable
        ins.raidtable_timebonus = raidtable_timebonus or raidtable
        ins.raidtable_big = ins.raidtable
        ins.raidtable_timebonus_big = ins.raidtable_timebonus
        ins.rankingprizes = rankingprizes or []
        ins.destroyprizes = destroyprizes or []
        ins.pointratio = pointratio
        ins.pointprize_text = pointprize_text
        ins.destroyprize_text = destroyprize_text
        ins.op = op
        ins.ed = ed
        ins.champagne_num_max = champagne_num_max
        ins.champagne_time = champagne_time
        for idx, materialid in enumerate((materiallist or [])[:Defines.RAIDEVENT_MATERIAL_KIND_MAX]):
            setattr(ins, 'material%d' % idx, materialid)
        ins.flag_dedicated_stage = flag_dedicated_stage
        
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RaidEventMaster.getByKey(pkey)
        if m:
            m.delete()

class RaidEventRaidMasterDummy(BaseDummy):
    """レイドイベント用レイドマスタ.
    """
    def create(self, eventid, raidid, specialcard=None, ownerpoint=0, mvppoint=0, ownerpoint_timebonus=0, mvppoint_timebonus=0, pointrandmin=50, pointrandmax=150):
        ins = RaidEventRaidMaster()
        ins.id = RaidEventRaidMaster.makeID(eventid, raidid)
        ins.eventid = eventid
        ins.mid = raidid
        ins.specialcard = specialcard or []
        ins.ownerpoint = ownerpoint
        ins.mvppoint = mvppoint
        ins.ownerpoint_timebonus = ownerpoint_timebonus or ownerpoint
        ins.mvppoint_timebonus = mvppoint_timebonus or mvppoint
        ins.pointrandmin = pointrandmin
        ins.pointrandmax = pointrandmax
        
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RaidEventRaidMaster.getByKey(pkey)
        if m:
            m.delete()

class RaidEventScoreDummy(BaseDummy):
    """レイドイベントの得点.
    """
    def create(self, eventid, uid, point=0, point_total=0, destroy=0, ticket=0):
        ins = RaidEventScore.makeInstance(RaidEventScore.makeID(uid, eventid))
        ins.point = point
        ins.point_total = point_total
        ins.destroy = destroy
        ins.ticket = ticket
        
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RaidEventScore.getByKey(pkey)
        if m:
            m.delete()

class RaidEventFlagsDummy(BaseDummy):
    """レイドイベントのフラグ.
    """
    def create(self, eventid, uid, tbvtime=None):
        ins = RaidEventFlags.makeInstance(RaidEventFlags.makeID(uid, eventid))
        ins.tbvtime = tbvtime or OSAUtil.get_now()
        
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RaidEventFlags.getByKey(pkey)
        if m:
            m.delete()

class RaidEventChampagneDummy(BaseDummy):
    """シャンパンコール情報.
    """
    def create(self, uid, eventid, num, etime=None):
        ins = RaidEventChampagne.makeInstance(uid)
        ins.eventid = eventid
        ins.num = num
        ins.etime = etime or OSAUtil.get_now()
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RaidEventChampagne.getByKey(pkey)
        if m:
            m.delete()

class RaidEventRecipeMasterDummy(BaseDummy):
    """レイドイベント交換所のレシピ.
    """
    def create(self, eventid, itype=Defines.ItemType.GOLD, itemid=0, itemnum=100, stock=0, material_num_list=None):
        ins_id = _getDummyID(RaidEventRecipeMaster)
        
        ins = RaidEventRecipeMaster.makeInstance(ins_id)
        ins.name = 'recipe:%s' % ins_id
        ins.thumb = 'hoge'
        ins.eventid = eventid
        ins.itype = itype
        ins.itemid = itemid
        ins.itemnum = itemnum
        ins.stock = stock
        for idx, material_num in enumerate((material_num_list or [])[:Defines.RAIDEVENT_MATERIAL_KIND_MAX]):
            setattr(ins, 'materialnum%s' % idx, material_num)
        ins.save()
        
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RaidEventRecipeMaster.getByKey(pkey)
        if m:
            m.delete()

class RaidEventMixDataDummy(BaseDummy):
    """レイドイベント交換所の交換回数データ.
    """
    def create(self, uid, recipemaster, cnt):
        
        ins = RaidEventMixData.makeInstance(RaidEventMixData.makeID(uid, recipemaster.id))
        ins.eventid = recipemaster.eventid
        ins.cnt = cnt
        ins.save()
        
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RaidEventMixData.getByKey(pkey)
        if m:
            m.delete()

class RaidEventMaterialMasterDummy(BaseDummy):
    """レイドイベント交換所の素材マスター.
    """
    def create(self):
        ins_id = _getDummyID(RaidEventMaterialMaster)
        
        ins = RaidEventMaterialMaster.makeInstance(ins_id)
        ins.name = 'material:%s' % ins_id
        ins.thumb = 'hoge'
        ins.save()
        
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RaidEventMaterialMaster.getByKey(pkey)
        if m:
            m.delete()

class RaidEventMaterialDataDummy(BaseDummy):
    """レイドイベント交換所の素材所持数データ.
    """
    def create(self, uid, eventid, material_num_list):
        
        ins = RaidEventMaterialData.makeInstance(uid)
        ins.eventid = eventid
        for idx, material_num in enumerate((material_num_list or [])[:Defines.RAIDEVENT_MATERIAL_KIND_MAX]):
            ins.setMaterialNum(eventid, idx, material_num)
        ins.save()
        
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RaidEventMaterialData.getByKey(pkey)
        if m:
            m.delete()

class RaidEventScoutStageMasterDummy(BaseDummy):
    """レイドイベント専用ステージ.
    """
    def create(self, eventid, stage, area=1, prizes=None, boss=0, bossprizes=None, execution=1, apcost=0, exp=0, gold=0, dropitems=None, happenings=None, treasuregold=0, treasuresilver=0, treasurebronze=0, bossscenario=0):
        
        key = _getDummyID(RaidEventScoutStageMaster)
        
        ins = RaidEventScoutStageMaster.makeInstance(key)
        ins.eventid = eventid
        ins.stage = stage
        ins.area = area
        ins.areaname = u'RaidEventScoutStageMasterDummy'
        ins.schedule = 0
        ins.prizes = prizes or []
        ins.boss = boss
        ins.bossprizes = bossprizes or []
        ins.execution = execution
        ins.apcost = apcost
        ins.exp = exp
        ins.goldmin = gold
        ins.goldmax = gold
        
        ins.eventrate_drop = 1 if dropitems else 0
        ins.eventrate_happening = 1 if happenings else 0
        ins.eventrate_treasure = 1 if treasuregold or treasuresilver or treasurebronze else 0
        
        ins.dropitems = dropitems or []
        ins.happenings = happenings or []
        ins.happenings_timebonus = ins.happenings
        ins.happenings_big = ins.happenings
        ins.happenings_timebonus_big = ins.happenings
        ins.treasuregold = treasuregold
        ins.treasuresilver = treasuresilver
        ins.treasurebronze = treasurebronze
        
        ins.bossscenario = bossscenario
        
        ins.save()
        
        self.set_id(key)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RaidEventScoutStageMaster.getByKey(pkey)
        if m:
            m.delete()

class RaidEventScoutPlayDataDummy(BaseDummy):
    """レイドイベントスカウトプレイ情報.
    """
    def create(self, uid, eventid, stage=1, cleared=0, progress=0):
        
        ins = RaidEventScoutPlayData.makeInstance(RaidEventScoutPlayData.makeID(uid, eventid))
        ins.stage = stage
        ins.cleared = cleared
        ins.progress = progress
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RaidEventScoutPlayData.getByKey(pkey)
        if m:
            m.delete()

class InviteMasterDummy(BaseDummy):
    """招待マスター.
    """
    def create(self, prizes, schedule=0, mid=None):
        if mid is None:
            mid = _getDummyID(InviteMaster)
        
        ins = InviteMaster.makeInstance(mid)
        ins.prizes = prizes
        ins.save()
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = InviteMaster.getByKey(pkey)
        if m:
            m.delete()

class InviteDummy(BaseDummy):
    """招待カウンタ.
    """
    def create(self, uid, mid, cnt=0):
        ins = Invite.makeInstance(Invite.makeID(uid, mid))
        ins.cnt = cnt
        ins.save()
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = Invite.getByKey(pkey)
        if m:
            m.delete()

class InviteDataDummy(BaseDummy):
    """招待レコード.
    """
    def create(self, dmmid, from_id, state=Defines.InviteState.SEND):
        ins = InviteData.makeInstance(dmmid)
        ins.fid = from_id
        ins.state = state
        ins.save()
        self.set_id(dmmid)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = InviteData.getByKey(pkey)
        if m:
            m.delete()

class ScoutEventMasterDummy(BaseDummy):
    """スカウトイベントマスター.
    """
    def create(self, rankingprizes=None, pointprizes=None, op=0, ed=0, lovetime_star=0, lovetime_timelimit=0, lovetime_tanzakuup=0):
        mid = _getDummyID(ScoutEventMaster)
        
        ins = ScoutEventMaster.makeInstance(mid)
        ins.name = 'ScoutEventMasterDummy:%s' % mid
        ins.htmlname = 'dummy'
        ins.effectname = 'dummy'
        ins.rankingprizes = rankingprizes or {}
        ins.rankingprize_text = 0
        ins.pointprizes = pointprizes or []
        ins.pointprize_text = 0
        ins.op = op
        ins.ed = ed
        ins.lovetime_star = lovetime_star
        ins.lovetime_timelimit = lovetime_timelimit
        ins.lovetime_tanzakuup = lovetime_tanzakuup
        ins.save()
        
        self.set_id(mid)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ScoutEventMaster.getByKey(pkey)
        if m:
            m.delete()

class ScoutEventStageMasterDummy(BaseDummy):
    """イベント限定スカウトマスター.
    """
    def create(self, eventid, stage, area=1, prizes=None, boss=0, bossprizes=None, execution=1, apcost=0, exp=0, gold=0, dropitems=None, happenings=None, treasuregold=0, treasuresilver=0, treasurebronze=0, eventpoint=0, lovetime_star_min=0, lovetime_star_max=0):
        
        key = _getDummyID(ScoutEventStageMaster)
        
        ins = ScoutEventStageMaster.makeInstance(key)
        ins.eventid = eventid
        ins.stage = stage
        ins.area = area
        ins.areaname = u'ScoutEventStageMasterDummy'
        ins.schedule = 0
        ins.prizes = prizes or []
        ins.boss = boss
        ins.bossprizes = bossprizes or []
        ins.execution = execution
        ins.apcost = apcost
        ins.exp = exp
        ins.goldmin = gold
        ins.goldmax = gold
        
        ins.eventrate_drop = 1 if dropitems else 0
        ins.eventrate_happening = 1 if happenings else 0
        ins.eventrate_treasure = 1 if ins.treasuregold or ins.treasuresilver or ins.treasurebronze else 0
        
        ins.dropitems = dropitems or []
        ins.happenings = happenings or []
        ins.treasuregold = treasuregold
        ins.treasuresilver = treasuresilver
        ins.treasurebronze = treasurebronze
        ins.eventpointmin = eventpoint
        ins.eventpointmax = eventpoint
        
        ins.lovetime_star_min = lovetime_star_min
        ins.lovetime_star_max = max(0, ins.lovetime_star_min, lovetime_star_max)
        ins.eventrate_lt_star = 1 if 0 < ins.lovetime_star_min <= ins.lovetime_star_max else 0
        
        ins.save()
        
        self.set_id(key)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ScoutEventStageMaster.getByKey(pkey)
        if m:
            m.delete()
    
class ScoutEventPlayDataDummy(BaseDummy):
    """スカウトイベントプレイ情報.
    """
    def create(self, uid, eventid, stage=1, cleared=0, feveretime=None, progress=0, star=0, lovetime_etime=None):
        
        ins = ScoutEventPlayData.makeInstance(ScoutEventPlayData.makeID(uid, eventid))
        ins.stage = stage
        ins.cleared = cleared
        ins.feveretime = feveretime or OSAUtil.get_now()
        ins.progress = progress
        ins.star = star
        ins.lovetime_etime = lovetime_etime or OSAUtil.get_now()
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ScoutEventPlayData.getByKey(pkey)
        if m:
            m.delete()

class ScoutEventScoreDummy(BaseDummy):
    """スカウトイベントのスコア.
    """
    def create(self, uid, eventid, point=0, tip=0):
        ins = ScoutEventScore.makeInstance(ScoutEventScore.makeID(uid, eventid))
        ins.point = point
        ins.point_total = point
        ins.tip = tip
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ScoutEventScore.getByKey(pkey)
        if m:
            m.delete()

class ScoutEventFlagsDummy(BaseDummy):
    """スカウトイベントのフラグ.
    """
    def create(self, uid, eventid, opvtime=None):
        ins = ScoutEventFlags.makeInstance(ScoutEventFlags.makeID(uid, eventid))
        ins.opvtime = opvtime or OSAUtil.get_now()
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ScoutEventFlags.getByKey(pkey)
        if m:
            m.delete()

class ScoutEventPresentPrizeMasterDummy(BaseDummy):
    """スカウトイベントのプレゼント報酬.
    """
    def create(self, eventid, number, prizes):
        ins = ScoutEventPresentPrizeMaster()
        ins.id = ScoutEventPresentPrizeMaster.makeID(eventid, number)
        ins.eventid = eventid
        ins.number = number
        ins.prizes = prizes
        ins.name = 'Dummy:%d' % number
        ins.text = 'Dummy:%d' % number
        ins.mgrname = 'Dummy:%d' % number
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ScoutEventPresentPrizeMaster.getByKey(pkey)
        if m:
            m.delete()

class ScoutEventPresentNumDummy(BaseDummy):
    """スカウトイベントのプレゼント報酬.
    """
    def create(self, uid, eventid, point=0, nums=None, result_number=0, result_pointpre=0, result_pointpost=0):
        ins = ScoutEventPresentNum.makeInstance(ScoutEventPresentNum.makeID(uid, eventid))
        ins.point = point
        ins.nums = nums or {}
        ins.result_number = result_number
        ins.result_pointpre = result_pointpre
        ins.result_pointpost = result_pointpost
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ScoutEventPresentNum.getByKey(pkey)
        if m:
            m.delete()

class ScoutEventRaidMasterDummy(BaseDummy):
    """スカウトイベントのレイドマスター.
    """
    def create(self, eventid, raidid, tanzaku_number=0, tanzaku_randmin=0, tanzaku_randmax=0, tanzaku_help_number=0, tanzaku_help_randmin=0, tanzaku_help_randmax=0):
        
        ins = ScoutEventRaidMaster.makeInstance(ScoutEventRaidMaster.makeID(eventid, raidid))
        ins.tanzaku_number = tanzaku_number
        ins.tanzaku_randmin = tanzaku_randmin
        ins.tanzaku_randmax = tanzaku_randmax
        ins.tanzaku_rate = 100 if 0 < tanzaku_randmin else 0
        ins.tanzaku_help_number = tanzaku_help_number
        ins.tanzaku_help_randmin = tanzaku_help_randmin
        ins.tanzaku_help_randmax = tanzaku_help_randmax
        ins.tanzaku_help_rate = 100 if 0 < tanzaku_help_randmin else 0
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ScoutEventRaidMaster.getByKey(pkey)
        if m:
            m.delete()

class ScoutEventTanzakuCastMasterDummy(BaseDummy):
    """スカウトイベントの短冊とキャストのマスター.
    """
    def create(self, eventid, number, prizes=None, tanzaku=0, tip_rate=0, tip_quota=0):
        
        ins = ScoutEventTanzakuCastMaster.makeInstance(ScoutEventTanzakuCastMaster.makeID(eventid, number))
        ins.castname = u'キャスト名'
        ins.castthumb = u'hoge'
        ins.tanzakuthumb = u'hoge'
        ins.prizes = prizes or []
        ins.tanzaku = tanzaku
        ins.tip_rate = tip_rate
        ins.tip_quota = tip_quota
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ScoutEventTanzakuCastMaster.getByKey(pkey)
        if m:
            m.delete()

class ScoutEventTanzakuCastDataDummy(BaseDummy):
    """スカウトイベントの短冊とチップの情報.
    """
    def create(self, uid, eventid, current_cast=-1, tanzaku_nums=None, tip_nums=None):
        
        ins = ScoutEventTanzakuCastData.makeInstance(ScoutEventTanzakuCastData.makeID(uid, eventid))
        ins.current_cast = current_cast
        
        if tanzaku_nums:
            for k,v in tanzaku_nums.items():
                ins.set_tanzaku(k, v)
        
        if tip_nums:
            for k,v in tip_nums.items():
                ins.set_tip(k, v)
        
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ScoutEventTanzakuCastData.getByKey(pkey)
        if m:
            m.delete()

class ScoutEventHappeningTableMasterDummy(BaseDummy):
    """スカウトイベントの曜日別レイド発生テーブル.
    """
    def create(self, eventid, wday, happenings=None):
        
        ins = ScoutEventHappeningTableMaster.makeInstance(ScoutEventHappeningTableMaster.makeID(eventid, wday))
        ins.happenings = happenings or []
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ScoutEventHappeningTableMaster.getByKey(pkey)
        if m:
            m.delete()

class BattleEventMasterDummy(BaseDummy):
    """バトルイベントのマスター.
    """
    def create(self, rankingprizes=None, pointprizes=None, specialtype=Defines.CharacterType.ALL, specialtable=None, rankstart=1, rankbeginer=1, op=0, ed=0):
        
        ins = BattleEventMaster()
        ins.id = _getDummyID(BattleEventMaster)
        ins.name = 'BEMasterDummy:%s' % ins.id
        ins.htmlname = 'dummy'
        ins.effectname = 'dummy'
        ins.rankingprizes = rankingprizes or []
        ins.rankingprize_text = 0
        ins.pointprizes = pointprizes or []
        ins.pointprize_text = 0
        ins.specialtype = specialtype
        ins.specialtable = specialtable or []
        ins.rankstart = rankstart
        ins.rankbeginer = rankbeginer
        ins.op = op
        ins.ed = ed
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = BattleEventMaster.getByKey(pkey)
        if m:
            m.delete()

class BattleEventRankMasterDummy(BaseDummy):
    """バトルイベントのマスター.
    """
    def create(self, eventid, rank, bpcost=0, membernummax_auto=30, membernummax_additional=20, loginbonus=None, pointtable=None, rankuptable=None, battlepoint_w=0, battlepoint_l=0, battlepoint_lv=0, battlepointreceive=0, winprizes=None, loseprizes=None, group_rankingprizes=None, pointrandmin=50, pointrandmax=150):
        
        ins = BattleEventRankMaster()
        ins.id = BattleEventRankMaster.makeID(eventid, rank)
        ins.name = 'BERankMasterDummy:%s' % ins.id
        ins.eventid = eventid
        ins.rank = rank
        ins.bpcost = bpcost
        ins.membernummax_auto = membernummax_auto
        ins.membernummax_additional = membernummax_additional
        ins.loginbonus = loginbonus or []
        ins.loginbonus_text = 0
        ins.pointtable = pointtable or []
        ins.rankuptable = rankuptable or []
        ins.battlepoint_w = battlepoint_w
        ins.battlepoint_l = battlepoint_l
        ins.battlepoint_lv = battlepoint_lv
        ins.battlepointreceive = battlepointreceive
        ins.winprizes = winprizes or []
        ins.winprizes_text = 0
        ins.loseprizes = loseprizes or []
        ins.loseprizes_text = 0
        ins.group_rankingprizes = group_rankingprizes or []
        ins.group_rankingprize_text = 0
        ins.pointrandmin = pointrandmin
        ins.pointrandmax = pointrandmax
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = BattleEventRankMaster.getByKey(pkey)
        if m:
            m.delete()

class BattleEventScoreDummy(BaseDummy):
    """バトルイベントのスコア.
    """
    def create(self, uid, eventid, point=0, win=0, ltime=None):
        ins = BattleEventScore.makeInstance(BattleEventScore.makeID(uid, eventid))
        
        ins.point = point
        ins.point_total = point
        ins.win = win
        ins.winmax = win
        ins.ltime = ltime or OSAUtil.get_now()
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = BattleEventScore.getByKey(pkey)
        if m:
            m.delete()

class BattleEventFlagsDummy(BaseDummy):
    """バトルイベントのフラグ.
    """
    def create(self, uid, eventid, opvtime=None, epvtime=None):
        ins = BattleEventFlags.makeInstance(BattleEventFlags.makeID(uid, eventid))
        ins.opvtime = opvtime or OSAUtil.get_now()
        ins.epvtime = epvtime or OSAUtil.get_now()
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = BattleEventFlags.getByKey(pkey)
        if m:
            m.delete()

class BattleEventRankDummy(BaseDummy):
    """バトルイベントのランク情報.
    """
    def create(self, uid, eventid, rank=0, fame=0, rank_next=0, fame_next=0, utime=None, groups=None):
        ins = BattleEventRank.makeInstance(BattleEventRank.makeID(uid, eventid))
        
        ins.rank = rank
        ins.fame = fame
        ins.rank_next = rank_next
        ins.fame_next = fame_next
        ins.utime = utime or OSAUtil.get_now()
        ins.groups = groups or []
        
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = BattleEventRank.getByKey(pkey)
        if m:
            m.delete()

class BattleEventGroupLogDummy(BaseDummy):
    """バトルイベントのランク履歴情報.
    """
    def create(self, rankrecord, rank=None, cdate=None, userdata=None):
        ins = BattleEventGroupLog()
        ins.id = _getDummyID(BattleEventGroupLog)
        ins.eventid = rankrecord.mid
        
        if userdata is None:
            data = BattleEventGroupUserData()
            data.uid = rankrecord.uid
            data.point = 100
            data.win = 3
            data.fame = 2
            data.rankup = 1
            userdata = [data]
        ins.userdata = userdata
        ins.cdate = cdate or datetime.date.today()
        ins.rankid = BattleEventRankMaster.makeID(rankrecord.mid, rank or rankrecord.rank)
        ins.save()
        self.set_id(ins.id)
        
        rankrecord.groups.insert(0, ins.id)
        rankrecord.save()
        
        ModelRequestMgr().delete_models_from_cache(BattleEventRank, [rankrecord.id])
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = BattleEventRank.getByKey(pkey)
        if m:
            m.delete()

class BattleEventPresentContentMasterDummy(BaseDummy):
    """バトルイベント贈り物の中身マスター.
    """
    def create(self, prizes=None):
        
        ins = BattleEventPresentContentMaster()
        ins.id = _getDummyID(BattleEventPresentContentMaster)
        ins.prizes = prizes or []
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = BattleEventPresentContentMaster.getByKey(pkey)
        if m:
            m.delete()

class BattleEventPresentMasterDummy(BaseDummy):
    """バトルイベント贈り物マスター.
    """
    def create(self, eventid, number, contents=None, point=1, rate=1, special_conditions=None):
        
        ins = BattleEventPresentMaster.makeInstance(BattleEventPresentMaster.makeID(eventid, number))
        ins.contents = contents or []
        ins.point = point
        ins.rate = rate
        
        if special_conditions:
            for idx,cond in enumerate(special_conditions):
                setattr(ins, 'specialnum%s' % idx, cond['num'])
                setattr(ins, 'specialcnt%s' % idx, cond['cnt'])
        
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = BattleEventPresentMaster.getByKey(pkey)
        if m:
            m.delete()

class BattleEventPresentDataDummy(BaseDummy):
    """バトルイベント贈り物ユーザ情報.
    """
    def create(self, uid, eventid, point=0, currentnum=0, currentcontent=0, prenum=0, precontent=0):
        
        ins = BattleEventPresentData.makeInstance(BattleEventPresentData.makeID(uid, eventid))
        ins.point = point
        ins.currentnum = currentnum
        ins.currentcontent = currentcontent
        ins.prenum = prenum
        ins.precontent = precontent
        
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = BattleEventPresentData.getByKey(pkey)
        if m:
            m.delete()

class BattleEventPresentCountsDummy(BaseDummy):
    """バトルイベント贈り物出現回数.
    """
    def create(self, uid, number, cnt=0):
        
        ins = BattleEventPresentCounts.makeInstance(BattleEventPresentCounts.makeID(uid, number))
        ins.cnt = cnt
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = BattleEventPresentCounts.getByKey(pkey)
        if m:
            m.delete()

class PromotionConfigKoihimeDummy(BaseDummy):
    """クロスプロモーション設定.
    """
    def create(self):
        
        ins = PromotionConfigKoihime.getByKey(PromotionConfigKoihime.SINGLE_ID)
        if ins is None:
            ins = PromotionConfigKoihime.makeInstance(PromotionConfigKoihime.SINGLE_ID)
            ins.schedule = 0
            ins.name = 'PromotionConfigKoihime'
            ins.appurl = ''
            ins.appurl_sandbox = ''
            ins.save()
            
            self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = PromotionConfigKoihime.getByKey(pkey)
        if m:
            m.delete()

class PromotionPrizeMasterKoihimeDummy(BaseDummy):
    """クロスプロモーション報酬.
    """
    def create(self, rid=1, prizes=None):
        
        ins = PromotionPrizeMasterKoihime()
        
        ins.id = _getDummyID(PromotionPrizeMasterKoihime)
        ins.rid = rid
        ins.prizes = prizes or []
        ins.prize_text = 0
        ins.name = 'PromotionPrizeMasterKoihimeDummy:%s' % ins.id
        ins.text = 'PromotionPrizeMasterKoihimeDummy:%s' % ins.id
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = PromotionPrizeMasterKoihime.getByKey(pkey)
        if m:
            m.delete()

class PromotionRequirementMasterKoihimeDummy(BaseDummy):
    """クロスプロモーション達成条件.
    """
    def create(self, condition_type=None, condition_value=None):
        
        ins = PromotionRequirementMasterKoihime()
        
        ins.id = _getDummyID(PromotionRequirementMasterKoihime)
        ins.name = 'PromotionRequirementMasterKoihime:%s' % ins.id
        ins.text = 'PromotionRequirementMasterKoihime:%s' % ins.id
        ins.condition_type = condition_type or Defines.PromotionRequirementType.LEVEL
        ins.condition_value = condition_value or 0
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = PromotionRequirementMasterKoihime.getByKey(pkey)
        if m:
            m.delete()

class PromotionDataKoihimeDummy(BaseDummy):
    """クロスプロモーション報酬受取状態.
    """
    def create(self, uid, mid, status):
        
        ins = PromotionDataKoihime.makeInstance(PromotionDataKoihime.makeID(uid, mid))
        ins.status = status
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = PromotionDataKoihime.getByKey(pkey)
        if m:
            m.delete()

class SerialCampaignMasterDummy(BaseDummy):
    """シリアルコード入力キャンペーンマスター.
    """
    def create(self, prizes=None, schedule=0, limit_pp=0):
        
        ins_id = _getDummyID(SerialCampaignMaster)
        
        ins = SerialCampaignMaster.makeInstance(ins_id)
        ins.name = 'Dummy_%s' % ins.id
        ins.rtime = OSAUtil.get_now()
        ins.header = 'dummy_img'
        ins.schedule = schedule
        ins.prizes = prizes or []
        ins.prize_img = 'dummy_img'
        ins.prize_text = 0
        ins.limit_pp = limit_pp
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = SerialCampaignMaster.getByKey(pkey)
        if m:
            m.delete()

class SerialCodeDummy(BaseDummy):
    """シリアルコード.
    """
    def create(self, mid, uid=0):
        
        ins_id = _getDummyID(SerialCode)
        
        ins = SerialCode.makeInstance(ins_id)
        ins.serial = 'DUMMY%s' % ins_id
        ins.mid = mid
        ins.uid = uid
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = SerialCode.getByKey(pkey)
        if m:
            key = 'get_serialcode_by_serial:%s' % m.serial
            OSAUtil.get_cache_client().delete(key)
            m.delete()

class SerialCountDummy(BaseDummy):
    """シリアルコード入力回数.
    """
    def create(self, uid, mid, cnt=0):
        
        ins_id = SerialCount.makeID(uid, mid)
        
        ins = SerialCount.makeInstance(ins_id)
        ins.cnt = cnt
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = SerialCount.getByKey(pkey)
        if m:
            m.delete()

class ComeBackCampaignMasterDummy(BaseDummy):
    """カムバックキャンペーンマスター.
    """
    def create(self, interval, prize_1, prize_2, prize_3, prize_4, prize_5, prize_6, prize_7):
        
        ins_id = _getDummyID(ComeBackCampaignMaster)
        
        ins = ComeBackCampaignMaster.makeInstance(ins_id)
        ins.name = 'Dummy_%s' % ins.id
        ins.interval = interval
        ins.prize_1 = prize_1
        ins.prize_2 = prize_2
        ins.prize_3 = prize_3
        ins.prize_4 = prize_4
        ins.prize_5 = prize_5
        ins.prize_6 = prize_6
        ins.prize_7 = prize_7
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ComeBackCampaignMaster.getByKey(pkey)
        if m:
            m.delete()

class ComeBackCampaignDataDummy(BaseDummy):
    """カムバックキャンペーンのユーザ情報.
    """
    def create(self, uid, mid, days=0, comeback=False):
        ins_id = ComeBackCampaignData.makeID(uid, mid)
        
        ins = ComeBackCampaignData.makeInstance(ins_id)
        ins.days = days
        ins.comeback = comeback
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ComeBackCampaignData.getByKey(pkey)
        if m:
            m.delete()

class CardStockDummy(BaseDummy):
    """異動情報.
    """
    def create(self, uid, mid, num=0):
        ins_id = CardStock.makeID(uid, mid)
        
        ins = CardStock.makeInstance(ins_id)
        ins.num = num
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = CardStock.getByKey(pkey)
        if m:
            m.delete()

class PanelMissionPanelMasterDummy(BaseDummy):
    """パネルミッションのパネル.
    """
    def create(self, prizes=None):
        
        ins_id = _getDummyID(PanelMissionPanelMaster)
        
        ins = PanelMissionPanelMaster.makeInstance(ins_id)
        ins.name = 'Dummy:%s' % ins_id
        ins.prizes = prizes or []
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = PanelMissionPanelMaster.getByKey(pkey)
        if m:
            m.delete()

class PanelMissionMissionMasterDummy(BaseDummy):
    """パネルミッションのミッション.
    """
    def create(self, panel, number, prizes=None, condition_type=0, condition_value1=0, condition_value2=0):
        
        ins_id = PanelMissionMissionMaster.makeID(panel, number)
        
        ins = PanelMissionMissionMaster.makeInstance(ins_id)
        ins.name = 'Dummy:%s' % ins_id
        ins.prizes = prizes or []
        ins.condition_type = condition_type
        ins.condition_value1 = condition_value1
        ins.condition_value2 = condition_value2
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = PanelMissionMissionMaster.getByKey(pkey)
        if m:
            m.delete()

class PlayerPanelMissionDummy(BaseDummy):
    """パネルミッションのプレイヤー.
    """
    def create(self, uid, panel=1):
        
        ins = PlayerPanelMission.makeInstance(uid)
        ins.panel = panel
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = PlayerPanelMission.getByKey(pkey)
        if m:
            m.delete()

class PanelMissionDataDummy(BaseDummy):
    """パネルミッションのミッションの進行度.
    """
    def create(self, uid, panel, missiondata_dict):
        
        ins_id = PanelMissionData.makeID(uid, panel)
        
        ins = PanelMissionData.makeInstance(ins_id)
        
        for number in xrange(1, Defines.PANELMISSION_MISSIN_NUM_PER_PANEL+1):
            missiondata = missiondata_dict.get(number)
            if missiondata:
                ins.set_data(number, **missiondata)
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = PanelMissionData.getByKey(pkey)
        if m:
            m.delete()


class EventScenarioMasterDummy(BaseDummy):
    """イベントシナリオ.
    """
    def create(self):
        
        ins_id = _getDummyID(ScenarioMaster)
        
        ins = ScenarioMaster.makeInstance(ins_id)
        ins.number = ScenarioMaster.max_value('number', 1) + 1
        ins.name = u'hoge'
        ins.bg = u'hoge'
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = ScenarioMaster.getByKey(pkey)
        if m:
            m.delete()

class RankingGachaMasterDummy(BaseDummy):
    """ランキングガチャのマスターデータ.
    """
    def create(self, boxid, randmin=0, randmax=0, singleprizes=None, totalprizes=None, group=None, wholeprizes=None, wholewinprizes=None):
        
        ins_id = boxid
        
        ins = RankingGachaMaster.makeInstance(ins_id)
        ins.name = 'RankingGachaMaster:%s' % ins_id
        ins.randmin = randmin
        ins.randmax = randmax
        ins.singleprizes = singleprizes or []
        ins.singleprize_text = 0
        ins.totalprizes = totalprizes or []
        ins.totalprize_text = 0
        ins.img_rule = 'hoge'
        ins.img_appeal = 'fuga'
        ins.group = group or ins_id
        ins.wholeprizes = wholeprizes or []
        ins.wholeprize_text = 0
        ins.wholewinprizes = wholewinprizes or []
        ins.wholewinprize_text = 0
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        arr = [
            RankingGachaMaster.getByKey(pkey),
            RankingGachaWholeData.getByKey(pkey),
        ]
        for m in arr:
            if m:
                m.delete()
        
        RankingGachaScore.all().filter(mid=pkey).delete()
        RankingGachaWholePrizeQueue.all().filter(boxid=pkey).delete()
        
        RankingGachaSingleRanking.getDB().delete(RankingGachaSingleRanking.makeKey(pkey))
        RankingGachaTotalRanking.getDB().delete(RankingGachaTotalRanking.makeKey(pkey))
        RankingGachaWholePrizeQueueIdSet.flush()

class RankingGachaScoreDummy(BaseDummy):
    """ランキングガチャのスコア情報.
    """
    def create(self, uid, boxid, single=0, total=0, firstpoint=0):
        
        ins_id = RankingGachaScore.makeID(uid, boxid)
        
        ins = RankingGachaScore.makeInstance(ins_id)
        ins.single = single
        ins.total = total
        ins.firstpoint = firstpoint
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RankingGachaScore.getByKey(pkey)
        if m:
            m.delete()

class RankingGachaWholePrizeQueueDummy(BaseDummy):
    """ランキングガチャの総計pt達成報酬配布キュー.
    """
    def create(self, boxid, point=0, prizes=None):
        
        ins = RankingGachaWholePrizeQueue()
        ins.boxid = boxid
        ins.point = point
        ins.prizes = prizes or []
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RankingGachaWholePrizeQueue.getByKey(pkey)
        if m:
            m.delete()

class RankingGachaWholePrizeDataDummy(BaseDummy):
    """ランキングガチャの総計pt達成報酬受け取り情報.
    """
    def create(self, uid, queueid=0):
        
        ins = RankingGachaWholePrizeData.makeInstance(uid)
        ins.queueid = queueid
        ins.save()
        
        self.set_id(ins.id)
        
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = RankingGachaWholePrizeData.getByKey(pkey)
        if m:
            m.delete()

class LoginBonusSugorokuMasterDummy(BaseDummy):
    """双六ログインボーナス.
    """
    def create(self, mapidlist, queueid=0):
        ins_id = _getDummyID(LoginBonusSugorokuMaster)
        ins = LoginBonusSugorokuMaster.makeInstance(ins_id)
        ins.name = u'Dummy:{}'.format(ins_id)
        ins.maps = mapidlist
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = LoginBonusSugorokuMaster.getByKey(pkey)
        if m:
            m.delete()

class LoginBonusSugorokuMapMasterDummy(BaseDummy):
    """双六ログインボーナスのマップ.
    """
    def create(self, prizeidlist=None):
        ins_id = _getDummyID(LoginBonusSugorokuMapMaster)
        ins = LoginBonusSugorokuMapMaster.makeInstance(ins_id)
        ins.name = ins.effectname = u'Dummy:{}'.format(ins_id)
        ins.prize = prizeidlist or []
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = LoginBonusSugorokuMapMaster.getByKey(pkey)
        if m:
            m.delete()

class LoginBonusSugorokuMapSquaresMasterDummy(BaseDummy):
    """双六ログインボーナスのマス.
    """
    def create(self, mapid, number, event_type=Defines.SugorokuMapEventType.NONE, event_value=0, prizeidlist=None, last=False):
        ins_id = LoginBonusSugorokuMapSquaresMaster.makeID(mapid, number)
        ins = LoginBonusSugorokuMapSquaresMaster.makeInstance(ins_id)
        ins.name = ins.name_mgr = ins.thumb = u'Dummy:{}'.format(ins_id)
        ins.event_type = event_type
        ins.event_value = event_value
        ins.prize = prizeidlist or []
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = LoginBonusSugorokuMapSquaresMaster.getByKey(pkey)
        if m:
            m.delete()

class LoginBonusSugorokuPlayerDataDummy(BaseDummy):
    """双六ログインボーナスのマス.
    """
    def create(self, uid, mid, lap=0, loc=1, lose_turns=0):
        ins_id = LoginBonusSugorokuPlayerData.makeID(uid, mid)
        ins = LoginBonusSugorokuPlayerData.makeInstance(ins_id)
        ins.lap = lap
        ins.loc = loc
        ins.lose_turns = lose_turns
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = LoginBonusSugorokuPlayerData.getByKey(pkey)
        if m:
            m.delete()

class CabaClubMasterDummy(BaseDummy):
    """キャバクラシステムの設定.
    """
    def create(self, week=None, customer_prizes=None, customer_prize_interval=0, cr_correction=None):
        ins = None
        if week:
            arr = CabaClubMaster.fetchValues(filters=dict(week=week))
            if arr:
                ins = arr
        if ins is None:
            ins = CabaClubMaster.makeInstance(_getDummyID(CabaClubMaster))
            self.set_id(ins.id)
        ins.name = u'Dummy:%s' % week
        ins.customer_prizes = customer_prizes or []
        ins.cr_correction = cr_correction or dict()
        ins.save()
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = CabaClubMaster.getByKey(pkey)
        if m:
            m.delete()

class CabaClubEventMasterDummy(BaseDummy):
    """キャバクラシステムの発生イベント.
    """
    def create(self, seconds=0, customer_up=100, proceeds_up=100, ua_type=Defines.CabaClubEventUAType.NONE, ua_value=0, ua_cost=0):
        
        ins_id = _getDummyID(CabaClubEventMaster)
        ins = CabaClubEventMaster.makeInstance(ins_id)
        ins.name = ins.text = u'Dummy:%s' % ins_id
        ins.seconds = seconds
        ins.customer_up = customer_up
        ins.proceeds_up = proceeds_up
        ins.ua_type = ua_type
        ins.ua_value = ua_value
        ins.ua_cost = ua_cost
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = CabaClubEventMaster.getByKey(pkey)
        if m:
            m.delete()

class CabaClubStoreMasterDummy(BaseDummy):
    """キャバクラシステムの店舗.
    """
    def create(self, days=0, cost=0, customer_interval=0, proceeds_rand_min=100, proceeds_rand_max=100, customer_rand_min=100, customer_rand_max=100, customer_max=0, cast_num_max=0, scoutman_num_max=0, scoutman_add_max=0, events=None):
        ins_id = _getDummyID(CabaClubStoreMaster)
        ins = CabaClubStoreMaster.makeInstance(ins_id)
        ins.name = ins.text = ins.thumb = u'Dummy:%s' % ins_id
        ins.days_0 = days
        ins.cost_0 = cost
        ins.customer_interval = customer_interval
        ins.proceeds_rand_min = proceeds_rand_min
        ins.proceeds_rand_max = proceeds_rand_max
        ins.customer_rand_min = customer_rand_min
        ins.customer_rand_max = customer_rand_max
        ins.customer_max = customer_max
        ins.cast_num_max = cast_num_max
        ins.scoutman_num_max = scoutman_num_max
        ins.scoutman_add_max = scoutman_add_max
        ins.events = events or []
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = CabaClubStoreMaster.getByKey(pkey)
        if m:
            m.delete()

class CabaClubStorePlayerDataDummy(BaseDummy):
    """キャバクラシステムの店舗のプレイヤーデータ.
    """
    def create(self, uid, mid, ltime=None, etime=None, utime=None, event_id=0, scoutman_add=0, is_open=False, ua_flag=False, customer=0, proceeds=0):
        now = OSAUtil.get_now()
        ins_id = CabaClubStorePlayerData.makeID(uid, mid)
        ins = CabaClubStorePlayerData.makeInstance(ins_id)
        ins.ltime = ltime or (now + datetime.timedelta(days=1))
        ins.etime = etime or now
        ins.utime = utime or now
        ins.event_id = event_id
        ins.scoutman_add = scoutman_add
        ins.is_open = is_open
        ins.ua_flag = ua_flag
        ins.customer = customer
        ins.proceeds = proceeds
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = CabaClubStorePlayerData.getByKey(pkey)
        if m:
            m.delete()

class CabaClubCastPlayerDataDummy(BaseDummy):
    """キャバクラシステムの店舗のキャスト配置情報.
    """
    def create(self, uid, mid, cardlist):
        ins_id = CabaClubCastPlayerData.makeID(uid, mid)
        ins = CabaClubCastPlayerData.makeInstance(ins_id)
        ins.cast = [card.id for card in cardlist]
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = CabaClubCastPlayerData.getByKey(pkey)
        if m:
            m.delete()

class CabaClubItemPlayerDataDummy(BaseDummy):
    """キャバクラシステムのアイテム仕様状況.
    """
    def create(self, uid, preferential_id=0, preferential_time=None, barrier_id=0, barrier_time=None):
        now = OSAUtil.get_now()
        ins = CabaClubItemPlayerData.makeInstance(uid)
        ins.preferential_id = preferential_id
        ins.preferential_time = preferential_time or now
        ins.barrier_id = barrier_id
        ins.barrier_time = barrier_time or now
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = CabaClubItemPlayerData.getByKey(pkey)
        if m:
            m.delete()

class CabaClubScorePlayerDataDummy(BaseDummy):
    """キャバクラシステムのトータルスコア情報状況.
    """
    def create(self, uid, money=0, point=0):
        ins = CabaClubScorePlayerData.makeInstance(uid)
        ins.money = money
        ins.point = point
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = CabaClubScorePlayerData.getByKey(pkey)
        if m:
            m.delete()

class CabaClubScorePlayerDataWeeklyDummy(BaseDummy):
    """キャバクラシステムの週間スコア情報状況.
    """
    def create(self, uid, etime=None, proceeds=0, customer=0, flag_aggregate=False, view_result=False):
        now = OSAUtil.get_now()
        etime = etime or BackendApi.to_cabaretclub_section_starttime(now)
        ins_id = CabaClubScorePlayerDataWeekly.makeID(uid, etime)
        ins = CabaClubScorePlayerDataWeekly.makeInstance(ins_id)
        ins.proceeds = proceeds
        ins.customer = customer
        ins.flag_aggregate = flag_aggregate
        ins.view_result = view_result
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = CabaClubScorePlayerDataWeekly.getByKey(pkey)
        if m:
            m.delete()

class TitleMasterDummy(BaseDummy):
    """称号マスター.
    """
    def create(self, days=1, cost=0, gold_up=0, exp_up=0, raidevent_point_up=0, raidevent_power_up=0, raidevent_treasure_up=0, scoutevent_point_up=0, battleevent_point_up=0, battleevent_power_up=0):
        ins_id = _getDummyID(TitleMaster)
        ins = TitleMaster.makeInstance(ins_id)
        ins.days = days
        ins.cost = cost
        ins.gold_up = gold_up
        ins.exp_up = exp_up
        ins.raidevent_point_up = raidevent_point_up
        ins.raidevent_power_up = raidevent_power_up
        ins.raidevent_treasure_up = raidevent_treasure_up
        ins.scoutevent_point_up = scoutevent_point_up
        ins.battleevent_point_up = battleevent_point_up
        ins.battleevent_power_up = battleevent_power_up
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = TitleMaster.getByKey(pkey)
        if m:
            m.delete()

class TitlePlayerDataDummy(BaseDummy):
    """称号のプレイヤー情報.
    """
    def create(self, uid, title=0, stime=None):
        ins = TitlePlayerData.makeInstance(uid)
        ins.title = title
        ins.stime = stime or OSAUtil.get_now()
        ins.save()
        self.set_id(ins.id)
        return ins
    
    @classmethod
    def remove(cls, pkey):
        m = TitlePlayerData.getByKey(pkey)
        if m:
            m.delete()
