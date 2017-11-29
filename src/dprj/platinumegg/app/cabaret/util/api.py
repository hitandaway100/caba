# -*- coding: utf-8 -*-
import settings, hashlib

from platinumegg.app.cabaret.util.player import ModelPlayer
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

from platinumegg.app.cabaret.models.Player import Player, PlayerRegist,\
    PlayerTutorial, PlayerExp, PlayerGold, PlayerAp, PlayerDeck, PlayerFriend,\
    PlayerGachaPt, PlayerTreasure, PlayerScout, PlayerCard, PlayerLogin,\
    PlayerComment, RareCardLog, PlayerHappening, PlayerKey, PlayerRequest,\
    PlayerLimitation, PlayerLoginTimeLimited, PlayerConsumePoint, PlayerTradeShop, \
    PlayerCrossPromotion, PlayerPlatinumPiece, PlayerCrystalPiece
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.lib.platform.dmmsp.api import ApiRequestMaker as ApiRequestMakerSp
from platinumegg.lib.platform.dmmpc.api import ApiRequestMaker as ApiRequestMakerPc
import time
import operator
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.models.Card import Deck, Card, CardMaster,\
    CardSortMaster, CardDeleted, DefaultCardMaster, CardAcquisition,\
    AlbumAcquisition, CompositionData, EvolutionData, DeckBase, RaidDeck,\
    CardStock
from platinumegg.app.cabaret.util.card import ModelCardMaster, CardSet, CardUtil,\
    CardListFilter
from platinumegg.app.cabaret.models.Friend import Friend, FriendRecordNum
import datetime
from platinumegg.app.cabaret.models.Present import Present, PrizeMaster,\
    PresentReceived
from platinumegg.app.cabaret.util.present import PresentSet, PrizeData
from platinumegg.lib.platform.api.objects import PeopleRequestData,\
    IgnorelistRequestData, InspectionGetRequestData, People, PaymentData,\
    PaymentGetRequestData
from platinumegg.lib.platform.api.request import ApiNames
from platinumegg.app.cabaret.models.PlayerLog import PlayerLog
from platinumegg.app.cabaret.util.playerlog import getGameLog,\
    BossWinLog, ScoutClearLog, EventStageClearLog, EventBossWinLog,\
    RaidEventBossWinLog, RaidEventStageClearLog
from platinumegg.app.cabaret.models.Greet import GreetLog, GreetData,\
    GreetPlayerData
from platinumegg.app.cabaret.util.greetlog import GreetLogData
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Battle import BattleWin, BattleLose, BattleReceiveWin, BattleReceiveLose,\
    BattlePlayer, BattleResult, BattleRankMaster
from platinumegg.app.cabaret.models.Skill import SkillMaster
from platinumegg.app.cabaret.util.apprandom import AppRandom
from platinumegg.app.cabaret.models.Scout import ScoutPlayData, ScoutMaster
from platinumegg.app.cabaret.models.Area import AreaMaster, AreaPlayData
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.lib import timezone
from platinumegg.app.cabaret.util.scout import ScoutExec, ScoutDropItemSelector,\
    ScoutEventNone, ScoutEventExec
from platinumegg.app.cabaret.models.Item import ItemMaster, Item
from platinumegg.app.cabaret.models.Boss import BossMaster, BossBattle
from platinumegg.app.cabaret.models.Happening import HappeningMaster,\
    Happening, RaidMaster, Raid, RaidHelp, RaidBattle, RaidLog, RaidDestroyCount,\
    RaidPrizeDistributeQueue
from platinumegg.app.cabaret.models.Gacha import GachaMaster, GachaBoxMaster,\
    GachaGroupMaster, GachaStepupMaster, GachaPlayData, GachaPlayCount,\
    GachaSlideCastMaster, GachaSeatMaster, GachaSeatPlayData,\
    GachaSeatTableMaster, GachaSeatTablePlayCount, GachaTicket,\
    GachaHeaderMaster, GachaConsumePoint, RankingGachaMaster, RankingGachaScore,\
    RankingGachaWholePrizeData, RankingGachaWholePrizeQueue,\
    RankingGachaWholeData, RankingGachaPlayLog, GachaBoxGachaDetailMaster, GachaBoxResetPlayerData
from platinumegg.app.cabaret.util.gacha import GachaBox, GachaBoxGroup, GachaMasterSet,\
    GachaBoxCardData
from platinumegg.app.cabaret.models.Shop import ShopItemMaster, ShopItemBuyData
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusMaster,\
    AccessBonusMaster, LoginBonusTimeLimitedMaster,\
    LoginBonusTimeLimitedDaysMaster, LoginBonusTimeLimitedConfig,\
    TotalLoginBonusConfig, LoginBonusTimeLimitedData, LoginBonusSugorokuMaster,\
    LoginBonusSugorokuMapMaster, LoginBonusSugorokuMapSquaresMaster,\
    LoginBonusSugorokuPlayerData
from platinumegg.app.cabaret.util.redisdb import DMMPlayerAssociate,\
    LevelGroupSet, LevelSet, RedisModel, LoginTimeSet, BattleLevelSet,\
    FriendListSet, FriendAcceptNum, FreeGachaLastTime,\
    RareLogList, PresentIdListSet, delete_by_user as delete_by_user_from_redisdb,\
    GreetLogListSet,\
    RaidCallFriendTime, RaidLogListSet,LastViewArea,\
    RaidHelpSet, RaidHelpFriendData,\
    TreasureListSet, delete_card_by_uid, CardKindListSet,\
    PlayerLogListSet, EvolutionAlbumHkLevelListSet, UserCardIdListSet,\
    RaidEventRanking, delete_raidevent, SubProcessPid, ScoutEventRanking,\
    delete_scoutevent, RaidLogNotificationSet, BattleEventRanking,\
    BattleEventDailyRanking, ScoutSkipFlag, ScoutSearchFlag, PlayerLastHappeningType,\
    RankingGachaSingleRanking, RankingGachaTotalRanking, FriendLogList,\
    FriendLogReserveList, RaidEventRankingBeginer, delete_battleevent,\
    ScoutEventRankingBeginer, BattleEventRankingBeginer, PlayerConfigData,\
    LoginBonusFixationDataHash, PopupViewTime, PopupResetTime,\
    CabaClubRecentlyViewedTime, CabaClubRanking, ProduceEventRanking
from platinumegg.app.cabaret.util.redisbattleevent import BattleEventOppList,\
    BattleEventBattleLogListSet, BattleEventRevengeSet,BattleEventRankUidSet,\
    delete_by_user as delete_by_user_redisbattleevent,\
    BattleEventOppRivalListCost
from platinumegg.app.cabaret.util.rediscache import InfomationMasterIdListCache,\
    TopBannerMasterIdListCache, EventBannerMasterIdListCache,\
    PlayerLevelExpMasterListCache, CardLevelExpMsterListCache,\
    AreaScoutListCache, AlbumList, AlbumMemoriesSet, GachaBoxCardListInfoSet,\
    AlbumHkLevelSet, EventAreaStageListCache, MoviePlayListUniqueNameSetSp,\
    MoviePlayListUniqueNameSetPc, ScoutEventPresentPrizeNumberList,\
    PopupMasterIdListCache, RankingGachaWholePrizeQueueIdSet,\
    LoginbonusSugorokuMapSquaresIdList
from platinumegg.app.cabaret.models.Memories import MemoriesMaster, Memories,\
    MoviePlayList, VoicePlayList, MovieViewData, PcMoviePlayList, PcMovieViewData,\
    EventMovieMaster, EventMovieViewData
from platinumegg.app.cabaret.models.Infomation import InfomationMaster,\
    EventBannerMaster, PopupMaster
from platinumegg.app.cabaret.models.Tutorial import TutorialConfig
from platinumegg.app.cabaret.models.LevelUpBonus import LevelUpBonusMaster, LevelUpBonusPlayerData
from copy import copy
from platinumegg.app.cabaret.models.PaymentEntry import ShopPaymentEntry,\
    GachaPaymentEntry
from platinumegg.app.cabaret.util.happening import HappeningRaidSet, RaidBoss,\
    HappeningSet, HappeningUtil
from platinumegg.app.cabaret.models.Trade import TradeMaster, TradePlayerData,\
    TradeResetTime
from platinumegg.app.cabaret.models.TradeShop import TradeShopMaster, TradeShopItemMaster, TradeShopPlayerData
from random import randint
from platinumegg.lib.dbg import DbgLogger
from platinumegg.app.cabaret.util.treasure import TreasureUtil
from platinumegg.app.cabaret.util.media import Media
from platinumegg.app.cabaret.util.battle import BattleAnimParam, BattleUtil,\
    BossBattleAnimParam
import random
from platinumegg.app.cabaret.models.AppConfig import AppConfig, PreRegistConfig
from platinumegg.app.cabaret.util import db_util
import math
from platinumegg.app.cabaret.util.item import ItemUtil
from platinumegg.app.cabaret.models.UserLog import UserLogLoginBonus,\
    UserLogCardGet, UserLogComposition, UserLogEvolution, UserLogGacha,\
    UserLogAreaComplete, UserLogScoutComplete, UserLogPresentReceive,\
    UserLogItemGet, UserLogItemUse, UserLogTreasureGet, UserLogTreasureOpen,\
    UserLogTrade, UserLogCardSell, UserLogPresentSend, UserLogTicketGet,\
    UserLogLoginBonusTimeLimited, UserLogComeBack, UserLogCardStock,\
    UserLogBattleEventPresent, UserLogScoutEventGachaPt,\
    UserLogRankingGachaWholePrize, UserLogScoutEventTipGet, UserLogTradeShop, UserLogReprintTicketTradeShop,\
    UserLogLoginbonusSugoroku, UserLogCabaClubStore
from platinumegg.app.cabaret.kpi.operator import KpiOperator
from platinumegg.app.cabaret.models.PresentEveryone import PresentEveryoneRecord,\
    PresentEveryoneLoginBonusMaster, PresentEveryoneMypageMaster,\
    PresentEveryoneReceiveLoginBonus, PresentEveryoneReceiveMypage
import settings_sub
from platinumegg.app.cabaret.models.raidevent.RaidEvent import CurrentRaidEventConfig,\
    RaidEventMaster, RaidEventScore, RaidEventFlags, RaidEventRaidMaster,\
    RaidEventFlagsUnwilling, RaidEventChampagne, RaidEventSpecialBonusScore,\
    RaidEventSpecialBonusScoreLog, RaidEventHelpSpecialBonusScore
from platinumegg.app.cabaret.models.Invite import InviteMaster, Invite, InviteData
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventMaster,\
    ScoutEventStageMaster, ScoutEventPlayData, ScoutEventScore,\
    ScoutEventFlags, CurrentScoutEventConfig, ScoutEventPresentNum,\
    ScoutEventPresentPrizeMaster,\
    ScoutEventRaidMaster, ScoutEventTanzakuCastData, ScoutEventTanzakuCastMaster,\
    ScoutEventHappeningTableMaster, ScoutEventCastPerformanceResult
from platinumegg.lib.cache.localcache import localcache
from platinumegg.app.cabaret.models.battleevent.BattleEvent import CurrentBattleEventConfig,\
    BattleEventMaster, BattleEventRankMaster, BattleEventFlags, BattleEventScore,\
    BattleEventRank, BattleEventBattleLog, BattleEventRevenge, BattleEventGroup,\
    BattleEventGroupLog, BattleEventBattleTime, BattleEventGroupRankingPrize,\
    BattleEventScorePerRank, BattleEventPieceMaster, BattleEventPieceCollection,\
    BattleEventContinueVictory
from platinumegg.app.cabaret.util.battleevent import BattleEventGroupUserData
from platinumegg.app.cabaret.util.promotion import PromotionUtil
from platinumegg.app.cabaret.models.ComeBack import CurrentComeBackCampaignConfig,\
    ComeBackCampaignMaster, ComeBackCampaignData
from platinumegg.app.cabaret.models.SerialCampaign import SerialCampaignMaster,\
    SerialCode, SerialCount, ShareSerialLog
import cPickle
from platinumegg.app.cabaret.models.battleevent.BattleEventPresent import BattleEventPresentMaster,\
    BattleEventPresentContentMaster, BattleEventPresentData,\
    BattleEventPresentCounts
from platinumegg.app.cabaret.models.Mission import PanelMissionData,\
    PanelMissionPanelMaster, PanelMissionMissionMaster, PlayerPanelMission
from platinumegg.app.cabaret.util.mission import PanelMissionConditionExecuter
from platinumegg.app.cabaret.models.base.queryset import Query
from platinumegg.app.cabaret.models.Scenario import ScenarioMaster
from platinumegg.lib.pljson import Json
from platinumegg.app.cabaret.models.raidevent.RaidCardMixer import RaidEventRecipeMaster,\
    RaidEventMaterialMaster, RaidEventMixData, RaidEventMaterialData
from platinumegg.app.cabaret.util.popup import PopupBanner
from platinumegg.app.cabaret.models.raidevent.RaidEventScout import RaidEventScoutStageMaster,\
    RaidEventScoutPlayData
from platinumegg.app.cabaret.models.EventScout import EventScoutStageMaster
from platinumegg.app.cabaret.models.ReprintTicketTradeShop import ReprintTicketTradeShopMaster,\
    ReprintTicketTradeShopPlayerData
from collections import namedtuple
from platinumegg.app.cabaret.util.sugoroku import Sugoroku
from platinumegg.app.cabaret.models.CabaretClub import CabaClubScorePlayerData,\
    CabaClubStoreMaster, CabaClubEventMaster, CabaClubStorePlayerData,\
    CabaClubScorePlayerDataWeekly, CabaClubCastPlayerData,\
    CabaClubItemPlayerData, CabaClubMaster
from platinumegg.app.cabaret.models.CabaretClubEvent import CabaClubRankEventMaster, CurrentCabaClubRankEventConfig
from platinumegg.app.cabaret.models.CabaretClubEvent import CabaClubEventRankMaster
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import ProduceEventMaster, CurrentProduceEventConfig,\
    ProduceCastMaster, ProduceEventScore, ProduceEventScoutStageMaster, ProduceEventScoutPlayData, ProduceEventRaidMaster, \
    ProduceEventHappening, PlayerEducation, ProduceEventHappeningResult, ProduceEventFlags
from platinumegg.app.cabaret.models.Title import TitleMaster, TitlePlayerData
from platinumegg.app.cabaret.util.cabaclub_store import CabaclubStoreSet
from platinumegg.app.cabaret.util.title import TitleSet
from platinumegg.app.cabaret.models.GachaExplain import GachaExplainMaster
from platinumegg.app.cabaret.models.View import CardMasterView

class Objects:
    """クラスインスタンスを決められたフォーマットの辞書型に置き換えたい.
    """
    @staticmethod
    def person(handler, player, person=None):
        if person is None:
            if player is None:
                person = People.makeNotFound('')
            else:
                person = People.makeNotFound(player.dmmid)
        return {
            'id' : person.id,
            'nickname' : person.nickname,
        }
    
    @staticmethod
    def player(handler, player, person=None, leader=None):
        """プレイヤー情報.
        """
        model_mgr = handler.getModelMgr()
        data = {}
        for att, model_cls in ModelPlayer._columns.items():
            if model_cls in (PlayerHappening,):
                continue
            model = player.getModel(model_cls)
            if model:
                data[att] = getattr(model, att)
        
        data['person'] = Objects.person(handler, player, person)
        
        if data.has_key('ptype'):
            data['ptype_str'] = Defines.CharacterType.NAMES[data['ptype']]
        
        if player.getModel(PlayerAp) and player.getModel(PlayerFriend):
            now = OSAUtil.get_now()
            
            data['ap'] = player.get_ap()
            data['apmax'] = player.get_ap_max()
            data['aprtime'] = player.aprtime
            data['bp'] = player.get_bp()
            data['bpmax'] = player.get_bp_max()
            data['bprtime'] = player.bprtime
            
            ap_sec = player.get_ap_timediff(now)
            bp_sec = player.get_bp_timediff(now)
            
            aprtime = now + datetime.timedelta(seconds=ap_sec)
            bprtime = now + datetime.timedelta(seconds=bp_sec)
            def makeStrRtime(sec):
                minutes = int(sec / 60)
                hours = int(minutes / 60)
                if 0 < hours:
                    return u'%d時間%02d分' % (hours, minutes % 60)
                else:
                    return u'%d分%02d秒' % (minutes, sec % 60)
            
            data['str_aprtime_diff'] = makeStrRtime(ap_sec)
            data['str_bprtime_diff'] = makeStrRtime(bp_sec)
            data['str_aprtime'] = aprtime.strftime("%H:%M")
            data['str_bprtime'] = bprtime.strftime("%H:%M")
        
        if player.getModel(PlayerDeck):
            data['deckcapacity'] = player.deckcapacity
            data['cardlimit'] = player.cardlimit
            levelexp = BackendApi.get_playerlevelexp_bylevel(1, model_mgr, using=settings.DB_READONLY)
            data['cardlimitlv'] = levelexp.cardlimit
        if player.getModel(PlayerExp):
            levelexp_prev = BackendApi.get_playerlevelexp_bylevel(player.level, model_mgr, using=settings.DB_READONLY)
            levelexp_next = BackendApi.get_playerlevelexp_bylevel(player.level+1, model_mgr, using=settings.DB_READONLY) or levelexp_prev
            if levelexp_prev:
                data['exp_prev'] = levelexp_prev.exp
            if levelexp_next:
                data['exp_next'] = levelexp_next.exp
        if player.getModel(PlayerTreasure):
            data['cabaretking'] = player.get_cabaretking_num()
        
        data['url'] = handler.makeAppLinkUrl(UrlMaker.profile(player.id))
        data['url_friendrequest_send'] = handler.makeAppLinkUrl(UrlMaker.friendrequest_yesno(player.id))
        data['url_friendrequest_cancel'] = handler.makeAppLinkUrl(UrlMaker.friendcancel_yesno(player.id))
        data['url_friendrequest_accept'] = handler.makeAppLinkUrl(UrlMaker.friendreceive_yesno(player.id, True))
        data['url_friendrequest_veto'] = handler.makeAppLinkUrl(UrlMaker.friendreceive_yesno(player.id, False))
        data['url_friendremove'] = handler.makeAppLinkUrl(UrlMaker.friendremove_yesno(player.id))
        data['url_greet'] = handler.makeAppLinkUrl(UrlMaker.greet(player.id))
        data['url_greetlog'] = handler.makeAppLinkUrl(UrlMaker.greetlog(player.id))
        
        if leader:
            data['leader'] = Objects.card(handler, leader)
        
        return data
    
    @staticmethod
    def battlerank(handler, rankmaster):
        """バトルのランク情報.
        """
        return {
            'id' : rankmaster.id,
            'region' : rankmaster.region,
            'town' : rankmaster.town,
            'text' : rankmaster.text,
            'bpcost' : rankmaster.bpcost,
            'thumbUrl' : handler.makeAppLinkUrlImg(rankmaster.thumb),
            'win' : rankmaster.win,
            'times' : rankmaster.times,
        }
    
    @staticmethod
    def battleplayer(handler, battleplayer, rankmaster):
        """バトルのプレイヤー情報.
        """
        rest = BackendApi.get_battle_opponent_change_restcnt(handler.getModelMgr(), battleplayer, rankmaster, using=settings.DB_READONLY)
        return {
            'rank' : Objects.battlerank(handler, rankmaster),
            'win' : battleplayer.win_continuity,
            'times' : battleplayer.times,
            'change_cnt' : battleplayer.change_cnt,
            'rest_cnt' : rest,
        }
    
    @staticmethod
    def cardmaster(handler, master):
        """カードマスターデータ.
        """
        skillmaster = master.getSkill()
        skill = None
        if skillmaster:
            skill = Objects.skillmaster(skillmaster)
        
        dmmurllist = master.dmmurl
        if dmmurllist and not isinstance(dmmurllist, list):
            dmmurllist = [{
                'url' : master.dmmurl,
            }]
        
        return {
            'id' : master.id,
            'name' : master.name,
            'text' : master.text,
            'kind' : master.ckind,
            'hklevel' : master.hklevel,
            'rare' : master.rare,
            'rare_str' : Defines.Rarity.NAMES[master.rare],
            'rare_color' : Defines.Rarity.COLORS.get(master.rare, '#ffffff'),
            'maxlevel' : master.maxlevel,
            'maxpower' : master.maxpower,
            'thumbUrl' : handler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(master)),
            'thumbnail' : {
                'small' : handler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlSmall(master)),
                'middle' : handler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(master)),
                'large' : handler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlLarge(master)),
                'bustup' : handler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlBustup(master)),
            },
            'cost' : master.cost,
            'type' : master.ctype,
            'type_str' : Defines.CharacterType.NAMES[master.ctype],
            'album' : master.album,
            'skill' : skill,
            'iconUrl' : handler.makeAppLinkUrlImg(Defines.CharacterType.ICONS[master.ctype]),
            'unit':Defines.CardKind.UNIT[master.ckind],
            'url_album' : handler.makeAppLinkUrl(UrlMaker.albumdetail(master.album)),
            'url_dmm' : dmmurllist,
        }
    @staticmethod
    def card(handler, cardset, deck=None, is_new=False):
        """カード情報.
        """
        model_mgr = handler.getModelMgr()
        
        card = cardset.card
        master = cardset.master
        
        deckmember = False
        if deck:
            if isinstance(deck, DeckBase):
                deckmember = deck.is_member(card.id)
            elif isinstance(deck, (list, tuple)):
                deckmember = card.id in deck
        
        data = {
            'master' : Objects.cardmaster(handler, master),
            'level' : min(master.maxlevel, card.level),
            'exp' : card.exp,
            'power' : cardset.power,
            'takeover' : card.takeover,
            'protection' : card.protection,
            'skilllevel' : card.skilllevel,
            'sellprice' : cardset.sellprice,
            'sellprice_treasure' : cardset.sellprice_treasure,
            'deckmember' : deckmember,
            'is_new' : is_new,
            'is_can_composition' : cardset.is_can_composition,
            'is_can_evolution' : cardset.is_can_evolution,
        }
        if card.id:
            data.update({
                'id' : card.id,
                'url_detail' : handler.makeAppLinkUrl(UrlMaker.carddetail(card.id)),
                'url_composition' : handler.makeAppLinkUrl(UrlMaker.compositionmaterial(card.id)),
                'url_evolution' : handler.makeAppLinkUrl(UrlMaker.evolutionmaterial(card.id)),
                'url_deck' : handler.makeAppLinkUrl(OSAUtil.addQuery(UrlMaker.deck(), Defines.URLQUERY_CARD, card.id)),
                'url_sell' : handler.makeAppLinkUrl(OSAUtil.addQuery(UrlMaker.sellyesno(), Defines.URLQUERY_CARD, card.id)),
                'url_transfer' : handler.makeAppLinkUrl(OSAUtil.addQuery(UrlMaker.transferyesno(), Defines.URLQUERY_CARD, card.id)),
             })
        levelexp_prev = BackendApi.get_cardlevelexp_bylevel(min(card.level, master.maxlevel), model_mgr, using=settings.DB_READONLY)
        levelexp_next = BackendApi.get_cardlevelexp_bylevel(min(card.level+1, master.maxlevel), model_mgr, using=settings.DB_READONLY) or levelexp_prev
        if levelexp_prev:
            data['exp_prev'] = levelexp_prev.exp
        if levelexp_next:
            data['exp_next'] = levelexp_next.exp
        
        return data
    
    @staticmethod
    def listalbum(handler, master, is_open, stocknum=0):
        """アルバム一覧.
        """
        if master is None:
            is_open = False
            thumb = ''
            url = ''
        else:
            thumb = handler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(master))
            url = handler.makeAppLinkUrl(UrlMaker.albumdetail(master.album))
        
        return {
            'thumbUrl' : thumb,
            'url' : url,
            'is_open' : is_open,
            'stocknum' : stocknum,
        }
    
    @staticmethod
    def memoriesmaster(handler, memoriesmaster, card_acquisition=None, vtime=None):
        """思い出アルバムのマスターデータ.
        """
        if BackendApi.check_album_memories_opened(memoriesmaster, card_acquisition):
            acquisition = True
            is_new = vtime is None or OSAUtil.get_now() < vtime
            url_memories = handler.makeAppLinkUrl(UrlMaker.albummemories(memoriesmaster.id))
        else:
            acquisition = False
            is_new = False
            url_memories = None
        
        thumbUrl = None
        dataUrls = []
        flvUrl = ''
        if memoriesmaster.contenttype == Defines.MemoryContentType.IMAGE:
            thumbUrl = handler.makeAppLinkUrlImg(memoriesmaster.thumb)
            dataUrls.append(handler.makeAppLinkUrlImg(memoriesmaster.contentdata))
        elif memoriesmaster.contenttype == Defines.MemoryContentType.MOVIE:
            moviemaster = BackendApi.get_movieplaylist_master(handler.getModelMgr(), int(memoriesmaster.contentdata), using=settings.DB_READONLY)
            if moviemaster:
                thumbUrl = handler.makeAppLinkUrlMedia(Media.movie_thumbnail(moviemaster.filename))
                dataUrls.append(handler.makeAppLinkUrlMedia(Media.movie_m3u8(moviemaster.filename)))
                flvUrl = handler.makeAppLinkUrlMedia(Media.movie_flv(moviemaster.filename))
        elif memoriesmaster.contenttype == Defines.MemoryContentType.MOVIE_PC:
            moviemaster = BackendApi.get_pcmovieplaylist_master(handler.getModelMgr(), int(memoriesmaster.contentdata), using=settings.DB_READONLY)
            if moviemaster:
                thumbUrl = handler.makeAppLinkUrlMedia(Media.movie_pc_thumbnail(moviemaster.filename))
                dataUrls.append(handler.makeAppLinkUrlMedia(Media.movie_m3u8(moviemaster.filename)))
                flvUrl = handler.makeAppLinkUrl(UrlMaker.movie_keyget(int(memoriesmaster.contentdata)))
        elif memoriesmaster.contenttype == Defines.MemoryContentType.VOICE:
            thumbUrl = handler.makeAppLinkUrlImg(memoriesmaster.thumb)
            voicemaster = BackendApi.get_voiceplaylist_master(handler.getModelMgr(), int(memoriesmaster.contentdata), using=settings.DB_READONLY)
            if voicemaster:
                dataUrls.append(handler.makeAppLinkUrlMedia(Media.voice_aac(voicemaster.filename)))
                dataUrls.append(handler.makeAppLinkUrlMedia(Media.voice_ogg(voicemaster.filename)))
        
        return {
            'id' : memoriesmaster.id,
            'name' : memoriesmaster.name,
            'text' : memoriesmaster.text,
            'thumbUrl' : thumbUrl,
            'dataUrl' : dataUrls,
            'flvUrl' : flvUrl,
            'contenttype' : memoriesmaster.contenttype,
            'contentdata' : memoriesmaster.contentdata,
            'acquisition' : acquisition,
            'is_new' : is_new,
            'url_memories' : url_memories,
            'is_new' : is_new,
            'cardid' : memoriesmaster.cardid,
        }
    
    @staticmethod
    def itemmaster(handler, itemmaster):
        data = {}
        data['id'] = itemmaster.id
        data['name'] = itemmaster.name
        data['text'] = itemmaster.text
        data['url_useyesno'] = handler.makeAppLinkUrl(UrlMaker.item_useyesno(itemmaster.id))
        data['thumbUrl'] = handler.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmall(itemmaster))
        data['thumbnail'] = {
            'small' : data['thumbUrl'],
            'middle' : handler.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlMiddle(itemmaster)),
        }
        data['unit'] = itemmaster.unit
        data['useable'] = itemmaster.id in Defines.ItemEffect.USE_ABLE
        data['url_buy'] = handler.makeAppLinkUrl(UrlMaker.shop())
        return data
    
    @staticmethod
    def item(handler, itemmaster, num, use_nummax=None):
        data = {
            'master' : Objects.itemmaster(handler, itemmaster)
        }
        data['num'] = num
        if use_nummax is None:
            use_nummax = Defines.ItemEffect.USE_NUM_MAX.get(itemmaster.id, num)
        if 0 < use_nummax:
            data['usenums'] = ItemUtil.makeUseNumList(use_nummax)
        return data
    
    @staticmethod
    def infomation(apphandler, infomation):
        """運営からのお知らせ.
        """
        return {
            'id' : infomation.id,
            'title' : infomation.title,
            'body' : infomation.body,
            'jumpto': infomation.jumpto,
            'imageurl': infomation.imageurl,
            'date' : infomation.stime.strftime("%Y/%m/%d"),
            'url_detail' : apphandler.makeAppLinkUrl(UrlMaker.infomation_detail(infomation.id)),    # 詳細へのURL.
            'is_new' : False,
        }
    
    @staticmethod
    def topbanner(apphandler, topbanner):
        """Topバナー.
        """
        jumpto = topbanner.jumpto
        is_external_link = False
        if jumpto:
            if jumpto.find('http') != 0:
                jumpto = apphandler.makeAppLinkUrl(jumpto)
            elif 0 <= jumpto.find(settings_sub.WEB_GLOBAL_HOST):
                # Webサーバへのリンク.
                pass
            elif jumpto.find(settings_sub.STATIC_URL_ROOT) == 0:
                # 静的コンテンツサーバへのリンク.
                pass
            else:
                # 外部コンテンツへのリンク.
                if jumpto.find(',') != -1:
                    jumpto_list = jumpto.split(',')
                    if apphandler.is_pc:
                        jumpto = jumpto_list[0]
                    else:
                        jumpto = jumpto_list[1]
                is_external_link = True
        imageurl = topbanner.imageurl
        if imageurl.find('http') != 0:
            imageurl = apphandler.makeAppLinkUrlImg(imageurl)
        return {
            'id' : topbanner.id,
            'name' : topbanner.name,
            'jumpto' : jumpto,
            'imageurl' : imageurl,
            'is_external_link' : is_external_link,
            'external_comment' : topbanner.comment_external,
        }
    
    @staticmethod
    def eventbanner(apphandler, eventbanner):
        """イベントバナー.
        """
        data = Objects.topbanner(apphandler, eventbanner)
        data['comment'] = eventbanner.comment
        if eventbanner.has_teaser:
            data['teaser'] = {
                'header' : apphandler.makeAppLinkUrlImg(eventbanner.teaserheader) if eventbanner.teaserheader else None,
                'body' : apphandler.makeAppLinkUrlImg(eventbanner.teaserbody) if eventbanner.teaserbody else None,
                'bodytitle' : eventbanner.teaserbodytitle,
                'bodybottom' : eventbanner.teaserbodybottom,
                'scheduletext' : eventbanner.teaserscheduletext,
            }
            data['jumpto'] = apphandler.makeAppLinkUrl(UrlMaker.teaser(eventbanner.id))
            data['is_external_link'] = False
        return data
    
    @staticmethod
    def popup(apphandler, popupbanner):
        """ポップアップ.
        """
        banner = popupbanner.banner
        obj_banner = Objects.eventbanner(apphandler, banner) if banner else None
        
        return {
            'id' : popupbanner.id,
            'title' : popupbanner.title,
            'image' : apphandler.makeAppLinkUrlImg(popupbanner.imageurl),
            'banner' : obj_banner,
            'url_flag' : apphandler.makeAppLinkUrl(UrlMaker.popupview(popupbanner.id)),
        }
    
    @staticmethod
    def gamelog(gamelog):
        """行動履歴.
        """
        return {
            'id' : gamelog.id,
            'logtype' : gamelog.logtype,
            'params' : gamelog.params,
            'ctime' : gamelog.ctime.strftime(u"%m月%d日　%H:%M"),
        }
    
    @staticmethod
    def greetlog(greetlog):
        """あいさつ履歴.
        """
        return {
            'params' : greetlog.params,
            'ctime' : greetlog.gtime.strftime(u"%m月%d日　%H:%M"),
        }
    
    @staticmethod
    def rarelog(handler, card, gtime):
        """レア獲得履歴.
        """
        return {
            'card' : Objects.cardmaster(handler, card),
            'gtime' : gtime.strftime(u"%m月%d日　%H:%M"),
        }
    
    @staticmethod
    def scout(handler, player, scoutmaster, progress, dropitems, scoutkey=None):
        """スカウト
        """
        model_mgr = handler.getModelMgr()
        if scoutkey is None:
            scoutkey = BackendApi.get_scoutkey(model_mgr, player.id, scoutmaster.id, using=settings.DB_READONLY)
        return {
            'id' : scoutmaster.id,
            'name' : scoutmaster.name,
            'text' : scoutmaster.text,
            'thumbUrl' : handler.makeAppLinkUrlImg(scoutmaster.thumb),
            'progress' : progress,
            'execution' : scoutmaster.execution,
            'percent' : min(100, int(progress * 100 / scoutmaster.execution)),
            'cleared' : scoutmaster.execution <= progress,
            'url_exec' : handler.makeAppLinkUrl(UrlMaker.scoutdo(scoutmaster.id, scoutkey)),
            'dropitems' : dropitems,
            'exp' : scoutmaster.exp,
            'goldmin' : scoutmaster.goldmin,
            'goldmax' : scoutmaster.goldmax,
            'apcost' : BackendApi.get_apcost(scoutmaster, player),
        }
    
    @staticmethod
    def scoutdropitem(handler, master, flag):
        """スカウトでドロップするアイテム.
        """
        if isinstance(master, (ModelCardMaster, CardMaster)):
            thumb = CardUtil.makeThumbnailUrlIcon(master)
        else:
            thumb = master.thumb
        
        return {
            'thumbUrl' : handler.makeAppLinkUrlImg(thumb),
            'drop' : flag,
        }
    
    @staticmethod
    def raidmaster(handler, raidmaster, is_produceevent=False):
        """レイドボスのマスターデータ.
        """
        return {
            'id' : raidmaster.id,
            'name' : raidmaster.name,
            'thumbUrl' : handler.makeAppLinkUrlImg(HappeningUtil.makeThumbnailUrl(raidmaster, is_produceevent)),
            'iconUrl' : handler.makeAppLinkUrlImg(HappeningUtil.makeThumbnailUrlIcon(raidmaster)),
            'commentappear' : raidmaster.commentappear,
            'commentwin' : raidmaster.commentwin,
            'commentwin_full' : raidmaster.commentwin_full,
            'commentlose' : raidmaster.commentlose,
            'ctype' : raidmaster.ctype,
            'str_ctype' : Defines.CharacterType.BOSS_NAMES.get(raidmaster.ctype),
        }
    
    @staticmethod
    def raid(handler, raidboss, o_person=None, o_leader=None, eventmaster=None, destroytime=None, is_produceevent=False):
        """レイド.
        """
        v_player = handler.getViewerPlayer(True)
        uid = None
        if v_player:
            uid = v_player.id
        
        raid = raidboss.raid
        master = raidboss.master
        
        str_ctime = raid.ctime.strftime(u'%Y/%m/%d %H:%M')
        
        o_person = o_person or People.makeNotFound()
        listthunbnail = HappeningUtil.makeThumbnailUrlIcon(master)
        if o_leader:
            listthunbnail = CardUtil.makeThumbnailUrlIcon(o_leader.master)
        
        combobonus = None
        feverdata = None
        fastbonusdata = None
        damagerecord = raidboss.getDamageRecord(uid)
        if eventmaster and not isinstance(eventmaster, ProduceEventMaster):
            # コンボボーナス.
            now = OSAUtil.get_now()
            combobonus_rate = BackendApi.get_raidevent_combobonus_powuprate(handler.getModelMgr(), eventmaster, raidboss, using=settings.DB_READONLY, now=now)
            combo_cnt = raidboss.getCurrentComboCount(now=now)
            combobonus_rate_next = BackendApi.choice_raidevent_combobonus_powuprate(eventmaster, combo_cnt+1)
            is_last_user = False
            
            lastrecord = raidboss.getLastDamageRecord()
            if lastrecord and uid == lastrecord.uid:
                is_last_user = True
            
            combobonus = {
                'cnt' : combo_cnt,
                'powup' : combobonus_rate,
                'powup_next' : combobonus_rate_next,
                'timelimit' : Objects.timelimit(raidboss.combo_etime, now=now),
                'is_last_user' : is_last_user,
            }
            
            if uid:
                # フィーバーチャンス.
                if damagerecord.is_fever(now=now):
                    feverdata = {
                        'powup' : eventmaster.feverchancepowup,
                        'timelimit' : Objects.timelimit(damagerecord.feverendtime, now=now)
                    }
            
            # 秘宝ボーナス.
            fastbonusdata = BackendApi.get_raidevent_fastbonusdata(eventmaster, raidboss, destroytime=destroytime)
        
        maxhp = raidboss.get_maxhp()
        
        return {
            'id' : master.id,
            'name' : master.name,
            'thumbUrl' : handler.makeAppLinkUrlImg(HappeningUtil.makeThumbnailUrl(master, is_produceevent=is_produceevent)),
            'iconUrl' : handler.makeAppLinkUrlImg(HappeningUtil.makeThumbnailUrlIcon(master)),
            'listThumbUrl' : handler.makeAppLinkUrlImg(listthunbnail),
            'commentappear' : master.commentappear,
            'commentwin' : master.commentwin,
            'commentwin_full' : master.commentwin_full,
            'commentlose' : master.commentlose,
            'oid' : raid.oid,
            'o_nickname' : o_person.nickname,
            'level' : raid.level,
            'hp' : raid.hp,
            'hpmax' : maxhp,
            'bpcost' : master.bpcost,
            'bpcost_strong' : master.bpcost_strong,
            'bpcost_first' : master.bpcost_first if raid.oid == uid else master.bpcost_first_other,
            'defense' : raidboss.get_defense(),
            'url_helpdetail' : handler.makeAppLinkUrl(UrlMaker.raidhelpdetail(raid.id)),
            'cabaretking' : raidboss.get_cabaretking(),
            'demiworld' : raidboss.get_demiworld(),
            'ctime' : str_ctime,
            'help' : raid.helpflag,
            'is_mine' : uid == raid.oid,
            'member_num' : raidboss.get_member_num(),
            'combobonus' : combobonus,
            'fever' : feverdata,
            'fastbonus' : fastbonusdata,
            'ctype' : master.ctype,
            'str_ctype' : Defines.CharacterType.BOSS_NAMES.get(master.ctype),
            'damage_cnt' : damagerecord.damage_cnt if damagerecord else 0,
        }
    
    @staticmethod
    def raidlog(handler, raidlog, raidboss, playerdict, people, leaders):
        """レイド履歴.
        """
        is_win = raidboss.raid.hp == 0
        
        o_player = playerdict[raidboss.raid.oid]
        o_person = people.get(o_player.dmmid, People.makeNotFound(o_player.dmmid))
        
        is_me = handler.osa_util.viewer_id == o_player.dmmid
        
        data = {
            'raid' : Objects.raid(handler, raidboss, o_person),
            'is_win' : is_win,
            'owner' : Objects.player(handler, o_player, o_person, leaders[raidboss.raid.oid]),
            'url_detail' : handler.makeAppLinkUrl(UrlMaker.raidlogdetail(raidlog.id)),
            'log_ctime' : raidlog.ctime,
            'is_me' : is_me,
        }
        if is_win:
            lastrecord = raidboss.getLastDamageRecord()
            destroyer = playerdict[lastrecord.uid]
            destroyer_person = people.get(destroyer.dmmid, People.makeNotFound(destroyer.dmmid))
            data.update(
                destroyer=Objects.player(handler, destroyer, destroyer_person)
            )
        return data
    
    @staticmethod
    def raidprize(handler, player, raidboss, dropitems):
        """レイド報酬.
        """
        prizelist = []
        if player.id == raidboss.raid.oid:
            prizeidlist = raidboss.master.prizes
            prizeidlist.extend([item.id for item in dropitems])
            prizelist.append(PrizeData.create(cabaretking=raidboss.get_cabaretking()))
        else:
            prizeidlist = raidboss.master.helpprizes
            prizelist.append(PrizeData.create(demiworld=raidboss.get_demiworld()))
        model_mgr = handler.getModelMgr()
        prizelist.extend(BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY))
        return BackendApi.make_prizeinfo(handler, prizelist, using=settings.DB_READONLY)
    
    @staticmethod
    def raid_damage_record(handler, player, person, leader, damage, attack_cnt, border_damage):
        """レイドのダメージ履歴.
        """
        return {
            'id' : player.id,
            'nickname' : person.nickname,
            'level' : player.level,
            'thumbUrl' : handler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(leader.master)),
            'damage' : damage,
            'attack_cnt' : attack_cnt,
            'rest' : max(0, border_damage - damage),
            'url_profile' : handler.makeAppLinkUrl(UrlMaker.profile(player.id)),
            'is_me':player.dmmid == handler.osa_util.viewer_id,
        }
    
    @staticmethod
    def happening(handler, happeningraidset, prize=None, o_person=None):
        """ハプニング.
        """
        now = OSAUtil.get_now()
        
        happeningset = happeningraidset.happening
        raidboss = happeningraidset.raidboss
        
        happening = happeningset.happening
        master = happeningset.master
        
        raid = None
        raidevent_id = 0
        if raidboss:
            eventmaster = None
            raidevent_id = HappeningUtil.get_raideventid(happeningset.happening.event)
            if raidevent_id:
                eventmaster = BackendApi.get_raideventmaster(handler.getModelMgr(), raidevent_id, using=settings.DB_READONLY)
            raid = Objects.raid(handler, raidboss, o_person=o_person, eventmaster=eventmaster)
        
        return {
            'id' : happening.id,
            'oid' : happening.oid,
            'name' : master.name,
            'text' : master.text,
            'thumbUrl' : handler.makeAppLinkUrlImg(master.thumb),
            'progress' : happening.progress,
            'execution' : master.execution,
            'percent' : int(happening.progress * 100 / master.execution) if 0 < master.execution else 100,
            'cleared' : master.execution <= happening.progress,
            'prize' : prize or {},
            'exp' : master.exp,
            'goldmin' : master.goldmin,
            'goldmax' : master.goldmax,
            'timelimit' : Objects.timelimit(happening.etime, now),
            'apcost' : master.apcost,
            'raid' : raid,
            'event' : raidevent_id,
        }

    @staticmethod
    def producehappening(handler, happeningraidset, prize=None, o_person=None):
        """ハプニング.
        """
        now = OSAUtil.get_now()

        happeningset = happeningraidset.happening
        raidboss = happeningraidset.raidboss

        happening = happeningset.happening
        master = happeningset.master

        raid = None
        produceevent_id = 0
        if raidboss:
            eventmaster = None
            produceevent_id = HappeningUtil.get_produceeventid(happeningset.happening.event)
            if produceevent_id:
                eventmaster = BackendApi.get_produce_event_master(handler.getModelMgr(), produceevent_id, using=settings.DB_READONLY)
            raid = Objects.raid(handler, raidboss, o_person=o_person, eventmaster=eventmaster, is_produceevent=True)

        return {
            'id': happening.id,
            'oid': happening.oid,
            'name': master.name,
            'text': master.text,
            'thumbUrl': handler.makeAppLinkUrlImg(master.thumb),
            'progress': happening.progress,
            'execution': master.execution,
            'percent': int(happening.progress * 100 / master.execution) if 0 < master.execution else 100,
            'cleared': master.execution <= happening.progress,
            'prize': prize or {},
            'exp': master.exp,
            'goldmin': master.goldmin,
            'goldmax': master.goldmax,
            'timelimit': 0,
            'apcost': master.apcost,
            'raid': raid,
            'event': produceevent_id,
        }
    
    @staticmethod
    def area(handler, areamaster, playdata):
        """エリア
        """
        url = UrlMaker.scout()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_AREA, areamaster.id)
        
        return {
            'id' : areamaster.id,
            'name' : areamaster.name,
            'text' : areamaster.text,
            'thumbUrl' : handler.makeAppLinkUrlImg(areamaster.thumb),
            'cleared' : playdata is not None,
            'url_scout' : handler.makeAppLinkUrl(url),
        }
    
    @staticmethod
    def boss(handler, bossmaster, hp_rest=None):
        """ボス.
        """
        if hp_rest is None:
            hp_rest = bossmaster.hp
        
        return {
            'id' : bossmaster.id,
            'name' : bossmaster.name,
            'thumbUrl' : handler.makeAppLinkUrlImg(bossmaster.thumb),
            'commentappear' : bossmaster.commentappear,
            'commentwin' : bossmaster.commentwin,
            'commentlose' : bossmaster.commentlose,
            'hp' : bossmaster.hp,
            'hp_rest' : hp_rest,
            'apcost' : bossmaster.apcost,
            'defense' : bossmaster.defense,
        }
    
    @staticmethod
    def prize(handler, gold, gachapt, itemlist, cardlist, rareoverticket, ticket, memoriesticket, gachaticket, goldkey, silverkey, cabaretking=0, demiworld=0, eventticket_list=None, additional_tickets=None, tanzaku_list=None, cabaclub_money=None, platinum_piece_num=None, crystal_piece_num=None):
        """報酬.
        """
        listitem_list = []
        
        def addListItem(thumb, name, num, unit, sep=u' ', smallname=None, icon=None, rare=None, power=None, thumbMiddle=None):
            smallname = smallname or name
            listitem_list.append({
                'thumbUrl' : thumb,
                'text' : u'%s%s%d%s' % (name, sep, num, unit),
                'smalltext' : u'%s%s%d%s' % (smallname, sep, num, unit),
                'name' : name,
                'num' : num,
                'unit' : unit,
                'sep' : sep,
                'icon' : icon,
                'rare' : rare,
                'power' : power,
                'thumbMiddle' : thumbMiddle or thumb,
            })
        
        def addListItemByType(itype, num, sep=u''):
            thumb = handler.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(itype))
            name = Defines.ItemType.NAMES[itype]
            unit = Defines.ItemType.UNIT[itype]
            smalltext_name = Defines.ItemType.SMALL_NAMES.get(itype, name)
            addListItem(thumb, name, num, unit, sep, smalltext_name)
        
        data = {
            'gold': None,
            'gold_thumbUrl' : handler.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD)),
            'gold_unit': Defines.ItemType.UNIT[Defines.ItemType.GOLD],
            'gachapt': None,
            'itemlist': None,
            'cardlist': None,
            'rareoverticket' : None,
            'ticket': None,
            'memoriesticket': None,
            'gachaticket' : None,
            'goldkey': None,
            'silverkey': None,
            'cabaretking' : None,
            'demiworld' : None,
            'eventticket_list' : None,
            'tanzaku_list' : None,
            'cabaclub_money': None,
            'platinum_piece_num': None,
            'crystal_piece_num': None,
        }
        
        if cardlist:
            cardlist.sort(key=lambda x:(((Defines.CardKind.NUM_MAX - x['master']['kind'])<<8)+x['master']['rare']), reverse=True)
            data['cardlist'] = cardlist
            for card in cardlist:
                master = card['master']
                icon, rare, power = (master['iconUrl'], master['rare'], master['maxpower']) if master['kind'] == Defines.CardKind.NORMAL else (None, None, None)
                addListItem(master['thumbUrl'], master['name'], card.get('num', 1), master['unit'], u'x', icon=icon, rare=rare, power=power, thumbMiddle=master['thumbnail']['small'])
        if additional_tickets:
            unit = Defines.ItemType.UNIT[Defines.ItemType.ADDITIONAL_GACHATICKET]
            data['additionalticket'] = additional_tickets
            for ttype, tnum in additional_tickets.items():
                thumb = ItemUtil.makeThumbnailUrlSmallByDBString(Defines.GachaConsumeType.GachaTicketType.THUMBNAIL[ttype])
                thumb = handler.makeAppLinkUrlImg(thumb)
                name = Defines.GachaConsumeType.GachaTicketType.NAMES[ttype]
                addListItem(thumb, name, tnum, unit, u'x')
        if rareoverticket:
            data['rareoverticket'] = rareoverticket
            addListItemByType(Defines.ItemType.RAREOVERTICKET, rareoverticket)
        if eventticket_list:
            unit = Defines.ItemType.UNIT[Defines.ItemType.EVENT_GACHATICKET]
            data['eventticket_list'] = eventticket_list
            for eventticket in eventticket_list:
                master = eventticket['master']
                if settings_sub.IS_DEV:
                    name = '%s(%s)' % (master['ticketname'], master['id'])
                else:
                    name = master['ticketname']
                addListItem(master['ticketThumbUrl'], name, eventticket.get('num', 1), unit, u'x')
        if tanzaku_list:
            data['tanzaku_list'] = tanzaku_list
            for tanzaku in tanzaku_list:
                master = tanzaku['master']
                if settings_sub.IS_DEV:
                    name = '%s(%s)' % (master['tanzakuname'], master['number'])
                else:
                    name = master['tanzakuname']
                addListItem(master['tanzakuthumb'], name, tanzaku.get('num', 1), master['tanzakuunit'], u'x')
        if cabaretking:
            data['cabaretking'] = cabaretking
            addListItemByType(Defines.ItemType.CABARETKING_TREASURE, cabaretking)
        if demiworld:
            data['demiworld'] = demiworld
            addListItemByType(Defines.ItemType.DEMIWORLD_TREASURE, demiworld)
        if itemlist:
            data['itemlist'] = itemlist
            for item in itemlist:
                master = item['master']
                addListItem(master['thumbUrl'], master['name'], item.get('num', 1), master['unit'], u'x')
        if ticket:
            data['ticket'] = ticket
            addListItemByType(Defines.ItemType.TRYLUCKTICKET, ticket)
        if memoriesticket:
            data['memoriesticket'] = memoriesticket
            addListItemByType(Defines.ItemType.MEMORIESTICKET, memoriesticket)
        if gachaticket:
            data['gachaticket'] = gachaticket
            addListItemByType(Defines.ItemType.GACHATICKET, gachaticket)
        if goldkey:
            data['goldkey'] = goldkey
            addListItemByType(Defines.ItemType.GOLDKEY, goldkey)
        if silverkey:
            data['silverkey'] = silverkey
            addListItemByType(Defines.ItemType.SILVERKEY, silverkey)
        if gachapt:
            data['gachapt'] = gachapt
            addListItemByType(Defines.ItemType.GACHA_PT, gachapt)
        if gold:
            data['gold'] = gold
            addListItemByType(Defines.ItemType.GOLD, gold)
        if cabaclub_money:
            data['cabaclub_money'] = cabaclub_money
            addListItemByType(Defines.ItemType.CABARETCLUB_SPECIAL_MONEY, cabaclub_money)
        if platinum_piece_num:
            data['platinum_piece_num'] = platinum_piece_num
            addListItemByType(Defines.ItemType.PLATINUM_PIECE, platinum_piece_num)
        if crystal_piece_num:
            data['crystal_piece_num'] = crystal_piece_num
            addListItemByType(Defines.ItemType.CRYSTAL_PIECE , crystal_piece_num)
        data['listitem_list'] = listitem_list
        return data
    
    @staticmethod
    def timelimit(timelimit_time, now=None):
        """制限時間.
        """
        now = now or OSAUtil.get_now()
        timedelta = timelimit_time - now
        tmp = max(timedelta.days * 86400 + timedelta.seconds, 0)
        
        s = tmp % 60
        tmp /= 60
        m = int(tmp % 60)
        h = int(tmp / 60)
        
        return {
            'hours' : h,
            'minutes' : m,
            'seconds' : s,
        }
    
    @staticmethod
    def gachaseat(handler, gachamaster, seattablemaster, presentsetlist, seatplaycount, seatplaydata, allend=False):
        """シートガチャ情報.
        """
        last = seatplaydata.last if seatplaydata else -1
        obj_last = None
        
        obj_list = []
        for idx, arr in enumerate(presentsetlist):
            obj = None
            if arr:
                presentset, thumb = arr
                obj = {
                    'name' : presentset.itemname,
                    'numtext' : presentset.numtext_with_x,
                    'thumb' : handler.makeAppLinkUrlImg(thumb or presentset.itemthumbnail_rect_middle),
                    'last' : last == idx,
                    'got' : allend or (seatplaydata and seatplaydata.getFlag(idx)),
                }
                if last == idx:
                    obj_last = obj
            obj_list.append(obj)
        
        url_reset = None

        if seatplaydata and not seatplaydata.is_first() and gachamaster.consumetype != Defines.GachaConsumeType.MINI_SEAT and gachamaster.stock == 0:
            url_reset = OSAUtil.addQuery(UrlMaker.gachaseatreset(), Defines.URLQUERY_ID, gachamaster.id)
            url_reset = handler.makeAppLinkUrl(url_reset)
        
        return {
            'tableid' : gachamaster.seattableid,
            'list' : obj_list,
            'url_reset' : url_reset,
            'lap' : seatplaycount.lap if seatplaycount else 0,
            'last' : obj_last,
            'thumb' : handler.makeAppLinkUrlImg(seattablemaster.thumb) if seattablemaster.thumb else None,
        }
    
    @staticmethod
    def gacha(handler, gachamaster, player, playcount, gachabox=None, boxgrouplist=None, omake=None, banner=None, stepup=None, raremin=None, boxraremap=None, seatinfo=None):
        """ガチャ.
        """
        model_mgr = handler.getModelMgr()
        now = OSAUtil.get_now()

        seatmodels = {}
        if gachamaster.firsttimetype == Defines.GachaFirsttimeType.SEAT:
            seatmodels = BackendApi.get_gachaseatmodels_by_gachamaster(model_mgr, player.id, gachamaster, using=settings.DB_READONLY)
        
        seatplaydata=seatmodels.get('playdata')
        first_stock = BackendApi.get_gacha_firstplay_restnum(gachamaster, playcount, seatplaydata=seatplaydata)
        is_first = 0 < first_stock
        continuity = BackendApi.get_gacha_continuity_num(model_mgr, gachamaster, player, False, using=settings.DB_READONLY)
        continuity_first = BackendApi.get_gacha_continuity_num(model_mgr, gachamaster, player, True, using=settings.DB_READONLY)
        price = BackendApi.get_consumevalue(gachamaster, continuity, False, playcount, seatplaydata=seatplaydata)
        price_first = BackendApi.get_consumevalue(gachamaster, continuity, True, seatplaydata=seatplaydata)
        addsocardflg = gachamaster.addsocardflg
        
        firsttype_text = u''
        if gachamaster.firsttimetype == Defines.GachaFirsttimeType.ONETIME:
            if gachamaster.firststock == 1:
                firsttype_text = u'初回'
            else:
                firsttype_text = u'%d回目まで' % gachamaster.firststock
        elif gachamaster.firsttimetype == Defines.GachaFirsttimeType.EVERYDAY:
            firsttype_text = u'1日%d回' % gachamaster.firststock
        
        total_group_totalnum = 0
        total_group_restnum = 0
        
        url_boxreset = UrlMaker.gachaboxreset(player.req_confirmkey)
        
        is_empty = False
        if gachabox:
            total_group_totalnum = gachabox.rest
            total_group_restnum = gachabox.num_total
            is_empty = gachabox.is_empty
            
            topic = Defines.GachaConsumeType.TO_TOPIC.get(gachamaster.consumetype)
            url_boxreset = OSAUtil.addQuery(UrlMaker.gachaboxreset(player.req_confirmkey), Defines.URLQUERY_ID, gachamaster.boxid)
            url_boxreset = OSAUtil.addQuery(url_boxreset, Defines.URLQUERY_CTYPE, topic)
            url_boxreset = OSAUtil.addQuery(url_boxreset, Defines.URLQUERY_GTYPE, Defines.GachaConsumeType.GTYPE_NAMES[gachamaster.consumetype])
            url_boxreset = OSAUtil.addQuery(url_boxreset, Defines.URLQUERY_GTAB, gachamaster.tabengname)
            url_boxreset = handler.makeAppLinkUrl(url_boxreset)
        
        model_mgr = handler.getModelMgr()
        stime = None
        etime = None
        schedulewday = Defines.WeekDay.ALL
        scheduleshour = 0
        schedulesmin = 0
        if gachamaster.schedule:
            schedulemaster = BackendApi.get_model(model_mgr, ScheduleMaster, gachamaster.schedule, using=settings.DB_READONLY)
            if schedulemaster:
                stime = schedulemaster.stime
                etime = schedulemaster.etime
                schedulewday = schedulemaster.wday
                scheduleshour = schedulemaster.shour
                schedulesmin = schedulemaster.sminute
        
        price_once = gachamaster.consumevalue
        values_list = []
        if gachamaster.consumetype in Defines.GachaConsumeType.PAYMENT_TYPES:
            if isinstance(gachamaster.variableconsumevalue, dict) and len(gachamaster.variableconsumevalue) > 0:
                price_once = price
                for k, v in sorted(gachamaster.variableconsumevalue.iteritems()):
                    values_list.append(v)

        step = None
        lap = None
        stepmax = None
        lapdaymax = None
        timelimitstep = None
        timelimitlap = None
        stepup_img = None
        if stepup:
            if playcount:
                step = playcount.step + 1
                lap = playcount.lap + 1
            else:
                step = 1
                lap = 1
            stepmax = stepup.stepmax
            lapdaymax = stepup.lapdaymax
            if stepup.stepreset:
                resettm = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
                resettm = resettm.replace(tzinfo=timezone.TZ_DEFAULT)
                resettm += datetime.timedelta(0, stepup.stepresettime)
                if now >= resettm:
                    resettm += datetime.timedelta(1)
                timelimitstep = Objects.timelimit(resettm, now)
            if stepup.lapreset:
                resettm = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
                resettm = resettm.replace(tzinfo=timezone.TZ_DEFAULT)
                resettm += datetime.timedelta(0, stepup.lapresettime)
                if now >= resettm:
                    resettm += datetime.timedelta(1)
                timelimitlap = Objects.timelimit(resettm, now)
            stepup_img = {}
            if stepup.img_banner:
                stepup_img.update(banner=handler.makeAppLinkUrlImg(stepup.img_banner))
            if stepup.img_rule:
                stepup_img.update(rule=handler.makeAppLinkUrlImg(stepup.img_rule))
        
        stock = BackendApi.get_gacha_stock(model_mgr, gachamaster, playcount, now, using=settings.DB_READONLY)

        # リセット可能な box ガチャのユーザデータ
        player_boxdata = model_mgr.get_model(GachaBoxResetPlayerData, player.id, using=settings.DB_DEFAULT)
        if player_boxdata is None:
            player_boxdata = GachaBoxResetPlayerData.makeInstance(player.id)

        # リセット可能な box ガチャのマスター
        gachabox_limit_resettime = 0
        boxdetail = model_mgr.get_model(GachaBoxGachaDetailMaster, gachamaster.id, using=settings.DB_READONLY)
        if boxdetail:
            detail = {
                "allowreset_rarity": boxdetail.allowreset_rarity,
                "allowreset_cardidlist": boxdetail.allowreset_cardidlist,
                "limit_resettime": boxdetail.limit_resettime,
                "resetnum": player_boxdata.resetcount,
            }
            gachabox_limit_resettime = boxdetail.limit_resettime
        
        if gachamaster.consumetype in {Defines.GachaConsumeType.LIMITED_RESET_BOX, Defines.GachaConsumeType.EVENTTICKET} and \
           (boxdetail is None or player_boxdata.resetcount < boxdetail.limit_resettime) and \
           (player_boxdata.is_get_targetrarity or is_empty) and \
           (boxdetail is not None and player_boxdata.resetcount < boxdetail.limit_resettime):
            is_box_reset = True
        elif gachamaster.consumetype not in {Defines.GachaConsumeType.MINI_BOX,
                                             Defines.GachaConsumeType.MINI_BOX2,
                                             Defines.GachaConsumeType.LIMITED_RESET_BOX,
                                             Defines.GachaConsumeType.EVENTTICKET}:
            is_box_reset = True
        else:
            is_box_reset = None

        if gachamaster.consumetype in {Defines.GachaConsumeType.SEAT, Defines.GachaConsumeType.SEAT2}:
            if playcount and playcount.cnttotal == 0:
                is_first = True
            else:
                is_first = False

        gacha_explain_model = model_mgr.get_model(GachaExplainMaster, gachamaster.gacha_explain_text_id, using=settings.DB_READONLY)
        if gacha_explain_model:
            explain_text = gacha_explain_model.explain_text
        else:
            explain_text = None

        return {
            'id' : gachamaster.id,
            'name' : gachamaster.name,
            'unique_name' : gachamaster.unique_name,
            'consumetype' : gachamaster.consumetype,
            'boxid' : gachamaster.boxid,
            'text' : gachamaster.text,
            'total_group_totalnum' : total_group_totalnum,
            'total_group_restnum' : total_group_restnum,
            'thumbUrl' : handler.makeAppLinkUrlImg(gachamaster.thumb),
            'ruleUrl' : handler.makeAppLinkUrlImg(gachamaster.img_rule) if gachamaster.img_rule else '',
            'is_first' : is_first,
            'first_stock' : first_stock,
            'first_stock_ori' : gachamaster.firststock,
            'continuity' : continuity,
            'price_once' : price_once,
            'price' : price,
            'price_origin' : gachamaster.consumevalue,
            'continuity_first' : continuity_first,
            'price_first' : price_first,
            'url_do' : handler.makeAppLinkUrl(UrlMaker.gachado(gachamaster.id, player.req_confirmkey)),
            'url_cardlist' : handler.makeAppLinkUrl(UrlMaker.gachacardlist(gachamaster.id)),
            'url_boxreset' : url_boxreset if is_box_reset else None,
            'url_supinfo' : handler.makeAppLinkUrl(UrlMaker.gachasupinfo(gachamaster.stepid)),
            'url_supcard' : handler.makeAppLinkUrl(UrlMaker.gachasupcard(gachamaster.id)),
            'url_supcard_subbox' : handler.makeAppLinkUrl(UrlMaker.gachasupcard(gachamaster.id, subbox=1)),
            'firsttimetype' : gachamaster.firsttimetype,
            'firsttype_text' : firsttype_text,
            'boxgrouplist' : boxgrouplist,
            'omake' : omake,
            'banner' : banner,
            'stime' : stime,
            'etime' : etime,
            'stime_text' : gachamaster.stime_text,
            'etime_text' : gachamaster.etime_text,
            'step' : step,
            'stepmax' : stepmax,
            'lap' : lap,
            'lapdaymax' : lapdaymax,
            'raremin' : raremin,
            'timelimitstep' : timelimitstep,
            'timelimitlap' : timelimitlap,
            'playcount' : playcount.cnttotal if playcount else 0,
            'boxraremap' : boxraremap,
            'is_empty' : is_empty,
            'seatinfo' : seatinfo,
            'addsocardflg' : addsocardflg,
            'stock' : stock,
            'stockmax' : gachamaster.stock,
            'stepup_img' : stepup_img,
            'tabname' : gachamaster.tabname,
            'tabengname' : gachamaster.tabengname,
            'schedulewday' : schedulewday,
            'scheduleshour' : scheduleshour,
            'schedulesmin' : schedulesmin,
            'tradeshopid' : gachamaster.trade_shop_master_id,
            'values_list' : values_list,
            'rarity_fixed_num' : gachamaster.rarity_fixed_num,
            'boxdetail' : detail if boxdetail else None,
            'gachabox_player_resetcount' : player_boxdata.resetcount,
            'gachabox_limit_resettime' : gachabox_limit_resettime,
            'explain_text' : explain_text,
        }

    @staticmethod
    def boxGroup(handler, gachagroupmaster, totalnum, restnum, card):
        """ボックスのグループ情報.
        """
        return {
            'id' : gachagroupmaster.id,
            'name' : gachagroupmaster.name,
            'group_totalnum' : totalnum,
            'group_restnum' : restnum,
            'card' : card,
        }
    
    @staticmethod
    def gachaNews(handler, obj_player, cardmaster, time):
        """ガチャ速報.
        """
        return {
            'player' : obj_player,
            'card' : Objects.cardmaster(handler, cardmaster),
            'time' : u'%s/%s %s' % (time.month, time.day, time.strftime(u"%H:%M")),
            '_time' : time,
        }
    
    @staticmethod
    def rankinggacha(handler, rankinggachamaster, wholepoint=0):
        """ランキングガチャ.
        """
        return {
            'boxid' : rankinggachamaster.id,
            'name' : rankinggachamaster.name,
            'rule' : handler.makeAppLinkUrlImg(rankinggachamaster.img_rule) if rankinggachamaster.img_rule else '',
            'appeal' : [handler.makeAppLinkUrlImg(img) for img in rankinggachamaster.img_appeal] if rankinggachamaster.img_appeal else [],
            'is_support_totalranking' : rankinggachamaster.is_support_totalranking,
            'group' : rankinggachamaster.group,
            'is_support_wholepoint' : rankinggachamaster.is_support_wholepoint,
            'wholepoint' : wholepoint,
        }
    
    @staticmethod
    def gachaomakeinfo(handler, gachamaster, prizeinfo_list):
        """ガチャおまけ情報.
        """
        is_random = bool(prizeinfo_list)
        return {
            'id' : gachamaster.id,
            'name' : gachamaster.name,
            'thumbUrl' : handler.makeAppLinkUrlImg(gachamaster.thumb),
            'prizelist' : prizeinfo_list,
            'is_random' : is_random,
            'consumetype' : gachamaster.consumetype,
        }
    
    @staticmethod
    def shopitem(handler, master, player, buydata, num=-1, url_use=None, unit=''):
        """商品情報.
        """
        if master.consumetype == Defines.ShopConsumeType.PAYMENT:
            url_buy = UrlMaker.shopdo(master.id)
        else:
            url_buy = UrlMaker.shopyesno(master.id)
        data = {
            'id' : master.id,
            'name' : master.name,
            'text' : master.text,
            'thumbUrl' : handler.makeAppLinkUrlImg(master.thumb),
            'price' : master.price,
            'stock' : master.stock,
            'url_buy' : handler.makeAppLinkUrl(url_buy),
            'url_result' : handler.makeAppLinkUrl(UrlMaker.shopresult(master.id)),
            'unit' : unit,
            'consumetype' : master.consumetype,
            'inum0' : master.inum0,
        }
        rest = BackendApi.get_shopitem_stock(handler.getModelMgr(), master, buydata)
        if 0 < rest:
            data['rest'] = rest
        if 0 <= num:
            data['num'] = num
        if url_use:
            data['url_use'] = handler.makeAppLinkUrl(url_use)
        return data
    
    @staticmethod
    def present(handler, presentset, overlimit=False, cur_topic=None):
        """プレゼント.
        """
        url_receive = OSAUtil.addQuery(UrlMaker.presentdo(), Defines.URLQUERY_ID, presentset.present.id)
        if cur_topic is not None:
            url_receive = OSAUtil.addQuery(url_receive, Defines.URLQUERY_CTYPE, cur_topic)
        
        presentid = presentset.present.id if presentset.present.id else 0
        strctime = presentset.present.ctime.strftime(u"%m/%d %H:%M") if presentset.present.ctime else ''
        
        if not presentset.present.limittime or OSAUtil.get_datetime_max() == presentset.present.limittime:
            limittime = None
        else:
            limittime = presentset.present.limittime.strftime(u"%m/%d %H:%M")
        
        iconUrl = presentset.typeIconImg
        
        return {
            'id' : presentid,
            'name' : presentset.itemname,
            'text' : presentset.text,
            'thumbUrl' : handler.makeAppLinkUrlImg(presentset.itemthumbnail),
            'thumbUrlMiddle' : handler.makeAppLinkUrlImg(presentset.itemthumbnail_middle),
            'url_receive' : handler.makeAppLinkUrl(url_receive),
            'ctime' : strctime,
            'limittime' : limittime,
            'numtext' : presentset.numtext_with_x,
            'unit' : presentset.unit,
            'err' : presentset.check_receiveable(overlimit),
            'rareData' : presentset.rareData,
            'statusText' : presentset.statusText,
            'iconUrl' : handler.makeAppLinkUrlImg(iconUrl) if iconUrl else None,
        }
    
    @staticmethod
    def treasureitem(handler, presentset, num):
        """宝箱の中身.
        """
        return {
            'item' : Objects.present(handler, presentset),
            'numtext' : presentset.numtext,
            'num' : num,
        }
    
    @staticmethod
    def treasure(handler, treasure, ttype):
        """宝箱.
        """
        data = {
            'id' : treasure.id,
            'get_url' : handler.makeAppLinkUrl(UrlMaker.treasureget(ttype, treasure.id)),
            'timelimit' : Objects.timelimit(treasure.etime),
            'view' : Objects.treasure_view(handler, ttype),
        }
        return data
    
    @staticmethod
    def treasure_view(handler, treasure_type):
        """宝箱(見た目).
        """
        data = {
            'name' : Defines.TreasureType.NAMES[treasure_type],
            'thumbUrl' : handler.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByTreasureType(treasure_type)),
            'url_list' : handler.makeAppLinkUrl(UrlMaker.treasurelist(treasure_type)),
        }
        return data
    
    @staticmethod
    def treasuremaster(handler, master):
        """宝箱.
        """
        # キャバゴールド・ガチャPt
        if master.itype in [Defines.ItemType.GOLD, Defines.ItemType.GACHA_PT]:
            detail = u'%s×%d%s' % (master.name, master.ivalue2, master.unit)
        # カード・アイテム・チケット
        else:
            detail = u'%s×%d%s' % (master.name, master.ivalue2, master.unit)
        
        return {
            'id' : master.id,
            'itype' : master.itype,
            'ivalue1' : master.ivalue1,
            'ivalue2' : master.ivalue2,
            'name' : master.name,
            'text' : master.text,
            'detail' : detail,
            'thumbUrl' : handler.makeAppLinkUrlImg(master.thumb),
        }
    
    @staticmethod
    def key(handler, player):
        """鍵.
        """
        def makeObj(itype, num):
            return {
                'name' : Defines.ItemType.NAMES.get(itype, ''),
                'thumbUrl' : handler.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(itype)),
                'unit' : Defines.ItemType.UNIT.get(itype, ''),
                'num' : num,
            }
        
        return {
            'gold' : makeObj(Defines.ItemType.GOLDKEY, player.goldkey),
            'silver' : makeObj(Defines.ItemType.SILVERKEY, player.silverkey),
        }
    
    @staticmethod
    def trade(handler, trade, presentset):
        """秘宝交換.
        """
        name = presentset.itemname
        thumbnail = presentset.itemthumbnail
        unit = presentset.unit
        
        data = {
            'id' : trade.id,
            'itype' : trade.itype,
            'itemid' : trade.itemid,
            'itemnum' : trade.itemnum,
            'name' : name,
            'unit' : unit,
            'thumbUrl' : handler.makeAppLinkUrlImg(thumbnail),
            'rate_cabaretking' : trade.rate_cabaretking,
            'rate_demiworld' : trade.rate_cabaretking,  # rate_demiworld.
            'item' : Objects.present(handler, presentset),
            'stock' : trade.stock,
            'trade_cnt' : 0,
            'err_mess' : None,
        }
        return data

    @staticmethod
    def produceevent(handler, eventmaster, config):
        """プロデュースイベント
        """
        now = OSAUtil.get_now()

        is_opened = False
        starttime = None
        endtime = None

        if config and config.mid == eventmaster.id:
            starttime = config.starttime
            endtime = config.endtime

            is_opened = (starttime <= now < endtime)

        mainname = eventmaster.name
        subname = eventmaster.subname
        name = mainname
        if subname:
            name = u'%s〜%s〜' % (name, subname)

        return {
            'id' : eventmaster.id,
            'name' : name,
            'mainname' : mainname,
            'subname' : subname,
            'codename': eventmaster.codename,
            'html' : eventmaster.htmlname,
            'starttime' : starttime,
            'endtime' : endtime,
            'is_opened' : is_opened,
            'appeal' : [handler.makeAppLinkUrlImg(img) for img in eventmaster.img_appeal] if eventmaster.img_appeal else [],
        }

    @staticmethod
    def produceevent_stage(handler, player, cur_stagenumber, stagemaster, progress=0, confirmkey=None, bossattack=False, areaboss_attack=False):
        """プロデュースイベントステージ
        """
        url = None
        if bossattack:
            url = handler.makeAppLinkUrl(UrlMaker.produceevent_battlepre())
        elif areaboss_attack:
            url = handler.makeAppLinkUrl(UrlMaker.bosspre(stagemaster.id))
        elif cur_stagenumber == stagemaster.stage and not bossattack and confirmkey:
            url = handler.makeAppLinkUrl(UrlMaker.produceevent_scoutdo(stagemaster.id, confirmkey))

        return {
            'id': stagemaster.id,
            'name': stagemaster.name,
            'areaname': stagemaster.areaname,
            'text': stagemaster.text,
            'thumbUrl': handler.makeAppLinkUrlImg(stagemaster.thumb),
            'progress': progress,
            'execution': stagemaster.execution,
            'percent': min(100, int(progress * 100 / stagemaster.execution)),
            'cleared': stagemaster.execution <= progress,
            'url_exec': url,
            'dropitems': [],
            'exp': stagemaster.exp,
            'goldmin': stagemaster.goldmin,
            'goldmax': stagemaster.goldmax,
            'apcost': BackendApi.get_event_apcost(stagemaster, player),
            'url_scout': handler.makeAppLinkUrl(UrlMaker.produceevent_scouttop()),
        }

    @staticmethod
    def produceevent_score(eventmaster, scorerecord, rank, rank_beginer=None):
        """レイドイベントのスコア.
        """
        if scorerecord is None:
            scorerecord = ProduceEventScore.makeInstance(ProduceEventScore.makeID(0, eventmaster.id))
        return {
            'mid': eventmaster.id,
            'point': scorerecord.point,
            'rank': rank,
        }

    @staticmethod
    def raidevent(handler, eventmaster, config):
        """レイドイベント.
        """
        now = OSAUtil.get_now()
        
        is_opened = False
        is_ticket_opened = False
        ticket_etime = None
        if config and config.mid == eventmaster.id:
            starttime = config.starttime
            endtime = config.endtime
            ticket_etime = config.ticket_endtime
            if starttime <= now < endtime:
                is_opened = True
            if starttime <= now < ticket_etime:
                is_ticket_opened = True
        else:
            starttime = None
            endtime = None
        
        if is_opened:
            _, etime = BackendApi.choice_raidevent_timebonus_time(config, now=now)
        else:
            etime = None
        
        mainname = eventmaster.name
        subname = eventmaster.subname
        name = mainname
        if subname:
            name = u'%s〜%s〜' % (name, subname)
        
        return {
            'id' : eventmaster.id,
            'name' : name,
            'mainname' : mainname,
            'subname' : subname,
            'codename' : eventmaster.codename,
            'pointratio' : eventmaster.pointratio,
            'timebonus_etime' : etime,
            'starttime' : starttime,
            'endtime' : endtime,
            'ticket_etime' : ticket_etime,
            'is_opened' : is_opened,
            'is_big_opened' : config and config.bigtime and config.bigtime <= now,
            'is_ticket_opened' : is_ticket_opened,
            'pointname' : eventmaster.pointname,
            'ticketname' : eventmaster.ticketname,
            'pointThumbUrl' : handler.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByDBString(eventmaster.pointthumb)),
            'ticketThumbUrl' : handler.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByDBString(eventmaster.ticketthumb)),
            'pointThumbnail' : {
                'small' : handler.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByDBString(eventmaster.pointthumb)),
                'middle' : handler.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlMiddleByDBString(eventmaster.pointthumb)),
            },
            'ticketThumbnail' : {
                'small' : handler.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByDBString(eventmaster.ticketthumb)),
                'middle' : handler.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlMiddleByDBString(eventmaster.ticketthumb)),
            },
            'url_tradeyesno' : handler.makeAppLinkUrl(UrlMaker.tradeyesno('event')),
            'feverchancepowup' : eventmaster.feverchancepowup,
            'feverchancetime' : eventmaster.feverchancetime,
            'topbuttontext' : eventmaster.topbuttontext,
            'appeal' : [handler.makeAppLinkUrlImg(img) for img in eventmaster.img_appeal] if eventmaster.img_appeal else [],
            'champagne_num_max' : eventmaster.champagne_num_max,
            'champagne_time' : eventmaster.champagne_time,
            'champagne_material_bonus' : eventmaster.champagne_material_bonus,
            'flag_dedicated_stage' : eventmaster.flag_dedicated_stage,
        }
    
    @staticmethod
    def raidevent_score(eventmaster, scorerecord, rank, rank_beginer=None):
        """レイドイベントのスコア.
        """
        if scorerecord is None:
            scorerecord = RaidEventScore.makeInstance(RaidEventScore.makeID(0, eventmaster.id))
        return {
            'destroy' : scorerecord.destroy,
            'destroy_big' : scorerecord.destroy_big,
            'point' : scorerecord.point,
            'point_total' : scorerecord.point_total,
            'ticket' : scorerecord.ticket,
            'rank' : rank,
            'rank_beginer' : rank_beginer,
        }
    
    @staticmethod
    def raidevent_recipe(handler, recipemaster, presentset, mixdata=None):
        """レイドイベントのレシピ.
        """
        name = presentset.itemname
        unit = presentset.unit
        trade_cnt = mixdata.getCount(recipemaster.eventid) if mixdata else 0
        
        return {
            'id' : recipemaster.id,
            'name' : name,
            'unit' : unit,
            'thumbUrl' : handler.makeAppLinkUrlImg(recipemaster.thumb),
            'eventid' : recipemaster.eventid,
            'trade_cnt' : trade_cnt,
            'itype' : recipemaster.itype,
            'itemid' : recipemaster.itemid,
            'itemnum' : recipemaster.itemnum,
            'stock' : recipemaster.stock,
            'materialnum0' : recipemaster.materialnum0,
            'materialnum1' : recipemaster.materialnum1,
            'materialnum2' : recipemaster.materialnum2,
            'item' : Objects.present(handler, presentset),
            'err_mess' : None,
            'url_yesno' : handler.makeAppLinkUrl(UrlMaker.raidevent_recipe_yesno(recipemaster.id)),
            'trade_max' : None,
        }
    
    @staticmethod
    def raidevent_material(handler, materialmaster, num=0):
        """レイドイベントの素材.
        """
        return {
            'id' : materialmaster.id,
            'name' : materialmaster.name,
            'thumbUrl' : handler.makeAppLinkUrlImg(materialmaster.thumb),
            'num' : num,
            'unit' : materialmaster.unit,
        }
    
    @staticmethod
    def raidevent_champagne(handler, raideventmaster, champagnedata, now=None):
        """レイドイベントのシャンパン情報.
        """
        now = now or OSAUtil.get_now()
        
        obj = {}
        num = 0
        is_fever_ready = False
        is_fever = False
        if 0 < raideventmaster.champagne_num_max and champagnedata:
            num = champagnedata.getChampagneNum(raideventmaster.id)
            if now <= champagnedata.etime:
                obj.update(timelimit=Objects.timelimit(champagnedata.etime, now))
                is_fever = True
            elif raideventmaster.champagne_num_max <= num:
                is_fever_ready = True
        obj.update(num=num, is_fever=is_fever, is_fever_ready=is_fever_ready)
        return obj
    
    @staticmethod
    def raidevent_stage(handler, player, cur_stagenumber, stagemaster, progress=0, confirmkey=None, bossattack=False):
        """スカウトイベント
        """
        url = None
        if cur_stagenumber == stagemaster.stage and not bossattack and confirmkey:
            url = handler.makeAppLinkUrl(UrlMaker.raidevent_scoutdo(stagemaster.id, confirmkey))
        
        return {
            'id' : stagemaster.id,
            'name' : stagemaster.name,
            'areaname' : stagemaster.areaname,
            'text' : stagemaster.text,
            'thumbUrl' : handler.makeAppLinkUrlImg(stagemaster.thumb),
            'progress' : progress,
            'execution' : stagemaster.execution,
            'percent' : min(100, int(progress * 100 / stagemaster.execution)),
            'cleared' : stagemaster.execution <= progress,
            'url_exec' : url,
            'dropitems' : [],
            'exp' : stagemaster.exp,
            'goldmin' : stagemaster.goldmin,
            'goldmax' : stagemaster.goldmax,
            'apcost' : BackendApi.get_event_apcost(stagemaster, player),
            'url_scout' : handler.makeAppLinkUrl(UrlMaker.raidevent_scouttop()),
        }
    
    @staticmethod
    def scoutevent_stage_bustup(handler, stagemaster):
        """スカウトイベントバストアップ画像.
        """
        bustup_arr = []
        arr = [
            stagemaster.bustuprate_0,
            stagemaster.bustuprate_1,
            stagemaster.bustuprate_2,
        ]
        randmax = sum(arr)
        if stagemaster.bustup and randmax:
            cnt = 0
            rand = AppRandom()
            v = rand.getIntN(randmax)
            for idx, bustuprate in enumerate(arr):
                if bustuprate < 1:
                    continue
                v -= bustuprate
                if v < 0:
                    cnt = idx
                    break
            tmp = stagemaster.bustup[:]
            random.shuffle(tmp)
            for bustup in tmp[:cnt]:
                bustup_arr.append({
                    'img' : handler.makeAppLinkUrlImg(bustup),
                })
        return bustup_arr
    
    @staticmethod
    def scoutevent_stage(handler, stagemaster, playdata):
        """スカウトイベントステージ
        """
        url = UrlMaker.scoutevent()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_AREA, stagemaster.id)
        
        bustup_arr = Objects.scoutevent_stage_bustup(handler, stagemaster)
        
        return {
            'id' : stagemaster.id,
            'name' : stagemaster.name,
            'areaname' : stagemaster.areaname,
            'text' : stagemaster.text,
            'thumbUrl' : handler.makeAppLinkUrlImg(stagemaster.thumb),
            'cleared' : playdata is not None,
            'url_scout' : handler.makeAppLinkUrl(url),
            'bustup' : bustup_arr,
        }
    
    @staticmethod
    def scouteventmaster(handler, eventmaster, config):
        """スカウトイベント.
        """
        now = OSAUtil.get_now()
        
        is_opened = False
        is_produce_open = False
        produce_etime = None
        if config and config.mid == eventmaster.id:
            starttime = config.starttime
            endtime = config.endtime
            if starttime <= now < endtime:
                is_opened = True
            if eventmaster.is_produce:
                produce_etime = config.present_endtime
                is_produce_open = now <= produce_etime
        else:
            starttime = None
            endtime = None
        
        codename = eventmaster.codename
        
        mainname = eventmaster.name
        subname = eventmaster.subname
        name = mainname
        if subname:
            name = u'%s〜%s〜' % (name, subname)
        
        return {
            'id' : eventmaster.id,
            'name' : name,
            'mainname' : mainname,
            'subname' : subname,
            'codename' : codename,
            'starttime' : starttime,
            'endtime' : endtime,
            'is_opened' : is_opened,
            'appeal' : [handler.makeAppLinkUrlImg(img) for img in eventmaster.img_appeal] if eventmaster.img_appeal else [],
            'img_produce' : handler.makeAppLinkUrlImg(eventmaster.img_produce) if eventmaster.is_produce and eventmaster.img_produce else None,
            'produce_etime' : produce_etime,
            'is_produce_open' : is_produce_open,
            'is_produce' : eventmaster.is_produce,
            'gachaptname' : eventmaster.gachaptname,
            'point_name' : "チョコ" if eventmaster.gachaptname == "カカオ" else "ハート",
            'gachaptimg' : handler.makeAppLinkUrlImg(eventmaster.gachaptimg),
            'chocolate_thumb' : 'item/scevent/common/event_item_choco_01_m.png' if eventmaster.gachaptname == 'カカオ' else 'item/scevent/common/event_item_heart_60_60.png',
            'lovetime_star' : eventmaster.lovetime_star,
            'tanzaku_name' : eventmaster.tanzaku_name  or '指名用名刺',
            'lovetime_starname' : eventmaster.lovetime_starname,
            'lovetime_starimgon' : eventmaster.lovetime_starimgon,
            'lovetime_starimgoff' : eventmaster.lovetime_starimgoff,
            'lovetime_pointname' : eventmaster.lovetime_pointname,
        }
    
    @staticmethod
    def scoutevent(handler, player, cur_stagenumber, stagemaster, progress, confirmkey, bossattack=False):
        """スカウトイベント
        """
        url = None
        if stagemaster.stage >= cur_stagenumber:
            if not bossattack:
                url = handler.makeAppLinkUrl(UrlMaker.scouteventdo(stagemaster.id, confirmkey))
        
        bustup_arr = Objects.scoutevent_stage_bustup(handler, stagemaster)
        
        return {
            'id' : stagemaster.id,
            'name' : stagemaster.name,
            'areaname' : stagemaster.areaname,
            'text' : stagemaster.text,
            'thumbUrl' : handler.makeAppLinkUrlImg(stagemaster.thumb),
            'progress' : progress,
            'execution' : stagemaster.execution,
            'percent' : min(100, int(progress * 100 / stagemaster.execution)),
            'cleared' : stagemaster.execution <= progress,
            'url_exec' : url,
            'dropitems' : [],
            'exp' : stagemaster.exp,
            'goldmin' : stagemaster.goldmin,
            'goldmax' : stagemaster.goldmax,
            'apcost' : BackendApi.get_event_apcost(stagemaster, player),
            'bustup' : bustup_arr,
        }
    
    @staticmethod
    def scoutevent_score(scorerecord, point=0, pointeffect=0, successpoint=0):
        """スカウトイベントのスコア.
        """
        if scorerecord is None:
            return {
                'point_add' : point,
                'point' : point,
                'point_pre' : 0,
                'point_effect' : pointeffect,
                'point_gacha' : 0,
                'success_point' : successpoint,
                'tip' : 0,
            }
        return {
            'point_add' : point,
            'point' : scorerecord.point_total,
            'point_pre' : scorerecord.point_total - point,
            'point_effect' : pointeffect,
            'point_gacha' : scorerecord.point_gacha,
            'success_point' : successpoint,
            'tip' : scorerecord.tip,
        }
    
    @staticmethod
    def scoutevent_data(scorerecord, areanum_cleared, areanum_total, rank, rank_beginer=None):
        """スカウトイベントのイベントデータ欄で表示するパラメータ.
        """
        return {
            'score' : Objects.scoutevent_score(scorerecord),
            'areanum_cleared' : areanum_cleared,
            'areanum_total' : areanum_total,
            'rank' : rank,
            'rank_beginer' : rank_beginer,
        }
    
    @staticmethod
    def scoutevent_fever(eventplaydata, now=None):
        """スカウトイベントのフィーバー時間.
        """
        feverstart = False
        lovetimestart = False
        
        now = now or OSAUtil.get_now()
        star = 0
        if eventplaydata is None:
            feveretime = now
            lovetime_etime = now
        else:
            feveretime = eventplaydata.feveretime
            lovetime_etime = eventplaydata.lovetime_etime or now
            star = eventplaydata.star
            
            if eventplaydata.result:
                feverstart = eventplaydata.result.get('feverstart')
                lovetimestart = eventplaydata.result.get('lovetime_start')
        
        return {
            'etime' : feveretime,
            'timelimit' : Objects.timelimit(feveretime, now) if now < feveretime else None,
            'start' : feverstart,
            
            'lovetime_star' : star,
            'lovetime_etime' : lovetime_etime,
            'lovetime_timelimit' : Objects.timelimit(lovetime_etime, now) if now < lovetime_etime else None,
            'lovetime_start' : lovetimestart,
        }
    
    @staticmethod
    def scoutevent_present_selectobj(handler, presentprizemaster):
        """スカウトイベントハートプレゼント選択情報.
        """
        return {
            'number' : presentprizemaster.number,
            'name' : presentprizemaster.name,
        }
    
    @staticmethod
    def scoutevent_present(handler, presentprizemaster, cur_point, prizepoint, prizeinfo):
        """スカウトイベントハートプレゼント情報.
        """
        return {
            'number' : presentprizemaster.number,
            'name' : presentprizemaster.name,
            'prize' : prizeinfo,
            'pointnext' : (prizepoint - cur_point) if prizepoint else 0,
            'all_received' : prizeinfo is None,
        }
    
    @staticmethod
    def scoutevent_present_result(handler, post_point, prizeinfo):
        """スカウトイベントハートプレゼント投入結果.
        """
        return {
            'point' : post_point,
            'prize' : prizeinfo,
        }
    
    @staticmethod
    def scoutevent_tanzaku(handler, tanzakumaster, tanzakudata=None):
        """短冊所持情報.
        """
        number = tanzakumaster.number
        
        # 所持数とチップ投入数.
        tanzaku = 0
        tip = 0
        if tanzakudata:
            tanzaku = tanzakudata.get_tanzaku(number)
            tip = tanzakudata.get_tip(number)
        
        return {
            'eventid' : tanzakumaster.eventid,
            'number' : number,
            'castname' : tanzakumaster.castname,
            'castthumb' : handler.makeAppLinkUrlImg(tanzakumaster.castthumb),
            'castbg' : handler.makeAppLinkUrlImg(tanzakumaster.castbg),
            'castthumb_small' : handler.makeAppLinkUrlImg(tanzakumaster.castthumb_small),
            'tanzakuname' : tanzakumaster.tanzakuname,
            'tanzakuunit' : tanzakumaster.tanzakuunit,
            'tanzakuthumb' : handler.makeAppLinkUrlImg(tanzakumaster.tanzakuthumb),
            'tanzaku' : tanzakumaster.tanzaku,
            'tip_rate' : tanzakumaster.tip_rate,
            'tip_quota' : tanzakumaster.tip_quota,
            'userdata' : {
                'tanzaku' : tanzaku,
                'tip' : tip,
                'tanzaku_usenums' : ItemUtil.makeUseNumListByList(tanzaku),
            }
        }
    
    @staticmethod
    def battleevent(handler, eventmaster, now=None):
        """バトルイベント.
        """
        model_mgr = handler.getModelMgr()
        now = now or OSAUtil.get_now()
        
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        battlestarttime = None
        battleendtime = None
        is_battle_opened = False
        if config.mid == eventmaster.id:
            starttime = config.starttime
            endtime = config.endtime
            is_opened = BackendApi.is_battleevent_open(model_mgr, using=settings.DB_READONLY, now=now)
            if is_opened:
                battleendtime = BackendApi.get_battleevent_battle_endtime(model_mgr, using=settings.DB_READONLY, now=now)
                if battleendtime is not None:
                    is_battle_opened = now < battleendtime
                    battlestarttime = DateTimeUtil.toLoginTime(now + datetime.timedelta(days=1))
        else:
            starttime = None
            endtime = None
            is_opened = False
        
        mainname = eventmaster.name
        subname = eventmaster.subname
        name = mainname
        if subname:
            name = u'%s〜%s〜' % (name, subname)
        
        return {
            'id' : eventmaster.id,
            'name' : name,
            'mainname' : mainname,
            'subname' : subname,
            'codename' : eventmaster.codename,
            'specialtype' : Defines.CharacterType.SKILL_TARGET_NAMES[eventmaster.specialtype],
            'timelimit_end' : Objects.timelimit(battleendtime, now) if battleendtime else None,
            'timelimit_start' : Objects.timelimit(battlestarttime, now) if battlestarttime else None,
            'starttime' : starttime,
            'endtime' : endtime,
            'is_opened' : is_opened,
            'is_battle_opened' : is_battle_opened,
            'is_emergency' : config.is_emergency,
            'specialtype_long' : Defines.CharacterType.LONG_NAMES.get(eventmaster.specialtype),
            'specialtype_color' : Defines.CharacterType.COLORS.get(eventmaster.specialtype),
            'is_goukon' : eventmaster.is_goukon,
            'appeal' : [handler.makeAppLinkUrlImg(img) for img in eventmaster.img_appeal] if eventmaster.img_appeal else [],
            'bpcalctype' : eventmaster.bpcalctype,
        }
    
    @staticmethod
    def battleevent_score(handler, scorerecord, rank=None, battleresult=None, rank_beginer=None):
        """バトルイベントスコア情報.
        """
        now = OSAUtil.get_now()
        fever = None
        if scorerecord:
            point = scorerecord.getPointToday()
            point_total = scorerecord.point_total
            win = scorerecord.getWinToday()
            winmax = scorerecord.getWinMaxToday()
            if scorerecord.feveretime and now < scorerecord.feveretime:
                fever = {
                    'timelimit' : Objects.timelimit(scorerecord.feveretime, now),
                    'start' : bool(battleresult and battleresult.data.get('feverstart')),
                }
        else:
            point = 0
            point_total = 0
            win = 0
            winmax = 0
        
        return {
            'point' : point,
            'point_total' : point_total,
            'win' : win,
            'winmax' : winmax,
            'rank' : rank,
            'fever' : fever,
            'rank_beginer' : rank_beginer,
        }
    
    @staticmethod
    def battleevent_rank_selectobj(handler, rankmaster, no1_prizeinfo=None):
        """バトルイベントランク選択情報.
        """
        cardmaster = None
        if rankmaster.cardid:
            cardmaster = BackendApi.get_cardmasters([rankmaster.cardid], handler.getModelMgr(), using=settings.DB_READONLY).get(rankmaster.cardid)
        if cardmaster is None:
            return None
        return {
            'cardmaster' : Objects.cardmaster(handler, cardmaster),
            'rank' : rankmaster.rank,
            'name' : rankmaster.name,
            'str_battlepointrate' : rankmaster.str_battlepointrate,
            'no1_prizeinfo' : no1_prizeinfo,
        }
    
    @staticmethod
    def battleevent_rank(handler, rankrecord, rankmaster, grouprecord, grouprankingdata=None):
        """バトルイベントランク情報.
        """
        config = BackendApi.get_current_battleeventconfig(handler.getModelMgr(), using=settings.DB_READONLY)
        # 欲しいのは翌日の最大ランク.
        rank_max = config.getRankMax(OSAUtil.get_now()+datetime.timedelta(days=1))
        
        url = None
        cdate = None
        if isinstance(grouprecord, BattleEventGroup):
            url = handler.makeAppLinkUrl(UrlMaker.battleevent_groupdetail(grouprecord.id))
            cdate = "%d/%02d" % (grouprecord.cdate.month, grouprecord.cdate.day)
        elif isinstance(grouprecord, BattleEventGroupLog):
            url = handler.makeAppLinkUrl(UrlMaker.battleevent_grouplogdetail(grouprecord.id))
            cdate = "%d/%02d" % (grouprecord.cdate.month, grouprecord.cdate.day)
        
        if not grouprankingdata:
            grouprankingdata = {
                'rank' : None,
                'playerlist' : [],
                'vscore' : 0,
            }
        
        now = OSAUtil.get_now()
        return {
            'rank' : rankmaster.rank,
            'name' : rankmaster.name,
            'str_battlepointrate' : rankmaster.str_battlepointrate,
            'thumbUrl' : handler.makeAppLinkUrlImg(rankmaster.thumb),
            'fame' : rankrecord.getFamePoint(config) if rankrecord else 0,
            'rankuptext' : rankmaster.getRankUpText(grouprankingdata.get('rank'), 1, rank_max),
            'rankuptext_zero' : rankmaster.getRankUpText(grouprankingdata.get('rank'), 0, rank_max),
            'fameadd' : rankmaster.getPoint(grouprankingdata.get('rank'), 1),
            'bpcost' : rankmaster.bpcost,
            'cdate' : cdate,
            'url_detail' : url,
            'grouprankingdata' : grouprankingdata,
            'feverpointrate' : rankmaster.feverpointrate,
            'fevertimelimit' : Objects.timelimit(now + datetime.timedelta(seconds=rankmaster.fevertimelimit), now),
        }
    
    @staticmethod
    def battleevent_battlelog(handler, logid, o_player, o_person, o_leader, is_win, is_attack, point, ctime):
        """バトルイベントバトル履歴.
        """
        return {
            'id' : logid,
            'player' : Objects.player(handler, o_player, o_person, o_leader),
            'is_win' : is_win,
            'is_attack' : is_attack,
            'point' : point,
            'ctime' : ctime.strftime("%m/%d %H:%M"),
        }
    
    @staticmethod
    def battleevent_present(handler, presentmaster, presentdata):
        """バトルイベントプレゼント情報.
        """
        return {
            'number' : presentmaster.number,
            'name' : presentmaster.name,
            'point_max' : presentmaster.point,
            'point' : presentdata.point,
            'thumb' : handler.makeAppLinkUrlImg(presentmaster.thumb),
        }
    
    @staticmethod
    def battleevent_present_content(handler, presentmaster, prizeinfo_list):
        """バトルイベントプレゼントの中身.
        """
        return {
            'id' : presentmaster.id,
            'name' : presentmaster.name,
            'prizelist' : prizeinfo_list,
        }
    
    @staticmethod
    def longloginbonus(config_data, cur_day, now=None):
        """ロングログインボーナスデータ.
        """
        now = now or OSAUtil.get_now()
        stime = config_data['stime']
        etime = config_data['etime']
        
        is_open = stime <= now < etime
        return {
            'stime' : stime,
            'etime' : etime,
            'is_open' : is_open,
            'cur_day' : cur_day or 0,
        }
    
    @staticmethod
    def longloginbonus_daydata(day, itemlist, cur_day=0):
        """ロングログインボーナス日付データ.
        """
        return {
            'day' : day,
            'itemlist' : itemlist,
            'rest' : day - cur_day,
        }
    
    @staticmethod
    def serialcampaign(handler, serialcodecampaignmaster):
        """シリアルコードキャンペーン.
        """
        return {
            'id' : serialcodecampaignmaster.id,
            'name' : serialcodecampaignmaster.name,
            'rtime' : serialcodecampaignmaster.rtime,
            'header' : handler.makeAppLinkUrlImg(serialcodecampaignmaster.header),
            'prize_img' : handler.makeAppLinkUrlImg(serialcodecampaignmaster.prize_img),
            'limit_pp' : serialcodecampaignmaster.limit_pp,
        }
    
    @staticmethod
    def eventmovie(handler, eventmoviemaster, moviemaster, viewdata, is_open):
        """イベント動画.
        """
        thumbUrl = None
        dataUrls = []
        flvUrl = ''
        if isinstance(moviemaster, MoviePlayList):
            thumbUrl = handler.makeAppLinkUrlMedia(Media.movie_thumbnail(moviemaster.filename))
            dataUrls.append(handler.makeAppLinkUrlMedia(Media.movie_m3u8(moviemaster.filename)))
            flvUrl = handler.makeAppLinkUrlMedia(Media.movie_flv(moviemaster.filename))
        elif isinstance(moviemaster, PcMoviePlayList):
            thumbUrl = handler.makeAppLinkUrlMedia(Media.movie_pc_thumbnail(moviemaster.filename))
            dataUrls.append(handler.makeAppLinkUrlMedia(Media.movie_m3u8(moviemaster.filename)))
            flvUrl = handler.makeAppLinkUrl(UrlMaker.movie_keyget(moviemaster.id))
        
        cnt = viewdata.getCountTotal() if viewdata else 0
        is_new = cnt < 1
        
        return {
            'id' : eventmoviemaster.id,
            'movieid' : moviemaster.id,
            'title' : eventmoviemaster.title,
            'cast' : eventmoviemaster.cast,
            'text' : eventmoviemaster.text,
            'thumbUrl' : thumbUrl,
            'dataUrl' : dataUrls,
            'flvUrl' : flvUrl,
            'is_new' : is_new,
            'is_open' : is_open,
            'cnt' : cnt,
        }
    
    @staticmethod
    def playerconfigdata(configdata, scoutskip):
        """プレイヤーのコンフィグ情報.
        """
        return {
            'scoutskip' : scoutskip,
            'autosell' : configdata.autosell_rarity,
        }
    
    @staticmethod
    def panelmission(handler, panelmaster, obj_mission_list, prizeinfo, is_cleared):
        """パネルミッション.
        """
        return {
            'id' : panelmaster.id,
            'name' : panelmaster.name,
            'image' : handler.makeAppLinkUrlImg(panelmaster.image) if panelmaster.image else None,
            'header' : handler.makeAppLinkUrlImg(panelmaster.header) if panelmaster.header else None,
            'rule' : handler.makeAppLinkUrlImg(panelmaster.rule) if panelmaster.rule else None,
            'missionlist' : obj_mission_list,
            'prize' : prizeinfo,
            'cleared' : is_cleared,
        }
    
    @staticmethod
    def panelmission_mission(handler, missionmaster, current_value, target_value, prizeinfo, is_received):
        """パネルミッションのミッション.
        """
        url = PanelMissionConditionExecuter().getJumpUrl(missionmaster)
        return {
            'id' : missionmaster.id,
            'name' : missionmaster.name,
            'panel' : missionmaster.panel,
            'number' : missionmaster.number,
            'image_pre' : handler.makeAppLinkUrlImg(missionmaster.image_pre),
            'image_post' : handler.makeAppLinkUrlImg(missionmaster.image_post),
            'prize' : prizeinfo,
            'cur_v' : current_value,
            'tar_v' : target_value,
            'cleared' : is_received or target_value <= current_value,
            'received' : is_received,
            'url' : handler.makeAppLinkUrl(url) if url else None,
            'condition_text' : missionmaster.condition_text,
        }
    
    @staticmethod
    def skillmaster(skillmaster):
        """スキル情報.
        """
        return {
            'id': skillmaster.id,
            'name' : skillmaster.name,
            'text' : skillmaster.text,
            'eskill': skillmaster.eskill,
        }
    
    @staticmethod
    def cabaclubstoremaster(handler, cabaclubstoremaster):
        """キャバクラ店舗マスター.
        """
        cabaclub_store_set = CabaclubStoreSet(cabaclubstoremaster, None)
        days_cost_items = cabaclub_store_set.get_rental_cost_dict().items()
        days_cost_items.sort()
        return dict(
            id = cabaclubstoremaster.id,
            name = cabaclubstoremaster.name,
            thumb = handler.makeAppLinkUrlImg(cabaclubstoremaster.thumb),
            customer_interval = cabaclubstoremaster.customer_interval,
            customer_max = cabaclubstoremaster.customer_max,
            cast_num_max = cabaclubstoremaster.cast_num_max,
            scoutman_num_max = cabaclubstoremaster.scoutman_num_max,
            scoutman_add_max = cabaclubstoremaster.scoutman_add_max,
            days_cost_items = days_cost_items,
            url_store = handler.makeAppLinkUrl(UrlMaker.cabaclubstore(cabaclubstoremaster.id)),
            url_rental = handler.makeAppLinkUrl(UrlMaker.cabaclubrentyesno(cabaclubstoremaster.id)),
        )
    
    @staticmethod
    def cabaclubstore(handler, cabaclub_store_set, now):
        """キャバクラ店舗.
        """
        playerdata = cabaclub_store_set.playerdata
        is_alive = cabaclub_store_set.is_alive(now)
        is_open = is_alive and playerdata.is_open
        ltime = cabaclub_store_set.get_limit_time()
        return dict(
            master = Objects.cabaclubstoremaster(handler, cabaclub_store_set.master),
            is_alive = is_alive,
            is_open = is_open,
            ltime = ltime,
            scoutman_add = playerdata.scoutman_add,
            proceeds = playerdata.proceeds,
            customer = playerdata.customer,
            event = Objects.cabaclubstoreevent(handler, cabaclub_store_set, now),
            url_open = handler.makeAppLinkUrl(UrlMaker.cabaclubopen(playerdata.mid)),
            url_close = handler.makeAppLinkUrl(UrlMaker.cabaclubclose(playerdata.mid)),
            url_cancel = handler.makeAppLinkUrl(UrlMaker.cabaclubcancelyesno(playerdata.mid)),
            rental_timelimit = Objects.timelimit(ltime, now),
        )
    
    @staticmethod
    def cabaclubstoreeventmaster(handler, cabaclubeventmaster):
        """キャバクラ店舗で発生するイベントのマスターデータ.
        """
        return dict(
            id = cabaclubeventmaster.id,
            name = cabaclubeventmaster.name,
            text = cabaclubeventmaster.text,
            thumb = handler.makeAppLinkUrlImg(cabaclubeventmaster.thumb),
            seconds = cabaclubeventmaster.seconds,
            customer_up = cabaclubeventmaster.customer_up,
            proceeds_up = cabaclubeventmaster.proceeds_up,
            ua_type = cabaclubeventmaster.ua_type,
            ua_value = cabaclubeventmaster.ua_value,
            ua_cost = cabaclubeventmaster.ua_cost,
            ua_text = cabaclubeventmaster.ua_text,
        )
    
    @staticmethod
    def cabaclubstoreevent(handler, cabaclub_store_set, now):
        """キャバクラ店舗で発生中のイベントデータ.
        """
        cabaclubeventmaster = cabaclub_store_set.get_current_eventmaster(now)
        if cabaclubeventmaster is None:
            return None
        endtime = cabaclub_store_set.get_event_endtime()
        if endtime <= now:
            return None
        return dict(
            master = Objects.cabaclubstoreeventmaster(handler, cabaclubeventmaster),
            endtime = endtime,
            ua_flag = cabaclub_store_set.playerdata.ua_flag,
            url_store = handler.makeAppLinkUrl(UrlMaker.cabaclubstore(cabaclub_store_set.master.id)),
            url_uayesno = handler.makeAppLinkUrl(UrlMaker.cabaclubuayesno(cabaclub_store_set.master.id)),
            timelimit = Objects.timelimit(endtime, now),
            customer_up = cabaclub_store_set.get_customer_up_by_event(),
            proceeds_up = cabaclub_store_set.get_proceeds_up_by_event(),
        )
    
    @staticmethod
    def cabaclubitemdata(handler, cabaclub_store_set, now):
        """キャバクラのアイテム情報.
        """
        data = dict()
        if cabaclub_store_set.itemdata:
            model_mgr = handler.getModelMgr()
            def make_data(iid, limittime):
                master = BackendApi.get_itemmaster(model_mgr, iid, using=settings.DB_READONLY) if iid else None
                return dict(master=Objects.itemmaster(handler, master), limittime=limittime, timelimit=Objects.timelimit(limittime, now))
            # 優待券配布.
            preferential_item_id = cabaclub_store_set.get_current_preferential_item_id(now)
            if preferential_item_id:
                data.update(preferential=make_data(preferential_item_id, cabaclub_store_set.itemdata.preferential_time))
            # バリア的なアイテム.
            barrier_item_id = cabaclub_store_set.get_current_barrier_item_id(now)
            if barrier_item_id:
                data.update(barrier=make_data(barrier_item_id, cabaclub_store_set.itemdata.barrier_time))
        return data
    
    @staticmethod
    def cabaclub_management_info(handler, scoredata=None, scoredata_weekly=None):
        """キャバクラの経営情報.
        """
        data = dict.fromkeys(('money', 'point', 'proceeds', 'customer', 'week'), 0)
        if scoredata:
            data.update(money=scoredata.money, point=scoredata.point)
        if scoredata_weekly:
            data.update(proceeds=scoredata_weekly.proceeds, customer=scoredata_weekly.customer,
                        week=scoredata_weekly.week)
        return data
    
    @staticmethod
    def titlemaster(handler, titlemaster):
        """称号マスター.
        """
        return dict(
            id = titlemaster.id,
            name = titlemaster.name,
            text = titlemaster.text,
            thumb = handler.makeAppLinkUrlImg('{}_01.png'.format(titlemaster.thumb)),
            mypage_thumb = handler.makeAppLinkUrlImg('{}_02.png'.format(titlemaster.thumb)),
            days = titlemaster.days,
            cost = titlemaster.cost,
            gold_up = titlemaster.gold_up,
            exp_up = titlemaster.exp_up,
            raidevent_point_up = titlemaster.raidevent_point_up,
            raidevent_power_up = titlemaster.raidevent_power_up,
            scoutevent_point_up = titlemaster.scoutevent_point_up,
            battleevent_point_up = titlemaster.battleevent_point_up,
            battleevent_power_up = titlemaster.battleevent_power_up,
            url_tradeyesno = handler.makeAppLinkUrl(UrlMaker.titleyesno(titlemaster.id)),
        )
    
    @staticmethod
    def title(handler, titlemaster, title, now=None):
        """称号.
        """
        now = now or OSAUtil.get_now()
        limittime = (title.stime + datetime.timedelta(days=titlemaster.days)) if title else now
        return dict(
            master = Objects.titlemaster(handler, titlemaster),
            limittime = limittime,
            timelimit = Objects.timelimit(limittime, now)
        )


class BackendApi:
    """データ操作をAPI的な感じに.
    """
    
    model_mgr = ModelRequestMgr()
    
    @staticmethod
    def get_model_list(model_mgr, model_cls, idlist, get_instance=False, using=settings.DB_DEFAULT):
        modellist = model_mgr.get_models(model_cls, idlist, get_instance=get_instance, using=using)
        return modellist
    @staticmethod
    def get_model_dict(model_mgr, model_cls, idlist, get_instance=False, using=settings.DB_DEFAULT, key=None):
        if key is None:
            key = lambda x:x.key()
        
        modellist = BackendApi.get_model_list(model_mgr, model_cls, idlist, get_instance=get_instance, using=using)
        return dict([(key(model), model) for model in modellist])
    @staticmethod
    def get_model(model_mgr, model_cls, modelid, get_instance=False, using=settings.DB_DEFAULT):
        return BackendApi.get_model_dict(model_mgr, model_cls, [modelid], get_instance=get_instance, using=using).get(modelid, None)
    
    #===========================================================
    # appconfig.
    @staticmethod
    def get_appconfig(model_mgr, using=settings.DB_DEFAULT):
        """アプリの設定モデルを取得.
        """
        model = BackendApi.get_model(model_mgr, AppConfig, AppConfig.SINGLE_ID, get_instance=False, using=using)
        if model is None:
            def tr():
                model_mgr = ModelRequestMgr()
                model = AppConfig.makeInstance(AppConfig.SINGLE_ID)
                model_mgr.set_save(model)
                return model_mgr, model
            tmp_model_mgr, model = db_util.run_in_transaction(tr)
            tmp_model_mgr.write_end()
            model_mgr.set_got_models([model])
        return model
    
    @staticmethod
    def update_appconfig(is_emergency, stime=None, etime=None, is_platform=False):
        """アプリの設定モデルを更新.
        """
        def tr():
            model_mgr = ModelRequestMgr()
            app_config = BackendApi.get_model(model_mgr, AppConfig, AppConfig.SINGLE_ID, get_instance=True)
            if is_emergency:
                if is_platform:
                    app_config.maintenancetype = Defines.MaintenanceType.EMERGENCY_PLATFORM
                else:
                    app_config.maintenancetype = Defines.MaintenanceType.EMERGENCY
            else:
                if is_platform:
                    app_config.maintenancetype = Defines.MaintenanceType.REGULAR_PLATFORM
                else:
                    app_config.maintenancetype = Defines.MaintenanceType.REGULAR
            app_config.stime = stime or app_config.stime
            app_config.etime = etime or app_config.etime
            model_mgr.set_save(app_config)
            model_mgr.write_all()
            return model_mgr, app_config
        model_mgr, app_config = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        return app_config
    
    #===========================================================
    # 事前登録.
    @staticmethod
    def get_preregistconfig(model_mgr, using=settings.DB_DEFAULT):
        """事前登録設定モデルを取得.
        """
        model = BackendApi.get_model(model_mgr, PreRegistConfig, PreRegistConfig.SINGLE_ID, get_instance=False, using=using)
        if model is None:
            def tr():
                model_mgr = ModelRequestMgr()
                model = PreRegistConfig.makeInstance(PreRegistConfig.SINGLE_ID)
                model_mgr.set_save(model)
                return model_mgr, model
            tmp_model_mgr, model = db_util.run_in_transaction(tr)
            tmp_model_mgr.write_end()
            model_mgr.set_got_models([model])
        return model
    
    #===========================================================
    # player.
    @staticmethod
    def get_players(apphandler, uidlist, clslist=None, using=settings.DB_DEFAULT, model_mgr=None, logger=None):
        """Player情報取得.
        """
        if not uidlist:
            return []
        elif clslist is None:
            clslist = ModelPlayer.Meta.MODELS
        
        if logger is None:
            logger = lambda x:None
        model_mgr = model_mgr or apphandler.getModelMgr()
        
        # 基本情報をまず取得.
        playerlist = model_mgr.get_models(Player, uidlist, False, using=using)
        
        modelplayerdict = {}
        for player in playerlist:
            modelplayerdict[player.id] = ModelPlayer([player])
        
        for model_cls in clslist:
            logger('get %s' % model_cls.__name__)
            for model in model_mgr.get_models(model_cls, modelplayerdict.keys(), False, using=using):
                modelplayerdict[model.id].setModel(model)
        return [modelplayerdict[uid] for uid in uidlist if modelplayerdict.has_key(uid)]
    
    @staticmethod
    def get_player(apphandler, uid, clslist=None, using=settings.DB_DEFAULT, model_mgr=None):
        """単体取得.
        """
        players = BackendApi.get_players(apphandler, [uid], clslist, using, model_mgr)
        if players:
            return players[0]
        else:
            return None
    
    @staticmethod
    def get_playerrequest(model_mgr, uid, using=settings.DB_DEFAULT):
        """確認キーだけ単体取得.
        """
        return BackendApi.get_model(model_mgr, PlayerRequest, uid, using=using)
    
    @staticmethod
    def get_dmmplayers(apphandler, playerlist, using=settings.DB_DEFAULT, do_execute=True):
        """DMMPlayer情報取得.
        """
        result = {}
        
        def callback(ret_data, reqkey, dmmid, result):
            try:
                person = ret_data[reqkey].get()
                if type(person) in (list, tuple):
                    person = person[0]
                result[dmmid] = person
            except:
                pass
        
        key_format = 'get_dmmplayer:%s:%s' % (OSAUtil.makeSessionID(), '%s')
        
        dmmidlist = [player.dmmid for player in playerlist]
        for dmmid in dmmidlist:
            data = PeopleRequestData.createForPeople(dmmid)
            request = apphandler.osa_util.makeApiRequest(ApiNames.People, data)
            reqkey = key_format % dmmid
            result[dmmid] = People.makeNotFound(dmmid)
            apphandler.addAppApiRequest(reqkey, request, callback, reqkey, dmmid, result)
        
        if do_execute:
            apphandler.execute_api()
        
        return result
    
    @staticmethod
    def dmmid_to_appuid(apphandler, dmmidlist, using=settings.DB_DEFAULT):
        """DMMIDをアプリ内IDに変換.
        """
        if len(dmmidlist) == 0:
            return {}
        redismodellist = DMMPlayerAssociate.fetch(dmmidlist)
        
        result = {}
        dbrequests = {}
        for redismodel in redismodellist:
            uid = redismodel.uid
            dmmid = redismodel.dmmid
            if uid is None:
                dbrequests[dmmid] = redismodel
            else:
                result[dmmid] = int(uid)
        
        req_num = len(dbrequests)
        if 0 < req_num:
            if req_num == 1:
                model = Player.getValues(filters={'dmmid':dbrequests.keys()[0]}, using=using)
                modellist = []
                if model:
                    modellist.append(model)
            else:
                modellist = Player.fetchValues(filters={'dmmid__in':dbrequests.keys()}, using=using)
            if apphandler:
                model_mgr = apphandler.getModelMgr()
                model_mgr.set_got_models(modellist)
            
            if 0 < len(modellist):
                updates = []
                for model in modellist:
                    redismodel = dbrequests[model.dmmid]
                    redismodel.uid = model.id
                    updates.append(redismodel)
                    result[model.dmmid] = model.id
                DMMPlayerAssociate.save_many(updates)
        return result
    
    @staticmethod
    def check_blacklist(apphandler, uid, oid, arg_model_mgr=None):
        """ブラックリストチェック.
        """
        model_mgr = arg_model_mgr or apphandler.getModelMgr()
        
        players = model_mgr.get_models(Player, [uid, oid], using=settings.DB_READONLY)
        dmmid0, dmmid1 = tuple([player.dmmid for player in players])
        
        keys = []
        for id0, id1 in [(dmmid1, dmmid0), (dmmid0, dmmid1)]:
            data = IgnorelistRequestData()
            data.guid = id0
            data.pid = id1
            request = apphandler.osa_util.makeApiRequest(ApiNames.Ignorelist, data)
            key = 'Ignorelist:%s:%s' % (id0, id1)
            apphandler.addAppApiRequest(key, request)
            keys.append(key)
        ret_data = apphandler.execute_api()
        try:
            for key in keys:
                datalist = ret_data[key].get()
                if datalist:
                    return False
        except:
            return False
        return True
    
    @staticmethod
    def get_profile_comment(apphandler, playerlist, arg_model_mgr=None, do_execute=True):
        """プロフィールコメントを取得.
        """
        comments = {}
        for player in playerlist:
            model = player.getModel(PlayerComment)
            if model is None:
                continue
            commentid = player.commentid
            if commentid:
                comments[commentid] = None
        
        if not comments:
            return comments
        
        data = InspectionGetRequestData()
        data.textId = comments.keys()
        request = apphandler.osa_util.makeApiRequest(ApiNames.InspectionGet, data)
        def cb(ret_data):
            try:
                datalist = ret_data['getProfileComment'].get()
            except:
                return
            for data in datalist:
                comments[data.textId] = data.data
        apphandler.addAppApiRequest('getProfileComment', request, cb)
        
        if do_execute:
            apphandler.execute_api()
        return comments
    
    @staticmethod
    def tr_add_gacha_pt(model_mgr, uid, point):
        """引抜ポイントを加算.
        """
        def forUpdateTask(model, inserted):
            if settings_sub.IS_BENCH:
                return
            
            v = model.gachapt + point
            if v < 0:
                raise CabaretError(u'引抜Ptが足りません', CabaretError.Code.NOT_ENOUGH)
            model.gachapt = min(v, Defines.VALUE_MAX_GACHA_PT)
        model_mgr.add_forupdate_task(PlayerGachaPt, uid, forUpdateTask)
    
    @staticmethod
    def tr_add_rareoverticket(model_mgr, uid, num):
        """レア以上チケットを加算.
        """
        def forUpdateTask(model, inserted):
            v = model.rareoverticket + num
            if v < 0:
                raise CabaretError(u'思い出チケットが足りません', CabaretError.Code.NOT_ENOUGH)
            model.rareoverticket = min(v, Defines.VALUE_MAX)
        model_mgr.add_forupdate_task(PlayerGachaPt, uid, forUpdateTask)
    
    @staticmethod
    def tr_add_memoriesticket(model_mgr, uid, num):
        """思い出チケットを加算.
        """
        def forUpdateTask(model, inserted):
            v = model.memoriesticket + num
            if v < 0:
                raise CabaretError(u'思い出チケットが足りません', CabaretError.Code.NOT_ENOUGH)
            model.memoriesticket = min(v, Defines.VALUE_MAX)
        model_mgr.add_forupdate_task(PlayerGachaPt, uid, forUpdateTask)
    
    @staticmethod
    def tr_add_tryluckticket(model_mgr, uid, num):
        """運試しチケットを加算.
        """
        def forUpdateTask(model, inserted):
            v = model.tryluckticket + num
            if v < 0:
                raise CabaretError(u'運試しチケットが足りません', CabaretError.Code.NOT_ENOUGH)
            model.tryluckticket = min(v, Defines.VALUE_MAX)
        model_mgr.add_forupdate_task(PlayerGachaPt, uid, forUpdateTask)
    
    @staticmethod
    def tr_add_gachaticket(model_mgr, uid, num):
        """引き抜きチケットを加算.
        """
        def forUpdateTask(model, inserted):
            v = model.gachaticket + num
            if v < 0:
                raise CabaretError(u'思い出チケットが足りません', CabaretError.Code.NOT_ENOUGH)
            model.gachaticket = min(v, Defines.VALUE_MAX)
        model_mgr.add_forupdate_task(PlayerGachaPt, uid, forUpdateTask)
    
    @staticmethod
    def tr_add_additional_gachaticket(model_mgr, uid, tickettype, num):
        """追加分引き抜きチケットを加算.
        """
        if not Defines.GachaConsumeType.GachaTicketType.NAMES.has_key(tickettype):
            raise CabaretError(u'未実装のチケットです', CabaretError.Code.ILLEGAL_ARGS)
        
        def forUpdateTask(model, inserted):
            v = model.num + num
            if v < 0:
                raise CabaretError(u'チケットが足りません', CabaretError.Code.NOT_ENOUGH)
            model.num = min(v, Defines.VALUE_MAX)
            UserLogTicketGet.create(model.uid, tickettype, model.num, num).save()
        model_mgr.add_forupdate_task(GachaTicket, GachaTicket.makeID(uid, tickettype), forUpdateTask)
    
    @staticmethod
    def tr_add_cabaretking_treasure(model_mgr, uid, num, before_num=None):
        """キャバ王の秘宝を加算.
        """
        def forUpdateTask(model, inserted):
            if before_num is not None and before_num != model.cabaretking:
                # すでに減らしてある.
                raise CabaretError(u'処理済みです', CabaretError.Code.ALREADY_RECEIVED)
            
            if 0 < num:
                total = model.get_cabaretking_num()
                if (num + total) < 0:
                    raise CabaretError(u'キャバ王の秘宝が足りません', CabaretError.Code.NOT_ENOUGH)
                model.cabaretking = min(model.cabaretking+num, Defines.VALUE_MAX)
            else:
                model.demiworld += num
                if model.demiworld < 0:
                    model.cabaretking += model.demiworld
                    model.demiworld = 0
        model_mgr.add_forupdate_task(PlayerTreasure, uid, forUpdateTask)
    
    @staticmethod
    def tr_add_demiworld_treasure(model_mgr, uid, num, before_num=None):
        """裏社会の秘宝を加算.
        """
        if num < 0:
            raise CabaretError(u'想定外のフローです.')
        
        def forUpdateTask(model, inserted):
            if before_num is not None and before_num != model.demiworld:
                # すでに減らしてある.
                raise CabaretError(u'処理済みです', CabaretError.Code.ALREADY_RECEIVED)
            
            v = model.demiworld + num
            model.demiworld = min(v, Defines.VALUE_MAX)
        model_mgr.add_forupdate_task(PlayerTreasure, uid, forUpdateTask)

    @staticmethod
    def tr_add_goldkey(model_mgr, uid, num):
        """金の鍵を加算.
        """
        def forUpdateTask(model, inserted):
            v = model.goldkey + num
            if v < 0:
                raise CabaretError(u'金の鍵が足りません', CabaretError.Code.NOT_ENOUGH)
            model.goldkey = min(v, Defines.VALUE_MAX)
        model_mgr.add_forupdate_task(PlayerKey, uid, forUpdateTask)
    
    @staticmethod
    def tr_add_silverkey(model_mgr, uid, num):
        """銀の鍵を加算.
        """
        def forUpdateTask(model, inserted):
            v = model.silverkey + num
            if v < 0:
                raise CabaretError(u'銀の鍵が足りません', CabaretError.Code.NOT_ENOUGH)
            model.silverkey = min(v, Defines.VALUE_MAX)
        model_mgr.add_forupdate_task(PlayerKey, uid, forUpdateTask)
    
    @staticmethod
    def tr_add_gold(model_mgr, uid, gold, notenough=False):
        """所持金を加算.
        """
        def forUpdateTask(model, inserted):
            if settings_sub.IS_BENCH:
                return
            v = model.gold + gold
            if v < 0 and not notenough:
                raise CabaretError(u'所持金が足りません', CabaretError.Code.NOT_ENOUGH)
            model.gold = max(0, min(v, Defines.VALUE_MAX))
        model_mgr.add_forupdate_task(PlayerGold, uid, forUpdateTask)
        
    @staticmethod
    def set_exp(model_mgr, player, exp, do_write=False, using=settings.DB_DEFAULT):
        """経験値を設定.
        """
        if do_write:
            player.exp = 0
            BackendApi.tr_add_exp(model_mgr, player, exp)
        else:
            level_pre = player.level
            levelexp = BackendApi.get_playerlevelexp_byexp(exp, model_mgr, using=using)
            if levelexp is None:
                raise CabaretError(u'プレイヤーの経験値テーブルがありません', CabaretError.Code.INVALID_MASTERDATA)
            elif level_pre != levelexp.level:
                # レベルが変わった.
                player.level = levelexp.level
                
                # ステータスを設定.
                if player.getModel(PlayerDeck):
                    player.hp = levelexp.hp
                    player.deckcapacitylv = levelexp.deckcapacity
                    player.cardlimitlv = levelexp.cardlimit
                if player.getModel(PlayerAp):
                    player.apmax = levelexp.ap
                    player.set_ap(player.apmax)
                    player.set_bp(player.bpmax)
                if player.getModel(PlayerFriend):
                    player.friendlimit = levelexp.friendlimit
                
                maxlevel = BackendApi.get_playermaxlevel(model_mgr, using=using)
                if maxlevel == levelexp.level:
                    # 最大レベル.
                    exp = levelexp.exp
                player.exp = exp
            elif player.exp != exp:
                player.exp = exp
            else:
                return
    
    @staticmethod
    def tr_add_exp(model_mgr, player, exp):
        """経験値を加算.
        """
        model = model_mgr.get_model(PlayerExp, player.id)
        player.setModel(model)
        
        level_pre = model.level
        v = model.exp + exp
        if settings_sub.IS_BENCH:
            levelexp = BackendApi.get_playerlevelexp_byexp(model.exp, model_mgr)
        else:
            levelexp = BackendApi.get_playerlevelexp_byexp(v, model_mgr)
        if levelexp is None:
            raise CabaretError(u'プレイヤーの経験値テーブルがありません', CabaretError.Code.INVALID_MASTERDATA)
        elif model.level != levelexp.level:
            # レベルが変わった.
            model.level = levelexp.level
            
            # ステータスを設定.
            playerdeck = model_mgr.get_model(PlayerDeck, player.id)
            playerap = model_mgr.get_model(PlayerAp, player.id)
            playerfriend = model_mgr.get_model(PlayerFriend, player.id)
            
            model.hp = levelexp.hp
            playerdeck.deckcapacitylv = levelexp.deckcapacity
            playerdeck.cardlimitlv = levelexp.cardlimit
            playerap.apmax = levelexp.ap
            playerfriend.friendlimit = levelexp.friendlimit
            
            player.setModel(playerdeck)
            player.setModel(playerap)
            player.setModel(playerfriend)
            
            # 行動力回復.
            player.set_ap(player.get_ap_max())
            player.set_bp(player.get_bp_max())
            
            model_mgr.set_save(playerdeck)
            model_mgr.set_save(playerap)
            model_mgr.set_save(playerfriend)
            
            maxlevel = BackendApi.get_playermaxlevel(model_mgr)
            if maxlevel == levelexp.level:
                # 最大レベル.
                v = levelexp.exp
            if not settings_sub.IS_BENCH:
                model.exp = v
            model_mgr.set_save(model)

            if PlayerCrossPromotion.is_session():
                if 20 <= player.level:
                    BackendApi.update_player_cross_promotion(model_mgr, player.id, 'is_level10', 'is_level20')
                elif 10 <= player.level:
                    BackendApi.update_player_cross_promotion(model_mgr, player.id, 'is_level10')
        elif model.exp != v:
            if not settings_sub.IS_BENCH:
                model.exp = v
            model_mgr.set_save(model)
        else:
            return
        
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            BackendApi.save_battle_levelset(player.id, player.level, pipe=pipe)
            if player.level != level_pre:
                LevelGroupSet.createByLevel(player.id, level_pre).delete(pipe)
                LevelSet.create(player.id, level_pre).delete(pipe)
            LevelGroupSet.createByLevel(player.id, player.level).save(pipe)
            LevelSet.create(player.id, player.level).save(pipe)
            pipe.execute()
            KpiOperator().set_save_playerlevel(player.id, player.level).save()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def tr_add_ap(model_mgr, player, ap, notenough=False):
        """体力を回復.
        """
        def forUpdateTask(model, inserted):
            player.setModel(model)
            
            apnow = player.get_ap()
            apmax = player.get_ap_max()
            appost = apnow + ap
            
            if appost < 0 and not notenough:
                raise CabaretError(u'体力が足りません', CabaretError.Code.NOT_ENOUGH)
            elif 0 < ap and apnow == apmax:
                raise CabaretError(u'これ以上回復できません', CabaretError.Code.OVER_LIMIT)
            
            appost = max(0, min(appost, apmax))
            player.set_ap(appost)
            
            model_mgr.set_save(model)
        
        model_mgr.add_forupdate_task(PlayerAp, player.id, forUpdateTask)
        
        def writeEnd():
            pass
        
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def tr_max_ap(model_mgr, player):
        """体力を全回復.
        """
        
        def forUpdateTask(model, inserted):
            player.setModel(model)
            
            ap = player.get_ap()
            apmax = player.get_ap_max()
            if ap < apmax:
                player.set_ap(apmax)
                player.aprtime = OSAUtil.get_now()
            else:
                raise CabaretError(u'既に回復済みです', CabaretError.Code.ALREADY_RECEIVED)
            
            model_mgr.set_save(model)
        
        model_mgr.add_forupdate_task(PlayerAp, player.id, forUpdateTask)
        
        def writeEnd():
            pass
        
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def tr_add_bp(model_mgr, player, bp, notenough=False):
        """気力を回復.
        """
        def forUpdateTask(model, inserted):
            player.setModel(model)
            
            bpnow = player.get_bp()
            bpmax = player.get_bp_max()
            bppost = bpnow + bp
            
            if not settings_sub.IS_BENCH:
                if bp < 0 and bppost < 0 and not notenough:
                    raise CabaretError(u'気力が足りません', CabaretError.Code.NOT_ENOUGH)
                elif 0 < bp and bpnow == bpmax:
                    raise CabaretError(u'これ以上回復できません', CabaretError.Code.OVER_LIMIT)
            
            bppost = max(0, min(bppost, bpmax))
            if not settings_sub.IS_BENCH:
                player.set_bp(bppost)
            
            model_mgr.set_save(model)
        
        model_mgr.add_forupdate_task(PlayerAp, player.id, forUpdateTask)
        
        def writeEnd():
            pass
        
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def tr_max_bp(model_mgr, player):
        """気力を全回復.
        """
        
        def forUpdateTask(model, inserted):
            player.setModel(model)
            
            bp = player.get_bp()
            bpmax = player.get_bp_max()
            if bp < bpmax:
                player.set_bp(bpmax)
                player.bprtime = OSAUtil.get_now()
            else:
                raise CabaretError(u'既に回復済みです', CabaretError.Code.ALREADY_RECEIVED)
            
            model_mgr.set_save(model)
        
        model_mgr.add_forupdate_task(PlayerAp, player.id, forUpdateTask)
        
        def writeEnd():
            pass
        
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def tr_add_card_limit(model_mgr, uid, num, is_lvup=True):
        """カード所持上限数を加算.
        """
        def forUpdateTask(model, inserted):
            
            if is_lvup == True:
                v = model.cardlimitlv + num
                if v < 0:
                    raise CabaretError(u'所属キャスト上限数が足りません', CabaretError.Code.NOT_ENOUGH)
                model.cardlimitlv = min(v, Defines.UNSIGNED_SMALL_INT_MAX)
            else:
                v = model.cardlimititem + num
                if v < 0:
                    raise CabaretError(u'所属キャスト上限数が足りません', CabaretError.Code.NOT_ENOUGH)
                elif Defines.CARDLIMITITEM_MAX < v:
                    raise CabaretError(u'これ以上拡張できません', CabaretError.Code.OVER_LIMIT)
                model.cardlimititem = min(v, Defines.UNSIGNED_SMALL_INT_MAX)
        model_mgr.add_forupdate_task(PlayerDeck, uid, forUpdateTask)
    
    @staticmethod
    def install(apphandler, arg_model_mgr=None, preregist=False):
        """アプリインストール.
        """
        if not apphandler.osa_util.viewer_id:
            raise CabaretError('Illegal viewer_id=%s' % apphandler.osa_util.viewer_id, CabaretError.Code.ILLEGAL_ARGS)
        
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        
        player = Player()
        player.dmmid = apphandler.osa_util.viewer_id
        player.preregist = preregist
        model_mgr.set_save(player)
        
        
        def writeEnd():
            KpiOperator().set_save_tutorialstate(player.id, Defines.TutorialStatus.REGIST_SELECT).save()
        model_mgr.add_write_end_method(writeEnd)
        
        # 保存.
        if arg_model_mgr is None:
            model_mgr.write_all()
            model_mgr.write_end()
        
        modelplayer = ModelPlayer([player])
        
        return modelplayer
    
    @staticmethod
    def tr_regist_player(model_mgr, uid, player_type):
        """ユーザー登録.
        """
        # PlayerRegistを確認.
        playerregist = PlayerRegist.getByKeyForUpdate(uid)
        if playerregist is not None:
            raise CabaretError('User is registered. uid=%s' % uid, CabaretError.Code.ALREADY_RECEIVED)
        
        # modelplayer.
        p = model_mgr.get_model(Player, uid)
        model_player = ModelPlayer([p])
        
        # levelexp.
        levelexpmaster = BackendApi.get_playerlevelexp_bylevel(1, model_mgr)
        if levelexpmaster is None:
            raise CabaretError(u'プレイヤーの経験値テーブルがありません', CabaretError.Code.INVALID_MASTERDATA)
        
        # Player作成.
        p = PlayerRegist(id=uid)
        p.ptype = player_type
        model_mgr.set_save(p)
        model_player.setModel(p)
        
        p = PlayerTutorial(id=uid)
        p.tutorialstate = Defines.TutorialStatus.REGIST_COMPLETE
        model_mgr.set_save(p)
        model_player.setModel(p)
        
        p = PlayerLogin(id=uid)
        model_mgr.set_save(p)
        model_player.setModel(p)
        
        p = PlayerCard(id=uid)
        model_mgr.set_save(p)
        model_player.setModel(p)
        
        # デッキ設定.
        p = PlayerExp(id=uid)
        p.exp = levelexpmaster.exp
        p.level = levelexpmaster.level
        p.hp = levelexpmaster.hp
        model_mgr.set_save(p)
        model_player.setModel(p)
        
        p = PlayerGold(id=uid)
        p.gold = 0
        model_mgr.set_save(p)
        model_player.setModel(p)
        
        p = PlayerFriend(id=uid)
        p.friendlimit = levelexpmaster.friendlimit
        model_mgr.set_save(p)
        model_player.setModel(p)
        
        p = PlayerAp(id=uid)
        p.apmax = levelexpmaster.ap
        model_player.setModel(p)
        model_player.set_ap(p.apmax)
        model_player.set_bp(p.bpmax)
        model_mgr.set_save(p)
        
        p = PlayerDeck(id=uid)
        p.deckcapacitylv = levelexpmaster.deckcapacity
        p.cardlimitlv = levelexpmaster.cardlimit
        model_mgr.set_save(p)
        model_player.setModel(p)
        
        p = PlayerGachaPt(id=uid)
        model_mgr.set_save(p)
        model_player.setModel(p)
        
        p = PlayerScout(id=uid)
        model_mgr.set_save(p)
        model_player.setModel(p)
        
        p = PlayerRequest(id=uid)
        model_mgr.set_save(p)
        model_player.setModel(p)
        
        p = PlayerLimitation(id=uid)
        model_mgr.set_save(p)
        
        # 初期デッキ.
        BackendApi.tr_add_defaultcard(model_mgr, model_player)
        
        def writeEnd():
            kpi = KpiOperator()
            kpi.set_save_tutorialstate(uid, Defines.TutorialStatus.REGIST_COMPLETE)
            kpi.set_save_playerlevel(uid, model_player.level)
            kpi.set_incrment_battlerankup_count(1)
            kpi.save()
        model_mgr.add_write_end_method(writeEnd)
        
        return model_player
    
    @staticmethod
    def tr_update_tutorialstate(model_mgr, uid, tutostate):
        """チュートリアルの状態を更新.
        """
        # PlayerTutorialを確認.
        playertutorial = PlayerTutorial.getByKeyForUpdate(uid)
        if playertutorial is None:
            raise CabaretError('User is not registered. uid=%s' % uid, CabaretError.Code.NOT_DATA)
        elif playertutorial.tutorialstate != tutostate:
            if playertutorial.tutorialstate == Defines.TutorialStatus.COMPLETED:
                raise CabaretError('already received. uid=%s' % uid, CabaretError.Code.ALREADY_RECEIVED)
            playertutorial.tutorialstate = tutostate
            model_mgr.set_save(playertutorial)
        
        def writeEnd():
            KpiOperator().set_save_tutorialstate(uid, tutostate).save()
        model_mgr.add_write_end_method(writeEnd)
        
        return playertutorial
    
    @staticmethod
    def tr_tutorialend(model_mgr, player, is_pc):
        """チュートリアル完了.
        """
        uid = player.id
        now = OSAUtil.get_now()
        
        # PlayerTutorialを確認.
        playertutorial = BackendApi.tr_update_tutorialstate(model_mgr, uid, Defines.TutorialStatus.COMPLETED)
        playertutorial.etime = now
        
        # modelplayer.
        plist = [model_mgr.get_model(model_cls, uid, using=settings.DB_DEFAULT) for model_cls in (Player, PlayerExp, PlayerDeck, PlayerRegist)]
        plist.append(playertutorial)
        model_player = ModelPlayer(plist)
        
        p = PlayerTreasure(id=uid)
        model_mgr.set_save(p)
        model_player.setModel(p)
        
        p = PlayerHappening(id=uid)
        model_mgr.set_save(p)
        model_player.setModel(p)
        
        p = PlayerKey(id=uid)
        model_mgr.set_save(p)
        model_player.setModel(p)
        
        ptype = model_player.ptype
        # ハメ管理合成.
        deck = BackendApi.get_deck(uid, model_mgr)
        leader = BackendApi.get_cards([deck.leader], model_mgr, forupdate=True)[0]
        evol_materialcard = BackendApi.get_tutorialevolution_material(model_mgr, uid)
        leader, evol_masterlist = BackendApi.tutorial_evolution(model_mgr, leader, evol_materialcard)
        
        # スカウトで手に入れたお金と経験値.
        gold, exp = BackendApi.get_tutorial_scoutresult(model_mgr, ptype, len(Defines.TutorialStatus.SCOUT_CHAPTERS))
        
        # 宝箱.
#        treasure = BackendApi.get_tutorial_treasure(model_mgr, ptype)
#        BackendApi.tr_add_treasure(model_mgr, uid, Defines.TreasureType.TUTORIAL_TREASURETYPE, treasure.id)
        
        # スカウトクリア.
        scout = BackendApi.get_tutorial_scout(model_mgr, ptype)
        model_player.deckcapacityscout += 1
        model_mgr.set_save(model_player.getModel(PlayerDeck))
        
        # プレイデータの書き込み.
        playdata = ScoutPlayData.makeInstance(ScoutPlayData.makeID(uid, scout.id))
        playdata.progress = scout.execution
        model_mgr.set_save(playdata)
        
        # 教育.
        materialcard = BackendApi.get_tutorialcomposition_material(model_mgr, ptype)
        BackendApi.composition(model_mgr, leader, [materialcard], False)
        
        # カード取得フラグ.
        for evol_master in evol_masterlist:
            BackendApi.tr_set_cardacquisition(model_mgr, uid, evol_master, level=evol_master.maxlevel)
        
        # エリアクリア状態に.
        area = BackendApi.get_tutorial_area(model_mgr, ptype)
        BackendApi.tr_area_clear(model_mgr, model_player, area)
        
        # 報酬.
        prizelist = BackendApi.get_tutorial_prizelist(model_mgr, ptype)
        BackendApi.tr_add_prize(model_mgr, uid, prizelist, Defines.TextMasterID.TUTORIAL_END)
        
        # 事前登録報酬.
        if player.preregist:
            preregist = BackendApi.get_preregistconfig(model_mgr)
            prizelist = BackendApi.get_prizelist(model_mgr, preregist.prizes)
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, Defines.TextMasterID.PREREGIST)
        
        # 招待報酬.
        flag_invite = False
        invitedata = model_mgr.get_model(InviteData, player.dmmid, using=settings.DB_DEFAULT)
        if invitedata:
            if invitedata.state is not Defines.InviteState.ACCEPT:
                invitedata.state = Defines.InviteState.ACCEPT
                model_mgr.set_save(invitedata)
                
                prizes = None
                invitemaster = BackendApi.get_current_invitemaster(model_mgr, using=settings.DB_READONLY, now=now)
                if invitemaster:
                    cnt = BackendApi.add_invite_cnt(model_mgr, invitedata.fid, invitemaster.id)
                    prizes = BackendApi.get_invite_prizes(invitemaster, cnt)
                
                if prizes:
                    prizelist = BackendApi.get_prizelist(model_mgr, prizes)
                    BackendApi.tr_add_prize(model_mgr, invitedata.fid, prizelist, Defines.TextMasterID.INVITE)
                flag_invite = True
        
        BackendApi.tr_add_exp(model_mgr, model_player, exp)
        BackendApi.tr_add_gold(model_mgr, uid, gold, notenough=True)
        model_mgr.set_save(leader.card)
        
        BackendApi.tr_updatelogintime(model_mgr, model_player, is_pc)
        
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            BackendApi.save_cardidset(leader, deck=deck, pipe=pipe)
            pipe.execute()
            
            kpi_operator = KpiOperator()
            kpi_operator.set_save_tutorialstate(uid, Defines.TutorialStatus.COMPLETED, now=now)
            if flag_invite:
                kpi_operator.set_increment_invite_tutoend_count(now=now)
            kpi_operator.save()
        model_mgr.add_write_end_method(writeEnd)
        
        return model_player

    @staticmethod
    def tr_add_platinum_piece(model_mgr, uid, num):
        def forUpdateTask(model, inserted):
            v = model.count + num
            if v < 0:
                raise CabaretError(u'プラチナの欠片の数がマイナスです', CabaretError.Code.NOT_ENOUGH)
            model.count = min(v, Defines.VALUE_MAX)
        model_mgr.add_forupdate_task(PlayerPlatinumPiece, uid, forUpdateTask)
    
    @staticmethod
    def get_platinum_piece(model_mgr, uid):
        player_platinumpiece = model_mgr.get_model(PlayerPlatinumPiece, uid)
        if player_platinumpiece:
            return player_platinumpiece.count
        else:
            return 0

    @staticmethod
    def tr_add_crystal_piece(model_mgr, uid, num):
        def forUpdateTask(model, inserted):
            v = model.count + num
            if v < 0:
                raise CabaretError(u'クリスタルの欠片の数がマイナスです', CabaretError.Code.NOT_ENOUGH)
            model.count = min(v, Defines.VALUE_MAX)
        model_mgr.add_forupdate_task(PlayerCrystalPiece, uid, forUpdateTask)

    @staticmethod
    def get_crystal_piece(model_mgr, uid):
        player_crystalpiece = model_mgr.get_model(PlayerCrystalPiece, uid)
        if player_crystalpiece:
            return player_crystalpiece.count
        return 0

    @staticmethod
    def tr_add_battle_ticket(model_mgr, uid, num):
        """add/remove the players' battle ticket amount
        """
        battle_ticket_id = GachaTicket.makeID(uid, Defines.GachaConsumeType.GachaTicketType.BATTLE_TICKET)

        def forUpdateTask(model, inserted):
            v = model.num + num
            if v < 0:
                raise CabaretError(u'バトルチケットの数がマイナスです', CabaretError.Code.NOT_ENOUGH)
            model.num = min(v, Defines.VALUE_MAX)
        model_mgr.add_forupdate_task(GachaTicket, battle_ticket_id, forUpdateTask)


    @staticmethod
    def get_battle_ticket(model_mgr, uid):
        #player_battleticket = model_mgr.get_model(PlayerBattleTicket, uid)
        #if player_battleticket:
        #    return player_battleticket.count
        #else:
        #    return 0
        return 0

    @staticmethod
    def tr_update_requestkey(model_mgr, uid, confirmkey, force=False):
        """書き込みリクエストの確認キーを更新.
        """
        playerrequest = PlayerRequest.getByKeyForUpdate(uid)
        if playerrequest is None:
            raise CabaretError(u'プレイヤーが存在しません', CabaretError.Code.NOT_REGISTERD)
        elif force or settings_sub.IS_BENCH:
            pass
        elif playerrequest.req_alreadykey == confirmkey:
            model_mgr.delete_models_from_cache(PlayerRequest, [uid])
            raise CabaretError(u'書き込み済みです', CabaretError.Code.ALREADY_RECEIVED)
        elif playerrequest.req_confirmkey != confirmkey:
            model_mgr.delete_models_from_cache(PlayerRequest, [uid])
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
        
        if not settings_sub.IS_BENCH:
            playerrequest.req_alreadykey = playerrequest.req_confirmkey
            playerrequest.req_confirmkey = OSAUtil.makeSessionID()
        
        model_mgr.set_got_models_forupdate([playerrequest])
        model_mgr.set_got_models([playerrequest])
        model_mgr.set_save(playerrequest)
        
        return playerrequest
    
    @staticmethod
    def save_weeklylogin(uid, is_pc, now=None):
        """一週間のログインを記録.
        """
        ope = KpiOperator()
        ope.set_save_weeklylogin(uid, is_pc, now)
        ope.save()
    
    @staticmethod
    def tr_updatelogintime(model_mgr, v_player, is_pc, now=None):
        """最終ログイン時間の更新.
        """
        playerlogin = v_player.getModel(PlayerLogin)
        if playerlogin is None:
            playerlogin = model_mgr.get_model(PlayerLogin, v_player.id)
            v_player.setModel(playerlogin)
        
        playerexp = v_player.getModel(PlayerExp)
        if playerexp is None:
            playerexp = model_mgr.get_model(PlayerExp, v_player.id)
            v_player.setModel(playerexp)
        
        # ログイン時間の更新.
        playerlogin.ltime = now or OSAUtil.get_now()
        model_mgr.set_save(playerlogin)

        BackendApi.cache_battleevent_userdata(model_mgr, v_player.id)
        
        def writeEnd():
            # 検索用にzsetに追加.
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            LevelGroupSet.createByLevel(v_player.id, v_player.level).save(pipe)
            LevelSet.create(v_player.id, v_player.level).save(pipe)
            LoginTimeSet.create(v_player.id, v_player.ltime).save(pipe)
            BackendApi.save_battle_levelset(v_player.id, v_player.level, pipe=pipe)
            pipe.execute()
            
            ope = KpiOperator()
            ope.set_save_playerlevel(v_player.id, v_player.level)
            ope.set_save_weeklylogin(v_player.id, is_pc, now)
            ope.save()
            
        model_mgr.add_write_end_method(writeEnd)

    @staticmethod
    def serch_playerid_bylevelgroup(levelgroup, limit=10, ignorelist=None, arg_model_mgr=None):
        """レベル帯指定でプレイヤーを検索.
        """
        ignorelist = ignorelist or []
        ignoreset = set(ignorelist)
        
        if not LevelGroupSet.exists(levelgroup):
            return []
        
        tmp = set([])
        # 範囲内のレコード数.
        nummax = LevelGroupSet.recordnum(levelgroup)
        
        result = []
        
        zero_cnt_max = 20
        while len(tmp) < nummax and len(result) < limit and 0 < zero_cnt_max:
            arr_set = set([int(model.uid) for model in LevelGroupSet.fetch_random(levelgroup, limit)])
            tmp |= arr_set
            arr = list((arr_set - ignoreset) - set(result))
            if len(arr) == 0:
                zero_cnt_max -= 1
            else:
                result.extend(arr)
        return result
    
    @staticmethod
    def serch_playerid_bylevel(level_min, level_max, limit=10, ignorelist=None, arg_model_mgr=None):
        """レベル指定でプレイヤーを検索.
        """
        ignorelist = ignorelist or []
        ignoreset = set(ignorelist)
        
        candidate = []
        for lv in xrange(level_min, level_max+1):
            if not LevelSet.exists(lv):
                continue
            arr_set = set([int(model.uid) for model in LevelSet.fetch_random(lv, limit)])
            candidate.extend(list(arr_set - ignoreset))
        
        indexes = range(len(candidate))
        result = []
        rand = AppRandom()
        for _ in xrange(min(limit, len(candidate))):
            idx = indexes.pop(rand.getIntN(len(indexes)))
            result.append(candidate[idx])
        return result
    
    @staticmethod
    def tr_delete_player(model_mgr, uid):
        """プレイヤーの削除.
        """
        player = Player.getByKey(uid)
        if player is None:
            return
        
        model_player = ModelPlayer([player])
        model_player.setModel(PlayerExp.getByKey(uid))
        
        friendlist = Friend.fetchValues(filters={'uid':uid})
        if friendlist:
            raise CabaretError(u'フレンドの削除を行っていない')
        
        model_mgr.set_delete(player)
        
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            delete_by_user_from_redisdb(model_player)
            delete_by_user_redisbattleevent(model_player)
            for raidevent in model_mgr.get_mastermodel_all(RaidEventMaster, using=settings.DB_READONLY):
                delete_raidevent(raidevent.id, uid, pipe)
            for scoutevent in model_mgr.get_mastermodel_all(ScoutEventMaster, using=settings.DB_READONLY):
                delete_scoutevent(scoutevent.id, uid, pipe)
            for battleevent in model_mgr.get_mastermodel_all(BattleEventMaster, using=settings.DB_READONLY):
                delete_battleevent(battleevent.id, uid, pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def tr_delete_friend_all(model_mgr, uid):
        """フレンドを削除.
        """
        # フレンド.
        friendlist = Friend.fetchValues(filters={'uid':uid})
        for friend in friendlist:
            if friend.state == Defines.FriendState.ACCEPT:
                BackendApi.tr_delete_friend(model_mgr, friend.uid, friend.fid)
            elif friend.state == Defines.FriendState.SEND:
                BackendApi.tr_delete_friendrequest(model_mgr, friend.uid, friend.fid)
            elif friend.state == Defines.FriendState.RECEIVE:
                BackendApi.tr_delete_friendrequest(model_mgr, friend.fid, friend.uid)
    
    @staticmethod
    def check_player_ban(model_mgr, uid, using=settings.DB_DEFAULT, handler=None):
        """停止中のアカウントかをチェック.
        プレイ可能->True, 停止中->False.
        """
        if handler:
            addloginfo = lambda x:handler.addloginfo(x)
        else:
            addloginfo = lambda x:None
        
        model = model_mgr.get_model(PlayerLimitation, uid, using=using)
        addloginfo('get PlayerLimitation')
        if model is None:
            BackendApi.update_player_ban([uid], False)
            addloginfo('update_player_ban')
            return True
        else:
            return not model.ban
    
    @staticmethod
    def update_player_ban(uidlist, ban):
        """アカウント停止フラグの更新.
        """
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.ban = ban
            for uid in uidlist:
                model_mgr.add_forupdate_task(PlayerLimitation, uid, forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
    
    @staticmethod
    def get_playerlimitation_list(model_mgr, ban=True, using=settings.DB_DEFAULT):
        """プレイヤーの制限レコードを取得.
        """
        return PlayerLimitation.fetchValues(filters={'ban':ban}, using=using)
    
    #===========================================================
    # バトル.
    @staticmethod
    def get_battleKOs(uid, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """戦歴を取得.
        """
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        
        win = model_mgr.get_model(BattleWin, uid, True, using=using).win
        lose = model_mgr.get_model(BattleLose, uid, True, using=using).lose
        win_receive = model_mgr.get_model(BattleReceiveWin, uid, True, using=using).win
        lose_receive = model_mgr.get_model(BattleReceiveLose, uid, True, using=using).lose
        
        return {
            'win' : win,
            'lose' : lose,
            'win_receive' : win_receive,
            'lose_receive' : lose_receive,
            'win_total' : win + win_receive,
            'lose_total' : lose + lose_receive,
        }
    
    @staticmethod
    def save_battle_levelset(uid, level, pipe=None):
        """バトル用のレベルごとのユーザーのセットに保存.
        """
        BattleLevelSet.create(uid, level).save(pipe)
    
    @staticmethod
    def get_battleopponents_by_levelband(level, num=1, excludes=None):
        """レベル帯で対戦相手を検索.
        """
        excludes = excludes or []
        arr = None
        lv = level
        while not arr:
            level_min, level_max = BackendApi.get_battle_saferange(lv)
            arr = BattleLevelSet.fetchRandom(num, level_min, level_max, excludes)
            if lv <= 1:
                break
            lv = level_min
        if arr:
            return [model.uid for model in arr]
        else:
            return None
    
    @staticmethod
    def get_battle_saferange(level):
        leveldiff_safe = 0
        if 0 < level <= 20:
            leveldiff_safe = 5
        elif 20 < level <= 30:
            leveldiff_safe = 7
        else:
            leveldiff_safe = 10
        return max(level - leveldiff_safe, 1), level + leveldiff_safe
    
    @staticmethod
    def get_friendcandidate_range(level):
        leveldiff_safe = 0
        if 0 < level <= 20:
            leveldiff_safe = 5
        elif 20 < level <= 30:
            leveldiff_safe = 7
        elif 30 < level <= 40:
            leveldiff_safe = 10
        elif 40 < level <= 50:
            leveldiff_safe = 15
        elif 50 < level <= 70:
            leveldiff_safe = 20
        elif 70 < level <= 100:
            leveldiff_safe = 25
        else:
            leveldiff_safe = 30
        return max(level - leveldiff_safe, 1), level + leveldiff_safe
    
    @staticmethod
    def get_battle_goldkey_rate(model_mgr, battleplayer, rankmaster, using=settings.DB_DEFAULT):
        """金の鍵の出現率.
        """
        if BackendApi.check_rankup_battle(model_mgr, battleplayer, rankmaster, using=using):
            win_continuity = rankmaster.win
        else:
            win_continuity = min(max(battleplayer.win_continuity, 0), rankmaster.win)
        return min(100, max(0, rankmaster.goldkeyrate_base + rankmaster.goldkeyrate_up * win_continuity))
    
    @staticmethod
    def get_battle_silverkey_rate(model_mgr, battleplayer, rankmaster, using=settings.DB_DEFAULT):
        """銀の鍵の出現率.
        """
        if BackendApi.check_rankup_battle(model_mgr, battleplayer, rankmaster, using=using):
            return 100
        else:
            return rankmaster.silverkeyrate
    
    @staticmethod
    def get_battle_feverrate(cardset):
        """フィーバーの確率を取得.
        """
        return Defines.Rarity.FEVER_RATE.get(cardset.master.rare, 0)
    
    @staticmethod
    def get_battle_fever_powerup_rate(cardset):
        """フィーバーの接客力上昇率を取得.
        """
        return Defines.Rarity.FEVER_POWERUP_RATE.get(cardset.master.rare, 0)
    
    @staticmethod
    def update_battle_lp_vtime(uid, now=None):
        """バトルのLPの閲覧時間を更新.
        """
        now = now or OSAUtil.get_now()
        def tr():
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                model.lpvtime = now
            model_mgr.add_forupdate_task(BattlePlayer, uid, forUpdate)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
    
    @staticmethod
    def battle(v_player, v_deck_cardlist, o_player, o_deck_cardlist, rand, eventmaster=None, title_effect=0):
        """バトル実行.
        """
        specialtype = None
        specialtable = None
        specialcard = None
        effect_getter = None
        if eventmaster:
            specialtype = eventmaster.specialtype
            specialtable = dict(eventmaster.specialtable)
            specialcard = dict(eventmaster.specialcard)
            effect_getter = lambda x:x[0] if x else None
        
        # 接客力.
        v_power, o_power, _, _, _, o_power_default, v_skillinfolist, o_skillinfolist, _, v_sp_powup, o_sp_powup, v_spt_powup, o_spt_powup, _, _ = BattleUtil.calcTeamPower(v_deck_cardlist, o_deck_cardlist, rand, specialcard=specialcard, specialtype=specialtype, specialtable=specialtable, effect_getter=effect_getter, v_title_effect=title_effect)
        
        # フィーバー.
        leader = v_deck_cardlist[0]
        fever = rand.getIntN(1000) < BackendApi.get_battle_feverrate(leader)
        fever_powerup_rate = 100
        if fever:
            fever_powerup_rate = BackendApi.get_battle_fever_powerup_rate(leader)
            v_power = v_power * fever_powerup_rate / 100
        
        # アニメーション用のパラメータ.
        animdata = BattleAnimParam.create(v_power, o_power, v_deck_cardlist, o_deck_cardlist, v_skillinfolist, o_skillinfolist, fever)
        
        data = {
            'is_win' : o_power <= v_power,
            'v_power' : v_power,
            'o_power' : o_power,
            'fever' : fever,
            'fever_powerup_rate' : fever_powerup_rate,
            'v_sp_powup' : v_sp_powup or 0,
            'o_sp_powup' : o_sp_powup or 0,
            'v_spt_powup' : v_spt_powup or 0,
            'o_spt_powup' : o_spt_powup or 0,
            'v_cost' : sum([card.master.cost for card in v_deck_cardlist]),
            'o_cost' : sum([card.master.cost for card in o_deck_cardlist]),
            'o_power_default' : o_power_default,
        }
        return data, animdata
    
    @staticmethod
    def tr_battle(model_mgr, v_player, o_player, v_cardidlist, o_cardidlist, battledata, battleid):
        """バトル実行.
        """
        now = OSAUtil.get_now()
        
        data, animdata = battledata
        
        is_win = data['is_win']
        resultdata = {}
        resultdata.update(data)
        
        # プレイヤーのバトル情報.
        battleplayer = model_mgr.get_model_forupdate(BattlePlayer, v_player.id)
        if battleplayer is None:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        elif battleplayer.result != battleid:
            raise CabaretError(u'結果を書き込み済みです', CabaretError.Code.ALREADY_RECEIVED)
        
        # 前回の結果を消しておく.
        if battleplayer.result:
            battleresult = model_mgr.get_model(BattleResult, battleplayer.result)
            if battleresult:
                model_mgr.set_delete(battleresult)
        
        # 現在のランク.
        rankmaster = BackendApi.get_battlerank(model_mgr, battleplayer.rank)
        
        result_code = None
        prizes = None
        prize_textid = 0
        rankup = False
        norma_comp = False
        
        rand = AppRandom()
        
        # ミッション.
        mission_executer = PanelMissionConditionExecuter()
        # バトル実行達成を登録.
        mission_executer.addTargetDoBattle()
        
        crosspromotion_targetfields = ["is_battle"]
        if is_win:
            if 1 <= battleplayer.win_continuity:
                crosspromotion_targetfields.append("is_battle_win_continue")
            
            result_code = Defines.BattleResultCode.WIN
            
            # 勝敗数.
            winrecord = model_mgr.get_model(BattleWin, v_player.id, get_instance=True)
            winrecord.win += 1
            model_mgr.set_save(winrecord)
            
            def forUpdateLose(model, inserted):
                model.lose += 1
            model_mgr.add_forupdate_task(BattleReceiveLose, o_player.id, forUpdateLose)
            
            # 鍵.
            goldkeyrate = BackendApi.get_battle_goldkey_rate(model_mgr, battleplayer, rankmaster)
            silverkeyrate = BackendApi.get_battle_silverkey_rate(model_mgr, battleplayer, rankmaster)
            v = rand.getIntN(100)
            
            if v < goldkeyrate:
                # 金の鍵獲得.
                BackendApi.tr_add_goldkey(model_mgr, v_player.id, 1)
                resultdata['goldkey'] = True
            else:
                v -= goldkeyrate
                if v < silverkeyrate:
                    # 銀の鍵.
                    BackendApi.tr_add_silverkey(model_mgr, v_player.id, 1)
                    resultdata['silverkey'] = True
            
            # 連勝数.
            rankup, norma_comp = BackendApi.add_battle_continuity_winnum(model_mgr, battleplayer)
            resultdata.update(rankup=rankup, norma_comp=norma_comp, win=battleplayer.win_continuity)
            
            if rankup:
                # ランクアップ報酬.
                prizes = rankmaster.select_rankupprize(rand)
                prize_textid = Defines.TextMasterID.BATTLE_RANKUP
                # ランクアップ達成を登録.
                mission_executer.addTargetBattleRankUp(battleplayer.rank)

                if PlayerCrossPromotion.is_session() and 5 <= battleplayer.rank:
                    crosspromotion_targetfields.append("is_battle_rank5")
            else:
                # 勝利報酬.
                prizes = rankmaster.select_winprize(rand)
                prize_textid = Defines.TextMasterID.BATTLE_WIN
            
        else:
            result_code = Defines.BattleResultCode.LOSE
            
            # 勝敗数.
            loserecord = model_mgr.get_model(BattleLose, v_player.id, get_instance=True)
            loserecord.lose += 1
            model_mgr.set_save(loserecord)
            
            def forUpdateWin(model, inserted):
                model.win += 1
            model_mgr.add_forupdate_task(BattleReceiveWin, o_player.id, forUpdateWin)
            
            # 連勝数.
            BackendApi.reset_battle_continuity_winnum(battleplayer, do_reset_rankopplist=False)
            # 敗北報酬.
            prizes = rankmaster.select_loseprize(rand)
            prize_textid = Defines.TextMasterID.BATTLE_LOSE

        BackendApi.update_player_cross_promotion(model_mgr, v_player.id, *crosspromotion_targetfields)

        # 報酬を付与.
        if prizes:
            prizelist = BackendApi.get_prizelist(model_mgr, prizes)
            BackendApi.tr_add_prize(model_mgr, v_player.id, prizelist, prize_textid, auto_receive=True)
            resultdata['prizes'] = prizes
        
        exp = max(1, int(o_player.level - math.ceil(v_player.level / 2.0)))
        
        # カードへの経験値.
        levelupcard = {}
        cardlist = BackendApi.get_cards(v_cardidlist, model_mgr, forupdate=True)
        for cardset in cardlist:
            _, level_add = BackendApi.tr_add_cardexp(model_mgr, cardset, exp)
            if 0 < level_add:
                levelupcard[cardset.id] = level_add
        
        # バトル結果.
        ins = BattleResult()
        ins.uid = v_player.id
        ins.oid = o_player.id
        ins.result = result_code
        ins.levelupcard = levelupcard
        ins.data = resultdata
        ins.anim = animdata
        ins.save()
        
        # 結果保存.
        battleplayer.result = ins.id
        model_mgr.set_save(battleplayer)
        
        # ミッション達成書き込み.
        BackendApi.tr_complete_panelmission(model_mgr, v_player.id, mission_executer, now)
        
        # 行動力.
        def forUpdatePlayerAp(model, inserted):
            v_player.setModel(model)
            if v_player.get_bp() < rankmaster.bpcost:
                raise CabaretError(u'行動力が足りません', CabaretError.Code.NOT_ENOUGH)
            v_player.add_bp(-rankmaster.bpcost)
        model_mgr.add_forupdate_task(PlayerAp, v_player.id, forUpdatePlayerAp)
        
        # 書き込み後のタスク.
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            
            deck = Deck()   # 自分のデッキ固定.
            deck.set_from_array(v_cardidlist)
            for cardset in cardlist:
                BackendApi.save_cardidset(cardset, deck, pipe)
            pipe.execute()
            
            now = OSAUtil.get_now()
            kpi = KpiOperator()
            kpi.set_incrment_battleplay_count(rankmaster.id, now)
            if rankup:
                kpi.set_incrment_battlerankup_count(battleplayer.rank, now)
            kpi.save()
        
        model_mgr.add_write_end_method(writeEnd)
        
        return ins
    
    @staticmethod
    def get_battleplayer(model_mgr, uid, get_instance=False, using=settings.DB_DEFAULT):
        return model_mgr.get_model(BattlePlayer, uid, get_instance=get_instance, using=using)
    
    @staticmethod
    def get_battleresult(model_mgr, uid, using=settings.DB_DEFAULT):
        battleplayer = BackendApi.get_battleplayer(model_mgr, uid, using)
        if battleplayer.result:
            return model_mgr.get_model(BattleResult, battleplayer.result, using=using)
        else:
            return None
    
    @staticmethod
    def get_battlerecord(model_mgr, battleidlist, using=settings.DB_DEFAULT):
        records = model_mgr.get_models(BattleResult, battleidlist, using=using)
        return records
    
    @staticmethod
    def get_battlerank(model_mgr, rank, using=settings.DB_DEFAULT):
        """ランクを取得.
        """
        return model_mgr.get_model(BattleRankMaster, rank, using=using)
    
    @staticmethod
    def get_battlerank_max(model_mgr, using=settings.DB_DEFAULT):
        """ランクの最大値を取得.
        """
        return model_mgr.get_mastermodel_count(BattleRankMaster, using=using)
    
    @staticmethod
    def add_battle_continuity_winnum(model_mgr, battleplayer, cnt=1, using=settings.DB_DEFAULT):
        """連勝数をカウントアップ.
        """
        rankmax = BackendApi.get_battlerank_max(model_mgr, using=using)
        
        rankup = False
        norma_comp = False
        if battleplayer.rank < rankmax:
            # 最大ランクじゃない.
            rankmaster = BackendApi.get_battlerank(model_mgr, battleplayer.rank, using=using)
            if BackendApi.check_rankup_battle(model_mgr, battleplayer, rankmaster, using=using):
                # ランクアップ.
                BackendApi.reset_battle_continuity_winnum(battleplayer, do_reset_times=True)
                battleplayer.rank += 1
                rankup = True
            else:
                battleplayer.win_continuity += 1
                if rankmaster.win <= battleplayer.win_continuity:
                    BackendApi.reset_battle_continuity_winnum(battleplayer, do_reset_change_cnt=False, do_reset_rankopplist=False)
                    battleplayer.times += 1
                    norma_comp = True
                else:
                    battleplayer.opponent = 0
        else:
            BackendApi.reset_battle_continuity_winnum(battleplayer, do_reset_times=True)
        return rankup, norma_comp
    
    @staticmethod
    def reset_battle_continuity_winnum(battleplayer, do_reset_times=False, do_reset_change_cnt=True, do_reset_rankopplist=True):
        """連勝数をリセット.
        """
        battleplayer.win_continuity = 0
        if do_reset_times:
            battleplayer.times = 0
        
        # 対戦相手変更回数もリセット.
        battleplayer.opponent = 0
        if do_reset_change_cnt:
            battleplayer.change_cnt = 0
        if do_reset_rankopplist:
            battleplayer.rankopplist = []
    
    @staticmethod
    def check_rankup_battle(model_mgr, battleplayer, rankmaster, using=settings.DB_DEFAULT):
        """ランクアップ戦チェック.
        """
        if battleplayer.times < rankmaster.times:
            return False
        rankmax = BackendApi.get_battlerank_max(model_mgr, using=using)
        if rankmaster.id == rankmax:
            # これ以上上がらない.
            return False
        return True
    
    @staticmethod
    def get_battle_opponent_change_restcnt(model_mgr, battleplayer, rankmaster, using=settings.DB_DEFAULT):
        """残り対戦相手変更回数を取得.
        """
        if BackendApi.check_rankup_battle(model_mgr, battleplayer, rankmaster, using=using):
            # ランクアップ線は変更できない.
            return 0
        else:
            return max(0, Defines.BATTLE_OPPONENT_CHANGE_COUNT_MAX - battleplayer.change_cnt)
    
    @staticmethod
    def tr_update_battle_opponent(model_mgr, uid, oid, post_cnt, do_remove_count=True):
        """対戦相手を更新.
        """
        def forUpdate(battleplayer, inserted):
            if inserted:
                if do_remove_count:
                    # ここに来るのはなにかフローがおかしい.
                    raise CabaretError(u'想定外のフローです')
                BackendApi.reset_battle_continuity_winnum(battleplayer, do_reset_times=True)
                battleplayer.rank = 1
            
            battleplayer.opponent = oid
            battleplayer.rankopplist.append(oid)
            battleplayer.rankopplist = list(set(battleplayer.rankopplist))
            
            if do_remove_count:
                if post_cnt == battleplayer.change_cnt:
                    raise CabaretError(u'設定済みです.', CabaretError.Code.ALREADY_RECEIVED)
                
                rankmaster = model_mgr.get_model(BattleRankMaster, battleplayer.rank)
                if rankmaster is None:
                    raise CabaretError(u'ランクが設定されていません. rank=%d' % rankmaster.rank, CabaretError.Code.INVALID_MASTERDATA)
                
                rest = BackendApi.get_battle_opponent_change_restcnt(model_mgr, battleplayer, rankmaster)
                if rest < 1:
                    raise CabaretError(u'これ以上対戦相手を変更できません.', CabaretError.Code.OVER_LIMIT)
                
                if not settings_sub.IS_BENCH:
                    battleplayer.change_cnt += 1
        model_mgr.add_forupdate_task(BattlePlayer, uid, forUpdate)
    
    #===========================================================
    # カード.
    @staticmethod
    def create_card_by_master(cardmaster):
        """マスターデータからカードを作成.
        保存しません.
        """
        card = Card()
        card.mid = cardmaster.id
        return card
    
    @staticmethod
    def check_sellauto(master, autosell_rarity=None):
        """自動退店確認.
        """
        if master.ckind != Defines.CardKind.NORMAL:
            return False
        return autosell_rarity is not None and master.rare <= autosell_rarity
    
    @staticmethod
    def tr_create_card(model_mgr, playercard, mid, level=1, skilllevel=1, way=Defines.CardGetWayType.OTHER, autosell_rarity=None, autosell_cache_obj=None):
        """カードを作成.
        """
        # マスターデータを取得.
        master = BackendApi.get_cardmasters([mid], model_mgr).get(mid)
        if master is None:
            raise CabaretError(u'マスターデータが存在しません', CabaretError.Code.INVALID_MASTERDATA)
        elif master.maxlevel < level:
            raise CabaretError(u'キャストの最大レベルを超えています', CabaretError.Code.INVALID_MASTERDATA)
        
        cardset = None
        autosell = BackendApi.check_sellauto(master, autosell_rarity)
        sellprice = 0
        sellprice_treasure = 0
        
        # 取得フラグ.
        maxlevel = level if 1 < level else None
        is_new = BackendApi.tr_set_cardacquisition(model_mgr, playercard.id, master, level=maxlevel)
        
        # 自動売却でアルバム云々で問題になったらコメントを外す.
#        if not is_new and autosell and CardUtil.checkEvolvable(master):
#            # ハメ管理できるキャストはアルバムの開放をチェック.
#            # ハメ管理Maxの
#            autosell_cache_obj = autosell_cache_obj or {}
#            is_complete = autosell_cache_obj.get(master.album, None)
#            if is_complete is None:
#                is_complete = BackendApi.check_album_memories_complete(model_mgr, playercard.id, master.album)
#                autosell_cache_obj[master.album] = is_complete
#            # アルバムが開放されてないので自動売却できない.
#            autosell = autosell and is_complete
        
        if autosell:
            # 自動退店.
            sellprice = CardUtil.calcSellPrice(master.baseprice, master.maxprice, level, master.maxlevel)
            if 0 < sellprice:
                # お金を付与.
                BackendApi.tr_add_gold(model_mgr, playercard.id, sellprice)
            
            sellprice_treasure = CardUtil.calcSellPriceTreasure(master.rare)
            if 0 < sellprice_treasure:
                # 秘宝を付与.
                BackendApi.tr_add_cabaretking_treasure(model_mgr, playercard.id, sellprice_treasure)
        else:
            # 経験値.
            exp = 0
            if 1 < level:
                levelexp = BackendApi.get_cardlevelexp_bylevel(level, model_mgr)
                if levelexp is None:
                    raise CabaretError(u'キャストの経験値が見つかりません', CabaretError.Code.INVALID_MASTERDATA)
                exp = levelexp.exp
            
            # カードを作成.
            card = BackendApi.create_card_by_master(master)
            card.id = Card.makeID(playercard.id, playercard.card)
            card.uid = playercard.id
            card.exp = exp
            card.level = level
            card.skilllevel = skilllevel
            card.way = way
            
            # 保存.
            model_mgr.set_save(card)
            
            # カード番号をincrement.
            playercard.card += 1
            model_mgr.set_save(playercard)
            
            cardset = CardSet(card, master)
        
        # ログ.
        model_mgr.set_save(UserLogCardGet.create(playercard.id, mid, way, autosell=autosell))
        BackendApi.tr_add_rarelog(model_mgr, playercard.id, master)
        
        if cardset:
            def writeEnd():
                BackendApi.save_cardidset(cardset)
                if master.ckind == Defines.CardKind.EVOLUTION:
                    # 指輪流出量の集計.
                    KpiOperator().set_incr_ringnum(card.uid, card.mid, card.way, card.ctime).save()
            model_mgr.add_write_end_method(writeEnd)
        
        result = {
            'is_new' : is_new,
            'card' : cardset,
            'autosell' : autosell,
            'sellprice' : sellprice,
            'sellprice_treasure' : sellprice_treasure,
        }
        return result
    
    @staticmethod
    def tr_set_cardacquisition(model_mgr, uid, master, level=None):
        """取得フラグを設定.
        """
        is_newcard = False
        
        cardacquisitionid = CardAcquisition.makeID(uid, master.id)
        cardacquisition = model_mgr.get_model(CardAcquisition, cardacquisitionid)
        if cardacquisition is None:
            cardacquisition = CardAcquisition.makeInstance(cardacquisitionid)
            cardacquisition.maxlevel = max(1, level or 1)
            model_mgr.set_save(cardacquisition)
            is_newcard = True
        elif level is not None and cardacquisition.maxlevel < level:
            cardacquisition = model_mgr.get_model_forupdate(CardAcquisition, cardacquisitionid)
            cardacquisition.maxlevel = level
            model_mgr.set_save(cardacquisition)
            model_mgr.set_got_models([cardacquisition])
            model_mgr.set_got_models_forupdate([cardacquisition])
        
        albumacquisitionid = AlbumAcquisition.makeID(uid, master.album)
        albumacquisition = model_mgr.get_model(AlbumAcquisition, albumacquisitionid)
        if albumacquisition is None:
            albumacquisition = AlbumAcquisition.makeInstance(albumacquisitionid)
            model_mgr.set_save(albumacquisition)
            model_mgr.set_got_models([albumacquisition])
        return is_newcard
    
    @staticmethod
    def tr_add_cardexp(model_mgr, cardset, exp):
        exp_add, level_add = BackendApi.add_cardexp(model_mgr, cardset, exp)
        if 0 < level_add:
            BackendApi.tr_set_cardacquisition(model_mgr, cardset.card.uid, cardset.master, level=cardset.card.level)
            model_mgr.set_save(cardset.card)
        elif 0 < exp_add:
            model_mgr.set_save(cardset.card)
        return exp_add, level_add
    
    @staticmethod
    def add_cardexp(model_mgr, cardset, exp, using=settings.DB_DEFAULT):
        """カードの経験値を加算.
        """
        if cardset.is_levelmax:
            # レベルが最大.
            return 0, 0
        
        card = cardset.card
        master = cardset.master
        
        if settings_sub.IS_BENCH:
            exp = 0
        
        post_exp = card.exp + exp
        post_level = card.level
        
        levelexp = BackendApi.get_cardlevelexp_byexp(post_exp, model_mgr, using=using)
        
        if levelexp is None:
            raise CabaretError(u'キャストの経験値を設定できません', CabaretError.Code.INVALID_MASTERDATA)
        elif master.maxlevel == levelexp.level:
            # 最大レベル.
            post_exp = levelexp.exp
            post_level = levelexp.level
        elif master.maxlevel < levelexp.level:
            # 最大レベルを超えた.
            levelexp = BackendApi.get_cardlevelexp_bylevel(master.maxlevel, model_mgr, using=using)
            post_exp = levelexp.exp
            post_level = levelexp.level
        elif card.level != levelexp.level:
            # レベルが変わった.
            post_level = levelexp.level
        else:
            pass
        
        exp_add = post_exp - card.exp
        level_add = post_level - card.level
        
        card.exp = post_exp
        card.level = post_level
        
        return exp_add, level_add
    
    @staticmethod
    def get_memoriesmasters(masteridlist, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """思い出アルバムのマスター情報を取得する.
        dictです.
        """
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        return BackendApi.get_model_dict(model_mgr, MemoriesMaster, masteridlist, get_instance=False, using=using)
    
    @staticmethod
    def get_memoriesmaster_list(model_mgr, masteridlist, using=settings.DB_DEFAULT):
        """思い出アルバムのマスター情報を取得する.
        """
        return BackendApi.get_model_list(model_mgr, MemoriesMaster, masteridlist, get_instance=False, using=using)
    
    @staticmethod
    def get_memories_vtime(model_mgr, uid, masteridlist, using=settings.DB_DEFAULT):
        """思い出アルバムを見た時間を取得.
        """
        memories = BackendApi.get_model_list(model_mgr, Memories, [Memories.makeID(uid, mid) for mid in masteridlist], get_instance=False, using=using)
        dic = {}
        for model in memories:
            dic[model.mid] = model.vtime
        return dic
    
    @staticmethod
    def get_albumacquisitions(model_mgr, uid, albumidlist, using=settings.DB_DEFAULT):
        """思い出アルバムのアルバム解放フラグを取得する.
        dictです.
        """
        records = dict.fromkeys(list(set(albumidlist)), None)
        modellist = model_mgr.get_models(AlbumAcquisition, [AlbumAcquisition.makeID(uid, albumid) for albumid in records.keys()], using=using)
        for model in modellist:
            records[model.mid] = model
        return records
    
    @staticmethod
    def get_cardacquisitions(model_mgr, uid, cardidlist, using=settings.DB_DEFAULT):
        """カードの解放フラグを取得する.
        """
        records = dict.fromkeys(list(set(cardidlist)), None)
        modellist = model_mgr.get_models(CardAcquisition, [CardAcquisition.makeID(uid, cardid) for cardid in records.keys()], using=using)
        for model in modellist:
            records[model.mid] = model
        return records
    
    @staticmethod
    def get_cardmasters(cardmasteridlist, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """カードのマスター情報を取得する.
        dictです.
        """
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        
        masters = dict.fromkeys(list(set(cardmasteridlist)), None)
        masterlist = model_mgr.get_models(CardMaster, masters.keys(), get_instance=False, using=using)
        sortmasterlist = model_mgr.get_models(CardSortMaster, masters.keys(), get_instance=False, using=using)
        
        skillmasters = {}
        for master in masterlist:
            masters[master.id] = ModelCardMaster([master])
            if master.skill:
                skillmasters[master.skill] = None
        for sortmaster in sortmasterlist:
            masters[sortmaster.id].setModel(sortmaster)
        skillmasterlist = model_mgr.get_models(SkillMaster, skillmasters.keys(), get_instance=False, using=using)
        for skillmaster in skillmasterlist:
            skillmasters[skillmaster.id] = skillmaster
        
        for master in masterlist:
            modelmaster = masters[master.id]
            skill = skillmasters.get(modelmaster.skill)
            if skill:
                modelmaster.setSkill(skill)
        return masters
    
    @staticmethod
    def get_cards(cardidlist, arg_model_mgr=None, using=settings.DB_DEFAULT, forupdate=False, deleted=False, filter_func=None):
        """カード情報を取得する.
        """
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        
        if filter_func is None:
            filter_func = lambda x,y: True
        
        if deleted:
            model_cls = CardDeleted
        else:
            model_cls = Card
        
        # カードを引いてくる.
        if forupdate:
            cardlist = model_cls.fetchByKeyForUpdate(cardidlist)
        else:
            cardlist = model_mgr.get_models(model_cls, cardidlist, False, using=using)
            model_mgr.set_got_models(cardlist)
        # マスターデータ.
        carddict = {}
        masters = {}
        for card in cardlist:
            carddict[card.id] = card
            masters[card.mid] = None
        masters.update(BackendApi.get_cardmasters(masters.keys(), model_mgr, using=using))
        result = [CardSet(carddict[cardid], masters[carddict[cardid].mid]) for cardid in cardidlist if carddict.has_key(cardid) and filter_func(carddict[cardid], masters[carddict[cardid].mid])]
        return result
    
    @staticmethod
    def get_deck(uid, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """デッキを取得.
        """
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        # デッキ情報を取得.
        deck = model_mgr.get_model(Deck, uid, True, using=using)
        return deck
    
    @staticmethod
    def get_decks(uidlist, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """デッキを取得.
        """
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        return BackendApi.get_model_dict(model_mgr, Deck, uidlist, get_instance=True, using=using)
    
    @staticmethod
    def get_raid_deck(uid, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """レイド用デッキを取得.
        """
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        # デッキ情報を取得.
        deck = model_mgr.get_model(RaidDeck, uid, False, using=using)
        if deck is None:
            deck = BackendApi.get_deck(uid, model_mgr, using=using)
        return deck
    
    @staticmethod
    def get_deck_castid_list(model_mgr, uid, using=settings.DB_DEFAULT):
        """デッキに含まれているカードのID.
        """
        # デッキ確認.
        decks = [
            BackendApi.get_deck(uid, model_mgr),
            BackendApi.get_raid_deck(uid, model_mgr),
        ]
        cardidlist = []
        for deck in decks:
            if deck:
                cardidlist.extend(deck.to_array())
        return cardidlist
    
    @staticmethod
    def check_deck_cast_include(model_mgr, uid, cardidlist, using=settings.DB_DEFAULT):
        """デッキに含まれているカードがないかを検証.
        """
        ignores = BackendApi.get_deck_castid_list(model_mgr, uid, using=using)
        # すでに設定されているかを確認.
        if set(cardidlist) & set(ignores):
            raise CabaretError(u'キャスト編成に設定されているキャストが含まれています', CabaretError.Code.ILLEGAL_ARGS)
    
    @staticmethod
    def __set_deck(model_mgr, deck_cls, player, cardidlist):
        """デッキを設定.
        """
        uid = player.id
        deckcapacity = player.deckcapacity
        
        # 店舗に配置されているキャストを確認.
        BackendApi.check_cabaretclub_cast_include(model_mgr, uid, cardidlist)
        
        cardlist = BackendApi.get_cards(cardidlist, model_mgr, using=settings.DB_DEFAULT)
        
        # おかしなIDがないか確認.
#        if len(cardlist) != len(list(set(cardidlist))) or len(cardlist) != len(cardidlist):
#            raise CabaretError(u"不正な引数です", CabaretError.Code.ILLEGAL_ARGS)
        if len(cardlist) < 1:
            raise CabaretError(u"不正な引数です", CabaretError.Code.ILLEGAL_ARGS)
        elif Defines.DECK_CARD_NUM_MAX < len(cardlist) and not settings_sub.IS_BENCH:
            raise CabaretError(u"所属キャストの上限を超えています", CabaretError.Code.OVER_LIMIT)
        
        # 自分のカードかどうか.
        cost = 0
        cardidlist = []
        for cardset in cardlist:
            if cardset.card.uid != uid:
                raise CabaretError(u"他人のキャストです", CabaretError.Code.ILLEGAL_ARGS)
            elif cardset.master.ckind != Defines.CardKind.NORMAL:
                raise CabaretError(u"出勤キャストに設定できないキャストです", CabaretError.Code.ILLEGAL_ARGS)
            cost += cardset.master.cost
            cardidlist.append(cardset.id)
        
        if deckcapacity < cost:
            raise CabaretError(u"人件費オーバーです", CabaretError.Code.OVER_LIMIT)
        
        # デッキ情報を取得.
        deck = model_mgr.get_model(deck_cls, uid, True, using=settings.DB_DEFAULT)
        
        # No.1を変更したか.
        no1_change = deck.leader != cardidlist[0]
        
        # デッキに設定.
        deck.set_from_array(cardidlist)

        # 通常の場合 deckcost を更新
        if isinstance(deck, Deck):
            cost = sum([x.master.cost for x in BackendApi.get_cards(deck.to_array())])
            playerdeck = player.getModel(PlayerDeck)
            playerdeck.deckcost = cost
            model_mgr.set_save(playerdeck)
        
        # ミッション.
        mission_executer = PanelMissionConditionExecuter()
        mission_executer.addTargetEditDeck(no1_change)
        BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
        
        # 保存.
        model_mgr.set_save(deck)
    
    @staticmethod
    def set_deck(player, cardidlist, arg_model_mgr=None):
        """デッキを設定.
        """
        model_mgr = arg_model_mgr or ModelRequestMgr()
        BackendApi.__set_deck(model_mgr, Deck, player, cardidlist)
        if arg_model_mgr is None:
            model_mgr.write_all()
    
    @staticmethod
    def set_raid_deck(player, cardidlist, arg_model_mgr=None):
        """デッキを設定.
        """
        model_mgr = arg_model_mgr or ModelRequestMgr()
        BackendApi.__set_deck(model_mgr, RaidDeck, player, cardidlist)
        if arg_model_mgr is None:
            model_mgr.write_all()
    
    @staticmethod
    def get_leaders(uididlist, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """デッキのリーダーを取得.
        """
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        # デッキ情報を取得.
        decklist = model_mgr.get_models(Deck, uididlist, using=using)
        
        cardidlist = [deck.leader for deck in decklist if deck.leader]
        cardlist = BackendApi.get_cards(cardidlist, model_mgr, using)
        
        table = {}
        for cardset in cardlist:
            table[cardset.card.uid] = cardset
        return table
    
    @staticmethod
    def get_raid_leaders(uidlist, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """レイド用デッキのリーダーを取得.
        """
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        # デッキ情報を取得.
        leader_ids = dict([(deck.id, deck.leader) for deck in model_mgr.get_models(RaidDeck, uidlist, using=using)])
        cardlist = BackendApi.get_cards(leader_ids.values(), model_mgr, using)
        table = dict([(cardset.card.uid, cardset) for cardset in cardlist])
        
        not_found_uidlist = list(set(uidlist) - set(table.keys()))
        if not_found_uidlist:
            table.update(BackendApi.get_leaders(not_found_uidlist, model_mgr, using))
        return table
    
    @staticmethod
    def get_sortattrgetter(sortby):
        if sortby in (Defines.CardSortType.CTIME, Defines.CardSortType.CTIME_REV):
            return lambda card : int(time.mktime(card.card.ctime.timetuple()))
        
        elif sortby in (Defines.CardSortType.RARE, Defines.CardSortType.RARE_REV):
            return lambda card : ((card.master.rare << 32) + card.master.id)
        
        elif sortby in (Defines.CardSortType.LEVEL, Defines.CardSortType.LEVEL_REV):
            return lambda card : ((card.card.level << 32) + card.master.id)
        
        elif sortby in (Defines.CardSortType.COST, Defines.CardSortType.COST_REV):
            return lambda card : ((card.master.cost << 32) + card.master.id)
        
        elif sortby in (Defines.CardSortType.POWER, Defines.CardSortType.POWER_REV):
            return lambda card : ((card.power << 32) + card.master.id)
        
        elif sortby in (Defines.CardSortType.HKLEVEL, Defines.CardSortType.HKLEVEL_REV):
            return lambda card : ((card.master.hklevel << 32) + card.master.id)
        
        elif sortby == Defines.CardSortType.EVO_MATERIAL:
            return lambda card : ((card.master.ckind << 32) + card.master.rare)
        
        else:
            return lambda card : card.id
    
    @staticmethod
    def save_cardidset(cardset, deck=None, pipe=None):
        """ソートと絞り込み用のセットに設定する.
        """
        card = cardset.card
        master = cardset.master
        
        uid = card.uid
        ckind = master.ckind
        do_execute = False
        if pipe is None:
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            do_execute = True
        
        UserCardIdListSet.create(uid, card.id).save(pipe)
        
        CardKindListSet.create(uid, card.id, ckind, master.rare).save(pipe)
        
        EvolutionAlbumHkLevelListSet.create(uid, card.id, master.albumhklevel).save(pipe)
        
        if do_execute:
            pipe.execute()
        
        KpiOperator().set_save_cardmasterid(card.id, master.id).save()
    
    @staticmethod
    def delete_cardidset(cardset, pipe=None):
        card = cardset.card
        master = cardset.master
        uid = card.uid
        ckind = master.ckind
        
        do_execute = False
        if pipe is None:
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            do_execute = True
        
        UserCardIdListSet.create(uid, card.id).delete(pipe)
        
        CardKindListSet.create(uid, card.id, ckind, master.rare).delete(pipe)
        
        EvolutionAlbumHkLevelListSet.create(uid, card.id, master.albumhklevel).delete(pipe)
        
        if do_execute:
            pipe.execute()
        
        KpiOperator().set_delete_cardmasterid(card.id, master.id).save()
    
    @staticmethod
    def preload_usercardidlist(model_mgr, uid, using=settings.DB_DEFAULT):
        """ユーザーのカードをロード.
        """
        if not UserCardIdListSet.get_num(uid):
            # 無い.
            
            cardlist = Card.fetchByOwner(uid, using=using)
            model_mgr.set_got_models(cardlist)
            
            cardsetlist = BackendApi.get_cards([card.id for card in cardlist], model_mgr, using=using)
            
            pipe = RedisModel.getDB().pipeline()
            
            delete_card_by_uid(uid, pipe)
            for cardset in cardsetlist:
                UserCardIdListSet.create(uid, cardset.id).save(pipe)
                BackendApi.save_cardidset(cardset, pipe=pipe)
            
            pipe.execute()
    
    @staticmethod
    def _get_card_list(uid, offset=0, limit=-1, filter_obj=None, sortby='-ctime', arg_model_mgr=None, using=settings.DB_DEFAULT):
        """所持カード一覧を絞り込んで取得.
        """
        model_mgr = arg_model_mgr or ModelRequestMgr()
        BackendApi.preload_usercardidlist(model_mgr, uid, using=using)
        
        myfilter_func = lambda x,y : filter_obj.check(x,y) if filter_obj else True
        
        cardidlist = UserCardIdListSet.fetch_id(uid)
        cardsetlist = BackendApi.get_cards(cardidlist, model_mgr, using=using, filter_func=myfilter_func)
        
        reverse = sortby and (sortby[0] == '-')
        
        cardsetlist.sort(key=BackendApi.get_sortattrgetter(sortby), reverse=reverse)
        
        if limit == -1:
            if 0 < offset:
                return cardsetlist[offset:]
            else:
                return cardsetlist
        else:
            return cardsetlist[offset:(offset + limit)]
    
    @staticmethod
    def _get_cardnum_by_ctype(uid, ctype, arg_model_mgr=None, using=settings.DB_DEFAULT, filter_func=None):
        """カード所持数を取得.
        """
        if ctype in (None, Defines.CharacterType.ALL) and filter_func is None:
            model_mgr = arg_model_mgr or ModelRequestMgr()
            BackendApi.preload_usercardidlist(model_mgr, uid, using=using)
            
            return UserCardIdListSet.get_num(uid)
        else:
            filter_obj = CardListFilter(ctype=ctype)
            if filter_func:
                filter_obj.add_optional_filter(filter_func)
            return len(BackendApi._get_card_list(uid, filter_obj=filter_obj, arg_model_mgr=arg_model_mgr, using=using))
    
    @staticmethod
    def get_card_list(uid, offset=0, limit=-1, ctype=None, sortby='-ctime', arg_model_mgr=None, using=settings.DB_DEFAULT):
        """所持カード一覧を取得.
        """
        filter_obj = CardListFilter(ctype=ctype)
        return BackendApi._get_card_list(uid, offset, limit, filter_obj, sortby, arg_model_mgr, using)
    
    @staticmethod
    def get_cardnum_by_ctype(uid, ctype, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """カード所持数を取得.
        """
        return BackendApi._get_cardnum_by_ctype(uid, ctype, arg_model_mgr, using)
    
    @staticmethod
    def get_cardnum(uid, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """カード所持数を取得.
        """
        return BackendApi.get_cardnum_by_ctype(uid, None, arg_model_mgr, using)
    
    # カード売却用.
    @staticmethod
    def get_sellcard_list(uid, offset=0, limit=-1, filter_obj=None, sortby='-ctime', arg_model_mgr=None, using=settings.DB_DEFAULT):
        """売却可能なカード一覧を取得.
        """
        model_mgr = arg_model_mgr or ModelRequestMgr()
        filter_obj = filter_obj or CardListFilter()
        store_castidlist = BackendApi.get_cabaretclub_active_cast_list(model_mgr, uid, OSAUtil.get_now(), using=using)
        filter_obj.add_optional_filter(lambda x,y:x.id not in store_castidlist)
        return BackendApi._get_card_list(uid, offset, limit, filter_obj, sortby, model_mgr, using)
    
    # 教育ベース用.
    @staticmethod
    def get_compositionbase_list(uid, offset=0, limit=-1, ctype=None, sortby='-ctime', arg_model_mgr=None, using=settings.DB_DEFAULT):
        """教育可能なカード一覧を取得.
        """
        filter_func = lambda x,y : CardSet(x,y).is_can_composition
        filter_obj = CardListFilter(ctype=ctype)
        filter_obj.add_optional_filter(filter_func)
        return BackendApi._get_card_list(uid, offset, limit, filter_obj, sortby, arg_model_mgr, using)
    
    @staticmethod
    def get_compositionbase_num(uid, ctype, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """教育可能なカード所持数を取得.
        """
        filter_func = lambda x,y : CardSet(x,y).is_can_composition
        return BackendApi._get_cardnum_by_ctype(uid, ctype, arg_model_mgr, using, filter_func)
    
    # 教育素材用.
    @staticmethod
    def get_compositionmaterial_list(uid, basecard, offset=0, limit=-1, filter_obj=None, sortby='-ctime', arg_model_mgr=None, using=settings.DB_DEFAULT):
        """教育素材カードのIDのリスト.
        """
        model_mgr = arg_model_mgr or ModelRequestMgr()
        
        basecardid = basecard.id
        cardidlist = BackendApi.get_deck(uid, model_mgr, using).to_array()[:]
        cardidlist.extend(BackendApi.get_raid_deck(uid, model_mgr, using).to_array())
        
        filter_obj = filter_obj or CardListFilter()
        filter_func = lambda x,y : basecardid != x.id and not x.protection and not x.id in cardidlist
        filter_obj.add_optional_filter(filter_func)
        store_castidlist = BackendApi.get_cabaretclub_active_cast_list(model_mgr, uid, OSAUtil.get_now(), using=using)
        filter_obj.add_optional_filter(lambda x,y:x.id not in store_castidlist)
        return BackendApi._get_card_list(uid, offset, limit, filter_obj, sortby, model_mgr, using)
    
    # 進化ベース用.
    @staticmethod
    def get_evolutionbase_list(uid, offset=0, limit=-1, ctype=None, sortby='-ctime', arg_model_mgr=None, using=settings.DB_DEFAULT):
        """進化ベースカード.
        """
        model_mgr = arg_model_mgr or ModelRequestMgr()
        
        # 進化専用カード.
        evol_cardnums = {}
        evol_rare_list = list(Defines.Rarity.EVOLUTION_ABLES)
        evol_rare_list.sort(reverse=True)
        num = 0
        for rare in evol_rare_list:
            num += CardKindListSet.count_by_kind(uid, Defines.CardKind.EVOLUTION, rare) or 0
            if num:
                evol_cardnums[rare] = num
        
        filter_obj = CardListFilter(ctype=ctype)
        filter_func = lambda x,y : CardSet(x,y).is_can_evolution
        filter_obj.add_optional_filter(filter_func)
        
        if len(evol_cardnums.keys()) == len(Defines.Rarity.EVOLUTION_ABLES):
            # 所持している進化可能カードが全て進化可能.
            return BackendApi._get_card_list(uid, offset, limit, filter_obj, sortby, model_mgr, using)
        
        cardlist = BackendApi._get_card_list(uid, filter_obj=filter_obj, sortby=sortby, arg_model_mgr=model_mgr, using=using)
        
        if limit == -1:
            start = offset
            end = len(cardlist)
        else:
            start = offset
            end = start + limit
        
        # 店舗設置キャスト.
        store_castidlist = BackendApi.get_cabaretclub_active_cast_list(model_mgr, uid, OSAUtil.get_now(), using=using)
        store_castlist = BackendApi.get_cards(store_castidlist, model_mgr, using=using)
        store_cast_counts = {}
        for cardset in store_castlist:
            counts = store_cast_counts[cardset.master.album] = store_cast_counts.get(cardset.master.album) or ([0] * Defines.HKLEVEL_MAX)
            counts[cardset.master.hklevel-1] += 1
        
        # 複数枚持っているカードだけ.
        arr = []
        nums = {}
        for card in cardlist:
            if evol_cardnums.has_key(card.master.rare):
                pass
            else:
                mid = card.master.id
                if not nums.has_key(mid):
                    master = card.master
                    num = EvolutionAlbumHkLevelListSet.count_evolution_ablenum(uid, master.album, master.hklevel)
                    store_counts = store_cast_counts.get(master.album)
                    if store_counts:
                        # 店舗に設置されている数を減らす.
                        num -= sum(store_counts[:master.hklevel])
                    nums[mid] = num
                num = nums[mid]
                if card.id in store_castidlist:
                    num += 1
                if num < 2:
                    continue
            arr.append(card)
            if end <= len(arr):
                break
        return arr[start:]
    
    @staticmethod
    def get_evolutionbase_num(uid, ctype, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """進化ベースカード所持数を取得.
        """
        evol_cardnums = {}
        for rare in Defines.Rarity.EVOLUTION_ABLES:
            num = CardKindListSet.count_by_kind(uid, Defines.CardKind.EVOLUTION, rare) or 0
            if num:
                evol_cardnums[rare] = num
        
        if len(evol_cardnums.keys()) == len(Defines.Rarity.EVOLUTION_ABLES):
            # 所持している進化可能カードが全て進化可能.
            filter_func = lambda x,y : CardSet(x,y).is_can_evolution
            return BackendApi._get_cardnum_by_ctype(uid, ctype, arg_model_mgr, using, filter_func)
        else:
            return len(BackendApi.get_evolutionbase_list(uid, ctype=ctype, arg_model_mgr=arg_model_mgr, using=using))
    
    @staticmethod
    def get_profile_newbie_cardlist(model_mgr, uid, limit=5, excludes=None, using=settings.DB_DEFAULT):
        """プロフィールページの最新カードを取得.
        """
        filter_func = lambda x,y,excludes : not x.id in excludes
        filter_obj = CardListFilter(ckind=Defines.CardKind.NORMAL)
        filter_obj.add_optional_filter(filter_func, excludes or [])
        cardlist = BackendApi._get_card_list(uid, 0, limit=limit, filter_obj=filter_obj, sortby='-ctime', arg_model_mgr=model_mgr, using=using)
        return cardlist
    
    # 進化素材用.
    @staticmethod
    def get_evolutionmaterial_list(uid, basecardset, offset=0, limit=-1, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """進化素材カード.
        """
        model_mgr = arg_model_mgr or ModelRequestMgr()
        
        albumhklevel_min = CardMaster.makeAlbumHklevel(basecardset.master.album, 1)
        albumhklevel_max = basecardset.master.albumhklevel
        
        filter_func = lambda x,y : x.id != basecardset.id and ((albumhklevel_min <= y.albumhklevel <= albumhklevel_max) or (y.ckind == Defines.CardKind.EVOLUTION and basecardset.master.rare <= y.rare))
        
        filter_obj = CardListFilter()
        filter_obj.add_optional_filter(filter_func)
        store_castidlist = BackendApi.get_cabaretclub_active_cast_list(model_mgr, uid, OSAUtil.get_now(), using=using)
        filter_obj.add_optional_filter(lambda x,y:x.id not in store_castidlist)
        cardlist = BackendApi._get_card_list(uid, offset, limit, filter_obj=filter_obj, sortby=Defines.CardSortType.EVO_MATERIAL, arg_model_mgr=model_mgr, using=using)
        
        return cardlist
    
    @staticmethod
    def get_card_list_by_cost(uid, cost_min, cost_max, offset=0, limit=-1, ctype=None, sortby='-ctime', arg_model_mgr=None, using=settings.DB_DEFAULT, filter_func=None):
        """所持カード一覧をコストの範囲指定で取得.
        """
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        
        filter_obj = CardListFilter(ctype=ctype, ckind=Defines.CardKind.NORMAL)
        opt_filter_func = lambda x,y,cmin,cmax : cmin<=y.cost<=cmax and (filter_func is None or filter_func(x,y))
        filter_obj.add_optional_filter(opt_filter_func, cost_min, cost_max)
        return BackendApi._get_card_list(uid, limit=limit, offset=offset, filter_obj=filter_obj, sortby=sortby, arg_model_mgr=model_mgr, using=using)
    
    @staticmethod
    def get_card_list_by_ckind(uid, ckind=[], offset=0, limit=-1, ctype=None, sortby='-ctime', arg_model_mgr=None, using=settings.DB_DEFAULT):
        """所持カード一覧をカードの種類指定で取得.
        """
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        
        filter_obj = CardListFilter(ctype=ctype, ckind=ckind)
        cardlist = BackendApi._get_card_list(uid, offset=offset, limit=limit, filter_obj=filter_obj, sortby=sortby, arg_model_mgr=model_mgr, using=using)
        return cardlist
    
    @staticmethod
    def get_rarelog(apphandler, uid, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """レアキャバ嬢獲得履歴.
        """
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        
        rarelog = model_mgr.get_model(RareCardLog, uid, False, using=using)
        if rarelog is None:
            return []
        
        arr = rarelog.to_array()
        masters = BackendApi.get_cardmasters([data['card'] for data in arr], model_mgr, using=using)
        
        logs = []
        for data in arr:
            master = masters.get(data['card'])
            if not master:
                continue
            logs.append(Objects.rarelog(apphandler, master, data['time']))
        return logs
    
    @staticmethod
    def tr_add_rarelog(model_mgr, uid, cardmaster):
        """レアキャバ嬢獲得履歴に追加.
        """
        if cardmaster.rare < Defines.Rarity.RARE:
            return
        
        def forUpdate(ins, inserted, mid):
            ins.add(mid)
        model_mgr.add_forupdate_task(RareCardLog, uid, forUpdate, cardmaster.id)
    
    @staticmethod
    def tr_sell_card(model_mgr, uid, cardidlist):
        """売却.
        """
        cardidlist = list(set(cardidlist))
        # 店舗に配置されているキャストを確認.
        BackendApi.check_cabaretclub_cast_include(model_mgr, uid, cardidlist)
        
        # カードを取得.
        cardlist = BackendApi.get_cards(cardidlist, model_mgr, using=settings.DB_DEFAULT, forupdate=True)
        
        # 確認のためにデッキを取得.
        deck = BackendApi.get_deck(uid, model_mgr, using=settings.DB_DEFAULT)
        raid_deck = BackendApi.get_raid_deck(uid, model_mgr, using=settings.DB_DEFAULT)
        
        # 売値.
        sellprice = 0
        
        # 秘宝.
        sellprice_treasure = 0
        
        # 売却できるかを確認.
        for cardset in cardlist:
            CardUtil.checkSellable(uid, deck, cardset)
            CardUtil.checkSellable(uid, raid_deck, cardset)
            sellprice += cardset.sellprice
            sellprice_treasure += cardset.sellprice_treasure
            
            # 削除.
            model_mgr.set_save(CardDeleted.create(cardset.card))
            model_mgr.set_delete(cardset.card)
        
        # お金を付与.
        if 0 < sellprice:
            BackendApi.tr_add_gold(model_mgr, uid, sellprice)
        
        # 秘宝を付与.
        if 0 < sellprice_treasure:
            BackendApi.tr_add_cabaretking_treasure(model_mgr, uid, sellprice_treasure)
        
        # ログ.
        model_mgr.set_save(UserLogCardSell.create(uid, cardidlist, sellprice, sellprice_treasure))
        
        # 書き込み後のタスク.
        def writeend():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            for cardset in cardlist:
                BackendApi.delete_cardidset(cardset, pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeend)
        
        return sellprice, sellprice_treasure
    
    @staticmethod
    def get_defaultleaders(model_mgr, ctypes, using=settings.DB_DEFAULT):
        """タイプごとにデフォルトで獲得するカード(リーダー)
        """
        defaultcardmasterlist = BackendApi.get_model_list(model_mgr, DefaultCardMaster, ctypes, using=using)
        
        result = {}
        for defaultcardmaster in defaultcardmasterlist:
            result[defaultcardmaster.ctype] = BackendApi.get_cardmasters([defaultcardmaster.leader], model_mgr, using).get(defaultcardmaster.leader)
        return result
    
    @staticmethod
    def tr_add_defaultcard(model_mgr, player):
        """初期カードを設定.
        リーダー.
        初期メンバー.
        BOX内のカード.
        """
        # 初期デッキ.
        defaultcardmaster = model_mgr.get_model(DefaultCardMaster, player.ptype)
        if defaultcardmaster is None:
            raise CabaretError(u'%sの初期キャスト情報がありません' % Defines.CharacterType.NAMES.get(player.ptype, u'不明のタイプ:%d' % player.ptype), CabaretError.Code.INVALID_MASTERDATA)
        
        playercard = player.getModel(PlayerCard)
        if playercard.card != 0:
            raise CabaretError(u'初期キャストを登録済みです', CabaretError.Code.ALREADY_RECEIVED)
        
        deck_cardidlist = []
        
        def _create_card(mid, is_deck):
            card = BackendApi.tr_create_card(model_mgr, playercard, mid, way=Defines.CardGetWayType.REGIST)['card'].card
            if is_deck:
                deck_cardidlist.append(card.id)
            model_mgr.set_got_models([card])
            return card
        # リーダー.
        _create_card(defaultcardmaster.leader, True)
        # メンバー.
        for mid in defaultcardmaster.members:
            _create_card(mid, True)
        # BOX.
        for mid in defaultcardmaster.box:
            _create_card(mid, False)
        # デッキに設定.
        BackendApi.set_deck(player, deck_cardidlist, model_mgr)
    
    @staticmethod
    def tr_set_cardprotection(model_mgr, flags):
        """カード保護書き込み.
        """
        cardsetlist = BackendApi.get_cards(flags.keys(), model_mgr, forupdate=True)
        for cardset in cardsetlist:
            card = cardset.card
            flag = flags[card.id]
            if flag != card.protection:
                card.protection = flags[card.id]
                model_mgr.set_save(card)
    
    @staticmethod
    def get_skillmaster(model_mgr, mid, using=settings.DB_READONLY):
        """スキルのマスターデータ.
        """
        return BackendApi.get_model(model_mgr, SkillMaster, mid, using=using)
    
    @staticmethod
    def get_skillmaster_list(model_mgr, midlist, using=settings.DB_READONLY):
        """スキルのマスターデータ.
        """
        skillmasterlist = BackendApi.get_model_list(model_mgr, SkillMaster, midlist, using=using)
        skillmasterlist.sort(key=lambda x:x.id)
        return skillmasterlist
    
    @staticmethod
    def get_cardstocks(model_mgr, uid, albumlist, using=settings.DB_DEFAULT):
        """図鑑のカードストック情報を取得.
        """
        idlist = [CardStock.makeID(uid, album) for album in albumlist]
        return BackendApi.get_model_dict(model_mgr, CardStock, idlist, get_instance=True, using=using, key=lambda x:x.mid)
    
    @staticmethod
    def get_cardstock(model_mgr, uid, album, using=settings.DB_DEFAULT):
        """図鑑のカードストック情報を取得.
        """
        return BackendApi.get_model(model_mgr, CardStock, CardStock.makeID(uid, album), get_instance=True, using=using)
    
    @staticmethod
    def get_album_addable_cardlist(model_mgr, uid, offset=0, limit=-1, ctype=None, rare=None, sortby='-ctime', using=settings.DB_DEFAULT):
        """図鑑に追加可能なカード一覧.
        """
        deck = BackendApi.get_deck(uid, model_mgr, using=settings.DB_DEFAULT)
        raid_deck = BackendApi.get_raid_deck(uid, model_mgr, using=settings.DB_DEFAULT)
        filter_obj = CardListFilter(ctype=ctype)
        filter_obj.add_optional_filter(lambda x,y:y.rare == rare)
        filter_obj.add_optional_filter(lambda x,y:CardUtil.checkStockable(uid, deck, CardSet(x,y), raise_on_error=False) and not raid_deck.is_member(x.id))
        store_castidlist = BackendApi.get_cabaretclub_active_cast_list(model_mgr, uid, OSAUtil.get_now(), using=using)
        filter_obj.add_optional_filter(lambda x,y:x.id not in store_castidlist)
        return BackendApi._get_card_list(uid, offset, limit, filter_obj=filter_obj, sortby=sortby, arg_model_mgr=model_mgr, using=using)
    
    @staticmethod
    def tr_add_cardstock(model_mgr, uid, cardidlist, confirmkey):
        """カードストック数を追加.
        """
        # リクエストの鍵を更新.
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        
        # 店舗に配置されているキャストを確認.
        BackendApi.check_cabaretclub_cast_include(model_mgr, uid, cardidlist)
        
        cardlist = BackendApi.get_cards(cardidlist, model_mgr, using=settings.DB_DEFAULT, forupdate=False, filter_func=lambda x,y:x.uid==uid)
        if len(cardlist) != len(cardidlist):
            # 指定されたIDが存在しない.
            if len(cardlist) == 0:
                cardlist = BackendApi.get_cards(cardidlist, model_mgr, using=settings.DB_DEFAULT, forupdate=False, deleted=True, filter_func=lambda x,y:x.uid==uid)
                if len(cardlist) == len(cardidlist):
                    raise CabaretError(u'ストック追加済みです', CabaretError.Code.ALREADY_RECEIVED)
            raise CabaretError(u'指定されたキャストが不正です', CabaretError.Code.ILLEGAL_ARGS)
        
        # 確認のためにデッキを取得.
        deck = BackendApi.get_deck(uid, model_mgr, using=settings.DB_DEFAULT)
        raid_deck = BackendApi.get_raid_deck(uid, model_mgr, using=settings.DB_DEFAULT)
        
        # ロックして取り直し.
        cardlist = BackendApi.get_cards(cardidlist, model_mgr, using=settings.DB_DEFAULT, forupdate=True)
        
        # ストック数.
        stocknums = {}
        for card in cardlist:
            CardUtil.checkStockable(uid, deck, card)
            CardUtil.checkStockable(uid, raid_deck, card)
            
            album = card.master.album
            stocknums[album] = stocknums.get(album, 0) + 1
            
            # 削除.
            model_mgr.set_save(CardDeleted.create(card.card))
            model_mgr.set_delete(card.card)
        
        # ストックのモデルに加算.
        result_nums = {}
        albumidlist = stocknums.keys()
        for idx, album in enumerate(albumidlist):
            def forUpdate(model, inserted, is_last):
                num = stocknums[model.mid]
                model.num += num
                if Defines.ALBUM_STOCK_NUM_MAX < model.num:
                    raise CabaretError(u'ストックの上限を超えています.', CabaretError.Code.OVER_LIMIT)
                
                result_nums[model.mid] = model.num
                if is_last:
                    # ログ.
                    UserLogCardStock.create(uid, cardidlist, result_nums).insert()
            
            model_mgr.add_forupdate_task(CardStock, CardStock.makeID(uid, album), forUpdate, idx+1 == len(albumidlist))
        
        # 書き込み後のタスク.
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            for cardset in cardlist:
                BackendApi.delete_cardidset(cardset, pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
        
        return stocknums
    
    @staticmethod
    def tr_create_card_from_stock(model_mgr, uid, cardmaster, num, confirmkey):
        """ストック情報からカードを作成.
        """
        if cardmaster.hklevel != 1:
            raise CabaretError(u'ストックから作成するキャストが正しくない')
        
        # リクエストの鍵を更新.
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        
        # カードの所持数を確認.
        cardnum = BackendApi.get_cardnum(uid, model_mgr, using=settings.DB_DEFAULT)
        playerdeck = BackendApi.get_model(model_mgr, PlayerDeck, uid, using=settings.DB_DEFAULT)
        if playerdeck.cardlimit < (cardnum + num):
            raise CabaretError(u'キャスト所持数オーバー', CabaretError.Code.OVER_LIMIT)
        
        # ストックの消費.
        def forUpdate(model, inserted):
            if model.num < num:
                raise CabaretError(u'ストックが足りない', CabaretError.Code.NOT_ENOUGH)
            model.num -= num
        model_mgr.add_forupdate_task(CardStock, CardStock.makeID(uid, cardmaster.album), forUpdate)
        
        # カードを作成.
        playercard = PlayerCard.getByKeyForUpdate(uid)
        model_mgr.set_got_models([playercard])
        for _ in xrange(num):
            BackendApi.tr_create_card(model_mgr, playercard, cardmaster.id, way=Defines.CardGetWayType.STOCK)
    
    #===========================================================
    # フレンド.
    @staticmethod
    def _save_friendidlist(uid, state, model_mgr, using=settings.DB_DEFAULT):
        redisdb = RedisModel.getDB()
        friendlist = Friend.fetchValues(filters={'uid':uid,'state':state}, using=using)
        friendlist.sort(key=operator.attrgetter('ctime'), reverse=True)
        idlist = []
        pipe = redisdb.pipeline()
        
        pipe.delete(FriendListSet.makeKey(uid, state))
        for friend in friendlist:
            FriendListSet.create(uid, friend.fid, state, friend.ctime).save(pipe)
            idlist.append(friend.fid)
        pipe.execute()
        model_mgr.set_got_models(friendlist)
        return idlist
    
    @staticmethod
    def delete_friendidlistset(uid):
        redisdb = RedisModel.getDB()
        pipe = redisdb.pipeline()
        for state in Defines.FriendState.NAMES.keys():
            pipe.delete(FriendListSet.makeKey(uid, state))
        pipe.execute()
    
    @staticmethod
    def _add_friendid_to_redis(uid, state, fid, ctime=None, pipe=None):
        FriendListSet.create(uid, fid, state, ctime).save(pipe)
    
    @staticmethod
    def _remove_friendid_to_redis(uid, state, fid, pipe=None):
        FriendListSet.create(uid, fid, state).delete(pipe)
    
    @staticmethod
    def _get_friend_idlist(uid, state, offset=0, limit=-1, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """フレンドのIDのリストを取得.
        """
        if limit == 0:
            return []
        
        num = FriendListSet.get_num(uid, state)
        if num is None:
            model_mgr = arg_model_mgr or ModelRequestMgr()
            idlist = BackendApi._save_friendidlist(uid, state, model_mgr, using)
            if 0 < limit:
                return idlist[offset:(offset+limit)]
            else:
                return idlist[offset:]
        else:
            return [model.fid for model in FriendListSet.fetch(uid, state, offset, limit)]
    
    @staticmethod
    def _get_friend_num(uid, state, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """フレンドの人数を取得.
        """
        num = FriendListSet.get_num(uid, state)
        if num is None:
            model_mgr = arg_model_mgr or ModelRequestMgr()
            idlist = BackendApi._save_friendidlist(uid, state, model_mgr, using)
            return len(idlist)
        else:
            return num
    
    @staticmethod
    def get_friend_idlist(uid, offset=0, limit=-1, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """フレンドのIDのリストを取得.
        """
        return BackendApi._get_friend_idlist(uid, Defines.FriendState.ACCEPT, offset, limit, arg_model_mgr, using)
    
    @staticmethod
    def get_friend_num(uid, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """フレンドの人数を取得.
        """
        return BackendApi._get_friend_num(uid, Defines.FriendState.ACCEPT, arg_model_mgr, using)
    
    @staticmethod
    def tr_add_friend(model_mgr, uid, fid, using=settings.DB_DEFAULT):
        """フレンドを追加.
        リクエストを作成するときに上限を確認しているのでここでは必要ないはず.
        """
        now = OSAUtil.get_now()
        def forUpdateTask(model, inserted, truestate):
            if inserted:
                raise CabaretError(u'フレンド申請がありません', CabaretError.Code.NOT_DATA)
            elif model.state == Defines.FriendState.ACCEPT:
                # すでにフレンド.
                raise CabaretError(u'すでにフレンドです', CabaretError.Code.ALREADY_RECEIVED)
            elif model.state != truestate:
                # すでにフレンド.
                raise CabaretError(u'フレンド申請が来ていません', CabaretError.Code.NOT_DATA)
            model.state = Defines.FriendState.ACCEPT
            model.ctime = now
        model_mgr.add_forupdate_task(Friend, Friend.makeID(uid, fid), forUpdateTask, Defines.FriendState.RECEIVE)
        model_mgr.add_forupdate_task(Friend, Friend.makeID(fid, uid), forUpdateTask, Defines.FriendState.SEND)
        
        # 書き込み後のタスクを設定.
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            BackendApi._remove_friendid_to_redis(uid, Defines.FriendState.RECEIVE, fid, pipe)
            BackendApi._remove_friendid_to_redis(fid, Defines.FriendState.SEND, uid, pipe)
            BackendApi._add_friendid_to_redis(uid, Defines.FriendState.ACCEPT, fid, now, pipe=pipe)
            BackendApi._add_friendid_to_redis(fid, Defines.FriendState.ACCEPT, uid, now, pipe=pipe)
            BackendApi.incr_friendaccept_num(fid, 1, pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def tr_delete_friend(model_mgr, uid, fid, using=settings.DB_DEFAULT):
        """フレンドを削除.
        """
        def forUpdateTask(model, inserted):
            if inserted or model.state != Defines.FriendState.ACCEPT:
                raise CabaretError(u'フレンドではない', CabaretError.Code.NOT_DATA)
            model.delete()
        model_mgr.add_forupdate_task(Friend, Friend.makeID(uid, fid), forUpdateTask)
        model_mgr.add_forupdate_task(Friend, Friend.makeID(fid, uid), forUpdateTask)
        
        def forUpdateRecordNum(model, inserted):
            if model.num == 0:
                raise CabaretError(u'フレンドレコードが壊れている..%s' % model.id)
            model.num -= 1
        model_mgr.add_forupdate_task(FriendRecordNum, uid, forUpdateRecordNum)
        model_mgr.add_forupdate_task(FriendRecordNum, fid, forUpdateRecordNum)
        
        # 書き込み後のタスクを設定.
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            BackendApi._remove_friendid_to_redis(uid, Defines.FriendState.ACCEPT, fid, pipe)
            BackendApi._remove_friendid_to_redis(fid, Defines.FriendState.ACCEPT, uid, pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def check_friend(uid, oid, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """フレンドなのかを確認.
        """
        num = FriendListSet.get_num(uid, Defines.FriendState.ACCEPT)
        if num is None:
            model_mgr = arg_model_mgr or ModelRequestMgr()
            BackendApi._save_friendidlist(uid, Defines.FriendState.ACCEPT, model_mgr, using)
        return FriendListSet.exists(uid, oid, Defines.FriendState.ACCEPT)
    
    #===========================================================
    # フレンド申請.
    @staticmethod
    def get_friendrequest_receive_idlist(uid, offset=0, limit=-1, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """フレンド申請してきたIDのリストを取得.
        """
        return BackendApi._get_friend_idlist(uid, Defines.FriendState.RECEIVE, offset, limit, arg_model_mgr, using)
        
    @staticmethod
    def get_friendrequest_receive_num(uid, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """フレンド申請をもらった数を取得.
        """
        return BackendApi._get_friend_num(uid, Defines.FriendState.RECEIVE, arg_model_mgr, using)
        
    @staticmethod
    def get_friendrequest_send_idlist(uid, offset=0, limit=-1, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """フレンド申請したIDのリストを取得.
        """
        return BackendApi._get_friend_idlist(uid, Defines.FriendState.SEND, offset, limit, arg_model_mgr, using)
        
    @staticmethod
    def get_friendrequest_send_num(uid, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """フレンド申請をした件数を取得.
        """
        return BackendApi._get_friend_num(uid, Defines.FriendState.SEND, arg_model_mgr, using)
    
    @staticmethod
    def get_friendaccept_num(uid, using=settings.DB_DEFAULT):
        """フレンド申請を承認してくれた件数を取得.
        """
        return FriendAcceptNum.get(uid).num
    
    @staticmethod
    def incr_friendaccept_num(uid, num, pipe=None, using=settings.DB_DEFAULT):
        """フレンド申請を承認してくれた件数を加算.
        """
        FriendAcceptNum.incr(uid, num, pipe)
    
    @staticmethod
    def delete_friendaccept_num(uid, using=settings.DB_DEFAULT):
        """フレンド申請を承認してくれた件数を削除.
        """
        FriendAcceptNum.create(uid, 0).save()
    
    @staticmethod
    def tr_add_friendrequest(model_mgr, v_player, o_player, using=settings.DB_DEFAULT):
        """フレンド申請を追加.
        """
        uid = v_player.id
        fid = o_player.id
        
        if uid == fid:
            raise CabaretError(u'自分に申請出来ません', CabaretError.Code.ILLEGAL_ARGS)
        
        # 上限を確認.
        def forUpdateRecordNum(model, inserted, nummax, errmess):
            if nummax <= model.num:
                raise CabaretError(errmess, CabaretError.Code.OVER_LIMIT)
            model.num += 1
        model_mgr.add_forupdate_task(FriendRecordNum, uid, forUpdateRecordNum, v_player.friendlimit, u'これ以上フレンド申請できません')
        model_mgr.add_forupdate_task(FriendRecordNum, fid, forUpdateRecordNum, o_player.friendlimit, u'相手のフレンド人数が上限に達しています')
        
        def forUpdateFriend(model, inserted, state):
            # レコードが存在しているか.
            if not inserted:
                if model.state == Defines.FriendState.SEND:
                    raise CabaretError(u'送信済みです', CabaretError.Code.ALREADY_RECEIVED)
                elif model.state == Defines.FriendState.RECEIVE:
                    raise CabaretError(u'申請が届いています', CabaretError.Code.ALREADY_RECEIVED)
                elif model.state == Defines.FriendState.ACCEPT:
                    raise CabaretError(u'すでにフレンドです', CabaretError.Code.ILLEGAL_ARGS)
                else:
                    raise CabaretError(u'ここには来ないはず')
            model.state = state
        model_mgr.add_forupdate_task(Friend, Friend.makeID(uid, fid), forUpdateFriend, Defines.FriendState.SEND)
        model_mgr.add_forupdate_task(Friend, Friend.makeID(fid, uid), forUpdateFriend, Defines.FriendState.RECEIVE)
        
        # ミッション.
        mission_executer = PanelMissionConditionExecuter()
        mission_executer.addTargetSendFriendRequest(1)
        BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
        
        # 書き込み後のタスクを設定.
        def writeEnd():
            now = OSAUtil.get_now()
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            BackendApi._add_friendid_to_redis(uid, Defines.FriendState.SEND, fid, now, pipe=pipe)
            BackendApi._add_friendid_to_redis(fid, Defines.FriendState.RECEIVE, uid, now, pipe=pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def tr_delete_friendrequest(model_mgr, fromid, toid, using=settings.DB_DEFAULT):
        """フレンド申請を削除.
        """
        def forUpdateTask(model, inserted, truestate):
            if inserted or model.state != truestate:
                raise CabaretError(u'フレンド申請が来ていません', CabaretError.Code.NOT_DATA)
            model.delete()
        model_mgr.add_forupdate_task(Friend, Friend.makeID(fromid, toid), forUpdateTask, Defines.FriendState.SEND)
        model_mgr.add_forupdate_task(Friend, Friend.makeID(toid, fromid), forUpdateTask, Defines.FriendState.RECEIVE)
        
        def forUpdateRecordNum(model, inserted):
            if model.num == 0:
                raise CabaretError(u'フレンドレコードが壊れている..%s' % model.id)
            model.num -= 1
        model_mgr.add_forupdate_task(FriendRecordNum, fromid, forUpdateRecordNum)
        model_mgr.add_forupdate_task(FriendRecordNum, toid, forUpdateRecordNum)
        
        # 書き込み後のタスクを設定.
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            BackendApi._remove_friendid_to_redis(fromid, Defines.FriendState.SEND, toid, pipe)
            BackendApi._remove_friendid_to_redis(toid, Defines.FriendState.RECEIVE, fromid, pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def check_friendrequest_send(uid, oid, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """フレンド申請中かを確認.
        """
        num = FriendListSet.get_num(uid, Defines.FriendState.SEND)
        if num is None:
            model_mgr = arg_model_mgr or ModelRequestMgr()
            BackendApi._save_friendidlist(uid, Defines.FriendState.SEND, model_mgr, using)
        return FriendListSet.exists(uid, oid, Defines.FriendState.SEND)
    
    @staticmethod
    def check_friendrequest_receive(uid, oid, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """フレンド申請を受けているかを確認.
        """
        num = FriendListSet.get_num(uid, Defines.FriendState.RECEIVE)
        if num is None:
            model_mgr = arg_model_mgr or ModelRequestMgr()
            BackendApi._save_friendidlist(uid, Defines.FriendState.RECEIVE, model_mgr, using)
        return FriendListSet.exists(uid, oid, Defines.FriendState.RECEIVE)
    
    #===========================================================
    # ガチャ.
    @staticmethod
    def save_freegachalasttime(uid, now, pipe=None):
        """最後に無料ガチャを遊んだ時間を保存.
        """
        FreeGachaLastTime.create(uid, now).save(pipe)
    
    @staticmethod
    def get_freegachalasttime(uid, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """最後に無料ガチャを遊んだ時間を取得.
        """
        ltime = FreeGachaLastTime.get(uid).ltime
        if ltime is None:
            return OSAUtil.get_datetime_min()
        else:
            return ltime
    
    @staticmethod
    def get_gachamaster_list(model_mgr, midlist, using=settings.DB_DEFAULT):
        """ガチャのマスターデータ取得.
        """
        gachamastersdict = BackendApi.get_model_dict(model_mgr, GachaMaster, midlist, using=using)
        boxidlist = list(set([gachamaster.boxid for gachamaster in gachamastersdict.values()]))
        gachaboxmastersdict = BackendApi.get_model_dict(model_mgr, GachaBoxMaster, boxidlist, using=using)
        
        gachadata = []
        for gachamaster in gachamastersdict.values():
            if gachaboxmastersdict.has_key(gachamaster.boxid):
                gachabox = gachaboxmastersdict[gachamaster.boxid]
                gachadata.append(GachaMasterSet(gachamaster, gachabox))
            
        
        return gachadata
    
    @staticmethod
    def get_gachamaster_list_by_boxid(model_mgr, boxid, using=settings.DB_DEFAULT):
        """ガチャのマスターデータ取得.
        """
        client = OSAUtil.get_cache_client()
        key = 'get_gachamaster_list_by_boxid:%d' % boxid
        
        midlist = client.get(key)
        if midlist is None:
            masterlist = GachaMaster.fetchValues(filters={'boxid':boxid}, using=using)
            midlist = [master.id for master in masterlist]
            client.set(key, midlist)
        else:
            masterlist = BackendApi.get_gachamaster_list(model_mgr, midlist, using=using)
        masterlist.sort(key=operator.attrgetter('id'))
        return masterlist
    
    @staticmethod
    def get_gachamaster(model_mgr, mid, using=settings.DB_DEFAULT):
        """ガチャのマスターデータ取得.
        """
        arr = BackendApi.get_gachamaster_list(model_mgr, [mid], using=using)
        if arr:
            return arr[0]
        else:
            return None
    
    @staticmethod
    def get_gachastepupmaster(model_mgr, mid, using=settings.DB_DEFAULT):
        """ガチャのステップアップマスターデータ取得.
        """
        return model_mgr.get_model(GachaStepupMaster, mid, using=using)
    
    @staticmethod
    def get_gachagroupmaster_list(model_mgr, midlist, using=settings.DB_DEFAULT):
        """ガチャBOX内グループのマスターデータ取得.
        """
        return BackendApi.get_model_list(model_mgr, GachaGroupMaster, midlist, using=using)
    
    @staticmethod
    def get_gachagroupmaster_dict(model_mgr, midlist, using=settings.DB_DEFAULT):
        """ガチャBOX内グループのマスターデータ取得.
        """
        return BackendApi.get_model_dict(model_mgr, GachaGroupMaster, midlist, using=using)
    
    @staticmethod
    def get_gachagroupmaster(model_mgr, mid, using=settings.DB_DEFAULT):
        """ガチャBOX内グループマスターデータ取得.
        """
        arr = BackendApi.get_gachagroupmaster_list(model_mgr, [mid], using=using)
        if arr:
            return arr[0]
        else:
            return None
    
    @staticmethod
    def get_gachaseattablemaster(model_mgr, mid, using=settings.DB_DEFAULT):
        """ガチャシートマスター.
        """
        return BackendApi.get_model(model_mgr, GachaSeatTableMaster, mid, using=using)
    
    @staticmethod
    def get_gachaseatmaster(model_mgr, mid, using=settings.DB_DEFAULT):
        """ガチャシートマスター.
        """
        return BackendApi.get_model(model_mgr, GachaSeatMaster, mid, using=using)
    
    @staticmethod
    def put_gachaslidecarddata(handler, gachamasterlist):
        """ガチャページでスライド表示するカードのマスターデータ取得.
        """
        dest = {}
        handler.html_param['gachaslidedata'] = dest
        if not gachamasterlist:
            return dest
        
        model_mgr = handler.getModelMgr()
        using = settings.DB_READONLY
        
        gacha_dict = dict([(gachamaster.id, gachamaster) for gachamaster in gachamasterlist])
        slidemaster_list = BackendApi.get_model_list(model_mgr, GachaSlideCastMaster, gacha_dict.keys(), using=using)
        
        cardidlist = []
        for slidemaster in slidemaster_list:
            try:
                cardidlist.extend(dict(slidemaster.castlist).keys())
            except:
                cardidlist.extend(slidemaster.castlist)
        if not cardidlist:
            return dest
        
        cardmasters = BackendApi.get_cardmasters(list(set(cardidlist)), model_mgr, using=using)
        
        for slidemaster in slidemaster_list:
            gachamaster = gacha_dict[slidemaster.id]
            cardlist = []
            for data in slidemaster.castlist:
                if isinstance(data, (int, long)):
                    data = (data, ('', None))
                cardid, v = data
                if not isinstance(v, (list, tuple)):
                    v = (v, None)
                
                cardmaster = cardmasters.get(cardid)
                if cardmaster is None:
                    continue
                
                imgurl, text = v
                cardlist.append((Objects.cardmaster(handler, cardmaster), handler.makeAppLinkUrlImg(imgurl), text))
            dest[gachamaster.unique_name] = cardlist
        
        return dest
    
    @staticmethod
    def put_gachaheaderdata(handler, gachamasterlist):
        """ガチャページで表示すヘッダー画像のマスターデータ取得.
        """
        dest = {}
        handler.html_param['gachaheaderdata'] = dest
        if not gachamasterlist:
            return dest
        
        model_mgr = handler.getModelMgr()
        using = settings.DB_READONLY
        
        gacha_dict = dict([(gachamaster.id, gachamaster) for gachamaster in gachamasterlist])
        headermaster_list = BackendApi.get_model_list(model_mgr, GachaHeaderMaster, gacha_dict.keys(), using=using)
        
        headerlist = []
        for headermaster in headermaster_list:
            headerlist.extend(headermaster.header)
        if not headerlist:
            return dest
        
        for headermaster in headermaster_list:
            gachamaster = gacha_dict[headermaster.id]
            headerlist = []
            for headerurl in headermaster.header:
                imgurl = handler.makeAppLinkUrlImg(headerurl)
                headerlist.append(imgurl)
            dest[gachamaster.unique_name] = headerlist
        
        return dest
    
    @staticmethod
    def get_gachaplaydata(model_mgr, uid, midlist, using=settings.DB_DEFAULT, get_instance=False):
        """ガチャプレイ情報を取得.
        """
        idlist = [GachaPlayData.makeID(uid, boxid) for boxid in midlist]
        return BackendApi.get_model_dict(model_mgr, GachaPlayData, idlist, get_instance=get_instance, using=using, key=lambda x:x.mid)
    
    @staticmethod
    def get_gachaplaycount(model_mgr, uid, midlist, using=settings.DB_DEFAULT, get_instance=False):
        """ガチャプレイ回数を取得.
        """
        idlist = [GachaPlayCount.makeID(uid, boxid) for boxid in midlist]
        return BackendApi.get_model_dict(model_mgr, GachaPlayCount, idlist, get_instance=get_instance, using=using, key=lambda x:x.mid)
    
    @staticmethod
    def get_gachaseattableplaycount(model_mgr, uid, midlist, using=settings.DB_DEFAULT, get_instance=False):
        """ガチャシートプレイ情報.
        """
        idlist = [GachaSeatTablePlayCount.makeID(uid, boxid) for boxid in midlist]
        return BackendApi.get_model_dict(model_mgr, GachaSeatTablePlayCount, idlist, get_instance=get_instance, using=using, key=lambda x:x.mid)
    
    @staticmethod
    def get_gachaseatplaydata(model_mgr, uid, midlist, using=settings.DB_DEFAULT, get_instance=False):
        """ガチャシートプレイ情報.
        """
        idlist = [GachaSeatPlayData.makeID(uid, mid) for mid in midlist]
        return BackendApi.get_model_dict(model_mgr, GachaSeatPlayData, idlist, get_instance=get_instance, using=using, key=lambda x:x.mid)
    
    @staticmethod
    def get_gachaseatmodels_by_gachamaster(model_mgr, uid, gachamaster, for_update=False, do_get_result=False, using=settings.DB_DEFAULT):
        """シートガチャ報酬受取.
        """
        dest = {}
        
        tableid = gachamaster.seattableid
        tablemaster = None
        if tableid:
            tablemaster = BackendApi.get_gachaseattablemaster(model_mgr, tableid, using=using)
        if tablemaster is None:
            return dest
        dest['tablemaster'] = tablemaster
        
        if for_update:
            playcount = BackendApi.get_gachaseattableplaycount(model_mgr, uid, [tableid]).get(tableid)
            if playcount is None:
                playcount = GachaSeatTablePlayCount.makeInstance(GachaSeatTablePlayCount.makeID(uid, tableid))
                playcount.insert()
            else:
                playcount = GachaSeatTablePlayCount.getByKeyForUpdate(GachaSeatTablePlayCount.makeID(uid, tableid))
        else:
            playcount = BackendApi.get_gachaseattableplaycount(model_mgr, uid, [tableid], get_instance=True, using=using).get(tableid)
        dest['playcount'] = playcount
        
        def get(mid):
            if mid:
                master = BackendApi.get_gachaseatmaster(model_mgr, mid, using=using)
            
            if master is not None:
                if for_update:
                    playdata = BackendApi.get_gachaseatplaydata(model_mgr, uid, [mid]).get(mid)
                    if playdata is None:
                        playdata = GachaSeatPlayData.makeInstance(GachaSeatPlayData.makeID(uid, mid))
                        playdata.insert()
                    else:
                        playdata = GachaSeatPlayData.getByKeyForUpdate(GachaSeatPlayData.makeID(uid, mid))
                else:
                    playdata = BackendApi.get_gachaseatplaydata(model_mgr, uid, [mid], get_instance=True, using=using).get(mid)
            return master, playdata
        master, playdata = get(tablemaster.getSeatId(playcount.lap + 1))

        def _prizenumber_exist(startid):
            idx = startid
            while True:
                prizeid = master.getPrizeId(idx)
                if prizeid:
                    yield idx
                else:
                    break
                idx += 1

        allend = None
        if playdata:
            allflag = [playdata.getFlag(idx) for idx in _prizenumber_exist(0)]
            allend = len(filter((lambda x: x == True), allflag)) == 0

        if (do_get_result or Defines.GachaConsumeType.MINI_SEAT) and 0 < playcount.lap and allend and playdata.last != 0:
            master, playdata = get(tablemaster.getSeatId(playcount.lap))
        ##if playdata.is_first() and 0 < playcount.lap:##後日実装
        ##    seat_id = tablemaster.getSeatId(playcount.lap)
        ##    master = BackendApi.get_gachaseatmaster(model_mgr, seat_id, using=settings.DB_DEFAULT)

        dest['seatmaster'] = master
        dest['playdata'] = playdata

        return dest
    
    @staticmethod
    def get_consumevalue(gachamaster, continuity, is_first=False, playcount=None, seatplaydata=None):
        """ガチャの料金.
        """
        if is_first:
            consumevalue = gachamaster.consumefirstvalue
        else:
            cnttotal = BackendApi.get_gacha_playcount_from_firsttime(gachamaster, playcount, seatplaydata)
            consumevalue = gachamaster.variableconsumevalue.get(str(cnttotal+1), gachamaster.consumevalue)
        
        if gachamaster.consumetype == Defines.GachaConsumeType.GACHAPT:
            consumevalue *= continuity
        elif gachamaster.consumetype == Defines.GachaConsumeType.TRYLUCKTICKET:
            consumevalue *= continuity
        elif Defines.GachaConsumeType.TO_TOPIC.get(gachamaster.consumetype) == Defines.GachaConsumeType.GachaTopTopic.TICKET:
            consumevalue *= continuity
        elif gachamaster.consumetype == Defines.GachaConsumeType.SCOUTEVENT:
            consumevalue *= continuity
        elif gachamaster.consumetype in {Defines.GachaConsumeType.SEAT, Defines.GachaConsumeType.SEAT2}:
            if playcount is not None:
                cnttotal = playcount.cnttotal
                consumevalue = gachamaster.variableconsumevalue.get(str(cnttotal + 1), gachamaster.consumevalue)
        return consumevalue
    
    @staticmethod
    def get_gacha_stock(model_mgr, gachamaster, playcount, now=None, using=settings.DB_DEFAULT):
        """ガチャの残り在庫.
        無制限の場合はNone.
        """
        if gachamaster.stock == 0:
            return None
        elif playcount is None:
            return gachamaster.stock
        
        now = now or OSAUtil.get_now()
        if gachamaster.schedule:
            schedulemaster = BackendApi.get_schedule_master(model_mgr, gachamaster.schedule, using=using)
            if schedulemaster and schedulemaster.wday != Defines.WeekDay.ALL:
                # 日別の回数を見る.
                cnt = playcount.getTodayPlayCnt(now)
            else:
                # 総数を見る.
                cnt = playcount.cnttotal
        else:
            # 総数を見る.
            cnt = playcount.cnttotal
        return max(0, gachamaster.stock - cnt)
    
    @staticmethod
    def get_gacha_firstplay_restnum(gachamaster, playcount, now=None, seatplaydata=None):
        """ガチャ初回プレイ残り回数.
        """
        if settings_sub.IS_BENCH:
            return 0
        elif gachamaster.firsttimetype == Defines.GachaFirsttimeType.ONETIME:
            cnttotal = playcount.cnttotal if playcount else 0
            return max(0, gachamaster.firststock - cnttotal)
        elif gachamaster.firsttimetype == Defines.GachaFirsttimeType.EVERYDAY:
            cnttoday = playcount.getTodayPlayCnt(now) if playcount else 0
            return max(0, gachamaster.firststock - cnttoday)
        elif gachamaster.firsttimetype == Defines.GachaFirsttimeType.SEAT:
            if seatplaydata is None or seatplaydata.is_first():
                return 1
            else:
                return 0
        else:
            return 0
    
    @staticmethod
    def get_gacha_playcount_from_firsttime(gachamaster, playcount, seatplaydata=None, now=None):
        """ガチャ初回設定からのプレイ回数.
        """
        if settings_sub.IS_BENCH:
            return 0
        elif gachamaster.firsttimetype == Defines.GachaFirsttimeType.EVERYDAY:
            cnttoday = playcount.getTodayPlayCnt(now) if playcount else 0
            return cnttoday
        elif gachamaster.firsttimetype == Defines.GachaFirsttimeType.SEAT:
            if seatplaydata is None or seatplaydata.is_first():
                return 0
            else:
                return seatplaydata.getReceivedNum()
        else:
            return playcount.cnttotal if playcount else 0
    
    @staticmethod
    def get_gacha_continuity_num(model_mgr, gachamaster, player, is_first=False, using=settings.DB_DEFAULT):
        """ガチャを回す回数.
        無料ガチャはcontinuity内で回せるだけ.
        有料またはチケットガチャはcontinuity固定.
        """
        if is_first:
            continuity = gachamaster.firstcontinuity
            consumevalue = gachamaster.consumefirstvalue
        else:
            continuity = gachamaster.continuity
            consumevalue = gachamaster.consumevalue
        
        if gachamaster.consumetype == Defines.GachaConsumeType.GACHAPT:
            if 0 < consumevalue:
                if player.gachaticket >= Defines.GACHA_TICKET_COST_NUM:
                    gachaticket = player.gachaticket
                    continuity = min(continuity, int(gachaticket / Defines.GACHA_TICKET_COST_NUM))
                else:
                    gachapt = player.gachapt
                    continuity = min(continuity, int(gachapt / consumevalue))
        elif gachamaster.consumetype == Defines.GachaConsumeType.TRYLUCKTICKET:
            if 0 < consumevalue:
                # 運試し.
                continuity = min(continuity, int(player.tryluckticket / consumevalue))
        elif gachamaster.consumetype == Defines.GachaConsumeType.RAREOVERTICKET:
            if 0 < consumevalue:
                # レア以上確定.
                continuity = min(continuity, int(player.rareoverticket / consumevalue))
        elif gachamaster.consumetype == Defines.GachaConsumeType.MEMORIESTICKET:
            if 0 < consumevalue:
                # 思い出.
                continuity = min(continuity, int(player.memoriesticket / consumevalue))
        elif Defines.GachaConsumeType.ADDITIONAL_TICKETS.has_key(gachamaster.consumetype):
            if 0 < consumevalue:
                # 追加仕様チケット.
                tickettype = Defines.GachaConsumeType.ADDITIONAL_TICKETS[gachamaster.consumetype]
                model = BackendApi.get_additional_gachaticket_nums(model_mgr, player.id, [tickettype], using).get(tickettype, None)
                ticketnum = model.num if model else 0
                continuity = min(continuity, int(ticketnum / consumevalue))
        elif gachamaster.consumetype == Defines.GachaConsumeType.EVENTTICKET:
            if 0 < consumevalue:
                # イベントチケット.
                cur_eventmaster = BackendApi.get_current_ticket_raideventmaster(model_mgr, using=settings.DB_READONLY)
                scorerecord = None
                if cur_eventmaster:
                    # チケット所持数.
                    scorerecord = BackendApi.get_raidevent_scorerecord(model_mgr, cur_eventmaster.id, player.id, using=settings.DB_READONLY)
                ticketnum = scorerecord.ticket if scorerecord else 0
                continuity = min(continuity, int(ticketnum / consumevalue))
        elif gachamaster.consumetype == Defines.GachaConsumeType.SCOUTEVENT:
            if 0 < consumevalue:
                # イベントガチャPT.
                cur_eventmaster = BackendApi.get_current_present_scouteventmaster(model_mgr, using=settings.DB_READONLY)
                scorerecord = None
                if cur_eventmaster:
                    # イベントガチャPT所持数.
                    scorerecord = BackendApi.get_scoutevent_scorerecord(model_mgr, cur_eventmaster.id, player.id, using=settings.DB_READONLY)
                point_gacha = scorerecord.point_gacha if scorerecord else 0
                continuity = min(continuity, int(point_gacha / consumevalue))
        
        return continuity
    
    @staticmethod
    def make_gachabox_rateinfo(model_mgr, gachamaster, playdata=None, using=settings.DB_DEFAULT):
        """ガチャBOXのカードの出現率情報.
        """
        if GachaBoxCardListInfoSet.exists(gachamaster.boxid):
            info = GachaBoxCardListInfoSet.get(gachamaster.boxid)
        else:
            if playdata is None:
                playdata = GachaPlayData.makeInstance(0)
                playdata.mid = gachamaster.boxid
            
            gachabox = GachaBox(gachamaster, playdata, blank=True)
            if gachabox.is_boxgacha:
                # ボックスには必要ない.
                return None
            
            grouplist = BackendApi.get_gachagroupmaster_list(model_mgr, gachabox.get_group_id_list(), using=using)
            
            cardnum = 0
            cardidlist_dict = {}
            cardlist_dict = {}
            weight_dict = {}
            
            for group in grouplist:
                # 各レア度の重み.
                weight_dict[group.rare] = weight_dict.get(group.rare, 0) + gachabox.get_group_rate(group.id)
                
                # レア度ごとのカード.
                cardidlist = cardidlist_dict[group.rare] = cardidlist_dict.get(group.rare) or []
                for data in group.table:
                    carddata = GachaBoxCardData.createByTableData(data)
                    if 0 < carddata.rate:
                        cardidlist.append(carddata.card)
            
            for rare, cardidlist in cardidlist_dict.items():
                cardlist = BackendApi.get_cardmasters(list(set(cardidlist)), model_mgr, using=using).values()
                rare_cardlist_dict = {}
                for card in cardlist:
                    type_cardlist = rare_cardlist_dict[card.ctype] = rare_cardlist_dict.get(card.ctype) or []
                    type_cardlist.append(card.name)
                cardlist_dict[rare] = rare_cardlist_dict
                cardnum += len(cardlist)
            
            # 重みの合計.
            rate_total = gachabox.rate_total
            
            info = {
                'rate_total' : rate_total,
                'weight_dict' : weight_dict,
                'cardlist_dict' : cardlist_dict,
                'cardnum' : cardnum,
            }
            GachaBoxCardListInfoSet.save(gachamaster.boxid, info)
        return info
    
    @staticmethod
    def make_stepup_rateinfo(handler, gachamaster, playdata=None, subbox=False, using=settings.DB_DEFAULT):
        """ステップアップガチャBOXのカードの出現率情報.
        """
        model_mgr = handler.getModelMgr()
        
        if playdata is None:
            playdata = GachaPlayData.makeInstance(0)
            playdata.mid = gachamaster.boxid


        if subbox:
            gachamaster.boxid = gachamaster.rarity_fixed_boxid
            playdata = GachaPlayData.makeInstance(0)
            playdata.mid = gachamaster.rarity_fixed_boxid
            gachamaster.box = model_mgr.get_model(GachaBoxMaster, gachamaster.boxid).box
        
        gachabox = GachaBox(gachamaster, playdata, blank=True)
        grouplist = BackendApi.get_gachagroupmaster_list(model_mgr, gachabox.get_group_id_list(), using=using)

        cardweight_dict = {}
        group_weight_dict = {}
        for group in grouplist:
            # 各グループの重み.
            group_weight_dict[group.id] = float(gachabox.get_group_rate(group.id))
        # 重みの合計.
        group_weight_total = float(sum(group_weight_dict.values()))
        
        for group in grouplist:
            # 各グループの出現率.
            groupdata = GachaBoxGroup(group)
            group_weight = group_weight_dict[group.id]
            group_weight_rate = group_weight / group_weight_total
            
            # グループのカードの出現率.
            rate_total = float(groupdata.rate_total)
            for carddata in groupdata.carddata_list:
                if 0 < carddata.rate:
                    cardweight_dict[carddata.card] = cardweight_dict.get(carddata.card, 0) + carddata.rate * group_weight_rate * 100 / rate_total
        
        cardmasters = BackendApi.get_cardmasters(cardweight_dict.keys(), model_mgr, using=using)
        cardlist_dict = {}
        weight_dict = {}
        for cardid, rate in cardweight_dict.items():
            cardmaster = cardmasters[cardid]
            ckind = cardmaster.ckind
            
            if ckind == Defines.CardKind.NORMAL:
                rare = cardmaster.rare
                
                # レア度ごとの出現率.
                ckind_weight_dict = weight_dict[ckind] = weight_dict.get(ckind) or {}
                ckind_weight_dict[rare] = ckind_weight_dict.get(rare, 0) + rate
                
                # レア度とタイプ別のカード一覧.
                ckind_cardlist_dict = cardlist_dict[ckind] = cardlist_dict.get(ckind) or {}
                rare_cardlist_dict = ckind_cardlist_dict[cardmaster.rare] = ckind_cardlist_dict.get(cardmaster.rare) or {}
                type_cardlist = rare_cardlist_dict[cardmaster.ctype] = rare_cardlist_dict.get(cardmaster.ctype) or []
                type_cardlist.append(Objects.cardmaster(handler, cardmaster))
            else:
                if ckind == Defines.CardKind.EVOLUTION:
                    # 指輪.
                    key = 'ring'
                else:
                    key = 'accessories'
                # 出現率.
                weight_dict[key] = weight_dict.get(key, 0) + rate
                # カード一覧.
                key_cardlist_list = cardlist_dict[key] = cardlist_dict.get(key) or []
                key_cardlist_list.append(Objects.cardmaster(handler, cardmaster))
        
        cardnum = len(cardmasters.keys())
        
        # 重みの合計.
        rate_total = 100.0
        
        info = {
            'rate_total' : rate_total,
            'weight_dict' : weight_dict,
            'cardlist_dict' : cardlist_dict,
            'cardnum' : cardnum,
            'is_box' : gachabox.is_boxgacha,
            'unique_name' : gachamaster.unique_name,
            'consumetype' : gachamaster.consumetype,
        }
        # スケジュール.
        if gachamaster.consumetype == Defines.GachaConsumeType.EVENTTICKET:
            # イベントガチャはイベント中だけ.
            config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
            info['etime'] = config.starttime
            info['etime'] = config.ticket_endtime
        elif gachamaster.consumetype == Defines.GachaConsumeType.SCOUTEVENT:
            # イベントガチャはイベント中だけ.
            config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
            info['etime'] = config.starttime
            info['etime'] = config.present_endtime
        else:
            schedule = gachamaster.schedule
            if schedule:
                master = BackendApi.get_schedule_master(model_mgr, gachamaster.schedule, using=using)
                info['stime'] = master.stime
                info['etime'] = master.etime
            info['stime_text'] = gachamaster.stime_text
            info['etime_text'] = gachamaster.etime_text
        return info
    
    @staticmethod
    def tr_consume_by_gachamaster(model_mgr, uid, gachamaster, continuity, is_first, is_gachaticket, seatplaydata=None):
        """ガチャの料金を消費.
        """
        consumevalue = BackendApi.get_consumevalue(gachamaster, continuity, is_first, seatplaydata=seatplaydata)
        if gachamaster.consumetype == Defines.GachaConsumeType.GACHAPT:
            # 引き抜きポイントまたは引き抜きチケット.
            if is_gachaticket and not settings_sub.IS_BENCH:
                BackendApi.tr_add_gachaticket(model_mgr, uid, -Defines.GACHA_TICKET_COST_NUM)
            else:
                BackendApi.tr_add_gacha_pt(model_mgr, uid, -consumevalue)
        elif gachamaster.consumetype in Defines.GachaConsumeType.PAYMENT_TYPES:
            # 課金処理で消費する.
            pass
        elif Defines.GachaConsumeType.ADDITIONAL_TICKETS.has_key(gachamaster.consumetype):
            tickettype = Defines.GachaConsumeType.ADDITIONAL_TICKETS[gachamaster.consumetype]
            BackendApi.tr_add_additional_gachaticket(model_mgr, uid, tickettype, -consumevalue)
        elif gachamaster.consumetype == Defines.GachaConsumeType.RAREOVERTICKET:
            # レア以上チケット.
            BackendApi.tr_add_rareoverticket(model_mgr, uid, -consumevalue)
        elif gachamaster.consumetype == Defines.GachaConsumeType.TRYLUCKTICKET:
            # 運試しチケット.
            BackendApi.tr_add_tryluckticket(model_mgr, uid, -consumevalue)
        elif gachamaster.consumetype == Defines.GachaConsumeType.MEMORIESTICKET:
            # 思い出チケット.
            BackendApi.tr_add_memoriesticket(model_mgr, uid, -consumevalue)
        elif gachamaster.consumetype == Defines.GachaConsumeType.EVENTTICKET:
            # イベントチケット.
            cur_eventmaster = BackendApi.get_current_ticket_raideventmaster(model_mgr)
            if not cur_eventmaster:
                raise CabaretError(u'イベントは終了しました', CabaretError.Code.EVENT_CLOSED)
            BackendApi.tr_add_raidevent_ticket(model_mgr, uid, cur_eventmaster.id, -consumevalue)
        elif gachamaster.consumetype == Defines.GachaConsumeType.SCOUTEVENT:
            # イベントガチャPT.
            cur_eventmaster = BackendApi.get_current_present_scouteventmaster(model_mgr)
            if not cur_eventmaster:
                raise CabaretError(u'イベントは終了しました', CabaretError.Code.EVENT_CLOSED)
            BackendApi.tr_add_scoutevent_score(model_mgr, cur_eventmaster, uid, gachapoint=-consumevalue)
            
            def writeEnd():
                KpiOperator().set_increment_scoutevent_consume_gachapoint(cur_eventmaster.id, uid, consumevalue).save()
            model_mgr.add_write_end_method(writeEnd)
        return consumevalue
        
    
    @staticmethod
    def get_gachapaymententry(model_mgr, paymentId, using=settings.DB_DEFAULT):
        """サーバ側のガチャ課金レコードを取得.
        """
        return model_mgr.get_model(GachaPaymentEntry, paymentId, using=using)
    
    @staticmethod
    def tr_create_gachapaymententry(model_mgr, player, paymentdata, continuity, ctime):
        """ガチャ課金レコードの作成.
        """
        if paymentdata.status != PaymentData.Status.START:
            raise CabaretError(u'課金ステータスが不正です', CabaretError.Code.ILLEGAL_ARGS)
        
        ins = BackendApi.get_gachapaymententry(model_mgr, paymentdata.paymentId)
        if ins:
            raise CabaretError(u'作成済みです', CabaretError.Code.ALREADY_RECEIVED)
        
        item = paymentdata.paymentItems[0]
        iid = int(item.itemId)
        inum = int(item.quantity)
        
        ins = GachaPaymentEntry()
        ins.id = paymentdata.paymentId
        
        ins.uid = player.id
        ins.iid = iid
        ins.inum = inum
        ins.price = int(item.unitPrice)
        ins.state = PaymentData.Status.CREATE
        ins.ctime = ctime
        ins.continuity = continuity
        
        model_mgr.set_save(ins)
        
        return ins
    
    @staticmethod
    def tr_update_gachapaymententry(model_mgr, uid, paymentId, status):
        """課金レコードのステータスを更新.
        """
        if status == PaymentData.Status.CREATE:
            raise CabaretError(u'このステータスは指定できません', CabaretError.Code.ILLEGAL_ARGS)
        
        entry = BackendApi.get_gachapaymententry(model_mgr, paymentId)
        if entry is None:
            raise CabaretError(u'課金レコードが存在しません', CabaretError.Code.NOT_DATA)
        
        entry = GachaPaymentEntry.getByKeyForUpdate(paymentId)
        model_mgr.set_got_models_forupdate([entry])
        if entry.uid != uid:
            raise CabaretError(u'他人の課金レコードです', CabaretError.Code.ILLEGAL_ARGS)
        elif entry.state == status:
            raise CabaretError(u'キャンセル済みです', CabaretError.Code.ALREADY_RECEIVED)
        elif status == PaymentData.Status.START and entry.state != PaymentData.Status.CREATE:
            raise CabaretError(u'課金ステータスが不正です', CabaretError.Code.ILLEGAL_ARGS)
        elif status != PaymentData.Status.START and entry.state != PaymentData.Status.START:
            raise CabaretError(u'課金ステータスが不正です', CabaretError.Code.ILLEGAL_ARGS)
        entry.state = status
        model_mgr.set_save(entry)
        
        def writeEnd():
            client = OSAUtil.get_cache_client()
            KEY = 'payment_checked:%s' % uid
            client.delete(KEY)
        model_mgr.add_write_end_method(writeEnd)
        
        return entry
    
    @staticmethod
    def tr_gacha_cancel(model_mgr, uid, paymentId):
        """課金ガチャキャンセル書き込み.
        """
        return BackendApi.tr_update_gachapaymententry(model_mgr, uid, paymentId, PaymentData.Status.CANCEL)
    
    @staticmethod
    def tr_gacha_timeout(model_mgr, uid, paymentId):
        """課金ガチャ期限切れ書き込み.
        """
        return BackendApi.tr_update_gachapaymententry(model_mgr, uid, paymentId, PaymentData.Status.TIMEOUT)
    
    @staticmethod
    def _tr_add_gachabonus(model_mgr, uid, gachamaster, rand=None):
        """おまけを渡す.
        """
        prizeidlist = gachamaster.choice_bonus(rand=rand)
        if prizeidlist:
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, Defines.TextMasterID.GACHA_BONUS, auto_receive=True)
            return prizeidlist
        return []
    
    @staticmethod
    def get_memories_gacha_data(model_mgr, uid, using):
        """思い出しチケットガチャのガチャデータ取得.
        """
        filter_obj = CardListFilter(ckind=Defines.CardKind.NORMAL)
        cardlist = BackendApi._get_card_list(uid, filter_obj=filter_obj, arg_model_mgr=model_mgr, using=using)
        
        memories_gacha_data = {}
        album_mid = {}
        for cardset in cardlist:
            if cardset.master.hklevel != 1:
                mid = album_mid.get(cardset.master.album)
                if not mid:
                    mid = BackendApi.get_cardmasterid_by_albumid(model_mgr, cardset.master.album, using)
                    if mid:
                        album_mid[cardset.master.album] = mid
            else:
                mid = cardset.master.id
            
            if not memories_gacha_data.has_key(mid):
                memories_gacha_data[mid] = {
                    'id' : int(mid),
                    'rate' : 1,
                }
        return memories_gacha_data.values()
    
    @staticmethod
    def get_additional_gachaticket_nums(model_mgr, uid, tickettypelist, using=settings.DB_DEFAULT):
        """新規追加ガチャチケット所持数.
        """
        idlist = [GachaTicket.makeID(uid, tickettype) for tickettype in tickettypelist]
        modellist = BackendApi.get_model_list(model_mgr, GachaTicket, idlist, using=using)
        return dict([(model.mid, model) for model in modellist])
    
    @staticmethod
    def select_gacha_card(model_mgr, gachamaster, playdata, memories_gacha_data, continuity):
        """ガチャのカードを選別.
        """
        uid = playdata.uid
        
        # 回数別のBOX.
        special_box = {}
        if gachamaster.master.special_boxid:
            boxmaster_dict = BackendApi.get_model_dict(model_mgr, GachaBoxMaster, dict(gachamaster.master.special_boxid).values())
            for cnt,boxid in gachamaster.master.special_boxid:
                boxmaster = boxmaster_dict.get(boxid)
                if not boxmaster:
                    continue
                special_box[cnt] = boxmaster.box
        
        # BOX.
        box = GachaBox(gachamaster, playdata, special_box=special_box)
        
        # ランダム.
        rand = AppRandom(seed=playdata.seed)
        
        groupdict = {}
        
        # 思い出チケットガチャ.
        memories = False
        if memories_gacha_data is not None:
            groupmaster = GachaGroupMaster.makeInstance(0)
            groupmaster.table = memories_gacha_data
            groupdict[groupmaster.id] = GachaBoxGroup(groupmaster)
            memories = True
        
        # BOXからグループを選択.
        groupidlist = []
        tmp_playdata = playdata
        specialcounts = []

        # 引き抜きが足りない場合は （裏社会ガチャ）
        if gachamaster.consumetype == Defines.GachaConsumeType.EVENTTICKET and continuity > box.get_rest_num():
            raise CabaretError(u'引き抜きの数が足りません', CabaretError.Code.NOT_ENOUGH)

        for cnt in xrange(continuity):
            if box.is_empty:
                if gachamaster.consumetype in {Defines.GachaConsumeType.MINI_BOX,
                                               Defines.GachaConsumeType.MINI_BOX2,
                                               Defines.GachaConsumeType.LIMITED_RESET_BOX}:
                    tmp_playdata = GachaPlayData.makeInstance(playdata.id)
                    tmp_playdata.seed = playdata.seed
                else:
                    # 空になったのでリセット.
                    tmp_playdata.resetGroupCounts()
                box = GachaBox(gachamaster, tmp_playdata, special_box=special_box)
            groupid, is_special = box.select(rand, cnt=cnt+1)
            groupidlist.append(groupid)
            if is_special:
                specialcounts.append(cnt+1)
        if box.is_empty and gachamaster.consumetype not in {Defines.GachaConsumeType.MINI_BOX,
                                                            Defines.GachaConsumeType.MINI_BOX2,
                                                            Defines.GachaConsumeType.LIMITED_RESET_BOX,
                                                            Defines.GachaConsumeType.EVENTTICKET}:
            tmp_playdata.resetGroupCounts()
        
        # グループからカードを選択.
        groupmasterlist = BackendApi.get_gachagroupmaster_list(model_mgr, groupidlist)
        for groupmaster in groupmasterlist:
            groupdict[groupmaster.id] = GachaBoxGroup(groupmaster)

        # playercard.
        playercard = PlayerCard.getByKeyForUpdate(uid)
        model_mgr.set_got_models([playercard])
        
        # 獲得したカードのID.
        cardidlist = []
        # 獲得ランキングポイント.
        pointlist = []
        
        point_getter = lambda x : 0
        if gachamaster.consumetype == Defines.GachaConsumeType.RANKING and BackendApi.check_schedule(model_mgr, gachamaster.schedule, now=OSAUtil.get_now()):
            # スケジュールの後でも課金トランザクションは生きているのでポイントの加算をしていいのかをチェック.
            rankinggachamaster = BackendApi.get_rankinggacha_master(model_mgr, gachamaster.boxid)
            if rankinggachamaster:
                randmax = rankinggachamaster.randmax
                randmin = rankinggachamaster.randmin
                point_getter = lambda x : x.point * (100+rand.getIntN(randmin+randmax)-randmin) / 100

        for groupid in groupidlist:
            if memories and rand.getIntN(100) < Defines.GACHA_MEMORIES_MYCARD_RATE:
                # 思い出ガチャ.
                group = groupdict[0]
            else:
                group = groupdict[groupid]
            carddata = group.select_obj(rand)
            cardidlist.append(carddata.card)
            pointlist.append(point_getter(carddata))

        if gachamaster.consumetype in {Defines.GachaConsumeType.FIXEDSR, Defines.GachaConsumeType.STEPUP, Defines.GachaConsumeType.STEPUP2} and 0 < gachamaster.rarity_fixed_boxid:
            boxmaster = BackendApi.get_model(model_mgr, GachaBoxMaster, gachamaster.rarity_fixed_boxid)
            cardgroups = []
            for _ in xrange(gachamaster.rarity_fixed_num):
                cardgroup_id = boxmaster.lottery_cardgroup_id(rand)
                cardgroups.append(cardgroup_id)

            carddatagroups = BackendApi.selectcards_rarity_fixed(model_mgr, cardgroups, rand)
            for carddatagroup in carddatagroups:
                cardidlist.insert(0, carddatagroup.carddata.card)
                pointlist.insert(0, 0)
                groupidlist.insert(0, carddatagroup.group_id)
        playdata.seed = rand._seed
        return cardidlist, pointlist, groupidlist, specialcounts
    
    @staticmethod
    def selectcards_rarity_fixed(model_mgr, cardgroups, rand):
        group_masters = BackendApi.get_gachagroupmaster_list(model_mgr, cardgroups)
        group_master_dict = BackendApi.to_dict(group_masters)
        carddatas = []
        CardDataGroup = namedtuple('CardDataGroup', ('carddata', 'group_id'))
        for i,cardgroup in enumerate(cardgroups):
            group = GachaBoxGroup(group_master_dict[cardgroup])
            carddata = group.select_obj(rand)
            carddatagroup = CardDataGroup(carddata,cardgroups[i])
            carddatas.append(carddatagroup)
        return carddatas

    @staticmethod
    def to_dict(groupmasters):
        return_dict = {}
        for groupmaster in groupmasters:
            return_dict[groupmaster.id] = groupmaster
        return return_dict


    @staticmethod
    def _tr_add_gacharesult_card(model_mgr, uid, cardidlist, gachamaster, present_num, rankingpointlist, groupidlist, autosell_rarity, specialcounts):
        """ガチャ結果のカードをユーザに渡す.
        """
        playercard = PlayerCard.getByKeyForUpdate(uid)
        model_mgr.set_got_models([playercard])
        
        masters = BackendApi.get_cardmasters(cardidlist, model_mgr)
        
        rarelist = []
        presentlist = []
        resultlist = []
        if gachamaster.consumetype in Defines.GachaConsumeType.PAYMENT_TYPES:
            textid = Defines.TextMasterID.GACHA_CARD
            limittime = OSAUtil.get_datetime_max()
        else:
            textid = Defines.TextMasterID.GACHA_CARD_OVER
            limittime = None
        
        # BOXに追加できるカード枚数.
        addable_num = len(cardidlist) - present_num
        # 追加した数.
        add_num = 0
        
        autosell_cache_obj = {}
        for idx, cardid in enumerate(cardidlist):
            rankingpoint = rankingpointlist[idx]
            groupid = groupidlist[idx]
            cardmaster = masters.get(cardid)
            is_new = False
            autosell = False
            sellprice = 0
            sellprice_treasure = 0
            if add_num < addable_num or BackendApi.check_sellauto(cardmaster, autosell_rarity):
                # 追加可能 or 自動売却.
                result = BackendApi.tr_create_card(model_mgr, playercard, cardid, way=Defines.CardGetWayType.GACHA, autosell_rarity=autosell_rarity, autosell_cache_obj=autosell_cache_obj)
                is_new = result['is_new']
                autosell = result['autosell']
                if autosell:
                    # 自動退店.
                    sellprice = result['sellprice']
                    sellprice_treasure = result['sellprice_treasure']
                else:
                    add_num += 1
            else:
                present = Present.createByCard(0, uid, cardmaster, textid, limittime)
                model_mgr.set_save(present)
                presentlist.append(present)
                is_new = BackendApi.tr_set_cardacquisition(model_mgr, uid, cardmaster)
            resultlist.append({
                'id' : cardid,
                'is_new' : is_new,
                'point' : rankingpoint,
                'group' : groupid,
                'autosell' : autosell,
                'sellprice' : sellprice,
                'sellprice_treasure' : sellprice_treasure,
                'is_special' : (idx+1) in specialcounts,
            })
            if Defines.Rarity.SUPERRARE <= cardmaster.rare or settings_sub.IS_LOCAL:
                rarelist.append(cardid)
        return resultlist, rarelist, presentlist
    
    @staticmethod
    def _tr_play_gacha(model_mgr, player, gachamaster, playdata, continuity, present_num, now, autosell_rarity, is_first):
        """ガチャをプレイ.
        """
        uid = player.id
        
        # 思い出チケットガチャ処理.
        memories_gacha_data = None
        if gachamaster.consumetype == Defines.GachaConsumeType.MEMORIESTICKET:
            memories_gacha_data = BackendApi.get_memories_gacha_data(model_mgr, player.id, using=settings.DB_READONLY)
        
        # カードを選ぶ.
        cardidlist, rankingpointlist, groupidlist, specialcounts = BackendApi.select_gacha_card(model_mgr, gachamaster, playdata, memories_gacha_data, continuity)
        
        # プレイヤーにカードを渡す.
        resultlist, rarelist, presentlist = BackendApi._tr_add_gacharesult_card(model_mgr, uid, cardidlist, gachamaster, present_num, rankingpointlist, groupidlist, autosell_rarity, specialcounts)
        
        # おまけ.
        omake_prizeidlist = BackendApi._tr_add_gachabonus(model_mgr, uid, gachamaster)
        
        # 結果.
        playdata.result = {
            'result':resultlist,
            'omake':omake_prizeidlist,
        }
        
        # ミッション.
        mission_executer = PanelMissionConditionExecuter()
        mission_executer.addTargetPlayGacha(gachamaster.consumetype, 1)
        if is_first:
            mission_executer.addTargetPlayGachaFirst(gachamaster.consumetype, 1)
        BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer, now)
        
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            BackendApi.add_gachararelog(model_mgr, uid, gachamaster, rarelist, pipe=pipe)
            for present in presentlist:
                BackendApi.add_present(uid, present, pipe=pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
        
        return cardidlist, rankingpointlist


    @staticmethod
    def tr_play_gacha_boxdetail(model_mgr, cardidlist, gachamaster, playdata, using=settings.DB_READONLY):
        def forUpdateGachaResetData(model, inserted):
            model.is_get_targetrarity = True

        # cardidlist を見たら分かる
        if gachamaster.master.consumetype in {Defines.GachaConsumeType.LIMITED_RESET_BOX, Defines.GachaConsumeType.EVENTTICKET}:
            boxdetail = model_mgr.get_model(GachaBoxGachaDetailMaster, gachamaster.master.id, using=using)
            is_get_targetrarity = False
            for cardid in cardidlist:
                cardtype = int(str(cardid)[0])
                rarity = int(str(cardid)[1])
                if (boxdetail.allowreset_rarity <= rarity and cardtype in {1, 2, 3}) \
                   or cardid in boxdetail.allowreset_cardidlist:
                    is_get_targetrarity = True
            if is_get_targetrarity:
                model_mgr.add_forupdate_task(GachaBoxResetPlayerData, playdata.uid, forUpdateGachaResetData)

            boxgacha = GachaBox(gachamaster, playdata)
            if (boxgacha.rest - gachamaster.master.continuity) == 0:
                prizelist = BackendApi.get_prizemaster_list(model_mgr, boxdetail.prizelist)
                BackendApi.tr_add_prize(model_mgr, playdata.uid, prizelist, boxdetail.textid)

    @staticmethod
    def tr_play_gacha_free(model_mgr, player, gachamaster, confirmkey, continuity, now, autosell_rarity=None):
        """無料ガチャをプレイ.
        """
        uid = player.id
        mid = gachamaster.id
        boxid = gachamaster.boxid
        gachaticket = player.gachaticket
        is_payment = gachamaster.consumetype in Defines.GachaConsumeType.PAYMENT_TYPES
        if is_payment:
            raise CabaretError(u'不正アクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        
        playdata = model_mgr.get_model(GachaPlayData, GachaPlayData.makeID(uid, boxid))
        if playdata is None:
            playdata = GachaPlayData.makeInstance(GachaPlayData.makeID(uid, boxid))
        else:
            playdata = GachaPlayData.getByKeyForUpdate(GachaPlayData.makeID(uid, boxid))
        
        playcount = model_mgr.get_model(GachaPlayCount, GachaPlayCount.makeID(uid, mid))
        if playcount is None:
            playcount = GachaPlayCount.makeInstance(GachaPlayCount.makeID(uid, mid))
        else:
            playcount = GachaPlayCount.getByKeyForUpdate(GachaPlayCount.makeID(uid, mid))
        
        model_mgr.set_got_models([playdata, playcount])
        
        seatmodels = BackendApi.get_gachaseatmodels_by_gachamaster(model_mgr, uid, gachamaster, for_update=True)
        
        play_cnt = 1
        is_first = 0 < BackendApi.get_gacha_firstplay_restnum(gachamaster, playcount, now, seatplaydata=seatmodels.get('playdata'))
        true_continuity = BackendApi.get_gacha_continuity_num(model_mgr, gachamaster, player, is_first)

        # 枚数チェック.
        cardlimit = player.cardlimit
        cardnum = BackendApi.get_cardnum(uid, model_mgr)
        if cardlimit <= cardnum:
            raise CabaretError(u'在籍キャストがいっぱいです', CabaretError.Code.OVER_LIMIT)
        present_num = max(0, cardnum + continuity - cardlimit)
        
        # 回数確認.
        topic = Defines.GachaConsumeType.TO_TOPIC.get(gachamaster.consumetype)
        if gachamaster.consumetype in (Defines.GachaConsumeType.GACHAPT, Defines.GachaConsumeType.TRYLUCKTICKET) or topic in (Defines.GachaConsumeType.GachaTopTopic.TICKET, Defines.GachaConsumeType.GachaTopTopic.SCOUTEVENT):
            if true_continuity < continuity and not settings_sub.IS_BENCH:
                raise CabaretError(u'うまく実行できませんでした', CabaretError.Code.ILLEGAL_ARGS)
            play_cnt = continuity
        elif true_continuity != continuity:
            raise CabaretError(u'うまく実行できませんでした', CabaretError.Code.ILLEGAL_ARGS)
        
        # 消費.
        consumevalue = BackendApi.tr_consume_by_gachamaster(model_mgr, uid, gachamaster, continuity, is_first, gachaticket >= Defines.GACHA_TICKET_COST_NUM, seatplaydata=seatmodels.get('playdata'))
        
        # ガチャをプレイ.
        cardidlist, rankingpointlist = BackendApi._tr_play_gacha(model_mgr, player, gachamaster, playdata, continuity, present_num, now, autosell_rarity, is_first)

        boxdetail = model_mgr.get_model(GachaBoxGachaDetailMaster, gachamaster.master.id, using=settings.DB_READONLY)
        if isinstance(boxdetail, GachaBoxGachaDetailMaster):
            BackendApi.tr_play_gacha_boxdetail(model_mgr, cardidlist, gachamaster, playdata, using=settings.DB_READONLY)
        
        # シート報酬.
        seat_prizeid, seat_last = BackendApi.tr_receive_gachaseat_prize(model_mgr, uid, gachamaster, seatmodels.get('seatmaster'), seatmodels.get('playdata'), seatmodels.get('playcount'))
        
        # ランキングポイントの加算.
        point_single = sum(rankingpointlist)
        point_total = 0
        point_whole = 0
        if 0 < point_single:
            point_total, point_whole = BackendApi.tr_save_rankinggacha_score(model_mgr, uid, gachamaster.boxid, point_single)
            playdata.result['point_whole'] = point_whole
        
        # ログ.
        model_mgr.set_save(UserLogGacha.create(uid, mid, continuity, consumevalue, is_first, cardidlist, seat_prizeid, point_single, point_total, point_whole, seat_last))
        
        playcount.addPlayCnt(play_cnt, now)
        
        model_mgr.set_save(playcount)
        model_mgr.set_save(playdata)
        
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            if is_first and gachamaster.consumetype == Defines.GachaConsumeType.GACHAPT:
                BackendApi.save_freegachalasttime(uid, now, pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
        
        return cardidlist
    
    @staticmethod
    def tr_play_gacha_pay(model_mgr, player, paymentId, is_pc, do_update_key=True, autosell_rarity=None, player_trade_point=None):
        """課金ガチャを回す.
        """
        uid = player.id
        
        # 課金ステータスを更新.
        entry = BackendApi.tr_update_gachapaymententry(model_mgr, uid, paymentId, PaymentData.Status.COMPLETED)
        gachamaster = BackendApi.get_gachamaster(model_mgr, entry.iid)
        mid = gachamaster.id
        boxid = gachamaster.boxid
        if gachamaster.stepid > 0:
            g = BackendApi.get_gachamaster(model_mgr, gachamaster.stepsid)
            mid = g.id
        
        # 課金レコードがあるのでキーのチェックはしない.
        if do_update_key:
            playerrequest = BackendApi.tr_update_requestkey(model_mgr, uid, None, force=True)
            player.setModel(playerrequest)
        
        pkey = GachaPlayData.makeID(uid, boxid)
        playdata = model_mgr.get_model(GachaPlayData, pkey)
        if playdata is None:
            playdata = GachaPlayData.makeInstance(pkey)
        else:
            playdata = GachaPlayData.getByKeyForUpdate(pkey)
        
        playcount = model_mgr.get_model(GachaPlayCount, GachaPlayCount.makeID(uid, mid))
        if playcount is None:
            playcount = GachaPlayCount.makeInstance(GachaPlayCount.makeID(uid, mid))
        else:
            playcount = GachaPlayCount.getByKeyForUpdate(GachaPlayCount.makeID(uid, mid))
        
        model_mgr.set_got_models([playdata, playcount])
        
        # ガチャをプレイ.
        continuity = entry.continuity
        cardlimit = player.cardlimit
        cardnum = BackendApi.get_cardnum(uid, model_mgr)
        present_num = max(0, cardnum + continuity + gachamaster.rarity_fixed_num - cardlimit)
        is_first = 0 < BackendApi.get_gacha_firstplay_restnum(gachamaster, playcount)
        cardidlist, rankingpointlist = BackendApi._tr_play_gacha(model_mgr, player, gachamaster, playdata, continuity, present_num, entry.ctime, autosell_rarity, is_first)

        # Box ガチャのリセットフラグ条件確認と Box が空の時の報酬配布処理.
        boxdetail = model_mgr.get_model(GachaBoxGachaDetailMaster, gachamaster.master.id, using=settings.DB_READONLY)
        if isinstance(boxdetail, GachaBoxGachaDetailMaster):
            BackendApi.tr_play_gacha_boxdetail(model_mgr, cardidlist, gachamaster, playdata, using=settings.DB_READONLY)

        # シート報酬.
        seatmodels = BackendApi.get_gachaseatmodels_by_gachamaster(model_mgr, uid, gachamaster, for_update=True)
        seat_prizeid, seat_last = BackendApi.tr_receive_gachaseat_prize(model_mgr, uid, gachamaster, seatmodels.get('seatmaster'), seatmodels.get('playdata'), seatmodels.get('playcount'))
        
        # ランキングポイントの加算.
        point_single = sum(rankingpointlist)
        point_total = 0
        point_whole = 0
        if 0 < point_single:
            point_total, point_whole = BackendApi.tr_save_rankinggacha_score(model_mgr, uid, gachamaster.boxid, point_single)
            playdata.result['point_whole'] = point_whole

        # ポイントが付与されるガチャなら。
        if gachamaster.trade_shop_master_id > 0 and gachamaster.point_rate:
            #もし課金レコードが中断されてtop.pyから来た為に、player_trade_pointがNoneなら
            if player_trade_point is None:
                player_trade_point = BackendApi.lottery_rates(gachamaster.point_rate)

            player_trade_shop = BackendApi.find_or_create_instance_PlayerTradeShop(model_mgr, player.id,gachamaster.trade_shop_master_id)
            player_trade_shop.point += player_trade_point;
            model_mgr.set_save(player_trade_shop)

        # ログ.
        model_mgr.set_save(UserLogGacha.create(uid, mid, continuity, entry.price, entry.price == gachamaster.consumefirstvalue, cardidlist, seat_prizeid, point_single, point_total, point_whole, seat_last))

        def is_infinity_lap():
            return setpupmaster.lapdaymax == 0

        if gachamaster.stepid > 0:
            now = OSAUtil.get_now()
            BackendApi.stepup_reset(model_mgr, gachamaster, playcount,now)
            setpupmaster = BackendApi.get_gachastepupmaster(model_mgr, gachamaster.stepid, using=settings.DB_READONLY)
            if (setpupmaster.stepreset
                and not BackendApi.is_resettime_over(entry.ctime,setpupmaster.stepresettime,now)) \
                or is_infinity_lap():
                playcount.step += 1
                playcount.steptotal += 1

            if playcount.step >= setpupmaster.stepmax:
                if is_infinity_lap() or (playcount.lap + 1) < setpupmaster.lapdaymax:
                    playcount.lap += 1
                    playcount.laptotal += 1
                    playcount.step = 0
                else:
                    playcount.step = setpupmaster.stepmax - 1
            if setpupmaster.lapdaymax > 0:
                if playcount.lap >= setpupmaster.lapdaymax:
                    playcount.lap -= 1
                    playcount.laptotal -= 1
                    playcount.step = setpupmaster.stepmax - 1
        
        # プレイ回数を増やす.
        playcount.addPlayCnt(1, entry.ctime)
        
        model_mgr.set_save(playdata)
        model_mgr.set_save(playcount)
        
        # 消費ポイントを加算.
        def forUpdateGachaConsumePoint(model, inserted):
            model.point += entry.price * entry.inum
        model_mgr.add_forupdate_task(GachaConsumePoint, GachaConsumePoint.makeID(uid, mid), forUpdateGachaConsumePoint)
        
        def forUpdatePlayerConsumePoint(model, inserted):
            model.point_total += entry.price * entry.inum
        model_mgr.add_forupdate_task(PlayerConsumePoint, uid, forUpdatePlayerConsumePoint)
        
        playerlogin = BackendApi.get_model(model_mgr, PlayerLogin, uid)
        
        def writeEnd():
            leader = BackendApi.get_leaders([uid], model_mgr, using=settings.DB_READONLY)[uid]
            
            ope = KpiOperator()
            now = OSAUtil.get_now()
            if playerlogin and 5 <= playerlogin.ldays:
                ope.set_save_payment_fq5(uid, gachamaster.id, now)
            ope.set_save_gacha_laststep(uid, mid, gachamaster.step, now)
            ope.set_save_gacha_play(uid, is_pc, entry.inum*entry.price, now)
            if gachamaster.consumetype in Defines.GachaConsumeType.PREMIUM_TYPES:
                ope.set_save_paymentgacha_playerdata(uid, mid, leader.master.id, now)
            ope.save()
        model_mgr.add_write_end_method(writeEnd)
        
        return cardidlist, entry

    @staticmethod
    def find_or_create_instance_PlayerTradeShop(model_mgr, user_id, trade_shop_master_id):
        player_tradeshop = model_mgr.get_model(PlayerTradeShop, user_id, False, using=settings.DB_DEFAULT)
        if player_tradeshop is None:
            player_tradeshop = PlayerTradeShop.createInstance(user_id)
        return player_tradeshop

    @staticmethod
    def lottery_rates(rates):
        random.seed(time.time())

        lottery = sum([int(data['rate']) for data in rates])
        randint = random.randint(0, lottery)

        total_rate = 0
        for data in rates:
            total_rate += int(data['rate'])
            if randint < total_rate:
                return int(data['point'])

    @staticmethod
    def tr_reset_gachaboxplaydata(model_mgr, uid, box_id, confirmkey):
        """BOXの中身をリセット.
        """
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)

        def forUpdate(model, inserted):
            model.counts = {}
        model_mgr.add_forupdate_task(GachaPlayData, GachaPlayData.makeID(uid, box_id), forUpdate)

        def forUpdateGachaResetData(model, inserted):
            model.resetcount += 1
            model.is_get_targetrarity = False
        model_mgr.add_forupdate_task(GachaBoxResetPlayerData, uid, forUpdateGachaResetData)
        
        def forUpdateResetGachaPlayCount(model, inserted):
            model.cnt = 0
            model.cnttotal = 0
        gachamasterlist = BackendApi.get_playablegacha_list(model_mgr, using=settings.DB_READONLY)
        gachamaster_ids = [master.id for master in gachamasterlist if master.boxid == box_id]
        if len(gachamaster_ids) != 1:
            raise CabaretError(u'box_idとgachamasterの整合性がおかしいです', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr.add_forupdate_task(GachaPlayCount, GachaPlayCount.makeID(uid, gachamaster_ids[0]), forUpdateResetGachaPlayCount)

    @staticmethod
    def tr_reset_gachaseatplaydata(model_mgr, uid, gachamaster):
        """シートをリセット.
        """
        seatmodels = BackendApi.get_gachaseatmodels_by_gachamaster(model_mgr, uid, gachamaster, for_update=True)
        playcount = seatmodels.get('playcount')
        playdata = seatmodels.get('playdata')
        
        if playdata is None or playdata.is_first():
            raise CabaretError(u'リセット済みです', CabaretError.Code.ALREADY_RECEIVED)
        
        playdata.clearFlags()
        playcount.lap += 1
        
        model_mgr.set_save(playdata)
        model_mgr.set_save(playcount)
    
    @staticmethod
    def count_gachaseat_stampnum(seatmaster, seatplaydata):
        idx = 0
        
        t = 0
        f = 0
        
        while True:
            prizeid = seatmaster.getPrizeId(idx)
            if prizeid is None:
                break
            weight = seatmaster.getWeight(idx)
            if prizeid and weight:
                if seatplaydata and seatplaydata.getFlag(idx):
                    t += 1
                else:
                    f += 1
            idx += 1
        
        return t, f
    
    @staticmethod
    def tr_receive_gachaseat_prize(model_mgr, uid, gachamaster, seatmaster, playdata, playcount):
        """シートガチャ報酬受取.
        """
        if seatmaster is None:
            return None, None
        
        rand = AppRandom()
        rand.setSeed(playdata.seed)
        idx = seatmaster.select(playdata, rand)
        if idx is None:
            return None, None
        
        prizeid = seatmaster.getPrizeId(idx)
        prizelist = BackendApi.get_prizelist(model_mgr, [prizeid])
        BackendApi.tr_add_prize(model_mgr, uid, prizelist, seatmaster.textid)
        
        playdata.seed = rand._seed
        playdata.last = idx
        if gachamaster.consumetype != Defines.GachaConsumeType.MINI_SEAT or playcount.lap == 0:
            playdata.setFlag(idx, True)
            
            _, restnum = BackendApi.count_gachaseat_stampnum(seatmaster, playdata)
            if restnum < 1:
                playdata.clearFlags()
                playcount.lap += 1
        
        model_mgr.set_save(playcount)
        model_mgr.set_save(playdata)
        
        return prizeid, playdata.last
    
    @staticmethod
    def add_gachararelog(model_mgr, uid, gachamaster, midlist, pipe=None):
        """レアキャバ嬢獲得履歴.
        """
        if len(midlist) < 1:
            return
        
        boxid = gachamaster.boxid
        if gachamaster.stepsid:
            tmp = BackendApi.get_gachamaster(model_mgr, gachamaster.stepsid, using=settings.DB_READONLY)
            if tmp:
                boxid = tmp.boxid
        
        now = OSAUtil.get_now()
        modellist = [RareLogList.create(boxid, gachamaster.id, uid, mid, now) for mid in midlist]
        RareLogList.save_many(modellist, pipe)
    
    @staticmethod
    def get_gachararelog(gacha_boxid, num=2):
        """レアキャバ嬢獲得履歴を取得.
        """
        return RareLogList.fetch(gacha_boxid, limit=num)
    
    @staticmethod
    def get_playablegacha_list(model_mgr, using=settings.DB_READONLY, now=None):
        """開催中のガチャ.
        """
        gachamasterlist = model_mgr.get_mastermodel_all(GachaMaster, using=using)
        scheduleid_list = list(set([gachamaster.schedule for gachamaster in gachamasterlist]))
        schedule_flags = BackendApi.check_schedule_many(model_mgr, scheduleid_list, using=using, now=now)
        
        gachamasters = [gachamaster for gachamaster in gachamasterlist if schedule_flags.get(gachamaster.schedule, True)]
        boxidlist = list(set([gachamaster.boxid for gachamaster in gachamasters]))
        gachaboxmastersdict = BackendApi.get_model_dict(model_mgr, GachaBoxMaster, boxidlist, using=using)
        
        result = []
        for gachamaster in gachamasters:
            if gachaboxmastersdict.has_key(gachamaster.boxid):
                gachabox = gachaboxmastersdict[gachamaster.boxid]
                schedulemaster = BackendApi.get_schedule_master(model_mgr, gachamaster.schedule, using=using)
                result.append(GachaMasterSet(gachamaster, gachabox, schedulemaster))
        
        return result
    
    @staticmethod
    def get_playablegacha_list_by_consumetype(model_mgr, consumetype, using=settings.DB_READONLY, now=None):
        """開催中のガチャ.
        """
        client = localcache.Client()
        namespace = 'GachaMaster'
        key = "get_gacha_by_consumetype:%s" % consumetype
        mid_list = client.get(key, namespace)
        
        if mid_list is None:
            gachamasterlist = GachaMaster.fetchValues(filters={'consumetype':consumetype}, using=using)
            mid_list = [gachamaster.id for gachamaster in gachamasterlist]
            client.set(key, mid_list, namespace)
        else:
            gachamasterlist = BackendApi.get_gachamaster_list(model_mgr, mid_list, using=using)
        
        gachamasters = [gachamaster for gachamaster in gachamasterlist if BackendApi.check_schedule(model_mgr, gachamaster.schedule, using=using, now=now)]
        boxidlist = list(set([gachamaster.boxid for gachamaster in gachamasters]))
        gachaboxmastersdict = BackendApi.get_model_dict(model_mgr, GachaBoxMaster, boxidlist, using=using)
        
        result = []
        for gachamaster in gachamasters:
            if gachaboxmastersdict.has_key(gachamaster.boxid):
                gachabox = gachaboxmastersdict[gachamaster.boxid]
                schedulemaster = BackendApi.get_schedule_master(model_mgr, gachamaster.schedule, using=using)
                result.append(GachaMasterSet(gachamaster, gachabox, schedulemaster))
        
        return result
    
    @staticmethod
    def make_gachaseatinfo(handler, uid, gachamaster, result=False, using=settings.DB_READONLY):
        """シートガチャ情報.
        """
        model_mgr = handler.getModelMgr()

        seatmodels = BackendApi.get_gachaseatmodels_by_gachamaster(model_mgr, uid, gachamaster, do_get_result=result, using=using)
        seatmaster = seatmodels.get('seatmaster')
        if seatmaster is None:
            return None

        seattablemaster = seatmodels.get('tablemaster')
        seatplaycount = seatmodels.get('playcount')
        seatplaydata = seatmodels.get('playdata')

        if result and seatplaydata is not None and seatplaycount is not None and seatplaydata.is_first() and 0 < seatplaycount.lap:
            seatid = seattablemaster.getSeatId(seatplaycount.lap)
            seatmaster = BackendApi.get_gachaseatmaster(model_mgr, seatid, using=using)

        flags = {}
        prize_map = {}
        idx = 0
        allempty = True
        allend = True

        while True:
            prizeid = seatmaster.getPrizeId(idx)
            if prizeid is None:
                break
            weight = seatmaster.getWeight(idx)
            if prizeid and weight:
                if seatplaydata and seatplaydata.getFlag(idx):
                    allempty = False
                    flags[idx] = True
                else:
                    allend = False
                    flags[idx] = False
                prize_map[prizeid] = None
            idx += 1

        if allempty and (seatplaycount and 0 < seatplaycount.lap):
            allend = True

        for prizemaster in BackendApi.get_prizemaster_list(model_mgr, prize_map.keys(), using=settings.DB_READONLY):
            prize_map[prizemaster.id] = PrizeData.createByMaster(prizemaster)

        presentsetlist = []
        for i in xrange(idx):
            flag = flags.get(i, None)
            if flag is None:
                presentsetlist.append(None)
                continue

            prizeid = seatmaster.getPrizeId(i)
            prize = prize_map.get(prizeid)
            if not prize:
                presentsetlist.append(None)
                continue

            presentlist = BackendApi.create_present_by_prize(model_mgr, uid, [prize], 0, using=settings.DB_READONLY, do_set_save=False)
            if not presentlist:
                presentsetlist.append(None)
                continue

            thumb = seatmaster.getThumb(i)
            presentlist = presentlist[:1]
            presentset = PresentSet.presentToPresentSet(model_mgr, presentlist, using=settings.DB_READONLY)[0]
            presentsetlist.append((presentset, thumb))

        return Objects.gachaseat(handler, gachamaster, seattablemaster, presentsetlist, seatplaycount, seatplaydata, allend and (result or gachamaster.consumetype == Defines.GachaConsumeType.MINI_SEAT))

    @staticmethod
    def stepup_reset(model_mgr, gachamaster, playcount,now):
        """ステップアップガチャリセット.
        """
        if gachamaster.stepid > 0:
            stepup = BackendApi.get_gachastepupmaster(model_mgr, gachamaster.stepid, using=settings.DB_READONLY)

            if stepup.stepreset:
                if BackendApi.is_resettime_over(playcount.ptime,stepup.stepresettime,now):
                    playcount.step = 0
                    playcount.lap += 1
                    playcount.laptotal += 1

            if stepup.lapreset:
                if BackendApi.is_resettime_over(playcount.ptime,stepup.lapresettime,now):
                    playcount.step = 0
                    playcount.steptotal = 0
                    playcount.lap = 0
                    playcount.laptotal = 0
        return

    @staticmethod
    def is_resettime_over(base_time,reset_time,check_time):
        pt = base_time - datetime.timedelta(0, reset_time)
        pt += datetime.timedelta(1)
        dt = datetime.datetime(pt.year, pt.month, pt.day, 0, 0, 0)
        dt = dt.replace(tzinfo=timezone.TZ_DEFAULT)##base_timeの次の日の0:00になる
        dt += datetime.timedelta(0, reset_time)
        if dt <= check_time:
            return True
        return False

    @staticmethod
    def put_gachahtmldata(handler, gachamasterlist, topic=None, result_gachamaster=None, do_put_rare_log=True):
        """HTML用ガチャ表示パラメータを埋め込む.
        """
        model_mgr = handler.getModelMgr()
        v_player = handler.getViewerPlayer()
        uid = v_player.id
        
        overlimit = v_player.cardlimit <= BackendApi.get_cardnum(uid, model_mgr, using=settings.DB_READONLY)
        
        # 課金のトピックだけを埋め込むかのフラグ.
        is_payment_topic_only = topic is not None and topic in Defines.GachaConsumeType.GachaTopTopic.PAYMENT_TOPICS
        
        # 開催中のガチャ情報.
        gachadata = {}
        
        # イベントガチャ名.
        event_gacha_unique_name = None
        if topic is None or topic == Defines.GachaConsumeType.GachaTopTopic.TICKET:
            cur_eventmaster = BackendApi.get_current_ticket_raideventmaster(model_mgr, using=settings.DB_READONLY)
            if cur_eventmaster:
                # チケット所持数.
                scorerecord = BackendApi.get_raidevent_scorerecord(model_mgr, cur_eventmaster.id, v_player.id, using=settings.DB_READONLY)
                handler.html_param['raideventscore'] = Objects.raidevent_score(cur_eventmaster, scorerecord, None)
                handler.html_param['url_eventgacha_cast'] = handler.makeAppLinkUrl(UrlMaker.raidevent_gachacast(cur_eventmaster.id))
                
                event_gacha_unique_name = cur_eventmaster.gachaname
        
        # スカウトイベント.
        scoutevent_gacha_unique_name = None
        if topic is None or topic == Defines.GachaConsumeType.GachaTopTopic.SCOUTEVENT:
            config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
            cur_eventmaster = BackendApi.get_scouteventmaster(model_mgr, config.mid, using=settings.DB_READONLY) if config.mid else None
            if cur_eventmaster and config.starttime <= OSAUtil.get_now() <= config.present_endtime:
                # イベントアイテム所持数.
                scorerecord = BackendApi.get_scoutevent_scorerecord(model_mgr, cur_eventmaster.id, v_player.id, using=settings.DB_READONLY)
                handler.html_param['scouteventscore'] = Objects.scoutevent_score(scorerecord)
                
                scoutevent_gacha_unique_name = cur_eventmaster.gachaname
                
                handler.html_param['scoutevent_gacha_stime'] = config.starttime
                handler.html_param['scoutevent_gacha_etime'] = config.present_endtime if config.endtime < OSAUtil.get_now() else None
                
                handler.html_param['url_scoutevent_top'] = handler.makeAppLinkUrl(UrlMaker.scoutevent_top(cur_eventmaster.id))
                
                if handler.html_param.get('scoutevent') is None:
                    handler.html_param['scoutevent'] = Objects.scouteventmaster(handler, cur_eventmaster, config)
        
        midlist = []
        boxidlist = []
        flag_step = False
        gm = []
        for gachamaster in gachamasterlist:
            tmp_topic = Defines.GachaConsumeType.TO_TOPIC.get(gachamaster.consumetype)
            
            if topic is not None and topic != tmp_topic and (not is_payment_topic_only or not tmp_topic in Defines.GachaConsumeType.GachaTopTopic.PAYMENT_TOPICS):
                continue
            elif not is_payment_topic_only and result_gachamaster and result_gachamaster.id != gachamaster.id:
                # 課金以外は指定したものだけ.
                continue
            elif is_payment_topic_only and result_gachamaster and result_gachamaster.stepid <= 0 and result_gachamaster.boxid != gachamaster.boxid:
                # 課金は同じBOXだけ（ステップアップガチャ以外）.
                continue
            elif is_payment_topic_only and result_gachamaster and result_gachamaster.stepid > 0 and result_gachamaster.stepid != gachamaster.stepid:
                # 課金ステップアップガチャは同じステップアップガチャだけ.
                continue
            elif gachamaster.consumetype == Defines.GachaConsumeType.EVENTTICKET and (event_gacha_unique_name is None or event_gacha_unique_name != gachamaster.unique_name):
                # イベントガチャは期間中だけ.
                continue
            elif gachamaster.consumetype == Defines.GachaConsumeType.SCOUTEVENT and (scoutevent_gacha_unique_name is None or gachamaster.unique_name.find(scoutevent_gacha_unique_name) != 0):
                # イベントガチャは期間中だけ.
                continue
            
            if gachamaster.stepid <= 0:
                midlist.append(gachamaster.id)
                boxidlist.append(gachamaster.boxid)
            else:
                # ステップアップガチャ
                if gachamaster.step == 1:
                    midlist.append(gachamaster.id)
                boxidlist.append(gachamaster.boxid)
                flag_step = True
            gm.append(gachamaster)
        gachamasterlist = gm
        
        playdatas = BackendApi.get_gachaplaydata(model_mgr, uid, boxidlist, using=settings.DB_READONLY, get_instance=True)
        playcounts = BackendApi.get_gachaplaycount(model_mgr, uid, midlist, using=settings.DB_READONLY, get_instance=True)
        
        if flag_step:
            gm = []
            for gachamaster in gachamasterlist:
                if gachamaster.stepid <= 0:
                    gm.append(gachamaster)
                else:
                    if gachamaster.step == 1:
                        playcount = playcounts.get(gachamaster.id)
                        if playcount:
                            BackendApi.stepup_reset(model_mgr, gachamaster, playcount,OSAUtil.get_now())
                            step = playcount.step + 1
                        else:
                            step = 1
                        stepupmasters = filter(lambda x: x.consumetype in {
                            Defines.GachaConsumeType.STEPUP,
                            Defines.GachaConsumeType.STEPUP2
                        } and x.step == step and gachamaster.stepid == x.stepid, gachamasterlist)
                        for g in stepupmasters:
                            gm.append(g)
            gachamasterlist = gm

        box_dict = {}
        seat_dict = {}
        
        gacha_type_counts = {}
        
        # 開催時間でソート.
        gachamasterlist.sort(key=lambda x:x.id, reverse=True)
        gachamasterlist.sort(key=lambda x:x.schedulemaster.stime if x.schedulemaster else OSAUtil.get_datetime_min(), reverse=True)
        
        # オリジナルのタブを含ませる.
        gacha_consumetype_names = dict(Defines.GachaConsumeType.NAMES)
        handler.html_param['gacha_consumetype_names'] = gacha_consumetype_names
        tabname_to_consumetype = {}
        handler.html_param['tabname_to_consumetype'] = tabname_to_consumetype
        
        # 優先順位.
        premium_priority = []
        premium_payment_num = 0
        
        addsocardflgs = {}
        
        # レアキャスト獲得情報.
        rarecast_logs = {}
        rarelog_uidlist = []
        rarelog_midlist = []
        
        # ランキングガチャ.
        rankingdata = {}
        
        # おまけガチャのおまけ.
        omakedata = {}
        
        playable_masterlist = []
        for gachamaster in gachamasterlist:
            playdata = playdatas.get(gachamaster.boxid)
            tmp_topic = Defines.GachaConsumeType.TO_TOPIC.get(gachamaster.consumetype)
            
            if tmp_topic == topic and gachamaster.addsocardflg:
                # トピックが一致していて特効フラグがたっている.
                dic = addsocardflgs[gachamaster.consumetype] = addsocardflgs.get(gachamaster.consumetype) or {}
                dic[gachamaster.unique_name] = gachamaster.name
            
            gacha_type_counts[gachamaster.consumetype] = gacha_type_counts.get(gachamaster.consumetype, 0) + 1
            if gachamaster.consumetype in Defines.GachaConsumeType.PREMIUM_TYPES:
                if gachamaster.tabengname and gachamaster.tabname:
                    tab = gachamaster.tabengname
                    gacha_consumetype_names[gachamaster.tabengname] = gachamaster.tabname
                    tabname_to_consumetype[gachamaster.tabengname] = gachamaster.consumetype
                else:
                    tab = gachamaster.consumetype
                
                if not tab in premium_priority:
                    premium_priority.append(tab)
                premium_payment_num += 1
            
            tmp = box_dict.get(gachamaster.boxid)
            if tmp is None:
                gachabox = GachaBox(gachamaster, playdata, blank=True)
                
                boxgrouplist = None
                boxraremap = None
                raremin = None
                if gachabox.is_boxgacha:
                    groupmasterdict = BackendApi.get_gachagroupmaster_dict(model_mgr, gachabox.get_group_id_list(), using=settings.DB_READONLY)
                    
                    boxgrouplist = []
                    boxraremap = {}
                    
                    for groupdata in gachabox.get_groupdata_list():
                        groupid = groupdata.group
                        gachagroupmaster = groupmasterdict[groupid]
                        restnum = gachabox.get_group_restnum(groupid)
                        totalnum = gachabox.get_group_totalnum(groupid)
                        obj_card = None
                        if len(gachagroupmaster.table) == 1:
                            # 固定.
                            data = GachaBoxCardData.createByTableData(gachagroupmaster.table[0])
                            cardmaster = BackendApi.get_cardmasters([data.card], model_mgr, using=settings.DB_READONLY).get(data.card)
                            card = BackendApi.create_card_by_master(cardmaster)
                            obj_card = Objects.card(handler, CardSet(card, cardmaster))
                        boxgrouplist.append(Objects.boxGroup(handler, gachagroupmaster, totalnum, restnum, obj_card))
                        
                        miniboxnums = boxraremap[gachagroupmaster.rare] = boxraremap.get(gachagroupmaster.rare) or dict(totalnum=0, restnum=0)
                        miniboxnums['totalnum'] += totalnum
                        miniboxnums['restnum'] += restnum
                        
                        if raremin:
                            raremin = min(gachagroupmaster.rare, raremin)
                        else:
                            raremin = gachagroupmaster.rare
                banner = None
                if gachamaster.boxmaster.banner:
                    banner = handler.makeAppLinkUrlImg(gachamaster.boxmaster.banner)
                tmp = (gachabox, boxgrouplist, banner, raremin, boxraremap)
                box_dict[gachamaster.boxid] = tmp
                
                if gachamaster.consumetype == Defines.GachaConsumeType.RANKING and not rankingdata.has_key(gachamaster.boxid):
                    cb = BackendApi.make_rankinggacha_ranking(handler, gachamaster, False, 3, do_execute_api=False, single=True)
                    if cb is not None:
                        rankingdata[gachamaster.boxid] = {
                            'single' : {
                                'data' : cb,
                                'url' : handler.makeAppLinkUrl(UrlMaker.gacharanking(gachamaster.id, True, False)),
                            },
                            'total' : {
                                'data' : BackendApi.make_rankinggacha_ranking(handler, gachamaster, False, 3, do_execute_api=False, single=False),
                                'url' : handler.makeAppLinkUrl(UrlMaker.gacharanking(gachamaster.id, False, False)),
                            },
                            'url_prize' : handler.makeAppLinkUrl(UrlMaker.gacharankingprize(gachamaster.id, is_single=True)),
                            'url_wholeprize' : handler.makeAppLinkUrl(UrlMaker.gacharankingprize(gachamaster.id, is_single=False, is_whole=True)),
                        }
            else:
                gachabox, boxgrouplist, banner, raremin, boxraremap = tmp
            
            if not seat_dict.has_key(gachamaster.seattableid):
                seat_dict[gachamaster.seattableid] = BackendApi.make_gachaseatinfo(handler, v_player.id, gachamaster, using=settings.DB_READONLY)
            seatinfo = seat_dict[gachamaster.seattableid]
            
            omake = None
            if gachamaster.bonus:
                if isinstance(gachamaster.bonus[0], dict):
                    arr = omakedata[gachamaster.boxid] = omakedata.get(gachamaster.boxid) or [[], []]
                    arr[0].append('%s' % gachamaster.id)
                    arr[1].append('%s' % gachamaster.unique_name)
                else:
                    prizelist = BackendApi.get_prizelist(model_mgr, gachamaster.bonus, using=settings.DB_READONLY)
                    prizeinfo = BackendApi.make_prizeinfo(handler, prizelist, using=settings.DB_READONLY)
                    omake = prizeinfo
            
            stepup = None
            gachamasterstep = None
            gmid = gachamaster.id
            if gachamaster.stepid > 0:
                stepup = BackendApi.get_gachastepupmaster(model_mgr, gachamaster.stepid, using=settings.DB_READONLY)
                if gachamaster.stepsid > 0:
                    if gachamaster.stepsid != gachamaster.id:
                        gachamasterstep = BackendApi.get_gachamaster(model_mgr, gachamaster.stepsid, using=settings.DB_READONLY)
                        if gachamasterstep:
                            gmid = gachamasterstep.id
            
            gachadata[gachamaster.unique_name] = Objects.gacha(handler, gachamaster, v_player, playcounts.get(gmid), gachabox, boxgrouplist, omake, banner, stepup, raremin, boxraremap, seatinfo=seatinfo)
            playable_masterlist.append(gachamaster)
            
            if not rarecast_logs.has_key(gachamaster.boxid):
                # レアキャスト情報.
                boxid = gachamasterstep.boxid if gachamasterstep else gachamaster.boxid
                rareloglist = BackendApi.get_gachararelog(boxid, num=4)
                rarecast_logs[gachamaster.boxid] = rareloglist
                for rarelog in rareloglist:
                    rarelog_uidlist.append(rarelog.uid)
                    rarelog_midlist.append(rarelog.mid)
        
        # レアキャスト取得.
        if do_put_rare_log:
            rarelog_uidlist = list(set(rarelog_uidlist))
            rarelog_midlist = list(set(rarelog_midlist))
            rarelog_playerlist = BackendApi.get_players(handler, rarelog_uidlist, [], using=settings.DB_READONLY)
            rarelog_playerdict = dict([(player.id, player) for player in rarelog_playerlist])
            persons = BackendApi.get_dmmplayers(handler, rarelog_playerdict.values(), using=settings.DB_READONLY, do_execute=False)
        # カード.
        rarelog_cardmasters = BackendApi.get_cardmasters(rarelog_midlist, model_mgr, using=settings.DB_READONLY)
        
        BackendApi.put_gachaslidecarddata(handler, playable_masterlist)
        BackendApi.put_gachaheaderdata(handler, playable_masterlist)
        
        handler.html_param['gachadata'] = gachadata
        handler.html_param['num_key'] = Defines.URLQUERY_NUMBER
        handler.html_param['overlimit'] = overlimit
        
        raideventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
        obj_raidevent = None
        if raideventmaster:
            config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
            obj_raidevent = Objects.raidevent(handler, raideventmaster, config)
        handler.html_param['raidevent'] = obj_raidevent
        
        handler.html_param['event_gacha_unique_name'] = event_gacha_unique_name
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        event_gacha_stime = config.starttime
        event_gacha_etime = config.ticket_endtime
        handler.html_param['event_gacha_stime'] = event_gacha_stime
        handler.html_param['event_gacha_etime'] = event_gacha_etime
        
        handler.html_param['scoutevent_gacha_unique_name'] = scoutevent_gacha_unique_name
        
        # ううん..これは..
        handler.html_param['premium_payment_num'] = premium_payment_num
        handler.html_param['gacha_type_counts'] = gacha_type_counts
        handler.html_param['gacha_premium_priority'] = premium_priority
        
        # チケット所持数.
        tickettypelist = [Defines.GachaConsumeType.ADDITIONAL_TICKETS[k] for k in list(set(gacha_type_counts.keys()) & set(Defines.GachaConsumeType.ADDITIONAL_TICKETS.keys()))]
        ticketnums = dict.fromkeys(tickettypelist, 0)
        if tickettypelist:
            num_models = BackendApi.get_additional_gachaticket_nums(model_mgr, v_player.id, tickettypelist, using=settings.DB_READONLY)
            for num_model in num_models.values():
                ticketnums[num_model.mid] = num_model.num
        handler.html_param['gacha_ticket_nums'] = ticketnums
        
        # レアキャスト情報埋め込み.
        gachaNews_uniquename = {}
        gachaNews_topics = {}
        if do_put_rare_log:
            handler.execute_api()
            
            tmp_rarelogs = {}
            for unique_name, data in gachadata.items():
                boxid = data['boxid']
                obj_rarelog = tmp_rarelogs.get(boxid)
                if obj_rarelog is None:
                    obj_rarelog = []
                    rareloglist = rarecast_logs.get(boxid) or []
                    for rarelog in rareloglist:
                        player = rarelog_playerdict.get(rarelog.uid)
                        cardmaster = rarelog_cardmasters.get(rarelog.mid)
                        if not (player and cardmaster):
                            continue
                        obj_player = Objects.player(handler, player, persons.get(player.dmmid))
                        obj_rarelog.append(Objects.gachaNews(handler, obj_player, cardmaster, rarelog.ctime))
                    tmp_rarelogs[boxid] = obj_rarelog
                    
                    topic = Defines.GachaConsumeType.TO_TOPIC[data['consumetype']]
                    arr = gachaNews_topics[topic] = gachaNews_topics.get(topic) or []
                    arr.extend(obj_rarelog)
                gachaNews_uniquename[unique_name] = obj_rarelog
        handler.html_param['gachaNews_uniquename'] = gachaNews_uniquename
        handler.html_param['gachaNews_topics'] = gachaNews_topics
        
        # ランキングガチャデータ.
        boxidlist = rankingdata.keys()
        is_support_totalranking = False
        if boxidlist:
            rankingmaster_dict = BackendApi.get_rankinggacha_master_dict(model_mgr, boxidlist, using=settings.DB_READONLY)
            rankingmaster_dict_support_wholepoint = dict([(rankingmaster.id, rankingmaster) for rankingmaster in rankingmaster_dict.values() if rankingmaster.is_support_wholepoint])
            if rankingmaster_dict_support_wholepoint:
                # 総計Pt.
                wholepoint_dict = BackendApi.get_rankinggacha_wholepoint_dict(model_mgr, rankingmaster_dict_support_wholepoint.keys(), using=settings.DB_READONLY)
            else:
                wholepoint_dict = {}
            
            for boxid in boxidlist:
                data = rankingdata[boxid]
                rankingmaster = rankingmaster_dict.get(boxid)
                if data is not None and rankingmaster is not None:
                    wholepoint = wholepoint_dict.get(rankingmaster.id, 0)
                    
                    data['single']['data'] = data['single']['data']() if callable(data['single']['data']) else []
                    data['total']['data'] = data['total']['data']() if callable(data['total']['data']) else []
                    data['master'] = Objects.rankinggacha(handler, rankingmaster, wholepoint=wholepoint)
                    
                    # 達成報酬.
                    if rankingmaster.wholeprizes:
                        data['wholeprizelist'] = handler.make_pointprizelist(rankingmaster.wholeprizes, cur_point=wholepoint)[:3]
                    
                    # 勝利報酬.
                    if rankingmaster.wholewinprizes:
                        prizelist = BackendApi.get_prizelist(model_mgr, rankingmaster.wholewinprizes, using=settings.DB_READONLY)
                        data['wholewinprizeinfo'] = BackendApi.make_prizeinfo(handler, prizelist, using=settings.DB_READONLY)
                    
                    is_support_totalranking = is_support_totalranking or rankingmaster.is_support_totalranking
                else:
                    del rankingdata[boxid]
        handler.html_param['gacharankingdata'] = rankingdata
        handler.html_param['gacharanking_is_support_totalranking'] = is_support_totalranking
        
        # おまけページリンク.
        omakeurls = {}
        if omakedata:
            url_base = UrlMaker.gachaomakelist()
            for str_midlist, unique_names in omakedata.values():
                url = OSAUtil.addQuery(url_base, Defines.URLQUERY_ID, ','.join(str_midlist))
                omakeurls.update(dict.fromkeys(unique_names, handler.makeAppLinkUrl(url)))
        handler.html_param['omakeurls'] = omakeurls
        
        handler.html_param['addsocardflgs'] = addsocardflgs
    
    #===========================================================
    # ランキングガチャ.
    @staticmethod
    def get_rankinggacha_master_dict(model_mgr, boxidlist, using=settings.DB_DEFAULT):
        """ランキングガチャマスター取得.
        """
        return BackendApi.get_model_dict(model_mgr, RankingGachaMaster, boxidlist, using=using)
    
    @staticmethod
    def get_rankinggacha_master_by_group(model_mgr, group, using=settings.DB_DEFAULT):
        """ランキングガチャマスターをグループを指定して取得.
        """
        client = OSAUtil.get_cache_client()
        key = 'get_rankinggacha_master_by_group'
        midlist = client.get(key)
        
        if midlist is None:
            filters = {
                'group' : group
            }
            modellist = RankingGachaMaster.fetchValues(filters=filters, using=using)
            midlist = [model.id for model in modellist]
            client.set(key, midlist)
        else:
            modellist = BackendApi.get_model_list(model_mgr, RankingGachaMaster, midlist, using=using)
        
        return modellist
    
    @staticmethod
    def get_rankinggacha_master(model_mgr, boxid, using=settings.DB_DEFAULT):
        """ランキングガチャマスター取得.
        """
        return BackendApi.get_model(model_mgr, RankingGachaMaster, boxid, using=using)
    
    @staticmethod
    def get_rankinggacha_wholepoint_dict(model_mgr, boxidlist, using=settings.DB_DEFAULT):
        """ランキングガチャ総計Pt取得.
        """
        modellist = BackendApi.get_model_list(model_mgr, RankingGachaWholeData, boxidlist, using=using)
        dest = dict([(model.id, model.point) for model in modellist])
        return dest
    
    @staticmethod
    def tr_save_rankinggacha_score(model_mgr, uid, boxid, score):
        """ランキングガチャスコア保存・加算.
        """
        master = BackendApi.get_rankinggacha_master(model_mgr, boxid, using=settings.DB_DEFAULT)
        if master is None:
            # ランキングガチャ設定がない.
            return 0
        
        scorerecord_id = RankingGachaScore.makeID(uid, boxid)
        scorerecord = BackendApi.get_model(model_mgr, RankingGachaScore, scorerecord_id)
        if score < 1:
            return scorerecord.total if scorerecord else 0, 0
        
        point_whole = 0
        if master.is_support_wholepoint:
            # 総計pt報酬がある.
            wholedata = BackendApi.get_model(model_mgr, RankingGachaWholeData, boxid)
            if wholedata is None:
                wholedata = RankingGachaWholeData.makeInstance(boxid)
                wholedata.point = 0
            else:
                wholedata = RankingGachaWholeData.getByKeyForUpdate(boxid)
            
            # 総計ptの加算.
            point_pre = wholedata.point
            wholedata.point += score
            model_mgr.set_save(wholedata)
            point_whole = wholedata.point
            
            # 総計ptを受取可能にする.
            def forUpdateRankingGachaWholePrizeData(model, inserted):
                if inserted:
                    model.queueid = 0
            model_mgr.add_forupdate_task(RankingGachaWholePrizeData, uid, forUpdateRankingGachaWholePrizeData)
            
            # 達成確認.
            point_min = point_pre+1
            point_max = point_whole
            table = master.get_wholeprizes(point_min, point_max)
            if table:
                keys = table.keys()
                keys.sort()
                
                queuelist = []
                for key in keys:
                    if point_min <= key <= point_max:
                        queue = RankingGachaWholePrizeQueue()
                        queue.boxid = boxid
                        queue.point = key
                        queue.prizes = table[key]
                        model_mgr.set_save(queue)
                        queuelist.append(queue)
                if queuelist:
                    def writeEndRankingGachaWholePrizeQueue():
                        pipe = RankingGachaWholePrizeQueueIdSet.getDB().pipeline()
                        for queue in queuelist:
                            RankingGachaWholePrizeQueueIdSet.add(queue.id, pipe)
                        pipe.execute()
                    model_mgr.add_write_end_method(writeEndRankingGachaWholePrizeQueue)
        
        if scorerecord is None:
            scorerecord = RankingGachaScore.makeInstance(scorerecord_id)
            scorerecord.single = score
            scorerecord.total = score
            scorerecord.firstpoint = point_whole
            scorerecord.insert()
        else:
            scorerecord = model_mgr.get_model_forupdate(RankingGachaScore, scorerecord_id)
            scorerecord.single = max(scorerecord.single, score)
            scorerecord.total += score
        model_mgr.set_save(scorerecord)
        
        # 全体の履歴.
        ins = RankingGachaPlayLog()
        ins.uid = uid
        ins.boxid = boxid
        ins.point = score
        ins.point_whole = point_whole
        model_mgr.set_save(ins)
        
        def writeEnd():
            pipe = RankingGachaSingleRanking.getDB().pipeline()
            # ランキングのスコアを保存.
            RankingGachaSingleRanking.create(boxid, uid, scorerecord.single).save(pipe)
            if master.is_support_totalranking:
                RankingGachaTotalRanking.create(boxid, uid, scorerecord.total).save(pipe)
            pipe.execute()
        
        model_mgr.add_write_end_method(writeEnd)
        
        return scorerecord.total, point_whole
    
    @staticmethod
    def get_rankinggacha_single_score(boxid, uid):
        """ランキングガチャの単発ポイントを取得.
        """
        return BackendApi.get_ranking_score(RankingGachaSingleRanking, boxid, uid)
    @staticmethod
    def get_rankinggacha_total_score(boxid, uid):
        """ランキングガチャの累計ポイントを取得.
        """
        return BackendApi.get_ranking_score(RankingGachaTotalRanking, boxid, uid)
    
    @staticmethod
    def get_rankinggacha_single_rank(boxid, uid):
        """ランキングガチャの単発ランキング順位を取得.
        """
        return BackendApi.get_ranking_rank(RankingGachaSingleRanking, boxid, uid)
    
    @staticmethod
    def get_rankinggacha_total_rank(boxid, uid):
        """ランキングガチャの累計ランキング順位を取得.
        """
        return BackendApi.get_ranking_rank(RankingGachaTotalRanking, boxid, uid)
    
    @staticmethod
    def get_rankinggacha_single_rankindex(boxid, uid):
        """ランキングガチャの単発ランキング順位(index)を取得.
        """
        return BackendApi.get_ranking_rankindex(RankingGachaSingleRanking, boxid, uid)
    
    @staticmethod
    def get_rankinggacha_total_rankindex(boxid, uid):
        """ランキングガチャの累計ランキング順位(index)を取得.
        """
        return BackendApi.get_ranking_rankindex(RankingGachaTotalRanking, boxid, uid)
    
    @staticmethod
    def get_rankinggacha_single_rankernum(boxid):
        """ランキングガチャの単発ランキング人数を取得.
        """
        return BackendApi.get_ranking_rankernum(RankingGachaSingleRanking, boxid)
    
    @staticmethod
    def get_rankinggacha_total_rankernum(boxid):
        """ランキングガチャの累計ランキング人数を取得.
        """
        return BackendApi.get_ranking_rankernum(RankingGachaTotalRanking, boxid)
    
    @staticmethod
    def fetch_uid_by_rankinggacha_single_rank(boxid, limit, offset=0, withrank=False):
        """ランキングガチャの単発ランキングを範囲取得.
        """
        return BackendApi.fetch_uid_by_rankingrank(RankingGachaSingleRanking, boxid, limit, offset, withrank)
    
    @staticmethod
    def fetch_uid_by_rankinggacha_total_rank(boxid, limit, offset=0, withrank=False):
        """ランキングガチャの累計ランキングを範囲取得.
        """
        return BackendApi.fetch_uid_by_rankingrank(RankingGachaTotalRanking, boxid, limit, offset, withrank)
    
    @staticmethod
    def get_rankinggacha_scoredata_dict(model_mgr, uid, boxidlist, using=settings.DB_DEFAULT):
        """ランキングガチャのスコア情報を取得.
        """
        keylist = [RankingGachaScore.makeID(uid, boxid) for boxid in boxidlist]
        return BackendApi.get_model_dict(model_mgr, RankingGachaScore, keylist, using=using, key=lambda x:x.mid)
    
    @staticmethod
    def get_rankinggacha_wholeprize_data(model_mgr, uid, using=settings.DB_DEFAULT):
        """受け取った総計pt報酬IDを取得.
        """
        model = BackendApi.get_model(model_mgr, RankingGachaWholePrizeData, uid, using=using)
        return model
    
    @staticmethod
    def get_rankinggacha_wholeprize_queue_not_received(model_mgr, queueid, using=settings.DB_DEFAULT):
        """未受け取りの総計pt報酬配布キューを取得.
        """
        queueid_min = queueid + 1
        
        if RankingGachaWholePrizeQueueIdSet.exists():
            queueidlist = RankingGachaWholePrizeQueueIdSet.fetch(queueid_min)
            queuelist = BackendApi.get_model_list(model_mgr, RankingGachaWholePrizeQueue, queueidlist, using=using)
        else:
            queuelist = RankingGachaWholePrizeQueue.fetchValues(using=using)
            RankingGachaWholePrizeQueueIdSet.save(queuelist)
            queuelist = [queue for queue in queuelist if queueid_min <= queue.id]
        
        queuelist.sort(key=lambda x:x.id)
        
        return queuelist
    
    @staticmethod
    def tr_rankinggacha_receive_wholeprize(model_mgr, uid, queuelist, rankingmaster_dict):
        """総計pt報酬受け取り
        """
        # 受け取った総計pt報酬IDをforUpdateで取得.
        wholeprize_data = RankingGachaWholePrizeData.getByKeyForUpdate(uid)
        if wholeprize_data is None:
            # Noneは不正アクセス.
            raise CabaretError(u'ランキングガチャ未プレイです', CabaretError.Code.ILLEGAL_ARGS)
        
        # 配布用キューの中から受け取った総計pt報酬IDより大きいIDのものを抽出して報酬を配布.
        queueid = wholeprize_data.queueid
        queueid_max = queueid
        prize_dict = {}
        already_received = True
        for queue in queuelist:
            queueid_max = max(queueid_max, queue.id)
            if queue.id <= queueid:
                continue
            master = rankingmaster_dict[queue.boxid]
            textid = master.wholeprize_text
            prizelist = BackendApi.get_prizelist(model_mgr, queue.prizes)
            if prizelist:
                arr = prize_dict[textid] = prize_dict.get(textid) or []
                arr.extend(prizelist)
            
            # ユーザログ追加.
            model_mgr.set_save(UserLogRankingGachaWholePrize.create(uid, queue.boxid, queue.prizes, queue.point))
            
            already_received = False
        
        if already_received:
            model_mgr.delete_models_from_cache(RankingGachaWholePrizeData, [uid])
            raise CabaretError(u'全て受取済みです', CabaretError.Code.ALREADY_RECEIVED)
        
        for textid, prizelist in prize_dict.items():
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
        
        # 受け取った総計pt報酬IDを更新.
        wholeprize_data.queueid = queueid_max
        model_mgr.set_save(wholeprize_data)
    
    @staticmethod
    def make_rankinggacha_ranking(handler, gachamaster, view_myrank, page_content_num=10, offset=0, do_execute_api=True, single=True):
        """ランキングガチャランキングデータ.
        """
        if gachamaster.consumetype != Defines.GachaConsumeType.RANKING:
            return None
        
        model_mgr = handler.getModelMgr()
        boxid = gachamaster.boxid
        rankinggachamaster = BackendApi.get_rankinggacha_master(model_mgr, boxid, using=settings.DB_READONLY)
        if rankinggachamaster is None:
            return None
        elif not (single or rankinggachamaster.is_support_totalranking):
            return None
        
        v_player = handler.getViewerPlayer()
        uid = v_player.id
        
        if single:
            get_score = BackendApi.get_rankinggacha_single_score
            get_rankindex = BackendApi.get_rankinggacha_single_rankindex
            getUidScoreSetList = lambda boxid, offset, limit : BackendApi.fetch_uid_by_rankinggacha_single_rank(boxid, limit, offset, withrank=True)
        else:
            get_score = BackendApi.get_rankinggacha_total_score
            get_rankindex = BackendApi.get_rankinggacha_total_rankindex
            getUidScoreSetList = lambda boxid, offset, limit : BackendApi.fetch_uid_by_rankinggacha_total_rank(boxid, limit, offset, withrank=True)
        
        if view_myrank:
            score = get_score(boxid, uid)
            if score:
                # 自分のランクの周辺ヘ.
                index = get_rankindex(boxid, uid)
                offset = max(0, index - int((page_content_num+1) / 2))
                uidscoresetlist = getUidScoreSetList(boxid, offset, page_content_num)
            else:
                uidscoresetlist = []
        else:
            uidscoresetlist = getUidScoreSetList(boxid, offset, page_content_num)
        
        callback = None
        if uidscoresetlist:
            uidscoreset = dict(uidscoresetlist)
            
            playerlist = BackendApi.get_players(handler, uidscoreset.keys(), [PlayerExp], using=settings.DB_READONLY)
            persons = BackendApi.get_dmmplayers(handler, playerlist, using=settings.DB_READONLY, do_execute=False)
            
            leaders = BackendApi.get_leaders(uidscoreset.keys(), arg_model_mgr=model_mgr, using=settings.DB_READONLY)
            
            def cb():
                obj_playerlist = []
                for player in playerlist:
                    obj_player = Objects.player(handler, player, persons.get(player.dmmid), leaders.get(player.id))
                    score, rank = uidscoreset[player.id]
                    obj_player['event_score'] = score
                    obj_player['event_rank'] = rank
                    obj_player['is_me'] = uid == player.id
                    obj_playerlist.append(obj_player)
                obj_playerlist.sort(key=lambda x:x['id'], reverse=True)
                obj_playerlist.sort(key=lambda x:x['event_score'], reverse=True)
                return obj_playerlist
            callback = cb
        else:
            callback = list
        
        if do_execute_api:
            handler.execute_api()
            return callback()
        else:
            return callback
    
    #===========================================================
    # プレゼント.
    @staticmethod
    def _save_presentidlist(uid, model_mgr, topic=Defines.PresentTopic.ALL, using=settings.DB_DEFAULT, pipe=None):
        
        do_execute = False
        if pipe is None:
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            do_execute = True
        now = OSAUtil.get_now()
#        presentlist = Present.fetchValues(filters={'toid':uid, 'limittime__gt' : now}, using=using)
        presentlist = Present.fetchValues(filters={'toid':uid}, using=using)
        presentlist.sort(key=lambda x:x.ctime, reverse=True)
        
        for _topic in Defines.PresentTopic.RANGE:
            pipe.delete(PresentIdListSet.makeKey(uid, _topic))
        
        idlist = []
        for present in presentlist:
            if present.limittime <= now:
                continue
            BackendApi.add_present(uid, present, pipe=pipe)
            if topic in (Defines.PresentTopic.ALL, Defines.PRESENT_TOPIC_TABLE.get(present.itype)):
                idlist.append(present.id)
            model_mgr.set_got_models([present])
        
        if do_execute:
            pipe.execute()
        return idlist
    
    @staticmethod
    def add_present(uid, present, pipe=None):
        PresentIdListSet.create(uid, present.id, Defines.PresentTopic.ALL, present.ctime).save(pipe)
        if Defines.PRESENT_TOPIC_TABLE.has_key(present.itype):
            PresentIdListSet.create(uid, present.id, Defines.PRESENT_TOPIC_TABLE[present.itype], present.ctime).save(pipe)
    
    @staticmethod
    def remove_present(uid, presentid, itype, pipe=None):
        topic = Defines.PRESENT_TOPIC_TABLE.get(itype, Defines.PresentTopic.ALL)
        PresentIdListSet.create(uid, presentid, topic).delete(pipe)
    
    @staticmethod
    def get_present_num(uid, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """届いているプレゼント数を取得.
        """
        num = PresentIdListSet.get_presentnum(uid)
        if num is None:
            model_mgr = arg_model_mgr or ModelRequestMgr()
            idlist = BackendApi._save_presentidlist(uid, model_mgr, using=using)
            return len(idlist)
        else:
            return num
    
    @staticmethod
    def get_present_idlist(uid, topic=Defines.PresentTopic.ALL, offset=0, limit=-1, arg_model_mgr=None, using=settings.DB_DEFAULT, desc=True):
        """届いているプレゼント一覧を取得.
        """
        if limit == 0:
            return []
        
        num = PresentIdListSet.get_presentnum(uid)
        if num is None:
            model_mgr = arg_model_mgr or ModelRequestMgr()
            idlist = BackendApi._save_presentidlist(uid, model_mgr, topic=topic, using=using)
            if not desc:
                idlist.reverse()
            if 0 < limit:
                return idlist[offset:(offset+limit)]
            else:
                return idlist[offset:]
        else:
            modellist = PresentIdListSet.fetch(uid, topic, offset, limit, desc=desc)
            return [model.presentid for model in modellist]
    
    @staticmethod
    def get_presents(present_idlist, arg_model_mgr=None, using=settings.DB_DEFAULT, received=False):
        """届いているプレゼント一覧を取得.
        """
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        # Present.
        return PresentSet.collect(model_mgr, present_idlist, using=using, received=received)
    
    @staticmethod
    def __tr_receive_present(model_mgr, player, presentlist, excludetypes, do_delete=True, cardgetwaytype=None):
        """プレゼントを付与.
        """
        uid = player.id
        
        present_resultset = {}
        received_redis_present_list = []
        def addResult(present, result):
            present_resultset[present.id] = result
            if result == CabaretError.Code.OK:
                received_redis_present_list.append((present.id, present.itype))
        
        cardlimit = player.cardlimit
        
        cur_nums = {
            Defines.ItemType.GOLD : player.gold,
            Defines.ItemType.RAREOVERTICKET : player.rareoverticket,
            Defines.ItemType.MEMORIESTICKET : player.memoriesticket,
            Defines.ItemType.TRYLUCKTICKET : player.tryluckticket,
            Defines.ItemType.GACHATICKET : player.gachaticket,
            Defines.ItemType.GACHA_PT : player.gachapt,
            Defines.ItemType.CARD : BackendApi.get_cardnum(uid, model_mgr),
            Defines.ItemType.GOLDKEY : player.goldkey,
            Defines.ItemType.SILVERKEY : player.silverkey,
            Defines.ItemType.CABARETCLUB_SPECIAL_MONEY : 0,
            Defines.ItemType.CABARETCLUB_HONOR_POINT : 0,
            Defines.ItemType.PLATINUM_PIECE : 0,
            Defines.ItemType.CRYSTAL_PIECE : 0,
        }
        cabaretclub_playerdata = BackendApi.get_cabaretclub_scoreplayerdata(model_mgr, uid)
        if cabaretclub_playerdata:
            cur_nums.update({
                Defines.ItemType.CABARETCLUB_SPECIAL_MONEY : cabaretclub_playerdata.money,
                Defines.ItemType.CABARETCLUB_HONOR_POINT : cabaretclub_playerdata.point,
            })
        # 獲得する報酬.
        prizes = dict.fromkeys(cur_nums.keys(), 0)
        itemnums = {}
        cardnums = {}
        eventticketnums = {}
        additionalticketnums = {}
        tanzakunums = {}
        
        def addItem(present):
            v = present.ivalue
            num = present.inum
            itemnums[v] = itemnums.get(v, 0) + num
            return CabaretError.Code.OK
        def addCard(present):
            v = present.ivalue
            num = present.inum
            if (cur_nums[Defines.ItemType.CARD]+num) <= cardlimit:
                nums = cardnums[v] = cardnums.get(v) or []
                nums.extend([present.textid] * num)
                cur_nums[Defines.ItemType.CARD] += num
                return CabaretError.Code.OK
            return CabaretError.Code.OVER_LIMIT
        def addEventTicket(present):
            v = present.ivalue
            num = present.inum
            eventticketnums[v] = eventticketnums.get(v, 0) + num
            return CabaretError.Code.OK
        def addAdditionalTicket(present):
            v = present.ivalue
            num = present.inum
            additionalticketnums[v] = additionalticketnums.get(v, 0) + num
            return CabaretError.Code.OK
        def addScoutEventTanzaku(present):
            tanzaku_number = present.ivalue
            num = present.inum
            tanzakunums[tanzaku_number] = tanzakunums.get(tanzaku_number, 0) + num
            return CabaretError.Code.OK
        def addValue(present):
            itype = present.itype
            v = present.ivalue
            # 上限を超えた時は切り捨てに変更.
            prizes[itype] += v
            cur_nums[itype] += v
            return CabaretError.Code.OK
#            if (cur_nums[itype] + v) < Defines.VALUE_MAX:
#                prizes[itype] += v
#                cur_nums[itype] += v
#                return CabaretError.Code.OK
#            return CabaretError.Code.OVER_LIMIT
        
        table = {
            Defines.ItemType.GOLD : addValue,
            Defines.ItemType.GACHA_PT : addValue,
            Defines.ItemType.ITEM : addItem,
            Defines.ItemType.CARD : addCard,
            Defines.ItemType.RAREOVERTICKET : addValue,
            Defines.ItemType.MEMORIESTICKET : addValue,
            Defines.ItemType.TRYLUCKTICKET : addValue,
            Defines.ItemType.GACHATICKET : addValue,
            Defines.ItemType.GOLDKEY : addValue,
            Defines.ItemType.SILVERKEY : addValue,
            Defines.ItemType.EVENT_GACHATICKET : addEventTicket,
            Defines.ItemType.ADDITIONAL_GACHATICKET : addAdditionalTicket,
            Defines.ItemType.SCOUTEVENT_TANZAKU : addScoutEventTanzaku,
            Defines.ItemType.CABARETCLUB_SPECIAL_MONEY : addValue,
            Defines.ItemType.CABARETCLUB_HONOR_POINT : addValue,
            Defines.ItemType.PLATINUM_PIECE : addValue,
            Defines.ItemType.CRYSTAL_PIECE : addValue,
        }
        
        del_cnt = 0
        for present in presentlist:
            if present.toid != uid:
                raise CabaretError(u'不正アクセスです', CabaretError.Code.ILLEGAL_ARGS)
            elif present.itype in excludetypes:
                continue
            elif not table.has_key(present.itype):
                raise CabaretError(u'プレゼント未対応のアイテムです')
            result = table[present.itype](present)
            
            if do_delete and result == CabaretError.Code.OK:
                model_mgr.set_save(PresentReceived.createByPresent(present))
                model_mgr.set_delete(present)
                # ログ.
                model_mgr.set_save(UserLogPresentReceive.create(player.id, present.id))
                
                del_cnt += 1
            
            addResult(present, result)
        
        if 0 < del_cnt:
            # ミッション.
            mission_executer = PanelMissionConditionExecuter()
            mission_executer.addTargetReceivePresent(del_cnt)
            BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
        
        gold = prizes[Defines.ItemType.GOLD]
        gachapt = prizes[Defines.ItemType.GACHA_PT]
        rareoverticket = prizes[Defines.ItemType.RAREOVERTICKET]
        memoriesticket = prizes[Defines.ItemType.MEMORIESTICKET]
        ticket = prizes[Defines.ItemType.TRYLUCKTICKET]
        gachaticket = prizes[Defines.ItemType.GACHATICKET]
        goldkey = prizes[Defines.ItemType.GOLDKEY]
        silverkey = prizes[Defines.ItemType.SILVERKEY]
        cabaretclub_money = prizes[Defines.ItemType.CABARETCLUB_SPECIAL_MONEY]
        cabaretclub_honor_point = prizes[Defines.ItemType.CABARETCLUB_HONOR_POINT]
        platinum_piece = prizes[Defines.ItemType.PLATINUM_PIECE]
        crystal_piece = prizes[Defines.ItemType.CRYSTAL_PIECE]

        if 0 < gold:
            BackendApi.tr_add_gold(model_mgr, uid, gold)
        if 0 < gachapt:
            BackendApi.tr_add_gacha_pt(model_mgr, uid, gachapt)
        if 0 < rareoverticket:
            BackendApi.tr_add_rareoverticket(model_mgr, uid, rareoverticket)
        if 0 < memoriesticket:
            BackendApi.tr_add_memoriesticket(model_mgr, uid, memoriesticket)
        if 0 < ticket:
            BackendApi.tr_add_tryluckticket(model_mgr, uid, ticket)
        if 0 < gachaticket:
            BackendApi.tr_add_gachaticket(model_mgr, uid, gachaticket)
        if 0 < goldkey:
            BackendApi.tr_add_goldkey(model_mgr, uid, goldkey)
        if 0 < silverkey:
            BackendApi.tr_add_silverkey(model_mgr, uid, silverkey)
        if 0 < cabaretclub_money:
            BackendApi.tr_add_cabaretclub_money(model_mgr, uid, cabaretclub_money)
        if 0 < cabaretclub_honor_point:
            BackendApi.tr_add_cabaretclub_honor_point(model_mgr, uid, cabaretclub_honor_point)
        if 0 < platinum_piece:
            BackendApi.tr_add_platinum_piece(model_mgr, uid, platinum_piece)
        if 0 < crystal_piece:
            BackendApi.tr_add_crystal_piece(model_mgr, uid, crystal_piece)
        for mid, num in itemnums.items():
            BackendApi.tr_add_item(model_mgr, uid, mid, num, is_pay=False)
        for mid, num in eventticketnums.items():
            BackendApi.tr_add_raidevent_ticket(model_mgr, uid, mid, num)
        for mid, num in additionalticketnums.items():
            BackendApi.tr_add_additional_gachaticket(model_mgr, uid, mid, num)
        if tanzakunums:
            scouteventmaster = BackendApi.get_current_scouteventmaster(model_mgr)
            if scouteventmaster:
                BackendApi.tr_scoutevent_add_tanzaku(model_mgr, uid, scouteventmaster.id, tanzakunums)
        
        if cardnums:
            playercard = PlayerCard.getByKeyForUpdate(uid)
            model_mgr.set_got_models([playercard])
            waytypes = {
                Defines.TextMasterID.GACHA_CARD : Defines.CardGetWayType.GACHA,
                Defines.TextMasterID.GACHA_CARD_OVER : Defines.CardGetWayType.GACHA,
                Defines.TextMasterID.ACCESS_BONUS : Defines.CardGetWayType.LOGINBONUS,
                Defines.TextMasterID.LOGIN_BONUS : Defines.CardGetWayType.LOGINBONUS,
                Defines.TextMasterID.TUTORIAL_END : Defines.CardGetWayType.REGIST,
                Defines.TextMasterID.TREASURE_BOX : Defines.CardGetWayType.TREASURE,
                Defines.TextMasterID.AREA_CLEAR : Defines.CardGetWayType.AREA,
                Defines.TextMasterID.INVITE : Defines.CardGetWayType.INVITE,
            }
            for mid, arr in cardnums.items():
                for textid in arr:
                    if cardgetwaytype:
                        way = cardgetwaytype
                    elif Defines.TextMasterID.NAMES.has_key(textid):
                        way = waytypes.get(textid, Defines.CardGetWayType.PRIZE)
                    else:
                        way = Defines.CardGetWayType.OTHER
                    BackendApi.tr_create_card(model_mgr, playercard, mid, way=way)
        if do_delete:
            def writeEnd():
                redisdb = RedisModel.getDB()
                pipe = redisdb.pipeline()
                for presentid, itype in received_redis_present_list:
                    BackendApi.remove_present(uid, presentid, itype, pipe)
                pipe.execute()
                
                present_num = Present.count(filters={'toid':uid, 'limittime__gt' : OSAUtil.get_now()})
                if PresentIdListSet.get_presentnum(uid) != present_num:
                    pipe = redisdb.pipeline()
                    BackendApi._save_presentidlist(uid, model_mgr, pipe=pipe)
                    pipe.execute()
            model_mgr.add_write_end_method(writeEnd)
        
        return present_resultset
    
    @staticmethod
    def tr_receive_present(model_mgr, player, present_idlist, excludetypes):
        """プレゼントを付与.
        """
        # プレゼントを取得.
        presentlist = Present.fetchByKeyForUpdate(present_idlist)
        not_foundid_list = list(set(present_idlist) - set([present.id for present in presentlist]))
        result = {}
        if not_foundid_list:
            presentreceivedlist = PresentReceived.getByKey(not_foundid_list)
            for presentreceived in presentreceivedlist:
                result[presentreceived.id] = CabaretError.Code.ALREADY_RECEIVED
        
        result.update(BackendApi.__tr_receive_present(model_mgr, player, presentlist, excludetypes, do_delete=True))
        
        return result
    
    @staticmethod
    def create_present(model_mgr, fromid, toid, itemtype, itemid, itemvalue, textid=0, limittime=None, using=settings.DB_DEFAULT, do_set_save=True, do_set_dummy_id=False):
        """プレゼントレコードを作成.
        """
        do_set_dummy_id = (not do_set_save) and do_set_dummy_id
        presentlist = []
        
        def present_saved(ins):
            UserLogPresentSend.create(toid, ins.id, ins.itype, ins.ivalue, ins.inum, ins.textid).insert()
        
        dummy = {'id':1}
        def add_present(present):
            if do_set_save:
                model_mgr.set_save(present, saved_task=present_saved)
            elif do_set_dummy_id:
                present.id = dummy['id']
                dummy['id'] += 1
            presentlist.append(present)
        
        if not Defines.ItemType.PRESENT_TYPES.has_key(itemtype):
            raise CabaretError(u'プレゼント非対応のアイテムです')
        elif itemvalue < 1:
            raise CabaretError(u'0個でプレゼントを作成しようとしています', CabaretError.Code.INVALID_MASTERDATA)
        elif itemtype == Defines.ItemType.GOLD:
            # キャバゴールド.
            present = Present.createByGold(fromid, toid, itemvalue, textid, limittime)
            add_present(present)
        elif itemtype == Defines.ItemType.GACHA_PT:
            # 引抜Pt.
            present = Present.createByGachaPt(fromid, toid, itemvalue, textid, limittime)
            add_present(present)
        elif itemtype == Defines.ItemType.ITEM:
            # アイテム.
            master = BackendApi.get_itemmaster(model_mgr, itemid)
            if master is None:
                raise CabaretError(u'存在しないアイテムが設定されています.', CabaretError.Code.INVALID_MASTERDATA)
            if 0 < itemvalue:
                present = Present.createByItem(fromid, toid, master, textid, limittime, num=itemvalue)
                add_present(present)
        elif itemtype == Defines.ItemType.CARD:
            # カード.
            master = BackendApi.get_cardmasters([itemid], model_mgr).get(itemid)
            if master is None:
                raise CabaretError(u'キャストが存在しません', CabaretError.Code.INVALID_MASTERDATA)
            if 0 < itemvalue:
                present = Present.createByCard(fromid, toid, master, textid, limittime, num=itemvalue)
                add_present(present)
        elif itemtype == Defines.ItemType.RAREOVERTICKET:
            # レア以上チケット.
            present = Present.createByRareoverTicket(fromid, toid, itemvalue, textid, limittime)
            add_present(present)
        elif itemtype == Defines.ItemType.GACHATICKET:
            # 引抜チケット.
            present = Present.createByGachaTicket(fromid, toid, itemvalue, textid, limittime)
            add_present(present)
        elif itemtype == Defines.ItemType.TRYLUCKTICKET:
            # 運試しチケット.
            present = Present.createByTicket(fromid, toid, itemvalue, textid, limittime)
            add_present(present)
        elif itemtype == Defines.ItemType.MEMORIESTICKET:
            # 思い出チケット.
            present = Present.createByMemoriesTicket(fromid, toid, itemvalue, textid, limittime)
            add_present(present)
        elif itemtype == Defines.ItemType.GOLDKEY:
            # 金の鍵.
            present = Present.createByGoldKey(fromid, toid, itemvalue, textid, limittime)
            add_present(present)
        elif itemtype == Defines.ItemType.SILVERKEY:
            # 銀の鍵.
            present = Present.createBySilverKey(fromid, toid, itemvalue, textid, limittime)
            add_present(present)
        elif itemtype == Defines.ItemType.EVENT_GACHATICKET:
            # レイドイベントガチャチケット.
            master = BackendApi.get_raideventmaster(model_mgr, itemid, using=using)
            if master is None:
                raise CabaretError(u'イベントが存在しません', CabaretError.Code.INVALID_MASTERDATA)
            present = Present.createByEventGachaTicket(fromid, toid, master.id, itemvalue, textid, limittime)
            add_present(present)
        elif itemtype == Defines.ItemType.ADDITIONAL_GACHATICKET:
            # 追加分ガチャチケット.
            if not Defines.GachaConsumeType.GachaTicketType.NAMES.has_key(itemid):
                raise CabaretError(u'未実装のチケットです', CabaretError.Code.INVALID_MASTERDATA)
            present = Present.createByAdditionalTicket(fromid, toid, itemid, itemvalue, textid, limittime)
            add_present(present)
        elif itemtype == Defines.ItemType.SCOUTEVENT_TANZAKU:
            # スカウトイベント短冊.
            config = BackendApi.get_current_scouteventconfig(model_mgr, using=using)
            now = OSAUtil.get_now()
            if config and config.mid and now < config.endtime:
                # 受け取り時間はイベント終了まで.
                limittime = config.endtime
            present = Present.createByScoutEventTanzaku(fromid, toid, itemid, itemvalue, textid, limittime)
            add_present(present)
        elif itemtype == Defines.ItemType.CABARETCLUB_SPECIAL_MONEY:
            # キャバクラシステムの特別なマネー.
            present = Present.createByCabaretClubMoney(fromid, toid, itemvalue, textid, limittime)
            add_present(present)
        elif itemtype == Defines.ItemType.CABARETCLUB_HONOR_POINT:
            # 名誉ポイント.
            present = Present.createByCabaretClubHonor(fromid, toid, itemvalue, textid, limittime)
            add_present(present)
        elif itemtype == Defines.ItemType.PLATINUM_PIECE:
            # プラチナの欠片
            present = Present.createByPlatinumPiece(fromid, toid, itemvalue, textid, limittime)
            add_present(present)
        elif itemtype == Defines.ItemType.CRYSTAL_PIECE:
            # クリスタルの欠片
            present = Present.createByCrystalPiece(fromid, toid, itemvalue, textid, limittime)
            add_present(present)
        else:
            raise CabaretError(u'未実装のプレゼントです')
        return presentlist
    
    @staticmethod
    def create_present_by_prize(model_mgr, uid, prizelist, textid, using=settings.DB_DEFAULT, do_set_save=True, auto_receive=False):
        """ユーザーに報酬を渡す.
        """
        TABLE = dict([
            # (itemvalue, itemtype, itemid).
            ('gold', (Defines.ItemType.GOLD, None)),                          #お金.
            ('gachapt', (Defines.ItemType.GACHA_PT, None)),                   #引きぬきポイント.
            ('itemnum', (Defines.ItemType.ITEM, 'itemid')),                   #アイテム.
            ('cardnum', (Defines.ItemType.CARD, 'cardid')),                   #カード.
            ('rareoverticket', (Defines.ItemType.RAREOVERTICKET, None)),      #レア以上チケット.
            ('gachaticket', (Defines.ItemType.GACHATICKET, None)),            #引抜チケット.
            ('ticket', (Defines.ItemType.TRYLUCKTICKET, None)),               #運試しチケット.
            ('memoriesticket', (Defines.ItemType.MEMORIESTICKET, None)),      #思い出チケット.
            ('goldkey', (Defines.ItemType.GOLDKEY, None)),                    #金の鍵.
            ('silverkey', (Defines.ItemType.SILVERKEY, None)),                #銀の鍵.
            ('eventticket_num', (Defines.ItemType.EVENT_GACHATICKET, 'eventticket_id')),                      #イベントガチャチケット.
            ('additional_ticket_num', (Defines.ItemType.ADDITIONAL_GACHATICKET, 'additional_ticket_id')),     #追加分ガチャチケット.
            ('tanzaku_num', (Defines.ItemType.SCOUTEVENT_TANZAKU, 'tanzaku_number')),                         #スカウトイベント短冊.
            ('cabaclub_money', (Defines.ItemType.CABARETCLUB_SPECIAL_MONEY, None)),                           #キャバクラシステムの特別なマネー.
            ('cabaclub_honor', (Defines.ItemType.CABARETCLUB_HONOR_POINT, None)),                             #名誉ポイント.
            ('platinum_piece_num', (Defines.ItemType.PLATINUM_PIECE, None)),               #プラチナの欠片
            ('crystal_piece_num', (Defines.ItemType.CRYSTAL_PIECE, None)),                 # クリスタルの欠片
        ])
        key_set = set(TABLE.keys())
        auto_receive = do_set_save and auto_receive
        fromid = 0
        presentlist = []
        player = None
        for prize in prizelist:
            if isinstance(prize, PrizeData):
                keys = list(prize.get_active_keys() & key_set)
            else:
                keys = TABLE.keys()
            for attname_itemvalue in keys:
                itemtype, attname_itemid = TABLE[attname_itemvalue]
                itemvalue = getattr(prize, attname_itemvalue)
                if 0 < itemvalue:
                    itemid = None
                    if attname_itemid:
                        itemid = getattr(prize, attname_itemid)
                    if auto_receive and (itemtype in Defines.ItemType.AUTO_RECEIVE_TYPES or prize.itemid in Defines.ItemEffect.PRODUCE_ONLY_ITEMS):
                        # 受け取ってしまう場合.
                        arr = BackendApi.create_present(model_mgr, fromid, uid, itemtype, itemid, itemvalue, textid, using=using, do_set_save=False, do_set_dummy_id=True)
                        if arr:
                            if player is None:
                                player = BackendApi.get_player(None, uid, [PlayerDeck, PlayerGold, PlayerGachaPt, PlayerKey], model_mgr=model_mgr)
                            present_resultset = BackendApi.__tr_receive_present(model_mgr, player, arr, [], do_delete=False)
                            
                            # ちゃんと渡せたのかを確認.
                            failure = []
                            for present in arr:
                                if present_resultset.get(present.id) == CabaretError.Code.OK:
                                    continue
                                failure.append(present)
                            
                            if failure:
                                # うまく渡せなかったのでプレゼントに追加.
                                arr = BackendApi.create_present(model_mgr, fromid, uid, itemtype, itemid, itemvalue, textid, using=using, do_set_save=do_set_save)
                                presentlist.extend(arr)
                    else:
                        arr = BackendApi.create_present(model_mgr, fromid, uid, itemtype, itemid, itemvalue, textid, using=using, do_set_save=do_set_save)
                        presentlist.extend(arr)
        
        return presentlist
    
    #===========================================================
    # 全プレ.
    @staticmethod
    def get_presenteveryonerecord(model_mgr, using=settings.DB_DEFAULT, now=None):
        """本日の全プレを取得.
        """
        now = now or OSAUtil.get_now()
        today = DateTimeUtil.datetimeToDate(now)
        return BackendApi.get_model(model_mgr, PresentEveryoneRecord, today, using=using)
    
    @staticmethod
    def get_presenteveryone_list_formypage(model_mgr, using=settings.DB_DEFAULT, now=None):
        """マイページで受け取る全プレを取得.
        """
        record = BackendApi.get_presenteveryonerecord(model_mgr, using=using, now=now)
        if record and record.mid_mypage:
            masterlist = BackendApi.get_model_list(model_mgr, PresentEveryoneMypageMaster, record.mid_mypage, using=using)
            return [master for master in masterlist if BackendApi.check_schedule(model_mgr, master.schedule, using=using, now=now)]
        else:
            return []
    
    @staticmethod
    def get_presenteveryone_list_forloginbonus(model_mgr, using=settings.DB_DEFAULT, now=None):
        """ログインボーナスで受け取る全プレを取得.
        """
        record = BackendApi.get_presenteveryonerecord(model_mgr, using=using, now=now)
        if record and record.mid_loginbonus:
            return BackendApi.get_model_list(model_mgr, PresentEveryoneLoginBonusMaster, record.mid_loginbonus, using=using)
        else:
            return []
    
    @staticmethod
    def _get_presenteveryone_receiveflags(model_mgr, model_cls, uid, midlist, using=settings.DB_DEFAULT):
        """全プレ受取フラグを取得.
        """
        modellist = BackendApi.get_model_list(model_mgr, model_cls, [model_cls.makeID(uid, mid) for mid in midlist], using=using)
        return dict([(model.mid, model) for model in modellist])
    
    @staticmethod
    def get_presenteveryone_loginbonus_receiveflags(model_mgr, uid, midlist, using=settings.DB_DEFAULT):
        """ログインボーナスの全プレ受取フラグを取得.
        """
        return BackendApi._get_presenteveryone_receiveflags(model_mgr, PresentEveryoneReceiveLoginBonus, uid, midlist, using=using)
    
    @staticmethod
    def get_presenteveryone_mypage_receiveflags(model_mgr, uid, midlist, using=settings.DB_DEFAULT):
        """マイページの全プレ受取フラグを取得.
        """
        return BackendApi._get_presenteveryone_receiveflags(model_mgr, PresentEveryoneReceiveMypage, uid, midlist, using=using)
    
    @staticmethod
    def check_presenteveryone_received(master, flagmodel, now=None):
        now = now or OSAUtil.get_now()
        ltime = DateTimeUtil.toLoginTime(now)
        
        if isinstance(master, PresentEveryoneLoginBonusMaster):
            if flagmodel:
                if master.everyday:
                    return ltime <= flagmodel.rtime
                else:
                    return 0 < flagmodel.cnt
            return False
        else:
            return flagmodel and 0 < flagmodel.cnt
    
    @staticmethod
    def tr_receive_presenteveryone(model_mgr, player, masterlist, now=None, confirmkey=None):
        """全プレ受取.
        """
        uid=player.id
        if confirmkey:
            # キーで確認するときはここで.
            BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        
        now = now or OSAUtil.get_now()
        if isinstance(masterlist[0], PresentEveryoneLoginBonusMaster):
            flagmodel_cls = PresentEveryoneReceiveLoginBonus
            def prize_getter(master, flagmodel):
                return master.prizes_daily.get(str(flagmodel.cnt), master.prizes)
        
        elif isinstance(masterlist[0], PresentEveryoneMypageMaster):
            flagmodel_cls = PresentEveryoneReceiveMypage
            def prize_getter(master, flagmodel):
                return master.prizes
        
        else:
            raise CabaretError(u'未対応プレゼントです', CabaretError.Code.UNKNOWN)
        
        # 受取りフラグを確認.
        midlist = [master.id for master in masterlist]
        pre_flagmodels = BackendApi._get_presenteveryone_receiveflags(model_mgr, flagmodel_cls, uid, midlist)
        
        # 受け取るプレゼント.
        prizeidlistset = {}
        for master in masterlist:
            flagmodel = pre_flagmodels.get(master.id)
            

            player_regist=player.getModel(PlayerRegist)
            schedulemaster = BackendApi.get_schedule_master(model_mgr, master.schedule, using=settings.DB_READONLY)
            starttime, endtime = BackendApi.get_schedule_start_end_time(schedulemaster)
            if starttime < player_regist.ctime:
                continue            
            
            if BackendApi.check_presenteveryone_received(master, flagmodel, now):
                continue
            
            if not flagmodel:
                flagmodel = flagmodel_cls.makeInstance(flagmodel_cls.makeID(uid, master.id))
            
            flagmodel.rtime = now
            flagmodel.cnt += 1
            model_mgr.set_save(flagmodel)
            
            arr = prizeidlistset[master.textid] = prizeidlistset.get(master.textid) or []
            arr.extend(prize_getter(master, flagmodel))
        
        # 配布.
        for textid, prizeidlist in prizeidlistset.items():
            prizemasters = dict([(prize.id, prize) for prize in BackendApi.get_prizemaster_list(model_mgr, list(set(prizeidlist)))])
            prizelist = [prizemasters[prizeid] for prizeid in prizeidlist]
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
    
    #===========================================================
    # 履歴.
    @staticmethod
    def _save_log_idlist(log_cls, att_me, att_date, uid, model_mgr, limit=100, using=settings.DB_DEFAULT):
        """行動履歴のID一覧を保存.
        """
        redisdb = RedisModel.getDB()
        loglist = log_cls.get_modelclass().fetchValues(filters={att_me:uid}, limit=100, order_by='-%s' % att_date, using=using)
        idlist = []
        pipe = redisdb.pipeline()
        
        pipe.delete(log_cls.makeKey(uid))
        
        for logmodel in loglist:
            idlist.append(logmodel.id)
            log_cls.create(uid, logmodel.id, getattr(logmodel, att_date)).save(pipe)
        pipe.execute()
        model_mgr.set_got_models(loglist)
        return idlist[:limit]
    
    @staticmethod
    def _get_log_idlist(log_cls, attr_me, att_date, uid, offset=0, limit=-1, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """行動履歴のIDのリストを取得.
        """
        if limit == 0:
            return []
        
        if log_cls.exists(uid):
            return [logdata.logid for logdata in log_cls.fetch(uid, offset, limit)]
        else:
            model_mgr = arg_model_mgr or ModelRequestMgr()
            idlist = BackendApi._save_log_idlist(log_cls, attr_me, att_date, uid, model_mgr, using=using)
            if 0 < limit:
                return idlist[offset:(offset+limit)]
            else:
                return idlist[offset:]
    
    @staticmethod
    def _get_log_num(log_cls, attr_me, att_date, uid, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """行動履歴のIDのリストを取得.
        """
        if not log_cls.exists(uid):
            model_mgr = arg_model_mgr or ModelRequestMgr()
            BackendApi._save_log_idlist(log_cls, attr_me, att_date, uid, model_mgr, using=using)
        return log_cls.get_num(uid) or 0
    
    @staticmethod
    def add_playerlogid(logdata, pipe=None):
        """行動履歴追加.
        """
        PlayerLogListSet.create(logdata.uid, logdata.id, logdata.ctime).save(pipe)
    
    @staticmethod
    def delete_extra_playerlog(model_mgr, uid):
        """余分な行動履歴を削除.
        """
        idlist = BackendApi._get_log_idlist(PlayerLogListSet, 'uid', 'ctime', uid, Defines.PLAYERLOG_NUM_MAX, 10, model_mgr, using=settings.DB_READONLY)
        if not idlist:
            return
        
        def tr():
            model_mgr = ModelRequestMgr()
            playerloglist = model_mgr.get_models(PlayerLog, idlist)
            
            redismodellist = []
            for playerlog in playerloglist:
                redismodellist.append(PlayerLogListSet.create(playerlog.uid, playerlog.id, playerlog.ctime))
                model_mgr.set_delete(playerlog)
            
            def writeEnd():
                redisdb = PlayerLogListSet.getDB()
                pipe = redisdb.pipeline()
                
                for redismodel in redismodellist:
                    redismodel.delete(pipe)
                pipe.execute()
            model_mgr.add_write_end_method(writeEnd)
            
            model_mgr.write_all()
            
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        return len(idlist)
    
    @staticmethod
    def get_playerlog_num(model_mgr, uid, using=settings.DB_DEFAULT):
        """行動履歴を取得.
        """
        return BackendApi._get_log_num(PlayerLogListSet, 'uid', 'ctime', uid, model_mgr, using=using)
    
    @staticmethod
    def get_playerlog_list(appbasehandler, uid, offset=0, limit=-1, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """行動履歴を取得.
        """
        if limit == 0:
            return []
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        # 行動履歴IDを取得.
        idlist = BackendApi._get_log_idlist(PlayerLogListSet, 'uid', 'ctime', uid, offset, limit, model_mgr, using)
        # 行動履歴を取得.
        loglist = model_mgr.get_models(PlayerLog, idlist, using=using)
        logs = {}
        for log_data in loglist:
            gamelog = getGameLog(log_data)
            gamelog.load(appbasehandler)
            logs[log_data.id] = Objects.gamelog(gamelog)
        result = []
        for logid in idlist:
            obj = logs.get(logid)
            if obj:
                result.append(obj)
        return result
    
    @staticmethod
    def get_friendlog_num(model_mgr, uid, using=settings.DB_DEFAULT):
        """フレンドの近況の総数.
        """
        return FriendLogList.get_num(uid)
    
    @staticmethod
    def get_friendlog_list(appbasehandler, uid, offset=0, limit=-1, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """フレンドの近況を取得.
        """
        if limit == 0:
            return []
        
        # 行動履歴を取得.
        loglist = FriendLogList.fetch(uid, offset, limit)
        
        result = []
        for idx, log_data in enumerate(loglist):
            logid = (uid << 32) + idx
            log_data.id = logid
            gamelog = getGameLog(log_data)
            gamelog.load(appbasehandler)
            result.append(Objects.gamelog(gamelog))
        return result
    
    @staticmethod
    def tr_add_friendlog(model_mgr, logdata):
        """フレンドの近況を追加.
        """
        def writeEnd():
            friendlist = BackendApi.get_friend_idlist(logdata.uid, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
            if friendlist:
                FriendLogReserveList.create(friendlist, logdata).save()
        model_mgr.add_write_end_method(writeEnd)
    
    #===========================================================
    # お知らせ.
    @staticmethod
    def _update_infomations(apphandler, cache_cls, using=settings.DB_DEFAULT):
        """更新情報等を再設定.
        """
        model_cls = cache_cls.get_model_class()
        
        # 有効なお知らせ.
        now = OSAUtil.get_now()
        infomations = model_cls.fetchValues(filters={'etime__gt':now}, order_by='-stime', using=using)
        return cache_cls.save(infomations, now)
    
    @staticmethod
    def _get_infomations(apphandler, cache_cls, start=0, end=-1, order_by='-stime', using=settings.DB_DEFAULT):
        """更新情報等を取得.
        """
        def sort_infomations(infomations, order_by):
            reverse = False
            if isinstance(order_by, (str, unicode)):
                if order_by[0] == '-':
                    order_by = order_by[1:]
                    reverse = True
                key = operator.attrgetter(order_by)
            else:
                key = order_by
            infomations.sort(key=key, reverse=reverse)
        
        model_cls = cache_cls.get_model_class()
        if cache_cls.exists():
            infomation_ids = cache_cls.fetch(start, end)
            model_mgr = apphandler.getModelMgr()
            infomations = model_mgr.get_models(model_cls, infomation_ids, False, using=using)
            sort_infomations(infomations, order_by)
        else:
            infomations = BackendApi._update_infomations(apphandler, cache_cls, using=using)
            sort_infomations(infomations, order_by)
            if end == -1:
                infomations = infomations[start:]
            else:
                infomations = infomations[start:(end+1)]
        
        return infomations
    
    @staticmethod
    def update_infomations(apphandler, using=settings.DB_DEFAULT):
        """運営からのお知らせを再設定.
        """
        return BackendApi._update_infomations(apphandler, InfomationMasterIdListCache, using)
    
    @staticmethod
    def get_infomations(apphandler, page=0, using=settings.DB_DEFAULT):
        """運営からのお知らせを取得.
        """
        PAGE_CONTENT_NUM = Defines.INFORMATION_PAGE_CONTENT_NUM
        start = page * PAGE_CONTENT_NUM
        end = start + PAGE_CONTENT_NUM + 1
        infomations = BackendApi.get_infomation_all(apphandler, using=using)
        return infomations[start:end], len(infomations)
    
    @staticmethod
    def get_infomation_all(apphandler, using=settings.DB_DEFAULT):
        """運営からのお知らせをすべて取得.
        """
        return BackendApi._get_infomations(apphandler, InfomationMasterIdListCache, using=using)
    
    @staticmethod
    def get_infomation(model_mgr, mid, using=settings.DB_DEFAULT):
        """運営からのお知らせを取得.
        """
        return model_mgr.get_model(InfomationMaster, mid, using=using)
    
    @staticmethod
    def update_topbanners(apphandler, using=settings.DB_DEFAULT):
        """Topページのバナーを再設定.
        """
        return BackendApi._update_infomations(apphandler, TopBannerMasterIdListCache, using)
    
    @staticmethod
    def get_topbanners(apphandler, using=settings.DB_DEFAULT):
        """Topページのバナーを取得.
        """
        return BackendApi._get_infomations(apphandler, TopBannerMasterIdListCache, order_by='-priority', using=using)
    
    @staticmethod
    def update_eventbanners(apphandler, using=settings.DB_DEFAULT):
        """イベントバナーを再設定.
        """
        return BackendApi._update_infomations(apphandler, EventBannerMasterIdListCache, using)
    
    @staticmethod
    def get_eventbanners(apphandler, using=settings.DB_DEFAULT):
        """イベントバナーを取得.
        """
        modellist = BackendApi._get_infomations(apphandler, EventBannerMasterIdListCache, order_by='-priority', using=using)
        return [model for model in modellist if model.forpage]
    
    @staticmethod
    def get_eventbanner(model_mgr, mid, using=settings.DB_DEFAULT):
        """イベントバナーを取得.
        """
        return BackendApi.get_model(model_mgr, EventBannerMaster, mid, using=using)
    
    @staticmethod
    def get_tabeventbanners(apphandler, using=settings.DB_DEFAULT):
        """タブで分けられているイベントバナーを取得.
        """
        def get_dictionarys(banners):
            return [Objects.eventbanner(apphandler, banner) for banner in banners]

        eventbanners = BackendApi.get_eventbanners(apphandler, using)

        banners_show = filter(lambda x:x.priority > 3,eventbanners)
        banners_hidden = filter(lambda x:x.priority <= 3,eventbanners)

        return namedtuple('TabEventBanners', 'show hidden')(get_dictionarys(banners_show),get_dictionarys(banners_hidden))

    @staticmethod
    def get_menu_eventbanner(apphandler, using=settings.DB_DEFAULT):
        """メニュー用イベントバナーを取得.
        """
        modellist = BackendApi._get_infomations(apphandler, EventBannerMasterIdListCache, order_by='-priority', using=using)
        for model in modellist:
            if model.formenu:
                return model
        return None
    
    @staticmethod
    def get_popupbanners(apphandler, uid=None, using=settings.DB_DEFAULT):
        """ポップアップバナーを取得.
        """
        modellist = BackendApi._get_infomations(apphandler, PopupMasterIdListCache, order_by=lambda x:(x.priority<<32)+x.id, using=using)
        eventbanneridlist = [model.banner for model in modellist if model.banner]
        
        model_mgr = apphandler.getModelMgr()
        banners = BackendApi.get_model_dict(model_mgr, EventBannerMaster, eventbanneridlist, using=using)
        
        filter_func = None
        if uid:
            resettime_model = PopupResetTime.get()
            # 閲覧済みのものは除く.
            viewtime_model = PopupViewTime.get(uid)
            midlist = viewtime_model.get_viewed_midlist(resettime_model.rtime)
            filter_func = lambda x:not x.id in midlist
        
        return [PopupBanner(model, banners.get(model.banner)) for model in modellist if filter_func and filter_func(model)]
    
    @staticmethod
    def update_popupbanners(apphandler, using=settings.DB_DEFAULT):
        """イベントバナーを再設定.
        """
        return BackendApi._update_infomations(apphandler, PopupMasterIdListCache, using)
    
    @staticmethod
    def get_popupbanner(model_mgr, mid, using=settings.DB_DEFAULT):
        """ポップアップバナーを取得.
        """
        model = BackendApi.get_model(model_mgr, PopupMaster, mid, using=using)
        if model:
            banner = BackendApi.get_eventbanner(model_mgr, model.banner, using=using) if model.banner else None
            return PopupBanner(model, banner)
        return None
    
    @staticmethod
    def update_popup_flag(uid, midlist, now=None, pipe=None):
        """ポップアップの閲覧フラグを更新.
        """
        now = now or OSAUtil.get_now()
        lbtime = DateTimeUtil.toLoginTime(now)
        model = PopupViewTime.get(uid)
        resettime_model = PopupResetTime.get()
        db_midlist = model.get_viewed_midlist(resettime_model.rtime, lbtime)
        
        if 0 < len(set(midlist) - set(db_midlist)):
            model.midlist = list(set(db_midlist) | set(midlist))
            model.vtime = now
            model.save(pipe)
    
    @staticmethod
    def update_popup_reset_time(now=None, pipe=None):
        """ポップアップの閲覧時間のリセット時間を更新.
        """
        now = now or OSAUtil.get_now()
        PopupResetTime.create(now).save(pipe)
    
    #===========================================================
    # あいさつ.
    @staticmethod
    def get_greetlog_num(model_mgr, uid, using=settings.DB_DEFAULT):
        """あいさつ数.
        """
        return BackendApi._get_log_num(GreetLogListSet, 'toid', 'gtime', uid, model_mgr, using=using)
    
    @staticmethod
    def get_greetlog_list(appbasehandler, uid, offset=0, limit=-1, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """あいさつ履歴を取得.
        """
        if limit == 0:
            return []
        # model_mgr.
        model_mgr = arg_model_mgr or ModelRequestMgr()
        # あいさつ履歴IDを取得.
        idlist = BackendApi._get_log_idlist(GreetLogListSet, 'toid', 'gtime', uid, offset, limit, model_mgr, using)
        # あいさつ履歴を取得.
        loglist = model_mgr.get_models(GreetLog, idlist, using=using)
        logs = {}
        for log_data in loglist:
            greetlog = GreetLogData(log_data)
            greetlog.load(appbasehandler)
            logs[log_data.id] = Objects.greetlog(greetlog)
        result = []
        for logid in idlist:
            obj = logs.get(logid)
            if obj:
                result.append(obj)
        return result
    
    @staticmethod
    def delete_extra_greetlog(model_mgr, uid):
        """余分なあいさつ履歴を削除.
        """
        idlist = BackendApi._get_log_idlist(GreetLogListSet, 'toid', 'gtime', uid, Defines.PLAYERLOG_NUM_MAX, 10, model_mgr, using=settings.DB_READONLY)
        if not idlist:
            return
        
        def tr():
            model_mgr = ModelRequestMgr()
            greetloglist = model_mgr.get_models(GreetLog, idlist)
            
            redismodellist = []
            for greetlog in greetloglist:
                redismodellist.append(GreetLogListSet.create(greetlog.toid, greetlog.id, greetlog.gtime))
                model_mgr.set_delete(greetlog)
            
            def writeEnd():
                redisdb = GreetLogListSet.getDB()
                pipe = redisdb.pipeline()
                for redismodel in redismodellist:
                    redismodel.delete(pipe)
                pipe.execute()
            model_mgr.add_write_end_method(writeEnd)
            
            model_mgr.write_all()
            
            return model_mgr
        db_util.run_in_transaction(tr).write_end()
        return len(idlist)
    
    @staticmethod
    def get_greetlog_last(model_mgr, uid, oid, using=settings.DB_DEFAULT):
        """最後のあいさつ履歴を取得.
        """
        greetdata = model_mgr.get_model(GreetData, GreetData.makeID(uid, oid))
        greetlog = GreetLog.fetchValues(filters={'fromid':uid, 'toid':oid, 'gtime__gte':greetdata.ltime }, order_by='-gtime', limit=1, using=settings.DB_DEFAULT)
        if len(greetlog) != 1:
            return None
        return greetlog[0]
    
    @staticmethod
    def tr_save_greetlog(model_mgr, uid, oid):
        """あいさつログの保存.
        """
        model = GreetLog()
        model.fromid = uid
        model.toid = oid
        model_mgr.set_save(model)
        # 書き込み後のタスクを設定.
        def funcWriteEnd():
            BackendApi._save_log_idlist(GreetLogListSet, 'toid', 'gtime', oid, model_mgr, using=settings.DB_DEFAULT)
        model_mgr.add_write_end_method(funcWriteEnd)
    
    @staticmethod
    def get_greettimes(model_mgr, uid, oidlist, using=settings.DB_DEFAULT):
        """あいさつ時間.
        """
        idlist = [GreetData.makeID(uid, oid) for oid in oidlist if uid != oid]
        datalist = BackendApi.get_model_list(model_mgr, GreetData, idlist, using=using)
        return dict([(data.toid, data.ltime) for data in datalist])
    
    @staticmethod
    def check_greettime(ltime, now=None):
        """あいさつ時間のチェック.
        """
        if ltime is None:
            return True
        
        now = OSAUtil.get_now()
        return (ltime + Defines.GREET_INTERVAL) <= now
    
    @staticmethod
    def tr_greet(model_mgr, uid, oid, is_friend):
        """挨拶する.
        """
        now = OSAUtil.get_now()
        # 同じ相手にあいさつした時間をチェック.
        def forUpdateGreetData(model, inserted):
            if inserted:
                model.fromid = uid
                model.toid = oid
            elif not BackendApi.check_greettime(model.ltime, now):
                raise CabaretError(u"同じ相手には2時間に1度だけです", CabaretError.Code.ALREADY_RECEIVED)
            model.ltime = now
        model_mgr.add_forupdate_task(GreetData, GreetData.makeID(uid, oid), forUpdateGreetData)
        
        # 本日あいさつ回数をチェック.
        def forUpdateGreetPlayerData(model, inserted):
            if not inserted:
                today = model.getTodayCount()
                if Defines.GREET_COUNT_MAX_PER_DAY <= today:
                    raise CabaretError(u"あいさつは1日%d回までです" % Defines.GREET_COUNT_MAX_PER_DAY, CabaretError.Code.OVER_LIMIT)
            model.addCount()
        model_mgr.add_forupdate_task(GreetPlayerData, uid, forUpdateGreetPlayerData)
        
        # 引抜ポイントを加算.
        if is_friend:
            point = Defines.GREET_GACHA_PT_FRIEND
        else:
            point = Defines.GREET_GACHA_PT
        BackendApi.tr_add_gacha_pt(model_mgr, uid, point)
        
        # あいさつ履歴を追加.
        BackendApi.tr_save_greetlog(model_mgr, uid, oid)
    
    @staticmethod
    def tr_greet_comment(model_mgr, uid, oid, is_friend, logid, textid):
        """挨拶コメントする.
        """
        greetlog = GreetLog.fetchValues(filters={'id':logid, 'fromid':uid, 'toid':oid}, using=settings.DB_DEFAULT)
        if len(greetlog) != 1:
            raise CabaretError(u"不正です", CabaretError.Code.NOT_DATA)
        greetlog = greetlog[0]
        now = OSAUtil.get_now()
        if BackendApi.check_greettime(greetlog.gtime, now):
            raise CabaretError(u"不正です", CabaretError.Code.NOT_DATA)
        
        if greetlog.commenttextid == u'':
            def tr_comment(logid):
                model_mgr = ModelRequestMgr()
                
                log = model_mgr.get_model_forupdate(GreetLog, int(logid))
                log.commenttextid = textid
                model_mgr.set_save(log)
                model_mgr.write_all()
                return model_mgr
            db_util.run_in_transaction(tr_comment, logid).write_end()
            
            # 引抜ポイントを加算.
            if is_friend:
                point = Defines.GREET_COMMENT_GACHA_PT_FRIEND
            else:
                point = Defines.GREET_COMMENT_GACHA_PT
            BackendApi.tr_add_gacha_pt(model_mgr, uid, point)
        else:
            model = GreetLog()
            model.fromid = uid
            model.toid = oid
            model.commenttextid = textid
            model_mgr.set_save(model)
            def funcWriteEnd():
                BackendApi._save_log_idlist(GreetLogListSet, 'toid', 'gtime', oid, model_mgr, using=settings.DB_DEFAULT)
            model_mgr.add_write_end_method(funcWriteEnd)
    
    #===========================================================
    # レベルと経験値.
    @staticmethod
    def _get_levelexp_bylevel(levelexp_cls, level, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """レベルから経験値情報を引いてくる
        """
        model_cls = levelexp_cls.get_model_class()
        model_mgr = arg_model_mgr or ModelRequestMgr()
        levelexp = model_mgr.get_model(model_cls, level, using=using)
        return levelexp
    
    @staticmethod
    def _save_levelexp_idlist(levelexp_cls, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """経験値から引いてくるためにsortset型にIDを保存.
        """
        model_cls = levelexp_cls.get_model_class()
        levelexplist = model_cls.fetchValues(using=using)
        levelexp_cls.save(levelexplist)
        
        if arg_model_mgr:
            arg_model_mgr.set_got_models(levelexplist)
        return levelexplist
    
    @staticmethod
    def _get_levelexp_byexp(levelexp_cls, exp, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """経験値から経験値情報を引いてくる
        """
        model_mgr = arg_model_mgr or ModelRequestMgr()
        
        level = None
        
        for _ in xrange(3): # リトライしてみる.
            if levelexp_cls.exists():
                level = levelexp_cls.getByExp(exp)
                if level is None:
                    if not levelexp_cls.exists():
                        BackendApi._save_levelexp_idlist(levelexp_cls, model_mgr, using)
                    continue
                else:
                    break
            else:
                levelexplist = BackendApi._save_levelexp_idlist(levelexp_cls, model_mgr, using)
                levelexplist.sort(key=lambda x:x.level, reverse=True)
                for levelexp in levelexplist:
                    if levelexp.exp <= exp:
                        return levelexp
        
        if level is None:
            level = BackendApi._get_maxlevelexplevel(levelexp_cls, model_mgr, using)
        return BackendApi._get_levelexp_bylevel(levelexp_cls, level, model_mgr, using)
    
    @staticmethod
    def _get_maxlevelexplevel(levelexp_cls, arg_model_mgr=None, using=settings.DB_DEFAULT):
        """最大レベルを取得.
        """
        if not levelexp_cls.exists():
            model_mgr = arg_model_mgr or ModelRequestMgr()
            BackendApi._save_levelexp_idlist(levelexp_cls, model_mgr, using)
        return levelexp_cls.maxLevel()
    
    @staticmethod
    def get_playerlevelexp_bylevel(level, arg_model_mgr=None, using=settings.DB_DEFAULT):
        return BackendApi._get_levelexp_bylevel(PlayerLevelExpMasterListCache, level, arg_model_mgr, using)
    @staticmethod
    def get_playerlevelexp_byexp(exp, arg_model_mgr=None, using=settings.DB_DEFAULT):
        return BackendApi._get_levelexp_byexp(PlayerLevelExpMasterListCache, exp, arg_model_mgr, using)
    @staticmethod
    def get_playermaxlevel(arg_model_mgr=None, using=settings.DB_DEFAULT):
        return BackendApi._get_maxlevelexplevel(PlayerLevelExpMasterListCache, arg_model_mgr, using)
    
    @staticmethod
    def get_cardlevelexp_bylevel(level, arg_model_mgr=None, using=settings.DB_DEFAULT):
        return BackendApi._get_levelexp_bylevel(CardLevelExpMsterListCache, level, arg_model_mgr, using)
    @staticmethod
    def get_cardlevelexp_byexp(exp, arg_model_mgr=None, using=settings.DB_DEFAULT):
        return BackendApi._get_levelexp_byexp(CardLevelExpMsterListCache, exp, arg_model_mgr, using)
    
    @staticmethod
    def make_playerlevelup_info(model_mgr, player, using=settings.DB_DEFAULT):
        """プレイヤーのレベルアップ情報を作成.
        """
        pre_levelexp = BackendApi.get_playerlevelexp_bylevel(player.level - 1, model_mgr, using=using)
        
        tmp = (
            (0 < player.hp - pre_levelexp.hp, 'hp', None),
            (0 < player.deckcapacitylv - pre_levelexp.deckcapacity, 'deckcapacity', None),
            (0 < player.cardlimitlv - pre_levelexp.cardlimit, 'cardlimit', None),
            (0 < player.apmax - pre_levelexp.ap, 'get_ap_max', 'ap'),
            (0 < player.friendlimit - pre_levelexp.friendlimit, 'friendlimit', None),
        )
        infos = {}
        for flag, attname, name in tmp:
            if not flag:
                continue
            v = getattr(player, attname)
            if callable(v):
                v = v()
            infos[name or attname] = v
        infos['level'] = player.level
        return infos
    
    #===========================================================
    # スケジュール.
    @staticmethod
    def get_schedule_start_end_time(schedulemaster, now=None):
        """スケジュールの開始と終了時間を取得.
        """
        if schedulemaster is None:
            return None, None
        elif schedulemaster.wday == Defines.WeekDay.ALL and schedulemaster.timelimit == 1440:
            # 期間中ずっと.
            return schedulemaster.stime, schedulemaster.etime
        
        now = now or OSAUtil.get_now()
        starttime = DateTimeUtil.toBaseTime(now, schedulemaster.shour, schedulemaster.sminute)
        endtime = starttime + datetime.timedelta(seconds=schedulemaster.timelimit*60)
        return starttime, endtime

    @staticmethod
    def get_schedule_times_wrapper(model_mgr, scheduleid, now=None, using=settings.DB_DEFAULT):
        """スケジュールの開始と終了時間をスケジュールIDから直で取得.
           get_schedule_start_end_time と get_schedule_master の wrapper.
        """
        if now is None:
            now = OSAUtil.get_now()

        schedulemaster = BackendApi.get_schedule_master(model_mgr, scheduleid, using=using)
        return BackendApi.get_schedule_start_end_time(schedulemaster, now=now)
    
    @staticmethod
    def check_schedule_many(model_mgr, scheduleidlist, using=settings.DB_DEFAULT, now=None):
        """有効なスケジュールかを確認.
        """
        scheduleidlist = list(set(scheduleidlist))
        if 0 in scheduleidlist:
            scheduleidlist.remove(0)
        
        dest = {0:True}
        
        if scheduleidlist:
            now = now or OSAUtil.get_now()
            dest.update(dict.fromkeys(scheduleidlist, True))
            
            schedulemaster_list = BackendApi.get_model_list(model_mgr, ScheduleMaster, scheduleidlist, using=using)
            def check(schedulemaster):
                if now < schedulemaster.stime or schedulemaster.etime < now:
                    # 期間外.
                    return False
                
                starttime, endtime = BackendApi.get_schedule_start_end_time(schedulemaster, now)
                if not schedulemaster.wday in (Defines.WeekDay.ALL, Defines.WeekDay.EVERYDAY) and starttime.weekday() != schedulemaster.wday:
                    # 曜日が違う.
                    return False
                elif now < starttime or endtime < now:
                    # 期間外.
                    return False
                return True
            
            for schedulemaster in schedulemaster_list:
                dest[schedulemaster.id] = check(schedulemaster)
        
        return dest
    
    @staticmethod
    def check_schedule(model_mgr, scheduleid, using=settings.DB_DEFAULT, now=None):
        """有効なスケジュールかを確認.
        """
        return BackendApi.check_schedule_many(model_mgr, [scheduleid], using, now)[scheduleid]

    @staticmethod
    def check_schedule_error_or_nowtime(model_mgr, scheduleid, using=settings.DB_DEFAULT):
        """スケジュールが有効かチェックして期限外の場合エラーを吐く.
           エラーを吐か無い場合は現在時刻を返す.
        """
        now = OSAUtil.get_now()
        if not BackendApi.check_schedule(model_mgr, scheduleid, using=using, now=now):
            raise CabaretError(u'期間外です', CabaretError.Code.EVENT_CLOSED)
        return now
    
    @staticmethod
    def get_schedule_master(model_mgr, scheduleid, using=settings.DB_DEFAULT):
        """スケジュールの開始時間と終了時間を取得.
        """
        if scheduleid == 0:
            # 未設定は全公開.
            return None
        
        schedulemaster = model_mgr.get_model(ScheduleMaster, scheduleid, using=using)
        if schedulemaster is None:
            raise CabaretError(u'スケジュールが存在しません.%d' % scheduleid, CabaretError.Code.INVALID_MASTERDATA)
        
        return schedulemaster
    
    #===========================================================
    # アイテム.
    @staticmethod
    def get_itemmaster_list(model_mgr, itemidlist, using=settings.DB_DEFAULT):
        """アイテムのマスターデータを取得.
        """
        return model_mgr.get_models(ItemMaster, itemidlist, using=using)
    
    @staticmethod
    def get_itemmaster(model_mgr, itemid, using=settings.DB_DEFAULT):
        """アイテムのマスターデータを取得(単体).
        """
        itemlist = BackendApi.get_itemmaster_list(model_mgr, [itemid], using=using)
        return itemlist[0] if itemlist else None
    
    @staticmethod
    def get_item_nums(model_mgr, uid, itemidlist, att='num', using=settings.DB_DEFAULT):
        """アイテムの所持情報を辞書で返す.
        """
        modellist = model_mgr.get_models(Item, [Item.makeID(uid, itemid) for itemid in itemidlist], using=using)
        nums = {}
        for model in modellist:
            nums[model.mid] = getattr(model, att)
        return nums
    
    @staticmethod
    def get_item_list(apphandler, player, using=settings.DB_DEFAULT):
        """所持アイテムリスト.
        """
        
        model_mgr = apphandler.getModelMgr()
        uid = player.id
        
        # マスターデータ.
        masterlist = model_mgr.get_mastermodel_all(ItemMaster, using=using)
        masterdict = {}
        for master in masterlist:
            masterdict[master.id] = master
        
        # 所持数.
        nums = BackendApi.get_item_nums(model_mgr, uid, masterdict.keys(), using=using)
        
        # データをセット
        list_data_tmp = []
        for mid in sorted(nums.keys()):
            master = masterdict[mid]
            num = nums[mid]
            if 0 < num:
                usenum_max = ItemUtil.calcUseNumMax(master, player, num)
                data = Objects.item(apphandler, master, num, usenum_max)
                list_data_tmp.append({'pri': master.pri, 'data': data})
        
        list_data_tmp.sort(key=operator.itemgetter('pri'), reverse=True)
        
        list_data = [data['data'] for data in list_data_tmp]
        
        return list_data
    
    @staticmethod
    def tr_add_item(model_mgr, uid, mid, num=1, is_pay=False, before_num=None, do_check_mission=True):
        """アイテム数を加算.
        """
        master = model_mgr.get_model(ItemMaster, mid)
        if master is None:
            raise CabaretError(u'存在しないアイテムです.%d' % mid, CabaretError.Code.INVALID_MASTERDATA)
        elif num == 0:
            return
        
        wresult = {}
        def forUpdateTask(model, inserted):
            if before_num is not None and before_num != model.num:
                # すでに減らしてある.
                raise CabaretError(u'処理済みです', CabaretError.Code.ALREADY_RECEIVED)
            elif 0 < num:
                vnum_add, rnum_add = 0, 0
                if is_pay:
                    model.rnum += num
                    rnum_add = num
                else:
                    model.vnum += num
                    vnum_add = num
                # ログ.
                UserLogItemGet.create(model.uid, model.mid, model.vnum, model.rnum, vnum_add, rnum_add).save()
            else:
                vnum_rem, rnum_rem = 0, 0
                vnum = model.vnum + num
                if vnum < 0:
                    rnum = model.rnum + vnum
                    vnum = 0
                    if rnum < 0:
                        raise CabaretError(u'アイテムの所持数が足りません', CabaretError.Code.NOT_ENOUGH)
                    rnum_rem = model.rnum - rnum
                    model.rnum = rnum
                vnum_rem = model.vnum - vnum
                model.vnum = vnum
                # ログ.
                UserLogItemUse.create(model.uid, model.mid, model.vnum, model.rnum, vnum_rem, rnum_rem).save()
            wresult['model'] = model
        
        if num < 0 and do_check_mission:
            # ミッション.
            mission_executer = PanelMissionConditionExecuter()
            mission_executer.addTargetUseItem(mid, -num)
            BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
        
        def writeEnd():
            model = wresult.get('model')
            if model:
                KpiOperator().set_save_itemnum(uid, mid, model.rnum, model.vnum).save()
        
        model_mgr.add_forupdate_task(Item, Item.makeID(uid, mid), forUpdateTask)
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def put_itemuselead_info(handler, masteridlist_use, masteridlist_buy, num_max_getter=None):
        """体力不足とかで表示するアイテムの誘導情報.
        """
        model_mgr = handler.getModelMgr()
        v_player = handler.getViewerPlayer()
        
        # マスターデータ.
        masteridlist = list(set(tuple(masteridlist_use) + tuple(masteridlist_buy)))
        masterlist = BackendApi.get_itemmaster_list(model_mgr, masteridlist, using=settings.DB_READONLY)
        masters = {}
        for master in masterlist:
            masters[master.id] = master
        
        # 所持数.
        nums = BackendApi.get_item_nums(model_mgr, v_player.id, masteridlist, using=settings.DB_READONLY)
        
        def makeItemList(idlist, do_check_num):
            arr = []
            for mid in idlist:
                num = nums.get(mid) or 0
                if do_check_num and num < 1:
                    continue
                master = masters.get(mid)
                usenum = ItemUtil.calcUseNumMax(master, v_player, num)
                if num_max_getter:
                    usenum = min(num_max_getter(master, usenum), usenum)
                arr.append(Objects.item(handler, master, num, usenum))
            return arr
        
        # 持っているものから.
        itemlist = makeItemList(masteridlist_use, do_check_num=True)
        if not itemlist:
            itemlist = makeItemList(masteridlist_buy, do_check_num=False)
        handler.html_param['item_list'] = itemlist
        return itemlist
    
    @staticmethod
    def put_aprecover_uselead_info(handler):
        """体力回復アイテム使用の誘導を埋め込む.
        """
        masteridlist_use = Defines.ItemEffect.ACTION_RECOVERY_ITEMS
        masteridlist_buy = (Defines.ItemEffect.ACTION_ALL_RECOVERY,)
        return BackendApi.put_itemuselead_info(handler, masteridlist_use, masteridlist_buy)
    
    @staticmethod
    def put_bprecover_uselead_info(handler):
        """気力回復アイテム使用の誘導を埋め込む.
        """
        masteridlist_use = Defines.ItemEffect.TENSION_RECOVERY_ITEMS[:]
        masteridlist_buy = (Defines.ItemEffect.TENSION_ALL_RECOVERY,)
        return BackendApi.put_itemuselead_info(handler, masteridlist_use, masteridlist_buy)
    
    @staticmethod
    def put_scoutcard_uselead_info(handler, url_use):
        """名刺使用の誘導を埋め込む.
        """
        masteridlist_use = Defines.ItemEffect.SCOUT_CARD_ITEMS[:]
        masteridlist_buy = []
        objlist = BackendApi.put_itemuselead_info(handler, masteridlist_use, masteridlist_buy)
        for obj in objlist:
            obj['url_use'] = handler.makeAppLinkUrl(OSAUtil.addQuery(url_use, Defines.URLQUERY_ID, obj['master']['id']))
        return objlist
    
    @staticmethod
    def put_cabaclubitem_uselead_info(handler, cabaclubstoreset, now):
        """キャバクラ経営用アイテム使用の誘導を埋め込む.
        """
        # ignores = [cabaclubstoreset.get_current_preferential_item_id(now), cabaclubstoreset.get_current_barrier_item_id(now)]
        # 使用中でも表示するように.
        ignores = []
        scoutman_addable_num = cabaclubstoreset.get_scoutman_addable_num()
        if scoutman_addable_num < 1:
            ignores.append(Defines.ItemEffect.CABACLUB_SCOUTMAN)
        masteridlist_use = list(set(Defines.ItemEffect.CABACLUB_STORE_ITEMS) - set(ignores))
        masteridlist_buy = []
        if 0 < scoutman_addable_num:
            num_max_getter = lambda master, usenum: int((scoutman_addable_num + master.evalue - 1) / master.evalue) if master.id == Defines.ItemEffect.CABACLUB_SCOUTMAN else usenum
        else:
            num_max_getter = None
        return BackendApi.put_itemuselead_info(handler, masteridlist_use, masteridlist_buy, num_max_getter=num_max_getter)
    
    #===========================================================
    # アルバム.
    @staticmethod
    def get_cardmasterid_foralbum(model_mgr, ctype=Defines.CharacterType.ALL, rare=Defines.Rarity.ALL, offset=0, limit=-1, using=settings.DB_DEFAULT):
        """アルバム用にカードのマスターIDを絞り込み.
        """
        if not AlbumList.exists(ctype, rare):
            masterlist = model_mgr.get_mastermodel_all(CardSortMaster, using=using)
            midlist = [master.id for master in masterlist if master.hklevel == 1]
            masters = BackendApi.get_cardmasters(midlist, model_mgr, using=using)
            AlbumList.save(masters.values())
        return AlbumList.fetch(ctype, rare, offset, limit)
    
    @staticmethod
    def get_album_content_nummax(model_mgr, ctype=Defines.CharacterType.ALL, rare=Defines.Rarity.ALL, using=settings.DB_DEFAULT):
        """アルバム用にカードのマスターIDを絞り込み.
        """
        if not AlbumList.exists(ctype, rare):
            masterlist = model_mgr.get_mastermodel_all(CardSortMaster, using=using)
            midlist = [master.id for master in masterlist if master.hklevel == 1]
            masters = BackendApi.get_cardmasters(midlist, model_mgr, using=using)
            AlbumList.save(masters.values())
        return AlbumList.length(ctype, rare)
    
    @staticmethod
    def tr_set_memories_vtime(uid, master):
        model_mgr = ModelRequestMgr()
        mid = master.id
        
        ins = Memories.makeInstance(Memories.makeID(uid, mid))
        model_mgr.set_save(ins)
        
        # ミッション.
        mission_executer = PanelMissionConditionExecuter()
        if master.contenttype == Defines.MemoryContentType.IMAGE:
            mission_executer.addTargetViewMemoriesImage()
        elif master.contenttype in (Defines.MemoryContentType.MOVIE, Defines.MemoryContentType.MOVIE_PC):
            mission_executer.addTargetViewMemoriesMovie()
        BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
        
        model_mgr.write_all()
        return model_mgr
    
    @staticmethod
    def get_album_list(apphandler, uid, ctype, rare, offset=0, limit=-1, using=settings.DB_DEFAULT):
        """アルバム一覧を取得.
        """
        
        model_mgr = apphandler.getModelMgr()
        
        # マスター取得
        masteridlist = BackendApi.get_cardmasterid_foralbum(model_mgr, ctype, rare, offset, limit, using=using)
        
        # データがない
        if len(masteridlist) == 0:
            return []
        
        masters = BackendApi.get_cardmasters(masteridlist, model_mgr, using=using)
        
        albumidlist = []
        stockidlist = []
        for master in masters.values():
            albumidlist.append(master.album)
            if CardUtil.checkStockableMaster(master, raise_on_error=False):
                stockidlist.append(master.album)
        
        # 開放フラグ取得.
        album_acquisitions = BackendApi.get_albumacquisitions(model_mgr, uid, albumidlist, using=using)
        
        # 移動数.
        stockidlist = list(set(stockidlist) & set(album_acquisitions.keys()))
        stocknum_models = BackendApi.get_cardstocks(model_mgr, uid, stockidlist, using=using)
        
        # CardMaster取得
        list_data = []
        for masterid in masteridlist:
            master = masters.get(masterid, None)
            album_acquisition = None
            stocknum = 0
            if master:
                album_acquisition = album_acquisitions.get(master.album, None)
                stocknum_model = stocknum_models.get(master.album)
                stocknum = stocknum_model.num if stocknum_model else 0
            list_data.append(Objects.listalbum(apphandler, master, album_acquisition is not None, stocknum))
        return list_data
    
    @staticmethod
    def get_cardmasterid_by_albumid(model_mgr, albumid, using=settings.DB_DEFAULT):
        if not AlbumList.exists(Defines.CharacterType.ALL, Defines.Rarity.ALL):
            masterlist = model_mgr.get_mastermodel_all(CardSortMaster, using=using)
            midlist = [master.id for master in masterlist if master.hklevel == 1]
            masters = BackendApi.get_cardmasters(midlist, model_mgr, using=using)
            AlbumList.save(masters.values())
        cardmasterid = AlbumList.get_cardid_by_albumid(albumid)
        return cardmasterid
    
    @staticmethod
    def get_albumcardmasteridlist(model_mgr, albumid, using=settings.DB_DEFAULT):
        """同じアルバムのカードIDのリスト.
        """
        client = OSAUtil.get_cache_client()
        key = 'get_albumcardmasteridlist:%s' % albumid
        
        idlist = client.get(key)
        if idlist is None:
            cardsort_list = CardSortMaster.fetchValues(filters={'album':albumid}, using=using)
            model_mgr.set_got_models(cardsort_list)
            idlist = [cardsort.id for cardsort in cardsort_list]
            client.set(key, idlist)
        return idlist
    
    @staticmethod
    def check_album_viewable(model_mgr, uid, albumid, using=settings.DB_DEFAULT):
        records = BackendApi.get_albumacquisitions(model_mgr, uid, [albumid], using=using)
        if records.get(albumid):
            return True
        else:
            return False
    
    @staticmethod
    def make_album_detail(apphandler, uid, cardmaster, using=settings.DB_DEFAULT):
        """アルバムのカード詳細情報を作成.
        """
        card = BackendApi.create_card_by_master(cardmaster)
        cardset = CardSet(card, cardmaster)
        return Objects.card(apphandler, cardset)
    
    @staticmethod
    def get_album_detail(apphandler, uid, albumid, using=settings.DB_DEFAULT):
        """アルバムのカード詳細情報を取得.
        """
        
        model_mgr = apphandler.getModelMgr()
        
        # cardID取得
        cardid = CardMaster.getValues(fields=['id'], filters={'albumhklevel':CardMaster.makeAlbumHklevel(albumid, 1)}, using=using)
        
        # card取得
        carddata = BackendApi.get_cards([CardMaster.makeID(uid, cardid.id)], model_mgr, using)
        
        album_acquisition = BackendApi.get_albumacquisition(uid, [carddata[0].card.mid], using=using)
        if album_acquisition is not None:
            detail_data = Objects.card(apphandler, carddata[0])
        else:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        return detail_data
    
    @staticmethod
    def check_album_memories_opened(memoriesmaster, card_acquisition):
        """思い出アルバムの開放確認.
        """
        return card_acquisition is not None and memoriesmaster.cardlevel <= card_acquisition.maxlevel
    
    @staticmethod
    def __get_album_memories_params(model_mgr, uid, albumid, using=settings.DB_DEFAULT):
        """アルバムの思い出リスト取得の為のパラメータを取得.
        """
        if AlbumMemoriesSet.exists(albumid):
            mid_list = AlbumMemoriesSet.fetch(albumid)
            mid_list.sort()
            # 思い出アルバムマスター取得.
            master_list = BackendApi.get_memoriesmaster_list(model_mgr, mid_list, using=using)
            # カードの取得フラグ.
            cardid_list = list(set([master.cardid for master in master_list]))
        else:
            # アルバムのカード.
            cardid_list = BackendApi.get_albumcardmasteridlist(model_mgr, albumid, using=using)
            
            # カードに設定されている思い出アルバム.
            master_list = MemoriesMaster.fetchValues(filters={'cardid__in':cardid_list}, order_by='id', using=using)
            model_mgr.set_got_models(master_list)
            
            AlbumMemoriesSet.save(albumid, master_list)
            
            mid_list = [master.id for master in master_list]
        return mid_list, master_list, cardid_list
    
    @staticmethod
    def get_album_memories_list(apphandler, uid, albumid, using=settings.DB_DEFAULT):
        """アルバムの思い出リストを取得.
        """
        model_mgr = apphandler.getModelMgr()
        
        mid_list, master_list, cardid_list = BackendApi.__get_album_memories_params(model_mgr, uid, albumid, using=using)
        
        card_acquisitions = BackendApi.get_cardacquisitions(model_mgr, uid, cardid_list, using=using)
        vtimes = BackendApi.get_memories_vtime(model_mgr, uid, mid_list, using=using)
        
        # 解放フラグを取得
        list_data = []
        for memoriesmaster in master_list:
            card_acquisition = card_acquisitions.get(memoriesmaster.cardid, None)
            vtime = vtimes.get(memoriesmaster.id)
            list_data.append(Objects.memoriesmaster(apphandler, memoriesmaster, card_acquisition, vtime))
        list_data.sort(key=lambda x:x['id'])
        return list_data
    
    @staticmethod
    def check_album_memories_complete(model_mgr, uid, albumid, using=settings.DB_DEFAULT):
        """アルバムの思い出リストを取得.
        """
        _, master_list, cardid_list = BackendApi.__get_album_memories_params(model_mgr, uid, albumid, using=using)
        
        card_acquisitions = BackendApi.get_cardacquisitions(model_mgr, uid, cardid_list, using=using)
        
        for memoriesmaster in master_list:
            card_acquisition = card_acquisitions.get(memoriesmaster.cardid, None)
            if not BackendApi.check_album_memories_opened(memoriesmaster, card_acquisition):
                return False
        return True
    
    @staticmethod
    def get_movieplaylist_master(model_mgr, mid, using=settings.DB_DEFAULT):
        """動画プレイリストマスターデータ.
        """
        return BackendApi.get_model(model_mgr, MoviePlayList, mid, using=using)
    
    @staticmethod
    def get_movieplaylist_master_list(model_mgr, midlist, using=settings.DB_DEFAULT):
        """動画プレイリストマスターデータ.
        """
        return BackendApi.get_model_list(model_mgr, MoviePlayList, midlist, using=using)
    
    @staticmethod
    def get_movieplaylist_master_dict(model_mgr, midlist, using=settings.DB_DEFAULT):
        """動画プレイリストマスターデータ.
        """
        return BackendApi.get_model_dict(model_mgr, MoviePlayList, midlist, using=using)
    
    @staticmethod
    def get_movieplaylist_dict_by_uniquename(model_mgr, uniquename_list, using=settings.DB_DEFAULT):
        """動画プレイリストマスターデータをユニーク名で取得.
        """
        if not uniquename_list:
            return {}
        
        result = {}
        unique_to_mid = MoviePlayListUniqueNameSetSp.fetch(uniquename_list)
        not_found_list = list(set(uniquename_list) - set(unique_to_mid.keys()))
        if not_found_list:
            # 見つからなかったのでDBから引いてくる.
            masterlist = MoviePlayList.fetchValues(filters={'filename__in' : not_found_list}, using=using)
            if masterlist:
                MoviePlayListUniqueNameSetSp.save(masterlist)
                model_mgr.set_got_models(masterlist)
                for master in masterlist:
                    result[master.filename] = master
        masterlist = BackendApi.get_movieplaylist_master_list(model_mgr, unique_to_mid.values(), using=settings.DB_READONLY)
        for master in masterlist:
            result[master.filename] = master
        return result
    
    @staticmethod
    def get_movieplaylist_all(model_mgr, using=settings.DB_DEFAULT):
        """動画プレイリストマスターデータ.
        """
        return model_mgr.get_mastermodel_all(MoviePlayList, using=using)
    
    @staticmethod
    def get_pcmovieplaylist_master(model_mgr, mid, using=settings.DB_DEFAULT):
        """動画(PC)プレイリストマスターデータ.
        """
        return BackendApi.get_model(model_mgr, PcMoviePlayList, mid, using=using)
    
    @staticmethod
    def get_pcmovieplaylist_master_list(model_mgr, midlist, using=settings.DB_DEFAULT):
        """動画(PC)プレイリストマスターデータ.
        """
        return BackendApi.get_model_list(model_mgr, PcMoviePlayList, midlist, using=using)
    
    @staticmethod
    def get_pcmovieplaylist_master_dict(model_mgr, midlist, using=settings.DB_DEFAULT):
        """動画(PC)プレイリストマスターデータ.
        """
        return BackendApi.get_model_dict(model_mgr, PcMoviePlayList, midlist, using=using)
    
    @staticmethod
    def get_pcmovieplaylist_dict_by_uniquename(model_mgr, uniquename_list, using=settings.DB_DEFAULT):
        """動画プレイリストマスターデータをユニーク名で取得.
        """
        if not uniquename_list:
            return {}
        
        result = {}
        unique_to_mid = MoviePlayListUniqueNameSetPc.fetch(uniquename_list)
        not_found_list = list(set(uniquename_list) - set(unique_to_mid.keys()))
        if not_found_list:
            # 見つからなかったのでDBから引いてくる.
            masterlist = PcMoviePlayList.fetchValues(filters={'filename__in' : not_found_list}, using=using)
            if masterlist:
                MoviePlayListUniqueNameSetPc.save(masterlist)
                model_mgr.set_got_models(masterlist)
                for master in masterlist:
                    result[master.filename] = master
        masterlist = BackendApi.get_pcmovieplaylist_master_list(model_mgr, unique_to_mid.values(), using=settings.DB_READONLY)
        for master in masterlist:
            result[master.filename] = master
        return result
    
    @staticmethod
    def get_pcmovieplaylist_all(model_mgr, using=settings.DB_DEFAULT):
        """動画(PC)プレイリストマスターデータ.
        """
        return model_mgr.get_mastermodel_all(PcMoviePlayList, using=using)
    
    @staticmethod
    def get_voiceplaylist_master(model_mgr, mid, using=settings.DB_DEFAULT):
        """音声プレイリストマスターデータ.
        """
        return BackendApi.get_model(model_mgr, VoicePlayList, mid, using=using)
    
    @staticmethod
    def get_voiceplaylist_all(model_mgr, using=settings.DB_DEFAULT):
        """音声プレイリストマスターデータ.
        """
        return model_mgr.get_mastermodel_all(VoicePlayList, using=using)
    
    @staticmethod
    def tr_add_movieviewdata(model_mgr, mid, cnt=1):
        """動画閲覧回数加算.
        """
        def forUpdateTask(model, inserted):
            model.cnt += cnt
            model_mgr.set_save(model)
        
        model_mgr.add_forupdate_task(MovieViewData, mid, forUpdateTask)
        
        def writeEnd():
            pass
        
        model_mgr.add_write_end_method(writeEnd)
        
        return
    
    @staticmethod
    def get_movieview_list(model_mgr, using=settings.DB_DEFAULT):
        """動画閲覧回数取得.
        """
        movieviewlist = MovieViewData.fetchValues(using=using)
        return movieviewlist
    
    @staticmethod
    def tr_add_pcmovieviewdata(model_mgr, mid, cnt=1):
        """動画(PC)閲覧回数加算.
        """
        def forUpdateTask(model, inserted):
            model.cnt += cnt
            model_mgr.set_save(model)
        
        model_mgr.add_forupdate_task(PcMovieViewData, mid, forUpdateTask)
        
        def writeEnd():
            pass
        
        model_mgr.add_write_end_method(writeEnd)
        
        return
    
    @staticmethod
    def get_pcmovieview_list(model_mgr, using=settings.DB_DEFAULT):
        """動画(PC)閲覧回数取得.
        """
        movieviewlist = PcMovieViewData.fetchValues(using=using)
        return movieviewlist
    
    #===========================================================
    # スカウト.
    @staticmethod
    def get_scouts(model_mgr, scoutidlist, using=settings.DB_DEFAULT):
        """スカウトを取得.
        """
        return BackendApi.get_model_list(model_mgr, ScoutMaster, scoutidlist, using=using)
    
    @staticmethod
    def get_scout_dict(model_mgr, scoutidlist, using=settings.DB_DEFAULT):
        """スカウトを取得.
        """
        return BackendApi.get_model_dict(model_mgr, ScoutMaster, scoutidlist, using=using)
    
    @staticmethod
    def get_arealist(model_mgr, areaidlist, using=settings.DB_DEFAULT):
        """エリアを取得.
        """
        arealist = BackendApi.get_model_list(model_mgr, AreaMaster, areaidlist, using=using)
        return [area for area in arealist if BackendApi.check_schedule(model_mgr, area.schedule, using=using)]
    
    @staticmethod
    def get_area(model_mgr, areaid, using=settings.DB_DEFAULT):
        """エリアを取得.
        """
        arealist = BackendApi.get_arealist(model_mgr, [areaid], using)
        if arealist:
            return arealist[0]
        else:
            return None
    
    @staticmethod
    def get_playable_area_all(model_mgr, uid, using=settings.DB_DEFAULT):
        """プレイ可能なエリアを全て取得.
        """
        arealist = model_mgr.get_mastermodel_all(AreaMaster, using=using)
        playdata_dict = BackendApi.get_areaplaydata(model_mgr, uid, [area.id for area in arealist], using=using)
        
        result = []
        for area in arealist:
            if not BackendApi.check_schedule(model_mgr, area.schedule, using=using):
                continue
            elif area.opencondition and not playdata_dict.get(area.opencondition):
                continue
            result.append(area)
        
        result.sort(key=operator.attrgetter('id'))
        return result
    
    @staticmethod
    def _save_scoutidlist_by_area(model_mgr, area, using=settings.DB_DEFAULT):
        """エリアのスカウトID一覧を保存.
        """
        scoutlist = ScoutMaster.fetchValues(filters={'area':area}, using=using)
        scoutidlist = [scout.id for scout in scoutlist]
        AreaScoutListCache.save(area, scoutidlist)
        return scoutidlist
    
    @staticmethod
    def get_scoutidlist_by_area(model_mgr, areaid, using=settings.DB_DEFAULT):
        """エリアからでスカウトのID一覧を取得.
        """
        if AreaScoutListCache.exists(areaid):
            idlist = AreaScoutListCache.getScoutIdList(areaid)
        else:
            idlist = BackendApi._save_scoutidlist_by_area(model_mgr, areaid, using=using)
        idlist.sort()
        return idlist
    
    @staticmethod
    def get_areaplaydata(model_mgr, uid, areaidlist, using=settings.DB_DEFAULT):
        """エリアのプレイ情報を取得.
        """
        idlist = [AreaPlayData.makeID(uid, areaid) for areaid in areaidlist]
        result = BackendApi.get_model_dict(model_mgr, AreaPlayData, idlist, using=using, key=lambda x:x.mid)
        return result
    
    @staticmethod
    def get_scoutprogress(model_mgr, uid, scoutidlist, using=settings.DB_DEFAULT, reflesh=False):
        """スカウトの進行情報を取得.
        """
        progressidlist = [ScoutPlayData.makeID(uid, scoutid) for scoutid in scoutidlist]
        if reflesh:
            modellist = ScoutPlayData.getByKey(progressidlist, using=using)
            modeldict = dict([(model.mid, model) for model in modellist])
            model_mgr.set_got_models(modellist)
            model_mgr.save_models_to_cache(modellist)
        else:
            modeldict = BackendApi.get_model_dict(model_mgr, ScoutPlayData, progressidlist, using=using, key=lambda x:x.mid)
        return modeldict
    
    @staticmethod
    def get_scoutkey(model_mgr, uid, scoutid, using=settings.DB_DEFAULT):
        """スカウトの実行用キーを取得.
        """
        playdata = BackendApi.get_scoutprogress(model_mgr, uid, [scoutid], using).get(scoutid)
        if playdata is None:
            def tr(uid, scoutid):
                mgr = ModelRequestMgr()
                playdata = ScoutPlayData.makeInstance(ScoutPlayData.makeID(uid, scoutid))
                mgr.set_save(playdata)
                mgr.write_all()
                return mgr, playdata
            mgr, playdata = db_util.run_in_transaction(tr, uid, scoutid)
            mgr.write_end()
            
            model_mgr.set_got_models([playdata], using=settings.DB_DEFAULT)
            model_mgr.set_got_models([playdata], using=settings.DB_READONLY)
        return playdata.confirmkey
    
    @staticmethod
    def get_apcost(scoutmaster, player):
        """消費行動力.
        """
        if isinstance(scoutmaster, ScoutMaster) and player.level < Defines.BIGINNER_PLAYERLEVEL:
            return 0
        elif settings_sub.IS_BENCH:
            return 0
        return scoutmaster.apcost
    
    @staticmethod
    def save_lastview_areaid(uid, areaid, pipe=None):
        """最後に見たエリアIDを保存.
        """
        LastViewArea.create(uid, areaid).save(pipe)
    
    @staticmethod
    def delete_lastview_areaid(uid, pipe=None):
        """最後に見たエリアIDを削除.
        """
        LastViewArea.create(uid).delete(pipe)
    
    @staticmethod
    def get_lastview_area(model_mgr, uid, using=settings.DB_DEFAULT):
        """最後に見たエリアを取得.
        """
        model = LastViewArea.get(uid)
        area = None
        if model is not None:
            area = BackendApi.get_area(model_mgr, model.areaid, using=using)
        return area
    
    @staticmethod
    def get_newbie_areaid(model_mgr, uid, using=settings.DB_DEFAULT):
        """今遊べる最新のエリアID.
        """
        arealist = model_mgr.get_mastermodel_all(AreaMaster, using=using)
        arealist.sort(key=operator.attrgetter('id'))
        
        playdataidlist = []
        conditionmap = {}
        default_area_list = []
        for area in arealist:
            if area.opencondition:
                conditionmap[area.opencondition] = area
            else:
                default_area_list.insert(0, area)
            playdataidlist.append(AreaPlayData.makeID(uid, area.id))
        
        playdatalist = model_mgr.get_models(AreaPlayData, playdataidlist, using=using)
        playdatalist.sort(key=operator.attrgetter('mid'), reverse=True)
        
        clearflags = {}
        target_area = None
        for playdata in playdatalist:
            clearflags[playdata.mid] = True
            area = conditionmap.get(playdata.mid, None)
            if area is None:
                continue
            elif not BackendApi.check_schedule(model_mgr, area.schedule, using=using):
                continue
            target_area = area
            break
        
        if target_area is None:
            # 見つからなかったから最初から開いているエリアから選ぶ.
            for area in default_area_list:
                if BackendApi.check_schedule(model_mgr, area.schedule, using=using):
                    target_area = area
                    break
        
        if target_area is None:
            raise CabaretError(u'遊べるエリアがありません.uid=%d' % uid, CabaretError.Code.INVALID_MASTERDATA)
        
        return target_area.id
    
    @staticmethod
    def get_next_areaid(model_mgr, areaid, using=settings.DB_DEFAULT):
        """次のエリアIDを取得.
        """
        client = OSAUtil.get_cache_client()
        key = "get_next_areaid:%s" % areaid
        nextareaid = client.get(key)
        
        if str(nextareaid).isdigit():
            nextareaid = int(nextareaid)
        else:
            model = AreaMaster.getValues(filters={'opencondition':areaid}, using=settings.DB_READONLY)
            if model:
                model_mgr.set_got_models([model])
                nextareaid = model.id
            else:
                nextareaid = areaid
            client.set(key, nextareaid)
        return nextareaid
    
    @staticmethod
    def get_next_scoutid(model_mgr, scoutid, using=settings.DB_DEFAULT):
        """次のスカウトIDを取得.
        """
        model = ScoutMaster.getValues(filters={'opencondition':scoutid}, using=settings.DB_READONLY)
        if model:
            model_mgr.set_got_models([model])
            return model.id
        else:
            return scoutid
    
    @staticmethod
    def check_area_playable(model_mgr, area, uid, using=settings.DB_DEFAULT):
        """指定したエリアを閲覧できるかをチェック.
        """
        if area is None:
            return False
        elif not BackendApi.check_schedule(model_mgr, area.schedule, using=using):
            # 期間外.
            return False
        elif 0 < area.opencondition:
            playdata = model_mgr.get_model(AreaPlayData, AreaPlayData.makeID(uid, area.opencondition), using=using)
            if playdata is None:
                # 開放条件を満たしていない.
                return False
        return True
    
    @staticmethod
    def check_scout_playable(model_mgr, scoutmaster, player, using=settings.DB_DEFAULT):
        """指定したスカウトを実行できるかをチェック.
        """
        areamaster = BackendApi.get_area(model_mgr, scoutmaster.area, using=using)
        if not BackendApi.check_area_playable(model_mgr, areamaster, player.id, using=using):
            # エリアが開放されていない.
            return False
        elif 0 < scoutmaster.opencondition:
            # 開放条件が設定されている.
            cond_scoutmaster = model_mgr.get_model(ScoutMaster, scoutmaster.opencondition, using=using)
            if cond_scoutmaster is None:
                raise CabaretError(u'存在しないスカウトがクリア条件に設定されています.%d' % scoutmaster.opencondition, CabaretError.Code.INVALID_MASTERDATA)
            playdata_dict = BackendApi.get_scoutprogress(model_mgr, player.id, [scoutmaster.opencondition], using=using)
            playdata = playdata_dict.get(scoutmaster.opencondition, None)
            if playdata is None or playdata.progress < cond_scoutmaster.execution:
                # クリアしていない.
                return False
        return True
    
    @staticmethod
    def get_dropitemobj_list(handler, player, scoutmaster, using=settings.DB_DEFAULT):
        """ドロップアイテム情報.
        """
        model_mgr = handler.getModelMgr()
        if isinstance(scoutmaster, ScoutMaster):
            playdata = BackendApi.get_scoutprogress(model_mgr, player.id, [scoutmaster.id], using=using).get(scoutmaster.id)
            dropitems = scoutmaster.dropitems
        elif isinstance(scoutmaster, HappeningMaster):
            playdata = BackendApi.get_current_happening(model_mgr, player.id, using=using)
            dropitems = scoutmaster.items
        else:
            raise CabaretError(u'想定外のマスターデータ. %s' % scoutmaster)
        datalist = ScoutDropItemSelector.dropitemsTodatalist(dropitems, player)
        
        table = {
            Defines.ItemType.CARD : CardMaster,
            Defines.ItemType.ITEM : ItemMaster,
        }
        
        obj_list = []
        for data in datalist:
            itype = data.itype
            model_cls = table.get(itype)
            if model_cls is None:
                raise CabaretError(u'未実装のドロップアイテムが設定されています.scout=%d' % scoutmaster.id, CabaretError.Code.INVALID_MASTERDATA)
            mid = data.mid
            master = model_mgr.get_model(model_cls, mid)
            if master is None:
                raise CabaretError(u'存在しないドロップアイテムが設定されています.scout=%d' % scoutmaster.id, CabaretError.Code.INVALID_MASTERDATA)
            flag = playdata and playdata.idDropped(itype, mid)
            obj_list.append(Objects.scoutdropitem(handler, master, flag))
        
        return obj_list
    
    @staticmethod
    def check_areascout_allcleared(model_mgr, uid, areaid, using):
        """エリアのスカウトをすべてクリアしてるかチェック.
        """
        # エリアのスカウトを全てクリアしていないといけない.
        scoutidlist = BackendApi.get_scoutidlist_by_area(model_mgr, areaid, using=using)
        scoutlist = BackendApi.get_scouts(model_mgr, scoutidlist, using=using)
        if len(scoutlist) < 1:
            return False
        scoutplaydata_dict = BackendApi.get_scoutprogress(model_mgr, uid, scoutidlist, using=using)
        for scout in scoutlist:
            playdata = scoutplaydata_dict.get(scout.id, None)
            if playdata is None or playdata.progress < scout.execution:
                return False
        return True
    
    @staticmethod
    def choice_raideventscout_happeningtable(model_mgr, eventmaster, stagemaster=None, now=None, using=settings.DB_DEFAULT):
        """.
        """
        if eventmaster.flag_dedicated_stage:
            getter = lambda att:getattr(stagemaster or eventmaster, att) or getattr(eventmaster, att)
        else:
            getter = lambda att:getattr(eventmaster, att)
        
        config = BackendApi.get_current_raideventconfig(model_mgr, using=using)
        _, etime = BackendApi.choice_raidevent_timebonus_time(config, now=now)
        if BackendApi.check_raidevent_bigboss_opened(model_mgr, now=now, using=using):
            if etime is None:
                # タイムボーナスじゃない.
                event_happenings = getter('raidtable_big')
            else:
                # タイムボーナス.
                event_happenings = getter('raidtable_timebonus_big')
        else:
            if etime is None:
                # タイムボーナスじゃない.
                event_happenings = getter('raidtable')
            else:
                # タイムボーナス.
                event_happenings = getter('raidtable_timebonus')
        return event_happenings
    
    @staticmethod
    def tr_raidevent_start_champagnecall(model_mgr, uid, champagnecall_start, now):
        """シャンパンコール開始.
        """
        champagnecall_started = False
        if champagnecall_start:
            eventmaster = BackendApi.get_current_raideventmaster(model_mgr)
            if eventmaster:
                champagnedata = RaidEventChampagne.getByKeyForUpdate(uid)
                if champagnedata is None:
                    # 何かデータが壊れている.
                    raise CabaretError(u'Broken:RaidEventChampagne...%d' % uid)
                champagnedata.setStartChampagneCall(eventmaster.id, eventmaster.champagne_time, now=now)
                model_mgr.set_save(champagnedata)
                champagnecall_started = True
        return champagnecall_started
    
    @staticmethod
    def tr_do_scout(model_mgr, player, scoutmaster, key, champagnecall=False, champagnecall_start=False):
        """スカウト実行.
        """
        # 重複チェック.
        playdata = ScoutPlayData.getByKeyForUpdate(ScoutPlayData.makeID(player.id, scoutmaster.id))
        if playdata.alreadykey == key:
            raise CabaretError(u'実行済みです', CabaretError.Code.ALREADY_RECEIVED)
        elif playdata.confirmkey != key:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        # 次のレベル.
        nextlevelexp = BackendApi.get_playerlevelexp_bylevel(player.level+1, model_mgr)
        
        event_happenings = None
        eventid = 0
        now = OSAUtil.get_now()
        
        # ミッション確認用オブジェクト.
        mission_executer = PanelMissionConditionExecuter()
        
        # 現在のハプニング情報.
        do_select_happening = True
        happeningset = BackendApi.get_current_happening(model_mgr, player.id)
        if happeningset and not happeningset.happening.is_end():
            do_select_happening = False
        else:
            eventmaster = BackendApi.get_current_raideventmaster(model_mgr)
            if eventmaster and not eventmaster.flag_dedicated_stage:
                event_happenings = BackendApi.choice_raideventscout_happeningtable(model_mgr, eventmaster, now=now)
                eventid = eventmaster.id
        
        # 現在カード枚数.
        cardnum = BackendApi.get_cardnum(player.id, model_mgr)
        
        # 称号.
        title_master = BackendApi.get_current_title_master(model_mgr, player.id, now)
        
        # 実行オブジェクト.
        executer = ScoutExec(player, playdata, playdata.seed, scoutmaster, nextlevelexp, cardnum, do_select_happening, event_happenings, title=title_master)
        
        # 消費行動力.
        apcost = BackendApi.get_apcost(scoutmaster, player)
        
        # 終了するまで実行.
        while not executer.is_end:
            executer.execute(apcost)
        
        # SHOWTIME.
        champagnecall_started = False
        if 0 < executer.exec_cnt:
            champagnecall_started = BackendApi.tr_raidevent_start_champagnecall(model_mgr, player.id, champagnecall_start, now)
            champagnecall = champagnecall or champagnecall_started
        
        # スカウト実行を登録.
        mission_executer.addTargetDoScout(executer.exec_cnt)
        
        # 結果を集計.
        prize = executer.aggregatePrizes()
        # 想定外のイベント.
        if prize.get('item', None):
            raise CabaretError(u'想定外のドロップアイテムが設定されています.ScoutMaster.id=%d' % scoutmaster.id, CabaretError.Code.INVALID_MASTERDATA)
        
        # お金.
        gold = prize['gold']
        if 0 < gold:
            BackendApi.tr_add_gold(model_mgr, player.id, gold)
        # 経験値.
        exp = prize['exp']
        if 0 < exp:
            BackendApi.tr_add_exp(model_mgr, player, exp)
            level = player.level
            levelupevent = prize.get('levelup', None)
            if levelupevent:
                # 書き込み後のれべる.
                levelupevent.set_level(level)
                
                # レベルを確認.
                mission_executer.addTargetPlayerLevel(level)
        
        # 宝箱.
        treasureevent = prize.get('treasure', None)
        if treasureevent:
            # 宝箱の所持数確認.
            treasure_num = BackendApi.get_treasure_num(model_mgr, treasureevent.treasuretype, player.id)
            treasuremaster = None
            if treasure_num < Defines.TreasureType.POOL_LIMIT.get(treasureevent.treasuretype, 0):
                treasuremaster = BackendApi.choice_treasure(model_mgr, treasureevent.treasuretype)
            if treasuremaster is None:
                executer.cancelEvent()
            else:
                BackendApi.tr_add_treasure(model_mgr, player.id, treasureevent.treasuretype, treasuremaster.id)
        
        # ハプニング.
        happeningevent = prize.get('happening', None)
        if happeningevent:
            eventvalue = HappeningUtil.make_raideventvalue(eventid)
            BackendApi.tr_create_happening(model_mgr, player.id, happeningevent.happening, player.level, eventvalue, champagne=champagnecall)
        
        # スカウト完了.
        completeevent = prize.get('complete', None)
        if completeevent:
            player.deckcapacityscout += 1
            model_mgr.set_save(player.getModel(PlayerDeck))
            # フレンドの近況.
            logdata = ScoutClearLog.makeData(player.id, scoutmaster.id)
            BackendApi.tr_add_friendlog(model_mgr, logdata)
            # ログ.
            model_mgr.set_save(UserLogScoutComplete.create(player.id, scoutmaster.id))
            
            def writeCompleteEnd():
                KpiOperator().set_incrment_scoutcomplete_count(scoutmaster.id).save()
            model_mgr.add_write_end_method(writeCompleteEnd)
        
        # 行動力.
        # レベルが上がったら行動力は書き込まなくていい.
        if not executer.is_levelup:
            player.set_ap(executer.ap)
            model_mgr.set_save(player.getModel(PlayerAp))
        
        # プレイデータの書き込み.
        playdata.progress = executer.progress
        playdata.seed = executer.rand._seed
        playdata.alreadykey = playdata.confirmkey
        playdata.confirmkey = OSAUtil.makeSessionID()
        playdata.setResult(executer.result, executer.eventlist, champagnecall_started=champagnecall_started)
        model_mgr.set_save(playdata)
        
        # 最後にプレイしたスカウト.
        playerscout = model_mgr.get_model(PlayerScout, player.id, get_instance=True)
        playerscout.lastscout = scoutmaster.id
        model_mgr.set_save(playerscout)
        
        # ミッション達成書き込み.
        BackendApi.tr_complete_panelmission(model_mgr, player.id, mission_executer, now)
        
        def writeEnd():
            pipe = RedisModel.getDB().pipeline()
            BackendApi.save_lastview_areaid(player.id, scoutmaster.area, pipe=pipe)
            if happeningevent:
                # どこでハプニングが発生したかを保存.
                PlayerLastHappeningType.createFromScout(player.id).save(pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
        
        return playdata
    
    @staticmethod
    def tr_area_clear(model_mgr, player, area):
        """エリアクリア書き込み.
        """
        # クリアフラグ書き込み.
        def forUpdate(model, inserted):
            if not inserted:
                raise CabaretError(u'クリア済みです', CabaretError.Code.ALREADY_RECEIVED)
            model.clevel = player.level
        model_mgr.add_forupdate_task(AreaPlayData, AreaPlayData.makeID(player.id, area.id), forUpdate)
        
        # 報酬.
        prizeidlist = area.prizes
        prizelist = BackendApi.get_prizemaster_list(model_mgr, prizeidlist)
        dic = {}
        for prize in prizelist:
            dic[prize.id] = PrizeData.createByMaster(prize)
        prizelist = []
        for prizeid in prizeidlist:
            if not dic.has_key(prizeid):
                raise CabaretError(u'存在しない報酬が含まれています', CabaretError.Code.INVALID_MASTERDATA)
            prizelist.append(dic[prizeid])
        BackendApi.tr_add_prize(model_mgr, player.id, prizelist, Defines.TextMasterID.AREA_CLEAR)
        
        # ミッション.
        mission_executer = PanelMissionConditionExecuter()
        mission_executer.addTargetAreaComplete(area.id)
        BackendApi.tr_complete_panelmission(model_mgr, player.id, mission_executer)
        
        # ログ.
        model_mgr.set_save(UserLogAreaComplete.create(player.id, area.id))
        
        # フレンドの近況.
        logdata = BossWinLog.makeData(player.id, area.id)
        BackendApi.tr_add_friendlog(model_mgr, logdata)
    
    @staticmethod
    def get_determine_scoutcard_rate(cardmaster, itemmaster, usenum=1):
        """カードの獲得率を取得.
        """
        addv = 0
        if itemmaster:
            if not itemmaster.id in Defines.ItemEffect.SCOUT_CARD_ITEMS:
                raise CabaretError(u'名刺ではありません:%d' % itemmaster.id)
            addv = itemmaster.evalue
            addv *= usenum
        rate = Defines.Rarity.SCOUT_DETERMINE_RATE.get(cardmaster.rare, 0)
        return min(100, max(0, rate + addv))
    
    @staticmethod
    def find_scout_event(scoutplaydata, eventid):
        """指定したイベントを探す.
        """
        if not scoutplaydata:
            return None
        
        resultdata = scoutplaydata.result
        eventlist = resultdata.get('event')
        
        if not eventlist:
            return None
        
        target_event = None
        for event in eventlist:
            if event.get_type() == eventid:
                target_event = event
                break
        return target_event
    
    @staticmethod
    def tr_determine_scoutcard(model_mgr, uid, scoutid, itemmaster, autosell_rarity=None):
        """スカウトカード獲得.
        """
        # スカウト情報を取得.
        playdata = ScoutPlayData.getByKeyForUpdate(ScoutPlayData.makeID(uid, scoutid))
        target_event = BackendApi.find_scout_event(playdata, Defines.ScoutEventType.GET_CARD)
        
        # フラグ確認.
        if target_event is None:
            raise CabaretError(u'女の子に遭遇していません', CabaretError.Code.NOT_DATA)
        elif target_event.is_received:
            raise CabaretError(u'処理済みです', CabaretError.Code.ALREADY_RECEIVED)
        
        # カードのマスターデータ.
        card_mid = target_event.card
        cardmaster = BackendApi.get_cardmasters([card_mid], model_mgr).get(card_mid, None)
        if cardmaster is None:
            raise CabaretError(u'キャストが見つかりませんでした', CabaretError.Code.INVALID_MASTERDATA)
        
        # アイテム消費.
        if itemmaster:
            BackendApi.tr_add_item(model_mgr, uid, itemmaster.id, -1)
        
        # 獲得判定.
        rate = BackendApi.get_determine_scoutcard_rate(cardmaster, itemmaster)
        is_success = AppRandom().getIntN(100) < rate
        
        # カード付与.
        sellprice = None
        sellprice_treasure = None
        if is_success:
            playercard = PlayerCard.getByKeyForUpdate(uid)
            playerdeck = BackendApi.get_model(model_mgr, PlayerDeck, uid)
            if BackendApi.check_sellauto(cardmaster, autosell_rarity) or BackendApi.get_cardnum(uid, model_mgr) < playerdeck.cardlimit:
                result = BackendApi.tr_create_card(model_mgr, playercard, card_mid, way=Defines.CardGetWayType.SCOUT, autosell_rarity=autosell_rarity)
                is_new = result.get('is_new', False)
                if result.get('autosell', False):
                    sellprice = result.get('sellprice', 0)
                    sellprice_treasure = result.get('sellprice_treasure', 0)
                target_event.set_new(is_new)
            else:
                present = Present.createByCard(0, uid, cardmaster, Defines.TextMasterID.SCOUT)
                model_mgr.set_save(present)
                
                def writePresentEnd():
                    redisdb = RedisModel.getDB()
                    pipe = redisdb.pipeline()
                    BackendApi.add_present(uid, present, pipe=pipe)
                    pipe.execute()
                model_mgr.add_write_end_method(writePresentEnd)
            playdata.addDropItem(Defines.ItemType.CARD, card_mid)
        
        # 結果書き込み.
        target_event.set_result(is_success, sellprice, sellprice_treasure)
        model_mgr.set_save(playdata)
        
        # 結果を返す.
        return is_success
    
    @staticmethod
    def make_scoutresult_info(resultlist):
        """スカウト結果情報.
        """
        ap_add = 0
        exp_add = 0
        gold_add = 0
        progress_add = 0
        
        for result in resultlist:
            # 進行度.
            progress_pre = result['progress_pre']
            progress_post = result['progress']
            progress_add += progress_post - progress_pre
            
            # お金.
            gold_add += result['gold_add']
            
            # 経験値.
            exp_add += result['exp_add']
            
            # 体力.
            ap_pre = result['ap_pre']
            ap_post = result['ap_post']
            ap_add += ap_post - ap_pre
        dest = {
            'ap_add' : ap_add,
            'progress_add' : progress_add,
        }
        if exp_add != 0:
            dest['exp_add'] = exp_add
        if gold_add != 0:
            dest['gold_add'] = gold_add
        return dest
    
    @staticmethod
    def make_scoutanim_params(handler, scoutmaster, eventlist, resultlist, feveretime=None):
        """スカウト実行演出のクエリパラメータを作成.
        """
        if not resultlist:
            # 演出不要.
            return None
        
        params = {}
        
        model_mgr = handler.getModelMgr()
        using = settings.DB_READONLY
        
        girls = None
        if isinstance(scoutmaster, ScoutMaster):
            areamaster = BackendApi.get_area(model_mgr, scoutmaster.area, using=using)
            girls = areamaster.girls
        elif isinstance(scoutmaster, HappeningMaster):
            girls = scoutmaster.girls
        elif isinstance(scoutmaster, EventScoutStageMaster):
            girls = scoutmaster.girls
        girls = girls or [u'・・・・・・・']
        
        if eventlist:
            # ここで必要なのははじめの１件.
            event = eventlist[0]
        else:
            # なにも起きなかった.
            event = ScoutEventNone.create()
        
        eventKind = event.get_type()
        eventTexts = Defines.ScoutEventType.EVENT_TEXTS.get(eventKind, None)
        pat = 0
        eventTextParams = None
        
        # イベント毎の設定.
        if eventKind == Defines.ScoutEventType.GET_TREASURE:
            params['eventImage'] = handler.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlMiddleByTreasureType(event.treasuretype))
            eventTextParams = Defines.TreasureType.NAMES[event.treasuretype]
            if event.treasuretype == Defines.TreasureType.BRONZE:
                pat = 1
        
        if eventTexts and pat < len(eventTexts):
            eventText = eventTexts[pat]
        else:
            eventText = u''
        if eventText and eventTextParams is not None:
            eventText = eventText % eventTextParams
        
        if Defines.ScoutEventType.ANIMATION_EVENTS.has_key(eventKind):
            params['eventKind'] = Defines.ScoutEventType.ANIMATION_EVENTS[eventKind]
        elif eventText:
            params['eventKind'] = Defines.ScoutEventType.DEFAULT_ANIMATION_EVENT_WITH_TEXT
        else:
            params['eventKind'] = Defines.ScoutEventType.DEFAULT_ANIMATION_EVENT_TEXT_NONE
        
        charText = []
        cgText = []
        expText = []
        progressGauge = []
        hpGauge = []
        expGauge = []
        
        progress_post = None
        ap_post = None
        exp_post = None
        ap_max = None
        levelexp = None
        nextlevelexp = None
        
        for result in resultlist:
            level = result['level']
            if levelexp is None or levelexp.level != level:
                levelexp = BackendApi.get_playerlevelexp_bylevel(level, model_mgr, using=settings.DB_READONLY)
                nextlevelexp = BackendApi.get_playerlevelexp_bylevel(level+1, model_mgr, using=settings.DB_READONLY)
            
            # 進行度.
            progress_pre = result['progress_pre']
            progress_post = result['progress']
            execution = result['execution']
            progressGauge.append(str(int(100 * min(execution, progress_pre) / execution)))
            
            # お金.
            gold_add = result['gold_add']
            cgText.append(u'+%s%s' % (gold_add, Defines.ItemType.UNIT[Defines.ItemType.GOLD]))
            
            # 経験値.
            if nextlevelexp is None:
                expGauge.append(str(100))
                expText.append(u'')
            else:
                exp_post = result['exp_post']
                exp = result['exp_pre'] - levelexp.exp
                exp_max = nextlevelexp.exp - levelexp.exp
                expGauge.append(str(int(100 * min(exp_max, exp) / exp_max)))
                exp_add = result['exp_add']
                if 0 < exp_add:
                    expText.append(u'+%sExp' % exp_add)
                else:
                    expText.append(u'')
            
            # 体力.
            ap_pre = result['ap_pre']
            ap_post = result['ap_post']
            ap_max = result['ap_max']
            hpGauge.append(str(int(100 * min(ap_max, ap_pre) / ap_max)))
            
            # テキスト.
            charText.append(random.choice(girls))
        
        if progress_post is not None:
            progressGauge.append(str(int(100 * min(execution, progress_post) / execution)))
        if ap_post is not None:
            hpGauge.append(str(int(100 * min(ap_max, ap_post) / ap_max)))
        if nextlevelexp is None:
            expGauge.append(str(100))
        else:
            exp = exp_post - levelexp.exp
            exp_max = nextlevelexp.exp - levelexp.exp
            expGauge.append(str(int(100 * min(exp_max, exp) / exp_max)))
        
        sep = Defines.ANIMATION_SEPARATE_STRING
        
        backImage = handler.makeAppLinkUrlImg(scoutmaster.thumb)
        if feveretime:
            # フィーバー中は背景画像を変える
            if OSAUtil.get_now() < feveretime:
                if scoutmaster.thumbfever:
                    backImage = handler.makeAppLinkUrlImg(scoutmaster.thumbfever)
        
        params.update({
            'eventText' : eventText or u'',
            'scoutNum' : len(resultlist),
            'backImage' : backImage,
            'charText' : sep.join(charText),
            'cgText' : sep.join(cgText),
            'expText' : sep.join(expText),
            'progressGauge' : sep.join(progressGauge),
            'hpGauge' : sep.join(hpGauge),
            'expGauge' : sep.join(expGauge),
        })
        return params
    
    @staticmethod
    def get_scoutskip_flag(uid):
        return bool(ScoutSkipFlag.get(uid).flag)
    @staticmethod
    def set_scoutskip_flag(uid, flag, pipe=None):
        ScoutSkipFlag.set(uid, ScoutSkipFlag.value_to_int(flag), pipe)

    @staticmethod
    def get_scoutsearch_flag(uid):
        return bool(ScoutSearchFlag.get(uid).flag)

    @staticmethod
    def set_scoutsearch_flag(uid, flag, pipe=None):
        ScoutSearchFlag.set(uid, ScoutSearchFlag.value_to_int(flag), pipe)
    
    @staticmethod
    def get_playerlasthappeningtype(uid, get_instance=True):
        """ユーザごとの最後に発生したハプニングの種別.
        """
        model = PlayerLastHappeningType.get(uid)
        if model is None and get_instance:
            model = PlayerLastHappeningType.createFromScout(uid)
        return model
    
    #===========================================================
    # ボス.
    @staticmethod
    def get_boss(model_mgr, bossid, using=settings.DB_DEFAULT):
        """ボス情報を取得.
        """
        return model_mgr.get_model(BossMaster, bossid, using=using)
    
    @staticmethod
    def bossbattle(deck_cardlist, boss, powuprate=100, specialcard=None, friendcard=None, title_power_up=0):
        """ボス戦.
        """
        rand = AppRandom()
        
        # 合計接客力.
        cardlist = deck_cardlist[:]
        if friendcard:
            cardlist.append(friendcard)
        
        # 属性ボーナス.
        weakbonus = None
        if isinstance(boss, RaidBoss):
            weakbonus = dict(boss.weakbonus or [])
        
        power_total, _, power_no_skill, _, _, _, skillinfolist, _, specialcard_idlist, v_sppowup, _, _, _, v_weakpowup, _ = BattleUtil.calcTeamPower(cardlist, [], rand, specialcard=specialcard, weakbonus=weakbonus, v_title_effect=title_power_up)
        
        leader = deck_cardlist[0]
        
        hpmax = boss.get_maxhp()
        hppre = boss.hp
        b_hp = hppre
        
        # クリティカル発生率.
        # 発生率(%)=SQRT((レア度+1)*(ハメ管理Lv*0.8)*(No1カードLv*0.2)).
        # ・小数点以下切り上げ.
        critical_rate = math.ceil(math.sqrt((leader.master.rare + 1) * (leader.master.hklevel * 0.8) * (leader.card.level * 0.2)))
        
        # ダメージ(満足度)＝合計接客力.
        damage_base = int(power_total)
        
        damage_total = 0
        
        critical = False
        
        prate = powuprate
        # クリティカル.
        if rand.getIntN(100) < critical_rate:
            prate = prate * Defines.CRITICAL_POWERUP_RATE / 100
            critical = True
        
        # 最低1入る.
        damage = int(max(1, damage_base * prate / 100))
        v_sppowup = int(v_sppowup * prate / 100)
        damage_total += damage
        
        b_hp -= damage
        if b_hp <= 0:
            damage += b_hp
            b_hp = 0
        
        animdata = BossBattleAnimParam.create(power_total, power_no_skill, deck_cardlist, skillinfolist, damage_total, hppre, b_hp, hpmax, critical, specialcard_idlist, friendcard, v_sppowup, v_weakpowup)
        
        return b_hp, animdata
    
    @staticmethod
    def tr_save_bossresult(model_mgr, uid, area, boss, animdata, key):
        """ボス戦書き込み.
        """
        BackendApi.tr_update_requestkey(model_mgr, uid, key)
        
        # 結果を保存.
        def forUpdate(model, inserted):
            model.area = area.id
            model.anim = animdata
        model_mgr.add_forupdate_task(BossBattle, uid, forUpdate)
    
    @staticmethod
    def get_bossresult(model_mgr, uid, areaid, using=settings.DB_DEFAULT):
        """ボス戦結果取得.
        """
        model = BackendApi.get_model(model_mgr, BossBattle, uid, get_instance=False, using=using)
        if model and model.area == areaid:
            return model
        else:
            return None
    
    @staticmethod
    def make_bossbattle_animation_params(handler, animdata, img_boss, img_bosscast=None):
        """ボス戦演出用パラメータ作成.
        """
        params = animdata.to_animation_data(handler)
        
        # ボス情報.
        params['bossImage'] = handler.makeAppLinkUrlImg(img_boss)
        if img_bosscast:
            params['bossCastImage'] = handler.makeAppLinkUrlImg(img_bosscast)
        
        return params
    
    #===========================================================
    # ハプニング.
    @staticmethod
    def get_happeningmasters(model_mgr, midlist, using=settings.DB_DEFAULT):
        """ハプニングマスターを取得.
        """
        return BackendApi.get_model_dict(model_mgr, HappeningMaster, midlist, using=using)
    
    @staticmethod
    def get_happeningmaster(model_mgr, mid, using=settings.DB_DEFAULT):
        """ハプニングマスターを取得.
        """
        return BackendApi.get_model(model_mgr, HappeningMaster, mid, using=using)
    
    @staticmethod
    def get_playerhappening(model_mgr, uid, using=settings.DB_DEFAULT):
        """プレイヤーのハプニング情報を取得.
        """
        return BackendApi.get_model(model_mgr, PlayerHappening, uid, using=using)
    
    @staticmethod
    def get_happenings(model_mgr, idlist, using=settings.DB_DEFAULT):
        """ハプニングプレイ情報を取得.
        """
        happenings = BackendApi.get_model_dict(model_mgr, Happening, idlist, using=using)
        midlist = list(set([happening.mid for happening in happenings.values()]))
        masters = BackendApi.get_happeningmasters(model_mgr, midlist, using=using)
        return dict([(happening.id, HappeningSet(happening, masters.get(happening.mid))) for happening in happenings.values()])
    
    @staticmethod
    def get_happening(model_mgr, happeningid, using=settings.DB_DEFAULT):
        """ハプニングプレイ情報を取得.
        """
        return BackendApi.get_happenings(model_mgr, [happeningid], using=using).get(happeningid, None)
    
    @staticmethod
    def get_current_happeningid(model_mgr, uid, using=settings.DB_DEFAULT, reflesh=False):
        """現在のハプニングIDを取得.
        """
        if reflesh:
            playerhappening = PlayerHappening.getByKey(uid, using=using)
            if playerhappening:
                model_mgr.set_got_models([playerhappening])
        else:
            playerhappening = BackendApi.get_playerhappening(model_mgr, uid, using=using)
        if playerhappening is None:
            return 0
        return Happening.makeID(playerhappening.id, playerhappening.happening)
    
    @staticmethod
    def get_current_happening(model_mgr, uid, using=settings.DB_DEFAULT):
        """現在のハプニングを取得.
        """
        happeningid = BackendApi.get_current_happeningid(model_mgr, uid, using=using)
        if happeningid:
            return BackendApi.get_happening(model_mgr, happeningid, using=using)
        return None

    @staticmethod
    def get_happeningraidset_list(model_mgr, idlist, using=settings.DB_DEFAULT):
        """ハプニングプレイ情報を取得.
        レイドも一緒にとる.
        """
        happenings = BackendApi.get_happenings(model_mgr, idlist, using=using)
        raids = BackendApi.get_raids(model_mgr, happenings.keys(), using=using)
        result = [HappeningRaidSet(happenings[happeningid], raids.get(happeningid)) for happeningid in idlist if happenings.get(happeningid)]
        return result
    
    @staticmethod
    def get_happeningraidset(model_mgr, happeningid, using=settings.DB_DEFAULT):
        """ハプニングプレイ情報を取得.
        レイドも一緒にとる.
        """
        happening = BackendApi.get_happening(model_mgr, happeningid, using=using)
        if happening is None:
            return None
        raid = BackendApi.get_raid(model_mgr, happening.id, using=using, happening_eventvalue=happening.happening.event)
        return HappeningRaidSet(happening, raid)
    
    @staticmethod
    def get_raid_destroyrecord(model_mgr, uid, mid, get_instance=False, using=settings.DB_DEFAULT):
        """レイド毎の討伐回数レコードを取得.
        """
        return BackendApi.get_model(model_mgr, RaidDestroyCount, RaidDestroyCount.makeID(uid, mid), get_instance, using)
    
    @staticmethod
    def tr_reset_raid_destroyrecord(model_mgr):
        """レイド毎の討伐回数をリセット.
        """
        RaidDestroyCount.all().update(cnt=0)
        
        def writeEnd():
            OSAUtil.get_cache_client().flush()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def choice_raidlevel(raidmaster, playerlevel, destroyrecord=None):
        """レイドレベル選択.
        """
        if destroyrecord is None:
            return playerlevel
        cnt = destroyrecord.cnt
        return max(1, min(cnt + 1, raidmaster.max_level))
#        if 0 <= cnt < 2:
#            level_min = 10
#            level_max = 10
#        elif 2 <= cnt < 6:
#            level_min = 10
#            level_max = 30
#        elif 6 <= cnt < 11:
#            level_min = 20
#            level_max = 50
#        elif 11 <= cnt < 21:
#            level_min = 30
#            level_max = 70
#        elif 21 <= cnt < 51:
#            level_min = 50
#            level_max = 100
#        else:
#            level_min = 70
#            level_max = 100
#        return randint(level_min, level_max)
        
    
    @staticmethod
    def tr_create_happening(model_mgr, uid, mid, level, eventvalue=0, champagne=False):
        """ハプニング情報を作成.
        """
        master = BackendApi.get_happeningmaster(model_mgr, mid)
        if master is None:
            raise CabaretError(u'ハプニングマスターが存在しません.id=%d' % mid, CabaretError.Code.INVALID_MASTERDATA)
        raidmaster = BackendApi.get_raid_master(model_mgr, master.boss)
        if raidmaster is None:
            raise CabaretError(u'レイドマスターが存在しません.id=%d' % master.boss, CabaretError.Code.INVALID_MASTERDATA)
        
        if model_mgr.get_model(PlayerHappening, uid):
            playerhappening = model_mgr.get_model_forupdate(PlayerHappening, uid)
        else:
            playerhappening = PlayerHappening.makeInstance(uid)
            model_mgr.set_got_models_forupdate([playerhappening])
        
        destroyrecord = BackendApi.get_raid_destroyrecord(model_mgr, uid, master.boss, get_instance=True)
        
        playerhappening.happening += 1
        
        ins_id = Happening.makeID(playerhappening.id, playerhappening.happening)
        happening = Happening.makeInstance(ins_id)
        happening.oid = playerhappening.id
        happening.mid = mid
        happening.state = Defines.HappeningState.ACTIVE
        happening.etime = OSAUtil.get_now() + datetime.timedelta(seconds=master.timelimit)
        happening.progress = 0
        happening.gold = 0
        happening.items = {}
        happening.level = BackendApi.choice_raidlevel(raidmaster, level, destroyrecord)
        happening.hprate = randint(raidmaster.hprate_min, raidmaster.hprate_max)
        happening.event = eventvalue
        
        if master.execution < 1:
            # すぐにレイド発生.
            BackendApi.tr_create_raid(model_mgr, master, happening, champagne=champagne)
        else:
            model_mgr.set_save(happening)
        
        model_mgr.set_save(playerhappening)
        
        return happening

    @staticmethod
    def tr_create_producehappening(model_mgr, uid, mid, level, eventvalue=0, champagne=False):
        """ハプニング情報を作成.
        """
        master = BackendApi.get_happeningmaster(model_mgr, mid)
        if master is None:
            raise CabaretError(u'ハプニングマスターが存在しません.id=%d' % mid, CabaretError.Code.INVALID_MASTERDATA)
        raidmaster = BackendApi.get_raid_master(model_mgr, master.boss)
        if raidmaster is None:
            raise CabaretError(u'レイドマスターが存在しません.id=%d' % master.boss, CabaretError.Code.INVALID_MASTERDATA)

        if model_mgr.get_model(PlayerHappening, uid):
            playerhappening = model_mgr.get_model_forupdate(PlayerHappening, uid)
        else:
            playerhappening = PlayerHappening.makeInstance(uid)
            model_mgr.set_got_models_forupdate([playerhappening])

        playerhappening.happening += 1

        ins_id = ProduceEventHappening.makeID(playerhappening.id, playerhappening.happening)
        happening = ProduceEventHappening.makeInstance(ins_id)
        happening.oid = playerhappening.id
        happening.mid = mid
        happening.state = Defines.HappeningState.ACTIVE
        happening.progress = 0
        happening.gold = 0
        happening.items = {}
        happening.level = 0
        happening.hprate = randint(raidmaster.hprate_min, raidmaster.hprate_max)
        happening.event = eventvalue

        if master.execution < 1:
            # すぐにレイド発生.
            BackendApi.tr_create_raid(model_mgr, master, happening, champagne=champagne)
        else:
            model_mgr.set_save(happening)

        model_mgr.set_save(playerhappening)

        return happening

    @staticmethod
    def aggregate_happeningprize(happening, cancel=False):
        """ハプニング実行中に獲得したアイテムを集計.
        """
        return []
        # ハプニングでスカウトしないからこれはいらない.
#        prizelist = []
#        # お金.
#        gold = happening.gold
#        if cancel:
#            gold = int(gold / 2)
#        if 0 < gold:
#            prizelist.append(PrizeData.create(gold=gold))
#        
#        # アイテム.
#        for key, value in happening.items.items():
#            if value < 1:
#                continue
#            itype = key >> 32
#            mid = key & 0xffffffff
#            if itype == Defines.ItemType.ITEM:
#                prizelist.append(PrizeData.create(itemid=mid, itemnum=value))
#        return prizelist
    
    @staticmethod
    def tr_do_happening(model_mgr, player, master, key):
        """ハプニング実行.
        """
        # 重複チェック.
        BackendApi.tr_update_requestkey(model_mgr, player.id, key)
        
        playerhappening = PlayerHappening.getByKeyForUpdate(player.id)
        happening = Happening.getByKeyForUpdate(Happening.makeID(playerhappening.id, playerhappening.happening))
        
        if happening is None or happening.is_end() or happening.is_cleared():
            raise CabaretError(u'終了済み', CabaretError.Code.NOT_DATA)
        elif master.execution <= happening.progress:
            raise CabaretError(u'これ以上実行できない', CabaretError.Code.OVER_LIMIT)
        model_mgr.set_got_models_forupdate([playerhappening, happening])
        
        # 次のレベル.
        nextlevelexp = BackendApi.get_playerlevelexp_bylevel(player.level+1, model_mgr)
        
        # 称号.
        title_master = BackendApi.get_current_title_master(model_mgr, player.id, OSAUtil.get_now())
        
        # 実行オブジェクト.
        executer = ScoutExec(player, happening, playerhappening.happening_seed, master, nextlevelexp, title=title_master)
        
        # 消費行動力.
        apcost = BackendApi.get_apcost(master, player)
        
        # 終了するまで実行.
        while not executer.is_end:
            executer.execute(apcost)
        happening.progress = executer.progress
        
        # 結果を集計.
        prize = executer.aggregatePrizes()
        
        if prize.get('card', None):
            # 想定外のイベント.
            raise CabaretError(u'想定外のドロップアイテムが設定されています.HappeningMaster.id=%d' % master.id, CabaretError.Code.INVALID_MASTERDATA)
        elif prize.get('happening', None):
            # ハプニング. ここに来るときは絶対サーバ側が悪い.
            raise CabaretError(u'ハプニングでハプニングが発生しました.')
        
        # お金.
        gold = prize['gold']
        if 0 < gold:
            # クリア後の報酬に追記.
            happening.gold += gold
        
        # 経験値.
        exp = prize['exp']
        if 0 < exp:
            BackendApi.tr_add_exp(model_mgr, player, exp)
            level = player.level
            levelupevent = prize.get('levelup', None)
            if levelupevent:
                # 書き込み後のれべる.
                levelupevent.set_level(level)
        
        # アイテム.
        itemeevent = prize.get('item', None)
        if itemeevent:
            # アイテムを設定.
            happening.addDropItem(Defines.ItemType.ITEM, itemeevent.item)
        
        # ボス出現.
        completeevent = prize.get('complete', None)
        raidboss = None
        if completeevent:
            # レイド作成.
            raidboss = BackendApi.tr_create_raid(model_mgr, master, happening)
        
        # 行動力.
        # レベルが上がったら行動力は書き込まなくていい.
        if not executer.is_levelup:
            player.set_ap(executer.ap)
            model_mgr.set_save(player.getModel(PlayerAp))
        
        # プレイデータの書き込み.
        playerhappening.happening_seed = executer.rand._seed
        playerhappening.happening_result = {
            'result' : executer.result,
            'event' : executer.eventlist,
        }
        model_mgr.set_save(happening)
        model_mgr.set_save(playerhappening)
        
        def writeEnd():
            if raidboss:
                KpiOperator().set_incrment_raidappear_count(raidboss.master.id, raidboss.raid.level, raidboss.raid.ctime).save()
        model_mgr.add_write_end_method(writeEnd)
    
    #===========================================================
    # レイド.
    @staticmethod
    def get_raid_masters(model_mgr, midlist, using=settings.DB_DEFAULT):
        """レイドのマスターデータを取得.
        返すのはdict.
        """
        masterlist = model_mgr.get_models(RaidMaster, midlist, using=using)
        masters = {}
        for master in masterlist:
            masters[master.id] = master
        return masters
    
    @staticmethod
    def get_raid_master(model_mgr, mid, using=settings.DB_DEFAULT):
        """レイドのマスターデータを取得.
        """
        return BackendApi.get_raid_masters(model_mgr, [mid], using=using).get(mid, None)
    
    @staticmethod
    def get_raids(model_mgr, raididlist, using=settings.DB_DEFAULT, get_instance=False, happening_eventvalue=0):
        """レイドを取得.
        返すのはdict.
        """
        raids = BackendApi.get_model_dict(model_mgr, Raid, raididlist, using=using)
        midlist = list(set([raid.mid for raid in raids.values()]))
        masters = BackendApi.get_raid_masters(model_mgr, midlist, using=using)
        
        raideventid = HappeningUtil.get_raideventid(happening_eventvalue)
        scouteventid = HappeningUtil.get_scouteventid(happening_eventvalue)
        produceeventid = HappeningUtil.get_produceeventid(happening_eventvalue)
        
        if raideventid:
            eventraid_getter = lambda midlist: BackendApi.get_raidevent_raidmasters(model_mgr, raideventid, midlist, using=using)
        elif scouteventid:
            eventraid_getter = lambda midlist: BackendApi.get_scoutevent_raidmasters(model_mgr, scouteventid, midlist, using=using)
        elif produceeventid:
            eventraid_getter = lambda midlist : BackendApi.get_produceevent_raidmasters(model_mgr, produceeventid, midlist, using=using)
        else:
            eventraid_getter = lambda x:{}
        eventraidmasters = eventraid_getter(midlist)
        
        raiddict = dict([(raid.id, RaidBoss(raid, masters.get(raid.mid), eventraidmasters.get(raid.mid))) for raid in raids.values()])
        
        if get_instance:
            happeningidlist = list(set(raididlist) - set(raiddict.keys()))
            if happeningidlist:
                # プロデュースイベントのID、チェック
                if produceeventid:
                    # プロデュースイベントの場合
                    happenings = BackendApi.get_producehappenings(model_mgr, happeningidlist, using=using)
                else:
                    happenings = BackendApi.get_happenings(model_mgr, happeningidlist, using=using)
                midlist = list(set([happeningset.master.boss for happeningset in happenings.values()]))
                raidmasters = BackendApi.get_raid_masters(model_mgr, midlist, using=using)
                eventraidmasters = eventraid_getter(midlist)
                
                for happeningid, happeningset in happenings.items():
                    happening = happeningset.happening
                    raidmaster = raidmasters[happeningset.master.boss]
                    eventraidmaster = eventraidmasters.get(happeningset.master.boss)
                    
                    ins = Raid.makeInstance(happening.id)
                    ins.oid = happening.oid
                    ins.mid = raidmaster.id
                    ins.level = happening.level
                    ins.damage_record = {}
                    
                    raidboss = RaidBoss(ins, raidmaster, eventraidmaster)
                    ins.hprate = happening.hprate
                    ins.hp = raidboss.get_maxhp()
                    raiddict[happeningid] = raidboss
        return raiddict
    
    @staticmethod
    def get_raid(model_mgr, raidid, using=settings.DB_DEFAULT, get_instance=False, happening_eventvalue=0):
        """レイドを取得.
        """
        return BackendApi.get_raids(model_mgr, [raidid], using=using, get_instance=get_instance, happening_eventvalue=happening_eventvalue).get(raidid, None)
    
    @staticmethod
    def add_raidhelpid(raidhelp, pipe=None):
        """救援要請を追加.
        """
        RaidHelpSet.create(raidhelp.toid, raidhelp.id, raidhelp.etime).save(pipe)
    
    @staticmethod
    def remove_raidhelpid_list(raidhelplist, pipe=None):
        """救援要請を削除.
        """
        redisdb = None
        if pipe is None:
            redisdb = RaidHelpSet.getDB()
            pipe = redisdb.pipeline()
        for raidhelp in raidhelplist:
            RaidHelpSet.create(raidhelp.toid, raidhelp.id).delete(pipe)
        if redisdb:
            pipe.execute()
    
    @staticmethod
    def _save_raidhelpidlist(model_mgr, uid, using=settings.DB_DEFAULT):
        """救援要請を保存.
        """
        modellist = RaidHelp.fetchValues(filters={'toid':uid, 'etime__gt':OSAUtil.get_now()}, using=using)
        if not modellist:
            return
        
        model_mgr.set_got_models(modellist)
        
        redisdb = RedisModel.getDB()
        pipe = redisdb.pipeline()
        
        pipe.delete(RaidHelpSet.makeKey(uid))
        
        redismodellist = []
        for model in modellist:
            redismodel = RaidHelpSet.create(uid, model.id, model.etime)
            redismodel.save(pipe)
            redismodellist.append(redismodel)
        
        pipe.execute()
        
        return redismodellist
    
    @staticmethod
    def get_raidhelpidlist(model_mgr, uid, limit=None, offset=0, using=settings.DB_DEFAULT):
        """救援要請ID.
        """
        if not RaidHelpSet.exists(uid):
            BackendApi._save_raidhelpidlist(model_mgr, uid, using=settings.DB_DEFAULT)
        modellist = RaidHelpSet.fetch(uid, limit, offset)
        return [model.raidhelpid for model in modellist]
    
    @staticmethod
    def get_raidhelp_num(model_mgr, uid, using=settings.DB_DEFAULT, nummax=None):
        """救援要請数.
        """
        if RaidHelpSet.exists(uid):
            RaidHelpSet.refresh(uid)
        else:
            BackendApi._save_raidhelpidlist(model_mgr, uid, using=settings.DB_DEFAULT)
        num = RaidHelpSet.get_num(uid)
        if nummax is None:
            return num
        else:
            return min(num, Defines.RAIDHELP_LIST_MAXLENGTH)
    
    @staticmethod
    def get_raidhelplist(model_mgr, helpidlist, using=settings.DB_DEFAULT):
        """救援要請.
        """
        raidhelpdict = BackendApi.get_model_dict(model_mgr, RaidHelp, helpidlist, using=using)
        return [raidhelpdict[helpid] for helpid in helpidlist if raidhelpdict.get(helpid)]

    @staticmethod
    def get_raidevent_helpspecialbonusscore(raidid, uid, using=settings.DB_DEFAULT):
        specialup_list = RaidEventHelpSpecialBonusScore.fetchValues(filters={'raidid':raidid}, using=using)
        if specialup_list:
            specials = filter(lambda x: getattr(x, 'uid') == uid, specialup_list)
            if len(specials) == 1:
                return specials[0]
            else:
                return None

    @staticmethod
    def save_raidhelpcard(model_mgr, uid, raidid, cardset, using=settings.DB_DEFAULT):
        """レイドで呼ぶフレンドのカードを設定.
        """
        if not BackendApi.check_friend(uid, cardset.card.uid, arg_model_mgr=model_mgr, using=using):
            raise CabaretError(u'フレンドではありません', CabaretError.Code.ILLEGAL_ARGS)
        
        redisdb = RedisModel.getDB()
        pipe = redisdb.pipeline()
        RaidHelpFriendData.create(uid, raidid, cardset.card).save(pipe)
        pipe.execute()
    
    @staticmethod
    def delete_raidhelpcard(uid, pipe=None):
        """レイドで呼ぶフレンドのカードを外す(自動設定可能).
        """
        RaidHelpFriendData.create(uid).delete(pipe)
    
    @staticmethod
    def cancel_raidhelpcard(uid, raidid, pipe=None):
        """レイドで呼ぶフレンドのカードを外す(自動設定不可能).
        """
        redisdb = RedisModel.getDB()
        pipe = redisdb.pipeline()
        RaidHelpFriendData.create(uid, raidid).save(pipe)
        pipe.execute()
    
    @staticmethod
    def get_raidhelpcard(model_mgr, uid, raidid, using=settings.DB_DEFAULT):
        """レイドで呼ぶフレンドのカードを取得.
        """
        model = RaidHelpFriendData.get(uid)
        if model is None or model.raidid != raidid or model.card is None:
            return None
        
        master = BackendApi.get_cardmasters([model.card.mid], arg_model_mgr=model_mgr, using=using).get(model.card.mid, None)
        if master is None:
            return None
        return CardSet(model.card, master)
    
    @staticmethod
    def check_raidhelpcard_canceled(model_mgr, uid, raidid, using=settings.DB_DEFAULT):
        """レイドで呼ぶフレンドのカードをキャンセルしたか.
        """
        model = RaidHelpFriendData.get(uid)
        if model is None or model.raidid != raidid:
            return False
        return model.card is None
    
    @staticmethod
    def update_raid_callfriendtime(uid, pipe=None):
        """レイドでフレンドを呼んだ時間を更新.
        """
        RaidCallFriendTime.create(uid, OSAUtil.get_now()).save(pipe)
    
    @staticmethod
    def get_raid_callfriend_opentime(uid):
        """レイドでフレンドを呼べるようになる時間.
        """
        model = RaidCallFriendTime.get(uid)
        if model:
            now = OSAUtil.get_now()
            opentime = model.helptime + datetime.timedelta(seconds=Defines.RAIDHELP_TIME_INTERVAL)
            if now < opentime:
                return opentime
        return None
    
    @staticmethod
    def get_raid_callfriend_opentimedelta(uid):
        """レイドでフレンドを呼べるまでの時間(秒).
        """
        opentime = BackendApi.get_raid_callfriend_opentime(uid)
        seconds = 0
        if opentime:
            delta = opentime - OSAUtil.get_now()
            seconds = max(0, delta.days * 86400 + delta.seconds)
        return seconds
    
    @staticmethod
    def get_raid_battleresult(model_mgr, uid, using=settings.DB_DEFAULT):
        """レイドバトル結果を取得.
        """
        return model_mgr.get_model(RaidBattle, uid, using=using)
    
    @staticmethod
    def raid_is_can_callfriend(uid):
        """レイドでフレンドを呼んだ時間をチェック.
        """
        seconds = BackendApi.get_raid_callfriend_opentimedelta(uid)
        return seconds < 1
    
    @staticmethod
    def tr_create_raid(model_mgr, happeningmaster, happening, champagne=False):
        """レイドを作成.
        """
        if happening.progress < happeningmaster.execution or happening.state != Defines.HappeningState.ACTIVE:
            raise CabaretError(u'レイド発生条件を満たしていません')
        
        raidmaster = BackendApi.get_raid_master(model_mgr, happeningmaster.boss)
        
        ins = Raid.makeInstance(happening.id)
        ins.oid = happening.oid
        ins.mid = raidmaster.id
        ins.level = happening.level
        ins.damage_record = {}
        
        raidboss = RaidBoss(ins, raidmaster)
        ins.hprate = happening.hprate
        
        evpointrate = 100
        raidevent_id = HappeningUtil.get_raideventid(happening.event)
        if 0 < raidevent_id:
            now = OSAUtil.get_now()
            ins.timebonusflag = BackendApi.check_raidevent_timebonus(model_mgr, now=now)
            ins.fastflag = BackendApi.check_raidevent_fastbonus(model_mgr, now=now)
            eventraidmaster = BackendApi.get_raidevent_raidmaster(model_mgr, raidevent_id, ins.mid)
            raidboss.setEventRaidMaster(eventraidmaster)
            if eventraidmaster:
                evpointrate = random.randint(eventraidmaster.pointrandmin, eventraidmaster.pointrandmax)
            if champagne:
                # SHOWTIMEフラグを立てておく.
                raidboss.getDamageRecord(ins.oid).setChampagne(True)
                raidboss.refrectDamageRecord()
        ins.setEvpointrate(evpointrate)

        produceevent_id = HappeningUtil.get_produceeventid(happening.event)
        if 0 < produceevent_id:
            eventraidmaster = BackendApi.get_produceevent_raidmaster(model_mgr, produceevent_id, ins.mid)
            raidboss.setEventRaidMaster(eventraidmaster)
        
        ins.hp = raidboss.get_maxhp()
        
        happening.state = Defines.HappeningState.BOSS
        model_mgr.set_save(happening)
        
        model_mgr.set_save(ins)
        
        return raidboss
    
    @staticmethod
    def tr_send_raidhelp(model_mgr, uid, to_other=False):
        """レイドの救援依頼を送信.
        アクティブなフレンドから最低20人.
        足りない分はアクティブユーザーから.
        """
        # 重複チェック.
        playerhappening = PlayerHappening.getByKeyForUpdate(uid)
        raidid = Happening.makeID(uid, playerhappening.happening)
        happening = Happening.getByKeyForUpdate(raidid)
        raid = Raid.getByKeyForUpdate(raidid)
        
        if raid is None:
            raise CabaretError(u'存在しない', CabaretError.Code.ILLEGAL_ARGS)
        elif raid.helpflag:
            raise CabaretError(u'送信済みです', CabaretError.Code.ALREADY_RECEIVED)
        elif happening.is_end() or happening.is_cleared():
            raise CabaretError(u'終了していて送信できない', CabaretError.Code.OVER_LIMIT)
        model_mgr.set_got_models_forupdate([playerhappening, happening, raid])
        
        if to_other:
            # フレンドに送らない.
            arr = []
        else:
            # フレンドを優先.
            arr = BackendApi.get_friend_idlist(uid, arg_model_mgr=model_mgr)
        now = OSAUtil.get_now()
        bordertime = now - datetime.timedelta(days=Defines.ACTIVE_DAYS)
        if arr:
            friendloginlist = PlayerLogin.fetchValues(['id','ltime'], filters={'id__in':arr})
            friendloginlist.sort(key=lambda x:x.ltime, reverse=True)
            friendidlist = [friendlogin.id for friendlogin in friendloginlist if bordertime < friendlogin.ltime]
            if Defines.RAIDFRIEND_NUM_MAX < len(friendidlist):
#                random.shuffle(friendidlist)
                friendidlist = friendidlist[:Defines.RAIDFRIEND_NUM_MAX]
        else:
            friendidlist = []
        
        rest = Defines.RAIDFRIEND_NUM_MIN - len(friendidlist)
        if 0 < rest:
            ignorelist = [uid] + arr
            friendidlist.extend(LoginTimeSet.fetchRandom(rest, bordertime, now, ignorelist))
        
        
        raidboss = RaidBoss(raid, None)
        myrecord = raidboss.getDamageRecord(uid)
        if myrecord.damage_cnt < 1:
            raise CabaretError(u'不正な遷移です', CabaretError.Code.ILLEGAL_ARGS)
        
        targetlist = list(set(friendidlist) - set(raidboss.getDamageRecordUserIdList()))
        if not targetlist:
            raise CabaretError(u'相手が見つからない', CabaretError.Code.NOT_ENOUGH)
        
        raidhelplist = []
        for fid in targetlist:
            ins = RaidHelp()
            ins.fromid = uid
            ins.toid = fid
            ins.raidid = raidid
            ins.raidevent_specialbonusscore = 0
            ins.ctime = raid.ctime
            ins.etime = happening.etime
            model_mgr.set_save(ins)
            raidhelplist.append(ins)
            
            raidboss.addUser(fid)
        raidboss.refrectDamageRecord()
        
        raid.helpflag = True
        model_mgr.set_save(raid)
        
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            for raidhelp in raidhelplist:
                BackendApi.add_raidhelpid(raidhelp, pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def judge_raidprize_distribution_outside_userid(target_uid, viewer_uid, raid_oid, is_clear):
        """報酬配布を外部で行うユーザーなのかをチェック.
        """
        if (not Defines.RAID_PRIZE_DISTRIBUTION_OUTSIDE) or (not is_clear) or (target_uid == viewer_uid) or (target_uid == raid_oid):
            # 外部配布を行わない.
            # 失敗した時は外部配布を行わない.
            # 自分は外部配布を行わない.
            # 発見者は外部配布を行わない.
            return False
        else:
            return True
    
    @staticmethod
    def __tr_send_raidhelp_prize(model_mgr, viewer_uid, toid, happening, raidboss, is_clear, prizelist, demiworld, bonusscore):
        """
        """
        damage_cnt = 0
        if is_clear:
            record = raidboss.getDamageRecord(toid)
            damage_cnt = record.damage_cnt
            if 0 < damage_cnt:
                # 報酬配布.
                if prizelist:
                    auto_receive = viewer_uid == toid
                    BackendApi.tr_add_prize(model_mgr, toid, prizelist, Defines.TextMasterID.RAID_JOIN, auto_receive=auto_receive)
                # 秘宝配布.
                if 0 < demiworld:
                    prize_num = int(demiworld * (1 + bonusscore / 100.0))
                    BackendApi.tr_add_demiworld_treasure(model_mgr, toid, prize_num)
        # ログ作成.
        raidlog = RaidLog()
        raidlog.uid = toid
        raidlog.raidid = happening.id
        raidlog.ctime = happening.etime
        model_mgr.set_save(raidlog)
        
        return {
            'log' : raidlog,
            'damage_cnt' : damage_cnt,
        }
    
    @staticmethod
    def tr_send_raidhelp_prize(model_mgr, viewer_uid, happening, raidboss, is_clear=True):
        """レイドの救援依頼を報酬を渡す.
        """
        if is_clear:
            # イベントレイドでももらえるようにする.(hayashi@20140226)
            # イベントレイドは報酬をもらえない.
            prizelist = BackendApi.get_prizelist(model_mgr, raidboss.master.helpprizes)
            demiworld = raidboss.get_demiworld()
        else:
            prizelist = []
            demiworld = 0
        
        filters = {
            'raidid' : raidboss.id,
        }
        raidhelplist = RaidHelp.fetchValues(filters=filters)
        
        raidloglist = []
        attackmemberlist = []
        raidhelpset_dict = {}
        
        is_need_queue = False
        for raidhelp in raidhelplist:
            # 成功外部で配布
            if BackendApi.judge_raidprize_distribution_outside_userid(raidhelp.toid, viewer_uid, happening.oid, is_clear):
                # 成功した時に自分の以外は外部で配布.
                is_need_queue = True
            else:
                tmp = BackendApi.__tr_send_raidhelp_prize(model_mgr, viewer_uid, raidhelp.toid, happening, raidboss, is_clear, prizelist, demiworld, raidhelp.raidevent_specialbonusscore)
                raidloglist.append(tmp['log'])
                if 0 < tmp['damage_cnt']:
                    attackmemberlist.append(raidhelp.toid)
            
            # 削除予約.
            raidhelpset_dict[raidhelp.id] = RaidHelpSet.create(raidhelp.toid, raidhelp.id)
        # 救援依頼を削除.
        RaidHelp.all().filter(**filters).delete()
        
        if is_need_queue:
            # 外部配布用のキューを積む.
            queue = RaidPrizeDistributeQueue()
            queue.uid = viewer_uid
            queue.raidid = happening.id
            model_mgr.set_save(queue)
        
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            
            # 一覧に並ぶ救援依頼を削除.
            for raidhelpset in raidhelpset_dict.values():
                raidhelpset.delete(pipe)
            
            # ログの保存.
            for raidlog in raidloglist:
                BackendApi.add_raidlogid(raidlog, pipe)
                if raidlog.uid in attackmemberlist:
                    # 攻撃した人には通知を送る.
                    BackendApi.add_raidlog_notificationid(viewer_uid, raidboss, raidlog, pipe)
            
            pipe.execute()
            
            # 救援依頼のモデルのキャッシュを削除.一日待てば消えるけど一応消しておく.
            model_mgr.delete_models_from_cache(RaidHelp, raidhelpset_dict.keys())
        
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def check_raid_joinable(model_mgr, raidboss, uid, using=settings.DB_DEFAULT):
        """救援参加可能かを確認.
        """
        raid = raidboss.raid
        # 参加できるかを確認.
        damage_record = raid.getDamageRecord()
        if damage_record.has_key(uid):
            # 一度攻撃したことがある.
            pass
        elif raid.oid == uid:
            # 発見者.
            pass
        else:
            raidhelp = RaidHelp.getValues(['id'], filters={'toid':uid, 'raidid':raidboss.id}, using=settings.DB_READONLY)
            if raidhelp is None:
                return False
        return True
    
    @staticmethod
    def tr_raidbattle(model_mgr, raidid, key, player, raidmaster, deckcardlist, friendcard, is_strong, is_pc=False, champagne=False, addloginfo=None, score=0, raidhelp=None, is_produceevent=False):
        """レイドバトル書き込み.
        """
        if addloginfo is None:
            addloginfo = lambda x:None
        addloginfo('tr_raidbattle start')
        
        now = OSAUtil.get_now()
        uid = player.id
        
        # 重複チェック.
        BackendApi.tr_update_requestkey(model_mgr, uid, key)
        addloginfo('tr_update_requestkey')
        
        raid = Raid.getByKeyForUpdate(raidid)
        if raid is None:
            raise CabaretError(u'存在しない', CabaretError.Code.ILLEGAL_ARGS)
        model_mgr.set_got_models_forupdate([raid])
        addloginfo('get raid')
        
        raidboss = RaidBoss(raid, raidmaster)
        
        # 参加できるかを確認.
        if not BackendApi.check_raid_joinable(model_mgr, raidboss, uid):
            raise CabaretError(u'このレイドには参加できません', CabaretError.Code.OVER_LIMIT)
        addloginfo('check_raid_joinable')
        
        if is_produceevent:
            happening = ProduceEventHappening.getByKeyForUpdate(raidid)
        else:
            happening = Happening.getByKeyForUpdate(raidid)
        if happening.is_end() or happening.is_cleared():
            # これは参加確認が終わってからのほうが自然.
            raise CabaretError(u'これ以上攻撃できない', CabaretError.Code.OVER_LIMIT)
        model_mgr.set_got_models_forupdate([happening])
        addloginfo('get happening')
        
        # イベント確認.
        BackendApi.reset_raidboss_eventraidmaster(model_mgr, raidboss, happening.event)
        specialcard = None

        if raidboss.raideventraidmaster:
            specialcard = dict(raidboss.raideventraidmaster.specialcard)
            if uid == happening.oid:
                # 特攻ボーナス獲得UP.
                specialup = RaidEventSpecialBonusScore.getByKeyForUpdate(uid)
                if specialup is None:
                    specialup = RaidEventSpecialBonusScore.makeInstance(uid, score)
                else:
                    specialup.bonusscore = score
                model_mgr.set_save(specialup)
            else:##もし救援者なら
                helpspecialbonusscore = BackendApi.get_raidevent_helpspecialbonusscore(raidid, uid, using=settings.DB_DEFAULT)

                if helpspecialbonusscore is None:
                    helpspecialbonusscore = RaidEventHelpSpecialBonusScore.makeInstance(raidid, uid, score)
                helpspecialbonusscore.bonusscore = score
                model_mgr.set_save(helpspecialbonusscore)

        addloginfo('reset_raidboss_eventraidmaster')
        
        damagerecord = raidboss.getDamageRecord(uid)
        # SHOWTIMEフラグを立てる.
        damagerecord.setChampagne(champagne and (raidboss.raideventraidmaster or raidboss.scouteventraidmaster))
        if is_produceevent:
            # just incase the planners forgot to set the bpcost to 0 in master data
            bpcost = 0
            powuprate = Defines.RAIDATTACK_RATE_NORMAL
        else:
            bpcost_first = raidmaster.bpcost_first if raid.oid == uid else raidmaster.bpcost_first_other
            if 0 <= bpcost_first and damagerecord.damage_cnt == 0:
                powuprate = Defines.RAIDATTACK_RATE_NORMAL
                bpcost = bpcost_first
            elif is_strong:
                powuprate = Defines.RAIDATTACK_RATE_STRONG
                bpcost = raidmaster.bpcost_strong
            else:
                powuprate = Defines.RAIDATTACK_RATE_NORMAL
                bpcost = raidmaster.bpcost
        addloginfo('damage record')
        
        eventmaster = None
        flag_fever = False
        raidevent_id = HappeningUtil.get_raideventid(happening.event)
        title_raidevent_power_up = 0
        if raidevent_id:
            eventmaster = BackendApi.get_raideventmaster(model_mgr, raidevent_id)
            if eventmaster:
                # コンボボーナス.
                combobonus_rate, combobonus_limittime = BackendApi.get_raidevent_combobonus_powuprate(model_mgr, eventmaster, raidboss, now=now, with_limittime=True)
                powuprate = powuprate * (combobonus_rate + 100) / 100
                
                # コンボ加算.
                raidboss.addComboCount(uid, combobonus_limittime, now=now)
                
                # フィーバーチャンス.
                record = raidboss.getDamageRecord(uid)
                if record.is_fever():
                    powuprate = powuprate * (eventmaster.feverchancepowup + 100) / 100
                    flag_fever = True
                
                # 接客力の称号効果.
                title_raidevent_power_up = BackendApi.reflect_title_effect_percent(model_mgr, 0, uid, 'raidevent_power_up', now)
        addloginfo('fever')
        
        # 行動力消費.
        if 0 < bpcost:
            BackendApi.tr_add_bp(model_mgr, player, -bpcost)
        addloginfo('ap')

        # 強攻撃(超接客)か否か
        if is_produceevent:
            cur_eventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=settings.DB_READONLY)
            specialcard = [[a[0], a[1]*100] for a in cur_eventmaster.specialcard]
            specialcard = dict(specialcard)
            if is_strong:
                BackendApi.tr_add_item(model_mgr, uid, cur_eventmaster.useitem, -1)
        
        # 結果を求める.
        cardlist = deckcardlist[:]
        bosshp, animdata = BackendApi.bossbattle(cardlist, raidboss, powuprate, specialcard, friendcard, title_power_up=title_raidevent_power_up)
        eventraidmaster = raidboss.produceeventraidmaster

        damage = raid.hp - bosshp
        if not settings_sub.IS_BENCH:
            raid.hp = bosshp
        
        feverendtime = None
        if eventmaster and not flag_fever and is_strong and 0 < eventmaster.feverchancetime and 0 < eventmaster.feverchancepowup:
            # フィーバー開始.
            feverendtime = now + datetime.timedelta(seconds=eventmaster.feverchancetime)
        addloginfo('battle')
        
        # ダメージのレコード.
        raidboss.addDamageRecord(uid, damage, feverendtime)
        
        raidhelpset_list = []
        if bosshp < 1:
            if not is_produceevent:
                happening.etime = now

            # 撃破.
            # 救援分の報酬.
            BackendApi.tr_send_raidhelp_prize(model_mgr, uid, happening, raidboss, is_clear=True)
            addloginfo('tr_send_raidhelp_prize')
            
            # イベント報酬.
            raidevent_id = HappeningUtil.get_raideventid(happening.event)
            BackendApi.tr_raidevent_raiddestroy(model_mgr, uid, raidboss, raidevent_id, outside=False, bonusscore=score)
            addloginfo('tr_raidevent_raiddestroy')

            scoutevent_id = HappeningUtil.get_scouteventid(happening.event)
            BackendApi.tr_scoutevent_raiddestroy(model_mgr, uid, raidboss, scoutevent_id, outside=False)
            addloginfo('tr_scoutevent_raiddestroy')
            
            if is_produceevent:
                produceevent_id = HappeningUtil.get_produceeventid(happening.event)
                BackendApi.tr_produceevent_raiddestroy(model_mgr, uid, raidboss, produceevent_id, animdata, eventraidmaster.big, is_great_success=is_strong)
                addloginfo('tr_produceevent_raiddestroy')
            
            # ハプニングをクリア状態に.
            happening.state = Defines.HappeningState.CLEAR
            model_mgr.set_save(happening)
            addloginfo('save happening')
            
#            if happening.oid == uid or is_pc:
#                # 発見者の場合は報酬もわたしてしまう.
#                BackendApi.tr_happening_end(model_mgr, happening, raidboss)
            # フレンドに結果を見せる仕様が来たら↑にする. <=勝利画面にスカウトに戻るがついたので微妙になった.やるなら他の方法を探すべき.
            BackendApi.tr_happening_end(model_mgr, happening, raidboss, viewer_uid=uid, addloginfo=addloginfo, bonusscore=score)
            addloginfo('tr_happening_end')

        # ダメージ履歴を反映.
        raidboss.refrectDamageRecord()
        model_mgr.set_save(raid)
        addloginfo('save raid')
        
        # 結果.
        def forUpdate(raidbattle, inserted):
            raidbattle.raidid = raidid
            raidbattle.process = animdata
            raidbattle.is_strong = is_strong
            if friendcard:
                raidbattle.setHelpCard(friendcard)
            else:
                raidbattle.helpcard = 0
        model_mgr.add_forupdate_task(RaidBattle, uid, forUpdate)
        
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            
            if friendcard:
                # フレンドを呼んだ時間を更新.
                BackendApi.update_raid_callfriendtime(uid, pipe)
                # 呼んだフレンドをリセット.
                BackendApi.delete_raidhelpcard(uid, pipe)
            
            # 救援要請を消すなら消す.
            for raidhelpset in raidhelpset_list:
                raidhelpset.delete(pipe)
            pipe.execute()
            
            ope = KpiOperator()
            if bosshp < 1:
                ope.set_incrment_raiddestroy_count(raidboss.master.id, raidboss.raid.level, raidboss.raid.ctime)
            if raidboss.raideventraidmaster:
                ope.set_save_raidevent_play(uid, now, is_pc)
            ope.save()
            
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def tr_happening_missed(model_mgr, happeningid, force=False):
        """ハプニング失敗.
        """
        happening = model_mgr.get_model_forupdate(Happening, happeningid)
        if happening is None:
            raise CabaretError(u'ハプニングが見つかりません', CabaretError.Code.NOT_DATA)
        elif happening.state == Defines.HappeningState.MISS:
            raise CabaretError(u'処理済み', CabaretError.Code.ALREADY_RECEIVED)
        elif not force and not happening.is_missed():
            raise CabaretError(u'不正な書き込みです', CabaretError.Code.ILLEGAL_ARGS)
        
        happening.state = Defines.HappeningState.MISS
        model_mgr.set_save(happening)
        
        raidboss = BackendApi.get_raid(model_mgr, happening.id, using=settings.DB_READONLY)
        
        if raidboss:
            # 救援の処理.
            BackendApi.tr_send_raidhelp_prize(model_mgr, happening.oid, happening, raidboss, is_clear=False)
        
        # ログ作成.レイドが発生していなくても作成する.
        raidlog = RaidLog()
        raidlog.uid = happening.oid
        raidlog.raidid = happening.id
        raidlog.ctime = happening.ctime
        model_mgr.set_save(raidlog)
        
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            # ログの保存.
            BackendApi.add_raidlogid(raidlog, pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def tr_happening_cancel(model_mgr, player, happeningmaster):
        """ハプニング諦める書き込み.
        """
        # クリアフラグ書き込み.
        happeningid = BackendApi.get_current_happeningid(model_mgr, player.id)
        happening = model_mgr.get_model_forupdate(Happening, happeningid)
        
        if happening.is_canceled():
            raise CabaretError(u'書き込み済み', CabaretError.Code.ALREADY_RECEIVED)
        elif not happening.can_cancel():
            raise CabaretError(u'キャンセルじゃないけど終了している', CabaretError.Code.OVER_LIMIT)
        happening.state = Defines.HappeningState.CANCEL
        model_mgr.set_save(happening)
        
        raidboss = BackendApi.get_raid(model_mgr, happeningid)
        if raidboss:
            if raidboss.is_help_sent():
                raise CabaretError(u'救援依頼を送ったので諦められません', CabaretError.Code.ILLEGAL_ARGS)
            # 救援依頼を削除.
            BackendApi.tr_send_raidhelp_prize(model_mgr, happening.oid, happening, raidboss, is_clear=False)
        
        # ログ作成.
        raidlog = RaidLog()
        raidlog.uid = happening.oid
        raidlog.raidid = happening.id
        raidlog.ctime = happening.ctime
        model_mgr.set_save(raidlog)
        
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            # ログの保存.
            BackendApi.add_raidlogid(raidlog, pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
        
        # ハプニング中に集めたアイテム.
        prizelist = BackendApi.aggregate_happeningprize(happening, cancel=True)
        if prizelist:
            BackendApi.tr_add_prize(model_mgr, player.id, prizelist, Defines.TextMasterID.HAPPENING_DROP)
    
    @staticmethod
    def tr_send_happening_prize(model_mgr, happening, raidboss, viewer_uid):
        """ハプニングの報酬配布(発見者分)
        """
        def choice_item(items):
            rate_total = sum([item.get('rate', 0) for item in items])
            v = AppRandom().getIntN(rate_total)
            for item in items:
                rate = item.get('rate', 0)
                v -= rate
                if 0 < rate and v <= 0:
                    return item['id']

        auto_receive = viewer_uid == happening.oid
        
        # ハプニング中に集めたアイテム.
        prizelist = BackendApi.aggregate_happeningprize(happening, cancel=False)
        if prizelist:
            BackendApi.tr_add_prize(model_mgr, happening.oid, prizelist, Defines.TextMasterID.HAPPENING_DROP, auto_receive=auto_receive)
        
        # レイドの報酬配布.
        # イベントでも配付するように修正(hayashi@20140226).
        # イベント中は配布しない.
        prizelist = BackendApi.get_prizelist(model_mgr, raidboss.master.prizes)
        if prizelist:
            BackendApi.tr_add_prize(model_mgr, happening.oid, prizelist, Defines.TextMasterID.RAID_CLEAR, auto_receive=auto_receive)
        
        # レイド毎のランダムアイテム
        if hasattr(raidboss.master,"items"):
            items = raidboss.master.items
            if items:
                prize_id = choice_item(items)
                prizelist = model_mgr.get_models(PrizeMaster, [prize_id])
                if prizelist:
                    BackendApi.tr_add_prize(model_mgr, happening.oid, prizelist, Defines.TextMasterID.RAID_CLEAR, auto_receive=auto_receive)
                    happening.items['dropitems'] = prizelist

        # 秘宝配布.
        cabaretking = raidboss.get_cabaretking()
        if 0 < cabaretking:
            BackendApi.tr_add_cabaretking_treasure(model_mgr, happening.oid, cabaretking)
        
    @staticmethod
    def tr_happening_end(model_mgr, happening, raidboss, viewer_uid=None, addloginfo=None, bonusscore=0):
        """ハプニング終了.
        """
        if addloginfo is None:
            addloginfo = lambda x:None
        
        if happening.state == Defines.HappeningState.END:
            raise CabaretError(u'配布済み', CabaretError.Code.ALREADY_RECEIVED)
        elif happening.state != Defines.HappeningState.CLEAR:
            raise CabaretError(u'接客出来ていない', CabaretError.Code.ILLEGAL_ARGS)
        
        addloginfo('tr_happening_end')

        # 発見者分の報酬.
        BackendApi.tr_send_happening_prize(model_mgr, happening, raidboss, viewer_uid)
        addloginfo('send prize')

        # レイド発見者特攻ボーナス獲得UP終了処理.
        #bonusscore_obj = BackendApi.get_model(model_mgr, RaidEventSpecialBonusScore, viewer_uid)
        if raidboss.raideventraidmaster:
            owner_score = RaidEventSpecialBonusScore.getByKey(happening.oid)
            if isinstance(owner_score, RaidEventSpecialBonusScore):
                bonusscorelog = RaidEventSpecialBonusScoreLog.makeInstance(happening.id, owner_score.bonusscore)
                model_mgr.set_save(bonusscorelog)

                def forUpdateBonusScore(model, inserted):
                    model.last_happening_score = model.bonusscore
                    model.bonusscore = 0
                model_mgr.add_forupdate_task(RaidEventSpecialBonusScore, happening.oid, forUpdateBonusScore)

        # ログ作成.
        raidlog = RaidLog()
        raidlog.uid = happening.oid
        raidlog.raidid = happening.id
        raidlog.ctime = happening.ctime
        model_mgr.set_save(raidlog)
        
        # 討伐回数加算.
        def forUpdate(model, inserted):
            model.cnt += 1
            model.total += 1
        model_mgr.add_forupdate_task(RaidDestroyCount, RaidDestroyCount.makeID(happening.oid, raidboss.master.id), forUpdate)
        addloginfo('RaidDestroyCount')
        
        # ミッション.
        mission_executer = PanelMissionConditionExecuter()
        mission_executer.addTargetRaidWin(raidboss.raid.level)
        BackendApi.tr_complete_panelmission(model_mgr, happening.oid, mission_executer)
        addloginfo('mission')
        
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            # ログの保存.
            BackendApi.add_raidlogid(raidlog, pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
        
        happening.state = Defines.HappeningState.END
        model_mgr.set_save(happening)
    
    @staticmethod
    def add_raidlogid(logdata, pipe=None):
        """レイド履歴追加.
        """
        RaidLogListSet.create(logdata.uid, logdata.id, logdata.ctime).save(pipe)
    
    @staticmethod
    def get_raidlog_num(model_mgr, uid, using=settings.DB_DEFAULT):
        """レイド履歴を取得.
        """
        return BackendApi._get_log_num(RaidLogListSet, 'uid', 'ctime', uid, model_mgr, using=using)
    
    @staticmethod
    def add_raidlog_notificationid(viewer_uid, raidboss, logdata, pipe=None):
        """レイド終了通知追加.
        """
        if logdata.uid in [viewer_uid, raidboss.raid.oid]:
            # 発見者とこれを書き込む人は除く.
            return
        RaidLogNotificationSet.create(logdata.uid, logdata.id, logdata.ctime).save(pipe)
    
    @staticmethod
    def refresh_raidlog_notification(model_mgr, uid, using=settings.DB_READONLY):
        """レイド終了通知のゴミを無くして更新.
        """
        num = min(100, RaidLogNotificationSet.get_num(uid))
        if num < 1:
            return
        
        redisdb = RaidLogNotificationSet.getDB()
        pipe = redisdb.pipeline()
        
        arr = RaidLogNotificationSet.fetch(uid, limit=num)
        
        raidlogidlist = []
        for raidlogid in arr:
            if isinstance(raidlogid, (int, long)):
                raidlogidlist.append(raidlogid)
            else:
                RaidLogNotificationSet.create(uid, raidlogid).delete(pipe)
        
        dic = BackendApi.get_model_dict(model_mgr, RaidLog, raidlogidlist, using=using)
        notfoundlist = list(set(raidlogidlist) - set(dic.keys()))
        for notfoundid in notfoundlist:
            RaidLogNotificationSet.create(uid, notfoundid).delete(pipe)
        
        pipe.execute()
    
    @staticmethod
    def delete_raidlog_notificationid(uid, raidlogid=None, pipe=None):
        """レイド終了通知削除.
        """
        if raidlogid:
            RaidLogNotificationSet.create(uid, raidlogid).delete(pipe)
        else:
            if pipe is None:
                pipe = RaidLogNotificationSet.getDB()
            pipe.delete(RaidLogNotificationSet.makeKey(uid))
    
    @staticmethod
    def get_raidlog_notification_num(uid):
        """レイド終了通知数を取得.
        """
        return RaidLogNotificationSet.get_num(uid)
    
    @staticmethod
    def get_raidlog_idlist(model_mgr, uid, offset=0, limit=-1, using=settings.DB_DEFAULT):
        """レイド履歴のIDを取得.
        """
        if limit == 0:
            return []
        # 行動履歴IDを取得.
        idlist = BackendApi._get_log_idlist(RaidLogListSet, 'uid', 'ctime', uid, offset, limit, model_mgr, using)
        return idlist
    
    @staticmethod
    def get_raidlogs(model_mgr, raidlogidlist, using=settings.DB_DEFAULT):
        """レイド履歴を取得.
        """
        return BackendApi.get_model_dict(model_mgr, RaidLog, raidlogidlist, using=using)
    
    @staticmethod
    def save_raidlog_idlist(model_mgr, uid, using=settings.DB_DEFAULT):
        BackendApi._save_log_idlist(RaidLogListSet, 'uid', 'ctime', uid, model_mgr, 100, using)
    
    @staticmethod
    def put_list_raidlog_obj(handler, raidloglist):
        """一覧用のレイド履歴オブジェクトを作成.
        """
        model_mgr = handler.getModelMgr()
        
        # 時間でソート.
        arr = raidloglist[:]
        arr.sort(key=operator.attrgetter('ctime'), reverse=True)
        
        raididlist = [raidlog.raidid for raidlog in arr]
        raiddict = BackendApi.get_raids(model_mgr, raididlist, using=settings.DB_READONLY, get_instance=True)
        
        # 必要なプレイヤー情報.
        player_dict = {}
        for raidid in raididlist:
            raidboss = raiddict[raidid]
            if raidboss.raid.hp == 0:
                # 倒した.
                lastrecord = raidboss.getLastDamageRecord()
                player_dict[lastrecord.uid] = None
            player_dict[raidboss.raid.oid] = None
        
        playerlist = BackendApi.get_players(handler, player_dict.keys(), [], using=settings.DB_READONLY)
        for player in playerlist:
            player_dict[player.id] = player
        people = BackendApi.get_dmmplayers(handler, playerlist, using=settings.DB_READONLY, do_execute=False)
        
        # リーダー.
        leaders = BackendApi.get_leaders(player_dict.keys(), arg_model_mgr=model_mgr, using=settings.DB_READONLY)
        
        obj_raidloglist = []
        handler.html_param['raidloglist'] = obj_raidloglist
        
        def executeEnd():
            for raidlog in arr:
                raidboss = raiddict[raidlog.raidid]
                if not player_dict.get(raidboss.raid.oid):
                    continue
                obj_raidloglist.append(Objects.raidlog(handler, raidlog, raidboss, player_dict, people, leaders))
            obj_raidloglist.sort(key=lambda x:x['log_ctime'], reverse=True)
        
        return executeEnd
    
    @staticmethod
    def get_raidlog_by_raidid(model_mgr, uid, raidid, using=settings.DB_DEFAULT):
        """レイド履歴のIDを取得.
        """
        client = OSAUtil.get_cache_client()
        key = 'get_raidlog_by_raidid:%s:%s' % (uid, raidid)
        modelid = client.get(key)
        if modelid is None:
            model = RaidLog.getValues(filters={'uid':uid, 'raidid':raidid}, using=using)
            client.set(key, model.id if model else 0)
        elif 0 < modelid:
            model = BackendApi.get_model(model_mgr, RaidLog, modelid, using=using)
        else:
            model = None
        return model
    
    @staticmethod
    def tr_delete_happening(model_mgr, happeningid):
        """ハプニングを削除.
        """
        happening = Happening.getByKeyForUpdate(happeningid)
        raid = None
        
        redismodellist = []
        if happening is None or happening.is_active():
            # 消せない.
            return False
        elif happening.is_cleared():
            # 報酬未受取.
            raid = Raid.getByKeyForUpdate(happeningid)
            raidmaster = BackendApi.get_raid_masters(model_mgr, [raid.mid]).get(raid.mid)
            BackendApi.tr_send_happening_prize(model_mgr, happening, RaidBoss(raid, raidmaster))
        else:
            # 全て完了済み.
            raid = Raid.getByKey(happeningid)
        model_mgr.set_delete(happening)
        
        if raid:
            # レイド発生済み.
            for raidlog in RaidLog.fetchValues(filters={'raidid':happeningid}):
                redismodellist.append(RaidLogListSet.create(raidlog.uid, raidlog.id))
            for raidhelp in RaidHelp.fetchValues(filters={'raidid':happeningid}):
                redismodellist.append(RaidHelpSet.create(raidhelp.toid, raidhelp.id))
        
        if redismodellist:
            def writeEnd():
                try:
                    redisdb = RedisModel.getDB()
                    pipe = redisdb.pipeline()
                    for redismodel in redismodellist:
                        redismodel.delete(pipe)
                    pipe.execute()
                except Exception, err:
                    DbgLogger.write_error('happening delete error:id=%d(%s)' % (happeningid, err))
            model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def tr_distribute_raid(model_mgr, queue, happening, raidboss, help_prizelist):
        """レイドの報酬を配布する.
        """
        uid = queue.uid
        raid_oid = raidboss.raid.oid
        is_clear = raidboss.raid.hp < 1
        
        # 救援者の報酬.
        demiworld = raidboss.get_demiworld()

        if raidboss.raideventraidmaster:
            bonusscore = 0
            bonusscore_obj = BackendApi.get_raidevent_helpspecialbonusscore(raidboss.raid.id, uid, using=settings.DB_DEFAULT)
            if isinstance(bonusscore_obj, RaidEventHelpSpecialBonusScore):
                bonusscore = bonusscore_obj.bonusscore

        # 救援者の報酬.
        raidloglist = []
        attackmemberlist = []
        for toid in raidboss.getDamageRecordUserIdList():
            if BackendApi.judge_raidprize_distribution_outside_userid(toid, uid, raid_oid, is_clear):
                # 外部で配布する人だけ.

                tmp = BackendApi.__tr_send_raidhelp_prize(model_mgr, uid, toid, happening, raidboss, is_clear, help_prizelist, demiworld, 0)
                raidloglist.append(tmp['log'])
                if 0 < tmp['damage_cnt']:
                    attackmemberlist.append(toid)

        # イベント報酬.
        raidevent_id = HappeningUtil.get_raideventid(happening.event)
        BackendApi.tr_raidevent_raiddestroy(model_mgr, uid, raidboss, raidevent_id, outside=True)
        
        scoutevent_id = HappeningUtil.get_scouteventid(happening.event)
        BackendApi.tr_scoutevent_raiddestroy(model_mgr, uid, raidboss, scoutevent_id, outside=True)
        
        model_mgr.set_delete(queue)
        
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            
            # ログの保存.
            for raidlog in raidloglist:
                BackendApi.add_raidlogid(raidlog, pipe)
                if raidlog.uid in attackmemberlist:
                    # 攻撃した人には通知を送る.
                    BackendApi.add_raidlog_notificationid(uid, raidboss, raidlog, pipe)
            pipe.execute()
        
        model_mgr.add_write_end_method(writeEnd)
    
    #===========================================================
    # 報酬.
    @staticmethod
    def get_prizemaster_list(model_mgr, prizeidlist, using=settings.DB_DEFAULT):
        """報酬マスターを取得.
        """
        return model_mgr.get_models(PrizeMaster, prizeidlist, using=using)
    
    @staticmethod
    def get_prizelist(model_mgr, prizeidlist, using=settings.DB_DEFAULT):
        """報酬情報を取得.
        """
        prizemasterlist = BackendApi.get_prizemaster_list(model_mgr, prizeidlist, using)
        prizemasterdict = {}
        for prizemaster in prizemasterlist:
            prizemasterdict[prizemaster.id] = prizemaster
        return [PrizeData.createByMaster(prizemasterdict[prizeid]) for prizeid in prizeidlist]
    
    @staticmethod
    def tr_add_prize(model_mgr, uid, prizelist, textid, auto_receive=False):
        """ユーザーに報酬を渡す.
        """
        presentlist = BackendApi.create_present_by_prize(model_mgr, uid, prizelist, textid, auto_receive=auto_receive)
        
        # 書き込み後の処理.
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            for present in presentlist:
                BackendApi.add_present(uid, present, pipe=pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def make_prizeinfo(handler, prizelist, using=settings.DB_DEFAULT):
        """出力用の報酬オブジェクトを作成.
        """
        model_mgr = handler.getModelMgr()
        gold = 0
        gachapt = 0
        rareoverticket = 0
        ticket = 0
        memoriesticket = 0
        gachaticket = 0
        goldkey = 0
        silverkey = 0
        cabaretking = 0
        demiworld = 0
        cabaclub_money = 0
        items = {}
        cards = {}
        event_tickets = {}
        additional_tickets = {}
        tanzaku_nums = {}
        platinum_piece_num = 0
        crystal_piece_num = 0

        for prize in prizelist:
            gold += prize.gold
            gachapt += prize.gachapt
            rareoverticket += prize.rareoverticket
            ticket += prize.ticket
            memoriesticket += prize.memoriesticket
            gachaticket += prize.gachaticket
            goldkey += prize.goldkey
            silverkey += prize.silverkey
            cabaretking += prize.cabaretking
            demiworld += prize.demiworld
            cabaclub_money += prize.cabaclub_money
            platinum_piece_num += prize.platinum_piece_num
            crystal_piece_num += prize.crystal_piece_num
            if 0 < prize.itemid and 0 < prize.itemnum:
                items[prize.itemid] = items.get(prize.itemid, 0) + prize.itemnum
            if 0 < prize.cardid and 0 < prize.cardnum:
                cards[prize.cardid] = cards.get(prize.cardid, 0) + prize.cardnum
            if 0 < prize.eventticket_id and 0 < prize.eventticket_num:
                event_tickets[prize.eventticket_id] = event_tickets.get(prize.eventticket_id, 0) + prize.eventticket_num
            if 0 < prize.additional_ticket_id and 0 < prize.additional_ticket_num:
                additional_tickets[prize.additional_ticket_id] = additional_tickets.get(prize.additional_ticket_id, 0) + prize.additional_ticket_num
            if 0 < prize.tanzaku_num:
                tanzaku_nums[prize.tanzaku_number] = tanzaku_nums.get(prize.tanzaku_number, 0) + prize.tanzaku_num
        
        itemmasterlist = BackendApi.get_itemmaster_list(model_mgr, items.keys(), using=using)
        cardmasters = BackendApi.get_cardmasters(cards.keys(), model_mgr, using=using)
        eventmasters = BackendApi.get_raideventmaster_list(model_mgr, event_tickets.keys(), using=using)
        tanzakumaster_list = []
        if tanzaku_nums:
            config = BackendApi.get_current_scouteventconfig(model_mgr, using=using)
            tanzakumaster_list = BackendApi.get_scoutevent_tanzakumaster_list(model_mgr, config.mid, tanzaku_nums.keys(), using=using)
        
        itemlist = [Objects.item(handler, itemmaster, items[itemmaster.id]) for itemmaster in itemmasterlist]
        cardlist = [{'master':Objects.cardmaster(handler, cardmaster), 'num':cards[mid]} for mid, cardmaster in cardmasters.items()]
        eventticket_list = [{'master':Objects.raidevent(handler, eventmaster, None), 'num':event_tickets[eventmaster.id]} for eventmaster in eventmasters]
        tanzaku_list = [{'master':Objects.scoutevent_tanzaku(handler, tanzakumaster), 'num':tanzaku_nums[tanzakumaster.number]} for tanzakumaster in tanzakumaster_list]
        
        return Objects.prize(handler, gold, gachapt, itemlist, cardlist, rareoverticket, ticket, memoriesticket, gachaticket, goldkey, silverkey, cabaretking, demiworld, eventticket_list, additional_tickets, tanzaku_list, cabaclub_money, platinum_piece_num, crystal_piece_num)
    
    #===========================================================
    # ショップ.
    @staticmethod
    def get_shopmaster_list(model_mgr, midlist, using=settings.DB_DEFAULT):
        """ショップ商品のマスターデータ.
        """
        return model_mgr.get_models(ShopItemMaster, midlist, using=using)
    
    @staticmethod
    def get_shopmaster(model_mgr, mid, using=settings.DB_DEFAULT):
        """ショップ商品のマスターデータ.
        """
        masterlist = BackendApi.get_shopmaster_list(model_mgr, [mid], using=using)
        if masterlist:
            return masterlist[0]
        else:
            return None
    
    @staticmethod
    def get_shopbuydata(model_mgr, uid, midlist, using=settings.DB_DEFAULT):
        """ショップ購入情報.
        """
        arr = model_mgr.get_models(ShopItemBuyData, [ShopItemBuyData.makeID(uid, mid) for mid in midlist], using=using)
        result = {}
        for model in arr:
            result[model.mid] = model
        return result
    
    @staticmethod
    def get_shopitem_stock(model_mgr, shopitemmaster, buydata, now=None):
        """在庫数.
        """
        if 0 < shopitemmaster.stock:
            cnt = buydata.getTodayBuyCnt(now) if buydata else 0
            return max(0, shopitemmaster.stock - cnt)
        else:
            return -1
    
    @staticmethod
    def check_buyable_shopitem(model_mgr, player, shopitemmaster, buydata, buynum=1, now=None, using=settings.DB_DEFAULT):
        """購入可能な商品かをチェック.
        """
        stock = BackendApi.get_shopitem_stock(model_mgr, shopitemmaster, buydata, now)
        if stock != -1 and stock < buynum:
            # 在庫がない.
            return False
        elif shopitemmaster.beginer and not player.is_beginer(now):
            # 初心者用.
            return False
        elif not BackendApi.check_schedule(model_mgr, shopitemmaster.schedule, using=using):
            # 期間外.
            return False
        return True
    
    @staticmethod
    def get_buyable_shopitemlist(model_mgr, player, now=None, using=settings.DB_DEFAULT):
        """購入可能なショップ商品リスト.
        """
        shopmasterlist = model_mgr.get_mastermodel_all(ShopItemMaster, using=using)
        masteridlist = [shopmaster.id for shopmaster in shopmasterlist]
        buydatas = BackendApi.get_shopbuydata(model_mgr, player.id, masteridlist, using=using)
        
        shopmasterlist = [shopmaster for shopmaster in shopmasterlist if BackendApi.check_buyable_shopitem(model_mgr, player, shopmaster, buydatas.get(shopmaster.id), now=now, using=using)]
        shopmasterlist.sort(key=operator.attrgetter('pri'), reverse=True)
        return shopmasterlist
    
    @staticmethod
    def make_shopitem_obj(handler, master, player, buydata):
        """HTML出力用の商品情報.
        """
        num = -1
        url_use = None
        unit = Defines.ItemType.UNIT.get(master.itype0, '')
        if master.itype0 == Defines.ItemType.ITEM:
            model_mgr = handler.getModelMgr()
            itemmaster = BackendApi.get_itemmaster(model_mgr, master.iid0, using=settings.DB_READONLY)
            num = BackendApi.get_item_nums(model_mgr, player.id, [master.iid0], using=settings.DB_READONLY).get(master.iid0, 0)
            ignores = Defines.ItemEffect.CABACLUB_STORE_ITEMS + Defines.ItemEffect.PRODUCE_ONLY_ITEMS
            if itemmaster.id not in ignores:
                url_use = UrlMaker.item_useyesno(master.iid0)
                if itemmaster:
                    unit = itemmaster.unit
        elif master.itype0 == Defines.ItemType.CARD:
            model_mgr = handler.getModelMgr()
            cardmaster = BackendApi.get_cardmasters([master.iid0], model_mgr, using=settings.DB_READONLY).get(master.iid0)
            if cardmaster:
                unit = Defines.CardKind.UNIT[cardmaster.ckind]
        elif master.itype0 == Defines.ItemType.TRYLUCKTICKET:
            num = player.ticket
            url_use = UrlMaker.gacha()
        elif master.itype0 == Defines.ItemType.CABARETCLUB_SPECIAL_MONEY:
            model_mgr = handler.getModelMgr()
            playerdata = BackendApi.get_cabaretclub_scoreplayerdata(model_mgr, player.id, using=settings.DB_READONLY)
            num = playerdata.money if playerdata else 0
        elif master.itype0 == Defines.ItemType.CABARETCLUB_HONOR_POINT:
            model_mgr = handler.getModelMgr()
            playerdata = BackendApi.get_cabaretclub_scoreplayerdata(model_mgr, player.id, using=settings.DB_READONLY)
            num = playerdata.point if playerdata else 0
        return Objects.shopitem(handler, master, player, buydata, num, url_use, unit)
    
    @staticmethod
    def get_shoppaymententry(model_mgr, paymentId, using=settings.DB_DEFAULT):
        """サーバ側の課金レコードを取得.
        """
        return model_mgr.get_model(ShopPaymentEntry, paymentId, using=using)
    
    @staticmethod
    def tr_create_shoppaymententry(model_mgr, player, paymentdata, ctime):
        """課金レコードの作成.
        """
        if paymentdata.status != PaymentData.Status.START:
            raise CabaretError(u'課金ステータスが不正です', CabaretError.Code.ILLEGAL_ARGS)
        
        ins = BackendApi.get_shoppaymententry(model_mgr, paymentdata.paymentId)
        if ins:
            raise CabaretError(u'作成済みです', CabaretError.Code.ALREADY_RECEIVED)
        
        item = paymentdata.paymentItems[0]
        iid = int(item.itemId)
        inum = int(item.quantity)
        
        ins = ShopPaymentEntry()
        ins.id = paymentdata.paymentId
        
        ins.uid = player.id
        ins.iid = iid
        ins.inum = inum
        ins.price = int(item.unitPrice)
        ins.state = PaymentData.Status.CREATE
        ins.ctime = ctime
        
        model_mgr.set_save(ins)
        
        return ins
    
    @staticmethod
    def tr_update_shoppaymententry(model_mgr, uid, paymentId, status):
        """課金レコードのステータスを更新.
        """
        if status == PaymentData.Status.CREATE:
            raise CabaretError(u'このステータスは指定できません', CabaretError.Code.ILLEGAL_ARGS)
        
        entry = BackendApi.get_shoppaymententry(model_mgr, paymentId)
        if entry is None:
            raise CabaretError(u'課金レコードが存在しません', CabaretError.Code.NOT_DATA)
        
        entry = ShopPaymentEntry.getByKeyForUpdate(paymentId)
        model_mgr.set_got_models_forupdate([entry])
        if entry.uid != uid:
            raise CabaretError(u'他人の課金レコードです', CabaretError.Code.ILLEGAL_ARGS)
        elif entry.state == status:
            raise CabaretError(u'処理済みです', CabaretError.Code.ALREADY_RECEIVED)
        elif status == PaymentData.Status.START and entry.state != PaymentData.Status.CREATE:
            raise CabaretError(u'課金ステータスが不正です', CabaretError.Code.ILLEGAL_ARGS)
        elif status != PaymentData.Status.START and entry.state != PaymentData.Status.START:
            raise CabaretError(u'課金ステータスが不正です', CabaretError.Code.ILLEGAL_ARGS)
        entry.state = status
        model_mgr.set_save(entry)
        
        def writeEnd():
            client = OSAUtil.get_cache_client()
            KEY = 'payment_checked:%s' % uid
            client.delete(KEY)
        model_mgr.add_write_end_method(writeEnd)
        
        return entry
    
    @staticmethod
    def tr_shopcancel(model_mgr, uid, paymentId):
        """キャンセル.
        """
        return BackendApi.tr_update_shoppaymententry(model_mgr, uid, paymentId, PaymentData.Status.CANCEL)
    
    @staticmethod
    def tr_shoptimeout(model_mgr, uid, paymentId):
        """キャンセル.
        """
        return BackendApi.tr_update_shoppaymententry(model_mgr, uid, paymentId, PaymentData.Status.TIMEOUT)
    
    @staticmethod
    def __tr_give_shopitem(model_mgr, player, shopitemmaster, buynum):
        """ショップの商品を付与.
        """
        prizelist = shopitemmaster.getItemList(buynum)
        
        rareoverticket = 0
        ticket = 0
        memoriesticket = 0
        gachaticket = 0
        goldkey = 0
        silverkey = 0
        cardidlist = []
        cabaclub_money = 0
        cabaclub_honor_point = 0
        
        for prize in prizelist:
            rareoverticket += prize.rareoverticket
            ticket += prize.ticket
            memoriesticket += prize.memoriesticket
            gachaticket += prize.gachaticket
            goldkey += prize.goldkey
            silverkey += prize.silverkey
            cabaclub_money += prize.cabaclub_money
            cabaclub_honor_point += prize.cabaclub_honor
            if 0 < prize.cardnum:
                cardidlist.extend([prize.cardid] * prize.cardnum)
            if 0 < prize.itemnum:
                BackendApi.tr_add_item(model_mgr, player.id, prize.itemid, prize.itemnum, is_pay=True)
        
        # チケット.
        if 0 < rareoverticket:
            BackendApi.tr_add_rareoverticket(model_mgr, player.id, rareoverticket)
        if 0 < ticket:
            BackendApi.tr_add_tryluckticket(model_mgr, player.id, ticket)
        if 0 < memoriesticket:
            BackendApi.tr_add_memoriesticket(model_mgr, player.id, memoriesticket)
        if 0 < gachaticket:
            BackendApi.tr_add_gachaticket(model_mgr, player.id, gachaticket)
        
        # 鍵.
        if 0 < goldkey:
            BackendApi.tr_add_goldkey(model_mgr, player.id, goldkey)
        if 0 < silverkey:
            BackendApi.tr_add_silverkey(model_mgr, player.id, silverkey)
        
        # カード.
        if cardidlist:
            for cardid in cardidlist:
                playercard = PlayerCard.getByKeyForUpdate(player.id)
                BackendApi.tr_create_card(model_mgr, playercard, cardid, way=Defines.CardGetWayType.SHOP)
        
        # 特別なマネー.
        if 0 < cabaclub_money:
            BackendApi.tr_add_cabaretclub_money(model_mgr, player.id, cabaclub_money)
        # 名誉ポイント.
        if 0 < cabaclub_honor_point:
            BackendApi.tr_add_cabaretclub_honor_point(model_mgr, player.id, cabaclub_honor_point)
    
    @staticmethod
    def tr_shopbuy(model_mgr, player, paymentId, is_pc):
        """購入.
        課金レコードのチェック以外はなにもチェックを入れない方がいい.
        """
        entry = BackendApi.tr_update_shoppaymententry(model_mgr, player.id, paymentId, PaymentData.Status.COMPLETED)
        
        shopitemmaster = BackendApi.get_shopmaster(model_mgr, entry.iid)
        BackendApi.__tr_give_shopitem(model_mgr, player, shopitemmaster, entry.inum)
        
        # 購入情報を更新.
        buydata = ShopItemBuyData.getByKeyForUpdate(ShopItemBuyData.makeID(player.id, shopitemmaster.id))
        buydata.addBuyCnt(entry.inum, entry.ctime)
        model_mgr.set_save(buydata)
        
        # 消費ポイントを加算.
        def forUpdatePlayerConsumePoint(model, inserted):
            model.point_total += entry.price * entry.inum
        model_mgr.add_forupdate_task(PlayerConsumePoint, player.id, forUpdatePlayerConsumePoint)
        
        def writeEnd():
            KpiOperator().set_save_shop_buy(player.id, is_pc, entry.inum*entry.price).save()
        model_mgr.add_write_end_method(writeEnd)
        
        return entry
    
    @staticmethod
    def tr_shopbuy_free(model_mgr, player, shopitemmaster, buynum, now):
        """アプリ内通貨で購入.
        """
        uid = player.id
        # 付与
        BackendApi.__tr_give_shopitem(model_mgr, player, shopitemmaster, buynum)
        
        # 通貨を消費.
        price = shopitemmaster.price * buynum
        if shopitemmaster.consumetype == Defines.ShopConsumeType.GOLD:
            BackendApi.tr_add_gold(model_mgr, uid, -price)
        elif shopitemmaster.consumetype == Defines.ShopConsumeType.CABAKING:
            BackendApi.tr_add_cabaretking_treasure(model_mgr, uid, -price)
        
        buydata = ShopItemBuyData.getByKeyForUpdate(ShopItemBuyData.makeID(player.id, shopitemmaster.id))
        buydata.addBuyCnt(buynum, now)
        model_mgr.set_save(buydata)
    
    #===========================================================
    # 強化合成.
    @staticmethod
    def get_compositiondata(model_mgr, uid, using=settings.DB_DEFAULT):
        """合成情報.
        """
        return BackendApi.get_model(model_mgr, CompositionData, uid, using=using)
    
    @staticmethod
    def choose_composition_result():
        """合成結果を選ぶ.
        成功 or 大成功.
        """
        rand = AppRandom()
        return rand.getIntN(10000) < (Defines.COMPOSITION_GREAT_SUCCESS_RATE * 100)
    
    @staticmethod
    def calc_composition_exp(basecardset, cardsetlist, is_great_success=False):
        """合成経験値を集計.
        経験値＝基本素材経験値×（1+使用コスト/100）×（1+素材のレベル/50）×属性補正.
        属性補正値：同属性1.1、異属性1
        """
        exp_total = 0
        basetype = basecardset.master.ctype
        
        if is_great_success:
            success_rate = Defines.COMPOSITION_GREAT_SUCCESS_EXP_RATE
        else:
            success_rate = 100
        
        for cardset in cardsetlist:
            card = cardset.card
            master = cardset.master
            exp = master.basematerialexp * (100 + master.cost) / 100 * (50 + card.level) / 50
            if basetype == master.ctype:
                exp *= Defines.COMPOSITION_SAME_TYPE_EXP_RATE / 100
            exp_total += int(int(exp) * success_rate / 100)
        return exp_total
    
    @staticmethod
    def calc_composition_cost(basecardset, cardsetlist):
        """合成費用を集計.
        """
        return (basecardset.card.level + 1) * 100 * len(cardsetlist)
    
    @staticmethod
    def calc_composition_skill_lvup(basecardset, cardsetlist):
        """合成でのスキルレベルアップ集計.
        """
        baseskill = basecardset.master.getSkill()
        if baseskill is None:
            return 0
        
        lvup = 0
        for cardset in cardsetlist:
            skill = cardset.master.getSkill()
            #もしティアラか、自身のレア度以下なら
            if cardset.master.id == Defines.MasterData.TIARA_ID \
                or (cardset.master.ckind == Defines.CardKind.SKILL and cardset.master.rare >= basecardset.master.rare):
                lvup += 1
            elif skill is not None and skill.group == baseskill.group:
                lvup += 1
        return lvup
    
    @staticmethod
    def composition(model_mgr, basecardset, materialcardsetlist, is_great_success, using=settings.DB_DEFAULT):
        # スキルレベル.
        skilllvup = BackendApi.calc_composition_skill_lvup(basecardset, materialcardsetlist)
        post_skilllevel = min(Defines.SKILLLEVEL_MAX, basecardset.card.skilllevel + skilllvup)
        skilllvup = post_skilllevel - basecardset.card.skilllevel
        basecardset.card.skilllevel = post_skilllevel
        
        # 経験値.
        exp_total = BackendApi.calc_composition_exp(basecardset, materialcardsetlist, is_great_success)
        exp_total, lvup = BackendApi.add_cardexp(model_mgr, basecardset, exp_total, using=using)
        return exp_total, skilllvup, lvup
    
    @staticmethod
    def tr_composition_do(model_mgr, uid, basecardid, materialcardidlist, confirmkey):
        """合成を実行.
        """
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        
        compositiondata = model_mgr.get_model(CompositionData, uid)
        if compositiondata is None:
            compositiondata = CompositionData.makeInstance(uid)
        else:
            compositiondata = CompositionData.getByKeyForUpdate(uid)
        model_mgr.set_got_models([compositiondata])
        
        deck = BackendApi.get_deck(uid, model_mgr)
        raid_deck = BackendApi.get_raid_deck(uid, model_mgr)
        
        # 店舗に配置されているキャストを確認.
        BackendApi.check_cabaretclub_cast_include(model_mgr, uid, materialcardidlist)
        
        cardidlist = [basecardid]
        cardidlist.extend(materialcardidlist)
        cardsetlist = BackendApi.get_cards(cardidlist, model_mgr)
        basecardset = None
        materialcardsetlist = []
        
        for cardset in cardsetlist:
            if uid != cardset.card.uid:
                raise CabaretError(u'他人のキャストです', CabaretError.Code.ILLEGAL_ARGS)
            elif cardset.id == basecardid and not settings_sub.IS_BENCH:
                if cardset.master.ckind != Defines.CardKind.NORMAL:
                    raise CabaretError(u'教育できないキャストです', CabaretError.Code.ILLEGAL_ARGS)
                else:
                    basecardset = cardset
            elif cardset.card.protection and not settings_sub.IS_BENCH:
                raise CabaretError(u'保護中のキャストです', CabaretError.Code.ILLEGAL_ARGS)
            elif deck.is_member(cardset.card.id) and not settings_sub.IS_BENCH:
                raise CabaretError(u'出勤中のキャストです', CabaretError.Code.ILLEGAL_ARGS)
            elif raid_deck and raid_deck.is_member(cardset.card.id) and not settings_sub.IS_BENCH:
                raise CabaretError(u'出勤中のキャストです', CabaretError.Code.ILLEGAL_ARGS)
            else:
                materialcardsetlist.append(cardset)
        
        if basecardset is None or len(materialcardsetlist) != len(materialcardidlist):
            raise CabaretError(u'キャストが存在しません', CabaretError.Code.ILLEGAL_ARGS)
        elif not basecardset.is_can_composition:
            raise CabaretError(u'これ以上教育できません', CabaretError.Code.OVER_LIMIT)
        
        # 合成前パラメータを保存.
        compositiondata.setBasePreParameter(basecardset.card)
        
        # 成功 or 大成功.
        is_great_success = BackendApi.choose_composition_result()
        
        # 費用.
        gold_total = BackendApi.calc_composition_cost(basecardset, materialcardsetlist)
        BackendApi.tr_add_gold(model_mgr, uid, -gold_total)
        
        # 経験値.
        exp_pre = basecardset.card.exp
        level_pre = basecardset.card.level
        
        # スキルレベル.
        exp_total, skilllvup, lvup = BackendApi.composition(model_mgr, basecardset, materialcardsetlist, is_great_success)
        
        # 結果を設定.
        compositiondata.setResult(basecardset, materialcardsetlist, is_great_success, gold_total, exp_total, exp_pre, level_pre, lvup, skilllvup)
        
        # ログ.
        model_mgr.set_save(UserLogComposition.create(uid, basecardset, materialcardsetlist, exp_total, is_great_success, basecardset.card.skilllevel, skilllvup))
        
        # カード削除.
        for materialcardset in materialcardsetlist:
            if settings_sub.IS_BENCH:
                model_mgr.set_save(materialcardset.card)
            else:
                model_mgr.set_save(CardDeleted.create(materialcardset.card))
                model_mgr.set_delete(materialcardset.card)
        
        model_mgr.set_save(compositiondata)
        model_mgr.set_save(basecardset.card)
        
        # ミッション.
        mission_executer = PanelMissionConditionExecuter()
        mission_executer.addTargetDoComposition()
        if skilllvup:
            # スキルのレベルが上った.
            mission_executer.addTargetServiceLevel(basecardset.card.skilllevel)
        BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
        
        # 書き込み後のタスク.
        def writeend():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            BackendApi.save_cardidset(basecardset, deck, pipe)
            if settings_sub.IS_BENCH:
                for cardset in materialcardsetlist:
                    BackendApi.save_cardidset(cardset, pipe=pipe)
            else:
                for cardset in materialcardsetlist:
                    BackendApi.delete_cardidset(cardset, pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeend)
    
    @staticmethod
    def make_composition_effectparams(handler, basecard, materialcardlist, exp_pre, exp_add, level_pre, level_add, skilllevelup, is_great_success):
        """教育演出用パラメータ作成.
        """
        basemaster = basecard.master
        
        model_mgr = handler.getModelMgr()
        def getExpRate(exp):
            cur_levelexp = BackendApi.get_cardlevelexp_byexp(exp, model_mgr, using=settings.DB_READONLY)
            next_levelexp = None
            if cur_levelexp:
                next_levelexp = BackendApi.get_cardlevelexp_bylevel(cur_levelexp.level + 1, model_mgr, using=settings.DB_READONLY)
            if next_levelexp:
                rate = max(0, min(100, int(100 * (exp - cur_levelexp.exp) / (next_levelexp.exp - cur_levelexp.exp))))
            else:
                rate = 100
            return rate
        
        exp_post = exp_pre + exp_add
        
        params = {
            'baseText' : Defines.EffectTextFormat.EDUCATION_BASETEXT % basemaster.name,
            'trainerText' : Defines.EffectTextFormat.EDUCATION_TRAINERTEXT,
            'levelupCount' : level_add,
            'serviceFlag' : int(bool(skilllevelup)),
            'greatFlag' : int(bool(is_great_success)),
            'levelGauge' : Defines.ANIMATION_SEPARATE_STRING.join([str(getExpRate(exp_pre)), str(getExpRate(exp_post))]),
            'baseImage':handler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(basemaster)),
        }
        if is_great_success:
            params['lastText1'] = Defines.EffectTextFormat.EDUCATION_LASTTEXT1_GREAT % basemaster.name
        else:
            params['lastText1'] = Defines.EffectTextFormat.EDUCATION_LASTTEXT1 % basemaster.name
        
        if 0 < level_add:
            pow_pre = CardUtil.calcPower(basemaster.gtype, basemaster.basepower, basemaster.maxpower, level_pre, basemaster.maxlevel, basecard.card.takeover)
            pow_post = CardUtil.calcPower(basemaster.gtype, basemaster.basepower, basemaster.maxpower, level_pre + level_add, basemaster.maxlevel, basecard.card.takeover)
            params['lastText2'] = Defines.EffectTextFormat.EDUCATION_LASTTEXT2 % (basemaster.name, pow_post - pow_pre)
        
        if skilllevelup:
            params['serviceText'] = Defines.EffectTextFormat.EDUCATION_SERVICETEXT % basemaster.getSkill().name
        
        indextable = Defines.EffectIndexTables.EDUCATION.get(len(materialcardlist)) or range(1, len(materialcardlist)+1)
        for i, materialcard in enumerate(materialcardlist):
            params['subImage%d' % indextable[i]] = handler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(materialcard.master))
        return params
    
    #===========================================================
    # 進化合成.
    @staticmethod
    def get_evolutiondata(model_mgr, uid, using=settings.DB_DEFAULT):
        """進化情報.
        """
        evolutiondata = model_mgr.get_model(EvolutionData, uid, using=using)
        if evolutiondata is None:
            evolutiondata = EvolutionData.makeInstance(uid)
            evolutiondata.save()
            model_mgr.set_got_models([evolutiondata])
        return evolutiondata
    
    @staticmethod
    def get_evolution_cardmaster(model_mgr, master, using=settings.DB_DEFAULT):
        """進化後のカードマスターデータを取得.
        """
        if not master.rare in Defines.Rarity.EVOLUTION_ABLES:
            return None
        elif not (1 <= master.hklevel <= Defines.HKLEVEL_MAX):
            return None
        return BackendApi.get_cardmaster_by_albumhklevel(model_mgr, master.album, master.hklevel + 1, using=using)
    
    @staticmethod
    def get_cardmasterid_by_albumhklevel(model_mgr, album, hklevel=None, using=settings.DB_DEFAULT):
        """アルバムとハメ管理度を指定してマスターIDを取得.
        """
        if hklevel is None:
            hklevels = range(1, Defines.HKLEVEL_MAX+1)
        elif isinstance(hklevel, (list, tuple)):
            if len(hklevel) == 0:
                return []
            hklevels = hklevel
        else:
            hklevels = [hklevel]
        
        midset = {}
        reqests = []
        for hklv in hklevels:
            mid = AlbumHkLevelSet.get(album, hklv)
            if mid is None:
                reqests.append(CardMaster.makeAlbumHklevel(album, hklv))
            else:
                midset[hklv] = mid
        
        if reqests:
            if len(reqests) == 1:
                data = CardMaster.getValues(['id', 'albumhklevel'], {'albumhklevel':reqests[0]}, using=using)
                if data:
                    data = [data]
            else:
                data = CardMaster.fetchValues(['id', 'albumhklevel'], {'albumhklevel__in':reqests}, using=using)
            if data:
                pipe = AlbumHkLevelSet.getDB().pipeline()
                for model in data:
                    midset[model.hklevel] = model.id
                    AlbumHkLevelSet._save(pipe, album, model.hklevel, model.id)
                pipe.execute()
        
        if hklevel is None or isinstance(hklevel, (list, tuple)):
            if midset:
                return [midset[hklv] for hklv in sorted(midset.keys())]
            else:
                return []
        else:
            return midset.get(hklevel, None)
    
    @staticmethod
    def get_cardmaster_by_albumhklevel(model_mgr, album, hklevel, using=settings.DB_DEFAULT):
        """アルバムとハメ管理度を指定してマスターを取得.
        """
        mid = BackendApi.get_cardmasterid_by_albumhklevel(model_mgr, album, hklevel, using=settings.DB_DEFAULT)
        if mid:
            return BackendApi.get_cardmasters([mid], model_mgr, using=using).get(mid, None)
        else:
            return None
    
    @staticmethod
    def check_evol_deckcost(model_mgr, player, basecard, using=settings.DB_DEFAULT):
        deck = BackendApi.get_deck(player.id, model_mgr, using=using)
        members = deck.to_array()[:]
        
        cost_over = False
        deck_none = False
        if basecard.id in members:
            members.remove(basecard.id)
            if members:
                member_cardsetlist = BackendApi.get_cards(members, model_mgr)
                cost = 0
                for member_cardset in member_cardsetlist:
                    cost += member_cardset.master.cost
                if player.deckcapacity < (cost + basecard.master.cost):
                    # コストオーバー.
                    cost_over = True
                    if not members:
                        deck_none = True
        return cost_over, deck_none
    
    @staticmethod
    def tr_evolution_do(model_mgr, player, basecardid, materialcardid, confirmkey):
        """進化合成を実行.
        """
        uid = player.id
        
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        
        # 店舗に配置されているキャストを確認.
        BackendApi.check_cabaretclub_cast_include(model_mgr, uid, [materialcardid])
        
        evolutiondata = model_mgr.get_model(EvolutionData, uid)
        if evolutiondata is None:
            evolutiondata = EvolutionData.makeInstance(uid)
        else:
            evolutiondata = EvolutionData.getByKeyForUpdate(uid)
        model_mgr.set_got_models([evolutiondata])
        
        deck = BackendApi.get_deck(uid, model_mgr)
        raid_deck = BackendApi.get_raid_deck(uid, model_mgr)
        
        cardidlist = [basecardid, materialcardid]
        cardsetlist = BackendApi.get_cards(cardidlist, model_mgr)
        
        basecardset = None
        materialcardset = None
        for cardset in cardsetlist:
            if uid != cardset.card.uid:
                raise CabaretError(u'他人のものを盗んではいけません', CabaretError.Code.ILLEGAL_ARGS)
            elif cardset.id == basecardid:
                if cardset.master.ckind != Defines.CardKind.NORMAL and not settings_sub.IS_BENCH:
                    raise CabaretError(u'この組み合わせはハメ管理できません', CabaretError.Code.ILLEGAL_ARGS)
                else:
                    basecardset = cardset
            elif cardset.card.protection and not settings_sub.IS_BENCH:
                raise CabaretError(u'保護された素材です', CabaretError.Code.ILLEGAL_ARGS)
            elif deck.is_member(cardset.card.id) and not settings_sub.IS_BENCH:
                raise CabaretError(u'設定中なので素材に出来ません', CabaretError.Code.ILLEGAL_ARGS)
            elif raid_deck and raid_deck.is_member(cardset.card.id) and not settings_sub.IS_BENCH:
                raise CabaretError(u'設定中なので素材に出来ません', CabaretError.Code.ILLEGAL_ARGS)
            else:
                materialcardset = cardset
        
        if basecardset is None or materialcardset is None:
            raise CabaretError(u'存在しません', CabaretError.Code.ILLEGAL_ARGS)
        elif not (CardMaster.makeAlbumHklevel(basecardset.master.album, 1) <= materialcardset.master.albumhklevel <= basecardset.master.albumhklevel) and not settings_sub.IS_BENCH:
            # 進化用カードはだいじょうぶ.
            if not (materialcardset.master.ckind == Defines.CardKind.EVOLUTION and basecardset.master.rare <= materialcardset.master.rare):
                raise CabaretError(u'この組み合わせではハメ管理できません', CabaretError.Code.ILLEGAL_ARGS)
        
        evolution_cardmaster = BackendApi.get_evolution_cardmaster(model_mgr, basecardset.master)
        if evolution_cardmaster is None or not basecardset.is_can_evolution:
            if settings_sub.IS_BENCH:
                evolution_cardmaster = basecardset.master
            else:
                raise CabaretError(u'これ以上ハメ管理合成できません', CabaretError.Code.OVER_LIMIT)
        
        takeover = basecardset.get_evolution_takeover()
        # 素材が何であろうと指輪と同じ効果に変更.
        takeover *= 2
        
        # ログ.
        model_mgr.set_save(UserLogEvolution.create(uid, basecardset, materialcardset, takeover))
        
        # 進化前パラメータを保存.
        evolutiondata.setBasePreParameter(basecardset.card)
        
        # レベルと経験値を初期化.
        if not settings_sub.IS_BENCH:
            basecardset.card.level = 1
            basecardset.card.exp = 0
            
            # 引き継ぎ.
            basecardset.card.takeover += takeover
        
        # 費用.
        gold_total = evolution_cardmaster.evolcost
        BackendApi.tr_add_gold(model_mgr, uid, -gold_total)
        
        if not settings_sub.IS_BENCH:
            # 進化後のマスターIDを設定.
            basecardset.card.mid = evolution_cardmaster.id
        
        # 進化後のカードの入手フラグ.
        is_newcard = BackendApi.tr_set_cardacquisition(model_mgr, uid, evolution_cardmaster)
        
        # 結果を設定.
        evolutiondata.setResult(basecardset, materialcardset, is_newcard, takeover)
        
        # カード削除.
        if settings_sub.IS_BENCH:
            model_mgr.set_save(materialcardset.card)
        else:
            model_mgr.set_save(CardDeleted.create(materialcardset.card))
            model_mgr.set_delete(materialcardset.card)
        
        model_mgr.set_save(evolutiondata)
        model_mgr.set_save(basecardset.card)
        
        # デッキ確認.
        basecardset_post = CardSet(basecardset.card, evolution_cardmaster)
        cost_over, deck_none = BackendApi.check_evol_deckcost(model_mgr, player, basecardset_post)
        if deck_none:
            raise CabaretError(u'人件費オーバーで出勤キャストいなくなってしまいます')
        elif cost_over:
            members = deck.to_array()
            members.remove(basecardid)
            deck.set_from_array(members)
            model_mgr.set_save(deck)
        
        # ミッション.
        mission_executer = PanelMissionConditionExecuter()
        mission_executer.addTargetEvolution(evolution_cardmaster.hklevel)
        if materialcardset.master.ckind == Defines.CardKind.EVOLUTION:
            # 指輪を使った.
            mission_executer.addTargetEvolutionRing(evolution_cardmaster.hklevel)
        BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
        
        # 書き込み後のタスク.
        def writeend():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            BackendApi.save_cardidset(basecardset_post, deck, pipe)
            if settings_sub.IS_BENCH:
                BackendApi.save_cardidset(materialcardset, pipe=pipe)
            else:
                BackendApi.delete_cardidset(materialcardset, pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeend)
    
    #===========================================================
    # ログインボーナス.
    @staticmethod
    def get_playerlogintimelimited(model_mgr, uid, using=settings.DB_DEFAULT):
        """期間別ログインボーナス用プレイヤーの取得(廃止予定).
        """
        playerlogin = BackendApi.get_model(model_mgr, PlayerLoginTimeLimited, uid, using=using)
        if playerlogin is None:
            def tr():
                model_mgr = ModelRequestMgr()
                def forUpdate(model, inserted):
                    if not inserted:
                        raise CabaretError('already', CabaretError.Code.ALREADY_RECEIVED)
                model_mgr.add_forupdate_task(PlayerLoginTimeLimited, uid, forUpdate)
                model_mgr.write_all()
                return model_mgr
            try:
                tmp_model_mgr = db_util.run_in_transaction(tr)
                tmp_model_mgr.write_end()
            except CabaretError, err:
                if err.code == CabaretError.Code.ALREADY_RECEIVED:
                    tmp_model_mgr = model_mgr
                else:
                    raise
            playerlogin = tmp_model_mgr.get_wrote_model(PlayerLoginTimeLimited, uid, PlayerLoginTimeLimited.getByKey, uid)
            model_mgr.set_got_models([playerlogin])
        return playerlogin
    
    @staticmethod
    def get_logintimelimited_data_dict(model_mgr, uid, midlist, using=settings.DB_DEFAULT):
        """期間別ログインボーナス情報の取得.
        """
        idlist = [LoginBonusTimeLimitedData.makeID(uid, mid) for mid in midlist]
        return BackendApi.get_model_dict(model_mgr, LoginBonusTimeLimitedData, idlist, using=using, key=lambda x:x.mid)
    
    @staticmethod
    def get_logintimelimited_data(model_mgr, uid, mid, using=settings.DB_DEFAULT):
        """期間別ログインボーナス情報の取得.
        """
        return BackendApi.get_logintimelimited_data_dict(model_mgr, uid, [mid], using).get(mid, None)
    
    @staticmethod
    def check_loginbonus_received(playerlogin, now=None):
        """ログインボーナスを受け取り済みなのかを判定.
        """
        now = now or OSAUtil.get_now()
        if DateTimeUtil.judgeSameDays(playerlogin.lbtime, now):
            # 受取済み.
            return True
        return False
    
    @staticmethod
    def check_loginbonustimelimited_received(logintimelimited_data, now=None):
        """期間別ログインボーナスを受け取り済みなのかを判定.
        """
        if logintimelimited_data and DateTimeUtil.judgeSameDays(logintimelimited_data.lbtltime, now):
            # 受取済み.
            return True
        return False
    
    @staticmethod
    def check_lead_loginbonustimelimited(model_mgr, uid, now=None):
        """期間別ログインボーナスを受け取り済みなのかを判定.
        """
        now = now or OSAUtil.get_now()
        
        playertutorial = BackendApi.get_model(model_mgr, PlayerTutorial, uid, using=settings.DB_READONLY)
        
        masterlist = BackendApi.get_current_loginbonustimelimitedmaster_list(model_mgr, using=settings.DB_READONLY, target_time=now, tutorialendtime=playertutorial.etime)
        if not masterlist:
            return False
        
        midlist = [master.id for master in masterlist]
        logindata_dict = BackendApi.get_logintimelimited_data_dict(model_mgr, uid, midlist, using=settings.DB_READONLY)
        
        for master in masterlist:
            if not BackendApi.check_loginbonustimelimited_received(logindata_dict.get(master.id), now):
                return True
        return False
    
    @staticmethod
    def get_continuityloginbonus(model_mgr, continuitylogin_days, using=settings.DB_DEFAULT):
        """連続ログインボーナスを取得.
        """
        days_max = LoginBonusMaster.max_value('day', 0, using=using)
        if days_max < 1:
            return None
        day = ((continuitylogin_days-1) % days_max) + 1
        master = model_mgr.get_model(LoginBonusMaster, day, using=using)
        return master
    
    @staticmethod
    def get_continuityloginbonus_all(model_mgr, using=settings.DB_DEFAULT):
        """連続ログインボーナスを全て取得.
        """
        return model_mgr.get_mastermodel_all(LoginBonusMaster, order_by='day', using=using)
    
    @staticmethod
    def get_accessbonus_list(model_mgr, access_days, using=settings.DB_DEFAULT):
        """アクセスボーナスを取得.
        """
        return model_mgr.get_models(AccessBonusMaster, [0, access_days], using=using)
    
    @staticmethod
    def tr_send_loginbonus(model_mgr, player, now, config, totallogintable, is_pc):
        """ログインボーナスの付与.
        """
        result = {}
        
        uid = player.id
        playerlogin = PlayerLogin.getByKeyForUpdate(uid)
        if BackendApi.check_loginbonus_received(playerlogin, now) and not settings_sub.IS_BENCH:
            raise CabaretError(u'受取済みです', CabaretError.Code.ALREADY_RECEIVED)
        player.setModel(playerlogin)
        
        # 前回受け取った時間の基準時間.
        pre_basetime = DateTimeUtil.toLoginTime(playerlogin.lbtime)
        # 今日の基準時間.
        basetime = DateTimeUtil.toLoginTime(now)
        # 前回受け取った時間からの差分.
        delta = basetime - pre_basetime
        if 1 < delta.days:
            # 連続ログインが切れた.
            playerlogin.ldays = 0
        playerlogin.pdays += 1
        playerlogin.ldays += 1
        lbtime_pre = playerlogin.lbtime
        playerlogin.lbtime = now
        
        def sendPrize(prizeidlist, textid):
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
        
        continuity_loginbonus = None
        total_loginbonus = None

        if totallogintable:
            daylist = totallogintable.keys()
            daylist.sort()
            daymax = daylist[-1]
            
            # 累計ログイン.
            mid = config.getCurrentMasterID(now)
            playerlogin.tldays = (playerlogin.getDays(mid) % daymax) + 1
            playerlogin.tldays_view = playerlogin.getDaysView(mid) + 1
            playerlogin.tlmid = mid
            
            master = BackendApi.get_loginbonustimelimitedmaster(model_mgr, mid)
            daymaster = BackendApi.get_loginbonustimelimiteddaysmaster(model_mgr, mid, playerlogin.tldays)
            sendPrize(daymaster.prizes, master.textid or Defines.TextMasterID.LOGIN_BONUS)
            
            total_loginbonus = daymaster
            
            # ログ.
            model_mgr.set_save(UserLogLoginBonus.create(uid, playerlogin.ldays, playerlogin.pdays, playerlogin.tldays, playerlogin.tldays_view))
        else:
            if config.continuity_login:
                # 連続ログイン.
                continuity_loginbonus = BackendApi.get_continuityloginbonus(model_mgr, playerlogin.ldays)
                if continuity_loginbonus:
                    sendPrize(continuity_loginbonus.prizes, Defines.TextMasterID.LOGIN_BONUS)
            # ログ.
            model_mgr.set_save(UserLogLoginBonus.create(uid, playerlogin.ldays, playerlogin.pdays, 0, 0))
        
        # アクセスボーナス.
        accessbonuslist = BackendApi.get_accessbonus_list(model_mgr, playerlogin.pdays)
        for accessbonus in accessbonuslist:
            sendPrize(accessbonus.prizes, Defines.TextMasterID.ACCESS_BONUS)
        
        # 全プレ.
        presenteveryone_list = BackendApi.get_presenteveryone_list_forloginbonus(model_mgr, now=now)
        if presenteveryone_list:
            BackendApi.tr_receive_presenteveryone(model_mgr, player, presenteveryone_list, now)
        
        # カムバックキャンペーン.
        if 1 < playerlogin.pdays:
            comeback_mid_list = BackendApi.tr_send_comebackcampaign_prize(model_mgr, uid, lbtime_pre, playerlogin.lbtime)
        else:
            comeback_mid_list = []
        
        # ロングログインボーナス.
        result_timelimited = None
        try:
            result_timelimited = BackendApi.tr_send_loginbonustimelimited(model_mgr, player, now)
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
        # 双六.
        result_sugoroku = BackendApi.tr_send_loginbonus_sugoroku(model_mgr, player, now)
        # ミッション.
        mission_executer = PanelMissionConditionExecuter()
        mission_executer.addTargetLoginBonus()
        BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
        
        BackendApi.tr_updatelogintime(model_mgr, player, is_pc, now=now)
        
        model_mgr.set_save(playerlogin)
        
        result.update(player=playerlogin, continuity=continuity_loginbonus, accessbonus=accessbonuslist, timelimited=result_timelimited, totallogin=total_loginbonus, comeback=comeback_mid_list, sugoroku=result_sugoroku)
        
        if PlayerCrossPromotion.is_session():
            BackendApi.update_player_cross_promotion(model_mgr, player.id, "total_login_count")
        return result
    
    @staticmethod
    def tr_send_loginbonustimelimited(model_mgr, player, now):
        """区間別ログインボーナスの付与.
        """
        resultlist = []
        
        logintime = DateTimeUtil.toLoginTime(now)
        day = logintime.day
        uid = player.id
        
        playertutorial = BackendApi.get_model(model_mgr, PlayerTutorial, uid, using=settings.DB_READONLY)
        masterlist = BackendApi.get_current_loginbonustimelimitedmaster_list(model_mgr, target_time=now, tutorialendtime=playertutorial.etime)
        
        # 日付固定のマスターID.
        fixation_midlist = []
        
        logindata_dict = BackendApi.get_logintimelimited_data_dict(model_mgr, uid, [master.id for master in masterlist])
        for master in masterlist:
            mid = master.id
            data_id = LoginBonusTimeLimitedData.makeID(uid, mid)
            if logindata_dict.get(mid) is None:
                logindata = LoginBonusTimeLimitedData.makeInstance(data_id)
                logindata.insert()
            logindata = LoginBonusTimeLimitedData.getByKeyForUpdate(data_id)
            if BackendApi.check_loginbonustimelimited_received(logindata, now):
                # 受取済み.
                continue
            
            result = {}
            
            if master.lbtype in Defines.LoginBonusTimeLimitedType.FIXATION_TYPES:
                # 日付固定の報酬.
                logindata.days = day
            else:
                # ログイン日数の報酬.
                logindata.days += 1
            logindata.lbtltime = now
            model_mgr.set_save(logindata)
            
            bonusmaster = BackendApi.get_loginbonustimelimiteddaysmaster(model_mgr, mid, logindata.days)
            if bonusmaster and bonusmaster.prizes:
                prizelist = BackendApi.get_prizelist(model_mgr, bonusmaster.prizes)
                BackendApi.tr_add_prize(model_mgr, uid, prizelist, master.textid)
                result.update(bonusmaster=bonusmaster)
                
                if master.lbtype == Defines.LoginBonusTimeLimitedType.FIXATION:
                    fixation_midlist.append(master.id)
            # ログ.
            model_mgr.set_save(UserLogLoginBonusTimeLimited.create(uid, mid, logindata.days))
            
            result.update(master=master, player=logindata)
            
            resultlist.append(result)
        
        if fixation_midlist:
            def writeEnd():
                # 演出用に受け取り情報を保存.
                redisdb = LoginBonusFixationDataHash.getDB()
                pipe = redisdb.pipeline()
                for mid in fixation_midlist:
                    LoginBonusFixationDataHash.create(uid, mid, day, now).save(pipe)
                pipe.execute()
            model_mgr.add_write_end_method(writeEnd)
        
        return resultlist
    
    @staticmethod
    def get_loginbonustimelimitedmaster_list(model_mgr, midlist, using=settings.DB_READONLY):
        """区間別ログインボーナスを取得.
        """
        master = BackendApi.get_model_list(model_mgr, LoginBonusTimeLimitedMaster, midlist, using=using)
        return master
    
    @staticmethod
    def get_loginbonustimelimitedmaster(model_mgr, mid, using=settings.DB_READONLY):
        """区間別ログインボーナスを取得.
        """
        master = BackendApi.get_model(model_mgr, LoginBonusTimeLimitedMaster, mid, using=using)
        return master
    
    @staticmethod
    def get_loginbonustimelimiteddaysmaster_by_idlist(model_mgr, midlist, using=settings.DB_READONLY):
        """区間別ログインボーナスの日別マスターデータを取得.
        """
        return BackendApi.get_model_list(model_mgr, LoginBonusTimeLimitedDaysMaster, midlist, using=using)
    
    @staticmethod
    def get_loginbonustimelimiteddaysmaster_by_id(model_mgr, mid, using=settings.DB_READONLY):
        """区間別ログインボーナスの日別マスターデータを取得.
        """
        return BackendApi.get_model(model_mgr, LoginBonusTimeLimitedDaysMaster, mid, using=using)
    
    @staticmethod
    def get_loginbonustimelimiteddaysmaster(model_mgr, mid, day, using=settings.DB_READONLY):
        """区間別ログインボーナスの日別マスターデータを取得.
        """
        key = LoginBonusTimeLimitedDaysMaster.makeID(mid, day)
        master = BackendApi.get_model(model_mgr, LoginBonusTimeLimitedDaysMaster, key, using=using)
        return master
    
    @staticmethod
    def get_loginbonustimelimiteddaysmaster_day_table_by_timelimitedmid(model_mgr, mid, using=settings.DB_READONLY):
        """同じくくりの区間別ログインボーナスの日別マスターIDを一括で取得.
        """
        client = OSAUtil.get_cache_client()
        key = 'get_loginbonustimelimiteddaysmaster_id_by_mid:%s' % mid
        
        table = client.get(key)
        if table is None:
            table = {}
            modellist = LoginBonusTimeLimitedDaysMaster.fetchValues(filters={'mid':mid}, using=using)
            model_mgr.set_got_models(modellist)
            
            for model in modellist:
                table[model.day] = model.id
            
            client.set(key, table)
        return table
    
    @staticmethod
    def get_current_totalloginbonusconfig(model_mgr, using=settings.DB_READONLY):
        """現在の累計ログインボーナス設定を取得.
        """
        return BackendApi.__get_current_eventconfig(model_mgr, TotalLoginBonusConfig, using=using)
    
    @staticmethod
    def update_totalloginbonusconfig(model_mgr, mid=None, stime=None, etime=None, mid_next=None, continuity_login=None):
        """現在の累計ログインボーナス設定を更新.
        """
        def tr():
            model_mgr = ModelRequestMgr()
            model = BackendApi.get_model(model_mgr, TotalLoginBonusConfig, TotalLoginBonusConfig.SINGLE_ID, get_instance=True)
            model.mid = mid if mid is not None else model.mid
            model.stime = stime or model.stime
            model.etime = etime or model.etime
            model.mid_next = mid_next if mid_next is not None else model.mid_next
            model.continuity_login = continuity_login if continuity_login is not None else model.continuity_login
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr, model
        model_mgr, model = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        return model
    
    @staticmethod
    def get_current_loginbonustimelimitedconfig(model_mgr, using=settings.DB_READONLY):
        """現在の区間別ログインボーナス設定を取得.
        """
        return BackendApi.__get_current_eventconfig(model_mgr, LoginBonusTimeLimitedConfig, using=using)
    
    @staticmethod
    def update_loginbonustimelimitedconfig(model_mgr, datalist):
        """現在の区間別ログインボーナス設定を更新.
        """
        def tr():
            model_mgr = ModelRequestMgr()
            model = BackendApi.get_model(model_mgr, LoginBonusTimeLimitedConfig, LoginBonusTimeLimitedConfig.SINGLE_ID, get_instance=True)
            
            model.formatData()
            for data in datalist:
                if isinstance(data, dict):
                    model.setData(**data)
                else:
                    model.setData(*data)
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr, model
        model_mgr, model = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        return model
    
    @staticmethod
    def __get_current_loginbonustimelimitedmaster_list(model_mgr, using, target_time, tutorialendtime, sugoroku):
        """現在の区間別ログインボーナスを取得.
        複数設定可能になったのでリストにする.
        """
        config = BackendApi.get_current_loginbonustimelimitedconfig(model_mgr, using)
        now = OSAUtil.get_now()
        target_time = target_time or now
        
        sugoroku = bool(sugoroku)
        # 期間内のログインボーナスだけ.
        data_dict = {}
        midlist = []
        for mid, data in config.getDataList():
            if sugoroku != bool(data.get('sugoroku')):
                continue
            elif not (data['stime'] <= target_time < data['etime']):
                continue
            elif tutorialendtime and data.get('beginer') and tutorialendtime < data['stime']:
                continue
            midlist.append(mid)
            data_dict[mid] = data
        
        if not data_dict:
            return []
        if sugoroku:
            masterlist = BackendApi.get_loginbonus_sugoroku_master_list(model_mgr, midlist, using=using)
        else:
            masterlist = BackendApi.get_loginbonustimelimitedmaster_list(model_mgr, midlist, using=using)
        masterlist.sort(key=lambda x:midlist.index(x.id))
        return masterlist
    
    @staticmethod
    def get_current_loginbonustimelimitedmaster_list(model_mgr, using=settings.DB_DEFAULT, target_time=None, tutorialendtime=None):
        """現在の区間別ログインボーナスを取得.
        複数設定可能になったのでリストにする.
        """
        return BackendApi.__get_current_loginbonustimelimitedmaster_list(model_mgr, using, target_time, tutorialendtime, sugoroku=False)
    
    @staticmethod
    def get_loginbonustimelimited_fixation_received_dates(uid, mid, min_time=None):
        """区間別ログインボーナスを受け取った日付.
        """
        return LoginBonusFixationDataHash.fetchAll(uid, mid, min_time) or {}
    
    #===========================================================
    # 双六ログインボーナス.
    @staticmethod
    def get_loginbonus_sugoroku_master_list(model_mgr, midlist, using=settings.DB_DEFAULT):
        """双六ログインボーナスのマスターデータを取得.
        """
        return BackendApi.get_model_list(model_mgr, LoginBonusSugorokuMaster, midlist, using=using)
    
    @staticmethod
    def get_loginbonus_sugoroku_master(model_mgr, mid, using=settings.DB_DEFAULT):
        """双六ログインボーナスのマスターデータを取得.
        """
        return BackendApi.get_model(model_mgr, LoginBonusSugorokuMaster, mid, using=using)
    
    @staticmethod
    def get_loginbonus_sugoroku_map_master_list(model_mgr, mapidlist, using=settings.DB_DEFAULT):
        """双六ログインボーナスのマップのマスターデータを複数取得.
        """
        return BackendApi.get_model_list(model_mgr, LoginBonusSugorokuMapMaster, mapidlist, using=using)
    
    @staticmethod
    def get_loginbonus_sugoroku_map_master(model_mgr, mapid, using=settings.DB_DEFAULT):
        """双六ログインボーナスのマップのマスターデータを取得.
        """
        return BackendApi.get_model(model_mgr, LoginBonusSugorokuMapMaster, mapid, using=using)
    
    @staticmethod
    def get_loginbonus_sugoroku_map_squares_master(model_mgr, mapid, number, using=settings.DB_DEFAULT):
        """双六ログインボーナスのマップ番号とマス番号からマス情報を取得.
        """
        return BackendApi.get_model(model_mgr, LoginBonusSugorokuMapSquaresMaster, LoginBonusSugorokuMapSquaresMaster.makeID(mapid, number), using=using)
    
    @staticmethod
    def get_loginbonus_sugoroku_map_squares_master_list_by_id(model_mgr, idlist, using=settings.DB_DEFAULT):
        """双六ログインボーナスのマス情報を取得.
        """
        return BackendApi.get_model_list(model_mgr, LoginBonusSugorokuMapSquaresMaster, idlist, using=using)
    
    @staticmethod
    def get_loginbonus_sugoroku_map_squares_master_by_mapid(model_mgr, mapid, loc_from=None, loc_to=None, using=settings.DB_DEFAULT):
        """双六ログインボーナスのマップ番号からマス情報を取得.
        """
        if LoginbonusSugorokuMapSquaresIdList.exists(mapid):
            squares_id_list = LoginbonusSugorokuMapSquaresIdList.get_squares_idlist(mapid)
            if loc_from or loc_to:
                id_from = LoginBonusSugorokuMapSquaresMaster.makeID(mapid, 1 if loc_from is None else loc_from)
                id_to = LoginBonusSugorokuMapSquaresMaster.makeID(mapid, 0xffffffff if loc_to is None else loc_to)
                squares_id_list = filter(lambda squares_id: id_from <= squares_id <= id_to, squares_id_list)
            modellist = BackendApi.get_model_list(model_mgr, LoginBonusSugorokuMapSquaresMaster, squares_id_list, using=using)
        else:
            modellist = LoginBonusSugorokuMapSquaresMaster.fetchValues(filters=dict(mid=mapid), using=using)
            LoginbonusSugorokuMapSquaresIdList.save(modellist)
            if loc_from or loc_to:
                id_from = LoginBonusSugorokuMapSquaresMaster.makeID(mapid, 1 if loc_from is None else loc_from)
                id_to = LoginBonusSugorokuMapSquaresMaster.makeID(mapid, 0xffffffff if loc_to is None else loc_to)
                modellist = filter(lambda model: id_from <= model.id <= id_to, modellist)
        modellist.sort(key=lambda x:x.number)
        return modellist
    
    @staticmethod
    def get_current_loginbonussugoroku_master_list(model_mgr, using=settings.DB_DEFAULT, target_time=None, tutorialendtime=None):
        """現在の双六ログインボーナスを取得.
        """
        return BackendApi.__get_current_loginbonustimelimitedmaster_list(model_mgr, using, target_time, tutorialendtime, sugoroku=True)
    
    @staticmethod
    def get_loginbonus_sugoroku_playerdata(model_mgr, uid, mid, using=settings.DB_DEFAULT):
        """双六ログインボーナスのプレイヤー情報.
        """
        return BackendApi.get_model(model_mgr, LoginBonusSugorokuPlayerData, LoginBonusSugorokuPlayerData.makeID(uid, mid), using=using)
    
    @staticmethod
    def get_loginbonus_sugoroku_playerdata_dict(model_mgr, uid, midlist, using=settings.DB_DEFAULT):
        """双六ログインボーナスのプレイヤー情報.
        """
        idlist = [LoginBonusSugorokuPlayerData.makeID(uid, mid) for mid in midlist]
        return BackendApi.get_model_dict(model_mgr, LoginBonusSugorokuPlayerData, idlist, using=using, key=lambda x:x.mid)
    
    @staticmethod
    def check_loginbonussugoroku_received(sugoroku_playerdata, now=None):
        """双六ログインボーナスを受け取り済みなのかを判定.
        """
        if sugoroku_playerdata and DateTimeUtil.judgeSameDays(sugoroku_playerdata.ltime, now):
            # 受取済み.
            return True
        return False
    
    @staticmethod
    def check_lead_loginbonus_sugoroku(model_mgr, uid, now=None):
        """双六ログインボーナスを受け取り済みなのかを判定.
        """
        now = now or OSAUtil.get_now()
        playertutorial = BackendApi.get_model(model_mgr, PlayerTutorial, uid, using=settings.DB_READONLY)
        masterlist = BackendApi.get_current_loginbonussugoroku_master_list(model_mgr, using=settings.DB_READONLY, target_time=now, tutorialendtime=playertutorial.etime)
        if not masterlist:
            return False
        midlist = [master.id for master in masterlist]
        logindata_dict = BackendApi.get_loginbonus_sugoroku_playerdata_dict(model_mgr, uid, midlist, using=settings.DB_READONLY)
        for master in masterlist:
            playerdata = logindata_dict.get(master.id)
            if BackendApi.check_loginbonussugoroku_received(playerdata, now):
                # 受取済み.
                continue
            elif playerdata:
                mapid = master.getMapIDByLap(playerdata.lap)
                squares_master = BackendApi.get_loginbonus_sugoroku_map_squares_master(model_mgr, mapid, playerdata.loc, using=settings.DB_READONLY)
                if squares_master.last:
                    mapmaster = BackendApi.get_loginbonus_sugoroku_map_master(model_mgr, mapid, using=settings.DB_READONLY)
                    if not mapmaster.prize:
                        # 最終マスにいて報酬が無いので対象外.
                        continue
            return True
        return False
    
    @staticmethod
    def tr_send_loginbonus_sugoroku(model_mgr, player, now, test=False):
        """双六ログインボーナスの付与.
        """
        uid = player.id
        # チュートリアル終了時間が欲しい.
        playertutorial = BackendApi.get_model(model_mgr, PlayerTutorial, uid, using=settings.DB_READONLY)
        # 開催中の双六ログインボーナス.
        masterlist = BackendApi.get_current_loginbonussugoroku_master_list(model_mgr, target_time=now, tutorialendtime=playertutorial.etime)
        masterlist.sort(key=lambda x:x.id)
        # ユーザーデータ.
        idlist = [LoginBonusSugorokuPlayerData.makeID(uid, master.id) for master in masterlist]
        logindata_dict = BackendApi.get_model_dict(model_mgr, LoginBonusSugorokuPlayerData, idlist, key=lambda x:x.mid)
        # 受け取った双六.
        received = []
        # 各すごろくの進行.
        for master in masterlist:
            mid = master.id
            data_id = LoginBonusSugorokuPlayerData.makeID(uid, mid)
            if logindata_dict.get(mid) is None:
                logindata = LoginBonusSugorokuPlayerData.makeInstance(data_id)
                logindata.insert()
            else:
                logindata = LoginBonusSugorokuPlayerData.getByKeyForUpdate(data_id)
                # 受け取り判定.
                if BackendApi.check_loginbonussugoroku_received(logindata, now):
                    # 受取済み.
                    continue
            # 受け取り時間の記録.
            logindata.ltime = now
            model_mgr.set_save(logindata)
            # 移動前の位置.
            loc_pre = logindata.loc
            map_pre = master.getMapIDByLap(loc_pre)
            # 双六実行モデル.
            sugoroku = Sugoroku(BackendApi, model_mgr, master, logindata)
            # 双六実行.
            result = sugoroku.play(test=test)
            if result is None:
                continue
            # 報酬配布.
            if result.prizes:
                for textid,prizelist in result.prizes.items():
                    BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
            # 演出用の結果設定.
            squares_id_list = [LoginBonusSugorokuMapSquaresMaster.makeID(map_pre, loc_pre)] + [squares_master.id for squares_master in result.squares_master_list]
            logindata.setResult(result.number, squares_id_list)
            # ログ.
            model_mgr.set_save(UserLogLoginbonusSugoroku.create(uid, result.number, squares_id_list))
            # 受け取ったことを記録.
            received.append(master)
        return received
    
    #===========================================================
    # カムバックキャンペーン.
    @staticmethod
    def get_comebackcampaignmaster_list(model_mgr, midlist, using=settings.DB_READONLY):
        """カムバックキャンペーンのマスターデータを取得.
        """
        return BackendApi.get_model_list(model_mgr, ComeBackCampaignMaster, midlist, using=using)
    
    @staticmethod
    def get_comebackcampaignmaster(model_mgr, mid, using=settings.DB_READONLY):
        """カムバックキャンペーンのマスターデータを取得.
        """
        return BackendApi.get_model(model_mgr, ComeBackCampaignMaster, mid, using=using)
    
    @staticmethod
    def get_comebackcampaign_userdata(model_mgr, uid, mid, using=settings.DB_READONLY):
        """カムバックキャンペーンのユーザデータを取得.
        """
        return BackendApi.get_model(model_mgr, ComeBackCampaignData, ComeBackCampaignData.makeID(uid, mid), using=using)
    
    @staticmethod
    def get_current_comebackcampaignconfig(model_mgr, using=settings.DB_READONLY):
        """現在のカムバックキャンペーン設定を取得.
        """
        return BackendApi.__get_current_eventconfig(model_mgr, CurrentComeBackCampaignConfig, using=using)
    
    @staticmethod
    def update_comebackcampaignconfig(model_mgr, datalist):
        """現在のカムバックキャンペーン設定を更新.
        datalistは{'mid':マスターID,'stime':開始時間,'etime':終了時間}のリスト
        """
        def tr():
            model_mgr = ModelRequestMgr()
            model = BackendApi.get_model(model_mgr, CurrentComeBackCampaignConfig, CurrentComeBackCampaignConfig.SINGLE_ID, get_instance=True)
            
            model.datalist = []
            for data in datalist:
                if isinstance(data, dict):
                    model.setData(**data)
                else:
                    model.setData(*data)
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr, model
        model_mgr, model = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        return model
    
    @staticmethod
    def get_current_comebackcampaignmaster_list(model_mgr, using=settings.DB_DEFAULT, target_time=None):
        """現在のカムバックキャンペーンを取得.
        複数設定可能になったのでリストにする.
        """
        config = BackendApi.get_current_comebackcampaignconfig(model_mgr, using)
        now = OSAUtil.get_now()
        target_time = target_time or now
        
        # 期間内のキャンペーンだけ.
        midlist = [mid for mid, data in config.getDataList() if data['stime'] <= target_time < data['etime']]
        if not midlist:
            return []
        
        masterlist = BackendApi.get_comebackcampaignmaster_list(model_mgr, midlist, using=using)
        masterlist.sort(key=lambda x:midlist.index(x.id))
        return masterlist
    
    
    @staticmethod
    def tr_send_comebackcampaign_prize(model_mgr, uid, lbtime_pre, lbtime_post):
        """カムバックキャンペーン報酬受取.
        """
        # 開催中のマスター.
        masterlist = BackendApi.get_current_comebackcampaignmaster_list(model_mgr, target_time=lbtime_post)
        
        interval = DateTimeUtil.toLoginTime(lbtime_post) - DateTimeUtil.toLoginTime(lbtime_pre)
        
        received_midlist = []
        for master in masterlist:
            is_comeback = master.interval <= interval.days
            mid = master.id
            ins_id = ComeBackCampaignData.makeID(uid, mid)
            userdata = ComeBackCampaignData.getByKey(ins_id)
            if userdata is None:
                if not is_comeback:
                    # カムバック状態ではなく,カムバック期間中でもない.
                    continue
                userdata = ComeBackCampaignData.makeInstance(ins_id)
                userdata.days = 0
                userdata.comeback = True
            elif master.get_prize(userdata.days) is None:
                # 日付をオーバーしている.
                continue
            else:
                userdata = ComeBackCampaignData.getByKeyForUpdate(ins_id)
                if not userdata.comeback:
                    # 報酬受取中ではない.
                    if not is_comeback:
                        # カムバック状態ではない.
                        continue
                    userdata.days = 0
                elif is_comeback:
                    # 初日からやり直し.
                    userdata.days = 0
                userdata.comeback = True
            
            # 日数を加算.
            userdata.days += 1
            
            # 報酬がない.
            prizeidlist = master.get_prize(userdata.days)
            if prizeidlist is None:
                # 報酬がない.
                continue
            
            # 報酬を付与.
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, master.prizetext)
            
            model_mgr.set_save(userdata)
            
            received_midlist.append(mid)
            
            # ログ.
            model_mgr.set_save(UserLogComeBack.create(uid, mid, userdata.days))
        
        return received_midlist
    
    #===========================================================
    # チュートリアル.
    @staticmethod
    def get_tutorialconfig(model_mgr, ptype, using=settings.DB_DEFAULT):
        """チュートリアルの設定を取得.
        """
        model = model_mgr.get_model(TutorialConfig, ptype, using=using)
        if model is None:
            raise CabaretError(u'チュートリアルの設定がありません. タイプ=%s' % ptype, CabaretError.Code.INVALID_MASTERDATA)
        return model
    
    @staticmethod
    def get_tutorialcomposition_material(model_mgr, ptype, using=settings.DB_DEFAULT):
        """チュートリアルの教育で使う素材カード.
        """
        config = BackendApi.get_tutorialconfig(model_mgr, ptype, using=using)
#        mid = config.compositioncard
        mid = config.scoutdropcard
        master = BackendApi.get_cardmasters([mid], model_mgr, using=using).get(mid, None)
        if master is None:
            raise CabaretError(u'チュートリアルで使用するキャストが見つかりません. タイプ=%s card=%s' % (ptype, mid), CabaretError.Code.INVALID_MASTERDATA)
        card = BackendApi.create_card_by_master(master)
        return CardSet(card, master)
    
    @staticmethod
    def get_tutorialevolution_material(model_mgr, uid, using=settings.DB_DEFAULT):
        """チュートリアルのハメ管理で使う素材カード.
        """
        leader = BackendApi.get_leaders([uid], model_mgr, using=using).get(uid, None)
        if leader is None:
            raise CabaretError(u'リーダーが見つかりません. uid=%s' % uid, CabaretError.Code.INVALID_MASTERDATA)
        card = BackendApi.create_card_by_master(leader.master)
        return CardSet(card, leader.master)
    
    @staticmethod
    def get_tutorial_scoutdropcard(model_mgr, ptype, using=settings.DB_DEFAULT):
        """チュートリアルのスカウトでドロップするカード.
        """
        config = BackendApi.get_tutorialconfig(model_mgr, ptype, using=using)
        mid = config.scoutdropcard
        master = BackendApi.get_cardmasters([mid], model_mgr, using=using).get(mid, None)
        if master is None:
            raise CabaretError(u'チュートリアルで使用するカードが見つかりません. タイプ=%s card=%s' % (ptype, mid), CabaretError.Code.INVALID_MASTERDATA)
        card = BackendApi.create_card_by_master(master)
        return CardSet(card, master)
    
    @staticmethod
    def get_tutorial_area(model_mgr, ptype, using=settings.DB_DEFAULT):
        """チュートリアルのエリア.
        """
        config = BackendApi.get_tutorialconfig(model_mgr, ptype, using=using)
        mid = config.scoutarea
        master = BackendApi.get_area(model_mgr, mid, using=using)
        if master is None:
            raise CabaretError(u'チュートリアルで使用するエリアが見つかりません. タイプ=%s area=%s' % (ptype, mid), CabaretError.Code.INVALID_MASTERDATA)
        return master
    
    @staticmethod
    def get_tutorial_scout(model_mgr, ptype, using=settings.DB_DEFAULT):
        """チュートリアルのスカウト.
        """
        config = BackendApi.get_tutorialconfig(model_mgr, ptype, using=using)
        scoutidlist = BackendApi.get_scoutidlist_by_area(model_mgr, config.scoutarea, using=using)
        scoutlist = BackendApi.get_scouts(model_mgr, scoutidlist, using=using)
        if len(scoutlist) == 0:
            raise CabaretError(u'チュートリアルで使用するスカウトが見つかりません. タイプ=%s area=%s' % (ptype, config.scoutarea), CabaretError.Code.INVALID_MASTERDATA)
        scoutlist.sort(key=operator.attrgetter('id'))
        return scoutlist[0]
    
    @staticmethod
    def get_tutorial_scoutresult(model_mgr, ptype, cnt=1, using=settings.DB_DEFAULT):
        """スカウトで手に入るお金と経験値.
        """
        scout = BackendApi.get_tutorial_scout(model_mgr, ptype, using=using)
        return scout.goldmin * cnt, scout.exp * cnt
    
    @staticmethod
    def get_tutorial_treasure(model_mgr, ptype, using=settings.DB_DEFAULT):
        """チュートリアルの宝箱.
        """
        config = BackendApi.get_tutorialconfig(model_mgr, ptype, using=using)
        mid = config.treasure
        return BackendApi.get_treasuremaster(model_mgr, Defines.TreasureType.TUTORIAL_TREASURETYPE, mid, using=using)
    
    @staticmethod
    def get_tutorial_memories(model_mgr, ptype, using=settings.DB_DEFAULT):
        """チュートリアルで閲覧する思い出アルバム.
        """
        config = BackendApi.get_tutorialconfig(model_mgr, ptype, using=using)
        mid = config.memories
        return BackendApi.get_memoriesmasters([mid], arg_model_mgr=model_mgr, using=using).get(mid)
    
    @staticmethod
    def get_tutorial_pcmemories(model_mgr, ptype, using=settings.DB_DEFAULT):
        """チュートリアルで閲覧する思い出アルバム(PC).
        """
        config = BackendApi.get_tutorialconfig(model_mgr, ptype, using=using)
        mid = config.pcmemories
        return BackendApi.get_memoriesmasters([mid], arg_model_mgr=model_mgr, using=using).get(mid)
    
    @staticmethod
    def tutorial_evolution(model_mgr, cardset, materialcard, using=settings.DB_DEFAULT):
        """チュートリアルでの進化.
        """
        materialcard_takeover = materialcard.get_evolution_takeover()
        
        master = cardset.master
        
        card = copy(cardset.card)
        post_cardset = CardSet(card, master)
        
        # 最大まで進化.
        evolution_cardmaster_list = []
        for hklevel in xrange(master.hklevel + 1, Defines.HKLEVEL_MAX + 1):
            evolution_cardmaster = BackendApi.get_cardmaster_by_albumhklevel(model_mgr, master.album, hklevel, using=using)
            if evolution_cardmaster:
                # パラメータの引き継ぎ.
                post_cardset.card.takeover += post_cardset.get_evolution_takeover() + materialcard_takeover
                post_cardset.card.mid = evolution_cardmaster.id
                post_cardset = CardSet(post_cardset.card, evolution_cardmaster)
                evolution_cardmaster_list.append(evolution_cardmaster)
        
        return post_cardset, evolution_cardmaster_list
    
    @staticmethod
    def get_tutorial_prizelist(model_mgr, ptype, using=settings.DB_DEFAULT):
        """チュートリアル完了報酬.
        """
        config = BackendApi.get_tutorialconfig(model_mgr, ptype, using=using)
        return BackendApi.get_prizelist(model_mgr, config.prizes, using=using)

    #===========================================================
    # レベルアップ達成ボーナス.
    @staticmethod
    def get_levelupbonus_master(model_mgr, version, using=settings.DB_DEFAULT):
        client = localcache.Client()
        key = "levelupbonus:{}".format(version)
        midlist = client.get(key)

        if midlist is None:
            masterlist = LevelUpBonusMaster.fetchValues(filters={'version': version}, using=using)
            masterlist.sort(key=(lambda x: x.level))
            midlist = [master.id for master in masterlist]
            client.set(key, midlist)
        return midlist

    @staticmethod
    def get_levelupbonus_data(handler, model_mgr, playdata_last_prize_level, version, using=settings.DB_DEFAULT):
        midlist = BackendApi.get_levelupbonus_master(model_mgr, version, using=using)
        levelupbonus_masters = BackendApi.get_model_list(model_mgr, LevelUpBonusMaster, midlist, using=using)
        itype = Defines.ItemType
        gtype = Defines.GachaConsumeType.GachaTicketType
        missions = []

        def create_data(name, thumb, num, unit, icon=None, rare=None):
            data = {
                'name': name,
                'thumbUrl': handler.makeAppLinkUrlImg(thumb),
                'icon': icon,
                'rare': rare,
                'sep': ' ',
                'num': num,
                'unit': unit,
            }
            return data

        def _ticket(ticket, num):
            name = itype.NAMES[ticket]
            thumb = ItemUtil.makeThumbnailUrlMiddleByDBString(itype.THUMBNAIL[ticket])
            num = num
            unit = itype.UNIT[ticket]
            return (name, thumb, num, unit)

        for levelupbonus_master in levelupbonus_masters:
            prizemasters = BackendApi.get_model_list(model_mgr, PrizeMaster, levelupbonus_master.prize_id, using=using)
            mission = {}
            datalist = []
            for prize in prizemasters:
                if 0 < prize.rareoverticket:
                    datalist.append(create_data(*_ticket(itype.RAREOVERTICKET, prize.rareoverticket)))
                if 0 < prize.ticket:
                    datalist.append(create_data(*_ticket(itype.TRYLUCKTICKET, prize.ticket)))
                if 0 < prize.memoriesticket:
                    datalist.append(create_data(*_ticket(itype.MEMORIESTICKET, prize.memoriesticket)))
                if 0 < prize.gachaticket:
                    datalist.append(create_data(*_ticket(itype.GACHATICKET, prize.gachaticket)))
                if 0 < prize.additional_ticket_id and 0 < prize.additional_ticket_num:
                    name = gtype.NAMES[prize.additional_ticket_id]
                    thumb = ItemUtil.makeThumbnailUrlMiddleByDBString(gtype.THUMBNAIL[prize.additional_ticket_id])
                    num = prize.additional_ticket_num
                    unit = itype.UNIT[itype.ADDITIONAL_GACHATICKET]
                    datalist.append(create_data(name, thumb, num, unit))
                if 0 < prize.itemid and 0 < prize.itemnum:
                    itemmaster = BackendApi.get_itemmaster(model_mgr, prize.itemid, using=using)
                    thumb = ItemUtil.makeThumbnailUrlMiddleByDBString(itemmaster.thumb)
                    unit = itemmaster.unit
                    datalist.append(create_data(itemmaster.name, thumb, prize.itemnum, unit))
                if 0 < prize.cardid and 0 < prize.cardnum:
                    carddict = BackendApi.get_cardmasters([prize.cardid])
                    card = carddict.get(prize.cardid)
                    name = card.name
                    thumb = CardUtil.makeThumbnailUrlIcon(card)
                    icon = handler.makeAppLinkUrlImg(Defines.CharacterType.ICONS[card.ctype])
                    rare = Defines.Rarity.NAMES.get(card.rare)
                    unit = Defines.CardKind.UNIT.get(card.ckind)
                    datalist.append(create_data(name, thumb, prize.cardnum, unit=unit, icon=icon, rare=rare))
            mission['items'] = datalist
            mission['name'] = 'キャバ王Lv{}'.format(levelupbonus_master.level)
            mission['cleared'] = True if levelupbonus_master.level <= playdata_last_prize_level else False
            
            missions.append(mission)
        return missions

    #===========================================================
    # 宝箱.
    @staticmethod
    def _save_treasureidlist(model_mgr, uid, treasure_type, using=settings.DB_DEFAULT, pipe=None):
        """宝箱ID一覧を更新.
        """
        do_execute = False
        if pipe is None:
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            do_execute = True
        
        # 先に削除.
        pipe.delete(TreasureListSet.makeKey(uid, treasure_type))
        
        model_cls = TreasureUtil.get_model_cls(treasure_type)
        treasurelist = model_cls.fetchValues(filters={'uid':uid, 'etime__gt':OSAUtil.get_now()}, order_by='ctime', using=using)
        
        idlist = []
        for treasure in treasurelist:
            TreasureListSet.create(uid, treasure_type, treasure.id, treasure.ctime).save(pipe)
            idlist.append(treasure.id)
        if do_execute:
            pipe.execute()
        model_mgr.set_got_models(treasurelist)
        return idlist
    
    @staticmethod
    def add_treasure(uid, treasureset, pipe=None):
        TreasureListSet.create(uid, treasureset.get_type(), treasureset.id, treasureset.treasure.ctime).save(pipe)
        
    
    @staticmethod
    def remove_treasure(uid, treasure_type, treasureid, pipe=None):
        TreasureListSet.create(uid, treasure_type, treasureid).delete(pipe)
    
    @staticmethod
    def get_public_treasuretablemaster_list(model_mgr, treasure_type, using=settings.DB_DEFAULT):
        """宝箱テーブルのマスターデータ.
        """
        now = OSAUtil.get_now()
        model_cls = TreasureUtil.get_table_cls(treasure_type)
        masterlist = model_mgr.get_mastermodel_all(model_cls, using=using)
        return [master for master in masterlist if BackendApi.check_schedule(model_mgr, master.schedule, using=using, now=now)]
    
    @staticmethod
    def get_public_treasuremaster_idlist(model_mgr, treasure_type, using=settings.DB_DEFAULT):
        tablemaster_list = BackendApi.get_public_treasuretablemaster_list(model_mgr, treasure_type, using)
        midlist = []
        for tablemaster in tablemaster_list:
            midlist.extend(tablemaster.table)
        return midlist
    
    @staticmethod
    def get_treasuremaster_list(model_mgr, treasure_type, midlist, using=settings.DB_DEFAULT):
        """宝箱のマスターデータ(複数).
        """
        model_cls = TreasureUtil.get_master_cls(treasure_type)
        return BackendApi.get_model_list(model_mgr, model_cls, midlist, using=using)
    
    @staticmethod
    def get_treasuremaster_dict(model_mgr, treasure_type, midlist, using=settings.DB_DEFAULT):
        """宝箱のマスターデータ(dict).
        """
        model_cls = TreasureUtil.get_master_cls(treasure_type)
        return BackendApi.get_model_dict(model_mgr, model_cls, midlist, using=using)
    
    @staticmethod
    def get_treasuremaster(model_mgr, treasure_type, mid, using=settings.DB_DEFAULT):
        """宝箱のマスターデータ(単体).
        """
        model_cls = TreasureUtil.get_master_cls(treasure_type)
        return BackendApi.get_model(model_mgr, model_cls, mid, using=using)
    
    @staticmethod
    def get_treasureset_list(model_mgr, treasure_type, treasureidlist, using=settings.DB_DEFAULT, forupdate=False, deleted=False):
        """宝箱の所持情報を取得.
        """
        if deleted:
            model_cls = TreasureUtil.get_opened_cls(treasure_type)
        else:
            model_cls = TreasureUtil.get_model_cls(treasure_type)
        
        if forupdate:
            treasurelist = model_cls.fetchByKeyForUpdate(treasureidlist)
        else:
            treasurelist = BackendApi.get_model_list(model_mgr, model_cls, treasureidlist, using=using)
        
        if not treasurelist:
            return treasurelist
        
        midlist = list(set([treasure.mid for treasure in treasurelist]))
        master_dict = BackendApi.get_treasuremaster_dict(model_mgr, treasure_type, midlist, using)
        
        modelset_cls = TreasureUtil.get_modelset_cls(treasure_type)
        treasuresetlist = [modelset_cls(treasure, master_dict[treasure.mid]) for treasure in treasurelist]
        
        return treasuresetlist
    
    @staticmethod
    def get_treasure(model_mgr, treasure_type, treasureid, using=settings.DB_DEFAULT, forupdate=False, deleted=False):
        """宝箱の所持情報を取得(単体).
        """
        if deleted:
            model_cls = TreasureUtil.get_opened_cls(treasure_type)
        else:
            model_cls = TreasureUtil.get_model_cls(treasure_type)
        
        if forupdate:
            treasure = model_cls.getByKeyForUpdate(treasureid)
        else:
            treasure = BackendApi.get_model(model_mgr, model_cls, treasureid, using=using)
        
        if treasure is None:
            return None
        
        master = BackendApi.get_treasuremaster(model_mgr, treasure_type, treasure.mid, using=using)
        modelset_cls = TreasureUtil.get_modelset_cls(treasure_type)
        return modelset_cls(treasure, master)
    
    @staticmethod
    def get_treasure_idlist(model_mgr, treasure_type, uid, offset=0, limit=-1, using=settings.DB_DEFAULT):
        """宝箱の所持情報を取得.
        """
        if not TreasureListSet.exists(uid, treasure_type):
            BackendApi._save_treasureidlist(model_mgr, uid, treasure_type, using=using)
        return [model.treasureid for model in TreasureListSet.fetch(uid, treasure_type, offset, limit)]
    
    @staticmethod
    def get_treasure_list(model_mgr, treasure_type, idlist, using=settings.DB_DEFAULT):
        """宝箱の所持情報を取得.
        """
        model_cls = TreasureUtil.get_model_cls(treasure_type)
        return BackendApi.get_model_list(model_mgr, model_cls, idlist, using=using)
    
    @staticmethod
    def get_treasure_num(model_mgr, treasure_type, uid, using=settings.DB_DEFAULT):
        """宝箱の所持数を取得.
        """
        if not TreasureListSet.exists(uid, treasure_type):
            BackendApi._save_treasureidlist(model_mgr, uid, treasure_type, using=using)
        return TreasureListSet.get_num(uid, treasure_type) or 0
    
    @staticmethod
    def check_treasure_openable(model_mgr, player, treasure_type, using=settings.DB_DEFAULT):
        """宝箱を開けられるか
        """
        if player.cardlimit <= BackendApi.get_cardnum(player.id, model_mgr, using=using):
            return False
        elif treasure_type == Defines.TreasureType.GOLD:
            if player.goldkey < 1:
                return False
        elif treasure_type == Defines.TreasureType.SILVER:
            if player.silverkey < 1:
                return False
        else:
            pass
        return True
    
    @staticmethod
    def get_treasure_key_num(model_mgr, uid, ttype, using=settings.DB_DEFAULT):
        """カギの所持数.
        """
        player = BackendApi.get_model(model_mgr, PlayerKey, uid, using=using)
        if not player:
            return 0
        elif ttype == Defines.TreasureType.GOLD:
            return player.goldkey
        elif ttype == Defines.TreasureType.SILVER:
            return player.silverkey
        return 0
    
    @staticmethod
    def tr_consume_treasure_key(model_mgr, uid, ttype, num=1):
        """カギの消費.
        """
        table = {
            Defines.TreasureType.GOLD : BackendApi.tr_add_goldkey,
            Defines.TreasureType.SILVER : BackendApi.tr_add_silverkey,
        }
        func = table.get(ttype, None)
        if func:
            return func(model_mgr, uid, -num)
        return None
    
    @staticmethod
    def tr_open_treasure(model_mgr, uid, ttype, treasureidlist):
        """宝箱の中身をプレゼントに移す.
        """
        treasuresetlist = BackendApi.get_treasureset_list(model_mgr, ttype, treasureidlist)
        if not treasuresetlist:
            treasureset_deleted = BackendApi.get_treasureset_list(model_mgr, ttype, treasureidlist, deleted=True)
            if treasureset_deleted:
                for treasureset in treasureset_deleted:
                    if uid != treasureset.treasure.uid:
                        raise CabaretError(u'宝箱のデータが存在しません', CabaretError.Code.NOT_DATA)
                raise CabaretError(u'取得済みです', CabaretError.Code.ALREADY_RECEIVED)
            else:
                raise CabaretError(u'宝箱のデータが存在しません', CabaretError.Code.NOT_DATA)
        for ts in treasuresetlist:
            if uid != ts.treasure.uid:
                raise CabaretError(u'宝箱のデータが不整合です', CabaretError.Code.ILLEGAL_ARGS)
        
        treasuresetlist = BackendApi.get_treasureset_list(model_mgr, ttype, treasureidlist, forupdate=True)
        
        # ちょっとずれるかもしれないけど大丈夫なはず.
        key_num = BackendApi.get_treasure_key_num(model_mgr, uid, ttype)
        
        # 鍵を減らす.
        treasure_num = len(treasuresetlist)
        BackendApi.tr_consume_treasure_key(model_mgr, uid, ttype, treasure_num)
        
        presentlist_all = []
        for treasureset in treasuresetlist:
            # プレゼントBOXに中身を預ける.
            treasuremaster = treasureset.master
            fromid = 0
            textid = Defines.TextMasterID.TREASURE_BOX
            presentlist = BackendApi.create_present(model_mgr, fromid, uid, treasuremaster.itype, treasuremaster.ivalue1, treasuremaster.ivalue2, textid)
            
            # 開封した宝箱のレコード.
            model_opened = TreasureUtil.createOpenedTreasure(treasureset.treasure)
            model_mgr.set_save(model_opened)
            
            # ログ.
            key_num -= 1
            model_mgr.set_save(UserLogTreasureOpen.create(uid, ttype, treasuremaster.id, key_num))
            
            # 宝箱を削除する.
            model_mgr.set_delete(treasureset.treasure)
            
            presentlist_all.extend(presentlist)
        
        # ミッション.
        mission_executer = PanelMissionConditionExecuter()
        if ttype == Defines.TreasureType.GOLD:
            mission_executer.addTargetOpenTreasureGold(treasure_num)
        elif ttype == Defines.TreasureType.SILVER:
            mission_executer.addTargetOpenTreasureSilver(treasure_num)
        elif ttype == Defines.TreasureType.BRONZE:
            mission_executer.addTargetOpenTreasureBronze(treasure_num)
        BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
        
        # 書き込み後の処理.
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            for present in presentlist_all:
                BackendApi.add_present(uid, present, pipe=pipe)
            for treasureset in treasuresetlist:
                BackendApi.remove_treasure(uid, ttype, treasureset.treasure.id, pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
        
        return treasuresetlist
    
    @staticmethod
    def choice_treasure(model_mgr, treasure_type, using=settings.DB_DEFAULT):
        """宝箱を選ぶ.
        """
        midlist = BackendApi.get_public_treasuremaster_idlist(model_mgr, treasure_type, using=using)
        
        master_cls = TreasureUtil.get_master_cls(treasure_type)
        master_dict = BackendApi.get_model_dict(model_mgr, master_cls, midlist, using=using)
        probability_total = 0
        treasuremasterlist = []
        for mid in midlist:
            treasuremaster = master_dict.get(mid)
            if not treasuremaster or treasuremaster.probability < 1:
                continue
            probability_total += treasuremaster.probability
            treasuremasterlist.append(treasuremaster)
        
        v = randint(0, max(0, probability_total - 1))
        for treasuremaster in treasuremasterlist:
            v -= treasuremaster.probability
            if v < 0:
                return treasuremaster
        return None
    
    @staticmethod
    def tr_add_treasure(model_mgr, uid, treasure_type, mid):
        """宝箱を追加.
        """
        modelset_cls = TreasureUtil.get_modelset_cls(treasure_type)
        model_cls = TreasureUtil.get_model_cls(treasure_type)
        
        master = BackendApi.get_treasuremaster(model_mgr, treasure_type, mid)
        if master is None:
            raise CabaretError(u'宝箱が存在しません', CabaretError.Code.INVALID_MASTERDATA)
        
        def treasur_saved(ins):
            # ログ.
            UserLogTreasureGet.create(uid, treasure_type, ins.id).insert()
            #model_mgr.set_save(UserLogTreasureGet.create(uid, treasure_type, treasureset.master.id))
        
        # データベース書き込み.
        model = model_cls()
        model.uid = uid
        model.mid = mid
        model.ctime = OSAUtil.get_now()
        model.etime = model.ctime + datetime.timedelta(seconds=Defines.TREASURE_TIMELIMIT)
        model_mgr.set_save(model, saved_task=treasur_saved)
        
        treasureset = TreasureUtil.get_modelset_cls(treasure_type)(model, master)
        
        # 書き込み後のタスクを設定.
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            BackendApi.add_treasure(uid, treasureset, pipe)
            pipe.execute()
        
        model_mgr.add_write_end_method(writeEnd)
        
        return modelset_cls(model, master)
    
    @staticmethod
    def make_treasureiteminfo_list(handler, treasuremasterlist):
        """宝箱の中身一覧情報.
        """
        model_mgr = handler.getModelMgr()
        
        treasuremasterlist.sort(key=lambda x:x.priority, reverse=True)
        
        presentlist = []
        nums = []
        for treasuremaster in treasuremasterlist:
            arr = BackendApi.create_present(model_mgr, 0, 0, treasuremaster.itype, treasuremaster.ivalue1, treasuremaster.ivalue2, using=settings.DB_READONLY, do_set_save=False)
            presentlist.append(arr[0])
            if treasuremaster.itype in [Defines.ItemType.GOLD, Defines.ItemType.GACHA_PT]:
                nums.append(treasuremaster.ivalue2)
            else:
                nums.append(len(arr))
        
        presentsetlist = PresentSet.presentToPresentSet(model_mgr, presentlist, using=settings.DB_READONLY)
        
        return [Objects.treasureitem(handler, presentset, nums[i]) for i, presentset in enumerate(presentsetlist)]
    
    @staticmethod
    def get_treasuretype_list_overlimit(model_mgr, uid, using=settings.DB_DEFAULT):
        """所持数が限界の宝箱タイプ.
        """
        overlimit_treasure_list = []
        for treasure_type in Defines.TreasureType.NAMES.keys():
            treasure_num = BackendApi.get_treasure_num(model_mgr, treasure_type, uid, using=using)
            if Defines.TreasureType.POOL_LIMIT.get(treasure_type, 0) <= treasure_num:
                overlimit_treasure_list.append(treasure_type)
        return overlimit_treasure_list
    
    #===========================================================
    # 秘宝.
    @staticmethod
    def get_trademaster(model_mgr, mid, using=settings.DB_DEFAULT):
        """秘宝交換レート取得(単体).
        """
        trademaster = BackendApi.get_model(model_mgr, TradeMaster, mid, using=using)
        return trademaster
    
    @staticmethod
    def get_trademaster_all(model_mgr, using=settings.DB_DEFAULT):
        """秘宝交換レート取得(全て).
        """
        return model_mgr.get_mastermodel_all(TradeMaster, using=using)
    
    @staticmethod
    def get_tradeplayerdata_dict(model_mgr, uid, midlist, using=settings.DB_DEFAULT):
        """秘宝交換プレイヤーデータ.
        """
        idlist = [TradePlayerData.makeID(uid, mid) for mid in midlist]
        return BackendApi.get_model_dict(model_mgr, TradePlayerData, idlist, using=using, key=lambda x:x.mid)
    
    @staticmethod
    def get_tradeplayerdata(model_mgr, uid, mid, using=settings.DB_DEFAULT):
        """秘宝交換プレイヤーデータ.
        """
        return BackendApi.get_tradeplayerdata_dict(model_mgr, uid, [mid], using).get(mid)
    
    @staticmethod
    def get_trade_resettime(model_mgr, using=settings.DB_DEFAULT):
        """秘宝交換リセット時間.
        """
        model = BackendApi.get_model(model_mgr, TradeResetTime, TradeResetTime.SINGLE_ID, using=using)
        if model is None:
            model = BackendApi.update_trade_resettime(model_mgr, OSAUtil.get_datetime_min())
        return model
    
    @staticmethod
    def update_trade_resettime(model_mgr, resettime):
        """秘宝交換リセット時間を更新.
        """
        def tr(resettime):
            model_mgr = ModelRequestMgr()
            ins = TradeResetTime.makeInstance(TradeResetTime.SINGLE_ID)
            ins.resettime = resettime
            model_mgr.set_save(ins)
            model_mgr.write_all()
            return model_mgr, ins
        model_mgr_w, ins = db_util.run_in_transaction(tr, resettime)
        model_mgr_w.write_end()
        
        model_mgr.set_got_models([ins])
        
        return ins
    
    @staticmethod
    def get_trade_cnt(model_mgr, trademaster, playdata, using=settings.DB_DEFAULT):
        """期間中の秘宝交換回数.
        """
        if playdata is None:
            return 0
        
        now = OSAUtil.get_now()
        is_reset = False
        if trademaster.reset_stock_monthly and playdata.ltime.strftime('%Y%m') != now.strftime('%Y%m'):
            is_reset = True
        else:
            starttime, endtime = None, None
            if trademaster.schedule:
                schedulemaster = BackendApi.get_schedule_master(model_mgr, trademaster.schedule, using=settings.DB_READONLY)
                starttime, endtime = BackendApi.get_schedule_start_end_time(schedulemaster)
                
                if starttime and endtime and starttime <= playdata.ltime < endtime:
                    pass
                else:
                    is_reset = True
        if not is_reset:
            model_resettime = BackendApi.get_trade_resettime(model_mgr, using=settings.DB_READONLY)
            if model_resettime.resettime <= now and playdata.ltime < model_resettime.resettime:
                # リセットされた and リセット前に受け取った.
                is_reset = True
        return 0 if is_reset else playdata.cnt
    
    @staticmethod
    def tr_trade_item(model_mgr, player, trademaster, confirmkey, num):
        """秘宝交換.
        """
        now = BackendApi.check_schedule_error_or_nowtime(model_mgr, trademaster.schedule)
        uid = player.id

        # 重複確認.
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        
        # 在庫数の確認と更新.
        if 0 < trademaster.stock:
            stime, etime = None, None
            if trademaster.schedule:
                schedulemaster = BackendApi.get_schedule_master(model_mgr, trademaster.schedule)
                stime, etime = BackendApi.get_schedule_start_end_time(schedulemaster)
            
            model_resettime = BackendApi.get_trade_resettime(model_mgr)
            
            def forUpdatePlayerData(model, inserted, stock, stime, etime):
                if trademaster.reset_stock_monthly and model.ltime.strftime('%Y%m') != now.strftime('%Y%m'):
                    model.cnt = 0
                elif stime and etime and not (stime <= model.ltime < etime):
                    model.cnt = 0
                elif model_resettime.resettime <= now and model.ltime < model_resettime.resettime:
                    model.cnt = 0
                model.cnt += num
                if stock < model.cnt:
                    raise CabaretError(u'交換回数の上限を超えています', CabaretError.Code.OVER_LIMIT)
                model.ltime = now
            model_mgr.add_forupdate_task(TradePlayerData, TradePlayerData.makeID(uid, trademaster.id), forUpdatePlayerData, trademaster.stock, stime, etime)
        
        # ミッション.
        mission_executer = PanelMissionConditionExecuter()
        mission_executer.addTargetTrade(trademaster)
        BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
        
        rate_cabaretking = trademaster.rate_cabaretking * num
        
        if trademaster.is_used_platinum_piece:
            # ログ.
            model_mgr.set_save(UserLogTrade.create(uid, trademaster.id, BackendApi.get_platinum_piece(model_mgr, uid) - rate_cabaretking, 0))
            # プラチナの欠片を減らす.
            BackendApi.tr_add_platinum_piece(model_mgr, uid, -rate_cabaretking)
        elif trademaster.is_used_battle_ticket:
            # ログ
            model_mgr.set_save(UserLogTrade.create(uid, trademaster.id, BackendApi.get_battle_ticket(model_mgr, uid) - rate_cabaretking, 0))
            # バトルチケットの数を減らす
            BackendApi.tr_add_battle_ticket(model_mgr, uid, -rate_cabaretking)
        elif trademaster.is_used_crystal_piece:
            # ログ
            model_mgr.set_save(UserLogTrade.create(uid, trademaster.id, BackendApi.get_crystal_piece(model_mgr, uid) - rate_cabaretking, 0))
            # クリスタルの欠片の数を減らす
            BackendApi.tr_add_crystal_piece(model_mgr, uid, -rate_cabaretking)
        else:
            # ログ.
            playertreasure = BackendApi.get_model(model_mgr, PlayerTreasure, uid)
            cabaretking = 0
            if playertreasure:
                cabaretking = playertreasure.get_cabaretking_num()
            model_mgr.set_save(UserLogTrade.create(uid, trademaster.id, cabaretking - rate_cabaretking, 0))
            # 秘宝を減らす.
            BackendApi.tr_add_cabaretking_treasure(model_mgr, uid, -rate_cabaretking)
        
        # 付与.
        presentlist = BackendApi.create_present(model_mgr, 0, uid, trademaster.itype, trademaster.itemid, trademaster.itemnum * num, do_set_save=False)
        for idx, present in enumerate(presentlist):
            present.id = idx
        present_resultset = BackendApi.__tr_receive_present(model_mgr, player, presentlist, [], do_delete=False, cardgetwaytype=Defines.CardGetWayType.TRADE)
        for result in present_resultset.values():
            if result == CabaretError.Code.OK:
                continue
            raise CabaretError(u'交換できませんでした', result)
    
    @staticmethod
    def get_tradeitem_current_num(model_mgr, player, itype, itemid, using=settings.DB_DEFAULT):
        """交換のマスターデータから現在の所持数を取得.
        カードの所持数の時はNone.
        """
        uid = player.id
        
        # 所持数.
        item_num = None
        if itype == Defines.ItemType.ADDITIONAL_GACHATICKET:
            num_model = BackendApi.get_additional_gachaticket_nums(model_mgr, uid, [itemid], using=settings.DB_READONLY).get(itemid)
            item_num = num_model.num if num_model else 0
        elif itype == Defines.ItemType.ITEM:
            item_num = BackendApi.get_item_nums(model_mgr, uid, [itemid], using=settings.DB_READONLY).get(itemid, 0)
        elif itype != Defines.ItemType.CARD:
            item_num = BackendApi.get_num_by_itemtype(model_mgr, player, itype, using=settings.DB_READONLY)
        return item_num
    
    @staticmethod
    def get_num_by_itemtype(model_mgr, player, itype, using=settings.DB_DEFAULT):
        """アイテム種別から所持数を取得.
        """
        def make_getter(attname):
            def get_value():
                return getattr(player, attname)
            return get_value
        def gett_cardnum():
            return BackendApi.get_cardnum(player.id, model_mgr, using)
        
        cur_nums = {
            Defines.ItemType.GOLD : make_getter('gold'),
            Defines.ItemType.RAREOVERTICKET : make_getter('rareoverticket'),
            Defines.ItemType.MEMORIESTICKET : make_getter('memoriesticket'),
            Defines.ItemType.TRYLUCKTICKET : make_getter('tryluckticket'),
            Defines.ItemType.GACHATICKET : make_getter('gachaticket'),
            Defines.ItemType.GACHA_PT : make_getter('gachapt'),
            Defines.ItemType.CARD : gett_cardnum,
            Defines.ItemType.GOLDKEY : make_getter('goldkey'),
            Defines.ItemType.SILVERKEY : make_getter('silverkey'),
        }
        f = cur_nums.get(itype, None)
        if not f:
            raise CabaretError(u'所持数確認未対応の種別です')
        return f()

    #========================================================================
    # 交換所.
    @staticmethod
    def get_tradeshopmaster(model_mgr, mid, using=settings.DB_DEFAULT):
        """交換所情報の取得"""
        return BackendApi.get_model(model_mgr, TradeShopMaster, mid, using=using)

    @staticmethod
    def get_current_tradeshopmaster(model_mgr, using=settings.DB_DEFAULT):
        """現在開催中の交換所マスターの取得"""
        master_list = model_mgr.get_mastermodel_all(TradeShopMaster, using=using)
        scheduleid_list = list(set([master.schedule for master in master_list]))
        schedule_flags = BackendApi.check_schedule_many(model_mgr, scheduleid_list, using=using, now=OSAUtil.get_now())
        masters = [master for master in master_list if schedule_flags.get(master.schedule, True)]

        if not masters:
            return None
        return masters[0]

    @staticmethod
    def get_current_reprintticket_tradeshopmaster(model_mgr, using=settings.DB_DEFAULT):
        """現在開催中の復刻チケット交換所の取得"""
        master_list = model_mgr.get_mastermodel_all(ReprintTicketTradeShopMaster, using=using)
        scheduleid_list = list(set([master.schedule_id for master in master_list]))
        schedule_flags = BackendApi.check_schedule_many(model_mgr, scheduleid_list, using=using, now=OSAUtil.get_now())
        masters = [master for master in master_list if schedule_flags.get(master.schedule_id, True)]

        if not masters:
            return None
        return masters

    @staticmethod
    def get_tradeshopitemmaster(model_mgr, mid, using=settings.DB_DEFAULT):
        """交換所のアイテムマスター取得"""
        return BackendApi.get_model(model_mgr, TradeShopItemMaster, mid, using=using)

    @staticmethod
    def get_tradeshopitemmaster_list(model_mgr, midlist, using=settings.DB_DEFAULT):
        """交換所のアイテムマスターをリスト取得する"""
        return BackendApi.get_model_list(model_mgr, TradeShopItemMaster, midlist, using=using)

    @staticmethod
    def get_tradeshop_usertradecount(model_mgr, uid, tradeshopitemid, using=settings.DB_DEFAULT):
        tradeid = TradeShopPlayerData.makeID(uid, tradeshopitemid)
        userdata = model_mgr.get_model(TradeShopPlayerData, tradeid, False, using=using)
        if userdata is None:
            count = 0
        else:
            count = userdata.cnt
        return count

    @staticmethod
    def get_tradeshopitem_tradecountdata(model_mgr, uid, tradeshopitemmasters, using=settings.DB_DEFAULT):
        itemmids = [master.id for master in tradeshopitemmasters]
        data = {}
        for itemmid in itemmids:
            userdata = BackendApi.get_tradeshop_usertradecount(model_mgr, uid, itemmid, using=using)
            if userdata is None:
                data[itemmid] = None
            else:
                data[itemmid] = userdata
        return data

    @staticmethod
    def get_reprintticket_tradeshop_playerdata(model_mgr, uid, tradeshopmaster, using=settings.DB_DEFAULT):
        key = ReprintTicketTradeShopPlayerData.makeID(uid, tradeshopmaster.id)
        return BackendApi.get_model(model_mgr, ReprintTicketTradeShopPlayerData, key, using=using)

    @staticmethod
    def get_reprintticket_tradeshop_playerdata_list(model_mgr, uid, tradeshopmasters, using=settings.DB_DEFAULT):
        keylist = [ReprintTicketTradeShopPlayerData.makeID(uid, master.id) for master in tradeshopmasters]
        return BackendApi.get_model_list(model_mgr, ReprintTicketTradeShopPlayerData, keylist, using=using)

    @staticmethod
    def get_reprintticket_tradeshop_usertradecount(userdata):
        if userdata is None:
            count = 0
        else:
            count = userdata.cnt
        return count

    @staticmethod
    def get_reprintticket_tradeshop_tradecountdata(itemids, userdata):
        data = {}
        for itemid in itemids:
            data[itemid] = BackendApi.get_reprintticket_tradeshop_usertradecount(userdata[itemid])
        return data

    @staticmethod
    def get_tradeshop_userpoint(model_mgr, uid):
        userdata = model_mgr.get_model(PlayerTradeShop, uid, False, using=settings.DB_DEFAULT)
        if userdata is None:
            shop_point = 0
        else:
            shop_point = userdata.point
        return shop_point

    @staticmethod
    def tr_reprintticket_tradeshop_item(model_mgr, player, trademasterid, confirmkey, num):
        """アイテム交換書き込み
        """
        uid = player.id

        # 重複確認.
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)

        trademaster = BackendApi.get_model(model_mgr, ReprintTicketTradeShopMaster, trademasterid)
        if trademaster is None:
            raise CabaretError(u'データが存在しません', CabaretError.Code.INVALID_MASTERDATA)
        now = BackendApi.check_schedule_error_or_nowtime(model_mgr, trademaster.schedule_id)

        if trademaster.ticket_id == 0:
            ticketid = Defines.GachaConsumeType.GachaTicketType.REPRINT_TICKET
        else:
            ticketid = trademaster.ticket_id

        ticketkey = GachaTicket.makeID(uid, ticketid)
        gachaticket = model_mgr.get_model_forupdate(GachaTicket, ticketkey)

        if gachaticket is None:
            raise CabaretError(u'対象のチケットを所持していません', CabaretError.Code.NOT_ENOUGH)

        use_ticketnum = num * trademaster.use_ticketnum
        is_trade = 0 <= (gachaticket.num - use_ticketnum)
        if is_trade == False:
            raise CabaretError(u'チケットが足りません', CabaretError.Code.NOT_ENOUGH)

        playerdatakey = ReprintTicketTradeShopPlayerData.makeID(uid, trademasterid)
        playerdata = model_mgr.get_model_forupdate(ReprintTicketTradeShopPlayerData, playerdatakey)
        if playerdata is None:
            playerdata = ReprintTicketTradeShopPlayerData.createInstance(playerdatakey)

        is_tradeover = trademaster.stock < (playerdata.cnt + num)
        if trademaster.stock != 0 and is_tradeover:
            raise CabaretError(u'交換可能最大数を超えています', CabaretError.Code.ILLEGAL_ARGS)

        # ログの作成.
        model_mgr.set_save(
            UserLogReprintTicketTradeShop.create(uid, trademaster.id, trademaster.card_id, ticketid, num, use_ticketnum, gachaticket.num)
        )

        mission_executer = PanelMissionConditionExecuter()
        # バトル実行達成を登録.
        mission_executer.addTargetReprintTicket()
        BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)

        gachaticket.num -= use_ticketnum
        playerdata.cnt += num

        prizelist = [PrizeData.create(cardid=trademaster.card_id, cardnum=num)]
        BackendApi.tr_add_prize(model_mgr, uid, prizelist, trademaster.reprintticket_trade_text)
        model_mgr.set_save(gachaticket)
        model_mgr.set_save(playerdata)
        
    @staticmethod
    def tr_tradeshop_item(model_mgr, player, itemmid, confirmkey, num):
        """交換所アイテム交換.
        """
        # 重複確認
        BackendApi.tr_update_requestkey(model_mgr, player.id, confirmkey)

        tradeshopmaster = BackendApi.get_current_tradeshopmaster(model_mgr)
        itemmaster = BackendApi.get_tradeshopitemmaster(model_mgr, itemmid)
        now = BackendApi.check_schedule_error_or_nowtime(model_mgr, tradeshopmaster.schedule)

        is_infinity = (itemmaster.stock == 0)
        def forUpdatePlayerData(model, inserted, stock, is_infinity):
            if not is_infinity and stock < model.cnt:
                raise CabaretError(u'交換回数の上限を超えています', CabaretError.Code.OVER_LIMIT)
            model.ltime = now
        tradeshopplayerdataid = TradeShopPlayerData.makeID(player.id, itemmaster.id)
        model_mgr.add_forupdate_task(TradeShopPlayerData, tradeshopplayerdataid, forUpdatePlayerData, itemmaster.stock, is_infinity)

        # ログを作成する.
        playertradeshop = BackendApi.get_model(model_mgr, PlayerTradeShop, player.id)
        model_mgr.set_save(UserLogTradeShop.create(player.id, tradeshopmaster.id, itemmaster.id, playertradeshop.point - (num * itemmaster.use_point)))

        # Pt交換時のポイント消費.
        BackendApi.tr_playertradeshop_usepoint(model_mgr, player.id, num, itemmaster)

        # 交換回数カウントアップ.
        BackendApi.tr_tradeshopplayerdata_add_tradecount(model_mgr, player.id, num, itemmaster, is_infinity)

        presentnum = num * itemmaster.itemnum
        # 付与.
        itemtype = Defines.ItemType
        if itemmaster.itype == itemtype.ITEM:
            prizelist = [PrizeData.create(itemid=itemmaster.itemid, itemnum=presentnum)]
        elif itemmaster.itype == itemtype.CARD:
            prizelist = [PrizeData.create(cardid=itemmaster.itemid, cardnum=presentnum)]
        elif itemmaster.itype == itemtype.RAREOVERTICKET:
            prizelist = [PrizeData.create(rareoverticket=presentnum)]
        elif itemmaster.itype == itemtype.TRYLUCKTICKET:
            prizelist = [PrizeData.create(tryluckticket=presentnum)]
        elif itemmaster.itype == itemtype.MEMORIESTICKET:
            prizelist = [PrizeData.create(memoriesticket=presentnum)]
        elif itemmaster.itype == itemtype.GACHATICKET:
            prizelist = [PrizeData.create(gachaticket=presentnum)]
        elif itemmaster.itype == itemtype.ADDITIONAL_GACHATICKET:
            prizelist = [PrizeData.create(additional_ticket_id=itemmaster.additional_ticket_id, additional_ticket_num=presentnum)]
        elif itemmaster.itype == itemtype.CABARETCLUB_SPECIAL_MONEY:
            prizelist = [PrizeData.create(cabaclub_money=presentnum)]
        elif itemmaster.itype == itemtype.CABARETCLUB_HONOR_POINT:
            prizelist = [PrizeData.create(cabaclub_honor=presentnum)]
        BackendApi.tr_add_prize(model_mgr, player.id, prizelist, itemmaster.pt_change_text)

    @staticmethod
    def tr_playertradeshop_usepoint(model_mgr, uid, num, tradeshopitem):
        """交換時のポイント消費適応.
        """
        playertradeshop = model_mgr.get_model(PlayerTradeShop, uid)
        playertradeshop.point -= (num * tradeshopitem.use_point)
        if playertradeshop.point < 0:
            raise CabaretError(u'獲得Ptが不足しています.', CabaretError.Code.ILLEGAL_ARGS)
        model_mgr.set_save(playertradeshop)

    @staticmethod
    def tr_tradeshopplayerdata_add_tradecount(model_mgr, uid, num, tradeshopitemmaster, is_infinity):
        """交換回数を保存.
        """
        tradeid = TradeShopPlayerData.makeID(uid, tradeshopitemmaster.id)
        tradeshopplayerdata = model_mgr.get_model(TradeShopPlayerData, tradeid)
        tradeshopplayerdata.cnt += num
        if not is_infinity and tradeshopitemmaster.stock < tradeshopplayerdata.cnt:
            raise CabaretError(u'交換回数の上限を越えています.', CabaretError.Code.OVER_LIMIT)
        model_mgr.set_save(tradeshopplayerdata)


    #========================================================================
    # 課金.
    @staticmethod
    def get_paymententry_list(model_cls, uid, is_complete, limit=-1, offset=0, using=settings.DB_DEFAULT):
        """課金レコードを取得.
        これはキャッシュとか使わないほうがいいかな.
        """
        filters = {
            'uid' : uid,
        }
        if is_complete:
            # 購入完了.
            filters['state'] = PaymentData.Status.COMPLETED
        else:
            # 課金コールバックが呼ばれたけど結果まで表示していない.
            filters['state'] = PaymentData.Status.START
        return model_cls.fetchValues(filters=filters, order_by='-ctime', limit=limit, offset=offset, using=using)
    
    @staticmethod
    def get_gachapaymententry_list(uid, is_complete, limit=-1, offset=0, using=settings.DB_DEFAULT):
        """ガチャの課金レコードを取得.
        """
        return BackendApi.get_paymententry_list(GachaPaymentEntry, uid, is_complete, limit, offset, using)
    
    @staticmethod
    def get_shoppaymententry_list(uid, is_complete, limit=-1, offset=0, using=settings.DB_DEFAULT):
        """ショップの課金レコードを取得.
        """
        return BackendApi.get_paymententry_list(ShopPaymentEntry, uid, is_complete, limit, offset, using)
    
    @staticmethod
    def check_payment_lostrecords(uid):
        """途中で抜けた課金レコードをチェック.
        """
        client = OSAUtil.get_cache_client()
        KEY = 'payment_checked:%s' % uid
        
        kind = client.get(KEY)
        if kind is None:
            kind = 'none'
            modellist = BackendApi.get_gachapaymententry_list(uid, False, limit=1, offset=0, using=settings.DB_READONLY)
            if modellist:
                kind = 'gacha'
            else:
                modellist = BackendApi.get_shoppaymententry_list(uid, False, limit=1, offset=0, using=settings.DB_READONLY)
                if modellist:
                    kind = 'shop'
            client.set(KEY, kind)
        return kind
    @staticmethod
    def delete_payment_lostrecords_flag(uid):
        client = OSAUtil.get_cache_client()
        KEY = 'payment_checked:%s' % uid
        client.delete(KEY)
    
    @staticmethod
    def get_restful_paymentrecord(handler, paymentId, viewer_id=None):
        if settings_sub.IS_LOCAL:
            paymentdata = PaymentData()
            paymentdata.paymentId = paymentId
            paymentdata.userId = viewer_id
            paymentdata.status = int(handler.request.get(Defines.URLQUERY_STATE) or 2)
        else:
            # APIで課金情報を取得.
            data = PaymentGetRequestData()
            data.paymentId = paymentId
            data.guid = viewer_id or handler.osa_util.viewer_id
            
            def get(request):
                handler.addAppApiRequest('payment_check', request)
                ret_data = handler.execute_api()
                paymentdata = ret_data['payment_check'].get()
                return paymentdata
            
            request = ApiRequestMakerSp.makePaymentGetApiRequest(handler.osa_util, data)
            try:
                paymentdata = get(request)
            except:
                request = ApiRequestMakerPc.makePaymentGetApiRequest(handler.osa_util, data)
                try:
                    paymentdata = get(request)
                except:
                    if viewer_id is None:
                        raise
                    else:
                        raise CabaretError(u'購入情報を確認できませんでした.', CabaretError.Code.ILLEGAL_ARGS)
        return paymentdata
    
    @staticmethod
    def get_restful_paymentrecord_status(handler, paymentId, viewer_id=None):
        record = BackendApi.get_restful_paymentrecord(handler, paymentId, viewer_id)
        return record.status if record else None
    
    #========================================================================
    # 招待.
    @staticmethod
    def tr_invite_add(apphandler, dmmidlist, from_id):
        """ADDライフサイクリイベント.
        """
        now = OSAUtil.get_now()
        
        # まずレコード作成.
        def tr_create():
            model_mgr = ModelRequestMgr()
            invitedata_dict = BackendApi.get_model_dict(model_mgr, InviteData, dmmidlist, using=settings.DB_DEFAULT)
            for dmmid in dmmidlist:
                invitedata = invitedata_dict.get(dmmid)
                if invitedata is None:
                    invitedata = InviteData.makeInstance(dmmid)
                    invitedata.fid = from_id
                    invitedata.state = Defines.InviteState.RECEIVE
                    invitedata.ctime = now
                    model_mgr.set_save(invitedata)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr_create).write_end()
        
        invitemap = {}
        def addInvite(etime):
            invitemaster = BackendApi.get_current_invitemaster(apphandler.getModelMgr(), using=settings.DB_READONLY, now=etime)
            if invitemaster:
                data = invitemap[invitemaster.id] = invitemap.get(invitemaster.id) or {'master':invitemaster, 'cnt':0}
                data['cnt'] += 1
        
        uiddict = BackendApi.dmmid_to_appuid(apphandler, dmmidlist, using=settings.DB_READONLY)
        playertutorial_dict = BackendApi.get_model_dict(apphandler.getModelMgr(), PlayerTutorial, uiddict.values(), using=settings.DB_DEFAULT)
        
        def tr_add():
            model_mgr = ModelRequestMgr()
            
            invite_num = 0
            invitedata_list = model_mgr.get_models_forupdate(InviteData, uiddict.keys())
            for invitedata in invitedata_list:
                if invitedata.state == Defines.InviteState.ACCEPT:
                    # 処理済み.
                    continue
                elif invitedata.fid != from_id:
                    # 他のユーザに招待された.
                    continue
                dmmid = invitedata.id
                uid = uiddict[dmmid]
                
                if playertutorial_dict.get(uid):
                    playertutorial = PlayerTutorial.getByKeyForUpdate(uid)
                    if playertutorial.tutorialstate == Defines.TutorialStatus.COMPLETED:
                        invitedata.state = Defines.InviteState.ACCEPT
                        model_mgr.set_save(invitedata)
                        addInvite(playertutorial.etime)
                invite_num += 1
            
            if 0 < invite_num:
                if invitemap:
                    for mid,data in invitemap.items():
                        invitemaster = data['master']
                        cnt = data['cnt']
                        cnt_post = BackendApi.add_invite_cnt(model_mgr, from_id, mid, cnt)
                        prizes = BackendApi.get_invite_prizes(invitemaster, cnt_post - cnt + 1, cnt_post)
                        if prizes:
                            prizelist = BackendApi.get_prizelist(model_mgr, prizes)
                            BackendApi.tr_add_prize(model_mgr, from_id, prizelist, Defines.TextMasterID.INVITE)
                def writeEnd():
                    kpi_operator = KpiOperator()
                    kpi_operator.set_increment_invite_success_count(invite_num, now)
                    for data in invitemap.values():
                        kpi_operator.set_increment_invite_tutoend_count(data['cnt'], now)
                    kpi_operator.save()
                model_mgr.add_write_end_method(writeEnd)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr_add).write_end()
        
        return True
    
    @staticmethod
    def get_invitemaster_all(model_mgr, using=settings.DB_DEFAULT):
        """招待マスター取得(全て).
        """
        return model_mgr.get_mastermodel_all(InviteMaster, using=using)
    
    @staticmethod
    def get_invitemaster(model_mgr, mid, using=settings.DB_DEFAULT):
        """招待マスター取得(全て).
        """
        return BackendApi.get_model(model_mgr, InviteMaster, mid, using=using)
    
    @staticmethod
    def get_current_invitemaster(model_mgr, using=settings.DB_DEFAULT, now=None):
        """有効な招待マスター取得.
        """
        now = now or OSAUtil.get_now()
        
        client = OSAUtil.get_cache_client()
        key = 'current_inviteid'
        current_inviteid = client.get(key)
        
        invitemaster = None
        if current_inviteid:
            invitemaster = BackendApi.get_invitemaster(model_mgr, current_inviteid, using=using)
            if invitemaster and not BackendApi.check_schedule(model_mgr, invitemaster.schedule, using=using, now=now):
                client.set(key, 0)
                invitemaster = None
        
        if invitemaster is None:
            invitemasterlist = BackendApi.get_invitemaster_all(model_mgr, using=using)
            for master in invitemasterlist:
                if BackendApi.check_schedule(model_mgr, master.schedule, using=using, now=now):
                    # 最初にみつけた１件のみを返す.
                    invitemaster = master
                    client.set(key, invitemaster.id)
                    break
        return invitemaster
    
    @staticmethod
    def get_invite(model_mgr, uid, mid, using=settings.DB_DEFAULT):
        """招待情報取得.
        """
        invite = model_mgr.get_model(Invite, Invite.makeID(uid, mid), True, using=using)
        return invite
    
    @staticmethod
    def add_invite_cnt(model_mgr, from_id, mid, cnt=1):
        """招待数更新.
        """
        invite_id = Invite.makeID(from_id, mid)
        invite = BackendApi.get_model(model_mgr, Invite, invite_id, using=settings.DB_DEFAULT)
        if invite is None:
            invite = Invite.makeInstance(invite_id)
            invite.insert()
            model_mgr.set_got_models([invite])
        invite = model_mgr.get_model_forupdate(Invite, invite_id)
        invite.cnt += cnt
        model_mgr.set_save(invite)
        return invite.cnt
    
    @staticmethod
    def get_invite_prizes(invitemaster, cnt_min, cnt_max=None):
        """報酬取得.
        """
        if cnt_max is None:
            cnt_max = cnt_min
        
        prizeidlist = []
        
        table = invitemaster.get_prizes(cnt_min, cnt_max)
        for arr in table.values():
            prizeidlist.extend(arr)
        return prizeidlist
    
    #========================================================================
    # クロスプロモーション.
    @staticmethod
    def get_promotionconfig(model_mgr, appname, using=settings.DB_DEFAULT, do_get_closed=False):
        """プロモーション報酬マスター取得(全て).
        """
        model_cls = PromotionUtil.getPromotionConfigCls(appname)
        if model_cls is None:
            return None
        
        master = BackendApi.get_model(model_mgr, model_cls, model_cls.SINGLE_ID, using=using)
        if master and (do_get_closed or BackendApi.check_schedule(model_mgr, master.schedule, using=using)):
            return master
        else:
            return None
    
    @staticmethod
    def get_promotionprizemaster_all(model_mgr, appname, using=settings.DB_DEFAULT):
        """プロモーション報酬マスター取得(全て).
        """
        model_cls = PromotionUtil.getPromotionPrizeMasterCls(appname)
        if model_cls is None:
            return []
        
        masterlist = model_mgr.get_mastermodel_all(model_cls, using=using)
        now = OSAUtil.get_now()
        return [master for master in masterlist if BackendApi.check_schedule(model_mgr, master.schedule, using=using, now=now)]
    
    @staticmethod
    def get_promotionprizemaster(model_mgr, appname, mid, using=settings.DB_DEFAULT):
        """プロモーション報酬マスター取得.
        """
        model_cls = PromotionUtil.getPromotionPrizeMasterCls(appname)
        if model_cls is None:
            return None
        
        master = BackendApi.get_model(model_mgr, model_cls, mid, using=using)
        if master and BackendApi.check_schedule(model_mgr, master.schedule, using=using):
            return master
        else:
            return None
    
    @staticmethod
    def get_promotionrequirementmaster_list(model_mgr, appname, midlist, using=settings.DB_DEFAULT):
        """プロモーション条件マスター取得.
        """
        model_cls = PromotionUtil.getPromotionRequirementMasterCls(appname)
        if model_cls is None:
            return []
        
        return BackendApi.get_model_list(model_mgr, model_cls, midlist, using=using)
    
    @staticmethod
    def get_promotionrequirementmaster(model_mgr, appname, mid, using=settings.DB_DEFAULT):
        """プロモーション条件マスター取得.
        """
        model_cls = PromotionUtil.getPromotionRequirementMasterCls(appname)
        if model_cls is None:
            return None
        
        return BackendApi.get_model(model_mgr, model_cls, mid, using=using)
    
    @staticmethod
    def get_promotionrequirementmaster_all(model_mgr, appname, using=settings.DB_DEFAULT):
        """プロモーション条件マスター取得(全て).
        """
        model_cls = PromotionUtil.getPromotionRequirementMasterCls(appname)
        if model_cls is None:
            return []
        
        masterlist = model_mgr.get_mastermodel_all(model_cls, using=using)
        return masterlist
    
    @staticmethod
    def __check_promotionrequirement_level(handler, uid, requirementmaster):
        """プロモーション条件クリア判定(レベル達成).
        """
        player = BackendApi.get_player(handler, uid, [PlayerExp], using=settings.DB_READONLY)
        if player is None or player.getModel(PlayerExp) is None:
            return False
        
        return requirementmaster.condition_value <= player.level
    
    @staticmethod
    def check_promotionrequirement(handler, uid, requirementmaster):
        """プロモーション条件クリア判定.
        """
        table = {
            Defines.PromotionRequirementType.LEVEL : BackendApi.__check_promotionrequirement_level,
        }
        func = table.get(requirementmaster.condition_type, None)
        if func:
            return func(handler, uid, requirementmaster)
        return False
    
    @staticmethod
    def get_promotion_userdata(model_mgr, appname, uid, midlist, using=settings.DB_DEFAULT):
        """プロモーション条件クリアフラグ.
        """
        model_cls = PromotionUtil.getPromotionDataCls(appname)
        if model_cls is None:
            return {}
        
        idlist = [model_cls.makeID(uid, mid) for mid in midlist]
        modellist = BackendApi.get_model_list(model_mgr, model_cls, idlist, using=using)
        return dict([(model.mid, model) for model in modellist])
    
    @staticmethod
    def tr_achieve_promotion(model_mgr, appname, uid, midlist):
        """プロモーション条件達成書き込み.
        """
        model_cls = PromotionUtil.getPromotionDataCls(appname)
        if model_cls is None:
            raise CabaretError(u'未対応のアプリです', CabaretError.Code.ILLEGAL_ARGS)
        
        dest = {}
        def forUpdate(model, inserted):
            if inserted or model.status == Defines.PromotionStatus.NONE:
                model.status = Defines.PromotionStatus.ACHIEVED
                model.atime = OSAUtil.get_now()
            dest[model.mid] = model
        for mid in midlist:
            model_mgr.add_forupdate_task(model_cls, model_cls.makeID(uid, mid), forUpdate)
        return dest
    
    @staticmethod
    def tr_receive_promotionprize(model_mgr, appname, uid, promotionprizemaster):
        """プロモーション報酬受取.
        """
        model_cls = PromotionUtil.getPromotionDataCls(appname)
        if model_cls is None:
            raise CabaretError(u'未対応のアプリです', CabaretError.Code.ILLEGAL_ARGS)
        
        mid = promotionprizemaster.id
        
        def forUpdate(model, inserted):
            if model.status == Defines.PromotionStatus.RECEIVED:
                raise CabaretError(u'受取済みです', CabaretError.Code.ALREADY_RECEIVED)
            elif model.status != Defines.PromotionStatus.ACHIEVED:
                raise CabaretError(u'条件達成を確認できていません', CabaretError.Code.ILLEGAL_ARGS)
            model.status = Defines.PromotionStatus.RECEIVED
            model.rtime = OSAUtil.get_now()
        model_mgr.add_forupdate_task(model_cls, model_cls.makeID(uid, mid), forUpdate)
        
        prizelist = BackendApi.get_prizelist(model_mgr, promotionprizemaster.prizes)
        if prizelist:
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, promotionprizemaster.prize_text)
    
    @staticmethod
    def make_promotion_prizeinfo(handler, appname, masterlist, requirement_texts, userdata_dict):
        """プロモーション報酬情報作成.
        """
        model_mgr = handler.getModelMgr()
        
        auto_receive = None
        
        obj_list = []
        for master in masterlist:
            requirement_text = requirement_texts.get(str(master.rid)) or requirement_texts.get(master.rid)
            if not requirement_text:
                continue
            
            prizelist = BackendApi.get_prizelist(model_mgr, master.prizes, using=settings.DB_READONLY)
            presentlist = BackendApi.create_present_by_prize(model_mgr, 0, prizelist, 0, using=settings.DB_READONLY, do_set_save=False)
            presentsetlist = PresentSet.presentToPresentSet(model_mgr, presentlist, using=settings.DB_READONLY)
            if not presentsetlist:
                continue
            
            obj_prizelist = []
            for presentset in presentsetlist:
                obj_prizelist.append(Objects.present(handler, presentset))
            
            userdata = userdata_dict.get(master.id)
            status = userdata.status if userdata else Defines.PromotionStatus.NONE
            
            obj = {
                'requirement' : requirement_text,
                'prizelist' : obj_prizelist,
                'url_yesno' : handler.makeAppLinkUrl(UrlMaker.promotion_prizereceive_yesno(appname, master.id)),
                'status' : status,
            }
            if status == Defines.PromotionStatus.ACHIEVED and auto_receive is None:
                auto_receive = obj
            
            obj_list.append(obj)
        
        return {
            'auto_receive' : auto_receive,
            'list' : obj_list,
        }
    
    #========================================================================
    # ランキング.
    @staticmethod
    def get_ranking_score(model_cls, mid, uid):
        """ランキングのスコアを取得.
        """
        return model_cls.getScore(mid, uid)
    
    @staticmethod
    def get_ranking_rank(model_cls, mid, uid):
        """ランキング順位を取得.
        """
        return model_cls.getRank(mid, uid)
    
    @staticmethod
    def get_ranking_rankindex(model_cls, mid, uid):
        """ランキング順位(index)を取得.
        """
        return model_cls.getIndex(mid, uid)
    
    @staticmethod
    def get_ranking_rankernum(model_cls, mid):
        """ランキング人数を取得.
        """
        return model_cls.getRankerNum(mid)
    
    @staticmethod
    def fetch_uid_by_rankingrank(model_cls, mid, limit, offset=0, withrank=False):
        """ランキングを範囲取得.
        """
        uidscoreset = model_cls.fetch(mid, offset, limit)
        arr = []
        if uidscoreset:
            if withrank:
                _, score = uidscoreset[0]
                if 0 < score:
                    rank_min = model_cls.getRankByScore(mid, score)
                    score_pre = score
                    cnt = max(0, model_cls.getCountByScore(mid, score) or 0)
                    rank = rank_min
                    # 先頭と同率の場合は加算したくない.
                    cntup = 0
                    for uid, score in uidscoreset:
                        if score < score_pre:
                            rank = rank_min + cnt
                            cntup = 1
                        arr.append((uid, (score, rank)))
                        score_pre = score
                        cnt += cntup
            else:
                arr = uidscoreset
        return arr
    
    #======================================================================================
    # イベント.
    @staticmethod
    def __get_current_eventconfig(model_mgr, model_cls, using=settings.DB_DEFAULT):
        """現在開催中のイベント設定.
        """
        model = BackendApi.get_model(model_mgr, model_cls, model_cls.SINGLE_ID, get_instance=False, using=using)
        if model is None:
            def tr():
                model_mgr = ModelRequestMgr()
                model = model_cls.makeInstance(model_cls.SINGLE_ID)
                model_mgr.set_save(model)
                model_mgr.write_all()
                return model_mgr, model
            tmp_model_mgr, model = db_util.run_in_transaction(tr)
            tmp_model_mgr.write_end()
            model_mgr.set_got_models([model])
        return model
    
    @staticmethod
    def check_event_beginer(model_mgr, uid, beginer_days, starttime, now=None, using=settings.DB_DEFAULT):
        """イベント初心者確認.
        """
        if beginer_days < 1:
            return False
        
        # イベント開始から○日前の0:00から新店舗.
        bordertime = DateTimeUtil.toBaseTime(starttime - datetime.timedelta(days=beginer_days), 0)
        
        playertutorial = BackendApi.get_model(model_mgr, PlayerTutorial, uid, using=using)
        return bordertime <= playertutorial.etime
    
    @staticmethod
    def get_eventscenario_by_number(model_mgr, number, using=settings.DB_DEFAULT):
        """イベントシナリオのパラメータ.
        """
        if not isinstance(number, (int, long)):
            return {}
        
        client = localcache.Client()
        key = 'get_eventscenario_by_number:%s' % number
        data = client.get(key)
        
        if data is None or settings_sub.IS_LOCAL:
            CAST_SIZE_W = 320
            CAST_SIZE_H = 514
            BG_SIZE_W = 262
            BG_SIZE_H = 232
            
            modellist = ScenarioMaster.fetchValues(filters={ 'number' : number }, using=using)
            if not modellist:
                return {}
            
            modellist.sort(key=lambda x:x.id)
            castdict = {}
            castdata = {}
            bgdict = {}
            bgdata = {}
            scenario = []
            
            cast_l = ''
            cast_c = ''
            cast_r = ''
            bg = 'bg_0'
            window = False
            img_pre = None
            
            def getCastSymbolName(cast):
                if not cast:
                    return ''
                elif not castdict.has_key(cast):
                    symbolname = 'cast_%d' % len(castdict)
                    castdict[cast] = symbolname
                    castdata[symbolname] = [cast, 0, 0, CAST_SIZE_W, CAST_SIZE_H]
                return castdict[cast]
            
            def getBGSymbolName(bg):
                if not bgdict.has_key(bg):
                    symbolname = 'bg_%d' % len(bgdict)
                    bgdict[bg] = symbolname
                    bgdata[symbolname] = [bg, -20, -20, BG_SIZE_W, BG_SIZE_H]
                return bgdict[bg]
            
            def setCast(cast, cur_cast, x, y):
                symbolname = getCastSymbolName(cast)
                if cur_cast != symbolname:
                    if cur_cast:
                        # 現在のキャストを退場.
                        addScenario(0, Defines.EventScenarioCommand.FADE_CAST, cur_cast, 100, 0, 12)
                    if symbolname:
                        # 新しいキャストを設定.
                        addScenario(0, Defines.EventScenarioCommand.SET_CAST_POSITION, symbolname, x, y)
                        addScenario(0, Defines.EventScenarioCommand.FADE_CAST, symbolname, 0, 100, 12)
                return symbolname
            
            def setBG(bg, cur_bg):
                symbolname = getBGSymbolName(bg)
                if cur_bg != symbolname:
                    addScenario(0, Defines.EventScenarioCommand.CHANGE_BG, cur_bg, symbolname, 20)
                return symbolname
            
            def addScenario(after, commandid, *args):
                arr = [after, commandid]
                arr.extend(args)
                scenario.append(arr)
            
            for model in modellist:
                
                img_pre = img_pre or model.thumb
                
                if model.window != window:
                    # テキストウィンドウを操作.
                    if model.window:
                        addScenario(0, Defines.EventScenarioCommand.WINDOW_OPEN)
                        addScenario(1, Defines.EventScenarioCommand.WAIT, 4)
                    else:
                        addScenario(0, Defines.EventScenarioCommand.WINDOW_CLOSE)
                        addScenario(1, Defines.EventScenarioCommand.WAIT, 4)
                    window = model.window
                
                # 背景.
                bg = setBG(model.bg, bg)
                
                # キャスト.
                cast_l = setCast(model.cast_l, cast_l, -160, 0)
                cast_c = setCast(model.cast_c, cast_c, 0, 0)
                cast_r = setCast(model.cast_r, cast_r, 160, 0)
                
                # テキスト.
                addScenario(1, Defines.EventScenarioCommand.SET_TEXT, model.text_name, model.text_body)
                
                # その他.
                addScenario(2 if model.touch else 1, Defines.EventScenarioCommand.WAIT, model.wait)
                
                # フェード.
                if 0 < model.fadeouttime:
                    addScenario(1, Defines.EventScenarioCommand.FADE_BLACK, 0, 100, model.fadeouttime)
                if 0 < model.fadeintime:
                    addScenario(1, Defines.EventScenarioCommand.FADE_BLACK, 100, 0, model.fadeintime)
            
            if window:
                addScenario(0, Defines.EventScenarioCommand.WINDOW_CLOSE)
            
            data = {
                'cast' : Json.encode(castdata),
                'bg' : Json.encode(bgdata),
                'scenario' : Json.encode(scenario),
                'thumb' : img_pre,
            }
            client.set(key, data)
        return data
    
    @staticmethod
    def __get_event_stagelist(model_mgr, model_cls, idlist, using=settings.DB_DEFAULT):
        """ステージを取得.
        """
        stage_max = None
        if model_cls is ScoutEventStageMaster:
            config = BackendApi.get_current_scouteventconfig(model_mgr, using=using)
            stage_max = config.get_stage_max()
        elif model_cls is RaidEventScoutStageMaster:
            config = BackendApi.get_current_raideventconfig(model_mgr, using=using)
            stage_max = config.get_stage_max()
        elif model_cls is ProduceEventScoutStageMaster:
            config = BackendApi.get_current_produce_event_config(model_mgr, using=using)

        stagelist = BackendApi.get_model_list(model_mgr, model_cls, idlist, using=using)
        if stage_max is None:
            return stagelist
        else:
            return [stage for stage in stagelist if stage.stage <= stage_max]
    
    @staticmethod
    def __get_event_stage(model_mgr, model_cls, stageid, using=settings.DB_DEFAULT):
        """ステージを取得.
        """
        stagelist = BackendApi.__get_event_stagelist(model_mgr, model_cls, [stageid], using=using)
        return stagelist[0] if stagelist else None
    
    @staticmethod
    def __get_event_stage_by_stagenumber(model_mgr, model_cls, eventid, stagenumber=None, using=settings.DB_DEFAULT):
        """イベントステージをイベント番号とステージ番号で取得.
        """
        client = OSAUtil.get_cache_client()
        key = "__get_event_stage_by_stagenumber##%s##%d##%d" % (model_cls.__name__, eventid, stagenumber or 0)
        
        result = None
        if stagenumber is not None:
            stagemasterid = str(client.get(key))
            stagemasterid = int(stagemasterid) if stagemasterid.isdigit() else None
            if stagemasterid is None:
                stagemaster = model_cls.getValues(filters={'eventid':eventid, 'stage':stagenumber}, using=using)
                stagemasterid = stagemaster.id if stagemaster else 0
                client.set(key, stagemasterid)
            if stagemasterid != 0:
                result = BackendApi.__get_event_stage(model_mgr, model_cls, stagemasterid, using=using)
        else:
            stagemasteridlist = client.get(key)
            if stagemasteridlist is None:
                stagemasterlist = model_cls.fetchValues(filters={'eventid':eventid}, using=using)
                stagemasteridlist = [stagemaster.id for stagemaster in stagemasterlist]
                client.set(key, stagemasteridlist)
            result = BackendApi.__get_event_stagelist(model_mgr, model_cls, stagemasteridlist, using=using)
        return result
    
    @staticmethod
    def __get_event_nextstage(model_mgr, eventid, stagemaster, using=settings.DB_DEFAULT):
        """次のステージを取得.
        """
        stagemodel_cls = stagemaster.__class__
        nextstagemaster = BackendApi.__get_event_stage_by_stagenumber(model_mgr, stagemodel_cls, eventid, stagemaster.stage+1, using=using)
        if nextstagemaster:
            return nextstagemaster
        else:
            return stagemaster
    
    @staticmethod
    def __get_current_eventstage_master(model_mgr, eventmaster, eventplaydata, using=settings.DB_DEFAULT):
        """現在のイベント専用スカウトステージを取得.
        """
        eventid = eventmaster.id
        stage = 1
        if eventplaydata:
            stage = max(eventplaydata.stage, stage)
        
        if isinstance(eventmaster, ScoutEventMaster):
            model_cls = ScoutEventStageMaster
        elif isinstance(eventmaster, RaidEventMaster):
            model_cls = RaidEventScoutStageMaster
        elif isinstance(eventmaster, ProduceEventMaster):
            model_cls = ProduceEventScoutStageMaster
        else:
            raise CabaretError(u'未実装のスカウトです', CabaretError.Code.ILLEGAL_ARGS)
        
        stagemaster = BackendApi.__get_event_stage_by_stagenumber(model_mgr, model_cls, eventid, stage, using)
        if stagemaster is None:
            stage = eventplaydata.cleared
            stagemaster = BackendApi.__get_event_stage_by_stagenumber(model_mgr, model_cls, eventid, stage, using)
            if stagemaster is None:
                # ここに来るのはマスターデータの設定がおかしいか何かバグってる.
                raise CabaretError(u'イベント進行データが壊れています.', CabaretError.Code.UNKNOWN)
        return stagemaster
    
    @staticmethod
    def __get_eventscout_playdata(model_mgr, model_cls, uid, mid, using=settings.DB_DEFAULT, reflesh=False):
        """イベントプレイデータ取得.
        """
        playdataid = model_cls.makeID(uid, mid)
        
        if reflesh:
            playdata = model_cls.getByKey(playdataid, using=using)
            if playdata:
                model_mgr.set_got_models([playdata])
                model_mgr.save_models_to_cache([playdata])
        else:
            playdata = model_mgr.get_model(model_cls, playdataid, using=using)
        
        if playdata is None:
            def tr():
                model_mgr = ModelRequestMgr()
                playdata = model_cls.makeInstance(playdataid)
                playdata.stage = 1
                playdata.ptime = OSAUtil.get_now()
                model_mgr.set_save(playdata)
                model_mgr.write_all()
                return model_mgr, playdata
            model_mgr, playdata = db_util.run_in_transaction(tr)
            model_mgr.write_end()
        return playdata
    
    @staticmethod
    def __get_eventscout_playdata_forupdate(model_mgr, stagemaster, uid, key):
        """書き込み用にイベント専用スカウトの進行情報を取得.
        """
        if isinstance(stagemaster, ScoutEventStageMaster):
            playdata_cls = ScoutEventPlayData
        elif isinstance(stagemaster, RaidEventScoutStageMaster):
            playdata_cls = RaidEventScoutPlayData
        elif isinstance(stagemaster, ProduceEventScoutStageMaster):
            playdata_cls = ProduceEventScoutPlayData
        else:
            raise CabaretError(u'未実装のスカウトです', CabaretError.Code.ILLEGAL_ARGS)
        
        playdata = playdata_cls.getByKeyForUpdate(playdata_cls.makeID(uid, stagemaster.eventid))
        if playdata.alreadykey == key:
            raise CabaretError(u'実行済みです', CabaretError.Code.ALREADY_RECEIVED)
        elif playdata.confirmkey != key:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        elif BackendApi.check_event_boss_playable(playdata, stagemaster):
            raise CabaretError(u'ボスが出現中です', CabaretError.Code.OVER_LIMIT)
        
        if playdata.stage == playdata.cleared and playdata.progress < stagemaster.execution:
            # ボスが出ているけどマスタの変更で進めなくなった人.
            playdata.cleared = playdata.stage - 1
        
        return playdata
    
    @staticmethod
    def __execute_eventscout(model_mgr, player, stagemaster, playdata, event_happenings=None, is_lovetime=False, is_produceevent=False):
        """イベントスカウトを実行.
        """
        uid = player.id
        
        # 次のレベル.
        nextlevelexp = BackendApi.get_playerlevelexp_bylevel(player.level+1, model_mgr)
        
        # 現在のハプニング情報.
        do_select_happening = True
        if is_produceevent:
            happeningset = BackendApi.get_current_producehappening(model_mgr, uid)
        else:
            happeningset = BackendApi.get_current_happening(model_mgr, uid)
        if happeningset and not happeningset.happening.is_end():
            do_select_happening = False
        
        # 現在カード枚数.
        cardnum = BackendApi.get_cardnum(uid, model_mgr)
        
        # 実行オブジェクト.
        if is_produceevent:
            is_full = BackendApi.get_scoutsearch_flag(uid)
        else:
            is_full = False
        executer = ScoutEventExec(player, playdata, playdata.seed, stagemaster, nextlevelexp, cardnum, do_select_happening, event_happenings, is_lovetime=is_lovetime, is_full=is_full)
        
        # 消費行動力.
        apcost = BackendApi.get_event_apcost(stagemaster, player, is_full)
        
        # 終了するまで実行.
        while not executer.is_end:
            executer.execute(apcost)
        
        return executer
    
    @staticmethod
    def __reflect_eventscout_common_result(model_mgr, executer, prize_obj, player):
        """イベント専用スカウト実行結果の共通部分を反映する.
        お金.
        経験値.
        宝箱.
        行動力.
        """
        uid = player.id
        # お金.
        gold = prize_obj['gold']
        if 0 < gold:
            BackendApi.tr_add_gold(model_mgr, uid, gold)
        
        # 経験値.
        exp = prize_obj['exp']
        if 0 < exp:
            BackendApi.tr_add_exp(model_mgr, player, exp)
            level = player.level
            levelupevent = prize_obj.get('levelup', None)
            if levelupevent:
                # 書き込み後のれべる.
                levelupevent.set_level(level)
        
        # 宝箱.
        treasureevent = prize_obj.get('treasure', None)
        if treasureevent:
            # 宝箱の所持数確認.
            treasure_num = BackendApi.get_treasure_num(model_mgr, treasureevent.treasuretype, uid)
            treasuremaster = None
            if treasure_num < Defines.TreasureType.POOL_LIMIT.get(treasureevent.treasuretype, 0):
                treasuremaster = BackendApi.choice_treasure(model_mgr, treasureevent.treasuretype)
            if treasuremaster is None:
                executer.cancelEvent()
            else:
                BackendApi.tr_add_treasure(model_mgr, uid, treasureevent.treasuretype, treasuremaster.id)
        
        # 行動力.
        # レベルが上がったら行動力は書き込まなくていい.
        if not executer.is_levelup:
            player.set_ap(executer.ap)
            model_mgr.set_save(player.getModel(PlayerAp))
    
    @staticmethod
    def __set_eventscoutstage_complete(model_mgr, stagemaster, playdata, now=None):
        """イベントステージのクリア設定.
        """
        now = now or OSAUtil.get_now()
        
        # このステージをクリア済みにする.
        playdata.cleared = playdata.stage
        
        flag_earlybonus = False
        if stagemaster.boss == 0:
            # ボスがいないので次のスカウトへ進む.
            playdata.stage = stagemaster.stage + 1
            playdata.progress = 0
            
            # 早期クリアボーナス.
            flag_earlybonus = BackendApi.__tr_event_send_earlybonus(model_mgr, playdata.uid, stagemaster, now)
        
        return flag_earlybonus
    
    @staticmethod
    def __check_event_earlybonus_stage(model_mgr, eventstagemaster, config, now, using):
        """早期クリアボーナス対象のステージかを判定.
        """
        if config.mid != eventstagemaster.eventid:
            return False
        
        max_stage = config.get_stage_max(now)
        if max_stage is not None and max_stage == eventstagemaster.stage:
            # 最大ステージの制限がありつつ対象が最大ステージ.
            return True
        return False
    
    @staticmethod
    def put_eventscout_earlybonusinfo(handler, eventmaster):
        """早期クリアボーナス対象のステージ情報を埋め込む.
        """
        earlybonus_stage = None
        
        model_mgr = handler.getModelMgr()
        
        if isinstance(eventmaster, ScoutEventMaster):
            config = BackendApi.get_current_scouteventconfig(model_mgr)
            stagemodel_cls = ScoutEventStageMaster
            make_stage_obj = lambda stagemaster : Objects.scoutevent_stage(handler, stagemaster, None)
        elif isinstance(eventmaster, RaidEventMaster):
            config = BackendApi.get_current_raideventconfig(model_mgr)
            stagemodel_cls = RaidEventScoutStageMaster
            make_stage_obj = lambda stagemaster : Objects.raidevent_stage(handler, handler.getViewerPlayer(), 0, stagemaster)
        else:
            raise CabaretError(u'未実装のスカウトです', CabaretError.Code.ILLEGAL_ARGS)
        
        stage_max = config.get_stage_max()
        
        if stage_max is not None:
            stagemaster = BackendApi.__get_event_stage_by_stagenumber(model_mgr, stagemodel_cls, eventmaster.id, stage_max, using=settings.DB_READONLY)
            if stagemaster and stagemaster.earlybonus:
                # 早期クリアボーナス.
                prizelist = BackendApi.get_prizelist(model_mgr, stagemaster.earlybonus, using=settings.DB_READONLY)
                earlybonus = BackendApi.make_prizeinfo(handler, prizelist, using=settings.DB_READONLY)
                
                earlybonus_stage = make_stage_obj(stagemaster)
                earlybonus_stage['earlybonus'] = earlybonus
        
        handler.html_param['earlybonus_stage'] = earlybonus_stage
    
    @staticmethod
    def __tr_event_send_earlybonus(model_mgr, uid, eventstagemaster, now):
        """早期クリアボーナスを付与.
        """
        # 早期クリアボーナスの設定がない.
        if not eventstagemaster.earlybonus:
            return False
        
        if isinstance(eventstagemaster, ScoutEventStageMaster):
            config = BackendApi.get_current_scouteventconfig(model_mgr)
        elif isinstance(eventstagemaster, RaidEventScoutStageMaster):
            config = BackendApi.get_current_raideventconfig(model_mgr)
        else:
            raise CabaretError(u'未実装のスカウトです', CabaretError.Code.ILLEGAL_ARGS)
        
        # 対象のステージなのかを判定.
        if not BackendApi.__check_event_earlybonus_stage(model_mgr, eventstagemaster, config, now, settings.DB_DEFAULT):
            return False
        
        prizelist = BackendApi.get_prizelist(model_mgr, eventstagemaster.earlybonus)
        BackendApi.tr_add_prize(model_mgr, uid, prizelist, eventstagemaster.earlybonus_text)
        return True
    
    @staticmethod
    def __tr_event_stage_clear(model_mgr, eventmaster, player, stagemaster):
        """イベントステージクリア書き込み.
        """
        if isinstance(stagemaster, ScoutEventStageMaster):
            eventscoutplaydata_cls = ScoutEventPlayData
        elif isinstance(stagemaster, RaidEventScoutStageMaster):
            eventscoutplaydata_cls = RaidEventScoutPlayData
        elif isinstance(stagemaster, ProduceEventScoutStageMaster):
            eventscoutplaydata_cls = ProduceEventScoutPlayData
        else:
            raise CabaretError(u'未実装のスカウトです', CabaretError.Code.ILLEGAL_ARGS)
        
        now = OSAUtil.get_now()
        flag_earlybonus = False
        # クリアフラグ書き込み.
        def forUpdate(model, inserted):
            if model.stage == (stagemaster.stage + 1):
                # 書き込み済み.
                raise CabaretError(u'処理済みです', CabaretError.Code.ALREADY_RECEIVED)
            elif stagemaster.stage != model.stage:
                # これは違う.
                raise CabaretError(u'プレイできない太客です', CabaretError.Code.ILLEGAL_ARGS)
            model.progress = 0
            model.cleared = model.stage
            model.stage = stagemaster.stage + 1
            model.ptime = now
            model.setResult(None, None, flag_earlybonus=flag_earlybonus)
        model_mgr.add_forupdate_task(eventscoutplaydata_cls, eventscoutplaydata_cls.makeID(player.id, eventmaster.id), forUpdate)
        
        # 報酬.
        prizeidlist = stagemaster.bossprizes
        prizelist = BackendApi.get_prizemaster_list(model_mgr, prizeidlist)
        dic = dict([(prize.id, PrizeData.createByMaster(prize)) for prize in prizelist])
        prizelist = []
        for prizeid in prizeidlist:
            if not dic.has_key(prizeid):
                raise CabaretError(u'存在しない報酬が含まれています', CabaretError.Code.INVALID_MASTERDATA)
            prizelist.append(dic[prizeid])
        BackendApi.tr_add_prize(model_mgr, player.id, prizelist, Defines.TextMasterID.AREA_CLEAR)
        
        # 早期クリアボーナス.
        flag_earlybonus = BackendApi.__tr_event_send_earlybonus(model_mgr, player.id, stagemaster, now)
    
    @staticmethod
    def __tr_determine_event_scoutcard(model_mgr, playdata, uid, itemmaster, usenum, autosell_rarity):
        """スカウトカード獲得.
        """
        # スカウト情報を取得.
        target_event = BackendApi.find_scout_event(playdata, Defines.ScoutEventType.GET_CARD)
        
        # フラグ確認.
        if target_event is None:
            raise CabaretError(u'女の子に遭遇していません', CabaretError.Code.NOT_DATA)
        elif target_event.is_received:
            raise CabaretError(u'処理済みです', CabaretError.Code.ALREADY_RECEIVED)
        
        # カードのマスターデータ.
        card_mid = target_event.card
        cardmaster = BackendApi.get_cardmasters([card_mid], model_mgr).get(card_mid, None)
        if cardmaster is None:
            raise CabaretError(u'キャストが見つかりませんでした', CabaretError.Code.INVALID_MASTERDATA)
        
        # アイテム消費.
        if itemmaster:
            BackendApi.tr_add_item(model_mgr, uid, itemmaster.id, -usenum)
        
        # 獲得判定.
        rate = BackendApi.get_determine_scoutcard_rate(cardmaster, itemmaster, usenum)
        is_success = AppRandom().getIntN(100) < rate
        
        # カード付与.
        sellprice = None
        sellprice_treasure = None
        if is_success:
            playercard = PlayerCard.getByKeyForUpdate(uid)
            playerdeck = BackendApi.get_model(model_mgr, PlayerDeck, uid)

            if isinstance(playdata, ScoutEventPlayData):
                # ポイント(ハート)の付与.
                point, pointeffect = playdata.result['point']
                base = target_event.data.get('heart', 0)
                # フィーバーモード時.
                if OSAUtil.get_now() < playdata.feveretime:
                    successpoint = base * 2
                else:
                    successpoint = base
                # 特効倍率の逆算.
                successpoint = successpoint * point / (point - pointeffect)
                # 特効倍率の反映.
                point += successpoint
                playdata.result['point'] = (point, pointeffect, successpoint)
                eventmaster = BackendApi.get_current_scouteventmaster(model_mgr)
                # スカウト成功時にポイントを成功報酬分を追加で配布する.
                BackendApi.tr_add_scoutevent_score(model_mgr, eventmaster, uid, successpoint)


            if BackendApi.check_sellauto(cardmaster, autosell_rarity) or BackendApi.get_cardnum(uid, model_mgr) < playerdeck.cardlimit:
                result = BackendApi.tr_create_card(model_mgr, playercard, card_mid, way=Defines.CardGetWayType.SCOUT, autosell_rarity=autosell_rarity)
                is_new = result.get('is_new', False)
                if result.get('autosell', False):
                    sellprice = result.get('sellprice', 0)
                    sellprice_treasure = result.get('sellprice_treasure', 0)
                target_event.set_new(is_new)
            else:
                present = Present.createByCard(0, uid, cardmaster, Defines.TextMasterID.SCOUT)
                model_mgr.set_save(present)
                
                def writePresentEnd():
                    redisdb = RedisModel.getDB()
                    pipe = redisdb.pipeline()
                    BackendApi.add_present(uid, present, pipe=pipe)
                    pipe.execute()
                model_mgr.add_write_end_method(writePresentEnd)
            # playdata.addDropItem(Defines.ItemType.CARD, card_mid)
        
        # 結果書き込み.
        target_event.set_result(is_success, sellprice, sellprice_treasure)
        model_mgr.set_save(playdata)
        
        # 結果を返す.
        return is_success
    
    @staticmethod
    def get_eventraidmasters_by_modeleventvalue(model_mgr, eventvalue, midlist, using=settings.DB_DEFAULT):
        """イベント用拡張レイドマスターを取得.
        """
        raideventid = HappeningUtil.get_raideventid(eventvalue)
        scouteventid = HappeningUtil.get_scouteventid(eventvalue)
        
        if raideventid:
            eventraid_getter = lambda midlist: BackendApi.get_raidevent_raidmasters(model_mgr, raideventid, midlist, using=using)
        elif scouteventid:
            eventraid_getter = lambda midlist: BackendApi.get_scoutevent_raidmasters(model_mgr, scouteventid, midlist, using=using)
        else:
            eventraid_getter = lambda x:{}
        return eventraid_getter(midlist)
    
    @staticmethod
    def get_eventraidmaster_by_modeleventvalue(model_mgr, eventvalue, mid, using=settings.DB_DEFAULT):
        """イベント用拡張レイドマスターを取得.
        """
        return BackendApi.get_eventraidmasters_by_modeleventvalue(model_mgr, eventvalue, [mid], using).get(mid)
    
    #========================================================================
    # レイドイベント.
    @staticmethod
    def get_current_raideventconfig(model_mgr, using=settings.DB_DEFAULT):
        """現在開催中のレイドイベント設定.
        """
        return BackendApi.__get_current_eventconfig(model_mgr, CurrentRaidEventConfig, using=using)
    
    @staticmethod
    def update_raideventconfig(mid, starttime, endtime, bigtime=None, ticket_endtime=None, timebonus_time=None, combobonus_opentime=None, feverchance_opentime=None, fastbonus_opentime=None, epilogue_endtime=None, stageschedule=None):
        """現在開催中のレイドイベント設定を更新.
        """
        bigtime = bigtime or OSAUtil.get_datetime_max()
        ticket_endtime = ticket_endtime or OSAUtil.get_datetime_max()
        timebonus_time = timebonus_time or []
        combobonus_opentime = combobonus_opentime or []
        feverchance_opentime = feverchance_opentime or []
        fastbonus_opentime = fastbonus_opentime or []
        def tr():
            model_mgr = ModelRequestMgr()
            model = BackendApi.get_model(model_mgr, CurrentRaidEventConfig, CurrentRaidEventConfig.SINGLE_ID, get_instance=True)
            model.starttime = starttime
            model.endtime = endtime
            model.bigtime = bigtime
            model.ticket_endtime = ticket_endtime
            if ticket_endtime < endtime:
                model.ticket_endtime = endtime
            model.timebonus_time = timebonus_time
            model.combobonus_opentime = combobonus_opentime
            model.feverchance_opentime = feverchance_opentime
            model.fastbonus_opentime = fastbonus_opentime
            model.epilogue_endtime = epilogue_endtime or model.endtime
            model.stageschedule = stageschedule or []
            
            if model.mid != mid:
                model.prize_flag = 0
                model.beginer_prize_flag = 0
            model.mid = mid
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr, model
        model_mgr, model = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        return model
    
    @staticmethod
    def get_raideventmaster_list(model_mgr, midlist, using=settings.DB_DEFAULT):
        """レイドイベントマスターデータ.
        """
        return BackendApi.get_model_list(model_mgr, RaidEventMaster, midlist, using=using)
    
    @staticmethod
    def get_raideventmaster(model_mgr, mid, using=settings.DB_DEFAULT):
        """レイドイベントマスターデータ.
        """
        return BackendApi.get_model(model_mgr, RaidEventMaster, mid, using=using)
    
    @staticmethod
    def get_current_raideventmaster(model_mgr, using=settings.DB_DEFAULT, do_check_schedule=True):
        """現在開催中のレイドイベント.
        """
        config = BackendApi.get_current_raideventconfig(model_mgr, using=using)
        if config.mid == 0 or (do_check_schedule and not (config.starttime <= OSAUtil.get_now() < config.endtime)):
            return None
        return BackendApi.get_raideventmaster(model_mgr, config.mid, using=using)
    
    @staticmethod
    def get_current_ticket_raideventmaster(model_mgr, using=settings.DB_DEFAULT):
        """イベントチケット関連開放中のレイドイベント.
        """
        config = BackendApi.get_current_raideventconfig(model_mgr, using=using)
        if config.mid == 0 or not (config.ticket_endtime and config.starttime <= OSAUtil.get_now() < config.ticket_endtime):
            return None
        return BackendApi.get_raideventmaster(model_mgr, config.mid, using=using)
    
    @staticmethod
    def get_raidevent_raidmaster_by_eventid(model_mgr, eventid, using=settings.DB_DEFAULT):
        """レイドイベントのレイドマスターデータ.
        """
        client = OSAUtil.get_cache_client()
        key = 'get_raidevent_raidmaster_by_eventid:%s' % eventid
        
        midlist = client.get(key)
        if midlist is None:
            modellist = RaidEventRaidMaster.fetchValues(filters={'eventid':eventid}, using=using)
            midlist = [model.mid for model in modellist]
            client.set(key, midlist)
            return modellist
        else:
            return BackendApi.get_raidevent_raidmasters(model_mgr, eventid, midlist, using=using).values()
    
    @staticmethod
    def get_raidevent_raidmasters(model_mgr, eventid, midlist, using=settings.DB_DEFAULT):
        """レイドイベントのレイドマスターデータ.
        """
        idlist = [RaidEventRaidMaster.makeID(eventid, mid) for mid in midlist]
        modellist = BackendApi.get_model_list(model_mgr, RaidEventRaidMaster, idlist, get_instance=True, using=using)
        return dict([(model.mid, model) for model in modellist])
    
    @staticmethod
    def get_raidevent_raidmaster(model_mgr, eventid, mid, using=settings.DB_DEFAULT):
        """レイドイベントのレイドマスターデータ.
        """
        return BackendApi.get_model(model_mgr, RaidEventRaidMaster, RaidEventRaidMaster.makeID(eventid, mid), get_instance=True, using=using)
    
    @staticmethod
    def get_raidevent_scorerecords(model_mgr, mid, uidlist, using=settings.DB_DEFAULT):
        """レイドイベントの得点レコード.
        """
        idlist = [RaidEventScore.makeID(uid, mid) for uid in uidlist]
        modellist = BackendApi.get_model_list(model_mgr, RaidEventScore, idlist, using=using)
        dic = dict([(model.uid, model) for model in modellist])
        return dic
    
    @staticmethod
    def get_raidevent_scorerecord(model_mgr, mid, uid, using=settings.DB_DEFAULT):
        """レイドイベントの得点レコードを単体取得.
        """
        return BackendApi.get_raidevent_scorerecords(model_mgr, mid, [uid], using=using).get(uid, None)
    
    @staticmethod
    def get_raidevent_flagrecords(model_mgr, mid, uidlist, using=settings.DB_DEFAULT):
        """レイドイベントのフラグレコード.
        """
        idlist = [RaidEventFlags.makeID(uid, mid) for uid in uidlist]
        modellist = BackendApi.get_model_list(model_mgr, RaidEventFlags, idlist, using=using)
        dic = dict([(model.uid, model) for model in modellist])
        return dic
    
    @staticmethod
    def get_raidevent_flagrecord(model_mgr, mid, uid, using=settings.DB_DEFAULT):
        """レイドイベントのフラグレコードを単体取得.
        """
        return BackendApi.get_raidevent_flagrecords(model_mgr, mid, [uid], using=using).get(uid, None)
    
    @staticmethod
    def update_raideventflagrecord(model_mgr, mid, uid, opvtime=None, tbvtime=None, epvtime=None):
        """レイドイベントのフラグレコードを更新.
        """
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        
        def tr():
            model_mgr = ModelRequestMgr()
            
            model = BackendApi.get_model(model_mgr, RaidEventFlags, RaidEventFlags.makeID(uid, mid))
            if model is None:
                model = RaidEventFlags.makeInstance(RaidEventFlags.makeID(uid, mid))
                model.opvtime = OSAUtil.get_datetime_min()
                model.insert()
            
            model = RaidEventFlags.getByKeyForUpdate(model.id)
            if opvtime and config.mid == mid:
                if not (config.starttime <= model.opvtime < config.endtime) and config.starttime <= opvtime < config.endtime:
                    eventmaster = BackendApi.get_raideventmaster(model_mgr, mid)
                    if eventmaster:
                        prizelist = BackendApi.get_prizelist(model_mgr, eventmaster.joinprizes)
                        if prizelist:
                            BackendApi.tr_add_prize(model_mgr, uid, prizelist, eventmaster.joinprize_text)
            
            model.opvtime = opvtime or model.opvtime
            model.tbvtime = tbvtime or model.tbvtime
            model.epvtime = epvtime or model.epvtime
            model_mgr.set_save(model)
            
            if opvtime:
                # ミッション.
                mission_executer = PanelMissionConditionExecuter()
                mission_executer.addTargetViewEventOpening()
                BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
            
            model_mgr.write_all()
            return model_mgr, model
        model_mgr, model = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        return model
    
    @staticmethod
    def get_raidevent_unwillingflagrecord(model_mgr, mid, uid, using=settings.DB_DEFAULT):
        """レイドイベントのフラグレコードを単体取得.
        """
        return BackendApi.get_model(model_mgr, RaidEventFlagsUnwilling, RaidEventFlagsUnwilling.makeID(uid, mid), get_instance=True, using=using)
    
    @staticmethod
    def update_raideventunwillingflagrecord(mid, uid, bigbosstime=None):
        """レイドイベントのフラグレコードを更新.
        """
        def tr():
            model_mgr = ModelRequestMgr()
            model = BackendApi.get_model(model_mgr, RaidEventFlagsUnwilling, RaidEventFlagsUnwilling.makeID(uid, mid), get_instance=True)
            model.bigbosstime = bigbosstime or model.bigbosstime
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr, model
        model_mgr, model = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        return model
    
    @staticmethod
    def check_raidevent_lead_opening(model_mgr, uid, eventid=None, using=settings.DB_DEFAULT):
        """レイドイベントのオープニングに誘導するべきかをチェック.
        """
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        eventid = eventid or config.mid
        if config.mid == 0 or config.mid != eventid or not (config.starttime <= OSAUtil.get_now() < config.endtime):
            # 開催中じゃない.
            return False
        
        flagrecord = BackendApi.get_raidevent_flagrecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
        if flagrecord is None or not (config.starttime <= flagrecord.opvtime < config.endtime):
            return True
        else:
            return False
    
    
    @staticmethod
    def check_raidevent_lead_bigboss(model_mgr, uid, eventid=None, using=settings.DB_DEFAULT):
        """レイドイベントの大ボス出現演出に誘導するべきかをチェック.
        """
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        eventid = eventid or config.mid
        now = OSAUtil.get_now()
        if config.mid == 0 or config.mid != eventid or not (config.starttime <= now < config.endtime):
            # 開催中じゃない.
            return False
        elif now < config.bigtime:
            # 大ボスが出ていない.
            return False
        
        flagrecord = BackendApi.get_raidevent_unwillingflagrecord(model_mgr, eventid, uid, using=using)
        if flagrecord.bigbosstime < config.bigtime:
            return True
        else:
            return False
    
    @staticmethod
    def check_raidevent_lead_epilogue(model_mgr, uid, eventid=None, using=settings.DB_DEFAULT):
        """エピローグの誘導チェック.
        """
        config = BackendApi.get_current_raideventconfig(model_mgr, using=using)
        eventid = eventid or config.mid
        now = OSAUtil.get_now()
        if config.mid == 0 or config.mid != eventid or now < config.endtime or config.epilogue_endtime < now:
            return False
        
        flagrecord = BackendApi.get_raidevent_flagrecord(model_mgr, eventid, uid, using=using)
        if flagrecord and config.starttime <= flagrecord.opvtime and flagrecord.epvtime < flagrecord.opvtime:
            return True
        else:
            return False
    
    @staticmethod
    def get_raidevent_score(mid, uid):
        """レイドイベントのスコアを取得.
        """
        return BackendApi.get_ranking_score(RaidEventRanking, mid, uid)
    
    @staticmethod
    def get_raidevent_rank(mid, uid, is_beginer=False):
        """レイドイベントのランキング順位を取得.
        """
        return BackendApi.get_ranking_rank(RaidEventRankingBeginer if is_beginer else RaidEventRanking, mid, uid)
    
    @staticmethod
    def get_raidevent_rankindex(mid, uid, is_beginer=False):
        """レイドイベントのランキング順位(index)を取得.
        """
        return BackendApi.get_ranking_rankindex(RaidEventRankingBeginer if is_beginer else RaidEventRanking, mid, uid)
    
    @staticmethod
    def get_raidevent_rankernum(mid, is_beginer=False):
        """レイドイベントのランキング人数を取得.
        """
        return BackendApi.get_ranking_rankernum(RaidEventRankingBeginer if is_beginer else RaidEventRanking, mid)
    
    @staticmethod
    def fetch_uid_by_raideventrank(mid, limit, offset=0, withrank=False, is_beginer=False):
        """レイドイベントのランキングを範囲取得.
        """
        return BackendApi.fetch_uid_by_rankingrank(RaidEventRankingBeginer if is_beginer else RaidEventRanking, mid, limit, offset, withrank)
    
    @staticmethod
    def choice_raidevent_timebonus_time(config, now=None):
        """レイドイベントのタイムボーナス時間.
        """
        now = now or OSAUtil.get_now()
        if not (config.starttime <= now < config.endtime):
            return None, None
        
        for data in config.timebonus_time:
            if data['stime'] <= now < data['etime']:
                return data['stime'], data['etime']
        return None, None
    
    @staticmethod
    def get_raidevent_timebonus_time(model_mgr, using=settings.DB_READONLY, now=None):
        """レイドイベントのタイムボーナス時間.
        """
        now = now or OSAUtil.get_now()
        config = BackendApi.get_current_raideventconfig(model_mgr, using=using)
        return BackendApi.choice_raidevent_timebonus_time(config, now)
    
    @staticmethod
    def get_raidevent_timebonus_limit(model_mgr, using=settings.DB_READONLY, now=None):
        """レイドイベントのタイムボーナス残り時間.
        """
        now = now or OSAUtil.get_now()
        _, etime = BackendApi.get_raidevent_timebonus_time(model_mgr, using, now)
        if etime is not None:
            return etime - now
        return None
    
    @staticmethod
    def choice_raidevent_combobonus_time(config, now=None):
        """レイドイベントのコンボボーナス時間.
        """
        now = now or OSAUtil.get_now()
        if not (config.starttime <= now < config.endtime):
            return None, None
        
        for data in config.combobonus_opentime:
            if data['stime'] <= now < data['etime']:
                return data['stime'], data['etime']
        return None, None
    
    @staticmethod
    def check_raidevent_combobonus(model_mgr, using=settings.DB_READONLY, now=None):
        """レイドイベントのコンボボーナスが開放されているか.
        """
        now = now or OSAUtil.get_now()
        config = BackendApi.get_current_raideventconfig(model_mgr, using=using)
        _, etime = BackendApi.choice_raidevent_combobonus_time(config, now)
        return etime is not None
    
    @staticmethod
    def choice_raidevent_combobonus_powuprate(eventmaster, combo_cnt, with_limittime=False):
        """コンボボーナスのパワーアップ倍率を選ぶ.
        """
        def to_result(dbdata):
            if str(dbdata).isdigit():
                result = int(dbdata), Defines.RAIDCOMBO_TIMELIMIT_DEFAULT
            else:
                result = tuple((list(dbdata) + [Defines.RAIDCOMBO_TIMELIMIT_DEFAULT])[:2])
            if with_limittime:
                return result
            else:
                return result[0]
        
        table = dict(eventmaster.combobonus)
        if table.has_key(combo_cnt):
            return to_result(table[combo_cnt])
        else:
            items = eventmaster.combobonus[:]
            items.sort(key=lambda x:x[0])
            tmp_rate = 0
            for num, rate in items:
                if combo_cnt < num:
                    break
                tmp_rate = rate
            return to_result(tmp_rate)
        
    @staticmethod
    def get_raidevent_combobonus_powuprate(model_mgr, eventmaster, raidboss, using=settings.DB_DEFAULT, now=None, with_limittime=False):
        """コンボボーナスのパワーアップ倍率.
        """
        now = now or OSAUtil.get_now()
        
        if eventmaster is None or not BackendApi.check_raidevent_combobonus(model_mgr, using, now):
            if with_limittime:
                return 0, 0
            else:
                return 0
        
        combo_cnt = raidboss.getCurrentComboCount(now=now)
        return BackendApi.choice_raidevent_combobonus_powuprate(eventmaster, combo_cnt, with_limittime=with_limittime)
    
    @staticmethod
    def choice_raidevent_feverchance_time(config, now=None):
        """レイドイベントのフィーバーチャンス公開時間.
        """
        now = now or OSAUtil.get_now()
        if not (config.starttime <= now < config.endtime):
            return None, None
        
        for data in config.feverchance_opentime:
            if data['stime'] <= now < data['etime']:
                return data['stime'], data['etime']
        return None, None
    
    @staticmethod
    def check_raidevent_feverchance(model_mgr, using=settings.DB_READONLY, now=None):
        """レイドイベントのフィーバーチャンスが開放されているか.
        """
        config = BackendApi.get_current_raideventconfig(model_mgr, using=using)
        _, etime = BackendApi.choice_raidevent_feverchance_time(config, now=now)
        return etime is not None
    
    @staticmethod
    def choice_raidevent_fastbonus_time(config, now=None):
        """レイドイベントの秘宝ボーナス公開時間.
        """
        now = now or OSAUtil.get_now()
        if not (config.starttime <= now < config.endtime):
            return None, None
        
        for data in config.fastbonus_opentime:
            if data['stime'] <= now < data['etime']:
                return data['stime'], data['etime']
        return None, None
    
    @staticmethod
    def check_raidevent_fastbonus(model_mgr, using=settings.DB_READONLY, now=None):
        """レイドイベントの秘宝ボーナスが開放されているか.
        """
        config = BackendApi.get_current_raideventconfig(model_mgr, using=using)
        _, etime = BackendApi.choice_raidevent_fastbonus_time(config, now=now)
        return etime is not None
    
    @staticmethod
    def get_raidevent_fastbonusdata(eventmaster, raidboss, destroytime=None):
        """レイドイベントの秘宝ボーナス倍率と終了時間を取得.
        """
        if not eventmaster or not raidboss.fastflag:
            return None
        
        # 経過時間.
        destroytime = destroytime or OSAUtil.get_now()
        timediff = destroytime - raidboss.raid.ctime
        timediff_sec = timediff.days * 86400 + timediff.seconds
        
        fastbonusdata_list = eventmaster.fastbonustable[:]
        fastbonusdata_list.sort(key=lambda x:x[0], reverse=True)
        
        fastbonusdata = None
        for sec, percent in fastbonusdata_list:
            if sec < timediff_sec:
                break
            fastbonusdata = sec, percent
        
        if fastbonusdata is None:
            return None
        
        sec, percent = fastbonusdata
        
        etime = raidboss.raid.ctime + datetime.timedelta(seconds=sec)
        
        rate = percent / 100.0
        if int(rate) == rate:
            str_rate = '%d' % int(rate)
        else:
            str_rate = '%s' % rate
        
        return {
            'percent' : percent,
            'rate' : rate,
            'str_rate' : str_rate,
            'etime' : etime,
            'timelimit' : Objects.timelimit(etime, destroytime),
        }
    
    @staticmethod
    def get_raidevent_specialcardids(model_mgr, uid, master, using=settings.DB_READONLY):
        """イベントレイドボスの特攻カード.
        """
        def filter_func(card, master, midlist, table):
            if master.id in midlist:
                table[master.id] = table[master.id] or []
                table[master.id].append(card.id)
                return True
            return False
        
        midlist = dict(master.specialcard).keys()
        table = dict.fromkeys(midlist)
        
        filter_obj = CardListFilter()
        filter_obj.add_optional_filter(filter_func, midlist, table)
        
        BackendApi._get_card_list(uid, filter_obj=filter_obj, arg_model_mgr=model_mgr, using=using)
        return table
    
    @staticmethod
    def put_raidevent_specialcard_info(handler, uid, eventraidmaster, using=settings.DB_READONLY):
        """特効カード情報.
        """
        model_mgr = handler.getModelMgr()
        specialcardids = BackendApi.get_raidevent_specialcardids(model_mgr, uid, eventraidmaster, using=using)
        
        deck = BackendApi.get_raid_deck(uid, model_mgr, using)
        deckcardset = set(deck.to_array())
        
        masterlist = BackendApi.get_cardmasters(dict(eventraidmaster.specialcard).keys(), model_mgr, using).items()
        
        albums = {}
        for _, master in masterlist:
            arr = albums[master.album] = albums.get(master.album) or []
            arr.append(master)
        albumitems = albums.items()
        albumitems.sort(key=lambda x:x[0])
        
        specialcardlist = []
        need_edit = False
        for _, masterlist in albumitems:
            masterlist.sort(key=lambda x:x.hklevel)
            
            target_master = None
            num = 0
            is_member = False
            for master in masterlist:
                cardidlist = specialcardids.get(master.id) or []
                if bool(set(cardidlist) & deckcardset):
                    target_master = master
                    is_member = True
                elif (not is_member and cardidlist) or target_master is None:
                    target_master = master
                num += len(cardidlist)
            
            if 0 < num:
                pass
            else:
                pass
            
            specialcardlist.append({
                'deck' : is_member,
                'master' : Objects.cardmaster(handler, target_master),
                'hasnum' : num,
            })
            if 0 < num and not is_member:
                need_edit = True
        handler.html_param['specialcardinfo'] = {
            'cardlist' : specialcardlist,
            'need_edit' : need_edit,
        }
    
    @staticmethod
    def check_raidevent_timebonus(model_mgr, using=settings.DB_READONLY, now=None):
        """レイドイベントがタイムボーナス中なのか.
        """
        delta = BackendApi.get_raidevent_timebonus_limit(model_mgr, using=using, now=now)
        return delta is not None
    
    @staticmethod
    def choice_raidevent_notfixed_destroy_prizeids(master, destroy, flagrecord, is_big):
        """未受け取りの報酬.
        """
        prizeids = {}
        
        if not flagrecord:
            return prizeids
        
        if is_big:
            flags = flagrecord.destroyprize_big_flags
            func = master.get_destroyprizes_big
        else:
            flags = flagrecord.destroyprize_flags
            func = master.get_destroyprizes
        
        d_min = 0
        if flags:
            flags.sort(reverse=True)
            d_min = flags[0]
        table = func(d_min, destroy)
        
        masterset = set(table.keys())
        fixedset = set(flags)
        keys = list(masterset - fixedset)
        keys.sort()
        
        for d in keys:
            if destroy < d:
                break
            elif not table[d]:
                continue
            prizeids[d] = table[d][:]
        return prizeids
    
    @staticmethod
    def get_raidevent_next_destroyprizedata(model_mgr, eventmaster, scorerecord, is_big, using=settings.DB_DEFAULT):
        """次に取得可能な討伐数と報酬.
        """
        if is_big:
            cur_destroy = scorerecord.destroy_big if scorerecord else 0
            func = eventmaster.get_next_destroyprizes_big
        else:
            cur_destroy = scorerecord.destroy if scorerecord else 0
            func = eventmaster.get_next_destroyprizes
        
        destroy_num, prizeidlist = func(cur_destroy)
        if prizeidlist:
            return {
                'destroy' : destroy_num,
                'prizelist' : BackendApi.get_prizelist(model_mgr, prizeidlist, using),
                'rest' : destroy_num - cur_destroy,
            }
        else:
            return None
    
    @staticmethod
    def tr_add_raidevent_ticket(model_mgr, uid, mid, num):
        """レイドイベントのチケットを加算.
        """
        def forUpdate(model, inserted):
            model.ticket += num
            if model.ticket < 0:
                raise CabaretError(u'チケットが足りません', CabaretError.Code.NOT_ENOUGH)
        model_mgr.add_forupdate_task(RaidEventScore, RaidEventScore.makeID(uid, mid), forUpdate)
        
        def writeEnd():
            kpi_operator = KpiOperator()
            if 0 < num:
                kpi_operator.set_increment_raidevent_ticket(mid, uid, num)
            else:
                kpi_operator.set_increment_raidevent_consume_ticket(mid, uid, -num)
            kpi_operator.save()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def tr_trade_raidevent_score(model_mgr, uid, master, num, confirmkey):
        """レイドイベントのスコアとチケットを交換.
        """
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        
        point = master.pointratio * num
        
        points = {
            'point' : 0,
            'point_total' : 0,
        }
        
        def forUpdate(model, inserted):
            model.point -= point
            if model.point < 0:
                raise CabaretError(u'秘宝が足りません', CabaretError.Code.NOT_ENOUGH)
            model.ticket += num
            points['point'] = model.point
            points['point_total'] = model.point_total
        model_mgr.add_forupdate_task(RaidEventScore, RaidEventScore.makeID(uid, master.id), forUpdate)
        
        def writeEnd():
            kpi_operator = KpiOperator()
            kpi_operator.set_save_raidevent_consume_point(master.id, uid, points['point_total'] - points['point'])
            kpi_operator.set_increment_raidevent_ticket(master.id, uid, num)
            kpi_operator.save()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def tr_receive_raidevent_destroyprize(model_mgr, uid, master, confirmkey):
        """レイドイベントの討伐報酬受け取り.
        """
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        
        key = RaidEventFlags.makeID(uid, master.id)
        flagrecord = model_mgr.get_model(RaidEventFlags, key)
        if flagrecord:
            flagrecord = model_mgr.get_model_forupdate(RaidEventFlags, key)
        else:
            flagrecord = RaidEventFlags.makeInstance(key)
        
        scorerecord = BackendApi.get_raidevent_scorerecord(model_mgr, master.id, uid)
        if scorerecord is None:
            raise CabaretError(u'報酬の条件を満たしていません', CabaretError.Code.ILLEGAL_ARGS)
        
        received_prizeidlist = []
        
        def receive(is_big):
            if is_big:
                destroy = scorerecord.destroy_big
            else:
                destroy = scorerecord.destroy
            
            prizes = BackendApi.choice_raidevent_notfixed_destroy_prizeids(master, destroy, flagrecord, is_big)
            if not prizes:
                return []
            
            arr = []
            # 討伐報酬.
            if is_big:
                flags = flagrecord.destroyprize_big_flags
            else:
                flags = flagrecord.destroyprize_flags
            for d, prizeidlist in prizes.items():
                if prizeidlist:
                    prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
                    BackendApi.tr_add_prize(model_mgr, uid, prizelist, master.destroyprize_text)
                    flags.append(d)
                    arr.extend(prizeidlist)
            return arr
        
        received_prizeidlist.extend(receive(False))
        received_prizeidlist.extend(receive(True))
        
        if not received_prizeidlist:
            raise CabaretError(u'受け取れる報酬がありません', CabaretError.Code.NOT_DATA)
        
        flagrecord.destroyprize_received = received_prizeidlist
        
        model_mgr.set_save(flagrecord)
    
    @staticmethod
    def tr_add_raidevent_score(model_mgr, master, raidboss, uid, point, destroy=1, is_big=False):
        """レイドイベントのスコアを加算.
        """
        mid = master.id
        
        key = RaidEventScore.makeID(uid, mid)
        tmp = model_mgr.get_model(RaidEventScore, key)
        if tmp is None:
            model = RaidEventScore.makeInstance(key)
        else:
            model = model_mgr.get_model_forupdate(RaidEventScore, key)
        
        model.point += point
        model.point_total += point
        if is_big:
            model.destroy_big += destroy
        else:
            model.destroy += destroy
        
        model_mgr.set_save(model)
        
        def writeEnd():
            pipe = RaidEventRanking.getDB().pipeline()
            RaidEventRanking.create(mid, uid, model.point_total).save(pipe)
            if BackendApi.check_raidevent_beginer(model_mgr, uid, master, using=settings.DB_READONLY):
                RaidEventRankingBeginer.create(mid, uid, model.point_total).save(pipe)
            pipe.execute()
            
            kpi_operator = KpiOperator()
            kpi_operator.set_save_raidevent_point(mid, uid, model.point_total)
            if is_big:
                kpi_operator.set_save_raidevent_destroy_big(mid, uid, model.destroy_big)
            else:
                kpi_operator.set_save_raidevent_destroy(mid, uid, model.destroy)
            if raidboss:
                kpi_operator.set_increment_raidevent_destroy_level(mid, raidboss.master.id, raidboss.raid.level, destroy)
            kpi_operator.save()
        
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def reset_raidboss_eventraidmaster(model_mgr, raidboss, eventvalue, using=settings.DB_DEFAULT):
        """レイドボス情報のイベント情報を更新.
        """
        if eventvalue == 0:
            return
        
        raideventid = HappeningUtil.get_raideventid(eventvalue)
        scouteventid = HappeningUtil.get_scouteventid(eventvalue)
        produceeventid = HappeningUtil.get_produceeventid(eventvalue)
        
        eventraidmaster = None
        
        if raideventid:
            if raidboss.raideventraidmaster is None or raidboss.raideventraidmaster.eventid != raideventid:
                eventraidmaster = BackendApi.get_raidevent_raidmaster(model_mgr, raideventid, raidboss.master.id, using=using)
            else:
                return
        elif scouteventid:
            if raidboss.scouteventraidmaster is None or raidboss.scouteventraidmaster.eventid != scouteventid:
                eventraidmaster = BackendApi.get_scoutevent_raidmaster(model_mgr, scouteventid, raidboss.master.id, using=using)
            else:
                return
        elif produceeventid:
            if raidboss.produceeventraidmaster is None or raidboss.produceeventraidmaster.eventid != produceeventid:
                eventraidmaster = BackendApi.get_produceevent_raidmaster(model_mgr, produceeventid, raidboss.master.id, using=using)
            else:
                return
        
        raidboss.setEventRaidMaster(eventraidmaster)
    
    @staticmethod
    def make_raidevent_destroypoint_info(model_mgr, uid, eventmaster, happeningraidset, specialbonusscore, using=settings.DB_DEFAULT):
        """撃破時の報酬ポイントを集計.
        """
        happeningset = happeningraidset.happening
        raidboss = happeningraidset.raidboss
        
        if 0 < raidboss.raid.hp:
            return None
        
        eventid = eventmaster.id
        eventvalue = HappeningUtil.make_raideventvalue(eventid)
        
        # イベント用のレイドマスターデータを確認.
        BackendApi.reset_raidboss_eventraidmaster(model_mgr, raidboss, eventvalue, using)
        
        # 秘宝ボーナス.
        fastbonusdata = BackendApi.get_raidevent_fastbonusdata(eventmaster, raidboss, happeningset.happening.etime)
        rate = 1
        if fastbonusdata:
            rate = fastbonusdata['rate']
        
        owner_point = 0
        help_point = 0
        mvp_point = 0
        
        # 発見者.
        if raidboss.raid.oid == uid:
            owner_point = raidboss.get_owner_eventpoint() * rate
        else:
            # 協力者報酬.
            helppoints = raidboss.getHelpEventPoints(uid)
            help_point = helppoints.get(uid, 0) * rate
        
        # MVP.
        if uid in raidboss.getMVPList():
            mvp_point = raidboss.get_mvp_eventpoint() * rate
        
        total = owner_point + help_point + mvp_point
        if 0 < total:
            points = {
                'owner' : int(owner_point),
                'help' : int(help_point),
                'mvp' : int(mvp_point),
                'total' : int(total),
                'bonusscore' : int(total * (specialbonusscore / 100.0)),
            }
        else:
            points = None
        return points
    
    @staticmethod
    def aggregate_raidevent_destroypoint(model_mgr, eventmaster, raidboss, using=settings.DB_DEFAULT, destroytime=None):
        """撃破時の報酬ポイントを集計.
        """
        eventid = eventmaster.id
        eventvalue = HappeningUtil.make_raideventvalue(eventid)
        
        # イベント用のレイドマスターデータを確認.
        BackendApi.reset_raidboss_eventraidmaster(model_mgr, raidboss, eventvalue, using)
        
        # 秘宝ボーナス.
        fastbonusdata = BackendApi.get_raidevent_fastbonusdata(eventmaster, raidboss, destroytime=destroytime)
        rate = 1
        if fastbonusdata:
            rate = fastbonusdata['rate']
        
        pointtable = {}
        def addPoint(uid, point):
            arr = pointtable[uid] = pointtable.get(uid) or []
            arr.append(int(point * rate))
        
        # 発見者報酬.
        addPoint(raidboss.raid.oid, raidboss.get_owner_eventpoint())
        
        # MVP報酬.
        mvpuidlist = raidboss.getMVPList()
        mvppoint = raidboss.get_mvp_eventpoint()
        for mvp in mvpuidlist:
            addPoint(mvp, mvppoint)
        
        # 協力者報酬.
        helppoints = raidboss.getHelpEventPoints()
        for uid,point in helppoints.items():
            addPoint(uid, point)
        return pointtable
    
    @staticmethod
    def tr_raidevent_raiddestroy(model_mgr, viewer_uid, raidboss, eventid, outside=False, bonusscore=0):
        """イベントレイド討伐成功.
        """
        if eventid == 0:
            # イベントレイドじゃない.
            return
        
        eventmaster = BackendApi.get_current_raideventmaster(model_mgr)
        if eventmaster is None or eventid != eventmaster.id:
            # イベントが発生していない.
            return
        
        # イベントポイントのテーブル.
        pointtable = BackendApi.aggregate_raidevent_destroypoint(model_mgr, eventmaster, raidboss)
        
        # 素材数.
        eventraidmaster = raidboss.raideventraidmaster
        if eventraidmaster:
            no_material = False
            default_decider = lambda : 0
            def makeDecider(material_droprate, material_num_min, material_num_max):
                if 0 < material_droprate and 0 < material_num_max:
                    return lambda : random.randint(material_num_min, material_num_max) if random.randint(0, 999) < material_droprate else 0
                else:
                    return None
            
            # 発見者.
            _decideMaterialNumOwner = makeDecider(eventraidmaster.material_droprate, eventraidmaster.material_num_min, eventraidmaster.material_num_max)
            no_material = no_material or _decideMaterialNumOwner is None
            _decideMaterialNumOwner = _decideMaterialNumOwner or default_decider
            
            # 救援者.
            _decideMaterialNumHelper = makeDecider(eventraidmaster.material_droprate_help, eventraidmaster.material_num_min_help, eventraidmaster.material_num_max_help)
            no_material = no_material or _decideMaterialNumHelper is None
            _decideMaterialNumHelper = _decideMaterialNumHelper or default_decider
            
            getMaterialIndex = lambda is_owner : eventraidmaster.material if is_owner else eventraidmaster.material_help
            decideMaterialNum = lambda is_owner : _decideMaterialNumOwner() if is_owner else _decideMaterialNumHelper()
            if no_material:
                uidlist = pointtable.keys()
            else:
                uidlist = raidboss.getDamageRecordUserIdList()
        else:
            getMaterialIndex = lambda is_owner : 0
            decideMaterialNum = lambda is_owner : 0
            uidlist = pointtable.keys()
        
        oid = raidboss.raid.oid
        is_big = raidboss.is_big()

        bonusscore_list = None
        if outside and raidboss.raideventraidmaster:
            # 救援者の特攻ボーナス取得.
            bonusscore_list = RaidEventHelpSpecialBonusScore.fetchValues(filters={'raidid':raidboss.raid.id}, using=settings.DB_DEFAULT)
        bonusscore_userdict = { viewer_uid: bonusscore }
        for uid in uidlist:
            record = raidboss.getDamageRecord(uid)
            if record.damage_cnt < 1:
                continue
            
            flag = bool(BackendApi.judge_raidprize_distribution_outside_userid(uid, viewer_uid, oid, True))
            
            if outside:
                material_num = record.material_num
            else:
                material_num = decideMaterialNum(uid == oid)
                if record.champagne:
                    # SHOWTIMEの恩恵を受ける.
                    material_num += int(material_num * eventmaster.champagne_material_bonus / 100)
                
                if 0 < material_num:
                    # 素材数を設定.
                    record.setMaterialResult(material_num)

            if flag == outside:
                # 通常時は外部で行うユーザーは配布しない.
                # 外部処理では外部で行うユーザーだけ配布.
                # ポイントの配布.
                arr = pointtable.get(uid)
                # raidhelp = RaidHelp.getValues(['raidevent_specialbonusscore'], filters={'raidid':raidboss.id, 'toid':viewer_uid}, using=settings.DB_DEFAULT)
                # if raidhelp:
                #     bonusscore = 0
                # else:
                # bonusscore_obj = BackendApi.get_model(model_mgr, RaidEventSpecialBonusScore, viewer_uid, using=settings.DB_DEFAULT)

                # if bonusscore_obj:
                #     bonusscore = bonusscore_obj.bonusscore
                # else:
                #     bonusscore = 0
                if oid == uid != viewer_uid:
                    # オーナー自身が接客して倒した場合は実行しない. ヘルプユーザが倒した時のみのオーナーへのポイント処理.
                    owner_bonusscore_obj = model_mgr.get_model(RaidEventSpecialBonusScore, oid)
                    if owner_bonusscore_obj is not None:
                        bonusscore = owner_bonusscore_obj.bonusscore
                    else:
                        bonusscore = 0
                elif oid != uid == viewer_uid:
                    # ヘルプユーザが特攻を付けて倒した際に bonusscore を正しく付けるには、一旦 dict にした物から撃破者 id で取りだす.
                    # オーナーの配布処理を先に済ませた場合、bonusscore の中身が汚染されているので、その回避.
                    bonusscore = bonusscore_userdict.get(viewer_uid, 0)

                if outside:
                    bonusscore = 0

                if bonusscore_list:
                    _bonusscores = filter(lambda x: getattr(x, 'uid') == uid, bonusscore_list)
                    if len(_bonusscores) == 1:
                        bonusscore = _bonusscores[0].bonusscore

                if arr:
                    total = sum(arr)
                    point = total + int(total * (bonusscore / 100.0))
                    BackendApi.tr_add_raidevent_score(model_mgr, eventmaster, raidboss, uid, point, 1, is_big)

                # 素材の配布.
                if 0 < material_num:
                    num_add_dict = {
                        getMaterialIndex(uid == oid) : material_num
                    }
                    BackendApi.tr_add_raidevent_material(model_mgr, uid, eventid, num_add_dict)
        
        # シャンパン加算.
        flag = bool(BackendApi.judge_raidprize_distribution_outside_userid(oid, viewer_uid, oid, True))
        if flag == outside:
            BackendApi.tr_add_raidevent_champagne(model_mgr, eventmaster, raidboss)
    
    @staticmethod
    def check_raidevent_bigboss_opened(model_mgr, now=None, using=settings.DB_DEFAULT):
        """大ボス出現チェック.
        """
        now = now or OSAUtil.get_now()
        config = BackendApi.get_current_raideventconfig(model_mgr, using=using)
        if config.bigtime and config.bigtime <= now:
            return True
        else:
            return False
    
    @staticmethod
    def tr_init_raidevent(model_mgr, eventid):
        """レイドイベント初期化.
        """
        config = BackendApi.get_current_raideventconfig(model_mgr)
        if config and config.mid == eventid:
            if config.starttime <= OSAUtil.get_now() < config.endtime:
                raise CabaretError(u'イベント開催中なので初期化できません', CabaretError.Code.ILLEGAL_ARGS)
            elif SubProcessPid.exists(Defines.CLOSE_EVENT_PROCESS_NAME):
                raise CabaretError(u'イベント終了処理実行中なので初期化できません', CabaretError.Code.ILLEGAL_ARGS)
            elif config.prize_flag == 0:
                raise CabaretError(u'イベント終了処理を行っていないので初期化できません', CabaretError.Code.ILLEGAL_ARGS)
        
        # スコア.
        RaidEventScore.all().delete()
        
        # 閲覧フラグ.
        RaidEventFlags.all().delete()
        
        def writeEnd():
            OSAUtil.get_cache_client().flush()
            delete_raidevent(eventid)
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def save_kpi_raidevent_join(uid, is_pc, now=None, kpi_operator=None):
        """レイドイベント参加のKPIを保存.
        """
        local_kpi_operator = kpi_operator or KpiOperator()
        local_kpi_operator.set_save_raidevent_join(uid, now, is_pc)
        if kpi_operator is None:
            local_kpi_operator.save()
        return local_kpi_operator
    
    @staticmethod
    def check_raidevent_beginer(model_mgr, uid, eventmaster, config=None, now=None, using=settings.DB_DEFAULT):
        """レイドイベント初心者確認.
        """
        if config is None:
            config = BackendApi.get_current_raideventconfig(model_mgr, using)
        if not config or config.mid != eventmaster.id:
            return False
        return BackendApi.check_event_beginer(model_mgr, uid, eventmaster.beginer_days, config.starttime, now=now, using=using)
    
    @staticmethod
    def get_raidevent_recipeid_by_eventid(model_mgr, eventid, using=settings.DB_DEFAULT):
        """レイドイベント交換所のレシピのIDをイベントIDで取得.
        """
        client = localcache.Client()
        key = 'get_raidevent_recipeid_by_eventid:%d' % eventid
        midlist = client.get(key)
        if midlist is None:
            modellist = RaidEventRecipeMaster.fetchValues(filters={'eventid':eventid}, using=using)
            midlist = [model.id for model in modellist]
            client.set(key, midlist)
            model_mgr.set_got_models(modellist, using=using)
        
        return midlist
    
    @staticmethod
    def get_raidevent_recipemaster_list(model_mgr, recipe_idlist, using=settings.DB_DEFAULT):
        """レイドイベント交換所のレシピ.
        """
        modellist = BackendApi.get_model_list(model_mgr, RaidEventRecipeMaster, recipe_idlist, using=using)
        modellist.sort(key=lambda x:x.id)
        modellist.sort(key=lambda x:x.pri, reverse=True)
        return modellist
    
    @staticmethod
    def get_raidevent_recipemaster(model_mgr, recipe_id, using=settings.DB_DEFAULT):
        """レイドイベント交換所のレシピ.
        """
        return BackendApi.get_model(model_mgr, RaidEventRecipeMaster, recipe_id, using=using)
    
    @staticmethod
    def get_raidevent_materialmaster_list(model_mgr, material_id_list, using=settings.DB_DEFAULT):
        """レイドイベント交換所の素材アイテム.
        """
        return BackendApi.get_model_list(model_mgr, RaidEventMaterialMaster, material_id_list, using=using)
    
    @staticmethod
    def get_raidevent_materialmaster(model_mgr, material_id, using=settings.DB_DEFAULT):
        """レイドイベント交換所の素材アイテム.
        """
        return BackendApi.get_model(model_mgr, RaidEventMaterialMaster, material_id, using=using)
    
    @staticmethod
    def get_raidevent_champagne(model_mgr, uid, using=settings.DB_DEFAULT):
        """レイドイベントのシャンパン情報を取得.
        """
        return BackendApi.get_model(model_mgr, RaidEventChampagne, uid, using=using)
    
    @staticmethod
    def get_raidevent_mixdata_dict(model_mgr, uid, recipe_idlist, using=settings.DB_DEFAULT):
        """レイドイベントの交換情報を複数取得.
        """
        idlist = [RaidEventMixData.makeID(uid, recipe_id) for recipe_id in recipe_idlist]
        return BackendApi.get_model_dict(model_mgr, RaidEventMixData, idlist, using=using, key=lambda x:x.mid)
    
    @staticmethod
    def get_raidevent_mixdata(model_mgr, uid, recipe_id, using=settings.DB_DEFAULT):
        """レイドイベントの交換情報を取得.
        """
        return BackendApi.get_raidevent_mixdata_dict(model_mgr, uid, [recipe_id], using=using).get(recipe_id)
    
    @staticmethod
    def get_raidevent_materialdata(model_mgr, uid, using=settings.DB_DEFAULT):
        """レイドイベントの素材情報を取得.
        """
        return BackendApi.get_model(model_mgr, RaidEventMaterialData, uid, using=using)
    
    @staticmethod
    def tr_add_raidevent_champagne(model_mgr, eventmaster, raidboss):
        """シャンパンを加算.
        """
        if eventmaster.champagne_num_max < 1 or eventmaster.champagne_time < 1:
            # SHOWTIMEがないイベント.
            return None
        elif raidboss.raideventraidmaster is None or raidboss.raideventraidmaster.champagne < 1:
            # シャンパンをドロップしないレイド.
            return None
        
        uid = raidboss.raid.oid
        record = raidboss.getDamageRecord(uid)
        if record.champagne:
            # SHOWTIMEの恩恵を受けるレイドでは加算しない.
            return None
        
        champagnedata = BackendApi.get_raidevent_champagne(model_mgr, uid)
        if champagnedata is None:
            champagnedata = RaidEventChampagne.makeInstance(uid)
        
        num_prev = champagnedata.getChampagneNum(eventmaster.id)
        
        if champagnedata.isChampagneCall(eventmaster.id):
            # SHOWTIME状態の時は加算しない.
            return champagnedata
        
        # シャンパンを加算.
        champagnedata.addChampagneNum(eventmaster.id, raidboss.raideventraidmaster.champagne, eventmaster.champagne_num_max)
        num_post = champagnedata.getChampagneNum(eventmaster.id)
        num_add = num_post - num_prev
        
        model_mgr.set_save(champagnedata)
        
        # シャンパンの獲得結果を入れておく(後付).
        record.setChampagneResult(num_post, num_add)
        
        return champagnedata
    
    @staticmethod
    def tr_add_raidevent_material(model_mgr, uid, eventid, num_add_dict):
        """素材アイテムを加算.
        """
        materialdata = BackendApi.get_raidevent_materialdata(model_mgr, uid)
        if materialdata is None:
            materialdata = RaidEventMaterialData.makeInstance(uid)
        else:
            materialdata = RaidEventMaterialData.getByKeyForUpdate(uid)
        
        for material, num_add in num_add_dict.items():
            cur_num = materialdata.getMaterialNum(eventid, material)
            if (num_add + cur_num) < 0:
                raise CabaretError(u'交換用アイテムが足りません', CabaretError.Code.NOT_ENOUGH)
            materialdata.addMaterialNum(eventid, material, num_add)
        
        model_mgr.set_save(materialdata)
        
        return materialdata
    
    @staticmethod
    def tr_raidevent_trade_item(model_mgr, player, eventmaster, recipemaster, trade_num, requestkey):
        """レイドイベント交換所の交換書き込み.
        """
        uid = player.id
        
        # 重複確認.
        BackendApi.tr_update_requestkey(model_mgr, uid, requestkey)
        
        # 在庫確認.
        if 0 < recipemaster.stock:
            mixdata = BackendApi.get_raidevent_mixdata(model_mgr, uid, recipemaster.id)
            if mixdata is None:
                mixdata = RaidEventMixData.makeInstance(RaidEventMixData.makeID(uid, recipemaster.id))
            
            if recipemaster.stock < (mixdata.getCount(recipemaster.eventid) + trade_num):
                raise CabaretError(u'交換可能回数が足りません', CabaretError.Code.OVER_LIMIT)
            
            mixdata.addCount(recipemaster.eventid, trade_num)
            model_mgr.set_save(mixdata)
        
        # 素材消費.
        num_add_dict = dict([(i, -recipemaster.getMaterialNum(i) * trade_num) for i in xrange(Defines.RAIDEVENT_MATERIAL_KIND_MAX)])
        BackendApi.tr_add_raidevent_material(model_mgr, uid, eventmaster.id, num_add_dict)
        
        # 付与.
        presentlist = BackendApi.create_present(model_mgr, 0, uid, recipemaster.itype, recipemaster.itemid, recipemaster.itemnum * trade_num, do_set_save=False)
        for idx, present in enumerate(presentlist):
            present.id = idx
        present_resultset = BackendApi.__tr_receive_present(model_mgr, player, presentlist, [], do_delete=False, cardgetwaytype=Defines.CardGetWayType.RAIDEVENT_MIX)
        for result in present_resultset.values():
            if result == CabaretError.Code.OK:
                continue
            raise CabaretError(u'交換できませんでした', result)
    
    @staticmethod
    def put_raidevent_champagnedata(handler, uid, is_event_page=False):
        """レイドイベントのシャンパン情報.
        """
        model_mgr = handler.getModelMgr()
        # レイドイベント.
        raideventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
        obj = None
        if raideventmaster:
            if not handler.html_param.has_key('raidevent'):
                config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
                handler.html_param['raidevent'] = Objects.raidevent(handler, raideventmaster, config)
            
            if not raideventmaster.flag_dedicated_stage or is_event_page:
                if 0 < raideventmaster.champagne_num_max and 0 < raideventmaster.champagne_time:
                    champagnedata = BackendApi.get_raidevent_champagne(model_mgr, uid, using=settings.DB_READONLY)
                    if champagnedata is None:
                        champagnedata = RaidEventChampagne.makeInstance(uid)
                    obj = Objects.raidevent_champagne(handler, raideventmaster, champagnedata)
        handler.html_param['raidevent_champagne'] = obj
        return obj
    
    @staticmethod
    def make_raidevent_recipe_htmlobj(handler, recipemaster, mixdata=None):
        """html埋め込み用レシピ情報.
        """
        model_mgr = handler.getModelMgr()
        v_player = handler.getViewerPlayer()
        
        uid = v_player.id
        presentlist = BackendApi.create_present(model_mgr, 0, uid, recipemaster.itype, recipemaster.itemid, recipemaster.itemnum, do_set_save=False)
        presentset = PresentSet.presentToPresentSet(model_mgr, [presentlist[0]], using=settings.DB_READONLY)[0]
        
        return Objects.raidevent_recipe(handler, recipemaster, presentset, mixdata)
    
    @staticmethod
    def get_raidevent_is_champagnecall_start(model_mgr, uid, using=settings.DB_DEFAULT):
        """シャンパンコールが開始するかどうかを取得.
        """
        raideventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=using)
        if raideventmaster and 0 < raideventmaster.champagne_num_max and 0 < raideventmaster.champagne_time:
            champagnedata = BackendApi.get_raidevent_champagne(model_mgr, uid, using=using)
            if champagnedata and raideventmaster.champagne_num_max <= champagnedata.getChampagneNum(raideventmaster.id):
                return True
        return False
    
    @staticmethod
    def get_raidevent_is_champagnecall(model_mgr, uid, using=settings.DB_DEFAULT):
        """シャンパンコール中かどうかを取得.
        """
        raideventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=using)
        if raideventmaster and 0 < raideventmaster.champagne_num_max and 0 < raideventmaster.champagne_time:
            champagnedata = BackendApi.get_raidevent_champagne(model_mgr, uid, using=using)
            if champagnedata and champagnedata.isChampagneCall(raideventmaster.id):
                return True
        return False
    
    @staticmethod
    def get_raidevent_stagemaster_list(model_mgr, idlist, using=settings.DB_DEFAULT):
        """ステージを取得.
        """
        return BackendApi.__get_event_stagelist(model_mgr, RaidEventScoutStageMaster, idlist, using=using)
    
    @staticmethod
    def get_raidevent_stagemaster(model_mgr, stageid, using=settings.DB_DEFAULT):
        """ステージを取得.
        """
        return BackendApi.__get_event_stage(model_mgr, RaidEventScoutStageMaster, stageid, using=using)
    
    @staticmethod
    def get_raidevent_next_stagemaster(model_mgr, eventid, stagemaster, using=settings.DB_DEFAULT):
        """次のステージIDを取得.
        """
        return BackendApi.__get_event_nextstage(model_mgr, eventid, stagemaster, using=using)
    
    @staticmethod
    def get_raidevent_stagemaster_by_stagenumber(model_mgr, eventid, stagenumber=None, using=settings.DB_DEFAULT):
        """イベントステージをイベント番号とステージ番号で取得.
        """
        return BackendApi.__get_event_stage_by_stagenumber(model_mgr, RaidEventScoutStageMaster, eventid, stagenumber, using=using)
    
    @staticmethod
    def get_current_raideventstage_master(model_mgr, eventmaster, eventplaydata, using=settings.DB_DEFAULT):
        """ステージを取得.
        """
        return BackendApi.__get_current_eventstage_master(model_mgr, eventmaster, eventplaydata, using=using)
    
    @staticmethod
    def get_raideventstage_playdata(model_mgr, mid, uid, using=settings.DB_DEFAULT, reflesh=False):
        """レイドイベントスカウトデータ取得.
        """
        return BackendApi.__get_eventscout_playdata(model_mgr, RaidEventScoutPlayData, uid, mid, using, reflesh)
    
    @staticmethod
    def tr_do_raidevent_scout(model_mgr, eventmaster, player, stagemaster, key, is_pc, handler=None, champagnecall_start=False, champagnecall=False):
        """レイドイベントスカウト実行.
        """
        now = OSAUtil.get_now()
        
        addloginfo = (lambda x:handler.addloginfo(x)) if handler else (lambda x:None)
        addloginfo('tr_do_raidevent_scout start')
        
        # 重複チェック.
        playdata = BackendApi.__get_eventscout_playdata_forupdate(model_mgr, stagemaster, player.id, key)
        addloginfo('get playdata')
        
        cur_stagemaster = BackendApi.get_current_raideventstage_master(model_mgr, eventmaster, playdata)
        if cur_stagemaster.id != stagemaster.id:
            raise CabaretError(u'実行できないステージです', CabaretError.Code.OVER_LIMIT)
        addloginfo('cur_stagemaster')
        
        # ミッション確認用オブジェクト.
        mission_executer = PanelMissionConditionExecuter()
        
        # 対象のレイド発生テーブル.
        event_happenings = BackendApi.choice_raideventscout_happeningtable(model_mgr, eventmaster, now=now)
        
        # 実行.
        executer = BackendApi.__execute_eventscout(model_mgr, player, stagemaster, playdata, event_happenings=event_happenings)
        
        # ミッション(スカウト実行)を登録.
        mission_executer.addTargetDoScout(executer.exec_cnt)
        
        # SHOWTIME.
        champagnecall_started = False
        if 0 < executer.exec_cnt:
            champagnecall_started = BackendApi.tr_raidevent_start_champagnecall(model_mgr, player.id, champagnecall_start, now)
            champagnecall = champagnecall or champagnecall_started
        
        # 結果を集計.
        prize = executer.aggregatePrizes()
        # 想定外のイベント.
        if prize.get('item', None):
            raise CabaretError(u'想定外のドロップアイテムが設定されています.ScoutMaster.id=%d' % stagemaster.id, CabaretError.Code.INVALID_MASTERDATA)
        
        # 共通部分の結果を反映.
        addloginfo('common result')
        BackendApi.__reflect_eventscout_common_result(model_mgr, executer, prize, player)
        
        # ハプニング.
        happeningevent = prize.get('happening', None)
        if happeningevent: 
            eventvalue = HappeningUtil.make_raideventvalue(eventmaster.id)
            BackendApi.tr_create_happening(model_mgr, player.id, happeningevent.happening, player.level, eventvalue=eventvalue, champagne=champagnecall)
        addloginfo('happening')
        
        # スカウト完了.
        flag_earlybonus = False
        completeevent = prize.get('complete', None)
        if completeevent:
            playdata.progress = executer.progress
            flag_earlybonus = BackendApi.__set_eventscoutstage_complete(model_mgr, stagemaster, playdata, now=now)
            
            # フレンドの近況.
            logdata = RaidEventStageClearLog.makeData(player.id, stagemaster.id)
            BackendApi.tr_add_friendlog(model_mgr, logdata)
            # ログ.
            model_mgr.set_save(UserLogScoutComplete.create(player.id, stagemaster.id, UserLogAreaComplete.EventScoutType.RAID))
            
        addloginfo('complete')
        
        # プレイデータの書き込み.
        if playdata.cleared != stagemaster.stage:
            playdata.progress = executer.progress
        playdata.seed = executer.rand._seed
        playdata.alreadykey = playdata.confirmkey
        playdata.confirmkey = OSAUtil.makeSessionID()
        playdata.setResult(executer.result, executer.eventlist, flag_earlybonus, champagnecall_started=champagnecall_started)
        playdata.ptime = now
        
        # ミッション達成書き込み.
        if not executer.is_levelup:
            # レベルを確認.
            mission_executer.addTargetPlayerLevel(player.level)
        BackendApi.tr_complete_panelmission(model_mgr, player.id, mission_executer, now)
        addloginfo('mission')
        
        def writeEnd():
            if happeningevent:
                # どこでハプニングが発生したかを保存.
                PlayerLastHappeningType.createFromRaidEventScout(playdata.uid).save()
            
            KpiOperator().set_save_scoutevent_stagenumber(playdata.mid, playdata.uid, playdata.stage).save()
        
        model_mgr.add_write_end_method(writeEnd)
        
        model_mgr.set_save(playdata)
        addloginfo('do_raidevent_scout end')
        
        return playdata

    @staticmethod
    def tr_do_produceevent_scout(model_mgr, eventmaster, player, stagemaster, key, is_pc, handler=None, champagnecall_start=False, champagnecall=False):
        """プロデュースイベントスカウト実行.
        """
        now = OSAUtil.get_now()

        addloginfo = (lambda x: handler.addloginfo(x)) if handler else (lambda x: None)
        addloginfo('tr_do_produceevent_scout start')

        # 重複チェック.
        playdata = BackendApi.__get_eventscout_playdata_forupdate(model_mgr, stagemaster, player.id, key)
        addloginfo('get playdata')

        cur_stagemaster = BackendApi.get_current_produceeventstage_master(model_mgr, eventmaster, playdata)
        if cur_stagemaster.id != stagemaster.id:
            raise CabaretError(u'実行できないステージです', CabaretError.Code.OVER_LIMIT)
        addloginfo('cur_stagemaster')

        # ミッション確認用オブジェクト.
        mission_executer = PanelMissionConditionExecuter()

        # 対象のレイド発生テーブル.
        event_happenings = BackendApi.choice_produceeventscout_happeningtable(model_mgr, eventmaster, player.id, now=now)

        # 実行.
        executer = BackendApi.__execute_eventscout(model_mgr, player, stagemaster, playdata,
                                                   event_happenings=event_happenings, is_produceevent=True)

        # ミッション(スカウト実行)を登録.
        mission_executer.addTargetDoScout(executer.exec_cnt)

        # 結果を集計.
        prize = executer.aggregatePrizes()
        # 想定外のイベント.
        if prize.get('item', None):
            raise CabaretError(u'想定外のドロップアイテムが設定されています.ScoutMaster.id=%d' % stagemaster.id, CabaretError.Code.INVALID_MASTERDATA)

        # 共通部分の結果を反映.
        addloginfo('common result')
        BackendApi.__reflect_eventscout_common_result(model_mgr, executer, prize, player)

        # ハプニング.
        happeningevent = prize.get('happening', None)
        if happeningevent:
            eventvalue = HappeningUtil.make_produceeventvalue(eventmaster.id)
            BackendApi.tr_create_producehappening(model_mgr, player.id, happeningevent.happening, player.level, eventvalue=eventvalue)
        addloginfo('happening')

        # スカウト完了.
        flag_earlybonus = False
        completeevent = prize.get('complete', None)
        if completeevent:
            playdata.progress = executer.progress
            flag_earlybonus = BackendApi.__set_eventscoutstage_complete(model_mgr, stagemaster, playdata, now=now)

        addloginfo('complete')

        # プレイデータの書き込み.
        if playdata.cleared != stagemaster.stage:
            playdata.progress = executer.progress
        playdata.seed = executer.rand._seed
        playdata.alreadykey = playdata.confirmkey
        playdata.confirmkey = OSAUtil.makeSessionID()
        playdata.setResult(executer.result, executer.eventlist, flag_earlybonus)
        playdata.ptime = now

        def writeEnd():
            if happeningevent:
                # どこでハプニングが発生したかを保存.
                PlayerLastHappeningType.createFromProduceEventScout(playdata.uid).save()

            KpiOperator().set_save_scoutevent_stagenumber(playdata.mid, playdata.uid, playdata.stage).save()

        model_mgr.add_write_end_method(writeEnd)

        model_mgr.set_save(playdata)
        addloginfo('do_produceevent_scout end')

        return playdata
    
    @staticmethod
    def tr_determine_raidevent_scoutcard(model_mgr, mid, uid, stageid, itemmaster, usenum=1, autosell_rarity=None):
        """スカウトカード獲得.
        """
        # スカウト情報を取得.
        playdata = RaidEventScoutPlayData.getByKeyForUpdate(RaidEventScoutPlayData.makeID(uid, mid))
        return BackendApi.__tr_determine_event_scoutcard(model_mgr, playdata, uid, itemmaster, usenum, autosell_rarity)
    
    @staticmethod
    def make_raidevent_champagnecall_effectparams(handler, raideventmaster, backUrl):
        """シャンパンコール演出のパラメータを作成..
        """
        params = None
        if raideventmaster:
            params = {
                'backUrl' : handler.makeAppLinkUrl(backUrl),
                'pre' : handler.url_static_img + 'event/raidevent/showtime/',
                'cast0' : 'rdev_Cast_01c.png',
                'cast1' : 'rdev_Cast_02c.png',
                'cast2' : 'rdev_Cast_03c.png',
                'cast3' : 'rdev_Cast_04c.png',
            }
        return params
    
    @staticmethod
    def tr_raidevent_stage_clear(model_mgr, eventmaster, player, stage):
        """スカウトステージクリア書き込み.
        """
        BackendApi.__tr_event_stage_clear(model_mgr, eventmaster, player, stage)
        
        # ログ.
        model_mgr.set_save(UserLogAreaComplete.create(player.id, stage.id, UserLogAreaComplete.EventScoutType.RAID))
        
        # フレンドの近況.
        logdata = RaidEventBossWinLog.makeData(player.id, stage.id)
        BackendApi.tr_add_friendlog(model_mgr, logdata)
        
        def writeEnd():
            KpiOperator().set_save_raidevent_stagenumber(eventmaster.id, player.id, stage.stage+1).save()
        model_mgr.add_write_end_method(writeEnd)

    @staticmethod
    def get_raidevent_specialbonusscore(model_mgr, uid, specialcard, specialcard_treasure, deckcardlist, raidid=None, using=settings.DB_DEFAULT, now=None):
        specialsets = {idx for idx in dict(specialcard).keys()}

        bonusscore = 0
        if raidid:
            # help ユーザのポイント
            bonusscore_obj = BackendApi.get_raidevent_helpspecialbonusscore(raidid, uid, using=using)
            if bonusscore_obj:
                bonusscore = bonusscore_obj.bonusscore
        else:
            # レイド発見者のポイント
            bonusscore_obj = BackendApi.get_model(model_mgr, RaidEventSpecialBonusScore, uid, using=using)
            if bonusscore_obj:
                bonusscore = bonusscore_obj.bonusscore

        scores = {}
        for cast in deckcardlist:
            if cast.master.id in specialsets:
                maxscore = scores.get(cast.master.album, 0)
                rarename = Defines.Rarity.NAMES[cast.master.rare]
                newscore = specialcard_treasure.get(rarename)[cast.master.hklevel-1]
                scores[cast.master.album] = max(maxscore, newscore)
        score = sum(scores.values())
        if 0 < score:
            # 称号効果.
            score = BackendApi.reflect_title_effect_percent(model_mgr, score, uid, 'raidevent_point_up', now or OSAUtil.get_now(), using=using, cnt=len(scores))
        return max(score, bonusscore)

    #========================================================================
    # スカウトイベント.
    @staticmethod
    def get_current_scouteventconfig(model_mgr, using=settings.DB_DEFAULT):
        """現在開催中のスカウトイベント設定.
        """
        return BackendApi.__get_current_eventconfig(model_mgr, CurrentScoutEventConfig, using=using)
    
    @staticmethod
    def update_scouteventconfig(mid, starttime, endtime, epilogue_endtime=None, stageschedule=None, present_endtime=None):
        """現在開催中のスカウトイベント設定を更新.
        """
        def tr():
            model_mgr = ModelRequestMgr()
            model = BackendApi.get_model(model_mgr, CurrentScoutEventConfig, CurrentScoutEventConfig.SINGLE_ID, get_instance=True)
            model.starttime = starttime
            model.endtime = endtime
            model.epilogue_endtime = epilogue_endtime or model.endtime
            model.stageschedule = stageschedule or []
            model.present_endtime = present_endtime or model.endtime
            
            if model.mid != mid:
                model.reset_prize_flags()
                
                for model_cls in (UserLogScoutEventTipGet, UserLogScoutEventTipGet):
                    query_string = "truncate table `%s`;" % model_cls.get_tablename()
                    Query.execute_update(query_string, [], False)
            model.mid = mid
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr, model
        model_mgr, model = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        return model
    
    @staticmethod
    def get_scouteventmaster(model_mgr, mid, using=settings.DB_DEFAULT):
        """スカウトイベントマスターデータ取得.
        """
        return BackendApi.get_model(model_mgr, ScoutEventMaster, mid, using=settings.DB_READONLY)
    
    @staticmethod
    def get_scouteventmaster_all(model_mgr, using=settings.DB_DEFAULT):
        """スカウトイベントマスターデータ取得（全て）.
        """
        return model_mgr.get_mastermodel_all(ScoutEventMaster, using=using)
    
    @staticmethod
    def get_current_scouteventmaster(model_mgr, using=settings.DB_DEFAULT, check_schedule=True):
        """現在開催中のスカウトイベント.
        """
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=using)
        if config.mid == 0:
            return None
        if check_schedule and not (config.starttime <= OSAUtil.get_now() < config.endtime):
            return None
        return BackendApi.get_scouteventmaster(model_mgr, config.mid, using=settings.DB_READONLY)
    
    @staticmethod
    def get_current_present_scouteventmaster(model_mgr, using=settings.DB_DEFAULT):
        """現在アイテム交換中のスカウトイベント.
        """
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=using)
        if config.mid == 0:
            return None
        elif not (config.starttime <= OSAUtil.get_now() < config.present_endtime):
            return None
        return BackendApi.get_scouteventmaster(model_mgr, config.mid, using=settings.DB_READONLY)
    
    @staticmethod
    def get_event_stagelist(model_mgr, stageidlist, using=settings.DB_DEFAULT):
        """ステージを取得.
        """
        return BackendApi.__get_event_stagelist(model_mgr, ScoutEventStageMaster, stageidlist, using=using)
    
    @staticmethod
    def get_event_stage(model_mgr, stageid, using=settings.DB_DEFAULT):
        """ステージを取得.
        """
        return BackendApi.__get_event_stage(model_mgr, ScoutEventStageMaster, stageid, using=using)
    
    @staticmethod
    def get_event_stage_by_stagenumber(model_mgr, eventid, stagenumber=None, using=settings.DB_DEFAULT):
        """イベントステージをイベント番号とステージ番号で取得.
        """
        return BackendApi.__get_event_stage_by_stagenumber(model_mgr, ScoutEventStageMaster, eventid, stagenumber, using=using)
    
    @staticmethod
    def get_current_scouteventstage_master(model_mgr, eventmaster, eventplaydata, using=settings.DB_DEFAULT):
        """ステージを取得.
        """
        return BackendApi.__get_current_eventstage_master(model_mgr, eventmaster, eventplaydata, using=using)
    
    @staticmethod
    def get_event_stagelist_filterby_bossprizes(model_mgr, eventid, using=settings.DB_DEFAULT):
        """ボス報酬のあるステージ.
        """
        client = OSAUtil.get_cache_client()
        key = 'get_event_stagelist_filterby_bossprizes:%s' % eventid
        
        stageidlist = client.get(key)
        if stageidlist is None:
            stagemasterlist = ScoutEventStageMaster.fetchValues(filters={'eventid':eventid}, order_by='stage', using=using)
            model_mgr.set_got_models(stagemasterlist)
            
            stageidlist = [stagemaster.id for stagemaster in stagemasterlist if stagemaster.bossprizes]
            client.set(key, stageidlist)
        
        stagemasterlist = BackendApi.get_model_list(model_mgr, ScoutEventStageMaster, stageidlist, using=using)
        stagemasterlist.sort(key=lambda x:x.stage)
        return stagemasterlist
    
    @staticmethod
    def check_event_stage_viewable(model_mgr, mid, stage, uid, using=settings.DB_DEFAULT):
        """指定したステージを閲覧できるかをチェック.
        """
        if stage is None:
            return False
        else:
            config = BackendApi.get_current_scouteventconfig(model_mgr, using=using)
            stage_max = config.get_stage_max()
            if stage_max and stage_max < stage.stage:
                # 期間外.
                return False
            else:
                playdata = model_mgr.get_model(ScoutEventPlayData, ScoutEventPlayData.makeID(uid, mid), using=using)
                if playdata is None:
                    return False
                elif playdata.stage < stage.stage:
                    # 到達していない.
                    return False
        return True
    
    @staticmethod
    def get_event_playdata(model_mgr, mid, uid, using=settings.DB_DEFAULT, reflesh=False):
        """イベントプレイデータ取得.
        """
        return BackendApi.__get_eventscout_playdata(model_mgr, ScoutEventPlayData, uid, mid, using, reflesh)
    
    @staticmethod
    def get_event_stageidlist_by_area(model_mgr, mid, area, using=settings.DB_DEFAULT):
        """エリア名からステージID一覧を取得.
        """
        if EventAreaStageListCache.exists(mid, area):
            idlist = EventAreaStageListCache.getStageIdList(mid, area)
        else:
            idlist = BackendApi._save_event_stageidlist_by_area(model_mgr, mid, area, using=using)
        idlist.sort()
        return idlist
    
    @staticmethod
    def get_event_areaidlist(model_mgr, eventid, using=settings.DB_DEFAULT):
        """エリアIDリストを取得.
        """
        client = localcache.Client()
        key = "firststageidlist:%s" % eventid
        namespace = "scouteventstage"
        stageidlist = client.get(key, namespace)
        
        if stageidlist is None:
            stagemasterlist = ScoutEventStageMaster.fetchValues(filters={'eventid':eventid}, order_by='-stage', using=using)
            model_mgr.set_got_models(stagemasterlist)
            
            areamap = {}
            for stagemaster in stagemasterlist:
                if areamap.has_key(stagemaster.area):
                    continue
                areamap[stagemaster.area] = stagemaster.id
            stageidlist = areamap.values()
            client.set(key, stageidlist, namespace=namespace, time=0)
        
        stagemasterlist = BackendApi.get_event_stagelist(model_mgr, stageidlist, using=using)
        stagemasterlist.sort(key=lambda x:x.stage)
        
        return [stage.area for stage in stagemasterlist]
    
    @staticmethod
    def get_event_stages(model_mgr, stageidlist, using=settings.DB_DEFAULT):
        """ステージを取得.
        """
        return BackendApi.get_model_list(model_mgr, ScoutEventStageMaster, stageidlist, using=using)
    
    @staticmethod
    def check_scoutevent_earlybonus_stage(model_mgr, eventstagemaster, config=None, now=None, using=settings.DB_DEFAULT):
        """早期クリアボーナス対象のステージかを判定.
        """
        config = config or BackendApi.get_current_scouteventconfig(model_mgr, using=using)
        now = now or OSAUtil.get_now()
        return BackendApi.__check_event_earlybonus_stage(model_mgr, eventstagemaster, config, now, using)
    
    @staticmethod
    def tr_scoutevent_send_earlybonus(model_mgr, uid, eventstagemaster, config=None, now=None):
        """早期クリアボーナスを付与.
        """
        now = now or OSAUtil.get_now()
        return BackendApi.__tr_event_send_earlybonus(model_mgr, uid, eventstagemaster, now)
    
    @staticmethod
    def tr_do_scoutevent_stage(model_mgr, eventmaster, player, stagemaster, key, is_pc, friend_num, lovetime=False, handler=None):
        """スカウト実行.
        """
        now = OSAUtil.get_now()
        
        addloginfo = (lambda x:handler.addloginfo(x)) if handler else (lambda x:None)
        addloginfo('tr_do_scoutevent_stage start')
        
        # 重複チェック.
        playdata = BackendApi.__get_eventscout_playdata_forupdate(model_mgr, stagemaster, player.id, key)
        addloginfo('get playdata')
        
        cur_stagemaster = BackendApi.get_current_scouteventstage_master(model_mgr, eventmaster, playdata)
        if cur_stagemaster.id != stagemaster.id:
            raise CabaretError(u'実行できないステージです', CabaretError.Code.OVER_LIMIT)
        addloginfo('cur_stagemaster')
        
        # ミッション確認用オブジェクト.
        mission_executer = PanelMissionConditionExecuter()
        
        # 逢引ラブタイム.
        is_lovetime = False
        if 0 < eventmaster.lovetime_timelimit:
            is_lovetime = playdata.is_lovetime(now=now)
        
        # 今日のハプニング.
        event_happenings = BackendApi.choice_scoutevent_happeningtable(model_mgr, stagemaster, now)
        
        # 実行.
        executer = BackendApi.__execute_eventscout(model_mgr, player, stagemaster, playdata, event_happenings=event_happenings, is_lovetime=is_lovetime)
        
        # ミッション(スカウト実行)を登録.
        mission_executer.addTargetDoScout(executer.exec_cnt)
        
        # 結果を集計.
        prize = executer.aggregatePrizes()
        # 想定外のイベント.
        if prize.get('item', None):
            raise CabaretError(u'想定外のドロップアイテムが設定されています.ScoutMaster.id=%d' % stagemaster.id, CabaretError.Code.INVALID_MASTERDATA)
        
        # 共通部分の結果を反映.
        addloginfo('common result')
        BackendApi.__reflect_eventscout_common_result(model_mgr, executer, prize, player)
        
        # フィーバー発生判定.
        flag_fever = False
        flag_fever_start = False
        if now < playdata.feveretime:
            flag_fever = True
        elif 0 < executer.exec_cnt and 0 < eventmaster.fevertime:
            
            # eventrate_fevere は0.1%単位  例 100:10%
            eventrate_fevere = 0
            if player.level <= 20:
                eventrate_fevere = 100
            elif player.level <= 40:
                eventrate_fevere = 70
            elif player.level <= 50:
                eventrate_fevere = 60
            elif player.level <= 70:
                eventrate_fevere = 40
            elif player.level <= 99:
                eventrate_fevere = 30
            else:
                eventrate_fevere = 15
            pap = player.get_ap() * 100 / player.get_ap_max()
            if pap <= 10:
                eventrate_fevere *= 4
            elif pap <= 20:
                eventrate_fevere *= 3
            elif pap <= 30:
                eventrate_fevere *= 2
            
            if 0 < eventrate_fevere:
                for _ in xrange(executer.exec_cnt):
                    # 実行した回数分判定.
                    if executer.rand.getIntN(1000) < eventrate_fevere:
                        # フィーバー発生
                        playdata.feveretime = now + datetime.timedelta(seconds=eventmaster.fevertime)
                        flag_fever = True
                        flag_fever_start = True
                        break
        addloginfo('fever')
        
        # ハプニング.
        happeningevent = prize.get('happening', None)
        if happeningevent:
            eventvalue = HappeningUtil.make_scouteventvalue(eventmaster.id)
            BackendApi.tr_create_happening(model_mgr, player.id, happeningevent.happening, player.level, eventvalue=eventvalue, champagne=lovetime)
        addloginfo('happening')
        
        # ガチャポイント.
        gachapoint = 0
        gachapointevent = prize.get('eventgacha', None)
        if gachapointevent:
            gachapoint = gachapointevent.point
        addloginfo('eventgacha')
        
        # スカウト完了.
        flag_earlybonus = False
        completeevent = prize.get('complete', None)
        if completeevent:
            playdata.progress = executer.progress
            flag_earlybonus = BackendApi.__set_eventscoutstage_complete(model_mgr, stagemaster, playdata, now=now)
            
            # フレンドの近況.
            logdata = EventStageClearLog.makeData(player.id, stagemaster.id)
            BackendApi.tr_add_friendlog(model_mgr, logdata)
            # ログ.
            model_mgr.set_save(UserLogScoutComplete.create(player.id, stagemaster.id, UserLogAreaComplete.EventScoutType.SCOUT))
            
            def writeCompleteEnd():
                KpiOperator().set_incrment_scoutcomplete_count(stagemaster.id).save()
            model_mgr.add_write_end_method(writeCompleteEnd)
        addloginfo('complete')
        
        # 星.
        star = 0
        is_lovetime_start = False
        lovetime_starevent = prize.get('lovetime_star', None)
        if lovetime_starevent and 0 < eventmaster.lovetime_timelimit:
            star = lovetime_starevent.num
            # 星加算.
            if not is_lovetime:
                playdata.star += star
                # 逢引ラブタイム発生判定.
                if 0 < eventmaster.lovetime_star <= playdata.star:
                    playdata.set_lovetime(now, eventmaster.lovetime_timelimit)
                    is_lovetime_start = True
        
        # スカウトイベントポイント.
        point = prize['point']
        pointeffect = 0
        if 0 < point or 0 < gachapoint:
            if 0 < point:
                point += friend_num
                if flag_fever:
                    point *= 2
                
                effects = BackendApi.aggregate_effect_specialcard(model_mgr, player, eventmaster.specialcard)
                effect = sum(effects.values())
                if effect > 1:
                    effect_percent = effect * 100
                    # 称号効果.
                    effect_percent = BackendApi.reflect_title_effect_percent(model_mgr, effect_percent, player.id, 'scoutevent_point_up', now, cnt=len(effects))
                    pointeffect = int(point * (effect_percent - 100) / 100)
                    point += pointeffect
            addloginfo('calc')
            
            BackendApi.tr_add_scoutevent_score(model_mgr, eventmaster, player.id, point, gachapoint, logger=addloginfo)
        addloginfo('point')
        
        # プレイデータの書き込み.
        if playdata.cleared != stagemaster.stage:
            playdata.progress = executer.progress
        playdata.seed = executer.rand._seed
        playdata.alreadykey = playdata.confirmkey
        playdata.confirmkey = OSAUtil.makeSessionID()
        playdata.setResult(executer.result, executer.eventlist, (point, pointeffect), flag_fever_start, flag_earlybonus, is_lovetime_start=is_lovetime_start)
        playdata.ptime = now
        
        # ミッション達成書き込み.
        if not executer.is_levelup:
            # レベルを確認.
            mission_executer.addTargetPlayerLevel(player.level)
        BackendApi.tr_complete_panelmission(model_mgr, player.id, mission_executer, now)
        addloginfo('mission')
        
        def writeEnd():
            ope = KpiOperator()
            ope.set_save_scoutevent_stagenumber(playdata.mid, playdata.uid, playdata.stage)
            ope.set_save_scoutevent_play(playdata.uid, now, is_pc)
            ope.save()
            
            if happeningevent:
                # どこでハプニングが発生したかを保存.
                PlayerLastHappeningType.createFromScoutEvent(playdata.uid).save()
        
        model_mgr.add_write_end_method(writeEnd)
        
        model_mgr.set_save(playdata)
        addloginfo('do_event_stage end')
    
    @staticmethod
    def get_num_event_play_friend(model_mgr, mid, player, now):
        """スカウトイベント実行友達数取得.
        """
        # フレンドのID.
        friendidlist = BackendApi.get_friend_idlist(player.id, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
        playerloginlist = BackendApi.get_model_list(model_mgr, PlayerLogin, friendidlist, using=settings.DB_READONLY)
        # 当日ログインした人について検索.
        idlist = [ScoutEventPlayData.makeID(playerlogin.id, mid) for playerlogin in playerloginlist if DateTimeUtil.judgeSameDays(playerlogin.lbtime, now)]
        
        playdatalist = BackendApi.get_model_list(model_mgr, ScoutEventPlayData, idlist, using=settings.DB_READONLY)
        cnt = 0
        for playdata in playdatalist:
            if playdata.ptime:
                if DateTimeUtil.judgeSameDays(playdata.ptime, now):
                    cnt += 1
        
        return cnt
    
    @staticmethod
    def get_event_apcost(stagemaster, player, is_full=None):
        """消費行動力.
        """
        if isinstance(stagemaster, ScoutEventStageMaster) and player.level < Defines.BIGINNER_PLAYERLEVEL:
            return 0
        # レイドイベントのスカウトでは初心者設定はないみたいなのでコメントアウト.
#        if isinstance(stagemaster, EventScoutStageMaster) and player.level < Defines.BIGINNER_PLAYERLEVEL:
#            return 0
        elif settings_sub.IS_BENCH:
            return 0
        return getattr(stagemaster, 'apcost_full', stagemaster.apcost) if is_full else stagemaster.apcost
    
    @staticmethod
    def aggregate_effect_specialcard(model_mgr, player, specialcard, cardlist=None, effect_getter=None):
        """特攻カード効果集計.
        """
        if effect_getter is None:
            effect_getter = lambda x:x
        specialcard = dict(specialcard)
        if cardlist is None:
            deck = BackendApi.get_deck(player.id, model_mgr, using=settings.DB_READONLY)
            raiddeck = BackendApi.get_raid_deck(player.id, model_mgr, using=settings.DB_READONLY)
            cardidlist = list(set(deck.to_array() + raiddeck.to_array()))
            cardlist = BackendApi.get_cards(cardidlist, model_mgr, using=settings.DB_READONLY)
        sp_hk = {}
        sp_effect = {}
        for cardset in cardlist:
            if specialcard.has_key(cardset.master.id):
                eff = effect_getter(specialcard[cardset.master.id])
                if not sp_hk.has_key(cardset.master.album) or sp_hk[cardset.master.album] < cardset.master.hklevel:
                    sp_hk[cardset.master.album] = cardset.master.hklevel
                    sp_effect[cardset.master.album] = eff
        return sp_effect
    
    @staticmethod
    def calc_effect_specialcard(model_mgr, player, specialcard, cardlist=None, effect_getter=None, default_value=1):
        """特攻カード効果算出.
        """
        sp = BackendApi.aggregate_effect_specialcard(model_mgr, player, specialcard, cardlist, effect_getter)
        return sum(sp.values()) if sp else default_value
    
    @staticmethod
    def get_event_next_stage(model_mgr, eventid, stagemaster, using=settings.DB_DEFAULT):
        """次のステージIDを取得.
        """
        return BackendApi.__get_event_nextstage(model_mgr, eventid, stagemaster, using=using)
    
    @staticmethod
    def tr_determine_scoutevent_scoutcard(model_mgr, mid, uid, stageid, itemmaster, usenum=1, autosell_rarity=None):
        """スカウトカード獲得.
        """
        # スカウト情報を取得.
        playdata = ScoutEventPlayData.getByKeyForUpdate(ScoutEventPlayData.makeID(uid, mid))
        return BackendApi.__tr_determine_event_scoutcard(model_mgr, playdata, uid, itemmaster, usenum, autosell_rarity)
    
    @staticmethod
    def _save_event_stageidlist_by_areaname(model_mgr, mid, areaname, using=settings.DB_DEFAULT):
        """エリア名からステージID一覧を保存.
        """
        stagelist = ScoutEventStageMaster.fetchValues(filters={'eventid':mid, 'areaname':areaname}, using=using)
        stageidlist = [stage.id for stage in stagelist]
        return stageidlist
    
    @staticmethod
    def check_event_boss_playable(playdata, stagemaster):
        """ボスと戦える状態かチェック.
        """
        if playdata is None:
            return False
        if stagemaster is None:
            return False
        
        if stagemaster.stage == playdata.stage == playdata.cleared and playdata.progress >= stagemaster.execution:
            return True
        return False
    
    @staticmethod
    def tr_add_scoutevent_score(model_mgr, eventmaster, uid, point=0, gachapoint=0, tip=0, logger=None):
        """スカウトイベントのスコアを加算.
        """
        if point == 0 and gachapoint == 0 and tip == 0:
            return
        
        if logger is None:
            logger = lambda x:None
        
        eventid = eventmaster.id
        
        key = ScoutEventScore.makeID(uid, eventid)
        tmp = model_mgr.get_model(ScoutEventScore, key)
        if tmp is None:
            model = ScoutEventScore.makeInstance(key)
            model_mgr.set_got_models([model])
            model_mgr.set_got_models_forupdate([model])
        else:
            model = model_mgr.get_model_forupdate(ScoutEventScore, key)
        logger('get score')
        
        # プレゼント用のハート所持数を加算.
        if point != 0:
            if eventmaster.is_produce:
                def forUpdatePresentNum(model, inserted, point):
                    model.point += point
                model_mgr.add_forupdate_task(ScoutEventPresentNum, ScoutEventPresentNum.makeID(uid, eventid), forUpdatePresentNum, point)
                logger('update present num')
            
            point_pre = model.point_total
            model.point += point
            model.point_total += point
            
            if 0 < point:
                # ポイント達成報酬.
                point_min = point_pre+1
                point_max = model.point_total
                table = eventmaster.get_pointprizes(point_min, point_max)
                logger('get_pointprizes')
                if table:
                    keys = table.keys()
                    keys.sort()
                    
                    prizeidlist = []
                    for key in keys:
                        if point_min <= key <= point_max:
                            prizeidlist.extend(table[key])
                    prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
                    logger('get prize %d' % len(prizeidlist))
                    BackendApi.tr_add_prize(model_mgr, uid, prizelist, eventmaster.pointprize_text)
                    logger('add prize')
            logger('prize end')
            
            def writeEndScore():
                pipe = ScoutEventRanking.getDB().pipeline()
                ScoutEventRanking.create(eventid, uid, model.point_total).save(pipe)
                if BackendApi.check_scoutevent_beginer(model_mgr, uid, eventmaster, using=settings.DB_READONLY):
                    ScoutEventRankingBeginer.create(eventid, uid, model.point_total).save(pipe)
                pipe.execute()
                KpiOperator().set_save_scoutevent_point(eventid, uid, model.point_total).save()
            model_mgr.add_write_end_method(writeEndScore)
        
        if gachapoint != 0:
            logger('gachapoint start')
            point_pre = model.point_gacha
            model.point_gacha += gachapoint
            if model.point_gacha < 0:
                raise CabaretError(u'ガチャPTが足りません', CabaretError.Code.NOT_ENOUGH)
            model_mgr.set_save(UserLogScoutEventGachaPt.create(uid, eventmaster.id, point_pre, model.point_gacha, gachapoint))
            logger('gachapoint end')
        
        if tip != 0:
            logger('tip start')
            model.tip += tip
            if model.tip < 0:
                raise CabaretError(u'チップが足りません', CabaretError.Code.NOT_ENOUGH)
            logger('tip end')
        
        model_mgr.set_save(model)
        
        return model
    
    @staticmethod
    def _save_event_stageidlist_by_area(model_mgr, mid, area, using=settings.DB_DEFAULT):
        """エリア番号からステージID一覧を保存.
        """
        stagelist = ScoutEventStageMaster.fetchValues(filters={'eventid':mid, 'area':area}, using=using)
        stageidlist = [stage.id for stage in stagelist]
        EventAreaStageListCache.save(mid, area, stageidlist)
        return stageidlist
    
    @staticmethod
    def tr_scoutevent_stage_clear(model_mgr, eventmaster, player, stage):
        """スカウトステージクリア書き込み.
        """
        BackendApi.__tr_event_stage_clear(model_mgr, eventmaster, player, stage)
        
        # ログ.
        model_mgr.set_save(UserLogAreaComplete.create(player.id, stage.id, UserLogAreaComplete.EventScoutType.SCOUT))
        
        # フレンドの近況.
        logdata = EventBossWinLog.makeData(player.id, stage.id)
        BackendApi.tr_add_friendlog(model_mgr, logdata)
        
        def writeEnd():
            KpiOperator().set_save_scoutevent_stagenumber(eventmaster.id, player.id, stage.stage+1).save()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def get_scoutevent_scorerecords(model_mgr, mid, uidlist, using=settings.DB_DEFAULT):
        """スカウトイベントの得点レコード.
        """
        idlist = [ScoutEventScore.makeID(uid, mid) for uid in uidlist]
        modellist = BackendApi.get_model_list(model_mgr, ScoutEventScore, idlist, using=using)
        dic = dict([(model.uid, model) for model in modellist])
        return dic
    
    @staticmethod
    def get_scoutevent_scorerecord(model_mgr, mid, uid, using=settings.DB_DEFAULT):
        """スカウトイベントの得点レコードを単体取得.
        """
        return BackendApi.get_scoutevent_scorerecords(model_mgr, mid, [uid], using=using).get(uid, None)
    
    @staticmethod
    def get_scoutevent_flagrecords(model_mgr, mid, uidlist, using=settings.DB_DEFAULT):
        """スカウトイベントのフラグレコード.
        """
        idlist = [ScoutEventFlags.makeID(uid, mid) for uid in uidlist]
        modellist = BackendApi.get_model_list(model_mgr, ScoutEventFlags, idlist, using=using)
        dic = dict([(model.uid, model) for model in modellist])
        return dic
    
    @staticmethod
    def get_scoutevent_flagrecord(model_mgr, mid, uid, using=settings.DB_DEFAULT):
        """スカウトイベントのフラグレコードを単体取得.
        """
        return BackendApi.get_scoutevent_flagrecords(model_mgr, mid, [uid], using=using).get(uid, None)
    
    @staticmethod
    def check_scoutevent_lead_opening(model_mgr, uid, eventid=None, using=settings.DB_DEFAULT):
        """スカウトイベントのオープニングに誘導するべきかをチェック.
        """
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
        eventid = eventid or config.mid
        if config.mid == 0 or config.mid != eventid or not (config.starttime <= OSAUtil.get_now() < config.endtime):
            # 開催中じゃない.
            return False
        
        flagrecord = BackendApi.get_scoutevent_flagrecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
        if flagrecord is None or not (config.starttime <= flagrecord.opvtime < config.endtime):
            return True
        else:
            return False
    
    @staticmethod
    def check_scoutevent_lead_epilogue(model_mgr, uid, eventid=None, using=settings.DB_DEFAULT):
        """エピローグの誘導チェック.
        """
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=using)
        eventid = eventid or config.mid
        now = OSAUtil.get_now()
        if config.mid == 0 or config.mid != eventid or now < config.endtime or config.epilogue_endtime < now:
            return False
        
        flagrecord = BackendApi.get_scoutevent_flagrecord(model_mgr, eventid, uid, using=using)
        if flagrecord and config.starttime <= flagrecord.opvtime and flagrecord.epvtime < flagrecord.opvtime:
            return True
        else:
            return False
    
    @staticmethod
    def update_scouteventflagrecord(mid, uid, opvtime=None, epvtime=None):
        """スカウトイベントのフラグレコードを更新.
        """
        def tr():
            model_mgr = ModelRequestMgr()
            model = BackendApi.get_model(model_mgr, ScoutEventFlags, ScoutEventFlags.makeID(uid, mid), get_instance=True)
            model.opvtime = opvtime or model.opvtime
            model.epvtime = epvtime or model.epvtime
            
            if opvtime:
                # ミッション.
                mission_executer = PanelMissionConditionExecuter()
                mission_executer.addTargetViewEventOpening()
                BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
            
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr, model
        model_mgr, model = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        return model
    
    @staticmethod
    def get_scoutevent_score(mid, uid):
        """スカウトイベントのスコアを取得.
        """
        return BackendApi.get_ranking_score(ScoutEventRanking, mid, uid)
    
    @staticmethod
    def get_scoutevent_rank(mid, uid, is_beginer=False):
        """スカウトイベントのランキング順位を取得.
        """
        return BackendApi.get_ranking_rank(ScoutEventRankingBeginer if is_beginer else ScoutEventRanking, mid, uid)
    
    @staticmethod
    def get_scoutevent_rankindex(mid, uid, is_beginer=False):
        """スカウトイベントのランキング順位(index)を取得.
        """
        return BackendApi.get_ranking_rankindex(ScoutEventRankingBeginer if is_beginer else ScoutEventRanking, mid, uid)
    
    @staticmethod
    def get_scoutevent_rankernum(mid, is_beginer=False):
        """スカウトイベントのランキング人数を取得.
        """
        return BackendApi.get_ranking_rankernum(ScoutEventRankingBeginer if is_beginer else ScoutEventRanking, mid)
    
    @staticmethod
    def fetch_uid_by_scouteventrank(mid, limit, offset=0, withrank=False, is_beginer=False):
        """スカウトイベントのランキングを範囲取得.
        """
        return BackendApi.fetch_uid_by_rankingrank(ScoutEventRankingBeginer if is_beginer else ScoutEventRanking, mid, limit, offset, withrank)
    
    @staticmethod
    def set_scoutevent_fever(model_mgr, mid, uid, sec):
        """スカウトイベントフィーバー発生.
        """
        now = OSAUtil.get_now()
        playdata = ScoutEventPlayData.getByKeyForUpdate(ScoutEventPlayData.makeID(uid, mid))
        playdata.feveretime = now + datetime.timedelta(seconds=sec)
        model_mgr.set_save(playdata)
    
    @staticmethod
    def save_kpi_scoutevent_join(uid, is_pc, now=None, kpi_operator=None):
        """スカウトイベント参加のKPIを保存.
        """
        local_kpi_operator = kpi_operator or KpiOperator()
        local_kpi_operator.set_save_scoutevent_join(uid, now, is_pc)
        if kpi_operator is None:
            local_kpi_operator.save()
        return local_kpi_operator
    
    @staticmethod
    def get_scoutevent_presentprizemaster(model_mgr, eventid, number, using=settings.DB_DEFAULT):
        """ハートプレゼントのマスターデータを取得.
        """
        modelid = ScoutEventPresentPrizeMaster.makeID(eventid, number)
        return BackendApi.get_model(model_mgr, ScoutEventPresentPrizeMaster, modelid, using=using)
    
    @staticmethod
    def get_scoutevent_presentprizemaster_by_eventid(model_mgr, eventid, using=settings.DB_DEFAULT):
        """スカウトイベントのIDを指定してハートプレゼントのマスターデータを取得.
        """
        if not ScoutEventPresentPrizeNumberList.exists(eventid):
            modellist = ScoutEventPresentPrizeMaster.fetchValues(filters={'eventid' : eventid}, using=using)
            ScoutEventPresentPrizeNumberList.save(eventid, modellist)
        else:
            numberlist = ScoutEventPresentPrizeNumberList.get(eventid)
            idlist = [ScoutEventPresentPrizeMaster.makeID(eventid, number) for number in numberlist]
            modellist = BackendApi.get_model_list(model_mgr, ScoutEventPresentPrizeMaster, idlist, using=using)
        modellist.sort(key=lambda x:x.number, reverse=True)
        return modellist
    
    @staticmethod
    def get_scoutevent_presentnums_record(model_mgr, mid, uid, get_instance=False, using=settings.DB_DEFAULT):
        """スカウトイベントのハートプレゼント数レコードを取得.
        """
        modelid = ScoutEventPresentNum.makeID(uid, mid)
        return BackendApi.get_model(model_mgr, ScoutEventPresentNum, modelid, get_instance=get_instance, using=using)
    
    @staticmethod
    def tr_scoutevent_add_presentpointnum(model_mgr, uid, presentprizemaster, reqkey):
        """スカウトイベントのハートプレゼント数を加算.
        """
        eventid = presentprizemaster.eventid
        number = presentprizemaster.number
        
        # 重複防止用のキー書き込み.
        BackendApi.tr_update_requestkey(model_mgr, uid, reqkey)
        
        # ポイントのレコード.
        modelid = ScoutEventPresentNum.makeID(uid, eventid)
        record = BackendApi.get_model(model_mgr, ScoutEventPresentNum, modelid)
        if record is None:
            raise CabaretError(u'ハートを持っていません', code=CabaretError.Code.OVER_LIMIT)
        record = ScoutEventPresentNum.getByKeyForUpdate(modelid)
        if record.point == 0:
            raise CabaretError(u'ハートを持っていません', code=CabaretError.Code.OVER_LIMIT)
        
        # 全投入した時の報酬を検索.
        point = record.point
        point_pre = record.get_num(number)
        prizetable = presentprizemaster.get_pointprizes(point_pre+1, point_pre+point)
        if prizetable:
            # その中で直近のポイント.
            pointlist = prizetable.keys()
            pointlist.sort()
            
            # 実際に投入するポイント.
            target_prize_point = pointlist[0]
            if (target_prize_point - point_pre) <= point:
                point = target_prize_point - point_pre
                
                # 報酬.
                prizeidlist = prizetable[target_prize_point]
                prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
                # 報酬付与.
                BackendApi.tr_add_prize(model_mgr, uid, prizelist, presentprizemaster.prize_text)
        
        # ポイントの減算.
        record.point -= point
        
        # 投入数を加算.
        record.add_num(number, point)
        point_post = record.get_num(number)
        
        # 結果を保存.
        record.result_number = number
        record.result_pointpre = point_pre
        record.result_pointpost = point_post
        
        model_mgr.set_save(record)
    
    @staticmethod
    def make_scoutevent_presentprizeinfo(handler, presentprizemaster, presentprizerecord):
        """プロデュースプレゼント項目作成.
        """
        model_mgr = handler.getModelMgr()
        
        number = presentprizemaster.number
        
        # 現在のポイント.
        cur_point = presentprizerecord.get_num(number) if presentprizerecord else 0
        
        # 次の報酬.
        prize_table = presentprizemaster.get_pointprizes(cur_point+1)
        prizepoint = None
        prizeinfo = None
        if prize_table:
            pointlist = prize_table.keys()
            pointlist.sort()
            prizepoint = pointlist[0]
            
            prizeidlist = prize_table[prizepoint]
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY)
            prizeinfo = BackendApi.make_prizeinfo(handler, prizelist, using=settings.DB_READONLY)
        
        return Objects.scoutevent_present(handler, presentprizemaster, cur_point, prizepoint, prizeinfo)
    
    @staticmethod
    def check_scoutevent_beginer(model_mgr, uid, eventmaster, config=None, now=None, using=settings.DB_DEFAULT):
        """スカウトイベント初心者確認.
        """
        if config is None:
            config = BackendApi.get_current_scouteventconfig(model_mgr, using)
        if not config or config.mid != eventmaster.id:
            return False
        return BackendApi.check_event_beginer(model_mgr, uid, eventmaster.beginer_days, config.starttime, now=now, using=using)
    
    @staticmethod
    def get_scoutevent_raidmaster_by_eventid(model_mgr, eventid, using=settings.DB_DEFAULT):
        """スカウトイベントのレイドマスターデータ.
        """
        client = OSAUtil.get_cache_client()
        key = 'get_raidevent_raidmaster_by_eventid:%s' % eventid
        
        midlist = client.get(key)
        if midlist is None:
            modellist = RaidEventRaidMaster.fetchValues(filters={'eventid':eventid}, using=using)
            midlist = [model.mid for model in modellist]
            client.set(key, midlist)
        else:
            modellist = BackendApi.get_raidevent_raidmasters(model_mgr, eventid, midlist, using=using).values()
        modellist.sort(key=lambda x:x.id)
        return modellist
    
    @staticmethod
    def get_scoutevent_raidmasters(model_mgr, eventid, midlist, using=settings.DB_DEFAULT):
        """スカウトイベントのレイドマスターデータ.
        """
        idlist = [ScoutEventRaidMaster.makeID(eventid, mid) for mid in midlist]
        return BackendApi.get_model_dict(model_mgr, ScoutEventRaidMaster, idlist, get_instance=True, using=using, key=lambda x:x.mid)
    
    @staticmethod
    def get_scoutevent_raidmaster(model_mgr, eventid, mid, using=settings.DB_DEFAULT):
        """スカウトイベントのレイドマスターデータ.
        """
        return BackendApi.get_scoutevent_raidmasters(model_mgr, eventid, [mid], using).get(mid)
    
    @staticmethod
    def get_scoutevent_tanzakumaster_list(model_mgr, eventid, numberlist, using=settings.DB_DEFAULT):
        """スカウトイベントの短冊キャストマスターデータ.
        """
        idlist = [ScoutEventTanzakuCastMaster.makeID(eventid, number) for number in numberlist]
        return BackendApi.get_model_list(model_mgr, ScoutEventTanzakuCastMaster, idlist, using=using)
    
    @staticmethod
    def get_scoutevent_tanzakumaster(model_mgr, eventid, number, using=settings.DB_DEFAULT):
        """スカウトイベントの短冊キャストマスターデータ.
        """
        return BackendApi.get_model(model_mgr, ScoutEventTanzakuCastMaster, ScoutEventTanzakuCastMaster.makeID(eventid, number), using=using)
    
    @staticmethod
    def get_scoutevent_tanzakumaster_by_eventid(model_mgr, eventid, using=settings.DB_DEFAULT):
        """スカウトイベントの短冊キャストマスターデータをイベントIDで絞り込む.
        """
        client = OSAUtil.get_cache_client()
        key = 'get_scoutevent_tanzakumaster_by_eventid:{}'.format(eventid)
        
        numberlist = client.get(key)
        if numberlist is None:
            modellist = ScoutEventTanzakuCastMaster.fetchValues(filters={'eventid':eventid}, using=using)
            numberlist = [model.number for model in modellist]
            client.set(key, numberlist)
        else:
            modellist = BackendApi.get_scoutevent_tanzakumaster_list(model_mgr, eventid, numberlist, using=using)
        modellist.sort(key=lambda x:x.id)
        return modellist
    
    @staticmethod
    def get_scoutevent_tanzakucastdata(model_mgr, uid, eventid, using=settings.DB_DEFAULT, forupdate=False):
        """スカウトイベントの短冊データ.
        """
        tanzakudata = BackendApi.get_model(model_mgr, ScoutEventTanzakuCastData, ScoutEventTanzakuCastData.makeID(uid, eventid), using=using)
        if forupdate:
            if tanzakudata is None:
                tanzakudata = ScoutEventTanzakuCastData.makeInstance(ScoutEventTanzakuCastData.makeID(uid, eventid))
                model_mgr.set_got_models([tanzakudata])
                model_mgr.set_got_models_forupdate([tanzakudata])
            else:
                tanzakudata = model_mgr.get_model_forupdate(ScoutEventTanzakuCastData, ScoutEventTanzakuCastData.makeID(uid, eventid))
        return tanzakudata
    
    @staticmethod
    def tr_scoutevent_raiddestroy(model_mgr, viewer_uid, raidboss, eventid, outside=False):
        """スカウトイベントレイド討伐成功.
        """
        if eventid == 0:
            # イベントレイドじゃない.
            return
        
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr)
        if eventmaster is None or eventid != eventmaster.id:
            # イベントが発生していない.
            return
        
        # イベント用の設定を一応反映.
        eventvalue = HappeningUtil.make_scouteventvalue(eventid)
        BackendApi.reset_raidboss_eventraidmaster(model_mgr, raidboss, eventvalue)
        if raidboss.scouteventraidmaster is None:
            # イベント用の設定がない.
            return
        eventraidmaster = raidboss.scouteventraidmaster
        
        # 短冊配布.
        oid = raidboss.raid.oid
        is_update_tanzaku = False
        for uid in raidboss.getDamageRecordUserIdList():
            record = raidboss.getDamageRecord(uid)
            if record.damage_cnt < 1:
                # 参加していない.
                continue
            
            flag = bool(BackendApi.judge_raidprize_distribution_outside_userid(uid, viewer_uid, oid, True))
            
            tanzaku_rate = eventraidmaster.tanzaku_rate if uid == oid else eventraidmaster.tanzaku_help_rate
            if tanzaku_rate <= random.randint(0, 99):
                # ドロップしなかった.
                continue
            
            tanzaku_number = eventraidmaster.tanzaku_number if uid == oid else eventraidmaster.tanzaku_help_number
            
            if outside:
                tanzaku_num = record.tanzaku_num
            else:
                tanzaku_min, tanzaku_max = (eventraidmaster.tanzaku_randmin, eventraidmaster.tanzaku_randmax) if uid == oid else (eventraidmaster.tanzaku_help_randmin, eventraidmaster.tanzaku_help_randmax)
                tanzaku_num = random.randint(tanzaku_min, tanzaku_max)
                if record.champagne:
                    # 逢引ラブタイムの恩恵を受ける.
                    tanzaku_num += int(tanzaku_num * eventmaster.lovetime_tanzakuup / 100)
                
                if 0 < tanzaku_num:
                    record.setTanzakuResult(tanzaku_num, 0)
            
            if flag == outside:
                # 通常時は外部で行うユーザーは配布しない.
                # 外部処理では外部で行うユーザーだけ配布.
                # 短冊の配布.
                if 0 < tanzaku_num:
                    num_add_dict = {
                        tanzaku_number : tanzaku_num
                    }
                    tanzakudata = BackendApi.tr_scoutevent_add_tanzaku(model_mgr, uid, eventid, num_add_dict)
                    
                    # 素材数を設定.
                    record.setTanzakuResult(tanzaku_num, tanzakudata.get_tanzaku(tanzaku_number))
                    
                    is_update_tanzaku = True
        
        if outside and is_update_tanzaku:
            raidboss.refrectDamageRecord()
            model_mgr.set_save(raidboss.raid)
    
    @staticmethod
    def tr_scoutevent_nominate_cast(model_mgr, uid, eventid, tanzakucastmaster):
        """短冊キャスト指名.
        """
        tanzakudata = BackendApi.get_scoutevent_tanzakucastdata(model_mgr, uid, eventid, forupdate=True)
        if tanzakucastmaster:
            if tanzakudata.current_cast != -1:
                model_mgr.delete_models_from_cache(ScoutEventTanzakuCastData, [ScoutEventTanzakuCastData.makeID(uid, eventid)])
                raise CabaretError(u'すでに指名済みです', CabaretError.Code.ALREADY_RECEIVED)
            
            tanzakudata.current_cast = tanzakucastmaster.number
            num_add_dict = {
                tanzakucastmaster.number : -tanzakucastmaster.tanzaku,
            }
            BackendApi.tr_scoutevent_add_tanzaku(model_mgr, uid, eventid, num_add_dict)
        else:
            if tanzakudata.current_cast == -1:
                raise CabaretError(u'すでに指名済みです', CabaretError.Code.ALREADY_RECEIVED)
            
            tanzakudata.current_cast = -1
        model_mgr.set_save(tanzakudata)
    
    @staticmethod
    def tr_scoutevent_add_tanzaku(model_mgr, uid, eventid, num_add_dict):
        """短冊加算.
        """
        tanzakudata = BackendApi.get_scoutevent_tanzakucastdata(model_mgr, uid, eventid, forupdate=True)
        
        for tanzaku_number, num_add in num_add_dict.items():
            cur_num = tanzakudata.get_tanzaku(tanzaku_number)
            if (num_add + cur_num) < 0:
                raise CabaretError(u'短冊が足りません', CabaretError.Code.NOT_ENOUGH)
            
            tanzakudata.set_tanzaku(tanzaku_number, num_add + cur_num)
        
        model_mgr.set_save(tanzakudata)
        
        def writeEnd():
            ope = KpiOperator()
            for k,v in num_add_dict.items():
                if 0 < v:
                    ope.set_increment_scoutevent_get_tanzaku(uid, k, v)
            ope.save()
        model_mgr.add_write_end_method(writeEnd)
        
        return tanzakudata
    
    @staticmethod
    def tr_scoutevent_add_tip(model_mgr, uid, eventid, num_add_dict):
        """チップ加算.
        """
        tanzakudata = BackendApi.get_scoutevent_tanzakucastdata(model_mgr, uid, eventid, forupdate=True)
        
        for tanzaku_number, num_add in num_add_dict.items():
            cur_num = tanzakudata.get_tip(tanzaku_number)
            if (num_add + cur_num) < 0:
                raise CabaretError(u'チップが足りません', CabaretError.Code.NOT_ENOUGH)
            
            tanzakudata.set_tip(tanzaku_number, num_add + cur_num)
        
        model_mgr.set_save(tanzakudata)
        
        return tanzakudata
    
    @staticmethod
    def tr_scoutevent_populate_tip(model_mgr, uid, eventmaster, tip):
        """チップを投入.
        """
        eventid = eventmaster.id
        
        tanzakudata = BackendApi.get_scoutevent_tanzakucastdata(model_mgr, uid, eventid, forupdate=True)
        num_add_dict = {
            tanzakudata.current_cast : tip,
        }
        # 指名状態を解除.
        BackendApi.tr_scoutevent_nominate_cast(model_mgr, uid, eventid, None)
        
        # チップを加算.
        BackendApi.tr_scoutevent_add_tip(model_mgr, uid, eventid, num_add_dict)
        
        # 現在のチップ数を減算.
        BackendApi.tr_add_scoutevent_score(model_mgr, eventmaster, uid, tip=-tip)
        
        def writeEnd():
            ope = KpiOperator()
            for k,v in num_add_dict.items():
                ope.set_increment_scoutevent_consume_tip(uid, k, v)
            ope.save()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def tr_scoutevent_trade_tip(model_mgr, uid, eventmaster, tanzakumaster, num, confirmkey):
        """短冊をチップに交換.
        """
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        
        eventid = eventmaster.id
        tipnum = tanzakumaster.tip_rate * num
        
        num_add_dict = {
            tanzakumaster.number : -num,
        }
        # 短冊を減算.
        tanzakudata = BackendApi.tr_scoutevent_add_tanzaku(model_mgr, uid, eventid, num_add_dict)
        
        # 所持チップ数を加算.
        scorerecord = BackendApi.tr_add_scoutevent_score(model_mgr, eventmaster, uid, tip=tipnum)
        
        # 履歴.
        model_mgr.set_save(UserLogScoutEventTipGet.create(uid, eventid, tanzakumaster.number, num, tanzakudata.get_tanzaku(tanzakumaster.number), tipnum, scorerecord.tip))
    
    @staticmethod
    def put_scoutevent_tanzakudata(handler, uid, check_schedule=True):
        """短冊情報をHTMLに埋め込む.
        """
        model_mgr = handler.getModelMgr()
        # スカウトイベント.
        scouteventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY, check_schedule=check_schedule)
        obj_tanzakulist = None
        if scouteventmaster:
            if not handler.html_param.has_key('scoutevent'):
                config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
                handler.html_param['scoutevent'] = Objects.scouteventmaster(handler, scouteventmaster, config)
            
            # 短冊のマスターデータ.
            tanzakumasterlist = BackendApi.get_scoutevent_tanzakumaster_by_eventid(model_mgr, scouteventmaster.id, using=settings.DB_READONLY)
            if tanzakumasterlist:
                # 短冊所持情報.
                tanzakudata = BackendApi.get_scoutevent_tanzakucastdata(model_mgr, uid, scouteventmaster.id, using=settings.DB_READONLY)
                
                obj_tanzakulist = [Objects.scoutevent_tanzaku(handler, tanzakumaster, tanzakudata) for tanzakumaster in tanzakumasterlist]
                
                if not check_schedule:
                    config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
                    if not (config.starttime <= OSAUtil.get_now() < config.endtime):
                        # イベント終了.
                        result_model = BackendApi.get_model(model_mgr, ScoutEventCastPerformanceResult, scouteventmaster.id, using=settings.DB_READONLY)
                        if result_model:
                            rankingdata = {}
                            arr = result_model.get_tip_all().items()
                            arr.sort(key=lambda x:x[1], reverse=True)
                            rank = 0
                            tip_tmp = None
                            for number, tip in arr:
                                if tip_tmp is None or tip_tmp != tip:
                                    rank += 1
                                rankingdata[number] = dict(rank=rank, tip=tip)
                            handler.html_param['scoutevent_tanzaku_rankingdata'] = rankingdata
        
        handler.html_param['scoutevent_tanzaku_list'] = obj_tanzakulist
        return obj_tanzakulist
    
    @staticmethod
    def choice_scoutevent_happeningtable(model_mgr, stagemaster, now):
        """レイド出現テーブルを選択..
        """
        logintime = DateTimeUtil.toLoginTime(now)
        wday = logintime.weekday()
        happeningtablemaster = BackendApi.get_model(model_mgr, ScoutEventHappeningTableMaster, ScoutEventHappeningTableMaster.makeID(stagemaster.eventid, wday), using=settings.DB_READONLY)
        return happeningtablemaster.happenings if happeningtablemaster else stagemaster.happenings
    
    #===========================================================
    # バトルイベント.
    @staticmethod
    def get_current_battleeventconfig(model_mgr, using=settings.DB_DEFAULT):
        """現在開催中のバトルイベント設定.
        """
        return BackendApi.__get_current_eventconfig(model_mgr, CurrentBattleEventConfig, using=using)
    
    @staticmethod
    def update_battleeventconfig(mid=None, starttime=None, endtime=None, epilogue_endtime=None,ticketendtime=None, is_emergency=False, rankschedule=None):
        """現在開催中のバトルイベント設定を更新.
        """
        def tr():
            model_mgr = ModelRequestMgr()
            model = BackendApi.get_model(model_mgr, CurrentBattleEventConfig, CurrentBattleEventConfig.SINGLE_ID, get_instance=True)
            model.starttime = starttime or model.starttime
            model.endtime = endtime or model.endtime
            model.is_emergency = is_emergency
            model.daily_prize_flag = model.daily_prize_flag or 0
            model.daily_prize_date = model.daily_prize_date or datetime.date.today()
            model.epilogue_endtime = epilogue_endtime or model.endtime
            model.ticket_endtime = ticketendtime or model.endtime
            model.rankschedule = rankschedule if rankschedule is not None else (model.rankschedule or [])
            
            if mid is not None:
                if model.mid != mid:
                    model.prize_flag = 0
                    model.beginer_prize_flag = 0
                    model.daily_prize_flag = 0
                    model.daily_prize_date = datetime.date.today()
                model.mid = mid
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr, model
        model_mgr, model = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        return model
    
    @staticmethod
    def is_battleevent_open(model_mgr, using=settings.DB_DEFAULT, now=None):
        """バトルイベントが開催中か.
        """
        return BackendApi.get_current_battleevent_master(model_mgr, using=using, now=now) is not None
    
    @staticmethod
    def get_battleevent_battle_endtime(model_mgr, using=settings.DB_DEFAULT, now=None, do_check_emergency=True):
        """バトルイベントのバトル終了時間.
        """
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=using)
        if do_check_emergency and config.is_emergency:
            return None
        now = now or OSAUtil.get_now()
        tomorrow = now + datetime.timedelta(days=1)
        etime = min(config.endtime, DateTimeUtil.toLoginTime(tomorrow) - datetime.timedelta(seconds=10800))
        return etime
    
    @staticmethod
    def is_battleevent_battle_open(model_mgr, using=settings.DB_DEFAULT, now=None, do_check_emergency=True):
        """バトルイベントのバトルを受け付けているか
        """
        now = now or OSAUtil.get_now()
        etime = BackendApi.get_battleevent_battle_endtime(model_mgr, using, now, do_check_emergency=do_check_emergency)
        if etime is None or etime <= now:
            return False
        return BackendApi.is_battleevent_open(model_mgr, using, now)
    
    @staticmethod
    def get_battleevent_master(model_mgr, mid, using=settings.DB_DEFAULT):
        """バトルイベントのマスターデータの取得.
        """
        return BackendApi.get_model(model_mgr, BattleEventMaster, mid, using=using)
    
    @staticmethod
    def get_current_battleevent_master(model_mgr, using=settings.DB_DEFAULT, now=None):
        """現在のバトルイベントのマスターデータの取得.
        """
        now = now or OSAUtil.get_now()
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=using)
        if config and config.mid and config.starttime <= now < config.endtime:
            return BackendApi.get_battleevent_master(model_mgr, config.mid, using=using)
        else:
            return None
    
    @staticmethod
    def get_battleevent_rankmaster_dict(model_mgr, eventid, ranklist, using=settings.DB_DEFAULT):
        """バトルイベントのランクマスター取得.
        """
        idlist = [BattleEventRankMaster.makeID(eventid, rank) for rank in ranklist]
        modellist = BackendApi.get_model_list(model_mgr, BattleEventRankMaster, idlist, using=using)
        return dict([(model.rank, model) for model in modellist])
    
    @staticmethod
    def get_battleevent_rankmaster(model_mgr, eventid, rank, using=settings.DB_DEFAULT):
        """バトルイベントのランクマスター取得.
        """
        return BackendApi.get_battleevent_rankmaster_byId(model_mgr, BattleEventRankMaster.makeID(eventid, rank), using=using)
    
    @staticmethod
    def get_battleevent_rankmaster_byId(model_mgr, rankid, using=settings.DB_DEFAULT):
        """バトルイベントのランクマスター取得.
        """
        return BackendApi.get_model(model_mgr, BattleEventRankMaster, rankid, using=using)
    
    @staticmethod
    def get_battleevent_rankmaster_by_eventid(model_mgr, eventid, using=settings.DB_DEFAULT, do_check_open=True):
        """バトルイベントのランクマスター取得.
        """
        client = OSAUtil.get_cache_client()
        key = "get_battleevent_rankmaster_by_eventid:%s" % eventid
        midlist = client.get(key)
        if midlist is None:
            masterlist = BattleEventRankMaster.fetchValues(filters={'eventid':eventid}, using=using)
            midlist = [master.id for master in masterlist]
            client.set(key, midlist)
        
        master_list = BackendApi.get_model_list(model_mgr, BattleEventRankMaster, midlist, using=using)
        if do_check_open:
            config = BackendApi.get_current_battleeventconfig(model_mgr, using=using)
            if config.mid == eventid:
                rank_max = config.getRankMax()
                if rank_max is not None:
                    master_list = [master for master in master_list if master.rank <= rank_max]
        return master_list
    
    @staticmethod
    def get_battleevent_maxrankmaster(model_mgr, eventid, using=settings.DB_DEFAULT):
        """バトルイベントの最大ランクのマスター取得.
        """
        masterdict = dict([(master.rank, master) for master in BackendApi.get_battleevent_rankmaster_by_eventid(model_mgr, eventid, using=using)])
        if not masterdict:
            return None
        ranklist = masterdict.keys()
        ranklist.sort(reverse=True)
        return masterdict[ranklist[0]]
    
    @staticmethod
    def get_battleevent_piecemaster(model_mgr, eventid, using=settings.DB_DEFAULT):
        """バトルイベントピースマスター取得
        """
        client = localcache.Client()
        key = "get_battleevent_piecemaster:%s" % eventid
        midlist = client.get(key)

        if midlist is None:
            masterlist = BattleEventPieceMaster.fetchValues(filters={'eventid':eventid}, excludes={'name':'piece_r'}, using=using)
            masterlist.sort(key=lambda x:x.number)
            midlist = [master.id for master in masterlist]
            client.set(key, midlist)

        master_list = BackendApi.get_model_list(model_mgr, BattleEventPieceMaster, midlist, using=using)
        return master_list
    
    @staticmethod
    def get_battleevent_piecemaster_by_piecenumber(model_mgr, eventid, piecenumber, using=settings.DB_DEFAULT):
        """piecenumberからBattleEventPieceMasterを取得.
        """
        ins_id = BattleEventPieceMaster.makeID(eventid, piecenumber)
        return BackendApi.get_model(model_mgr, BattleEventPieceMaster, ins_id, using=using)
    
    @staticmethod
    def check_battleevent_piececollection_userdata_and_create(model_mgr, uid, eventid):
        """ユーザの全てのレアリティでピースのコレクションデータを存在確認。全レアリティ分作成。"""
        piecemaster_list = BackendApi.get_battleevent_piecemaster(model_mgr, eventid, using=settings.DB_READONLY)
        if not piecemaster_list:
            return
        
        # 必要なレアリティ.
        rarity_list = [piecemaster.number for piecemaster in piecemaster_list]
        
        # 作成済みのユーザーデータ.
        userdata_list = BackendApi.get_user_piece_all_rarity_list(model_mgr, uid, eventid, using=settings.DB_READONLY)
        userdata_dict = dict([(userdata.rarity, userdata) for userdata in userdata_list])
        
        # 足りないrarity.
        not_found_rarity_list = list(set(rarity_list) - set(userdata_dict.keys()))
        if not not_found_rarity_list:
            return
        
        # 足りない分を作成.
        def tr(uid, eventid, not_found_rarity_list):
            model_mgr = ModelRequestMgr()
            modellist = []
            for rarity in not_found_rarity_list:
                model = BattleEventPieceCollection.get_or_create_instance(uid, eventid, rarity)
                model_mgr.set_save(model)
                modellist.append(model)
            model_mgr.write_all()
            model_mgr.write_end()
            return modellist
        modellist = db_util.run_in_transaction(tr, uid, eventid, not_found_rarity_list)
        
        # 取得済みの状態にしておく.
        for using in [settings.DB_DEFAULT, settings.DB_READONLY]:
            model_mgr.set_got_models(modellist, using)

    @staticmethod
    def get_rank_master_from_user_rank(model_mgr, uid, eventid):
        """ユーザーのランクに合わせたマスターデータを取得"""
        user_rank = BackendApi.get_battleevent_rankrecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
        if not user_rank:
            raise CabaretError(u'ユーザーデータがバトルイベントに存在しません.')
        rank_master_list = BackendApi.get_battleevent_rankmaster_by_eventid(model_mgr, eventid, using=settings.DB_READONLY)
        for master in rank_master_list:
            if master.rank == user_rank.rank:
                return master
        raise CabaretError(u'イベントランクのマスターデータとユーザーデータが一致しません.', CabaretError.Code.INVALID_MASTERDATA)

    @staticmethod
    def get_user_piece_all_rarity_list(model_mgr, uid, eventid, using=settings.DB_DEFAULT):
        piecemaster_list = BackendApi.get_battleevent_piecemaster(model_mgr, eventid, using=settings.DB_READONLY)
        if not piecemaster_list:
            return []
        
        ins_id_list = [BattleEventPieceCollection.makeID(uid, eventid, piecemaster.number) for piecemaster in piecemaster_list]
        modellist = BackendApi.get_model_list(model_mgr, BattleEventPieceCollection, ins_id_list, using=using)
        modellist.sort(key=lambda x:x.rarity)
        return modellist

    @staticmethod
    def save_kpi_battleevent_piece_collect(rarity):
        """バトルイベント時のピースの取得 KPI を保存.
        """
        kpi_operator = KpiOperator()
        kpi_operator.set_save_battleevent_piece_collect(rarity)
        kpi_operator.save()
        return kpi_operator

    @staticmethod
    def get_piececomplete_prize_card_list(eventid):
        """ピースコンプリート時の報酬カード ID の取得"""
        model_mgr = ModelRequestMgr()
        piecemaster = sorted(BackendApi.get_battleevent_piecemaster(model_mgr, eventid, using=settings.DB_READONLY), key=lambda x:x.number)
        cardid_list = [x.complete_prize for x in piecemaster]
        return cardid_list

    @staticmethod
    def get_userdata_piece_complete_prize_cardid(uid, eventid, rarity):
        model_mgr = ModelRequestMgr()
        userdata = BattleEventPieceCollection.get_or_create_instance(uid, eventid, rarity)
        #cardid_list = BackendApi.get_piececomplete_prize_card_list(eventid)
        """
        cardid_list would not contain piece_r, as a result its length is 4.
        userdata.rarity is 4 therefore the cardid_list[userdata.rarity] would return an index out of bounds error
        """
        piecemaster_list = BackendApi.get_battleevent_piecemaster(model_mgr, eventid, using=settings.DB_READONLY)
        cardid_dict = {master.number: master.complete_prize for master in piecemaster_list}
        return cardid_dict[userdata.rarity]
    
    @staticmethod
    def tr_battleevent_pieceresult(model_mgr, uid, eventmaster, eventrankmaster, is_win, rival_key):
        """ピースの為の結果書き込み処理.
        """
        eventid = eventmaster.id
        
        piece_master_list = BackendApi.get_battleevent_piecemaster(model_mgr, eventid, using=settings.DB_READONLY)
        if not piece_master_list:
            # ピース非対応.
            return None
        
        victory_count = BackendApi.tr_do_battleevent_continue_victory_count(model_mgr, uid, eventid, is_win)
        if not is_win:
            return None
        
        # 確率計算.
        if eventrankmaster.max_rise < victory_count:
            victory_count = eventrankmaster.max_rise
        
        rival_rise = 0
        if rival_key:
            rival_rise = eventrankmaster.rival_rise
        
        total_point = eventrankmaster.base_drop + rival_rise + (eventrankmaster.rise * victory_count)
        if 100 < total_point:
            total_point = 100
        
        if not BackendApi.do_battleevent_drop_lottery(total_point):
            # はずれ.
            return None
        
        # ピース獲得.
        return BackendApi.tr_do_get_piece_or_items(model_mgr, uid, eventmaster, eventrankmaster)
    
    @staticmethod
    def tr_do_get_piece_or_items(model_mgr, uid, eventmaster, eventrankmaster):
        """ユーザーにピースもしくはアイテムを配布する"""
        eventid = eventmaster.id
        
        rarity = BattleEventPieceCollection.select_rarity_box(eventrankmaster.rarity)
        userdata = BattleEventPieceCollection.get_or_create_instance(uid, eventid, rarity)
        
        # piece の取得処理。戻り値は取得したピースのフィールド名。
        get_piece = userdata.piece_or_item_drop()
        
        piece_master_list = BackendApi.get_battleevent_piecemaster(model_mgr, eventid, using=settings.DB_READONLY)
        piecemaster = BackendApi.get_battleevent_piecemaster_instance(rarity, piece_master_list)
        is_complete = userdata.is_complete()
        is_item = get_piece.get('is_item') or False
        piecedata = {
#             'image': piecemaster.name, # 画像の path
            'piece': get_piece.get('piece'),  # piece_number を数字で
            'rarity': rarity, # r, hr, sr, ssr のどれかを文字列で
            'is_complete': is_complete and not is_item,
            'is_item' : is_item,
        }
        
        if is_complete:
            # ピースコンプリート処理
            if userdata.do_complete_process(piecemaster.complete_cnt_max):
                # キャストの配布
                prize_cardid = CardMaster.getByKey(piecemaster.complete_prize).id
                prizelist = [PrizeData.create(cardid=prize_cardid, cardnum=1)]
                textid = piecemaster.complete_prize_text
            else:
                # 報酬の配布
                prizeids = userdata.item_lottery(piecemaster.item_lottery)
                prizelist = BackendApi.get_prizelist(model_mgr, prizeids, using=settings.DB_READONLY)
                textid = piecemaster.complete_item_prize_text
                piecedata['item_prizeids'] = prizeids
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)

        if get_piece:
            model_mgr.set_save(userdata)
            def writeEnd():
                BackendApi.save_kpi_battleevent_piece_collect(rarity)
            model_mgr.add_write_end_method(writeEnd)
        
        return piecedata

    @staticmethod
    def get_battleevent_piecemaster_instance(rarity, piece_master_list):
        instance = filter(lambda m:m.number == rarity, piece_master_list)
        if instance:
            return instance[0]
        else:
            raise CabaretError(u'バトルイベントのピースマスターデータと取得ピースのレアリティが一致しません.', CabaretError.Code.INVALID_MASTERDATA)

    @staticmethod
    def get_battleevent_continue_victory(model_mgr, uid, eventid, using=settings.DB_DEFAULT):
        ins_id = BattleEventContinueVictory.makeID(uid, eventid)
        userdata = BackendApi.get_model(model_mgr, BattleEventContinueVictory, ins_id, using=using)
        if userdata is None:
            userdata = BattleEventContinueVictory.get_or_create_instance(uid, eventid)
            model_mgr.delete_models_from_cache(BattleEventContinueVictory, [ins_id])
            for db in set([using, settings.DB_DEFAULT]):
                model_mgr.set_got_models([userdata], db)
        return userdata

    @staticmethod
    def tr_do_battleevent_continue_victory_count(model_mgr, uid, eventid, is_win):
        """バトルイベント勝利時のカウントアップ、リセット処理"""
        continue_victory = BattleEventContinueVictory.get_or_create_instance(uid, eventid)
        if is_win:
            # 連勝数カウントアップ
            continue_victory.count_up()
        else:
            # 連勝数リセット
            continue_victory.reset_count()
        model_mgr.set_save(continue_victory)
        
        return continue_victory.count

    @staticmethod
    def cache_battleevent_userdata(model_mgr, uid):
        #３００人分の自分のトータルデッキコストと近いユーザを取ってくる。
        # ログイン時間の計算はコレで
        ltime = BackendApi.get_model(model_mgr, PlayerLogin, uid, using=settings.DB_READONLY).ltime
        LoginTimeSet.create(uid, ltime).save()

        # Deck cost の計算
        deck = BackendApi.get_deck(uid, using=settings.DB_READONLY).to_array()
        cost = sum([x.master.cost for x in BackendApi.get_cards(deck)])

        BattleEventOppRivalListCost.create(uid, cost).save()
        LIMIT = 300
        uid_list = []
        for cost_range in (0, 30, 50, 100, 200):
            uid_list.extend(BattleEventOppRivalListCost.fetch_by_cost(cost, cost_range, cost_range, limit=LIMIT - len(uid_list), ignorelist=[uid] + uid_list))

            if LIMIT <= len(uid_list):
                break

        return uid_list
        
#         # redis にキャッシュ
#         data = BattleEventOppRivalList.create(uid, cost, ltime)
#         data.update()
# 
#         return data.get()

    @staticmethod
    def do_battleevent_drop_lottery(total_point):
        lottery_lists = [[True, total_point], [False, 100-total_point]]
        return BattleEventPieceCollection.is_drop_lottery(lottery_lists)

    @staticmethod
    def get_battleevent_rival(model_mgr, uid):
        """ライバルの選出: 人件費がプレイヤーに近いユーザを 10 人選んで抽選する。"""
        uid = int(uid)
        uid_list = BackendApi.cache_battleevent_userdata(model_mgr, uid)
        
        def get_active_user_id_list():
            client = OSAUtil.get_cache_client()
            key = '___get_active_user_id_list'
            uidlist = client.get(key)
            if uidlist is None:
                now = OSAUtil.get_now()
                uidlist = LoginTimeSet.fetch(now - datetime.timedelta(seconds=21600), now)
                client.set(key, uidlist, time=1800)
            return uidlist
        active_uid_list = list(set(get_active_user_id_list()))
        
        if len(uid_list) < 10:
            for _ in xrange(min(len(active_uid_list), 300)):
                active_uid = random.choice(active_uid_list)
                if uid == active_uid or active_uid in uid_list:
                    continue
                uid_list.append(active_uid)
        random.shuffle(uid_list)

        return uid_list[:10]

#         player = user_dict.get(uid)
#         rival_list = []
#         cost_dict = {}
# 
#         # 時間のチェック方法 (6 時間以内のログインかどうか)
#         for id, userdata in user_dict.iteritems():
#             if 21600 < (OSAUtil.get_now() - userdata['ltime']).total_seconds():
#                 pass
#             elif cost_dict.get(userdata['deckcost']):
#                 cost_dict[userdata['deckcost']].append(int(id))
#             else:
#                 cost_dict[userdata['deckcost']] = [int(id)]
# 
#         array = []
#         for cost, user_list in cost_dict.iteritems():
#             array.append(cost)
# 
#         if not player['deckcost'] in array:
#             cost_dict[player['deckcost']] = [uid]
#             array.append(player['deckcost'])
# 
#         array.sort()
#         index = array.index(player['deckcost'])
#         lower_list = sorted(array[:index], reverse=True)
#         upper_list = sorted(array[index:])
#         count = 0
#         for lower, upper in zip(lower_list, upper_list):
#             rival_list += cost_dict.get(lower) + cost_dict.get(upper)
#             count += 1
#             if 10 < len(rival_list):
#                 break
# 
#         if upper_list[count:] and len(upper_list) < 10:
#             for upper in upper_list[count:]:
#                 rival_list += cost_dict[upper]
# 
#         if lower_list[count:] and len(lower_list) < 10:
#             for lower in lower_list[count:]:
#                 rival_list += cost_dict[lower]
# 
#         if uid in rival_list:
#             rival_list.remove(uid)
#         return rival_list[:10]

    @staticmethod
    def make_is_rival_strings(oid, eventid):
        """対戦者がライバルかどうかを認識する為のハッシュ値を生成"""
        sha1 = hashlib.sha1(str(oid))
        sha1.update(str(eventid))
        return sha1.hexdigest()

    @staticmethod
    def get_rival_key(oid, eventid, request_key):
        """ライバルキーの取得。request_key が UrlArgs オブジェクトである事に注意。"""
        rival_index = BackendApi._check_is_rival_strings(oid, eventid, request_key)
        if not rival_index is None:
            rival_key = request_key.get(rival_index)
        else:
            rival_key = None
        return rival_key

    @staticmethod
    def _check_is_rival_strings(oid, eventid, request_key):
        """対戦者がライバルかどうかを確認"""
        if request_key:
            sha1 = BackendApi.make_is_rival_strings(oid, eventid)
            if sha1 in request_key.args:
                return request_key.args.index(sha1)
        return None

#     @staticmethod
#     def save_userdata(uid, eventid):
#         BattleEventPieceCollection.make_all_rarity_and_save(uid, eventid)

    @staticmethod
    def get_battleevent_flagrecord(model_mgr, eventid, uid, using=settings.DB_DEFAULT):
        """バトルイベントのフラグレコードの取得.
        """
        return BackendApi.get_model(model_mgr, BattleEventFlags, BattleEventFlags.makeID(uid, eventid), using=using)
    
    @staticmethod
    def update_battleevent_flagrecord(eventid, uid, opvtime=None, epvtime=None, scvtime=None):
        """バトルイベントのフラグレコードの更新.
        """
        def tr():
            dmin = OSAUtil.get_datetime_min()
            model_mgr = ModelRequestMgr()
            model = BackendApi.get_model(model_mgr, BattleEventFlags, BattleEventFlags.makeID(uid, eventid), get_instance=True)
            model.opvtime = opvtime or model.opvtime
            model.epvtime = epvtime or model.epvtime or dmin
            model.scvtime = scvtime or model.scvtime or dmin
            
            if opvtime:
                # ミッション.
                mission_executer = PanelMissionConditionExecuter()
                mission_executer.addTargetViewEventOpening()
                BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
            
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr, model
        model_mgr, model = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        return model
    
    @staticmethod
    def check_battleevent_lead_opening(model_mgr, uid, eventid=None, using=settings.DB_DEFAULT):
        """オープニングの誘導チェック.
        """
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=using)
        eventid = eventid or config.mid
        if config.mid == 0 or config.mid != eventid or not (config.starttime <= OSAUtil.get_now() < config.endtime):
            return False
        
        flagrecord = BackendApi.get_battleevent_flagrecord(model_mgr, eventid, uid, using=using)
        if flagrecord is None or not (config.starttime <= flagrecord.opvtime < config.endtime):
            return True
        else:
            return False
    
    @staticmethod
    def check_battleevent_lead_epilogue(model_mgr, uid, eventid=None, using=settings.DB_DEFAULT):
        """エピローグの誘導チェック.
        """
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=using)
        eventid = eventid or config.mid
        now = OSAUtil.get_now()
        if config.mid == 0 or config.mid != eventid or now < config.endtime or config.epilogue_endtime < now:
            return False
        
        flagrecord = BackendApi.get_battleevent_flagrecord(model_mgr, eventid, uid, using=using)
        if flagrecord and config.starttime <= flagrecord.opvtime and flagrecord.epvtime < flagrecord.opvtime:
            return True
        else:
            return False
    
    @staticmethod
    def check_battleevent_lead_scenario(model_mgr, uid, eventid=None, using=settings.DB_DEFAULT):
        """中押し演出の誘導チェック.
        """
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=using)
        eventid = eventid or config.mid
        master = BackendApi.get_battleevent_master(model_mgr, eventid, using=using)
        if master is None or not master.is_goukon:
            return False
        
        now = OSAUtil.get_now()
        if config.mid == 0 or config.mid != eventid or now < config.starttime or config.endtime < now:
            return False
        
        rank_open_time = config.getNewbieRankOpenTime(now)
        if rank_open_time is None or rank_open_time < config.starttime:
            return False
        
        flagrecord = BackendApi.get_battleevent_flagrecord(model_mgr, eventid, uid, using=using)
        if flagrecord and config.starttime <= flagrecord.opvtime and flagrecord.scvtime < rank_open_time:
            return True
        else:
            return False
    
    @staticmethod
    def get_battleevent_scorerecord_dict(model_mgr, eventid, uidlist, get_instance=False, using=settings.DB_DEFAULT):
        """バトルイベントのスコアレコードの取得.
        """
        modellist = BackendApi.get_model_list(model_mgr, BattleEventScore, [BattleEventScore.makeID(uid, eventid) for uid in uidlist], get_instance=get_instance, using=using)
        return dict([(model.uid, model) for model in modellist])
    
    @staticmethod
    def get_battleevent_scorerecord(model_mgr, eventid, uid, using=settings.DB_DEFAULT):
        """バトルイベントのスコアレコードの取得.
        """
        return BackendApi.get_battleevent_scorerecord_dict(model_mgr, eventid, [uid], using=using).get(uid)
    
    @staticmethod
    def get_battleevent_score_per_rank_record(model_mgr, uid, eventid, rank, using=settings.DB_READONLY):
        """バトルイベントのランク別スコア情報.
        """
        mid = BattleEventScorePerRank.makeMid(eventid, rank)
        key = BattleEventScorePerRank.makeID(uid, mid)
        return BackendApi.get_model(model_mgr, BattleEventScorePerRank, key, get_instance=True, using=using)
    
    @staticmethod
    def get_battleevent_battleresult(model_mgr, eventid, uid, using=settings.DB_DEFAULT):
        """バトルイベントのバトル結果を取得.
        """
        scorerecord = BackendApi.get_battleevent_scorerecord(model_mgr, eventid, uid, using=using)
        if scorerecord and scorerecord.result:
            return model_mgr.get_model(BattleResult, scorerecord.result, using=using)
        else:
            return None
    
    @staticmethod
    def tr_add_battleevent_battlepoint(model_mgr, eventmaster, uid, eventrankmaster, point, now=None, is_win=None, scorerecord=None):
        """バトルポイントの加算.
        is_winを指定しない場合は連勝数を変更しない.
        """
        if point == 0:
            return
        
        tmp = {}
        eventid = eventmaster.id
        p_key = BattleEventScore.makeID(uid, eventid)
        
        def forUpdate(model, inserted):
            if is_win is None:
                model.addPoint(point, now=now)
            else:
                model.addPointWithBattleResult(point, is_win, now=now)
            tmp['model'] = model
        
        if scorerecord is None:
            model_mgr.add_forupdate_task(BattleEventScore, p_key, forUpdate)
        else:
            forUpdate(scorerecord, False)
        
        # ポイント達成報酬.
        if 0 < point:
            # ランク別の獲得ポイント.
            p_key = BattleEventScorePerRank.makeID(uid, BattleEventScorePerRank.makeMid(eventid, eventrankmaster.rank))
            model = BackendApi.get_model(model_mgr, BattleEventScorePerRank, p_key, using=settings.DB_DEFAULT)
            if model is None:
                model = BattleEventScorePerRank.makeInstance(p_key)
                model.insert()
            else:
                model = BattleEventScorePerRank.getByKeyForUpdate(p_key)
            point_pre = model.point
            model.point += point
            model_mgr.set_save(model)
            
            # ポイント達成報酬.
            point_min = point_pre+1
            point_max = model.point
            table = eventrankmaster.get_battlepointprizes(point_min, point_max)
            prizelist = None
            if table:
                keys = table.keys()
                keys.sort()
                prizeidlist = []
                for key in keys:
                    prizeidlist.extend(table[key])
                prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
                BackendApi.tr_add_prize(model_mgr, uid, prizelist, eventrankmaster.battlepointprize_text)
        
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            
            if 0 < point:
                logintime = DateTimeUtil.toLoginTime(now or OSAUtil.get_now())
                rankingid = BattleEventDailyRanking.makeRankingId(logintime, eventid, eventrankmaster.rank)
                BattleEventDailyRanking.create(rankingid, uid, tmp['model'].point).save(pipe)
            BattleEventRanking.create(eventid, uid, tmp['model'].point_total).save(pipe)
            if BackendApi.check_battleevent_beginer(model_mgr, uid, eventmaster, using=settings.DB_READONLY):
                BattleEventRankingBeginer.create(eventid, uid, tmp['model'].point_total).save(pipe)
            
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def get_battleevent_rankrecord_dict(model_mgr, eventid, uidlist, using=settings.DB_DEFAULT):
        """バトルイベントのランクレコードの取得.
        """
        modellist = BackendApi.get_model_list(model_mgr, BattleEventRank, [BattleEventRank.makeID(uid, eventid) for uid in uidlist], using=using)
        return dict([(model.uid, model) for model in modellist])
    
    @staticmethod
    def get_battleevent_rankrecord(model_mgr, eventid, uid, using=settings.DB_DEFAULT):
        """バトルイベントのランクレコードの取得.
        """
        return BackendApi.get_battleevent_rankrecord_dict(model_mgr, eventid, [uid], using=using).get(uid)
    
    @staticmethod
    def check_battleevent_loginbonus_received(model_mgr, uid, eventid=None, using=settings.DB_DEFAULT, now=None):
        """バトルイベントのログインボーナスを受け取ったか.
        """
        now = now or OSAUtil.get_now()
        
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=using)
        eventid = eventid or config.mid
        if config.mid == 0 or config.mid != eventid or not (config.starttime <= now < config.endtime):
            return True
        
        rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventid, uid, using=using)
        return rankrecord is None or not rankrecord.isNeedUpdate(config, now=now)
    
    @staticmethod
    def __tr_battleevent_receive_famebonus(model_mgr, eventmaster, rankrecord):
        """名声ポイント達成報酬受取ボーナス受け取り.
        """
        uid = rankrecord.uid
        table = eventmaster.get_pointprizes(rankrecord.fame + 1, rankrecord.fame_next)
        
        prizelist = None
        if table:
            keys = table.keys()
            keys.sort()
            
            prizeidlist = []
            for key in keys:
                prizeidlist.extend(table[key])
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, eventmaster.pointprize_text)
        return prizelist
    
    @staticmethod
    def tr_battleevent_receive_loginbonus(model_mgr, eventmaster, uid, now):
        """バトルイベントログインボーナス受け取り.
        """
        # ランクレコード取得.
        ins_id = BattleEventRank.makeID(uid, eventmaster.id)
        rankrecord = BackendApi.get_model(model_mgr, BattleEventRank, ins_id)
        if rankrecord is None:
            rankrecord = BattleEventRank.makeInstance(ins_id)
            rankrecord.insert()
        rankrecord = model_mgr.get_model_forupdate(BattleEventRank, ins_id)
        
        config = BackendApi.get_current_battleeventconfig(model_mgr)
        
        # 受取済み確認.
        if config.is_emergency:
            raise CabaretError(u'event emergency..', CabaretError.Code.EVENT_CLOSED)
        elif not rankrecord.isNeedUpdate(config, now):
            raise CabaretError(u'Already received.', CabaretError.Code.ALREADY_RECEIVED)
        
        # 現在のランクの報酬.
        cur_rank = rankrecord.getRank(config, now)
        rankmaster = BackendApi.get_battleevent_rankmaster(model_mgr, eventmaster.id, cur_rank)
        if rankmaster.loginbonus:
            prizelist = BackendApi.get_prizelist(model_mgr, rankmaster.loginbonus)
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, rankmaster.loginbonus_text)
        
        # 名声ポイント報酬.
        BackendApi.__tr_battleevent_receive_famebonus(model_mgr, eventmaster, rankrecord)
        
        # グループ内ランキング報酬.
        prizerecord_id = BattleEventGroupRankingPrize.makeID(uid, eventmaster.id)
        prizerecord = model_mgr.get_model(BattleEventGroupRankingPrize, prizerecord_id)
        if prizerecord:
            prizerecord = BattleEventGroupRankingPrize.getByKeyForUpdate(prizerecord_id)
            if not prizerecord.fixed and prizerecord.prizes:
                for prizerecord_data in prizerecord.prizes:
                    prizeidlist = prizerecord_data['prizes']
                    textid = prizerecord_data['text']
                    prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
                    BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
                prizerecord.fixed = True
                model_mgr.set_save(prizerecord)
        
        received_data = {
            'fame' : rankrecord.fame,
            'fame_next' : rankrecord.fame_next,
            'rank' : rankrecord.rank,
            'rank_next' : rankrecord.rank_next,
        }
        
        # ランクレコードの更新.
        rankrecord.fame = rankrecord.fame_next
        rankrecord.rank = rankrecord.rank_next
        rankrecord.utime = now
        model_mgr.set_save(rankrecord)
        
        return received_data
    
    @staticmethod
    def get_battleevent_score(mid, uid):
        """バトルイベントのスコアを取得.
        """
        return BackendApi.get_ranking_score(BattleEventRanking, mid, uid)
    
    @staticmethod
    def get_battleevent_rank(mid, uid, is_beginer=False):
        """バトルイベントのランキング順位を取得.
        """
        return BackendApi.get_ranking_rank(BattleEventRankingBeginer if is_beginer else BattleEventRanking, mid, uid)
    
    @staticmethod
    def get_battleevent_rankindex(mid, uid, is_beginer=False):
        """バトルイベントのランキング順位(index)を取得.
        """
        return BackendApi.get_ranking_rankindex(BattleEventRankingBeginer if is_beginer else BattleEventRanking, mid, uid)
    
    @staticmethod
    def get_battleevent_rankernum(mid, is_beginer=False):
        """バトルイベントのランキング人数を取得.
        """
        return BackendApi.get_ranking_rankernum(BattleEventRankingBeginer if is_beginer else BattleEventRanking, mid)
    
    @staticmethod
    def fetch_uid_by_battleeventrank(mid, limit, offset=0, withrank=False, is_beginer=False):
        """バトルイベントのランキングを範囲取得.
        """
        return BackendApi.fetch_uid_by_rankingrank(BattleEventRankingBeginer if is_beginer else BattleEventRanking, mid, limit, offset, withrank)
    
    @staticmethod
    def tr_create_battleevent_battlelog(model_mgr, uid, oid, result, point, v_power, o_power, attack, is_fever=False):
        """バトルイベントバトル履歴を作成.
        """
        ins = BattleEventBattleLog()
        ins.uid = uid
        ins.setData(oid, result, point, v_power, o_power, attack, is_fever=is_fever)
        model_mgr.set_save(ins)
        # 書き込み後のタスク.
        def writeEnd():
            BattleEventBattleLogListSet.create(uid, ins.id, ins.ctime).save()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def get_battleevent_battlelog_list(model_mgr, uid, limit=100, offset=0, using=settings.DB_DEFAULT):
        """バトルイベントバトルログを取得.
        """
        NUM_MAX = 100
        if BattleEventBattleLogListSet.exists(uid):
            logidlist = [model.logid for model in BattleEventBattleLogListSet.fetch(uid, offset, limit)]
            modellist =  BackendApi.get_model_list(model_mgr, BattleEventBattleLog, logidlist, using=using)
        else:
            modellist = BattleEventBattleLog.fetchValues(filters={'uid':uid}, order_by='-ctime', limit=NUM_MAX, using=using)
            if modellist:
                pipe = BattleEventBattleLogListSet.getDB().pipeline()
                for model in modellist:
                    BattleEventBattleLogListSet.create(uid, model.id, model.ctime).save(pipe)
                pipe.execute()
                modellist = modellist[offset:(offset+limit)]
        modellist.sort(key=lambda x:x.ctime, reverse=True)
        return modellist
    
    @staticmethod
    def make_battleevent_battleloginfo(handler, loglist, do_execute=True):
        """バトルイベントバトルログを取得.
        """
        model_mgr = handler.getModelMgr()
        
        oidlist = [log.data.get('oid') for log in loglist if log.data.get('oid')]
        playerdict = dict([(player.id, player) for player in BackendApi.get_players(handler, list(set(oidlist)), [], using=settings.DB_READONLY)])
        persons = BackendApi.get_dmmplayers(handler, playerdict.values(), using=settings.DB_READONLY, do_execute=False)
        leaders = BackendApi.get_leaders(playerdict.keys(), model_mgr, using=settings.DB_READONLY)
        
        def execute_end():
            loginfolist = []
            for log in loglist:
                oid = log.data.get('oid')
                person = None
                if oid:
                    player = playerdict.get(oid)
                    if player:
                        person = persons.get(player.dmmid)
                        leader = leaders.get(oid)
                        is_win = log.data.get('result') == Defines.BattleResultCode.WIN
                        is_attack = log.data.get('attack')
                        point = log.data.get('point')
                        loginfolist.append(Objects.battleevent_battlelog(handler, log.id, player, person, leader, is_win, is_attack, point, log.ctime))
            return loginfolist
        
        if do_execute:
            handler.execute_api()
            return execute_end()
        else:
            return execute_end
    
    @staticmethod
    def get_battleevent_battlelog_num(model_mgr, uid, using=settings.DB_DEFAULT):
        """バトルイベントバトルログ数を取得.
        """
        NUM_MAX = 100
        if not BattleEventBattleLogListSet.exists(uid):
            modellist = BattleEventBattleLog.fetchValues(filters={'uid':uid}, order_by='-ctime', limit=NUM_MAX, using=using)
            if modellist:
                pipe = BattleEventBattleLogListSet.getDB().pipeline()
                for model in modellist:
                    BattleEventBattleLogListSet.create(uid, model.id, model.ctime).save(pipe)
                pipe.execute()
        return BattleEventBattleLogListSet.get_num(uid) or 0
    
    @staticmethod
    def get_battleevent_revenge_list(model_mgr, uid, num=5, using=settings.DB_DEFAULT):
        """バトルイベントリベンジリストを取得.
        """
        NUM_MAX = 100
        if BattleEventRevengeSet.exists(uid):
            revengeidlist = BattleEventRevengeSet.fetchRandom(uid, num)
            modellist = BackendApi.get_model_list(model_mgr, BattleEventRevenge, revengeidlist, using=using)
            modellist = [model for model in modellist if model.uid == uid]
            if len(revengeidlist) == len(modellist):
                return modellist
            
        modellist = BattleEventRevenge.fetchValues(filters={'uid':uid}, order_by='-ctime', limit=NUM_MAX, using=using)
        if modellist:
            pipe = BattleEventRevengeSet.getDB().pipeline()
            for model in modellist:
                BattleEventRevengeSet.create(uid, model.id).save(pipe)
            pipe.execute()
        revengeidlist = BattleEventRevengeSet.fetchRandom(uid, num)
        modellist = BackendApi.get_model_list(model_mgr, BattleEventRevenge, revengeidlist, using=using)
        
        return modellist
    
    @staticmethod
    def get_battleevent_revenge(model_mgr, revengeid, using=settings.DB_READONLY):
        """バトルイベントリベンジレコードを取得.
        """
        return BackendApi.get_model(model_mgr, BattleEventRevenge, revengeid, using=using)
    
    @staticmethod
    def tr_update_battleevent_revenge(model_mgr, uid, oid, revengeid=None):
        """バトルイベントリベンジレコードを更新.
        """
        ins = None
        if revengeid:
            ins = BackendApi.get_model(model_mgr, BattleEventRevenge, revengeid)
            if ins:
                if ins.uid == uid and ins.oid == oid:
                    # 書き込む必要なし.
                    return
                elif ins.uid == oid and ins.oid == uid:
                    pass
                else:
                    ins = None
        if ins is None:
            ins = BattleEventRevenge()
        ins.uid = uid
        ins.oid = oid
        ins.ctime = OSAUtil.get_now()
        
        model_mgr.set_save(ins)
        
        # 書き込み後のタスク.
        def writeEnd():
            pipe = BattleEventRevengeSet.getDB().pipeline()
            BattleEventRevengeSet.create(oid, ins.id).delete(pipe)
            BattleEventRevengeSet.create(uid, ins.id).save(pipe)
            pipe.execute()
        model_mgr.add_write_end_method(writeEnd)
        
        return ins


    @staticmethod
    def tr_battleevent_battle(model_mgr, eventmaster, eventrankmaster, o_eventrankmaster, v_player, o_player, v_cardidlist, o_cardidlist, battledata, grouprank, is_worst, revengeid, confirmkey, now, rival_key=None, battle_ticket_num=None, is_pc=False):
        """バトルイベントバトル実行.
        """
        uid = v_player.id
        oid = o_player.id
        eventid = eventmaster.id

        # 重複確認.
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        
        data, animdata = battledata
        
        is_win = data['is_win']
        v_power = data['v_power']
        o_power = data['o_power']
        resultdata = {}
        resultdata.update(data)
        
        # プレイヤーのバトル情報.
        ins_id = BattleEventScore.makeID(uid, eventid)
        scorerecord = BackendApi.get_model(model_mgr, BattleEventScore, ins_id)
        inserted = False
        if scorerecord is None:
            scorerecord = BattleEventScore.makeInstance(ins_id)
            scorerecord.insert()
            inserted = True
        scorerecord = model_mgr.get_model_forupdate(BattleEventScore, ins_id)
        is_fever = not inserted and scorerecord.feveretime and now < scorerecord.feveretime
        
        # 前回の結果を消しておく.
        if scorerecord.result:
            battleresult = model_mgr.get_model(BattleResult, scorerecord.result)
            if battleresult:
                model_mgr.set_delete(battleresult)
        
        result_code = None
        prizes = None
        prize_textid = 0
        point = 0
        
        rand = AppRandom()
        
        if is_win:
            result_code = Defines.BattleResultCode.WIN
            
            # バトルポイント.
            point += eventrankmaster.battlepoint_w
            
            # 能力差によるバトルポイント.
            if eventmaster.bpcalctype == Defines.BattleEventPointCalculationType.LEVEL:
                # プレイヤーレベル差.
                point += max(0, o_player.level - v_player.level) * eventrankmaster.battlepoint_lv
            elif eventmaster.bpcalctype == Defines.BattleEventPointCalculationType.COST:
                # コスト差.
                point += max(0, data['o_cost'] - data['v_cost']) * eventrankmaster.battlepoint_lv
            elif eventmaster.bpcalctype == Defines.BattleEventPointCalculationType.OPPONENT_POWER:
                # 相手の接客力.
                point = max(point, int(data['o_power_default'] / 1000))
            
            # 仕返しレコード.
            BackendApi.tr_update_battleevent_revenge(model_mgr, oid, uid, revengeid)
            
            # 勝利報酬.
            prizes = eventrankmaster.select_winprize(rand)
            prize_textid = eventrankmaster.winprizes_text
        else:
            result_code = Defines.BattleResultCode.LOSE
            
            # バトルポイント.
            point += eventrankmaster.battlepoint_l
            
            # 相手にポイントを加算.
            if o_eventrankmaster:
                battlepointreceive = int(o_eventrankmaster.battlepointreceive * random.randint(o_eventrankmaster.pointrandmin, o_eventrankmaster.pointrandmax) / 100)
                if 0 < battlepointreceive:
                    # TODO: 合コンイベントは当日ログインしている必要がある.
                    BackendApi.tr_add_battleevent_battlepoint(model_mgr, eventmaster, oid, o_eventrankmaster, battlepointreceive, now=now)
                BackendApi.tr_create_battleevent_battlelog(model_mgr, oid, uid, Defines.BattleResultCode.WIN, battlepointreceive, o_power, v_power, False)
            
            # 敗北報酬.
            prizes = eventrankmaster.select_loseprize(rand)
            prize_textid = eventrankmaster.loseprizes_text
        
        # 報酬を付与.
        if prizes:
            # 報酬にバトルチケットを付与
            if battle_ticket_num:
                BackendApi.tr_add_additional_gachaticket(model_mgr, uid, Defines.GachaConsumeType.GachaTicketType.BATTLE_TICKET, battle_ticket_num)

            prizelist = BackendApi.get_prizelist(model_mgr, prizes)
            BackendApi.tr_add_prize(model_mgr, v_player.id, prizelist, prize_textid, auto_receive=True)
            resultdata['prizes'] = prizes
        
        # ピースの獲得.
        piecedata = BackendApi.tr_battleevent_pieceresult(model_mgr, uid, eventmaster, eventrankmaster, is_win, rival_key)
        
        exp = max(1, int(o_player.level - math.ceil(v_player.level / 2.0)))
        
        # カードへの経験値.
        levelupcard = {}
        cardlist = BackendApi.get_cards(v_cardidlist, model_mgr, forupdate=True)
        for cardset in cardlist:
            _, level_add = BackendApi.tr_add_cardexp(model_mgr, cardset, exp)
            if 0 < level_add:
                levelupcard[cardset.id] = level_add
        
        # グループ補正.
        point = point * eventrankmaster.battlepointrate / 100
        
        # 特効分のポイント.
        effect_percent = 0
        if is_win:
            effects = BackendApi.aggregate_effect_specialcard(model_mgr, v_player, eventmaster.specialcard, cardlist=cardlist, effect_getter=lambda x:x[1] if x else 0)
            effect_percent = sum(effects.values())
            if effects:
                # 称号効果.
                effect_percent = BackendApi.reflect_title_effect_percent(model_mgr, effect_percent, uid, 'battleevent_point_up', now, cnt=len(effects))
                point = point * (effect_percent + 100) / 100
        
        is_feverstart = False
        if eventrankmaster.feverpointrate and eventrankmaster.fevertimelimit:
            if is_fever:
                point = point * eventrankmaster.feverpointrate / 100
            else:
                rand = AppRandom()
                rate = eventrankmaster.getFeverRate(grouprank, is_worst)
                if rand.getIntN(100) < rate:
                    # フィーバー発生.
                    scorerecord.feveretime = now + datetime.timedelta(seconds=eventrankmaster.fevertimelimit)
                    is_feverstart = True
        
        # ポイントの乱数.
        point = int(point * random.randint(eventrankmaster.pointrandmin, eventrankmaster.pointrandmax) / 100)
        
        # 履歴.
        if is_win:
            BackendApi.tr_create_battleevent_battlelog(model_mgr, uid, oid, Defines.BattleResultCode.WIN, point, v_power, o_power, True, is_fever=is_fever)
            BackendApi.tr_create_battleevent_battlelog(model_mgr, oid, uid, Defines.BattleResultCode.LOSE, 0, o_power, v_power, False)
        else:
            BackendApi.tr_create_battleevent_battlelog(model_mgr, uid, oid, Defines.BattleResultCode.LOSE, point, v_power, o_power, True, is_fever=is_fever)
        
        resultdata['eventpoint'] = point
        resultdata['fever'] = is_fever
        resultdata['feverstart'] = is_feverstart
        resultdata['revenge'] = bool(revengeid)
        resultdata['effp'] = effect_percent
        if piecedata:
            resultdata['piecedata'] = piecedata
        
        # バトル結果.
        ins = BattleResult()
        ins.uid = v_player.id
        ins.oid = o_player.id
        ins.result = result_code
        ins.levelupcard = levelupcard
        ins.data = resultdata
        ins.anim = animdata
        ins.save()
        
        # バトルポイント.
        if 0 < point:
            BackendApi.tr_add_battleevent_battlepoint(model_mgr, eventmaster, uid, eventrankmaster, point, is_win=is_win, now=now, scorerecord=scorerecord)
            # クリスマス贈り物ポイント.
            BackendApi.tr_battleeventpresent_add_point(model_mgr, uid, eventmaster.id, point)
        
        # 結果保存.
        scorerecord.result = ins.id
        model_mgr.set_save(scorerecord)
        
        # 対戦時間を確認.
        def forUpdateBattleTime(model, inserted):
            bordertime = now - Defines.BATTLEEVENT_BATTLE_INTERVAL_SAME_OPPONENT
            if not inserted and not revengeid and bordertime <= model.btime:
                raise CabaretError(u'同じ相手とは連続でバトルできません', CabaretError.Code.OVER_LIMIT)
            if is_win:
                model.btime = now
        model_mgr.add_forupdate_task(BattleEventBattleTime, BattleEventBattleTime.makeID(uid, oid), forUpdateBattleTime)
        
        # 行動力.
        def forUpdatePlayerAp(model, inserted):
            v_player.setModel(model)
            if v_player.get_bp() < eventrankmaster.bpcost:
                raise CabaretError(u'行動力が足りません', CabaretError.Code.NOT_ENOUGH)
            v_player.add_bp(-eventrankmaster.bpcost)
        model_mgr.add_forupdate_task(PlayerAp, v_player.id, forUpdatePlayerAp)
        
        # ミッション達成書き込み.
        mission_executer = PanelMissionConditionExecuter()
        mission_executer.addTargetDoBattle()
        BackendApi.tr_complete_panelmission(model_mgr, v_player.id, mission_executer, now)
        
        # 書き込み後のタスク.
        def writeEnd():
            redisdb = RedisModel.getDB()
            pipe = redisdb.pipeline()
            
            deck = Deck()   # 自分のデッキ固定.
            deck.set_from_array(v_cardidlist)
            for cardset in cardlist:
                BackendApi.save_cardidset(cardset, deck, pipe)
            
            pipe.execute()
            
            kpi_operator = KpiOperator()
            
            # バトル参加記録.
            kpi_operator.set_save_battleevent_battle_join(uid, eventrankmaster.rank, now)
            # それぞれのバトル回数と勝利回数.
            kpi_operator.set_increment_battleevent_battlecount(uid, eventrankmaster.rank, 1, True, is_win, now)
            if o_eventrankmaster:
                kpi_operator.set_increment_battleevent_battlecount(oid, o_eventrankmaster.rank, 1, False, not is_win, now)
            # イベントプレイ数.
            kpi_operator.set_save_battleevent_play(uid, now, is_pc)
            
            kpi_operator.save()
            
            # 対戦相手をリセット.
            BattleEventOppList.create(uid).delete()
        
        model_mgr.add_write_end_method(writeEnd)
        
        return ins

    @staticmethod
    def get_level_deckcapa(uid, level):
        deck = BackendApi.get_deck(uid, using=settings.DB_READONLY).to_array()
        cost = sum([x.master.cost for x in BackendApi.get_cards(deck)])

        return int(round(level / 5)) + cost

    # @staticmethod
    # def get_deckcost_bk(uidlist):
    #     decks = BackendApi.get_decks(uidlist, using=settings.DB_READONLY)
    #     deckcost = {}
    #     for uid, deck in decks.items():
    #         cost = sum([x.master.cost for x in BackendApi.get_cards(deck.to_array())])
    #         deckcost[uid] = cost
    #     return deckcost

    @staticmethod
    def get_deckcost(uidlist):
        model_mgr = ModelRequestMgr()
        playerdecks = BackendApi.get_model_list(model_mgr, PlayerDeck, uidlist)
        deckcost = {}
        for deck in playerdecks:
            deckcost[deck.id] = deck.deckcost
        return deckcost

    @staticmethod
    def save_battleevent_rankuidset(eventid, rank, pipe=None, using=settings.DB_DEFAULT):
        """対戦相手検索用のsetを更新.
        """
        flag_execute = False
        if pipe is None:
            pipe = BattleEventRankUidSet.getDB().pipeline()
            flag_execute = True
        
        pipe.delete(BattleEventRankUidSet.makeKey(eventid, rank))
        
        offset = 0
        LIMIT = 500
        while True:
            rankuidlist = [model.uid for model in BattleEventRank.fetchValues(filters={'mid':eventid, 'rank_next':rank}, order_by='id', offset=offset, limit=LIMIT, using=using)]
            if not rankuidlist:
                break
            deckcost = BackendApi.get_deckcost(rankuidlist)
            for playerexp in PlayerExp.getByKey(rankuidlist, using=using):
                BattleEventRankUidSet.create(eventid, rank, playerexp.id, int(round(playerexp.level/5))+deckcost[playerexp.id]).save(pipe)
            offset += LIMIT
        
        if flag_execute:
            pipe.execute()
    
    @staticmethod
    def save_battleevent_rankuidset_for_goukon(eventid, rankmaster_list, redisdb=None, using=settings.DB_DEFAULT):
        """合コンイベント用の対戦相手検索用のsetを更新.
        """
        redisdb = redisdb or BattleEventRankUidSet.getDB()
        
        pipe = redisdb.pipeline()
        for rankmaster in rankmaster_list:
            pipe.delete(BattleEventRankUidSet.makeKey(eventid, rankmaster.rank))
        pipe.execute()
        
        uid = PlayerExp.max_value('id')
        LIMIT = 500
        idx = 0
        while 0 < uid:
            pipe = redisdb.pipeline()
            
            model_mgr = ModelRequestMgr()
            
            uidlist = range(max(0, uid - LIMIT) + 1, uid + 1)
            playerexplist = BackendApi.get_model_list(model_mgr, PlayerExp, uidlist, using=settings.DB_READONLY)
            tutorial_uid_list = [model.id for model in BackendApi.get_model_list(model_mgr, PlayerTutorial, uidlist, using=settings.DB_READONLY) if model.tutorialstate == Defines.TutorialStatus.COMPLETED]
            rank_dict = BackendApi.get_model_dict(model_mgr, BattleEventRank, [BattleEventRank.makeID(uid, eventid) for uid in tutorial_uid_list], using=settings.DB_READONLY, key=lambda x:x.uid)
            
            for playerexp in playerexplist:
                if not playerexp.id in tutorial_uid_list:
                    continue
                rankmodel = rank_dict.get(playerexp.id)
                if rankmodel:
                    # 参加済み.
                    rank = rankmodel.rank
                else:
                    # 未参加なので適当に割り振り.
                    rank = rankmaster_list[idx].rank
                BattleEventRankUidSet.create(eventid, rank, uid, playerexp.level).save(pipe)
                idx = (idx + 1) % len(rankmaster_list)
            pipe.execute()
            uid -= LIMIT
    
    @staticmethod
    def filter_battleevent_opplist_by_battletime(model_mgr, uid, oidlist, now=None, using=settings.DB_DEFAULT):
        """対戦相手を対戦時間チェックでフィルタリング.
        """
        now = now or OSAUtil.get_now()
        bordertime = now - Defines.BATTLEEVENT_BATTLE_INTERVAL_SAME_OPPONENT
        
        btimeidlist = [BattleEventBattleTime.makeID(uid, oid) for oid in oidlist]
        model_dict = BackendApi.get_model_dict(model_mgr, BattleEventBattleTime, btimeidlist, get_instance=True, using=using)
        dest = [oid for oid in oidlist if model_dict[BattleEventBattleTime.makeID(uid, oid)].btime < bordertime]
        return dest
    
    @staticmethod
    def check_battleevent_battletime(model_mgr, uid, oid, now=None, using=settings.DB_DEFAULT):
        """対戦相手との対戦時間チェック.
        """
        now = now or OSAUtil.get_now()
        bordertime = now - Defines.BATTLEEVENT_BATTLE_INTERVAL_SAME_OPPONENT
        model = BackendApi.get_model(model_mgr, BattleEventBattleTime, BattleEventBattleTime.makeID(uid, oid), get_instance=True, using=using)
        return model.btime < bordertime
    
    @staticmethod
    def update_battleevent_opponent(model_mgr, rankrecord, level, using=settings.DB_DEFAULT):
        """バトルイベントの対戦相手を更新.
        """
        uid = rankrecord.uid
        rank = rankrecord.rank
        eventid = rankrecord.mid
        
        if not BattleEventRankUidSet.exists(eventid, rank):
            eventmaster = BackendApi.get_battleevent_master(model_mgr, eventid, using=settings.DB_DEFAULT)
            if eventmaster.is_goukon:
                rankmaster_list = BackendApi.get_battleevent_rankmaster_by_eventid(model_mgr, eventid, using)
                BackendApi.save_battleevent_rankuidset_for_goukon(eventid, rankmaster_list, BattleEventRankUidSet.getDB(), using=using)
            else:
                pipe = BattleEventRankUidSet.getDB().pipeline()
                BackendApi.save_battleevent_rankuidset(eventid, rank, pipe, using=using)
                pipe.execute()
        
        now = OSAUtil.get_now()
        # 新方式.
        # 同ランクの中から選別.
        RETRY_MAX = 3
        def search():
            opplist = BattleEventRankUidSet.fetchRandom(eventid, rank, uid, Defines.BATTLEEVENT_OPPONENT_NUM, [uid])
            filtered_opplist = BackendApi.filter_battleevent_opplist_by_battletime(model_mgr, uid, opplist, now=now, using=using)
            return opplist, filtered_opplist
        
        for _ in xrange(RETRY_MAX):
            opplist, filtered_opplist = search()
            if filtered_opplist:
                break
        
        # 旧方式.
        # 同ランクの同レベル帯の中から選別.
#        def search(level_min, level_max):
#            opplist = BattleEventRankUidSet.fetchRandom(eventid, rank, level_min, level_max, Defines.BATTLEEVENT_OPPONENT_NUM*2, [uid])
#            filtered_opplist = BackendApi.filter_battleevent_opplist_by_battletime(model_mgr, uid, opplist, now=now, using=using)
#            return opplist, filtered_opplist
#        
#        level_min, level_max = BackendApi.get_battle_saferange(level)
#        opplist, filtered_opplist = search(level_min, level_max)
#        if not filtered_opplist:
#            # 見つからなかったので上下10ほど増やしてみる.
#            level_min = max(level_min - Defines.BATTLEEVENT_OPPONENT_SEACH_RANGE_SPREAD_SIZE, 1)
#            level_max += Defines.BATTLEEVENT_OPPONENT_SEACH_RANGE_SPREAD_SIZE
#            opplist, filtered_opplist = search(level_min, level_max)
#            if not filtered_opplist:
#                # 見つからなかった.
#                level_max = PlayerLevelExpMaster.max_value('level', level_max, using=using)
#                opplist, filtered_opplist = search(1, level_max)
        
        opplist.sort(key=lambda x:0 if x in filtered_opplist else 1)
        opplist = opplist[:Defines.BATTLEEVENT_OPPONENT_NUM]
        if opplist:
            BattleEventOppList.create(uid, opplist).save()
        
        return opplist
    
    @staticmethod
    def get_battleevent_opponentidlist(model_mgr, eventid, uid, using=settings.DB_DEFAULT):
        """対戦相手を取得.
        """
        model = BattleEventOppList.get(uid)
        if model:
            return model.opplist
        else:
            rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventid, uid, using=using)
            playerexp = BackendApi.get_model(model_mgr, PlayerExp, uid, using=using)
            return BackendApi.update_battleevent_opponent(model_mgr, rankrecord, playerexp.level, using=using)
    
    @staticmethod
    def get_battleevent_group_dict(model_mgr, groupidlist, using=settings.DB_DEFAULT):
        """バトルイベントグループを取得
        """
        return BackendApi.get_model_dict(model_mgr, BattleEventGroup, groupidlist, using=using)
    
    @staticmethod
    def get_battleevent_group(model_mgr, groupid, using=settings.DB_DEFAULT):
        """バトルイベントグループを取得
        """
        return BackendApi.get_battleevent_group_dict(model_mgr, [groupid], using=using).get(groupid)
    
    @staticmethod
    def get_battleevent_grouplog_dict(model_mgr, groupidlist, using=settings.DB_DEFAULT):
        """バトルイベントグループ履歴を取得
        """
        return BackendApi.get_model_dict(model_mgr, BattleEventGroupLog, groupidlist, using=using)
    
    @staticmethod
    def get_battleevent_grouplog(model_mgr, groupid, using=settings.DB_DEFAULT):
        """バトルイベントグループ履歴を取得
        """
        return BackendApi.get_battleevent_grouplog_dict(model_mgr, [groupid], using=using).get(groupid)
    
    @staticmethod
    def get_battleevent_grouprank(model_mgr, groupdata, uid, using=settings.DB_DEFAULT, now=None):
        """バトルイベントグループ内順位を取得.
        """
        def findRank(arr, func):
            arr.sort(key=func, reverse=True)
            point = None
            tmp_rank = None
            for idx,data in enumerate(arr):
                v = func(data)
                if point is None or v < point:
                    point = v
                    tmp_rank = idx + 1
                if data.uid == uid:
                    return tmp_rank
            return None
        if isinstance(groupdata, BattleEventGroup):
            eventid = int(groupdata.rankid >> 32)
            scorerecordlist = BackendApi.get_battleevent_scorerecord_dict(model_mgr, eventid, groupdata.useridlist, get_instance=True, using=using).values()
            return findRank(scorerecordlist, lambda x:x.getPointToday(now))
        elif isinstance(groupdata, BattleEventGroupLog):
            return findRank(groupdata.userdata, lambda x:x.point)
        else:
            return None
    
    @staticmethod
    def make_battleevent_grouprankingdata(handler, groupdata, viewer_uid, now=None, do_execute=True, player_num_limit=None, using=settings.DB_DEFAULT, do_get_name=True):
        """バトルイベントグループ内ランキングを取得.
        """
        model_mgr = handler.getModelMgr()
        
        def makeScoreRankSet(arr, func):
            arr.sort(key=func, reverse=True)
            dest = []
            point = None
            tmp_rank = None
            for idx,data in enumerate(arr):
                v = func(data)
                if point is None or v < point:
                    point = v
                    tmp_rank = idx + 1
                dest.append((data.uid, (tmp_rank, point)))
            return dest, tmp_rank
        
        if isinstance(groupdata, BattleEventGroup):
            eventid = int(groupdata.rankid >> 32)
            scorerecordlist = BackendApi.get_battleevent_scorerecord_dict(model_mgr, eventid, groupdata.useridlist, get_instance=True, using=using).values()
            scorerankset, worst_rank = makeScoreRankSet(scorerecordlist, lambda x:x.getPointToday(now))
        elif isinstance(groupdata, BattleEventGroupLog):
            scorerankset, worst_rank = makeScoreRankSet(groupdata.userdata, lambda x:x.point)
        else:
            return None
        
        scorerank_dict = dict(scorerankset)
        viewer_data = scorerank_dict.get(viewer_uid)
        viewer_grouprank, viewer_grouppoint = viewer_data if viewer_data else (None, 0)
        
        if player_num_limit is not None:
            scorerankset = scorerankset[:player_num_limit]
            scorerank_dict = dict(scorerankset)
        
        uidlist = scorerank_dict.keys()
        if uidlist:
            playerlist = BackendApi.get_players(handler, uidlist, [PlayerExp], using=using)
            if do_get_name:
                persons = BackendApi.get_dmmplayers(handler, playerlist, using=using, do_execute=do_execute)
            else:
                persons = {}
            leaders = BackendApi.get_leaders(uidlist, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
        else:
            playerlist = []
            persons = {}
            leaders = {}
        
        def execute_end():
            obj_playerlist = []
            for player in playerlist:
                uid = player.id
                rank, score = scorerank_dict[uid]
                
                obj_player = Objects.player(handler, player, persons.get(player.dmmid), leaders.get(uid))
                obj_player['event_score'] = score
                obj_player['event_rank'] = rank
                obj_playerlist.append(obj_player)
            obj_playerlist.sort(key=lambda x:x['event_rank'])
            return {
                'rank' : viewer_grouprank,
                'playerlist' : obj_playerlist,
                'vscore' : viewer_grouppoint,
                'worst' : worst_rank and worst_rank == viewer_grouprank,
            }
        if do_execute:
            handler.execute_api()
            return execute_end()
        else:
            return execute_end
    
    @staticmethod
    def make_battleevent_rank_selectobj(handler, eventrankmaster):
        """ランク選択用のランク情報を作成.
        """
        model_mgr = handler.getModelMgr()
        
        prizeinfo = None
        if eventrankmaster.group_rankingprizes:
            arr = eventrankmaster.group_rankingprizes[:]
            arr.sort(key=lambda x:int(x['rank_min']==1), reverse=True)
            data = arr[0]
            if data['rank_min'] == 1:
                prizelist = BackendApi.get_prizelist(model_mgr, data['prize'], using=settings.DB_READONLY)
                prizeinfo = BackendApi.make_prizeinfo(handler, prizelist, using=settings.DB_READONLY)
        return Objects.battleevent_rank_selectobj(handler, eventrankmaster, no1_prizeinfo=prizeinfo)
    
    @staticmethod
    def tr_battleevent_regist_group(model_mgr, eventrankmaster, rankrecord, is_beginner, group, playerlevel, now=None):
        """バトルイベントに参加.
        """
        now = now or OSAUtil.get_now()
        if group is None:
            logintime = DateTimeUtil.toLoginTime(now)
            group = BattleEventGroup()
            group.eventid = eventrankmaster.eventid
            group.rankid = eventrankmaster.id
            group.cdate = datetime.date(logintime.year, logintime.month, logintime.day)
            group.insert()
            group = model_mgr.get_model_forupdate(BattleEventGroup, group.id)
        
        group.useridlist.append(rankrecord.uid)
        
        if eventrankmaster.level_lower:
            group.level_min = max(group.level_min, playerlevel - eventrankmaster.level_lower, 1)
        if eventrankmaster.level_upper:
            if group.level_max == 0:
                group.level_max = playerlevel + eventrankmaster.level_upper
            else:
                group.level_max = min(group.level_max, playerlevel + eventrankmaster.level_upper)
        
        membernummax = eventrankmaster.membernummax if is_beginner else eventrankmaster.membernummax_auto
        if membernummax <= len(group.useridlist):
            group.fixed = True
        model_mgr.set_save(group)
        
        rankrecord.addGroupId(group.id)
        model_mgr.set_save(rankrecord)
        
        def writeEnd():
            KpiOperator().set_increment_battleevent_member_count(eventrankmaster.rank, 1, now).save()
        model_mgr.add_write_end_method(writeEnd)
        
        return group
    
    @staticmethod
    def tr_battleevent_regist_from_teaser(model_mgr, eventmaster, uid, rank):
        """ティザーページからイベント登録.
        """
        eventid = eventmaster.id
        rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventid, uid)
        if rankrecord is not None:
            # 登録済み.
            raise CabaretError(u'登録済みです', CabaretError.Code.ALREADY_RECEIVED)
        
        rankrecord = BattleEventRank.makeInstance(BattleEventRank.makeID(uid, eventid))
        rankrecord.rank_next = rank
        rankrecord.rank = rankrecord.rank_next
        model_mgr.set_save(rankrecord)
    
    @staticmethod
    def tr_battleevent_regist_group_for_user(model_mgr, config, eventmaster, uid, level, rankmaster_list, **kwargs):
        """ユーザーが実行してグループに参加.
        途中参加で使う想定.
        """
        if eventmaster.is_goukon:
            target_rank = kwargs['target_rank']
        elif config.isFirstDay():
            target_rank = eventmaster.rankstart
        else:
            target_rank = eventmaster.rankbeginer
        
        eventid = eventmaster.id
        rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventid, uid)
        if rankrecord is None:
            rankrecord = BattleEventRank.makeInstance(BattleEventRank.makeID(uid, eventid))
            rankrecord.rank_next = target_rank
            rankrecord.rank = rankrecord.rank_next
            rankrecord.insert()
        rankrecord = model_mgr.get_model_forupdate(BattleEventRank, rankrecord.id)
        if eventmaster.is_goukon:
            # 合コンイベントはランクを更新する.
            rankrecord.rank_next = target_rank
            rankrecord.rank = rankrecord.rank_next
        model_mgr.set_save(rankrecord)
        
        groupid = rankrecord.getCurrentGroupId()
        rank = rankrecord.rank_next
        if groupid:
            group = BattleEventGroup.getByKey(groupid)
            if group:
                # 参加済み.
                model_mgr.delete_models_from_cache(BattleEventRank, [BattleEventRank.makeID(uid, eventid)])
                raise CabaretError(u'参加済みです', CabaretError.Code.ALREADY_RECEIVED)
            if not eventmaster.is_goukon:
                grouplog = BackendApi.get_battleevent_grouplog(model_mgr, groupid)
                rank = int(grouplog.rankid & 0xffffffff)
                rankrecord.rank_next = rank
                rankrecord.rank = rankrecord.rank_next
        
        eventrankmaster = BackendApi.get_battleevent_rankmaster(model_mgr, eventid, rank)
        
        rankid = eventrankmaster.id
        filters={
            'rankid':rankid,
            'fixed':False,
        }
        if eventrankmaster.level_upper:
            filters.update(level_max__lte=level)
        if eventrankmaster.level_lower:
            filters.update(level_min__gte=level)
        grouplist = BattleEventGroup.fetchValues(filters=filters, limit=5, using=settings.DB_DEFAULT)
        
        group = None
        if grouplist:
            group = random.choice(grouplist)
            group = BattleEventGroup.getByKeyForUpdate(group.id)
            if group.fixed:
                group = None
        
        group = BackendApi.tr_battleevent_regist_group(model_mgr, eventrankmaster, rankrecord, True, group, level)
        
        if not kwargs.get('skip_matching'):
            def writeEnd():
                pipe = BattleEventRankUidSet.getDB().pipeline()
                for rankmaster in rankmaster_list:
                    if rankmaster.rank == eventrankmaster.rank:
                        continue
                    BattleEventRankUidSet.create(eventid, rankmaster.rank, uid, level).delete(pipe)
                BattleEventRankUidSet.create(eventid, eventrankmaster.rank, uid, level).save(pipe)
                pipe.execute()
            
            model_mgr.add_write_end_method(writeEnd)
        
        return group
    
    @staticmethod
    def tr_battleevent_close_group(model_mgr, eventmaster, eventrankmaster, group, now, do_send_famebonus=False, rank_max=None):
        """グループを閉じる.
        """
        is_battle_open = BackendApi.is_battleevent_battle_open(model_mgr, do_check_emergency=False)
        
        useridlist = group.useridlist
        
        scorerecorddict = BackendApi.get_battleevent_scorerecord_dict(model_mgr, eventrankmaster.eventid, useridlist, get_instance=True)
        scorerecordlist = scorerecorddict.values()
        scorerecordlist.sort(key=lambda x:x.getPointToday(now), reverse=True)
        
        def forUpdateBattleEventGroupRankingPrize(model, insert, prizeidlist, textid):
            if model.fixed:
                model.clear_prizes()
            model.add_prize(prizeidlist, textid)
            model.fixed = False
        
        userdatalist = []
        userdata_rankmap = {}
        
        rank = 0
        pointpre = None
        rankrecordmap = {}
        
        for idx,scorerecord in enumerate(scorerecordlist):
            point = scorerecord.getPointToday(now)
            if pointpre is None or point < pointpre:
                rank = idx + 1
            
            userdata = BattleEventGroupUserData()
            userdata.uid = scorerecord.uid
            userdata.point = point
            userdata.win = scorerecord.getWinMaxToday(now)
            userdata.fame = eventrankmaster.getPoint(rank, point)
            userdata.rankup = eventrankmaster.getRankUpValue(rank, point, rank_max)
            userdata.grouprank = rank
            userdatalist.append(userdata)
            
            flag_send_famebonus = do_send_famebonus
            
            rankrecord = BattleEventRank.getByKeyForUpdate(BattleEventRank.makeID(userdata.uid, eventrankmaster.eventid))
            if rankrecord:
                # 名声ポイント加算.
                rankrecord.fame_next += userdata.fame
                
                # ランク増減書き込み.
                rankrecord.rank_next += userdata.rankup
                print '%s:grouprank=%s, fame=%s, rankup=%s' % (rankrecord.uid, rank, userdata.fame, userdata.rankup)
                
                if not flag_send_famebonus and is_battle_open and DateTimeUtil.toLoginTime(OSAUtil.get_now()) < rankrecord.utime:
                    # ログインボーナスを受け取ってしまっている.
                    flag_send_famebonus = True
                    rankrecord.utime = now
                
                if flag_send_famebonus:
                    if 0 < userdata.fame:
                        prizelist = BackendApi.__tr_battleevent_receive_famebonus(model_mgr, eventmaster, rankrecord)
                        rankrecord.fame = rankrecord.fame_next
                        if prizelist:
                            print "send famebonus:uid=%s,num=%s" % (rankrecord.uid, len(prizelist))
                    rankrecord.rank = rankrecord.rank_next
                
                model_mgr.set_save(rankrecord)
                
                rankrecordmap[rankrecord.uid] = rankrecord
                
            if 0 < point:
                arr = userdata_rankmap[rank] = userdata_rankmap.get(rank) or []
                arr.append((flag_send_famebonus, userdata))
            
            pointpre = point
        
        # グループ内ランキング報酬.
        group_rankingprize_text = eventrankmaster.group_rankingprize_text
        prizemap = {}
        for idx, data in enumerate(eventrankmaster.group_rankingprizes):
            prizeidlist = data['prize']
            rank_min = data['rank_min']
            rank_max = data['rank_max']
            
            # 対象のユーザー.
            uidlist = []
            for rank in xrange(rank_min, rank_max+1):
                arr = userdata_rankmap.get(rank) or []
                for flag_send_famebonus, userdata in arr:
                    if flag_send_famebonus:
                        uidlist.append(userdata.uid)
                    else:
                        prizemap[userdata.uid] = prizemap.get(userdata.uid) or []
                        prizemap[userdata.uid].extend(prizeidlist)
            
            if uidlist:
                prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
                for uid in uidlist:
                    BackendApi.tr_add_prize(model_mgr, uid, prizelist, group_rankingprize_text)
        
        # 受け取りフラグだけ立てておく.
        for uid,prizeidlist in prizemap.items():
            model_mgr.add_forupdate_task(BattleEventGroupRankingPrize, BattleEventGroupRankingPrize.makeID(uid, eventmaster.id), forUpdateBattleEventGroupRankingPrize, prizeidlist, group_rankingprize_text)
        
        # 履歴作成.
        grouplog = BattleEventGroupLog.makeInstance(group.id)
        grouplog.eventid = group.eventid
        grouplog.rankid = group.rankid
        grouplog.cdate = group.cdate
        grouplog.userdata = userdatalist
        model_mgr.set_save(grouplog)
        
        # グループ削除.
        model_mgr.set_delete(group)
        
        def writeEnd():
            logintime = DateTimeUtil.toLoginTime(now)
            
            kpi_operator = KpiOperator()
            
            redisdb = BattleEventDailyRanking.getDB()
            pipe = redisdb.pipeline()
            
            rankingid = BattleEventDailyRanking.makeRankingId(logintime, eventmaster.id, eventrankmaster.rank)
            
            for userdata in userdatalist:
                rankrecord = rankrecordmap.get(userdata.uid)
                if rankrecord:
                    kpi_operator.set_save_battleevent_famepoint(rankrecord.mid, rankrecord.uid, rankrecord.fame_next)
                kpi_operator.set_save_battleevent_result(userdata.uid, eventrankmaster.rank, userdata.grouprank, userdata.point, now)
                
                BattleEventDailyRanking.create(rankingid, userdata.uid, userdata.point).save(pipe)
            
            pipe.execute()
            
            kpi_operator.save()
        model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def battleevent_send_groupranking_prizes(eventmaster):
        """グループランキングの報酬を全て配布してしまう.
        """
        LIMIT = 500
        
        filters = {
            'mid' : eventmaster.id,
            'fixed' : False,
        }
        
        cnt = 0
        while True:
            idlist = [model.id for model in BattleEventGroupRankingPrize.fetchValues(['id'], filters=filters, limit=LIMIT)]
            if not idlist:
                break
            
            def tr():
                model_mgr = ModelRequestMgr()
                prizerecordlist = BattleEventGroupRankingPrize.fetchByKeyForUpdate(idlist)
                for prizerecord in prizerecordlist:
                    if not prizerecord.fixed and prizerecord.prizes:
                        for prizerecord_data in prizerecord.prizes:
                            prizeidlist = prizerecord_data['prizes']
                            textid = prizerecord_data['text']
                            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
                            BackendApi.tr_add_prize(model_mgr, prizerecord.uid, prizelist, textid)
                        prizerecord.fixed = True
                        model_mgr.set_save(prizerecord)
                model_mgr.write_all()
                return model_mgr
            db_util.run_in_transaction(tr).write_end()
            cnt += len(idlist)
        
        return cnt
    
    @staticmethod
    def save_kpi_battleevent_join(uid, is_pc, now=None, kpi_operator=None):
        """バトルイベント参加のKPIを保存.
        """
        local_kpi_operator = kpi_operator or KpiOperator()
        local_kpi_operator.set_save_battleevent_join(uid, now, is_pc)
        if kpi_operator is None:
            local_kpi_operator.save()
        return local_kpi_operator
    
    @staticmethod
    def check_battleevent_beginer(model_mgr, uid, eventmaster, config=None, now=None, using=settings.DB_DEFAULT):
        """バトルイベント初心者確認.
        """
        if config is None:
            config = BackendApi.get_current_battleeventconfig(model_mgr, using)
        if not config or config.mid != eventmaster.id:
            return False
        return BackendApi.check_event_beginer(model_mgr, uid, eventmaster.beginer_days, config.starttime, now=now, using=using)
    
    @staticmethod
    def get_battleeventpresent_master(model_mgr, eventid, number, using=settings.DB_DEFAULT):
        """バトルイベントのポイントプレゼントのマスターを取得.
        """
        mid = BattleEventPresentMaster.makeID(eventid, number)
        return BackendApi.get_model(model_mgr, BattleEventPresentMaster, mid, using=using)
    
    @staticmethod
    def get_battleeventpresent_master_by_eventdid(model_mgr, eventid, using=settings.DB_DEFAULT):
        """バトルイベントのポイントプレゼントのマスターをイベントIDから取得.
        numberがキーの辞書を返します.
        """
        client = localcache.Client()
        key = 'get_battleeventpresent_master_by_eventdid:%s' % eventid
        midlist = client.get(key)
        if midlist is None:
            modellist = BattleEventPresentMaster.fetchValues(filters={'eventid':eventid}, using=using)
            dest = dict([(model.id, model) for model in modellist])
            client.set(key, dest.keys())
            return dest
        else:
            return BackendApi.get_model_dict(model_mgr, BattleEventPresentMaster, midlist, using=using, key=lambda x:x.number)
    
    @staticmethod
    def get_battleeventpresent_content_master_list(model_mgr, midlist, using=settings.DB_DEFAULT):
        """バトルイベントのポイントプレゼントの中身のマスターを取得.
        """
        return BackendApi.get_model_list(model_mgr, BattleEventPresentContentMaster, midlist, using=using)
    
    @staticmethod
    def get_battleeventpresent_content_master(model_mgr, mid, using=settings.DB_DEFAULT):
        """バトルイベントのポイントプレゼントの中身のマスターを取得.
        """
        return BackendApi.get_model(model_mgr, BattleEventPresentContentMaster, mid, using=using)
    
    @staticmethod
    def get_battleeventpresent_pointdata(model_mgr, uid, eventid, using=settings.DB_DEFAULT):
        """バトルイベントのポイントプレゼントの獲得ポイント情報を取得.
        """
        if not BackendApi.get_battleeventpresent_master_by_eventdid(model_mgr, eventid, using=using):
            # プレゼントは無い.
            return None
        
        pointdata = BackendApi.get_model(model_mgr, BattleEventPresentData, BattleEventPresentData.makeID(uid, eventid), using=using)
        if pointdata is None or pointdata.getData() is None:
            eventmaster = BackendApi.get_battleevent_master(model_mgr, eventid, using=using)
            presentmaster_list = None
            if eventmaster.presentnumber_default:
                pm = BackendApi.get_battleeventpresent_master(model_mgr, eventid, eventmaster.presentnumber_default, using=using)
                if pm and pm.rate:
                    presentmaster_list = [pm]
            
            # プレゼントが未設定なので設定する.
            presentmaster = BackendApi.choice_battleeventpresent(model_mgr, uid, eventid, using=using, presentmaster_list=presentmaster_list)
            if presentmaster is None:
                return None
            
            def tr(uid, eventid, presentmaster):
                model_mgr = ModelRequestMgr()
                
                # プレゼントを設定.
                BackendApi.tr_battleeventpresent_set_present(model_mgr, uid, presentmaster)
                
                model_mgr.write_all()
                return model_mgr
            wrote_model_mgr = db_util.run_in_transaction(tr, uid, eventid, presentmaster)
            wrote_model_mgr.write_end()
            
            modelid = BattleEventPresentData.makeID(uid, eventid)
            pointdata = wrote_model_mgr.get_wrote_model(BattleEventPresentData, modelid, BattleEventPresentData.getByKey, modelid)
        
        return pointdata
    
    @staticmethod
    def choice_battleeventpresent(model_mgr, uid, eventid, using=settings.DB_DEFAULT, presentmaster_list=None):
        """バトルイベントのポイントプレゼントを選ぶ.
        """
        if presentmaster_list is None:
            presentmaster_list = BackendApi.get_battleeventpresent_master_by_eventdid(model_mgr, eventid).values()
        if not presentmaster_list:
            return None
        
        rate_total = 0
        countidlist = []
        for presentmaster in presentmaster_list:
            if presentmaster.rate < 1:
                continue
            rate_total += presentmaster.rate
            countidlist.append(BattleEventPresentCounts.makeID(uid, presentmaster.number))
        
        # 回数情報を取得.
        countdata_dict = BackendApi.get_model_dict(model_mgr, BattleEventPresentCounts, countidlist, get_instance=True, using=using, key=lambda x:x.mid)
        
        rand = AppRandom()
        rand_value = rand.getIntN(rate_total)
        
        # 抽選.
        tmp_presentmaster = None
        for presentmaster in presentmaster_list:
            if 0 <= rand_value and 0 < presentmaster.rate:
                rand_value -= presentmaster.rate
                if rand_value < 1:
                    tmp_presentmaster = presentmaster
            
            # 特別な条件で出現.
            conditions = presentmaster.getConditionDict()
            if not conditions:
                continue
            for k,v in conditions.items():
                countdata = countdata_dict.get(k)
                cnt = countdata.cnt if countdata else 0
                if cnt < v:
                    continue
                return presentmaster
        return tmp_presentmaster
    
    @staticmethod
    def tr_battleeventpresent_set_present(model_mgr, uid, presentmaster, contentmaster=None):
        """バトルイベントのポイントプレゼントを設定.
        """
        contentid = None
        
        if contentmaster is None:
            # 中身を抽選.
            contents = dict(presentmaster.contents)
            rate_total = sum(contents.values())
            if 0 < rate_total:
                v = AppRandom().getIntN(rate_total)
                for cid,rate in contents.items():
                    v -= rate
                    if v < 1:
                        contentid = cid
                        break
            if contentid is None:
                raise CabaretError(u'中身を決めようとしたけど見つかりませんでした', code=CabaretError.Code.INVALID_MASTERDATA)
        else:
            contentid = contentmaster.id
        
        # 設定.
        modelid = BattleEventPresentData.makeID(uid, presentmaster.eventid)
        userdata = BackendApi.get_model(model_mgr, BattleEventPresentData, modelid)
        if userdata is None:
            userdata = BattleEventPresentData.makeInstance(modelid)
            model_mgr.set_got_models([userdata])
        userdata.point = 0
        userdata.prenum = userdata.currentnum
        userdata.precontent = userdata.currentcontent
        userdata.currentnum = presentmaster.number
        userdata.currentcontent = contentid
        model_mgr.set_save(userdata)
        
        # 回数を加算.
        def forUpdateCount(model, inserted):
            model.cnt = min(model.cnt + 1, 0xff)
        model_mgr.add_forupdate_task(BattleEventPresentCounts, BattleEventPresentCounts.makeID(uid, presentmaster.number), forUpdateCount)
        
        # 特別な条件の回数をリセット.
        conditions = presentmaster.getConditionDict()
        def forUpdateCondition(model, inserted):
            model.cnt = 0
        for number in conditions.keys():
            model_mgr.add_forupdate_task(BattleEventPresentCounts, BattleEventPresentCounts.makeID(uid, number), forUpdateCondition)
    
    @staticmethod
    def tr_battleeventpresent_add_point(model_mgr, uid, eventid, point):
        """バトルイベントのポイントプレゼントのポイントを加算.
        """
        def forUpdate(model, inserted, point):
            model.point = min(model.point + point, 0xffffffff)
        model_mgr.add_forupdate_task(BattleEventPresentData, BattleEventPresentData.makeID(uid, eventid), forUpdate, point)
    
    @staticmethod
    def tr_battleeventpresent_receive_present(model_mgr, uid, eventid, confirmkey, presentmaster_next):
        """バトルイベントのポイントプレゼントを受け取る.
        """
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        
        # ポイント情報を取得.
        modelid = BattleEventPresentData.makeID(uid, eventid)
        userdata = BackendApi.get_model(model_mgr, BattleEventPresentData, modelid)
        if userdata is None:
            raise CabaretError(u'不正な遷移です', CabaretError.Code.ILLEGAL_ARGS)
        
        # マスターデータを取得.
        data = userdata.getData()
        if data is None:
            # 未設定.
            raise CabaretError(u'未設定です', CabaretError.Code.ILLEGAL_ARGS)
        presentmaster = BackendApi.get_battleeventpresent_master(model_mgr, eventid, data['number'])
        if presentmaster is None:
            raise CabaretError(u'マスターデータが存在しません', CabaretError.Code.INVALID_MASTERDATA)
        
        # 目標値を確認.
        if userdata.point < presentmaster.point:
            raise CabaretError(u'獲得バトルポイントが足りません', CabaretError.Code.NOT_ENOUGH)
        
        # 報酬付与.
        contentmaster = BackendApi.get_battleeventpresent_content_master(model_mgr, data['content'])
        if contentmaster is None:
            raise CabaretError(u'報酬の中身のマスターデータが存在しません', CabaretError.Code.INVALID_MASTERDATA)
        prizelist = BackendApi.get_prizelist(model_mgr, contentmaster.prizes)
        BackendApi.tr_add_prize(model_mgr, uid, prizelist, contentmaster.prize_text)
        
        # 次を設定.
        BackendApi.tr_battleeventpresent_set_present(model_mgr, uid, presentmaster_next)
        
        # ログ.
        model_mgr.set_save(UserLogBattleEventPresent.create(uid, eventid, data['number'], data['content']))
    
    #================================================================================
    # シリアルコード.
    @staticmethod
    def get_serialcampaign_master(model_mgr, mid, using=settings.DB_DEFAULT):
        """シリアルコードキャンペーンのマスターデータ.
        """
        return BackendApi.get_model(model_mgr, SerialCampaignMaster, mid, using=using)
    
    @staticmethod
    def get_serialcode_by_id(model_mgr, serialid, using=settings.DB_DEFAULT):
        """シリアルコードデータをIDから取得.
        """
        return BackendApi.get_model(model_mgr, SerialCode, serialid, using=using)
    
    @staticmethod
    def get_serialcode_by_serial(model_mgr, serialcode, using=settings.DB_DEFAULT):
        """シリアルコードデータをシリアルコードから取得.
        """
        # 全て大文字に変換.
        serialcode = serialcode.upper()
        
        client = OSAUtil.get_cache_client()
        key = 'get_serialcode_by_serial:%s' % serialcode
        serialid = client.get(key)
        
        model = None
        if serialid is None:
            modellist = SerialCode.fetchValues(filters={'serial' : serialcode}, limit=1, using=using)
            if modellist:
                model = modellist[0]
                serialid = model.id
                client.set(key, serialid)
        else:
            model = BackendApi.get_serialcode_by_id(model_mgr, int(serialid), using)
        
        return model
    
    @staticmethod
    def get_serialcode_count_model(model_mgr, uid, mid, using=settings.DB_DEFAULT):
        """シリアルコード入力回数情報.
        """
        modelid = SerialCount.makeID(uid, mid)
        return BackendApi.get_model(model_mgr, SerialCount, modelid, using=using)
    
    @staticmethod
    def tr_input_serialcode(model_mgr, uid, serialcampaignmaster, serialcodeid, is_pc):
        """シリアルコード入力書き込み.
        serialcampaignmasterの期間の確認等は外で.
        serialcodeidはトランザクション外で存在確認する.
        """
        now = OSAUtil.get_now()
        mid = serialcampaignmaster.id
        
        # シリアルコード情報を取得.
        if serialcampaignmaster.share_serial:
            # 共通の場合は上書きしない.
            serialcode_model = BackendApi.get_serialcode_by_id(model_mgr, serialcodeid)
        else:
            serialcode_model = SerialCode.getByKeyForUpdate(serialcodeid)
        if mid != serialcode_model.mid:
            # ここに来るのはサーバのバグ.
            raise CabaretError(u'シリアルキャンペーンのIDが一致しません.', CabaretError.Code.ILLEGAL_ARGS)
        
        # 使用済み確認.
        if serialcode_model.uid != 0:
            # 入力済み.
            if uid == serialcode_model.uid:
                # 自分で以前入力した.
                raise CabaretError(u'Already.', CabaretError.Code.ALREADY_RECEIVED)
            else:
                # 他の誰かが入力した.
                raise CabaretError(u'Others.', CabaretError.Code.ALREADY_RECEIVED)
        
        # 入力回数を確認.
        if 0 < serialcampaignmaster.limit_pp:
            def forUpdateCounter(model, inserted, limit_pp):
                if limit_pp <= model.cnt:
                    raise CabaretError(u'これ以上入力できません', CabaretError.Code.OVER_LIMIT)
                # 入力回数加算.
                model.cnt += 1
            model_mgr.add_forupdate_task(SerialCount, SerialCount.makeID(uid, mid), forUpdateCounter, serialcampaignmaster.limit_pp)
        
        # 入力者情報書き込み.
        logmodel = ShareSerialLog.createBySerialCode(serialcode_model) if serialcampaignmaster.share_serial else serialcode_model
        logmodel.uid = uid
        logmodel.itime = now
        logmodel.is_pc = is_pc
        model_mgr.set_save(logmodel)
        
        # 報酬付与.
        if serialcampaignmaster.prizes:
            prizelist = BackendApi.get_prizelist(model_mgr, serialcampaignmaster.prizes)
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, serialcampaignmaster.prize_text)
    
    #===============================================================
    # イベント動画.
    @staticmethod
    def get_eventmovie_master_dict(model_mgr, midlist, using=settings.DB_DEFAULT):
        """イベント動画のマスターを取得.
        """
        return BackendApi.get_model_dict(model_mgr, EventMovieMaster, midlist, using=using)
    
    @staticmethod
    def get_eventmovie_master_list(model_mgr, midlist, using=settings.DB_DEFAULT):
        """イベント動画のマスターを取得.
        """
        return BackendApi.get_model_list(model_mgr, EventMovieMaster, midlist, using=using)
    
    @staticmethod
    def get_eventmovie_master(model_mgr, mid, using=settings.DB_DEFAULT):
        """イベント動画のマスターを取得.
        """
        return BackendApi.get_model(model_mgr, EventMovieMaster, mid, using=using)
    
    @staticmethod
    def get_eventmovie_viewdata_dict(model_mgr, uid, midlist, using=settings.DB_DEFAULT):
        """イベント動画の閲覧情報を取得.
        """
        model_idlist = [EventMovieViewData.makeID(uid, mid) for mid in midlist]
        return BackendApi.get_model_dict(model_mgr, EventMovieViewData, model_idlist, using=using, key=lambda x:x.mid)
    
    @staticmethod
    def get_eventmovie_viewdata(model_mgr, uid, mid, using=settings.DB_DEFAULT):
        """イベント動画の閲覧情報を取得.
        """
        model_id = EventMovieViewData.makeID(uid, mid)
        return BackendApi.get_model_list(model_mgr, EventMovieViewData, model_id, using=using)
    
    @staticmethod
    def add_eventmovie_viewcount(uid, mid, is_pc):
        """イベント動画の閲覧回数を加算.
        """
        model_id = EventMovieViewData.makeID(uid, mid)
        def tr(model_id):
            model_mgr = ModelRequestMgr()
            def forUpdate(model, inserted):
                if is_pc:
                    model.cnt_pc += 1
                else:
                    model.cnt_sp += 1
            model_mgr.add_forupdate_task(EventMovieViewData, model_id, forUpdate)
            model_mgr.write_all()
            return model_mgr
        model_mgr = db_util.run_in_transaction(tr, model_id)
        model_mgr.write_end()
        
        return model_mgr.get_wrote_model(EventMovieViewData, model_id, EventMovieViewData.getByKey, model_id)
    
    @staticmethod
    def save_eventmovie_sessiondata(handler, uid, mid, name, is_pc, **kwargs):
        """イベント動画のセッションを保存.
        """
        remote_addr = handler.request.remote_addr
        if not remote_addr:
            return False
        
        redisdb = RedisModel.getDB()
        key = 'eventmovie:%s##%s' % (remote_addr, handler.osa_util.useragent.browser)
        data = {
            'uid' : uid,
            'mid' : mid,
            'name' : name,
            'is_pc' : is_pc,
        }
        data.update(**kwargs)
        strdata = cPickle.dumps(data)
        redisdb.set(key, strdata)
        redisdb.expire(key, 86400)
        
        return True
    
    @staticmethod
    def get_eventmovie_sessiondata(handler):
        """イベント動画のセッションを取得.
        """
        remote_addr = handler.request.remote_addr
        if remote_addr and remote_addr.find('10.116.41.') == 0:
            # rewriteで転送された.
            remote_addr = handler.request.django_request.META.get('HTTP_X_FORWARDED_FOR')
        
        if not remote_addr:
            return None
        
        key = 'eventmovie:%s##%s' % (remote_addr, handler.osa_util.useragent.browser)
        
        redisdb = RedisModel.getDB()
        strdata = redisdb.get(key)
        if strdata:
            try:
                obj = cPickle.loads(strdata)
                return obj
            except:
                pass
        return None
    
    @staticmethod
    def get_eventmovie_necessaryitems_dict(model_mgr, midlist, using=settings.DB_DEFAULT):
        """イベント動画のために必要なマスターデータのdict.
        {
            イベント動画ID : {
                'master' : EventMovieMaster,
                'sp' : MoviePlayList,
                'pc' : PcMoviePlayList,
            }
        }
        """
        result = {}
        eventmoviemasterlist = BackendApi.get_eventmovie_master_list(model_mgr, midlist, using=using)
        spmovienamelist = []
        pcmovienamelist = []
        for eventmoviemaster in eventmoviemasterlist:
            spmovienamelist.append(eventmoviemaster.sp)
            pcmovienamelist.append(eventmoviemaster.pc)
        
        spmovie_dict = BackendApi.get_movieplaylist_dict_by_uniquename(model_mgr, spmovienamelist, using=using)
        pcmovie_dict = BackendApi.get_pcmovieplaylist_dict_by_uniquename(model_mgr, pcmovienamelist, using=using)
        
        for eventmoviemaster in eventmoviemasterlist:
            result[eventmoviemaster.id] = {
                'master' : eventmoviemaster,
                'sp' : spmovie_dict[eventmoviemaster.sp],
                'pc' : pcmovie_dict[eventmoviemaster.pc],
            }
        return result
    
    @staticmethod
    def make_eventmovie_htmlobj_dict(handler, uid, midlist, openidlist=None):
        """イベント動画のHTML要オブジェクト.
        """
        model_mgr = handler.getModelMgr()
        openidlist = openidlist or []
        
        # 必要なマスターデータ.
        eventmovie_necessaryitems = BackendApi.get_eventmovie_necessaryitems_dict(model_mgr, midlist, using=settings.DB_READONLY)
        
        # 閲覧情報.
        viewdata_dict = BackendApi.get_eventmovie_viewdata_dict(model_mgr, uid, openidlist, using=settings.DB_READONLY)
        
        result = {}
        moviemaster_key = 'pc' if handler.is_pc else 'sp'
        for mid, items in eventmovie_necessaryitems.items():
            eventmoviemaster = items['master']
            moviemaster = items[moviemaster_key]
            viewdata = viewdata_dict.get(mid)
            is_open = mid in openidlist
            
            obj = Objects.eventmovie(handler, eventmoviemaster, moviemaster, viewdata, is_open)
            result[mid] = obj
        
        return result
    
    #===============================================================
    # プレイヤーのコンフィグ情報.
    @staticmethod
    def get_playerconfigdata(uid):
        """プレイヤーのコンフィグ情報を取得.
        """
        return PlayerConfigData.get(uid)
    
    @staticmethod
    def save_playerconfigdata(uid, scoutskip, autosell):
        """プレイヤーのコンフィグ情報を保存.
        """
        # スカウトのスキップは別にある.
        BackendApi.set_scoutskip_flag(uid, scoutskip)
        
        # その他の設定.
        model = PlayerConfigData.create(uid)
        model.setData(autosell)
        model.save()
        
        return model
    
    #===============================================================
    # パネルミッション.
    @staticmethod
    def get_panelmission_panelmaster(model_mgr, panel, using=settings.DB_DEFAULT):
        """パネルミッションのパネルのマスターを取得.
        """
        KEY = 'get_panelmission_panelmaster:%d:None' % panel
        client = localcache.Client()
        
        if client.get(KEY):
            return None
        
        model = BackendApi.get_model(model_mgr, PanelMissionPanelMaster, panel, using=using)
        if model is None:
            client.set(KEY, True)
        return model
    
    @staticmethod
    def get_panelmission_missionmaster(model_mgr, panel, number, using=settings.DB_DEFAULT):
        """パネルミッションのミッションのマスターを取得.
        """
        model_id = PanelMissionMissionMaster.makeID(panel, number)
        return BackendApi.get_model(model_mgr, PanelMissionMissionMaster, model_id, using=using)
    
    @staticmethod
    def get_panelmission_missionmaster_by_panelid(model_mgr, panel, using=settings.DB_DEFAULT):
        """パネルミッションのミッションのマスターをパネルIDを指定して取得.
        """
        model_idlist = [PanelMissionMissionMaster.makeID(panel, number) for number in xrange(1, Defines.PANELMISSION_MISSIN_NUM_PER_PANEL+1)]
        modellist =  BackendApi.get_model_list(model_mgr, PanelMissionMissionMaster, model_idlist, using=using)
        modellist.sort(key=lambda x:x.number)
        return modellist
    
    @staticmethod
    def get_panelmission_player(model_mgr, uid, using=settings.DB_DEFAULT):
        """パネルミッション用のプレイヤー情報.
        """
        return BackendApi.get_model(model_mgr, PlayerPanelMission, uid, get_instance=True, using=using)
    
    @staticmethod
    def get_panelmission_data(model_mgr, uid, panel, using=settings.DB_DEFAULT, for_update=False, get_instance=True):
        """パネルミッションの達成情報を取得.
        """
        model_id = PanelMissionData.makeID(uid, panel)
        missionplaydata = BackendApi.get_model(model_mgr, PanelMissionData, model_id, using=using)
        if missionplaydata is None:
            if get_instance:
                if for_update:
                    missionplaydata = PanelMissionData.makeInstance(model_id)
                    missionplaydata.insert()
                    model_mgr.set_save(missionplaydata)
                else:
                    def tr():
                        model_mgr = ModelRequestMgr()
                        missionplaydata = PanelMissionData.makeInstance(model_id)
                        model_mgr.set_save(missionplaydata)
                        model_mgr.write_all()
                        return model_mgr, missionplaydata
                    mng, missionplaydata = db_util.run_in_transaction(tr)
                    mng.write_end()
                model_mgr.set_got_models([missionplaydata], using=using)
                if for_update:
                    model_mgr.set_got_models_forupdate([missionplaydata])
        elif for_update:
            missionplaydata = model_mgr.get_model_forupdate(PanelMissionData, model_id)
        return missionplaydata
    
    @staticmethod
    def get_current_panelmission_panelmaster(model_mgr, uid, using=settings.DB_DEFAULT):
        """現在のパネルミッションのパネルのマスターを取得.
        """
        player = BackendApi.get_panelmission_player(model_mgr, uid, using=using)
        return BackendApi.get_panelmission_panelmaster(model_mgr, player.panel, using=using)
    
    @staticmethod
    def get_current_panelmission_data(model_mgr, uid, using=settings.DB_DEFAULT):
        """現在のパネルミッションの達成情報を取得.
        """
        player = BackendApi.get_panelmission_player(model_mgr, uid, using=using)
        if BackendApi.get_current_panelmission_panelmaster(model_mgr, uid, using=using):
            return BackendApi.get_panelmission_data(model_mgr, uid, player.panel, using=using)
        return None
    
    @staticmethod
    def check_lead_receive_panelmission(model_mgr, uid, now=None, using=settings.DB_DEFAULT):
        """パネルミッションの報酬受取へ遷移するかの判定.
        """
        missionplaydata = BackendApi.get_current_panelmission_data(model_mgr, uid, using=using)
        if missionplaydata is None:
            return False
        
        now = now or OSAUtil.get_now()
        for number in xrange(1, Defines.PANELMISSION_MISSIN_NUM_PER_PANEL+1):
            missiondata = missionplaydata.get_data(number)
            if missiondata['etime'] <= now < missiondata['rtime']:
                # 達成済みでみ受け取り.
                return True
        return False
    
    @staticmethod
    def check_lead_update_panelmission(model_mgr, v_player, panel, now=None, mission_executer=None, using=settings.DB_DEFAULT):
        """パネルミッションで何かしらの更新があるかの判定.
        """
        uid = v_player.id
        missionplaydata = BackendApi.get_current_panelmission_data(model_mgr, uid, using=using)
        if missionplaydata is None:
            # 全て終わっている.
            return False
        panel = missionplaydata.mid
        if panel != missionplaydata.mid:
            # 現在のパネルではない.
            return False
        
        # 対象のミッション.
        missionmaster_list = BackendApi.get_panelmission_missionmaster_by_panelid(model_mgr, panel)
        
        is_update = False
        for missionmaster in missionmaster_list:
            missiondata = missionplaydata.get_data(missionmaster.number)
            if missiondata['etime'] <= now:
                # 達成済み.
                if missiondata['rtime'] <= now:
                    # 受取済み.
                    continue
            elif missionmaster.condition_type == Defines.PanelMissionCondition.BATTLE_RANK_UP:
                battleplayer = BackendApi.get_battleplayer(model_mgr, uid, using=settings.DB_READONLY)
                if battleplayer is None or battleplayer.rank < missionmaster.condition_value1:
                    continue
                if mission_executer:
                    mission_executer.addTargetBattleRankUp(battleplayer.rank)
            elif missionmaster.condition_type == Defines.PanelMissionCondition.AREA_COMPLETE:
                areaid = missionmaster.condition_value1
                areacomplete = BackendApi.get_areaplaydata(model_mgr, uid, [areaid], using=settings.DB_READONLY).get(areaid)
                if areacomplete is None:
                    continue
                if mission_executer:
                    mission_executer.addTargetAreaComplete(areaid)
            elif missionmaster.condition_type == Defines.PanelMissionCondition.PLAYER_LEVEL:
                if v_player.level < missionmaster.condition_value1:
                    continue
                if mission_executer:
                    mission_executer.addTargetPlayerLevel(v_player.level)
            elif missionmaster.condition_type == Defines.PanelMissionCondition.HONOR_POINT:
                playerdata = model_mgr.get_model(CabaClubScorePlayerData, uid, using=settings.DB_READONLY)
                if playerdata is None:
                    continue
                point = playerdata.point
                if point is None or point < missionmaster.condition_value1:
                    continue
                elif mission_executer:
                    mission_executer.addTargetHonorPoint(point)
            elif missionmaster.condition_type in [Defines.PanelMissionCondition.CUSTOMER_TOTAL, Defines.PanelMissionCondition.PROCEEDS]:
                scoredata = BackendApi.get_cabaretclub_scoreplayerdata(model_mgr, uid, using=settings.DB_READONLY)
                scoredata_weekly = BackendApi.get_cabaretclub_scoreplayerdata_weekly(model_mgr, uid, OSAUtil.get_now(), using=settings.DB_READONLY)
                scoredata_total = Objects.cabaclub_management_info(None, scoredata, scoredata_weekly)

                if scoredata_total is None:
                    continue

                if missionmaster.condition_type == Defines.PanelMissionCondition.CUSTOMER_TOTAL:
                    if not scoredata_total.has_key("customer"):
                        continue

                    customer = scoredata_total["customer"]
                    if customer is None or customer < missionmaster.condition_value1:
                        continue
                    elif mission_executer:
                        mission_executer.addTargetCustomerTotal(customer)
                elif missionmaster.condition_type == Defines.PanelMissionCondition.PROCEEDS:
                    if not scoredata_total.has_key("proceeds"):
                        continue

                    proceeds = scoredata_total["proceeds"]
                    if proceeds is None or proceeds < (missionmaster.condition_value1*1000):
                        continue
                    if mission_executer:
                        mission_executer.addTargetProceeds(proceeds)
            else:
                continue
            # 何かしらの更新がある.
            is_update = True
            if mission_executer is None:
                break
        return is_update
    
    @staticmethod
    def make_panelmission_panel_htmlobj(handler, panelmaster, obj_mission_list, is_cleared, using=settings.DB_DEFAULT):
        """パネルミッションのHTML用パネルデータを作成.
        """
        model_mgr = handler.getModelMgr()
        
        prizeinfo = None
        if panelmaster.prizes:
            prizelist = BackendApi.get_prizelist(model_mgr, panelmaster.prizes, using=using)
            prizeinfo = BackendApi.make_prizeinfo(handler, prizelist, using=using)
        
        return Objects.panelmission(handler, panelmaster, obj_mission_list, prizeinfo, is_cleared=is_cleared)
        
    @staticmethod
    def make_panelmission_mission_htmlobj(handler, v_player, missionmaster, is_cleared, missionplaydata, now=None, using=settings.DB_DEFAULT):
        """パネルミッションのHTML用ミッションデータを作成.
        """
        model_mgr = handler.getModelMgr()
        uid = v_player.id
        current_value = None
        target_value = PanelMissionConditionExecuter().getConditionValue(missionmaster)
        is_received = is_cleared
        now = now or OSAUtil.get_now()
        
        if missionplaydata:
            missiondata = missionplaydata.get_data(missionmaster.number)
            if is_cleared or missiondata['etime'] <= now:
                # 達成済み.
                current_value = target_value
                if missiondata['rtime'] <= now:
                    # 受取済み.
                    is_received = True
            elif missionmaster.condition_type == Defines.PanelMissionCondition.BATTLE_RANK_UP:
                battleplayer = BackendApi.get_battleplayer(model_mgr, uid, using=settings.DB_READONLY)
                current_value = int(bool(battleplayer and missionmaster.condition_value1 <= battleplayer.rank))
            elif missionmaster.condition_type == Defines.PanelMissionCondition.AREA_COMPLETE:
                areaid = missionmaster.condition_value1
                areacomplete = BackendApi.get_areaplaydata(model_mgr, uid, [areaid], using=settings.DB_READONLY).get(areaid)
                current_value = int(areacomplete is not None)
            elif missionmaster.condition_type == Defines.PanelMissionCondition.PLAYER_LEVEL:
                current_value = v_player.level
            
            current_value = min(target_value, current_value if current_value is not None else missiondata['cnt'])
        else:
            current_value = target_value if is_cleared else 0
        
        prizeinfo = None
        if missionmaster.prizes:
            prizelist = BackendApi.get_prizelist(model_mgr, missionmaster.prizes, using=using)
            prizeinfo = BackendApi.make_prizeinfo(handler, prizelist, using=using)
        
        return Objects.panelmission_mission(handler, missionmaster, current_value, target_value, prizeinfo, is_received)
    
    @staticmethod
    def tr_complete_panelmission(model_mgr, uid, executer, now=None, confirmkey=None):
        """パネルミッションの達成書き込み.
        """
        now = now or OSAUtil.get_now()
        if confirmkey is not None:
            BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        
        # 現在のパネル.
        cur_panelmissionmaster = BackendApi.get_current_panelmission_panelmaster(model_mgr, uid)
        if cur_panelmissionmaster is None:
            return False
        panel = cur_panelmissionmaster.id
        
        # 対象のミッション.
        missionmaster_list = BackendApi.get_panelmission_missionmaster_by_panelid(model_mgr, panel)
        missionmaster_list = [missionmaster for missionmaster in missionmaster_list if 0 < executer.getTargetNum(missionmaster.condition_type)]
        if not missionmaster_list:
            return False
        
        # 進行情報.
        missionplaydata = BackendApi.get_panelmission_data(model_mgr, uid, panel, for_update=True)
        
        # 進行.
        is_update = False
        for missionmaster in missionmaster_list:
            if executer.getTargetNum(missionmaster.condition_type) < 1:
                continue
            
            missiondata = missionplaydata.get_data(missionmaster.number)
            if missiondata['etime'] <= now:
                # 達成済み.
                continue
            # 進行.
            executer.execute(missionmaster, missionplaydata, now=now)
            is_update = True
        
        if is_update:
            model_mgr.set_save(missionplaydata)
        
        return is_update
    
    @staticmethod
    def tr_receive_panelmission(model_mgr, uid, panel, confirmkey, now=None):
        """パネルミッションの報酬受取書き込み.
        """
        now = now or OSAUtil.get_now()
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        
        # 進行情報.
        cur_panelmissionmaster = BackendApi.get_current_panelmission_panelmaster(model_mgr, uid)
        if cur_panelmissionmaster is None or panel != cur_panelmissionmaster.id:
            raise CabaretError(u'パネルの指定が間違っています', CabaretError.Code.ILLEGAL_ARGS)
        
        panel = cur_panelmissionmaster.id
        
        # 対象のミッション.
        missionmaster_list = BackendApi.get_panelmission_missionmaster_by_panelid(model_mgr, panel)
        
        # 進行情報.
        missionplaydata = BackendApi.get_panelmission_data(model_mgr, uid, panel, for_update=True)
        
        # 進行.
        is_allend = True
        for missionmaster in missionmaster_list:
            missiondata = missionplaydata.get_data(missionmaster.number)
            if missiondata['rtime'] <= now:
                # 取得済み.
                continue
            elif missiondata['etime'] <= now:
                # 達成済みで未取得.
                if missionmaster.prizes:
                    prizelist = BackendApi.get_prizelist(model_mgr, missionmaster.prizes)
                    BackendApi.tr_add_prize(model_mgr, uid, prizelist, missionmaster.prize_text)
                missiondata['rtime'] = now
                missiondata = missionplaydata.set_data(missionmaster.number, **missiondata)
            else:
                is_allend = False
        model_mgr.set_save(missionplaydata)
        
        if is_allend:
            # パネル達成報酬.
            if cur_panelmissionmaster.prizes:
                prizelist = BackendApi.get_prizelist(model_mgr, cur_panelmissionmaster.prizes)
                BackendApi.tr_add_prize(model_mgr, uid, prizelist, cur_panelmissionmaster.prize_text)
            
            # すべて達成した場合は次のパネルへ.
            def forUpdate(model, inserted, panel):
                model.cleared = panel
                model.panel = panel + 1
            model_mgr.add_forupdate_task(PlayerPanelMission, uid, forUpdate, panel)
    #======================================================================================================
    # キャバクラシステム.
    @staticmethod
    def to_cabaretclub_section_starttime(now=None):
        """キャバクラシステムのセクションの開始時間.
        毎週月曜AM 4:00.
        """
        now = now or OSAUtil.get_now()
        basetime = DateTimeUtil.toLoginTime(now, Defines.CABARETCLUB_EVENT_DATE_CHANGE_TIME)
        cur_monday = basetime - datetime.timedelta(days=basetime.weekday())
        return cur_monday
    
    @staticmethod
    def to_cabaretclub_section_endtime(now=None):
        """キャバクラシステムのセクションの終了時間.
        毎週月曜AM 4:00.
        """
        cur_monday = BackendApi.to_cabaretclub_section_starttime(now)
        return cur_monday + datetime.timedelta(days=7)
    
    @staticmethod
    def get_cabaretclub_current_master(model_mgr, now, using=settings.DB_DEFAULT, reflesh=False):
        """現在のキャバクラシステムのマスターデータを取得.
        """
        # その日の基準時間に直す.終了時間の7日前==開始時間.
        basetime = BackendApi.to_cabaretclub_section_starttime(now)
        # その週を数値に.
        week = int(basetime.strftime("%Y%W"))
        # キャッシュクライアント.
        client = OSAUtil.get_cache_client()
        key = 'get_cabaretclub_current_master'
        master_id = None
        if not reflesh:
            # キャッシュから取得.
            data = client.get(key)
            if data:
                master_id, next_week = data
                if next_week and next_week <= week:
                    # 切り替える.
                    master_id = None
        if master_id is None:
            master_list = model_mgr.get_mastermodel_all(CabaClubMaster, order_by='-week', using=using)
            current_master = None
            next_master_week = None
            for master in master_list:
                if master.week < week:
                    current_master = master
                    break
                next_master_week = master.week
            master_id = current_master.id if current_master else 0
            client.set(key, (master_id, next_master_week), time=0)
            return current_master
        elif 0 < master_id:
            return BackendApi.get_model(model_mgr, CabaClubMaster, master_id, using=using)
        else:
            return None

    @staticmethod
    def is_cabaclubrankevent_open(model_mgr, using=settings.DB_DEFAULT, now=None):
        """キャバクラランクイベントが開催中か.
        """
        return BackendApi.get_current_cabaclubrankeventmaster(model_mgr, using=using) is not None

    @staticmethod
    def get_cabaretclub_store_master(model_mgr, mid, using=settings.DB_DEFAULT):
        """キャバクラ店舗のマスターデータを取得.
        """
        return BackendApi.get_model(model_mgr, CabaClubStoreMaster, mid, using=using)
    
    @staticmethod
    def get_cabaretclub_store_master_dict(model_mgr, midlist, using=settings.DB_DEFAULT):
        """キャバクラ店舗のマスターデータを複数取得.
        """
        return BackendApi.get_model_dict(model_mgr, CabaClubStoreMaster, midlist, using=using)
    
    @staticmethod
    def get_cabaretclub_store_master_all(model_mgr, using=settings.DB_DEFAULT):
        """キャバクラ店舗のマスターデータを全て取得.
        """
        return model_mgr.get_mastermodel_all(CabaClubStoreMaster, 'id', using=using)
    
    @staticmethod
    def get_cabaretclub_event_master(model_mgr, mid, using=settings.DB_DEFAULT):
        """キャバクラ発生イベントのマスターデータを取得.
        """
        return BackendApi.get_model(model_mgr, CabaClubEventMaster, mid, using=using)
    
    @staticmethod
    def get_cabaretclub_event_master_dict(model_mgr, midlist, using=settings.DB_DEFAULT):
        """キャバクラ発生イベントのマスターデータを複数取得.
        """
        return BackendApi.get_model_dict(model_mgr, CabaClubEventMaster, midlist, using=using)
    
    @staticmethod
    def get_cabaretclub_storeplayerdata_dict(model_mgr, uid, midlist, using=settings.DB_DEFAULT):
        """キャバクラ店舗のプレイヤー情報を複数取得.
        """
        idlist = [CabaClubStorePlayerData.makeID(uid, mid) for mid in midlist]
        return BackendApi.get_model_dict(model_mgr, CabaClubStorePlayerData, idlist, using=using, key=lambda x:x.mid)
    
    @staticmethod
    def get_cabaretclub_storeplayerdata(model_mgr, uid, mid, using=settings.DB_DEFAULT):
        """キャバクラ店舗のプレイヤー情報を取得.
        """
        return BackendApi.get_cabaretclub_storeplayerdata_dict(model_mgr, uid, [mid], using).get(mid)
    
    @staticmethod
    def get_cabaretclub_scoreplayerdata(model_mgr, uid, using=settings.DB_DEFAULT):
        """キャバクラシステムのスコア情報の取得.
        総売上,総集客数,特別なマネー,名誉ポイント.
        """
        return BackendApi.get_model(model_mgr, CabaClubScorePlayerData, uid, using=using)
    
    @staticmethod
    def get_cabaretclub_scoreplayerdata_weekly(model_mgr, uid, now, using=settings.DB_DEFAULT):
        """キャバクラシステムの週間スコア情報の取得.
        売上,集客数.
        """
        etime = BackendApi.to_cabaretclub_section_starttime(now)
        ins_id = CabaClubScorePlayerDataWeekly.makeID(uid, etime)
        return BackendApi.get_model(model_mgr, CabaClubScorePlayerDataWeekly, ins_id, using=using)
    
    @staticmethod
    def get_cabaretclub_castdata_dict(model_mgr, uid, midlist, using=settings.DB_DEFAULT):
        """キャバクラ店舗に配属されているキャスト情報を複数取得.
        """
        idlist = [CabaClubCastPlayerData.makeID(uid, mid) for mid in midlist]
        return BackendApi.get_model_dict(model_mgr, CabaClubCastPlayerData, idlist, using=using, key=lambda x:x.mid)
    
    @staticmethod
    def get_cabaretclub_castdata(model_mgr, uid, mid, using=settings.DB_DEFAULT):
        """キャバクラ店舗に配属されているキャスト情報を取得.
        """
        return BackendApi.get_cabaretclub_castdata_dict(model_mgr, uid, [mid], using).get(mid)
    
    @staticmethod
    def get_cabaretclub_rankingdata_dict(model_mgr, midlist, using=settings.DB_DEFAULT):
        """経営イベントのランキング情報を複数取得
        """
        return BackendApi.get_model_dict(model_mgr, CabaClubEventRankMaster, midlist, using=using)

    @staticmethod
    def get_cabaretclub_rankingdata(model_mgr, mid, using=settings.DB_DEFAULT):
        """経営イベントのランキング情報を取得
        """
        return BackendApi.get_cabaretclub_rankingdata_dict(model_mgr, [mid], using).get(mid)

    @staticmethod
    def get_cabaretclub_active_cast_dict(model_mgr, uid, now, using=settings.DB_DEFAULT):
        """キャバクラ店舗に配属されているキャストIDを取得.
        """
        if using == settings.DB_READONLY:
            midlist = model_mgr.get_mastermodel_idlist(CabaClubStoreMaster)
            cast_playerdata_list = BackendApi.get_cabaretclub_castdata_dict(model_mgr, uid, midlist, using=using).values()
        else:
            cast_playerdata_list = CabaClubCastPlayerData.fetchByOwner(uid, using=using)
        if not cast_playerdata_list:
            return {}
        cast_playerdata_dict = dict([(cast_playerdata.mid, cast_playerdata) for cast_playerdata in cast_playerdata_list])
        midlist = cast_playerdata_dict.keys()
        playdata_dict = BackendApi.get_cabaretclub_storeplayerdata_dict(model_mgr, uid, midlist, using=using)
        midlist = playdata_dict.keys()
        master_dict = BackendApi.get_cabaretclub_store_master_dict(model_mgr, midlist, using=settings.DB_READONLY)
        dest = {}
        for mid, master in master_dict.items():
            storeset = CabaclubStoreSet(master, playdata_dict[mid])
            if not storeset.is_alive(now):
                continue
            dest[mid] = cast_playerdata_dict[mid].cast[:]
        return dest
    
    @staticmethod
    def get_cabaretclub_active_cast_list(model_mgr, uid, now, using=settings.DB_DEFAULT):
        """キャバクラ店舗に配属されているキャストIDをlistで取得.
        """
        store_castidlist_dict = BackendApi.get_cabaretclub_active_cast_dict(model_mgr, uid, OSAUtil.get_now(), using=using)
        store_castidlist = []
        for idlist in store_castidlist_dict.values():
            store_castidlist.extend(idlist)
        return store_castidlist
    
    @staticmethod
    def get_cabaretclub_item_playerdata(model_mgr, uid, using=settings.DB_DEFAULT):
        """キャバクラ店舗のアイテム使用情報.
        """
        return BackendApi.get_model(model_mgr, CabaClubItemPlayerData, uid, using=using)
    
    @staticmethod
    def get_cabaretclub_storeset_dict(model_mgr, uid, midlist, using=settings.DB_DEFAULT):
        """キャバクラ店舗情報をまとめて複数取得.
        """
        # マスターデータ.
        master_dict = BackendApi.get_cabaretclub_store_master_dict(model_mgr, midlist, using=using)
        # ユーザー情報.
        userdata_dict = BackendApi.get_cabaretclub_storeplayerdata_dict(model_mgr, uid, master_dict.keys(), using=using)
        # アイテム使用情報.
        itemdata = BackendApi.get_cabaretclub_item_playerdata(model_mgr, uid, using=using)
        # イベント情報.
        eventmaster_id_list = list(set([userdata.event_id for userdata in userdata_dict.values() if userdata.event_id]))
        eventmaster_dict = BackendApi.get_cabaretclub_event_master_dict(model_mgr, eventmaster_id_list, using=using)
        # まとめる.
        dest = dict([(mid, CabaclubStoreSet(master_dict[mid], userdata, itemdata, eventmaster_dict.get(userdata.event_id))) for mid, userdata in userdata_dict.items()])
        return dest
    
    @staticmethod
    def get_cabaretclub_storeset_dict_all(model_mgr, uid, using=settings.DB_DEFAULT):
        """キャバクラ店舗情報をまとめて全て取得.
        """
        # マスターID.
        midlist = model_mgr.get_mastermodel_idlist(CabaClubStoreMaster, using=settings.DB_READONLY)
        return BackendApi.get_cabaretclub_storeset_dict(model_mgr, uid, midlist, using)
    
    @staticmethod
    def get_cabaretclub_storeset(model_mgr, uid, mid, using=settings.DB_DEFAULT):
        """キャバクラ店舗情報をまとめて取得.
        """
        return BackendApi.get_cabaretclub_storeset_dict(model_mgr, uid, [mid], using).get(mid)
    
    @staticmethod
    def get_cabaclub_setable_cardlist(model_mgr, uid, now, ctype=None, sortby='-ctime', offset=0, limit=-1, using=settings.DB_DEFAULT):
        """店舗に設定可能なキャスト.
        """
        # 配置済みのキャスト.
        excludes = BackendApi.get_cabaretclub_active_cast_list(model_mgr, uid, now, using)
        # デッキ設定中のキャスト.
        excludes.extend(BackendApi.get_deck_castid_list(model_mgr, uid, using))
        filter_func = lambda x,y,excludes : not x.id in excludes
        filter_obj = CardListFilter(ckind=Defines.CardKind.NORMAL, ctype=ctype)
        filter_obj.add_optional_filter(filter_func, excludes)
        cardlist = BackendApi._get_card_list(uid, offset, limit=limit, filter_obj=filter_obj, sortby=sortby, arg_model_mgr=model_mgr, using=using)
        return cardlist
    
    @staticmethod
    def tr_add_cabaretclub_money(model_mgr, uid, value, do_check_notenough=True):
        """特別なマネーの加算.
        """
        def forUpdateTask(model, inserted):
            if settings_sub.IS_BENCH:
                return
            v = model.money + value
            if v < 0 and do_check_notenough:
                raise CabaretError(u'{}が足りません'.format(Defines.ItemType.NAMES[Defines.ItemType.CABARETCLUB_SPECIAL_MONEY]), CabaretError.Code.NOT_ENOUGH)
            model.money = max(0, min(v, Defines.VALUE_MAX))
            return ['money']
        model_mgr.add_forupdate_task(CabaClubScorePlayerData, uid, forUpdateTask)
    
    @staticmethod
    def tr_add_cabaretclub_honor_point(model_mgr, uid, value, do_check_notenough=True):
        """名誉ポイントの加算.
        """
        def forUpdateTask(model, inserted):
            if settings_sub.IS_BENCH:
                return
            v = model.point + value
            if v < 0 and do_check_notenough:
                raise CabaretError(u'{}が足りません'.format(Defines.ItemType.NAMES[Defines.ItemType.CABARETCLUB_HONOR_POINT]), CabaretError.Code.NOT_ENOUGH)
            model.point = max(0, min(v, Defines.VALUE_MAX))
            return ['point']
        model_mgr.add_forupdate_task(CabaClubScorePlayerData, uid, forUpdateTask)
    
    @staticmethod
    def tr_add_cabaretclub_customer_and_proceeds(model_mgr, uid, cabaclubstoremaster, customer, proceeds, now):
        """集客数と売上の加算.
        """
        if customer == 0 and proceeds == 0:
            return
        
        def add_proceeds(model):
            model.proceeds = max(0, min(model.proceeds + proceeds, Defines.VALUE_MAX_BIG))
            model.today_proceeds = max(0, min(model.today_proceeds + proceeds, Defines.VALUE_MAX_BIG))
        def add_score(model, inserted):
            model.customer = max(0, min(model.customer + customer, Defines.VALUE_MAX_BIG))
            model.proceeds = max(0, min(model.proceeds + proceeds, Defines.VALUE_MAX_BIG))
        # 週間.
        etime = BackendApi.to_cabaretclub_section_starttime(now)
        weekly_model_id = CabaClubScorePlayerDataWeekly.makeID(uid, etime)
        weekly_model = model_mgr.get_model(CabaClubScorePlayerDataWeekly, weekly_model_id)
        if weekly_model is None:
            weekly_model = CabaClubScorePlayerDataWeekly.makeInstance(weekly_model_id)
            weekly_model.insert()
            model_mgr.set_got_models_forupdate([weekly_model])
            model_mgr.set_got_models([weekly_model])
            inserted = True
        else:
            weekly_model = model_mgr.get_model_forupdate(CabaClubScorePlayerDataWeekly, weekly_model_id)
            model_mgr.set_got_models([weekly_model])
            inserted = False
        customer_pre = weekly_model.customer
        add_score(weekly_model, inserted)
        model_mgr.set_save(weekly_model)
        # 店舗別の合計.
        storeplayerdata = BackendApi.__get_cabaretclub_storeplayerdata_forupdate(model_mgr, uid, cabaclubstoremaster.id, now)
        add_score(storeplayerdata, False)
        # 集客数達成報酬.
        if 0 < customer:
            master = BackendApi.get_cabaretclub_current_master(model_mgr, now, using=settings.DB_READONLY)
            if master is not None and 0 < master.customer_prize_interval and master.customer_prizes:
                customer_prize_cnt_pre = int(customer_pre / master.customer_prize_interval)
                customer_prize_cnt_post = int(weekly_model.customer / master.customer_prize_interval)
                cur_customer_prize_cnt = customer_prize_cnt_post - customer_prize_cnt_pre
                if 0 < cur_customer_prize_cnt:
                    total = sum(dict(master.customer_prizes).values())
                    prizeidlist = []
                    for _ in xrange(cur_customer_prize_cnt):
                        v = randint(1, 10000)
                        if total < v:
                            # ハズレ.
                            continue
                        for prizeid, rate in master.customer_prizes:
                            v -= rate
                            if v < 1:
                                prizeidlist.append(prizeid)
                                break
                    if prizeidlist:
                        prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
                        BackendApi.tr_add_prize(model_mgr, uid, prizelist, master.customer_prize_text)

        is_open_cabaclubevent = bool(BackendApi.get_current_cabaclubrankeventmaster(model_mgr, using=settings.DB_READONLY, now=now))
        if is_open_cabaclubevent:
            # 経営イベント別の合計
            cabaclubrankingdata = BackendApi.__get_cabaretclub_rankingdata_forupdate(model_mgr, uid, is_open_cabaclubevent)
            add_proceeds(cabaclubrankingdata)
            model_mgr.set_save(cabaclubrankingdata)
            # Write player proceeds (sales) data to Redis DB
            def writeEnd():
                redisdb = RedisModel.getDB()
                pipe = redisdb.pipeline()
                CabaClubRanking.create(cabaclubrankingdata.mid, uid, cabaclubrankingdata.proceeds).save(pipe)
                pipe.execute()
            model_mgr.add_write_end_method(writeEnd)
    
    @staticmethod
    def __get_cabaretclub_storeplayerdata_forupdate(model_mgr, uid, mid, now, make_instance=True):
        """キャバクラ店舗のプレイヤーデータを行ロックして取得.
        """
        playdata = BackendApi.get_cabaretclub_storeplayerdata(model_mgr, uid, mid)
        if playdata is None:
            if make_instance:
                playdata = CabaClubStorePlayerData.makeInstance(CabaClubStorePlayerData.makeID(uid, mid))
                playdata.rtime = playdata.ltime = playdata.etime = playdata.utime = now
                playdata.insert()
                model_mgr.set_got_models_forupdate([playdata])
                model_mgr.set_got_models([playdata])
        else:
            playdata = model_mgr.get_model_forupdate(CabaClubStorePlayerData, CabaClubStorePlayerData.makeID(uid, mid))
            model_mgr.set_got_models([playdata])
        return playdata
    
    @staticmethod
    def __get_cabaretclub_rankingdata_forupdate(model_mgr, uid, is_open_cabaclubevent, make_instance=True):
        # 経営イベント別の合計
        ranking_model = None
        if is_open_cabaclubevent:
            cabaclubrankeventconfig = BackendApi.get_current_cabaclubrankeventconfig(model_mgr, using=settings.DB_READONLY)
            if not CabaClubRanking.exists(cabaclubrankeventconfig.mid):
                # if ranking data isn't present in Redis
                # fetch the ranking data from the database and store it into Redis
                BackendApi.backup_ranking_data_into_redis(cabaclubrankeventconfig.mid)

            ranking_model_id = CabaClubEventRankMaster.makeID(uid, cabaclubrankeventconfig.mid)
            ranking_model = model_mgr.get_model(CabaClubEventRankMaster, ranking_model_id)
            if ranking_model is None:
                if make_instance:
                    ranking_model = CabaClubEventRankMaster.createInstance(ranking_model_id, uid)
                    ranking_model.insert()
                    model_mgr.set_got_models_forupdate([ranking_model])
                    model_mgr.set_got_models([ranking_model])
            else:
                ranking_model = model_mgr.get_model_forupdate(CabaClubEventRankMaster, ranking_model_id)
                model_mgr.set_got_models([ranking_model])
        return ranking_model

    @staticmethod
    def backup_ranking_data_into_redis(eventid):
        """In the case where players' ranking data previously stored in Redis DB
           is wiped out (due to unforeseen circumstances), get the ranking data from the MYSQL database and store
           it in Redis DB
        """
        model_mgr = ModelRequestMgr()
        ranking_data = CabaClubEventRankMaster.fetchValues(using=settings.DB_READONLY, filters={'mid': eventid})

        if ranking_data:
            def writeEnd():
                redisdb = RedisModel.getDB()
                pipe = redisdb.pipeline()
                for rank in ranking_data:
                    # Redisに書き込む
                    CabaClubRanking.create(rank.mid, rank.uid, rank.proceeds).save(pipe)
                pipe.execute()
            model_mgr.add_write_end_method(writeEnd)
        model_mgr.write_all()
        model_mgr.write_end()

    @staticmethod
    def __get_cabaretclub_storeset_for_update(model_mgr, uid, cabaclubstoremaster, now, make_instance=False, with_itemdata=False, with_eventmaster=False, do_check_alive=True, do_check_open=False, do_check_close=False):
        """書き込み用に店舗情報を取得.
        """
        assert not (do_check_open and do_check_close), u"do_check_openとdo_check_closeが両方Trueになっている.実装ミスです."
        # マスターデータ.
        if isinstance(cabaclubstoremaster, CabaClubStoreMaster):
            mid = cabaclubstoremaster.id
        else:
            mid = cabaclubstoremaster
            cabaclubstoremaster = BackendApi.get_cabaretclub_store_master(model_mgr, mid)
        # 店情報を取得.
        playdata = BackendApi.__get_cabaretclub_storeplayerdata_forupdate(model_mgr, uid, mid, now, make_instance=make_instance)
        if playdata is None and do_check_alive:
            raise CabaretError(u'店舗情報が存在しません', CabaretError.Code.NOT_DATA)
        # 開店閉店チェック.
        if do_check_open:
            if playdata is None or not playdata.is_open:
                raise CabaretError(u'閉店中は変更できません', CabaretError.Code.ILLEGAL_ARGS)
        elif do_check_close:
            if playdata and playdata.is_open:
                raise CabaretError(u'開店中は変更できません', CabaretError.Code.ILLEGAL_ARGS)
        # 借り入れチェック.
        if do_check_alive:
            # 仮で店舗情報を作成.
            tmp_storeset = CabaclubStoreSet(cabaclubstoremaster, playdata)
            if not tmp_storeset.is_alive(now):
                raise CabaretError(u'店舗を借りていません', CabaretError.Code.ILLEGAL_ARGS)
        # アイテム情報.
        if with_itemdata is None or isinstance(with_itemdata, CabaClubItemPlayerData):
            itemdata = with_itemdata
        elif with_itemdata:
            itemdata = BackendApi.get_cabaretclub_item_playerdata(model_mgr, uid)
        else:
            itemdata = None
        # イベント情報.
        if with_eventmaster is None or isinstance(with_eventmaster, CabaClubEventMaster):
            eventmaster = with_eventmaster
        elif with_eventmaster and playdata and playdata.event_id:
            eventmaster = BackendApi.get_cabaretclub_event_master(model_mgr, playdata.event_id, using=settings.DB_READONLY)
        else:
            eventmaster = None
        if playdata:
            return CabaclubStoreSet(cabaclubstoremaster, playdata, itemdata, eventmaster)
        else:
            return None
    
    @staticmethod
    def tr_cabaclub_store_rent(model_mgr, uid, cabaclubstoremaster, days, now):
        """キャバクラ店舗の借り入れ.
        """
        # 店情報を取得.
        storeset = BackendApi.__get_cabaretclub_storeset_for_update(model_mgr, uid, cabaclubstoremaster, now, make_instance=True, do_check_alive=False)
        cabaclubstoremaster = storeset.master
        # 既に借りているかを確認.
        if storeset.is_alive(now):
            # 既に借りている.
            raise CabaretError(u'既に借りています', code=CabaretError.Code.ALREADY_RECEIVED)
        
        cost = storeset.get_rental_cost(days)
        if cost is None:
            raise CabaretError(u'借り入れ日数が不正です', code=CabaretError.Code.ILLEGAL_ARGS)
        
        elif storeset.playerdata.is_open:
            # 開店状態の場合は期限切れの時間までの売上を更新する必要あり.
            endtime = storeset.get_limit_time() - datetime.timedelta(microseconds=1)
            BackendApi.tr_cabaclubstore_close(model_mgr, uid, storeset.master, endtime)
        
        playdata = storeset.playerdata
        # 借りた時間.
        playdata.rtime = now
        # 借用期限を記録.
        playdata.ltime = now + datetime.timedelta(days=days)
        # 売上と集客数をリセット.
        playdata.customer = 0
        playdata.proceeds = 0
        # イベントもリセットしておく.
        playdata.event_id = 0
        playdata.etime = now
        # スカウトマンのリセット.
        playdata.scoutman_add = 0
        # 開閉店の記録時間を更新.
        playdata.octime = now
        # 売上を更新した時間を更新.
        playdata.utime = now
        # 閉店状態にしておく.
        playdata.is_open = False
        # 保存予約.
        model_mgr.set_save(playdata)
        # 配置されているキャストの確認.
        castdata = BackendApi.get_cabaretclub_castdata(model_mgr, uid, storeset.master.id)
        if castdata and castdata.cast:
            # 重複を修正する.
            BackendApi.correct_duplication_cabaretclub_cast(castdata)
            # デッキに配置された可能性.
            deck_cardidlist = BackendApi.get_deck_castid_list(model_mgr, uid)
            # 他の店舗に配置された可能性.
            store_castidlist_dict = BackendApi.get_cabaretclub_active_cast_dict(model_mgr, uid, OSAUtil.get_now())
            store_castidlist = []
            for mid, idlist in store_castidlist_dict.items():
                if mid == storeset.master.id:
                    continue
                store_castidlist.extend(idlist)
            # キャストがもういない可能性.
            cardlist = BackendApi.get_cards(castdata.cast, model_mgr)
            card_idlist = [cardset.id for cardset in cardlist]
            cardidlist = list((set(castdata.cast) & set(card_idlist) - set(deck_cardidlist) - set(store_castidlist)))
            if len(cardidlist) != len(castdata.cast):
                # いなくなった分を削って再配置.
                cardidlist.sort(key=lambda x:castdata.cast.index(x))
                BackendApi.tr_cabaclubstore_set_cast(model_mgr, uid, storeset.master, cardidlist, now)
        # 特別なマネーを消費.
        BackendApi.tr_add_cabaretclub_money(model_mgr, uid, -cost)
        # ログ.
        model_mgr.set_save(UserLogCabaClubStore.createLogRental(uid, cabaclubstoremaster.id, now, days))
    
    @staticmethod
    def tr_cabaclub_store_open(model_mgr, uid, cabaclubstoremaster, now):
        """キャバクラ店舗のオープン.
        """
        # 店情報を取得.
        storeset = BackendApi.__get_cabaretclub_storeset_for_update(model_mgr, uid, cabaclubstoremaster, now, do_check_alive=True)
        if storeset.playerdata.is_open:
            raise CabaretError(u'既に開店しています', CabaretError.Code.ALREADY_RECEIVED)
        cabaclubstoremaster = storeset.master
        playdata = storeset.playerdata
        # 売上を更新した時間を更新.
        octime = playdata.octime if playdata.rtime < playdata.octime else playdata.utime
        diff = octime - playdata.utime
        playdata.utime = now - diff
        # イベント時間を更新.
        octime = playdata.octime if playdata.rtime < playdata.octime else playdata.etime
        diff = octime - playdata.etime
        playdata.etime = now - diff
        # 開店.
        playdata.is_open = True
        # 開店時間を記録.
        playdata.octime = now
        # 保存予約.
        model_mgr.set_save(playdata)
        # キャスト.
        castdata = BackendApi.get_cabaretclub_castdata(model_mgr, uid, cabaclubstoremaster.id)
        if castdata:
            cardlist = BackendApi.get_cards(castdata.cast, model_mgr, using=settings.DB_READONLY)
            cardmidlist = [card.master.id for card in cardlist]
        else:
            cardmidlist = []
        # ミッション.
        mission_executer = PanelMissionConditionExecuter()
        # 経営をプレイ達成を登録.
        mission_executer.addTargetPlayCabaclub()
        # ミッション達成書き込み.
        BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer, now)
        # ログ.
        model_mgr.set_save(UserLogCabaClubStore.createLogOpen(uid, cabaclubstoremaster.id, now, playdata.event_id, cardmidlist, cabaclubstoremaster.scoutman_num_max + playdata.scoutman_add))
    
    @staticmethod
    def filter_has_cabaclubskill(cardlist):
        dest = []
        for card in cardlist:
            skill = card.master.getSkill()
            if skill and skill.eskill == Defines.SkillEffect.CABACLUB:
                dest.append(card)
        return dest

    @staticmethod
    def calc_cabaclubskill_correction(cardlist):
        total_powerup = 1
        for card in cardlist:
            skill = card.master.getSkill()
            if skill is None:
                continue

            # 経営スキルは発動率のフィールドに補正値を設定してある….
            total_powerup += (skill.get_rate(card.card.skilllevel) / float(100))
        return total_powerup

    @staticmethod
    def calc_cabaretclub_customer_and_proceeds(model_mgr, uid, storeset, eventbonus_customer_up, eventbonus_proceeds_up, test_cnt, now):
        """集客数と売上の計算.
        """
        customer, proceeds = 0, 0
        if test_cnt < 1:
            return customer, proceeds
        cabaclubstoremaster = storeset.master
        scoutman_num = storeset.playerdata.scoutman_add + cabaclubstoremaster.scoutman_num_max
        if scoutman_num < 1:
            return customer, proceeds
        # 配属されているキャスト.
        castdata = BackendApi.get_cabaretclub_castdata(model_mgr, uid, cabaclubstoremaster.id)
        if not (castdata and castdata.cast):
            return customer, proceeds
        # カード取得.
        cardlist = BackendApi.get_cards(castdata.cast, model_mgr, using=settings.DB_READONLY)
        cast_num = len(cardlist)
        if cast_num < 1:
            return customer, proceeds
        # レアリティ補正.
        cabaclubmaster = BackendApi.get_cabaretclub_current_master(model_mgr, now, using=settings.DB_READONLY)
        cr_correction = cabaclubmaster.cr_correction if cabaclubmaster else dict()
        # 属性補正.
        ctype_customer_correction = cabaclubmaster.ctype_customer_correction if cabaclubmaster else dict()
        ctype_proceeds_correction = cabaclubmaster.ctype_proceeds_correction if cabaclubmaster else dict()
        # いろいろな補正値の集計.デッキ設定でやりたいけどマスターデータを変えられたら困るからここで.
        cost_total = 0
        cr_correction_total = 0
        cabaclub_customer_up_total = 0
        cabaclub_proceeds_up_total = 0
        for card in cardlist:
            master = card.master
            cost_total += master.cost
            cr_correction_total += cr_correction.get(str(master.rare), 100)
            cabaclub_customer_up_total += ctype_customer_correction.get(str(master.ctype), 100)
            cabaclub_proceeds_up_total += ctype_proceeds_correction.get(str(master.ctype), 100)
        # 集客数の計算.
        # (スカウトマン数)*(設定されているキャスト属性集客補正の合計値/設定されているキャスト数)*(キャストレリティ補正)*(乱数値0.8～1.2)*(集客数補正、イベント起きてない場合は1).
        # 忘れそうなのでメモ.eventbonusdata['costomer_up']は補正値の合計ですよ.eventbonusdata['costomer_up'] / test_cntで補正値の平均ですよ.
        customer = scoutman_num * cabaclub_customer_up_total * cr_correction_total * randint(cabaclubstoremaster.customer_rand_min, cabaclubstoremaster.customer_rand_max) * eventbonus_customer_up / (100000000.0 * cast_num)
        # 集客数の上限.
        customer = min(math.ceil(customer), cabaclubstoremaster.customer_max * test_cnt)
        # 売上の計算.
        # (集客人数)*(設定されているキャスト属性売上補正の合計値/設定されているキャスト数)*(設定されているキャストの平均コスト)*(売上数補正、イベントが起きていない場合は1)*(乱数値0.8～1.2)
        proceeds = customer * cabaclub_proceeds_up_total * cost_total * eventbonus_proceeds_up * randint(cabaclubstoremaster.proceeds_rand_min, cabaclubstoremaster.proceeds_rand_max) / (1000000.0 * test_cnt * cast_num * cast_num)
        proceeds = math.ceil(proceeds)

        # スキル補正.
        cardlist_has_skill = BackendApi.filter_has_cabaclubskill(cardlist)
        total_powerup = BackendApi.calc_cabaclubskill_correction(cardlist_has_skill)

        # 総売上の計算.
        total_proceeds = math.ceil(proceeds * total_powerup)

        return int(customer), int(total_proceeds)
    
    @staticmethod
    def __tr_cabaclubstore_advance_the_time(model_mgr, uid, storeset, now):
        """キャバクラ店舗の時間をすすめる.
        """
        cabaclubstoremaster = storeset.master
        # 売上などの更新時間に直す関数.
        def to_utime(dt):
            seconds = int((dt - storeset.playerdata.utime).total_seconds())
            return storeset.playerdata.utime + datetime.timedelta(seconds=seconds - seconds % cabaclubstoremaster.customer_interval)
        def calc_customer_update_cnt(dt_from, dt_to):
            seconds = (to_utime(dt_to) - to_utime(dt_from)).total_seconds()
            return int(seconds / cabaclubstoremaster.customer_interval)
        # 実際にチェックする時間.
        utime_to = to_utime(now)
        # 発生するイベントを先に選択.
        eventidlist = []
        tmp_etime = storeset.playerdata.etime
        event_cnt = 0
        while tmp_etime <= now:
            eventid = storeset.select_event(model_mgr, tmp_etime)
            eventidlist.append(eventid)
            tmp_etime += datetime.timedelta(seconds=Defines.CABARETCLUB_STORE_EVENT_INTERVAL)
            event_cnt += 1
        if utime_to <= storeset.playerdata.utime and event_cnt == 0:
            # 何も更新されていない.
            return
        # イベントのマスターデータ.
        eventmaster_dict = BackendApi.get_cabaretclub_event_master_dict(model_mgr, [eid for eid in set(eventidlist) if eid])
        utime = storeset.playerdata.utime
        # イベントのカウンタ.
        event_counts = {}
        def event_count_up(event_id):
            if event_id:
                event_counts[event_id] = event_counts.get(event_id, 0) + 1
        # 補正値の集計用.
        eventbonusdata = dict(
            test_cnt = 0,
            customer_up = 0,
            proceeds_up = 0,
        )
        def push_upvalue(cnt):
            if cnt < 1:
                return
            eventbonusdata['customer_up'] += storeset.get_customer_up_by_event() * cnt
            eventbonusdata['proceeds_up'] += storeset.get_proceeds_up_by_event() * cnt
            eventbonusdata['test_cnt'] += cnt
        while utime < utime_to:
            current_event = storeset.eventmaster
            if current_event:
                # イベント終了時間.
                event_endtime = storeset.get_event_endtime()
                eventcheck_endtime = min(event_endtime, now)
                # イベント中の補正.
                cnt = calc_customer_update_cnt(utime, eventcheck_endtime)
                push_upvalue(cnt)
                if event_endtime <= now:
                    event_count_up(current_event.id)
                    storeset.set_event(None, storeset.playerdata.etime)
                utime = to_utime(eventcheck_endtime)
                # 次のイベントが発生する時間.
                block_num = int((current_event.seconds + Defines.CABARETCLUB_STORE_EVENT_INTERVAL - 1) / Defines.CABARETCLUB_STORE_EVENT_INTERVAL)
                etime_next = storeset.playerdata.etime + datetime.timedelta(seconds=block_num * Defines.CABARETCLUB_STORE_EVENT_INTERVAL)
                if 1 < block_num:
                    eventidlist = eventidlist[block_num-1:]
            else:
                etime_next = storeset.playerdata.etime + datetime.timedelta(seconds=Defines.CABARETCLUB_STORE_EVENT_INTERVAL)
            # 次のイベント発生までの補正.
            cnt = calc_customer_update_cnt(utime, min(etime_next, now))
            push_upvalue(cnt)
            if etime_next <= now:
                event_count_up(storeset.playerdata.event_id)
                # 次のイベントを設定.
                eventmaster = eventmaster_dict.get(eventidlist.pop(0) or 0)
                storeset.set_event(eventmaster, etime_next)
            utime = to_utime(etime_next)
        # 集客数と売上を計算.
        test_cnt = eventbonusdata['test_cnt']
        if 0 < test_cnt:
            customer, proceeds = BackendApi.calc_cabaretclub_customer_and_proceeds(model_mgr, uid, storeset, eventbonusdata['customer_up'], eventbonusdata['proceeds_up'], test_cnt, now)
            # 集客数と売上を加算.
            BackendApi.tr_add_cabaretclub_customer_and_proceeds(model_mgr, uid, cabaclubstoremaster, customer, proceeds, now)
        else:
            customer, proceeds = 0, 0
        # 売上の更新時間を設定.
        storeset.playerdata.utime = utime_to
        model_mgr.set_save(storeset.playerdata)
        # ログ.
        model_mgr.set_save(UserLogCabaClubStore.createLogAdvance(uid, cabaclubstoremaster.id, now, storeset.playerdata.event_id, customer, proceeds, event_counts))
    
    @staticmethod
    def tr_cabaclubstore_advance_the_time(model_mgr, uid, cabaclubstoremaster, now):
        """キャバクラ店舗の時間をすすめる.
        週の切り替えを含める.
        """
        # 店情報を取得.
        storeset = BackendApi.__get_cabaretclub_storeset_for_update(model_mgr, uid, cabaclubstoremaster, now, with_itemdata=True, with_eventmaster=True, do_check_alive=True, do_check_open=True)
        # 前回集計した時の1週間の開始時間.
        pre_start_time = BackendApi.to_cabaretclub_section_starttime(storeset.playerdata.utime)
        # 現在の1週間の開始時間.
        cur_start_time = BackendApi.to_cabaretclub_section_starttime(now)
        if 0 < (cur_start_time - pre_start_time).days:
            # 週をまたいでいるので週の開始時間までまず進める.
            dt = BackendApi.to_cabaretclub_section_endtime(storeset.playerdata.utime) - datetime.timedelta(microseconds=1)
            while dt < now:
                BackendApi.__tr_cabaclubstore_advance_the_time(model_mgr, uid, storeset, dt)
                dt += datetime.timedelta(days=7)
        BackendApi.__tr_cabaclubstore_advance_the_time(model_mgr, uid, storeset, now)
    
    @staticmethod
    def tr_cabaclubstore_advance_the_time_with_checkalive(model_mgr, uid, cabaclubstoremaster, now):
        """キャバクラ店舗の時間をすすめる.
        期限も確認する.
        """
        # 店情報を取得.
        storeset = BackendApi.__get_cabaretclub_storeset_for_update(model_mgr, uid, cabaclubstoremaster, now, with_itemdata=True, with_eventmaster=True, do_check_alive=False)
        if storeset and storeset.playerdata.is_open:
            if storeset.is_alive(now):
                BackendApi.tr_cabaclubstore_advance_the_time(model_mgr, uid, cabaclubstoremaster, now)
            else:
                # 期限切れなので閉じる.
                BackendApi.tr_cabaclubstore_close(model_mgr, uid, cabaclubstoremaster, now)
    
    @staticmethod
    def __tr_cabaclubstore_close(model_mgr, uid, storeset, now):
        """店を閉じる.
        """
        if not storeset.playerdata.is_open:
            return
        cabaclubstoremaster = storeset.master
        # 閉店時間まですすめる.
        time_to = min(storeset.get_limit_time() - datetime.timedelta(microseconds=1), now)
        # 更新の必要がある.
        BackendApi.tr_cabaclubstore_advance_the_time(model_mgr, uid, cabaclubstoremaster, time_to)
        # 閉店時間を記録.
        storeset.playerdata.octime = time_to
        # 閉店状態にする.
        storeset.playerdata.is_open = False
        model_mgr.set_save(storeset.playerdata)
    
    @staticmethod
    def tr_cabaclubstore_close(model_mgr, uid, cabaclubstoremaster, now):
        """店を閉じる.
        お店の期限が切れた時にも呼ぶべき.
        """
        # 店情報を取得.
        storeset = BackendApi.__get_cabaretclub_storeset_for_update(model_mgr, uid, cabaclubstoremaster, now, do_check_alive=False)
        if storeset is None or not storeset.playerdata.is_open:
            raise CabaretError(u'既に閉店しています', CabaretError.Code.ALREADY_RECEIVED)
        BackendApi.__tr_cabaclubstore_close(model_mgr, uid, storeset, now)
        # ログ.
        model_mgr.set_save(UserLogCabaClubStore.createLogClose(uid, cabaclubstoremaster.id, now))
    
    @staticmethod
    def tr_cabaclubstore_cancel(model_mgr, uid, cabaclubstoremaster, now):
        """店を解約する.
        """
        # 店情報を取得.
        storeset = BackendApi.__get_cabaretclub_storeset_for_update(model_mgr, uid, cabaclubstoremaster, now, do_check_alive=False)
        if storeset is None or not storeset.is_alive(now):
            raise CabaretError(u'既に解約しています', CabaretError.Code.ALREADY_RECEIVED)
        # まずは閉じる.
        BackendApi.__tr_cabaclubstore_close(model_mgr, uid, storeset, now)
        # 期限を現在時刻にする.
        storeset.playerdata.ltime = now
        model_mgr.set_save(storeset.playerdata)
        # キャストの配置を解除.
        castdata = CabaClubCastPlayerData.makeInstance(CabaClubCastPlayerData.makeID(uid, cabaclubstoremaster.id))
        castdata.cast = []
        model_mgr.set_save(castdata)
        # ログ.
        model_mgr.set_save(UserLogCabaClubStore.createLogClose(uid, cabaclubstoremaster.id, now))
    
    @staticmethod
    def tr_cabaclubstore_useraction(model_mgr, uid, cabaclubstoremaster, now):
        """店舗に対してユーザーがアクションする.
        """
        # 店情報を取得.
        storeset = BackendApi.__get_cabaretclub_storeset_for_update(model_mgr, uid, cabaclubstoremaster, now, with_eventmaster=True, do_check_alive=True)
        cabaclubstoremaster = storeset.master
        # 発生中のイベント.
        if storeset.eventmaster is None:
            raise CabaretError(u'発生しているイベントがありません', CabaretError.Code.NOT_DATA)
        elif storeset.get_event_endtime() <= now:
            raise CabaretError(u'イベント終了済み', CabaretError.Code.ILLEGAL_ARGS)
        elif storeset.eventmaster.ua_type == Defines.CabaClubEventUAType.NONE:
            raise CabaretError(u'ユーザーアクションのないイベントです', CabaretError.Code.ILLEGAL_ARGS)
        event_id = storeset.eventmaster.id
        # ここまでの売上等を一旦保存.
        if storeset.playerdata.is_open and cabaclubstoremaster.customer_interval <= (now - storeset.playerdata.utime).total_seconds():
            # 開店中の場合は現在まですすめる.
            BackendApi.tr_cabaclubstore_advance_the_time(model_mgr, uid, cabaclubstoremaster, now)
            if event_id != storeset.eventmaster.id:
                raise CabaretError(u'イベント終了済み', CabaretError.Code.ILLEGAL_ARGS)
        # 特別なマネーの消費.
        BackendApi.tr_add_cabaretclub_money(model_mgr, uid, -storeset.eventmaster.ua_cost)
        # ユーザアクション設定.
        if storeset.eventmaster.ua_type == Defines.CabaClubEventUAType.TAKE_MEASURES:
            # イベントを強制終了.
            storeset.set_event(None, storeset.playerdata.etime)
        else:
            # ユーザーアクションのフラグを立てる.
            storeset.playerdata.ua_flag = True
        model_mgr.set_save(storeset.playerdata)
        # ログ.
        model_mgr.set_save(UserLogCabaClubStore.createLogUA(uid, cabaclubstoremaster.id, now, event_id))
    
    @staticmethod
    def correct_duplication_cabaretclub_cast(cabaclubcastdata):
        """キャバクラ店舗のキャストの重複を修正する.
        """
        if len(cabaclubcastdata.cast) != len(set(cabaclubcastdata.cast)):
            arr = []
            for cast in cabaclubcastdata.cast:
                if cast in arr:
                    continue
                arr.append(cast)
            cabaclubcastdata.cast = arr
    
    @staticmethod
    def tr_cabaclubstore_change_cast(model_mgr, uid, cabaclubstoremaster, now, cardid_remove=None, cardid_add=None):
        """キャバクラ店舗にキャストを設定する.
        """
        if cardid_remove is None and cardid_add is None:
            raise CabaretError(u'キャストを指定していません', CabaretError.Code.ILLEGAL_ARGS)
        mid = cabaclubstoremaster.id
        # 店情報を取得.
        BackendApi.__get_cabaretclub_storeset_for_update(model_mgr, uid, cabaclubstoremaster, now, do_check_alive=True, do_check_close=True)
        if cardid_add:
            # 現在配置されているキャストを除外.
            BackendApi.check_cabaretclub_cast_include(model_mgr, uid, [cardid_add], [mid])
            # デッキ確認.
            BackendApi.check_deck_cast_include(model_mgr, uid, [cardid_add])
            # キャストの存在確認.
            castlist = BackendApi.get_cards([cardid_add], model_mgr)
            if len(castlist) != 1:
                raise CabaretError(u'存在しないキャストです', CabaretError.Code.ILLEGAL_ARGS)
        # 書き込み.
        def forUpdate(model, inserted):
            idx = None
            if cardid_remove:
                if cardid_remove not in model.cast:
                    raise CabaretError(u'配置されていないキャストです', CabaretError.Code.ILLEGAL_ARGS if cardid_add else CabaretError.Code.ALREADY_RECEIVED)
                idx = model.cast.index(cardid_remove)
            if cardid_add:
                if cardid_add in model.cast:
                    # 入れ替えの場合は引数がおかしい.追加の場合は既に実行済み.
                    raise CabaretError(u'既に配置されています', CabaretError.Code.ILLEGAL_ARGS if cardid_remove else CabaretError.Code.ALREADY_RECEIVED)
                elif idx is None:
                    # 新しく追加.
                    model.cast.append(cardid_add)
                    if cabaclubstoremaster.cast_num_max < len(model.cast):
                        raise CabaretError(u'配置できるキャスト数を超えています', CabaretError.Code.OVER_LIMIT)
                else:
                    # 入れ替え.
                    model.cast[idx] = cardid_add
            elif idx is not None:
                # 削除.
                model.cast.pop(idx)
            # 重複を修正する. ユーザーから見たら突然変わるのでここではやめておく.
            #BackendApi.correct_duplication_cabaretclub_cast(model)
        
        model_mgr.add_forupdate_task(CabaClubCastPlayerData, CabaClubCastPlayerData.makeID(uid, mid), forUpdate)
    
    @staticmethod
    def tr_cabaclubstore_set_cast(model_mgr, uid, cabaclubstoremaster, cardidlist, now):
        """キャバクラ店舗にキャストを設定する.
        """
        if cabaclubstoremaster.cast_num_max < len(cardidlist):
            raise CabaretError(u'配置できるキャスト数を超えています', CabaretError.Code.OVER_LIMIT)
        mid = cabaclubstoremaster.id
        # 店情報を取得.
        BackendApi.__get_cabaretclub_storeset_for_update(model_mgr, uid, cabaclubstoremaster, now, do_check_alive=True, do_check_close=True)
        # 現在配置されているキャストを除外.
        BackendApi.check_cabaretclub_cast_include(model_mgr, uid, cardidlist, [mid])
        # デッキ確認.
        BackendApi.check_deck_cast_include(model_mgr, uid, cardidlist)
        # キャストの存在確認.
        castlist = BackendApi.get_cards(cardidlist, model_mgr)
        if len(castlist) != len(cardidlist):
            raise CabaretError(u'存在しないキャストが含まれています', CabaretError.Code.ILLEGAL_ARGS)
        # 書き込み.
        def forUpdate(model, inserted):
            model.cast = cardidlist
        model_mgr.add_forupdate_task(CabaClubCastPlayerData, CabaClubCastPlayerData.makeID(uid, mid), forUpdate)
    
    @staticmethod
    def check_cabaretclub_cast_include(model_mgr, uid, cardidlist, ignore_store_midlist=None):
        """キャストIDリストに店舗配置中のキャストが含まれているかを確認.
        """
        ignore_store_midlist = ignore_store_midlist or []
        cur_castidlist = []
        # 店舗に配置されているキャスト.
        cur_castidlist_dict = BackendApi.get_cabaretclub_active_cast_dict(model_mgr, uid, OSAUtil.get_now())
        for mid, idlist in cur_castidlist_dict.items():
            if mid in ignore_store_midlist:
                continue
            cur_castidlist.extend(idlist)
        if set(cur_castidlist) & set(cardidlist):
            raise CabaretError(u"店舗に配置されているキャストが含まれています", CabaretError.Code.ILLEGAL_ARGS)
    
    @staticmethod
    def tr_cabaclub_add_scoutman(model_mgr, uid, cabaclubstoremaster, num, now):
        """スカウトマン増加.
        """
        # 店情報を取得.
        storeset = BackendApi.__get_cabaretclub_storeset_for_update(model_mgr, uid, cabaclubstoremaster, now, do_check_alive=True, do_check_close=True)
        # 加算後の人数.
        num_post = storeset.playerdata.scoutman_add + num
        # 最大値の確認.
        if cabaclubstoremaster.scoutman_add_max < num_post:
            raise CabaretError(u"スカウトマンの上限を超えます", CabaretError.Code.OVER_LIMIT)
        storeset.playerdata.scoutman_add = num_post
        model_mgr.set_save(storeset.playerdata)
    
    @staticmethod
    def tr_cabaclub_set_preferential(model_mgr, uid, itemmaster, now):
        """優待券配布アイテムを使用.
        """
        def forUpdate(model, inserted):
            if model.preferential_id == itemmaster.id and now < model.preferential_time:
                raise CabaretError(u"既に優待券配布中です", CabaretError.Code.OVER_LIMIT)
            model.preferential_id = itemmaster.id
            model.preferential_time = now + datetime.timedelta(seconds=3600*6)
        model_mgr.add_forupdate_task(CabaClubItemPlayerData, uid, forUpdate)
    
    @staticmethod
    def tr_cabaclub_set_barrier(model_mgr, uid, itemmaster, now):
        """バリアアイテムを使用.
        """
        def forUpdate(model, inserted):
            if model.barrier_id == itemmaster.id and now < model.barrier_time:
                raise CabaretError(u"既にバリアアイテム使用中です", CabaretError.Code.OVER_LIMIT)
            model.barrier_id = itemmaster.id
            model.barrier_time = now + datetime.timedelta(seconds=3600*6)
        model_mgr.add_forupdate_task(CabaClubItemPlayerData, uid, forUpdate)
        # イベントを全て終了させる為に時間を進める.
        cabaclubstoremaster_list = BackendApi.get_cabaretclub_store_master_all(model_mgr, using=settings.DB_READONLY)
        for cabaclubstoremaster in cabaclubstoremaster_list:
            # イベントを終了させる為に時間を進める.
            BackendApi.tr_cabaclubstore_advance_the_time_with_checkalive(model_mgr, uid, cabaclubstoremaster, now)
            # イベントを終了させる.
            storeset = BackendApi.__get_cabaretclub_storeset_for_update(model_mgr, uid, cabaclubstoremaster, now, do_check_alive=False)
            if storeset and storeset.playerdata.event_id:
                storeset.set_event(None, now)
                model_mgr.set_save(storeset.playerdata)
    
    @staticmethod
    def __filter_cabaretclubstore_sould_be_updated(model_mgr, uid, master_list, now):
        """更新が必要なマスターデータを絞り込む.
        """
        # マスターIDのリスト.
        mid_list = [master.id for master in master_list]
        # 店舗.開閉を見るだけだしスレーブでいいはず.
        store_dict = BackendApi.get_cabaretclub_storeplayerdata_dict(model_mgr, uid, mid_list, using=settings.DB_READONLY)
        # 更新が必要なマスターデータを絞り込む.期限切れでもis_openがTrueなら更新が必要.
        dest = []
        for master in master_list:
            playerdata = store_dict.get(master.id)
            if playerdata is None:
                # 借りたことがない.
                continue
            elif not playerdata.is_open:
                # 閉店中は必要なし.
                continue
            # イベント時間の確認.
            if Defines.CABARETCLUB_STORE_EVENT_INTERVAL < int((now - playerdata.etime).total_seconds()):
                # 更新が必要.
                pass
            # 更新時間の確認.
            elif master.customer_interval < int((now - playerdata.utime).total_seconds()):
                # 更新が必要.
                pass
            else:
                continue
            dest.append(master)
        return dest
    
    @staticmethod
    def __tr_update_cabaretclubstore(uid, cabaclubstoremaster_list, now):
        """店舗の更新書き込み
        """
        model_mgr = ModelRequestMgr()
        for cabaclubstoremaster in cabaclubstoremaster_list:
            BackendApi.tr_cabaclubstore_advance_the_time_with_checkalive(model_mgr, uid, cabaclubstoremaster, now)
        model_mgr.write_all()
        model_mgr.write_end()
        return model_mgr
    
    @staticmethod
    def update_cabaretclubstore(model_mgr, uid, now, master=None):
        """店舗の更新.
        """
        # マスターデータ取得.
        if master is None:
            master_list = BackendApi.get_cabaretclub_store_master_all(model_mgr, using=settings.DB_READONLY)
        else:
            master_list = [master]
        # 更新が必要な物だけ絞込.
        master_list = BackendApi.__filter_cabaretclubstore_sould_be_updated(model_mgr, uid, master_list, now)
        if not master_list:
            return
        # 更新書き込み.
        result_model_mgr = db_util.run_in_transaction(BackendApi.__tr_update_cabaretclubstore, uid, master_list, now)
        # 書き込んだモデルを取得済みモデルに設定しておく.
        for data in result_model_mgr.get_wrote_models().values():
            if data.get('db'):
                model_mgr.set_got_models([data['db']], using=settings.DB_READONLY)
    
    @staticmethod
    def put_cabaretclub_eventinfo(handler, uid, now, using=settings.DB_DEFAULT):
        """店舗イベント情報を埋め込む.
        """
        def get_obj():
            model_mgr = handler.getModelMgr()
            # 店舗情報.
            storeset_list = BackendApi.get_cabaretclub_storeset_dict_all(model_mgr, uid, using=using).values()
            storeset_list.sort(key=lambda x:x.playerdata.etime)
            # 店舗の閲覧時間.
            vtime_dict = CabaClubRecentlyViewedTime.fetch(uid)
            # 店舗のイベント確認.
            obj_cabaclubstoreevent = None
            for storeset in storeset_list:
                if storeset.get_event_endtime() <= now:
                    continue
                data = vtime_dict.get(storeset.master.id)
                if data and data.vtime < storeset.playerdata.etime:
                    # 未閲覧.
                    return Objects.cabaclubstoreevent(handler, storeset, now)
                elif obj_cabaclubstoreevent is None:
                    obj_cabaclubstoreevent = Objects.cabaclubstoreevent(handler, storeset, now)
            return obj_cabaclubstoreevent
        handler.html_param['cabaclubstoreevent'] = get_obj()
    
    @staticmethod
    def check_cabaclub_lead_resultanim(model_mgr, uid, now, using=settings.DB_DEFAULT):
        """キャバクラ経営の結果演出に誘導するべきかを判定.
        """
        scoreplayerdata_weekly = BackendApi.get_cabaretclub_scoreplayerdata_weekly(model_mgr, uid, now - datetime.timedelta(days=7), using)
        if scoreplayerdata_weekly is None or scoreplayerdata_weekly.view_result:
            return False
        return True

    @staticmethod
    def get_cabaclubrankeventmaster(model_mgr, mid, using=settings.DB_DEFAULT):
        """経営イベントマスターデータ取得."""
        return BackendApi.get_model(model_mgr, CabaClubRankEventMaster, mid, using=settings.DB_READONLY)

    @staticmethod
    def get_current_cabaclubrankeventconfig(model_mgr, using=settings.DB_DEFAULT):
        """現在開催中の経営イベント設定."""
        return BackendApi.__get_current_eventconfig(model_mgr, CurrentCabaClubRankEventConfig, using=using)

    @staticmethod
    def get_current_cabaclubrankeventmaster(model_mgr, using=settings.DB_DEFAULT, check_schedule=True, now=None):
        """現在開催中の経営イベント.
        """
        config = BackendApi.get_current_cabaclubrankeventconfig(model_mgr, using=using)
        if now == None:
            now = OSAUtil.get_now()
        if config.mid == 0:
            return None
        if check_schedule and not (config.starttime <= now < config.endtime):
            return None
        return BackendApi.get_cabaclubrankeventmaster(model_mgr, config.mid, using=settings.DB_READONLY)

    @staticmethod
    def update_cabaclubrankeventconfig(mid, starttime, endtime, next_starttime, next_endtime):
        """現在開催中の経営イベント設定を更新."""
        def tr():
            model_mgr = ModelRequestMgr()
            model = BackendApi.get_model(model_mgr, CurrentCabaClubRankEventConfig, CurrentCabaClubRankEventConfig.SINGLE_ID, get_instance=True)
            model.starttime = starttime
            model.endtime = endtime
            model.next_starttime = next_starttime
            model.next_endtime = next_endtime

            if model.mid != mid:
                model.prize_flag = 0
            model.mid = mid
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr, model

        model_mgr, model = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        return model

    # ======================================================================================================
    # プロデュースイベント.
    @staticmethod
    def get_produce_event_master(model_mgr, mid, using=settings.DB_DEFAULT):
        """プロデュースイベントマスターデータ習得
        """
        return BackendApi.get_model(model_mgr, ProduceEventMaster, mid, using=using)

    @staticmethod
    def get_current_produce_event_master(model_mgr, using=settings.DB_DEFAULT, check_schedule=True):
        """現在開催中のプロデュースイベント.
        """
        config = BackendApi.get_current_produce_event_config(model_mgr, using=using)
        if config.mid == 0:
            return None
        if check_schedule and not (config.starttime <= OSAUtil.get_now() < config.endtime):
            return None
        return BackendApi.get_produce_event_master(model_mgr, config.mid, using=settings.DB_READONLY)

    @staticmethod
    def get_current_produce_event_config(model_mgr, using=settings.DB_DEFAULT):
        """現在開催中のプロデュースイベント習得
        """
        return BackendApi.__get_current_eventconfig(model_mgr, CurrentProduceEventConfig, using=using)

    @staticmethod
    def update_produce_event_config(mid, starttime, endtime, bigtime, epilogue_endtime):
        """現在開催中のプロデュースイベント設定を変更
        """

        def tr():
            model_mgr = ModelRequestMgr()
            model = BackendApi.get_model(model_mgr, CurrentProduceEventConfig, CurrentProduceEventConfig.SINGLE_ID, get_instance=True)
            model.starttime = starttime
            model.endtime = endtime
            model.bigtime = bigtime
            model.epilogue_endtime = epilogue_endtime
            model.mid = mid
            
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr, model

        model_mgr, model = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        return model

    @staticmethod
    def get_produceevent_scorerecords(model_mgr, mid, uidlist, using=settings.DB_DEFAULT):
        """プロデュースイベントの得点レコード
        """
        idlist = [ProduceEventScore.makeID(uid, mid) for uid in uidlist]
        modellist = BackendApi.get_model_list(model_mgr, ProduceEventScore, idlist, using=using)
        dic = dict([(model.uid, model) for model in modellist])
        return dic

    @staticmethod
    def get_produceevent_scorerecord(model_mgr, mid, uid, using=settings.DB_DEFAULT):
        """プロデュースイベントの得点レコードを単体取得
        """
        return BackendApi.get_produceevent_scorerecords(model_mgr, mid, [uid], using=using).get(uid, None)

    @staticmethod
    def backup_produce_event_ranking_data_into_redis(eventid):
        """ランキングデータ復旧"""
        model_mgr = ModelRequestMgr()
        ranking_data = ProduceEventScore.fetchValues(using=settings.DB_READONLY, filters={'mid': eventid})

        if ranking_data:
            def writeEnd():
                redisdb = RedisModel.getDB()
                pipe = redisdb.pipeline()
                for rank in ranking_data:
                    ProduceEventRanking.create(rank.mid, rank.uid, rank.point).save(pipe)
                pipe.execute()
            model_mgr.add_write_end_method(writeEnd)
        model_mgr.write_all()
        model_mgr.write_end()

    @staticmethod
    def get_produceevent_score(mid, uid):
        """プロデュースイベントのスコアを取得.
        """
        return BackendApi.get_ranking_score(ProduceEventRanking, mid, uid)

    @staticmethod
    def get_produceevent_rankindex(mid, uid):
        """プロデュースイベントのランキング順位(index)を取得.
        """
        return BackendApi.get_ranking_rankindex(ProduceEventRanking, mid, uid)

    @staticmethod
    def fetch_uid_by_produceeventrank(mid, limit, offset=0, withrank=False):
        """プロデュースイベントのランキングを範囲取得.
        """
        return BackendApi.fetch_uid_by_rankingrank(ProduceEventRanking, mid, limit, offset, withrank)

    @staticmethod
    def get_produceevent_rankernum(mid):
        """プロデュースイベントのランキング人数を取得.
        """
        return BackendApi.get_ranking_rankernum(ProduceEventRanking, mid)

    @staticmethod
    def get_produceevent_stagemaster(model_mgr, stageid, using=settings.DB_DEFAULT):
        """ステージを取得.
        """
        return BackendApi.__get_event_stage(model_mgr, ProduceEventScoutStageMaster, stageid, using=using)

    @staticmethod
    def get_current_produceeventstage_master(model_mgr, eventmaster, eventplaydata, using=settings.DB_DEFAULT):
        """ステージを取得.
        """
        return BackendApi.__get_current_eventstage_master(model_mgr, eventmaster, eventplaydata, using=using)

    @staticmethod
    def get_produceevent_stagemaster_list(model_mgr, idlist, using=settings.DB_DEFAULT):
        """ステージを取得.
        """
        return BackendApi.__get_event_stagelist(model_mgr, ProduceEventScoutStageMaster, idlist, using=using)

    @staticmethod
    def get_produceeventstage_playdata(model_mgr, mid, uid, using=settings.DB_DEFAULT, reflesh=False):
        """レイドイベントスカウトデータ取得.
        """
        return BackendApi.__get_eventscout_playdata(model_mgr, ProduceEventScoutPlayData, uid, mid, using, reflesh)

    @staticmethod
    def get_produceevent_next_stagemaster(model_mgr, eventid, stagemaster, using=settings.DB_DEFAULT):
        """次のステージIDを取得.
        """
        return BackendApi.__get_event_nextstage(model_mgr, eventid, stagemaster, using=using)

    @staticmethod
    def tr_produceevent_stage_clear(model_mgr, eventmaster, player, stage):
        """スカウトステージクリア書き込み.
        """
        BackendApi.__tr_event_stage_clear(model_mgr, eventmaster, player, stage)

        # ログ.
        model_mgr.set_save(UserLogAreaComplete.create(player.id, stage.id, UserLogAreaComplete.EventScoutType.PRODUCE))

    @staticmethod
    def get_produceevent_raidmasters(model_mgr, eventid, midlist, using=settings.DB_DEFAULT):
        """レイドイベントのレイドマスターデータ.
        """
        idlist = [ProduceEventRaidMaster.makeID(eventid, mid) for mid in midlist]
        modellist = BackendApi.get_model_list(model_mgr, ProduceEventRaidMaster, idlist, get_instance=True, using=using)
        return dict([(model.mid, model) for model in modellist])

    @staticmethod
    def get_produceevent_raidmaster(model_mgr, eventid, mid, using=settings.DB_DEFAULT):
        """レイドイベントのレイドマスターデータ.
        """
        return BackendApi.get_model(model_mgr, ProduceEventRaidMaster, ProduceEventRaidMaster.makeID(eventid, mid), get_instance=True, using=using)

    @staticmethod
    def get_producehappenings(model_mgr, idlist, using=settings.DB_DEFAULT):
        """ハプニングプレイ情報を取得.
        """
        happenings = BackendApi.get_model_dict(model_mgr, ProduceEventHappening, idlist, using=using)
        midlist = list(set([happening.mid for happening in happenings.values()]))
        masters = BackendApi.get_happeningmasters(model_mgr, midlist, using=using)
        return dict(
            [(happening.id, HappeningSet(happening, masters.get(happening.mid))) for happening in happenings.values()])

    @staticmethod
    def get_producehappening(model_mgr, happeningid, using=settings.DB_DEFAULT):
        """ハプニングプレイ情報を取得.
        """
        return BackendApi.get_producehappenings(model_mgr, [happeningid], using=using).get(happeningid, None)

    @staticmethod
    def get_current_producehappeningid(model_mgr, uid, using=settings.DB_DEFAULT, reflesh=False):
        """現在のハプニングIDを取得.
        """
        if reflesh:
            playerhappening = PlayerHappening.getByKey(uid, using=using)
            if playerhappening:
                model_mgr.set_got_models([playerhappening])
        else:
            playerhappening = BackendApi.get_playerhappening(model_mgr, uid, using=using)
        if playerhappening is None:
            return 0
        return ProduceEventHappening.makeID(playerhappening.id, playerhappening.happening)

    @staticmethod
    def get_current_producehappening(model_mgr, uid, using=settings.DB_DEFAULT):
        """現在のハプニングを取得.
        """
        happeningid = BackendApi.get_current_producehappeningid(model_mgr, uid, using=using)
        if happeningid:
            return BackendApi.get_producehappening(model_mgr, happeningid, using=using)
        return None

    @staticmethod
    def get_producehappeningraidset_list(model_mgr, idlist, using=settings.DB_DEFAULT):
        """ハプニングプレイ情報を取得.
        レイドも一緒にとる.
        """
        happenings = BackendApi.get_producehappenings(model_mgr, idlist, using=using)
        raids = BackendApi.get_raids(model_mgr, happenings.keys(), using=using)
        result = [HappeningRaidSet(happenings[happeningid], raids.get(happeningid)) for happeningid in idlist
                  if happenings.get(happeningid)]
        return result

    @staticmethod
    def get_producehappeningraidset(model_mgr, happeningid, using=settings.DB_DEFAULT):
        """ハプニングプレイ情報を取得.
        レイドも一緒にとる.
        """
        happening = BackendApi.get_producehappening(model_mgr, happeningid, using=using)
        if happening is None:
            return None
        raid = BackendApi.get_raid(model_mgr, happening.id, using=using, happening_eventvalue=happening.happening.event)
        return HappeningRaidSet(happening, raid)
    
    @staticmethod
    def create_produce_cardinfo(handler, model_mgr, uid, eventmaster_id):
        player_education = BackendApi.get_player_education(model_mgr, uid, eventmaster_id, using=settings.DB_READONLY)
        produce_castmaster = player_education.get_produce_castmaster()
        card_master = produce_castmaster.get_card(model_mgr, using=settings.DB_READONLY)
        card_master_view = BackendApi.get_model(model_mgr, CardMasterView, card_master.id)
        return BackendApi.create_cardinfo(handler, card_master_view, player_education, produce_castmaster.max_education_level)
    
    @staticmethod
    def create_cardinfo(handler, card_master, player_education, max_education_level):
        return {
            'rare' : card_master.rare,
            'thumbUrl' : handler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(card_master)),
            'thumbnail' : {
                'small' : handler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlSmall(card_master)),
                'middle' : handler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(card_master)),
                'large' : handler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlLarge(card_master)),
                'bustup' : handler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlBustup(card_master)),
            },
            'level' : player_education.level,
            'max_level' : max_education_level,
            'heart' : player_education.heart,
        }
        
    @staticmethod
    def get_player_education(model_mgr, uid, eventmaster_id, using=settings.DB_DEFAULT):
        player_education = BackendApi.get_model(model_mgr, PlayerEducation, PlayerEducation.makeID(uid, eventmaster_id), using=using)
        if not player_education:
            player_education = PlayerEducation.make_instance(uid, eventmaster_id)
        return player_education

    @staticmethod
    def add_education_point(model_mgr, uid, eventmaster, is_perfect_win, result):
        produce_castmasters = eventmaster.get_produce_castmasters(using=settings.DB_READONLY)
        player_education = BackendApi.get_player_education(model_mgr, uid, eventmaster.id)

        produce_castmaster = player_education.get_produce_castmaster_for_array(produce_castmasters)
        educate_point = produce_castmaster.get_point(is_perfect_win)
        max_order = ProduceCastMaster.get_maxorder(produce_castmasters)
        result.before_heart = player_education.heart 
        result.before_level = player_education.level 
        heartup_num, _, result.order = player_education.add_point(educate_point, produce_castmaster.max_education_level, max_order)
        result.education_point = heartup_num
        result.after_level = player_education.level
        result.is_perfect_win = is_perfect_win
        model_mgr.set_save(player_education)
        
        for level in xrange(result.before_level+1, result.after_level+1):
            BackendApi.tr_send_achievement_producecast_level(model_mgr, uid, produce_castmaster, level, result);
        
        BackendApi.tr_send_achievement_producecast_order(model_mgr, uid, player_education, produce_castmasters, result)

    @staticmethod
    def tr_send_achievement_producecast_order(model_mgr, uid, player_education, produce_castmasters, result):
        def send_prize(send_cast_order):
            produce_castmaster = ProduceCastMaster.select_produce_cast_master(produce_castmasters, send_cast_order)
            prize = PrizeData.create(cardid=produce_castmaster.produce_cast, cardnum=1)
            BackendApi.tr_add_prize(model_mgr, uid, [prize], produce_castmaster.complete_prizetext, auto_receive=True)
        
        produce_castmaster = player_education.get_produce_castmaster_for_array(produce_castmasters)
        max_order = ProduceCastMaster.get_maxorder(produce_castmasters)
        ##もし最後のキャストなら
        if player_education.is_education_limit(produce_castmaster.max_education_level, max_order) and result.education_point > 0:
            send_prize(player_education.cast_order)
        else:
            for cast_order in xrange(player_education.cast_order - result.order, player_education.cast_order):
                send_prize(cast_order)

    @staticmethod
    def tr_send_achievement_producecast_level(model_mgr, uid, produce_castmaster, level, result):
        """ プロデュースキャストのレベル達成報酬配布 """
        prizeidlist = produce_castmaster.get_prizeidlist(level)
        prizemasterlist = model_mgr.get_models(PrizeMaster, prizeidlist)
        prizelist = []
        for prize in prizemasterlist:
            prizelist.append(PrizeData.createByMaster(prize))
        if prizelist:
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, produce_castmaster.lvprize_text, auto_receive=True)
            result.is_send_prize = True

    @staticmethod
    def tr_produceevent_raiddestroy(model_mgr, uid, raidboss, eventid, animdata, is_big, is_great_success):
        """プロデュースイベントレイド討伐成功.
        """
        if eventid == 0:
            # イベントレイドじゃない.
            return

        eventmaster = BackendApi.get_current_produce_event_master(model_mgr)
        if eventmaster is None or eventid != eventmaster.id:
            # イベントが発生していない.
            return

        # イベント用の設定を一応反映.
        eventvalue = HappeningUtil.make_produceeventvalue(eventid)
        BackendApi.reset_raidboss_eventraidmaster(model_mgr, raidboss, eventvalue)
        eventraidmaster = raidboss.produceeventraidmaster
        if eventraidmaster is None:
            # イベント用の設定がない.
            return
        
        is_perfect_win = BackendApi.choose_produceraid_result(eventraidmaster.perfect_probability, is_great_success)
        produce_happening_result = ProduceEventHappeningResult.get_instance(model_mgr, uid, eventid)
        
        BackendApi.add_education_point(model_mgr, uid, eventmaster, is_perfect_win, produce_happening_result)

        # イベントポイントの計算
        point = BackendApi.calc_produceevent_point(eventraidmaster, animdata.power, is_perfect_win)
        
        # プレーヤースコアを保存する
        BackendApi.tr_add_produceevent_score(model_mgr, eventmaster, raidboss, uid, point, is_big)
        produce_happening_result.event_point = point
        
        # 短冊配布.
        oid = raidboss.raid.oid
        for uid in raidboss.getDamageRecordUserIdList():
            record = raidboss.getDamageRecord(uid)
            if record.damage_cnt < 1:
                # 参加していない.
                continue

            flag = bool(BackendApi.judge_raidprize_distribution_outside_userid(uid, uid, oid, True))

        raidboss.refrectDamageRecord()
        model_mgr.set_save(raidboss.raid)
        model_mgr.set_save(produce_happening_result)

    @staticmethod
    def calc_produceevent_point(eventraidmaster, team_power, is_perfect_win):
        """プロデュースイベントポイントの計算
            獲得イベントポイント ＝ 基礎獲得値 ＋ 接客係数 × 全接客力
        """
        base_point = eventraidmaster.ptbase
        if is_perfect_win:
            win_coefficient = eventraidmaster.perfect_coefficient
        else:
            win_coefficient = eventraidmaster.good_coefficient

        return int(base_point + (win_coefficient / 10000.0) * team_power)

    @staticmethod
    def tr_add_produceevent_score(model_mgr, master, raidboss, uid, point, is_big):
        def send_point_prize(produce_event_master, before_point):
            point_min = before_point+1
            point_max = model.point
            table = produce_event_master.get_pointprizes(point_min, point_max)
            if table:
                keys = table.keys()
                keys.sort()
                
                prizeidlist = []
                for key in keys:
                    if point_min <= key <= point_max:
                        prizeidlist.extend(table[key])
                prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
                BackendApi.tr_add_prize(model_mgr, uid, prizelist, produce_event_master.pointprize_text, auto_receive=True)

        """レイドイベントのスコアを計算.
        """
        model = ProduceEventScore.get_instance(model_mgr, uid, master.id)
        point_before = model.point
        model.point += point
        if is_big:
            model.destroy_big += 1
        else:
            model.destroy += 1
        model_mgr.set_save(model)
        
        send_point_prize(master, point_before)

        def writeEnd():
            pipe = ProduceEventRanking.getDB().pipeline()
            ProduceEventRanking.create(master.id, uid, model.point).save(pipe)
            pipe.execute()

        model_mgr.add_write_end_method(writeEnd)

    @staticmethod
    def choose_produceraid_result(perfect_value, is_great_success=False):
        """合成結果を選ぶ.
           成功 or 大成功.
        """
        if is_great_success:
            return True
        else:
            rand = AppRandom()
            return rand.getIntN(100) <= perfect_value

    @staticmethod
    def choice_produceeventscout_happeningtable(model_mgr, eventmaster, uid=None, now=None, using=settings.DB_DEFAULT):
        """.
        """
        getter = lambda att: getattr(eventmaster, att)

        is_full = BackendApi.get_scoutsearch_flag(uid) if uid else None

        if BackendApi.check_produceevent_bigboss_opened(model_mgr, now=now, using=using):
            # 超太客出現データ
            if is_full:
                event_happenings = getter('raidtable_big_full')
            else:
                event_happenings = getter('raidtable_big')
        else:
            # 太客出現データ
            if is_full:
                event_happenings = getter('raidtable_full')
            else:
                event_happenings = getter('raidtable')
        return event_happenings

    @staticmethod
    def check_produceevent_bigboss_opened(model_mgr, now=None, using=settings.DB_DEFAULT):
        """大ボス出現チェック.
        """
        now = now or OSAUtil.get_now()
        config = BackendApi.get_current_produce_event_config(model_mgr, using=using)
        if config.bigtime and config.bigtime <= now:
            return True
        else:
            return False

    @staticmethod
    def check_produceevent_lead_opening(model_mgr, uid, eventid=None, using=settings.DB_DEFAULT):
        """オープニングの誘導チェック.
        """
        config = BackendApi.get_current_produce_event_config(model_mgr, using=settings.DB_READONLY)
        eventid = eventid or config.mid
        if config.mid == 0 or config.mid != eventid or not config.is_open_event(OSAUtil.get_now()):
            return False

        flagrecord = BackendApi.get_produceevent_flagrecord(model_mgr, eventid, uid, using=using)

        if flagrecord is None or not (config.starttime <= flagrecord.opvtime < config.endtime):
            return True
        else:
            return False

    @staticmethod
    def check_produceevent_lead_epilogue(model_mgr, uid, eventid=None, using=settings.DB_DEFAULT):
        """エピローグの誘導チェック.
        """
        config = BackendApi.get_current_produce_event_config(model_mgr, using=settings.DB_READONLY)
        eventid = eventid or config.mid
        now = OSAUtil.get_now()
        if config.mid == 0 or config.mid != eventid or not config.is_open_epilogue(now):
            return False

        flagrecord = BackendApi.get_produceevent_flagrecord(model_mgr, eventid, uid, using=using)
        if flagrecord and config.starttime <= flagrecord.opvtime and flagrecord.epvtime < flagrecord.opvtime:
            return True
        else:
            return False

    @staticmethod
    def update_produceevenflagrecord(mid, uid, opvtime=None, epvtime=None):
        """プロデュースイベントのフラグレコードを更新.
        """
        def tr():
            model_mgr = ModelRequestMgr()
            model = BackendApi.get_model(model_mgr, ProduceEventFlags, ProduceEventFlags.makeID(uid, mid), get_instance=True)
            model.opvtime = opvtime or model.opvtime
            model.epvtime = epvtime or model.epvtime
            
            if opvtime:
                # ミッション.
                mission_executer = PanelMissionConditionExecuter()
                mission_executer.addTargetViewEventOpening()
                BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
            
            model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr, model
        model_mgr, model = db_util.run_in_transaction(tr)
        model_mgr.write_end()
        return model

    @staticmethod
    def get_produceevent_flagrecords(model_mgr, mid, uidlist, using=settings.DB_DEFAULT):
        """プロデュースイベントのフラグレコード.
        """
        idlist = [ProduceEventFlags.makeID(uid, mid) for uid in uidlist]
        modellist = BackendApi.get_model_list(model_mgr, ProduceEventFlags, idlist, using=using)
        dic = dict([(model.uid, model) for model in modellist])
        return dic

    @staticmethod
    def get_produceevent_flagrecord(model_mgr, mid, uid, using=settings.DB_DEFAULT):
        """プロデュースイベントのフラグレコードを単体取得.
        """
        return BackendApi.get_produceevent_flagrecords(model_mgr, mid, [uid], using=using).get(uid, None)

    @staticmethod
    def tr_determine_produceevent_scoutcard(model_mgr, mid, uid, stageid, itemmaster, usenum=1, autosell_rarity=None):
        """スカウトカード獲得.
        """
        # スカウト情報を取得.
        playdata = ProduceEventScoutPlayData.getByKeyForUpdate(ProduceEventScoutPlayData.makeID(uid, mid))
        return BackendApi.__tr_determine_event_scoutcard(model_mgr, playdata, uid, itemmaster, usenum, autosell_rarity)

    #======================================================================================================
    # 称号.
    @staticmethod
    def get_title_master(model_mgr, mid, using=settings.DB_DEFAULT):
        """称号のマスターを取得.
        """
        return BackendApi.get_model(model_mgr, TitleMaster, mid, using=using)
    
    @staticmethod
    def get_title_master_all(model_mgr, using=settings.DB_DEFAULT):
        """全ての称号のマスターを取得.
        """
        return model_mgr.get_mastermodel_all(TitleMaster, order_by='-priority', using=using)
    
    @staticmethod
    def get_title_playerdata(model_mgr, uid, using=settings.DB_DEFAULT):
        """称号のプレイヤーデータを取得.
        """
        return BackendApi.get_model(model_mgr, TitlePlayerData, uid, get_instance=True, using=using)
    
    @staticmethod
    def get_current_title_set(model_mgr, uid, now, using=settings.DB_DEFAULT):
        """現在設定中の称号情報を取得.
        """
        # プレイヤーデータ取得.
        playerdata = BackendApi.get_title_playerdata(model_mgr, uid, using=using)
        if playerdata.title == 0:
            # 称号設定されていない.
            return None
        # マスターデータ取得.
        master = BackendApi.get_title_master(model_mgr, playerdata.title, using=settings.DB_READONLY)
        titleset = TitleSet(master, playerdata) if master else None
        if titleset and titleset.is_alive(now):
            return titleset
        else:
            return None
    
    @staticmethod
    def get_current_title_master(model_mgr, uid, now, using=settings.DB_DEFAULT):
        """現在設定中の称号を取得.
        """
        titleset = BackendApi.get_current_title_set(model_mgr, uid, now, using)
        return titleset.master if titleset else None
    
    @staticmethod
    def tr_title_get(model_mgr, uid, titlemaster, now):
        """称号獲得.
        """
        # 名誉ポイントを減らす.
        if 0 < titlemaster.cost:
            BackendApi.tr_add_cabaretclub_honor_point(model_mgr, uid, -titlemaster.cost)
        # 称号付与.
        def forUpdate(model, inserted):
            if not inserted:
                # 既に設定しているかを確認.
                if model.title == titlemaster.id and now < (model.stime + datetime.timedelta(days=titlemaster.days)):
                    raise CabaretError(u'設定済み', code=CabaretError.Code.ALREADY_RECEIVED)
            model.title = titlemaster.id
            model.stime = now
        model_mgr.add_forupdate_task(TitlePlayerData, uid, forUpdate)
    
    @staticmethod
    def reflect_title_effect_percent(model_mgr, effect_percent, uid, field, now, using=settings.DB_DEFAULT, cnt=1):
        """称号効果を反映.
        """
        cur_title_master = BackendApi.get_current_title_master(model_mgr, uid, now, using)
        if cur_title_master is None:
            return effect_percent
        if isinstance(field, (str, unicode)):
            attrname = field
        elif hasattr(field, 'name'):
            attrname = field.name
        else:
            raise CabaretError(u'フィールドの指定が不正です')
        return effect_percent + getattr(cur_title_master, attrname) * cnt

    @staticmethod
    def update_player_cross_promotion(model_mgr, uid, *target_fields):
        """PlayerCrossPromotionの内容を書き換える際に行う処理をまとめたもの
        例:BackendApi.update_player_cross_promotion(mgr, 7, "total_login_count","is_level10","is_level20","is_battle")
        """
        PlayerCrossPromotion.update_player_cross_promotion(model_mgr, uid, *target_fields)
