# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.util.player import ModelPlayer
from platinumegg.lib.platform.api.objects import People
from platinumegg.app.cabaret.models.Card import CardMaster, CardAcquisition
from platinumegg.app.cabaret.util.card import CardSet, CardUtil
from defines import Defines
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.playerlog import getPlayerLogCls,\
    getFriendLogCls
from platinumegg.app.cabaret.util.greetlog import GreetLogData
from platinumegg.app.cabaret.models.Scout import ScoutMaster
from platinumegg.app.cabaret.models.Area import AreaMaster
from platinumegg.app.cabaret.models.Happening import HappeningMaster, Happening,\
    Raid, RaidMaster, RaidLog
from platinumegg.app.cabaret.util.present import PrizeData, PresentSet
from platinumegg.app.cabaret.models.Boss import BossMaster
from platinumegg.app.cabaret.models.Memories import MemoriesMaster,\
    MoviePlayList, EventMovieMaster, EventMovieViewData
from platinumegg.app.cabaret.util.happening import HappeningRaidSet,\
    HappeningSet, RaidBoss
from platinumegg.app.cabaret.util.treasure import TreasureUtil
from platinumegg.app.cabaret.models.Trade import TradeMaster
from platinumegg.app.cabaret.util.rediscache import InfomationMasterIdListCache
from platinumegg.app.cabaret.models.Gacha import GachaMaster, GachaGroupMaster,\
    GachaPlayData, GachaPlayCount, RankingGachaMaster
from platinumegg.app.cabaret.util.gacha import GachaBox
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventMaster,\
    CurrentRaidEventConfig, RaidEventScore
import datetime
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventScore,\
    ScoutEventMaster, CurrentScoutEventConfig, ScoutEventPlayData,\
    ScoutEventStageMaster, ScoutEventPresentPrizeMaster,\
    ScoutEventTanzakuCastMaster, ScoutEventTanzakuCastData
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventMaster,\
    BattleEventRankMaster, BattleEventGroup, BattleEventScore
from copy import copy
from platinumegg.app.cabaret.util.item import ItemUtil
from platinumegg.app.cabaret.util.redisdb import PlayerConfigData
from platinumegg.app.cabaret.models.Mission import PanelMissionPanelMaster,\
    PanelMissionMissionMaster
from platinumegg.app.cabaret.models.raidevent.RaidCardMixer import RaidEventRecipeMaster,\
    RaidEventMaterialMaster
from platinumegg.app.cabaret.models.Skill import SkillMaster
from platinumegg.app.cabaret.models.Infomation import PopupMaster,\
    EventBannerMaster
from platinumegg.app.cabaret.util.popup import PopupBanner
from platinumegg.app.cabaret.util.apprandom import AppRandom
from platinumegg.app.cabaret.models.CabaretClub import CabaClubScorePlayerData,\
    CabaClubScorePlayerDataWeekly, CabaClubStoreMaster, CabaClubStorePlayerData,\
    CabaClubEventMaster
from platinumegg.app.cabaret.util.cabaclub_store import CabaclubStoreSet
from platinumegg.app.cabaret.models.Title import TitleMaster, TitlePlayerData
from collections import namedtuple

class Handler(AppHandler):
    """スマホ版のテンプレートを閲覧するだけ.
    """
    def checkUser(self):
        if not self.osa_util.is_dbg_user:
            raise CabaretError(u'認証エラー', CabaretError.Code.NOT_AUTH)
    
    TEST_OBJECTS = None
    
    def process(self):
        urlargs = self.getUrlArgs(u'/template_test/')
        
        # ポップアップ用.
        tmp = urlargs.get(0, None)
        if tmp == 'getpopup':
            self.json_result_param['popupbanner'] = self.makeDummyPopupBanner()
            self.writeAppJson()
            return
        
        if self.is_pc:
            TEMPLATE_FORMAT = '/template_test/pc/%s.html'
        else:
            TEMPLATE_FORMAT = '/template_test/sp/%s.html'
        
        if Handler.TEST_OBJECTS is None:
            slidebanners = BackendApi.get_topbanners(self, using=settings.DB_READONLY)
            obj_infomation = None
            if self.is_pc:
                infomations = BackendApi.get_infomation_all(self, using=settings.DB_READONLY)
            else:
                infomations, _ = BackendApi.get_infomations(self, 0, using=settings.DB_READONLY)
                if 0 < len(infomations):
                    obj_infomation = Objects.infomation(self, infomations[0])
                else:
                    obj_infomation = self.makeDummyInfomation()
                
            
            omake = self.makeDummyPrizeInfo()
            gachadata = {}
            gachaslidedata = {}
            gachatable = {
                ('free', False, 10, 200, 0, u'1日1回', Defines.GachaConsumeType.GACHAPT),
                ('pay', True, 1, 300, 100, u'初回', Defines.GachaConsumeType.GACHAPT),
                ('pay10', False, 10, 3000, 0, u'', Defines.GachaConsumeType.GACHAPT),
                ('pay5', False, 10, 1500, 0, u'', Defines.GachaConsumeType.GACHAPT),
                ('rareoverticket', False, 1, 1, 0, u'', Defines.GachaConsumeType.RAREOVERTICKET),
                ('memoriesticket', False, 1, 1, 0, u'', Defines.GachaConsumeType.MEMORIESTICKET),
                ('ticket', False, 1, 1, 0, u'', Defines.GachaConsumeType.TRYLUCKTICKET),
                ('ranking0', False, 10, 3000, 0, u'', Defines.GachaConsumeType.RANKING),
            }
            slidelist = [self.makeDummyGachaSlideData() for _ in xrange(3)]
            for args in gachatable:
                gachadata[args[0]] = self.makeDummyGachaData(*args)
                gachaslidedata[args[0]] = slidelist
            gachadata['pay10']['omake'] = omake
            for gtype in Defines.GachaConsumeType.PREMIUM_TYPES:
                name = 'gacha_dummy_%s' % gtype
                gachadata[name] = self.makeDummyGachaData(name, False, 1, 99999, 99999, u'初回', gtype)
                gachaslidedata[name] = slidelist
            
            rankingdata_dict = {}
            for gacha in gachadata.values():
                boxid = gacha['boxid']
                if gacha['consumetype'] != Defines.GachaConsumeType.RANKING and not rankingdata_dict.get(boxid):
                    continue
                rankingdata_dict[boxid] = self.makeDummyRankingGachaMaster(boxid)
            
            supinfo = {
                'rate_total' : 100,
                'weight_dict' : {Defines.Rarity.RARE:10,Defines.Rarity.HIGH_RARE:20,Defines.Rarity.SUPERRARE:30},
                'cardlist_dict' : {Defines.Rarity.SUPERRARE:{Defines.CharacterType.TYPE_001:[slidelist[0][0]] + [self.makeDummyCardMaster()]*10}},
                'cardnum' : 11,
                'is_box' : False,
                'unique_name' : 'pay',
                'stime' : OSAUtil.get_now(),
                'etime' : OSAUtil.get_now(),
            }
            
            resultdata = {
                'is_win' : True,
                'v_power' : 10000,
                'o_power' : 10000,
                'v_skills' : [],
                'o_skills' : [],
                'rankup' : True,
                'norma_comp' : True,
                'win' : 1,
                'goldkey' : True,
                'eventpoint' : 9999,
            }
            
            # テスト用に欲しいパラメータを並べていく.
            Handler.TEST_OBJECTS = {
                'flag_template_test' : True,
                'handler' : self,
                'UrlMaker' : UrlMaker,
                'key_except_card' : Defines.URLQUERY_CHECK_CARD,
                'key_except_gold' : Defines.URLQUERY_CHECK_GOLD,
                'url_topimage' : self.makeAppLinkUrlImg('00/id_00_01/top_main.png'),
                'url_enter' : self.makeAppLinkUrl(TEMPLATE_FORMAT % 'mypage'),
                'infomations' : [Objects.infomation(self, infomation) for infomation in infomations],
                'infomation' : obj_infomation,
                'slidebanners' : [Objects.topbanner(self, banner) for banner in slidebanners],
                'eventbanners' : [],
                'presentlist' : [self.makeDummyPresent()] * 5,
                'presentreceivedlist' : [self.makeDummyPresent()] * 10,
                'power_total' : 100000,
                'cost_total' : 9999,
                'max_rank' : 20,
                'opponent_change_restnum' : 5,
                'rankmaster' : self.makeDummyBattleRank(),
                'battleplayer' : self.makeDummyBattlePlayer(),
                'cardmaster' : self.makeDummyCardMaster(),
                'card_num' : 100,
                'cardnum' : 50,
                'cardlimit' : 100,
                'stocknum' : 99,
                'friend_num' : 10,
                'friendrequest_num' : 5,
                'free_gacha' : True,
                'present_num' : 2,
                'profilecomment' : u'プロフィールコメント',
                'friendlog_list' : [self.makeDummyFriendLog(logtype) for logtype in (Defines.FriendLogType.BOSS_WIN,Defines.FriendLogType.SCOUT_CLEAR,Defines.FriendLogType.EVENTBOSS_WIN,Defines.FriendLogType.EVENTSTAGE_CLEAR)],
                'friendaccept_num' : 1,
                'playerlog_list' : [self.makeDummyPlayerLog(logtype) for logtype in (Defines.PlayerLogType.BATTLE_WIN, Defines.PlayerLogType.BATTLE_RECEIVE_LOSE)],
                'greetlog_list' : [self.makeDummyGreetLog() for _ in xrange(2)],
                'player' : self.makeDummyPlayer(),
                'playerlist' : [self.makeDummyPlayer()]*5,
                'o_player' : self.makeDummyPlayer(),
                'person' : self.makeDummyPlayer()['person'],
                'ptype' : Defines.CharacterType.TYPE_001,
                'leader' : self.makeDummyCard(),
                'leaders' : dict.fromkeys(Defines.CharacterType.NAMES.keys(), self.makeDummyCard()['master']),
                'url_enters' : dict.fromkeys(Defines.CharacterType.NAMES.keys(), self.get_html_param('', 'sp/regist/yesno.html')),
                'members' : [self.makeDummyCard() for _ in xrange(Defines.MYPAGE_DECK_MEMBER_NUM)],
                'memberlist' : [self.makeDummyCard() for _ in xrange(Defines.MYPAGE_DECK_MEMBER_NUM)],
                'resultdata' : resultdata,
                'news_num' : 3,
                'friend_num' : 1,
                'friendnum' : 99,
                'friendnummax' : 99,
                'restnum' : 99,
                'is_friend' : False,
                'is_friendrequest_ok' : True,
                'url_friendrequest_receive' : self.makeAppLinkUrl(OSAUtil.addQuery(UrlMaker.friendlist(), Defines.URLQUERY_STATE, Defines.FriendState.RECEIVE)),
                'LevelGroup' : Defines.LevelGroup.NAMES.items(),
                'battlekos' : {},
                'complete_series_num' : 0,
                'did_send_friendrequest' : False,
                'receive_friendrequest' : False,
                'newbie_cardlist' : [self.makeDummyCard()] * 3,
                'rarelog' : [self.makeDummyRareLog()] * 2,
                'gold_pre' : 10000,
                'gold_post' : 10000,
                'gacha_pt_pre' : 0,
                'gacha_pt_post' : 10,
                'item_list' : [self.makeDummyItem()] * 3,
                'item' : self.makeDummyItem(),
                'shopitemlist' : [self.makeDummyShopItem()] * 5,
                'shopitem' : self.makeDummyShopItem(),
                'num_key' : Defines.URLQUERY_NUMBER,
                'buy_num' : 1,
                'gachadata' : gachadata,
                'gacha_name' : gachadata['free']['name'],
                'gachacardlistinfo' : supinfo,
                'gacharankingdata' : dict([(boxid, self.makeDummyRankingGachaData(boxid, obj_master)) for boxid, obj_master in rankingdata_dict.items()]),
                'rankinggacha' : rankingdata_dict.values()[0],
                'current_tab' : u'template_test',
                'cardlist' : [self.makeDummyCard()] * 3,
                'cardmasterlist' : [self.makeDummyCardMaster()] * 3,
                'card' : self.makeDummyCard(),
                'levelupcardlist' : [self.makeDummyCard()] * 10,
                'logs' : [self.makeDummyGachaNews()] * 2,
                'overlimit' : False,
                'before_num' : 1,
                'cur_page' : 1,
                'page_max' : 1,
                'url_self' : '',
                'ctype' : Defines.CharacterType.TYPE_001,
                'rare' : Defines.Rarity.NORMAL,
                'sortby' : Defines.CardSortType.COST_REV,
                'flag_include_rare' : True,
                'flag_include_hkincr_already' : True,
                'sellprice' : 1000,
                Defines.URLQUERY_GOLD : 100,
                Defines.URLQUERY_GOLDADD : 100,
                Defines.URLQUERY_GOLDPRE : 100,
                Defines.URLQUERY_CARD_NUM : 1,
                'cost' : 10,
                'capacity' : 10,
                'url_addmember' : 'test',
                'url_auto' : '',
                'selected_card' : self.makeDummyCard(),
                'current_card' : self.makeDummyCard(),
                'basecard' : self.makeDummyCard(),
                'basecard_pre' : self.makeDummyCard(),
                'basecard_post' : self.makeDummyCard(),
                'materialcard' : self.makeDummyCard(),
                'area' : self.makeDummyAreaData(),
                'arealist' : [self.makeDummyAreaData()] * Defines.SCOUTAREAMAP_CONTENTNUM_PER_PAGE,
                'area_scout_dict' : {self.makeDummyAreaData()['id']:self.makeDummyScoutData()},
                'scout' : self.makeDummyScoutData(),
                'scoutlist' : [self.makeDummyScoutData()] * 5,
                'overlimit_card' : Defines.TreasureType.NAMES.keys(),
                'overlimit_treasure' : Defines.TreasureType.NAMES.keys(),
                'levelup_info' : self.makeDummyLevelupInfo(),
                'happening' : self.makeDummyHappeningData(),
                'happeninginfo' : {
                    'info' : 'bossappeared',
                    'timelimit' : Objects.timelimit(OSAUtil.get_now()),
                    'url' : '',
                },
                'raidhelplist' : [self.makeDummyRaidData()] * Defines.RAIDHELP_LIST_MAXLENGTH,
                'raidloglist' : [self.makeDummyRaidLogData()] * Defines.RAIDLOG_CONTENT_NUM_PER_PAGE,
                'deck_edit_target' : 'normal',
    #            'friend_call_opentime' : Objects.timelimit(OSAUtil.get_now()),
                'damagerecordlist' : [self.makeDummyRaidDamageRecord()] * 5,
                'boss': self.makeDummyBossData(),
                'prize' : self.makeDummyPrizeInfo(),
                'earlybonus' : self.makeDummyPrizeInfo(),
                'next_area' : self.makeDummyAreaData(),
                'list_column' : int(Defines.ALBUM_COLUMN_CONTENT_NUM),
                'list_line' : int(Defines.ALBUM_PAGE_CONTENT_NUM / Defines.ALBUM_COLUMN_CONTENT_NUM + 1),
                'cur_topic' : Defines.PresentTopic.ALL,
                'album_list' : [self.makeDummyListAlbum()] * (Defines.ALBUM_PAGE_CONTENT_NUM - 1),
                'album' : self.makeDummyMemoriy(),
                'memories_list' : [self.makeDummyMemoriy()] * 4,
                'movie_list' : [self.makeDummyMemoriy()],
                'voice_list' : [self.makeDummyMemoriy()],
                'treasurekey' : Objects.key(self, self.makeDummyPlayer(obj=False)),
                'treasure_name' : Defines.TreasureType.NAMES.get(Defines.TreasureType.GOLD),
                'treasure_type' : Defines.TreasureType.GOLD,
                'treasure_nums' : dict.fromkeys(Defines.TreasureType.NAMES.keys(), 99),
                'treasurelist' : [self.makeDummyTreasure(Defines.TreasureType.GOLD)] * 5,
                'treasure_item_list' : [self.makeDummyTreasureItem()] * 5,
                'treasure_view' : Objects.treasure_view(self, Defines.TreasureType.GOLD),
                'is_openable' : True,
                'treasure_get_data' : self.makeDummyTreasureItem(),
                'treasure_get_data_list' : [self.makeDummyTreasureItem()] * 10,
                'gacha_ticket_cost' : Defines.GACHA_TICKET_COST_NUM,
                'url_gacha_pt' : '',
                'url_payment' : '',
                'url_tryluck_ticket' : '',
                'thumbnaillist' : [self.makeAppLinkUrlImg('common/move_size.png')] * 3,
                'before_cabaretking' : 999,
                'before_demiworld' : 999,
                'item_num' : 10,
                'tradelist' : [self.makeDummyTradeData()] * 5,
                'tradedata' : self.makeDummyTradeData(),
                'trade_num' : 99,
                'trade_point' : 99999999,
                'raidevent' : self.makeDummyRaidEvent(),
                'url_raidevent_prizereceive' : 'test',
                'raideventscore' : self.makeDummyRaidEventScore(),
                'specialcardinfo' : self.makeDummySpecialCardInfo(),
                'specialcardlist' : self.makeDummySpecialCardList(),
                'destroypoint_info' : self.makeDummyDestroyPointInfo(),
                'destroyprizelist' : [self.makeDummyDestroyPrizeInfo() for _ in xrange(5)],
                'pointprizelist' : [self.makeDummyDestroyPrizeInfo() for _ in xrange(5)],
                'rankingprizelist' : [self.makeDummyRankingPrizeInfo() for _ in xrange(5)],
                'add_num' : 1,
                'damage' : 1000000,
                'specialcard_powup' : '+100000',
                'skilllist' : self.makeDummySkillInfoList(),
                'skillmasterlist' : [self.makeDummySkillMaster()] * 30,
                'profile_tag' : u'<a>テスト</a>',
                'scoutevent' : self.makeDummyScoutEvent(),
                'scouteventdata' : self.makeDummyScoutEventData(),
                'scouteventfever' : self.makeDummyScoutEventFever(),
                'scouteventstage' : self.makeDummyScoutEventStage(),
                'battleevent' : self.makeDummyBattleEvent(),
                'battleevent_rank' : self.makeDummyBattleEventRank(),
                'battleevent_score' : self.makeDummyBattleEventScore(),
                'battleevent_rank_number' : 1,
                'battleevent_rank_select' : [self.makeDummyBattleEventRankSelectObj()]*4,
                'rankmaster_list' : [{'rank':1, 'name':u'キャバ王', 'myrank':False}]*5,
                'battleloglist' : [self.makeDummyBattleEventBattleLog(is_win, is_attack) for is_win in (True, False) for is_attack in (True, False)],
                'battleevent_rank_list' : [self.makeDummyBattleEventRank()] * 10,
                'text_comment' : u'コメント',
                'invitecnt' : 9999,
                'gacha_type_counts' : dict([(consumetype, 1) for consumetype in Defines.GachaConsumeType.PAYMENT_TYPES]),
                'gacha_premium_priority' : Defines.GachaConsumeType.PREMIUM_TYPES,
                'gacha_ticket_nums' : dict([(tt, 1) for tt in Defines.GachaConsumeType.GachaTicketType.NAMES.keys()]),
                'scoutresultinfo' : self.makeDummyScoutResultInfo(),
                'promotioninfo' : self.makeDummyPromotionInfo(),
                'promotioninfo_data' : self.makeDummyPromotionInfo()['auto_receive'],
                'longloginbonus' : self.makeDummyLongLoginBonus(),
                'longloginbonus_daydata' : self.makeDummyLongLoginBonusDayData(),
                'longloginbonus_daydata_next' : self.makeDummyLongLoginBonusDayData(),
                'scoutresultinfo' : {'exp_add' : 999,'gold_add' : 9999,},
                'stage' : self.makeDummyScoutEventStage(),
                'eventscore' : self.makeDummyScoutEventScoreGetInfo(),
                'cur_sort' : 'desc',
                'url_desc' : 'hoge',
                'url_asc' : 'hoge',
                'event_gacha_stime' : OSAUtil.get_now(),
                'event_gacha_etime' : OSAUtil.get_now(),
                'gachaslidedata' : gachaslidedata,
                'happening_backinfo' : {'url':'', 'type':'scoutevent'},
                'eventmovielist' : [self.makeDummyEventMovie(True)]*5 + [self.makeDummyEventMovie(False)],
                'eventmovie' : self.makeDummyEventMovie(True),
                'scoutevent_present_selectobj' : [self.makeDummyScoutEventPresentPrizeMasterSelectObj() for _ in xrange(3)],
                'scoutevent_present_number' : 0,
                'scoutevent_presentprizelist' : [self.makeDummyScoutEventPresentPrizeMaster() for _ in xrange(3)],
                'scoutevent_heartnum' : 99999999,
                'playerconfigdata' : self.makeDummyPlayerConfigData(),
                'panelmission' : self.makeDummyPanelMission(),
                'recipelist' : [self.makeDummyRaidEventRecipe() for _ in xrange(5)],
                'recipe' : self.makeDummyRaidEventRecipe(),
                'raidevent_materials' : dict([(i, self.makeDummyRaidEventMaterial()) for i in xrange(Defines.RAIDEVENT_MATERIAL_KIND_MAX)]),
                'tabname_to_consumetype' : {},
                'gacha_consumetype_names' : Defines.GachaConsumeType.NAMES,
                'popupbanner_list' : [self.makeDummyPopupBanner()['url_flag'] for _ in xrange(2)],
                'scoutevent_tanzaku_list' : [self.makeDummyScoutEventTanzakuData(i) for i in xrange(5)],
                'scoutevent_tanzaku' : self.makeDummyScoutEventTanzakuData(0),
                'scouteventscore' : self.makeDummyScoutEventScore(),
                'tanzaku_num_add' : 1000000000,
                'tanzaku_num_pre' : 1000000000,
                'tanzaku_num_post' : 1000000000,
                'tanzaku_num' : 1000000000,
                'tip_usenums' : ItemUtil.makeUseNumListByList(10000),
                'tip_add' : 0xffffffff,
                'scoutevent_tanzaku_rankingdata' : self.makeDummyScoutEventTanzakuRankingData(),
                'piece_dropiteminfo' : self.makeDummyPieceDropitemInfo(),
                'store_castidlist' : [],
                'cabaclub_management_info' : self.makeDummyCabaclubManagementInfo(),
                'cabaclubstoreeventmaster' : self.makeDummyCabaClubStoreEventMaster(),
                'cabaclubstoreevent' : self.makeDummyCabaClubStoreEvent(),
                'cabaclubstoremaster' : self.makeDummyCabaClubStoreMaster(),
                'cabaclubstore' : self.makeDummyCabaClubStore(),
                'cabaclubitemdata' : self.makeDummyCabaClubItemData(),
                'days' : 3,
                'titlemaster_list' : [self.makeDummyTitleMaster() for _ in xrange(5)],
                'title' : self.makeDummyTitlePlayerData(),
                'section_timelimit' : Objects.timelimit(OSAUtil.get_now()+datetime.timedelta(seconds=86399)),
                'groups' : namedtuple('TabEventBanners', 'show hidden')([self.makeDummyEventBanner() for _ in xrange(3)], [self.makeDummyEventBanner() for _ in xrange(4)]),
            }
        self.html_param['getRandN'] = lambda num: AppRandom().getIntN(num)
        self.html_param['getRandS'] = lambda vmin, vmax: AppRandom().getIntS(vmin, vmax)
        self.html_param.update(Handler.TEST_OBJECTS)
        
        self.html_param['url_contents'] = self.makeAppLinkUrl('/template_test/pc/mypage.html')
        
        tmp = urlargs.get(0, None)
        if tmp and tmp != 'http:':
            template_path = '/'.join(urlargs.args)
        else:
            if self.is_pc:
                template_path = 'pc/top/top.html'
            else:
                template_path = 'sp/top/top.html'
        self.osa_util.write_html(template_path, self.html_param)
    
    def get_html_param(self, key, key_test=None, obj=None):
        htmlname = key_test or key
        url = u'/template_test/%s' % htmlname
        return self.makeAppLinkUrl(url)
    
    def __getCabaClubStoreMaster(self):
        """キャバクラ店舗マスターデータ.
        """
        master = CabaClubStoreMaster()
        master.name = u'お店の名前はここ'
        master.thumb = u'cb_system/cb_system_rental_branch_01.png'
        master.days_0 = 3
        master.cost_0 = 100
        master.days_1 = 5
        master.cost_1 = 150
        master.days_2 = 7
        master.cost_2 = 240
        master.days_3 = 10
        master.cost_3 = 260
        master.days_4 = 30
        master.cost_4 = 500
        master.customer_interval = 900
        master.customer_max = 999
        master.cast_num_max = 99
        master.scoutman_num_max = 99
        master.scoutman_add_max = 99
        return master
    
    def __getCabaClubEventMaster(self):
        """キャバクラ店舗イベントマスター.
        """
        master = CabaClubEventMaster()
        master.name = u'店舗イベントの名前'
        master.thumb = u'cb_system/cb_system_event_happen_icon.png'
        master.text = u'店舗イベントの効果説明はここ'
        master.seconds = 1800
        master.customer_up = 120
        master.proceeds_up = 100
        master.ua_type = Defines.CabaClubEventUAType.LIVEN_UP
        master.ua_value = 200
        master.ua_cost = Defines.VALUE_MAX
        master.ua_text = u'ユーザアクションの効果説明はここ'
        return master
    
    def __getCabaClubStorePlayerData(self, event_id=0):
        """キャバクラ店舗プレイヤー情報.
        """
        playerdata = CabaClubStorePlayerData.makeInstance(0)
        playerdata.ltime = OSAUtil.get_datetime_max()
        playerdata.etime = OSAUtil.get_now()
        playerdata.event_id = event_id
        playerdata.scoutman_add = 99
        playerdata.is_open = True
        playerdata.ua_flag = False
        playerdata.proceeds = Defines.VALUE_MAX_BIG
        playerdata.customer = Defines.VALUE_MAX_BIG
        return playerdata
    
    def __getTitleMaster(self):
        titlemaster = TitleMaster.makeInstance(0)
        titlemaster.name = u'称号の名前はここ'
        titlemaster.text = u'称号の説明はここ'
        titlemaster.thumb = u'cb_system/title/cb_system_title_thum_01'
        titlemaster.days = 99
        titlemaster.cost = Defines.VALUE_MAX
        titlemaster.gold_up = 10
        titlemaster.exp_up = 20
        titlemaster.raidevent_point_up = 100
        titlemaster.raidevent_power_up = 200
        titlemaster.raidevent_treasure_up = 300
        titlemaster.scoutevent_point_up = 400
        titlemaster.battleevent_point_up = 500
        titlemaster.battleevent_power_up = 600
        return titlemaster
    
    def makeDummyTitleMaster(self):
        titlemaster = self.__getTitleMaster()
        return Objects.titlemaster(self, titlemaster)
    
    def makeDummyTitlePlayerData(self):
        titlemaster = self.__getTitleMaster()
        titlemaster.id = 999
        playerdata = TitlePlayerData.makeInstance(0)
        playerdata.title = titlemaster.id
        playerdata.stime = OSAUtil.get_now()
        return Objects.title(self, titlemaster, playerdata)
    
    def makeDummyCabaClubStoreMaster(self):
        """キャバクラ店舗マスター情報.
        """
        master = self.__getCabaClubStoreMaster()
        return Objects.cabaclubstoremaster(self, master)
    
    def makeDummyCabaClubStore(self):
        """キャバクラ店舗情報.
        """
        master = self.__getCabaClubStoreMaster()
        eventmaster = self.__getCabaClubEventMaster()
        playerdata = self.__getCabaClubStorePlayerData(eventmaster.id)
        return Objects.cabaclubstore(self, CabaclubStoreSet(master, playerdata, None, eventmaster), OSAUtil.get_now())
    
    def makeDummyCabaClubItemData(self):
        """キャバクラ店舗アイテム情報.
        """
        obj = dict(master=self.makeDummyItem()['master'], limittime=OSAUtil.get_datetime_max(), timelimit=Objects.timelimit(OSAUtil.get_now() + datetime.timedelta(seconds=86399), OSAUtil.get_now()))
        return dict.fromkeys(['preferential', 'barrier'], obj)
    
    def makeDummyCabaClubStoreEventMaster(self):
        """キャバクラ店舗イベントマスター.
        """
        eventmaster = self.__getCabaClubEventMaster()
        return Objects.cabaclubstoreeventmaster(self, eventmaster)
    
    def makeDummyCabaClubStoreEvent(self):
        """キャバクラ店舗イベント情報.
        """
        master = self.__getCabaClubStoreMaster()
        eventmaster = self.__getCabaClubEventMaster()
        playerdata = self.__getCabaClubStorePlayerData(eventmaster.id)
        return Objects.cabaclubstoreevent(self, CabaclubStoreSet(master, playerdata, None, eventmaster), OSAUtil.get_now())
    
    def makeDummyCabaclubManagementInfo(self):
        """キャバクラ経営情報.
        """
        scoredata = CabaClubScorePlayerData()
        scoredata.money = Defines.VALUE_MAX
        scoredata.point = Defines.VALUE_MAX
        scoredata_weekly = CabaClubScorePlayerDataWeekly()
        scoredata_weekly.proceeds = Defines.VALUE_MAX_BIG
        scoredata_weekly.customer = Defines.VALUE_MAX_BIG
        return Objects.cabaclub_management_info(self, scoredata, scoredata_weekly)
    
    def makeDummyPieceDropitemInfo(self):
        """ピースコンプ後のアイテムドロップ情報.
        """
        return {
            'cardmaster' : self.makeDummyCardMaster(),
            'prize' : self.makeDummyPrizeInfo(),
        }
    
    def makeDummyScoutEventTanzakuRankingData(self):
        """スカウトイベントの業績の最終結果.
        """
        return dict([(number, dict(rank=number+1, tip=0xffffffffffffffff)) for number in xrange(3)])
    
    def makeDummyScoutEventScore(self):
        """スカウトイベントのスコア情報.
        """
        scorerecord = ScoutEventScore.makeInstance(0)
        scorerecord.tip = 0xffffffff
        return Objects.scoutevent_score(scorerecord, 100, 10000)
    
    def makeDummyScoutEventTanzakuData(self, number):
        """短冊.
        """
        tanzakumaster = ScoutEventTanzakuCastMaster.makeInstance(number)
        tanzakumaster.tanzaku = 100
        tanzakumaster.tip_rate = 1
        tanzakumaster.tip_quota = 0xffffffff
        tanzakudata = ScoutEventTanzakuCastData.makeInstance(0)
        tanzakudata.set_tanzaku(number, 0xffffffff)
        tanzakudata.set_tip(number, 0xffffffff)
        return Objects.scoutevent_tanzaku(self, tanzakumaster, tanzakudata)
    
    def makeDummyPopupBanner(self):
        """ポップアップ.
        """
        popup = PopupMaster.makeInstance(1)
        
        popup.title = u'ポップアップのタイトル'
        popup.imageurl = 'event/raidevent/rdev_10/rdev_10_top.png'
        popup.bannerflag = True
        
        obj_popupbanner = Objects.popup(self, PopupBanner(popup, None))
        obj_popupbanner['banner'] = self.makeDummyEventBanner()
        obj_popupbanner['url_flag'] = self.makeAppLinkUrl('/template_test/getpopup/')
        
        return obj_popupbanner
    
    def makeDummyRaidEventRecipe(self):
        """レイドイベントのレシピ.
        """
        model_mgr = self.getModelMgr()
        recipemaster = RaidEventRecipeMaster.makeInstance(0)
        recipemaster.name = u'交換アイテム名'
        recipemaster.thumb = ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD)
        recipemaster.itype = Defines.ItemType.CARD
        recipemaster.itemid = CardMaster.max_value('id')
        recipemaster.itemnum = 1
        recipemaster.stock = 9999
        recipemaster.materialnum0 = 9999
        recipemaster.materialnum1 = 9999
        recipemaster.materialnum2 = 9999
        presentlist = BackendApi.create_present(model_mgr, 0, 0, recipemaster.itype, recipemaster.itemid, recipemaster.itemnum, do_set_save=False)
        presentset = PresentSet.presentToPresentSet(model_mgr, presentlist)[0]
        return Objects.raidevent_recipe(self, recipemaster, presentset)
    
    def makeDummyRaidEventMaterial(self):
        """レイドイベントの素材アイテム.
        """
        materialmaster = RaidEventMaterialMaster.makeInstance(0)
        materialmaster.name = u'交換素材名'
        materialmaster.thumb = ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD)
        return Objects.raidevent_material(self, materialmaster, Defines.VALUE_MAX)
    
    def makeDummyPanelMission(self):
        """パネルミッション情報.
        """
        # ミッション.
        obj_mission_list = []
        for number in xrange(1, Defines.PANELMISSION_MISSIN_NUM_PER_PANEL+1):
            mission = PanelMissionMissionMaster.makeInstance(0)
            mission.name = u'ミッション名:%s' % number
            mission.number = number
            mission.image_pre = 'card/abeno_miku/H1/Card_thumb_320_314.png'
            mission.image_post = 'card/aida_minami/H1/Card_thumb_320_314.png'
            mission.condition_text = u'ミッションの説明テキスト:%s' % number
            
            prizeinfo = self.makeDummyPrizeInfo()
            
            condition = 4
            value = number % (condition+1)
            obj_mission_list.append(Objects.panelmission_mission(self, mission, value, condition, prizeinfo, value == condition and value == number))
        
        # パネル.
        panelmaster = PanelMissionPanelMaster.makeInstance(0)
        panelmaster.name = u'パネル名'
        
        panelmaster.image = 'card/abeno_miku/H1/Card_thumb_320_314.png'
        panelmaster.header = 'banner/event/scevent/scev_09/scev_09_header.png'
        panelmaster.rule = 'event/scevent/scev_09/scev_09_rule.png'
        
        prizeinfo = self.makeDummyPrizeInfo()
        
        return Objects.panelmission(self, panelmaster, obj_mission_list, prizeinfo, is_cleared=True)
    
    def makeDummyPlayerConfigData(self):
        """プレイヤーのコンフィグ情報.
        """
        data = {
            'autosell' : Defines.Rarity.NORMAL,
        }
        return Objects.playerconfigdata(PlayerConfigData.create(1, data), True)
    
    def makeDummyScoutEventPresentPrizeMasterSelectObj(self):
        """プルダウン用スカウトイベントプレゼント項目.
        """
        ins = ScoutEventPresentPrizeMaster.makeInstance(1)
        ins.name = u'項目名'
        return Objects.scoutevent_present_selectobj(self, ins)
    
    def makeDummyScoutEventPresentPrizeMaster(self):
        """プルダウン用スカウトイベントプレゼント項目.
        """
        ins = ScoutEventPresentPrizeMaster.makeInstance(1)
        ins.name = u'項目名'
        return Objects.scoutevent_present(self, ins, 0, 100, self.makeDummyPrizeInfo())
    
    def makeDummyGachaSlideData(self):
        """ガチャスライド情報.
        """
        cardmaster = self.makeDummyCardMaster(True)
        return (cardmaster, self.makeAppLinkUrlImg('gacha/slide/hame_388_300.png'), u'復刻！！')
    
    def makeDummyLongLoginBonus(self):
        """ロングログイン.
        """
        obj = Objects.longloginbonus({'stime':OSAUtil.get_datetime_min(),'etime':OSAUtil.get_datetime_max()}, 99)
        obj['is_open'] = True
        return obj
    
    def makeDummyLongLoginBonusDayData(self):
        """ロングログイン日別データ.
        """
        itemlist = [
            u'アイテム000000001x99',
            u'アイテム000000002x99',
            u'アイテム000000003x99',
        ]
        obj = Objects.longloginbonus_daydata(3, itemlist, 1)
        obj['is_open'] = True
        return obj
    
    def makeDummyScoutResultInfo(self):
        resultlist = [{'apcost': 1, 'progress_pre': 0, 'exp_pre': 143, 'exp_add': 1, 'level': 15, 'ap_max': 24, 'ap_post':13, 'gold_add': 4, 'point_add': 14, 'exp_post': 144, 'progress': 1, 'execution': 6, 'ap_pre': 14}, {'apcost':1, 'progress_pre': 1, 'exp_pre': 144, 'exp_add': 1, 'level': 15, 'ap_max': 24, 'ap_post': 12, 'gold_add':4, 'point_add': 15, 'exp_post': 145, 'progress': 2, 'execution': 6, 'ap_pre': 13}]
        return BackendApi.make_scoutresult_info(resultlist)
    
    def makeDummyPromotionInfo(self, ):
        """プロモーション情報.
        """
        def make(status):
            return {
                'requirement' : u'ここは相手側で設定された達成条件テキスト',
                'prizelist' : [{
                    'id' : 1,
                    'name' : 'ここは報酬アイテム名',
                    'thumbUrl' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD)),
                    'thumbUrlMiddle' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlMiddleByType(Defines.ItemType.GOLD)),
                    'numtext' : u'x99',
                }],
                'status' : status,
            }
        return {
            'auto_receive' : make(Defines.PromotionStatus.ACHIEVED),
            'list' : [make(status) for status in Defines.PromotionStatus.NAMES.keys()],
        }
    
    def makeDummyBattleEventBattleLog(self, is_win=True, is_attack=True):
        """バトルイベントバトル履歴.
        """
        player = self.makeDummyPlayer(obj=False)
        leader = self.makeDummyCard(obj=False)
        return Objects.battleevent_battlelog(self, 1, player, None, leader, is_win, is_attack, 999999, OSAUtil.get_now())
    
    def makeDummyBattleEvent(self):
        """バトルイベント.
        """
        model_mgr = self.getModelMgr()
        master = BattleEventMaster()
        master.id = 99999
        master.name = u'ダミーイベント'
        master.specialtype = Defines.CharacterType.ALL
        master.htmlname = 'btev_07'
        master.img_appeal = [
            'event/scevent/scev_09/scev_09_reward_ranking_ssr.png',
            'event/scevent/scev_09/scev_09_reward_ranking_sr.png',
            'event/scevent/scev_09/scev_09_reward_area.png',
            'event/scevent/scev_09/scev_09_reward_item.png',
        ]
        
        now = OSAUtil.get_now()
        tomorrow = now + datetime.timedelta(seconds=86399)
        
        config = BackendApi.get_current_battleeventconfig(model_mgr)
        obj_event = Objects.battleevent(self, master, max(config.starttime, min(config.endtime, OSAUtil.get_now())))
        obj_event['timelimit_end'] = Objects.timelimit(tomorrow, now)
        obj_event['timelimit_start'] = Objects.timelimit(tomorrow, now)
        obj_event['is_opened'] = True
        obj_event['is_battle_opened'] = True
        
        return obj_event
    
    def makeDummyBattleEventRankSelectObj(self):
        """バトルイベントランク選択情報.
        """
        rankmaster = BattleEventRankMaster()
        rankmaster.rank = 1
        rankmaster.name = u'ランク名'
        rankmaster.cardid = CardMaster.getValues().id
        return Objects.battleevent_rank_selectobj(self, rankmaster)
    
    def makeDummyBattleEventRank(self):
        """バトルイベントランク情報.
        """
        rankmaster = BattleEventRankMaster()
        rankmaster.name = u'ランク名'
        rankmaster.thumb = 'area/Area01.png'
        rankmaster.bpcost = 100
        rankmaster.pointtable = []
        rankmaster.rankuptable = []
        
        grouprecord = BattleEventGroup()
        grouprecord.cdate = datetime.date.today()
        
        grouprankingdata = {
            'rank' : 99,
            'playerlist' : [self.makeDummyPlayer()] * 10,
        }
        obj_rank = Objects.battleevent_rank(self, None, rankmaster, grouprecord, grouprankingdata)
        obj_rank['rankuptext'] = u'1ランクDOWN'
        return obj_rank
    
    def makeDummyBattleEventScore(self):
        """バトルイベントスコア情報.
        """
        scorerecord = BattleEventScore()
        scorerecord.point = 99999999
        scorerecord.point_total = 99999999999
        scorerecord.win = 99999
        scorerecord.winmax = 9999999
        return Objects.battleevent_score(self, scorerecord, rank=999999)
    
    def makeDummyScoutEventScoreGetInfo(self):
        """獲得携帯電話番号.
        """
        scorerecord = ScoutEventScore.makeInstance(0)
        scorerecord.point_total = 999999
        return Objects.scoutevent_score(scorerecord, 999, 888)
    
    def makeDummyScoutEventStage(self):
        """スカウトイベントのステージデータ.
        """
        player = self.makeDummyPlayer(obj=False)
        stagemaster = ScoutEventStageMaster.getValues()
        stagemaster.bustup = [
            'event/scevent/scev_07/boss/shibuya_arisu.png',
            'event/scevent/scev_07/boss/shibuya_arisu.png',
            'event/scevent/scev_07/boss/aoki_rin.png',
            'event/scevent/scev_07/boss/yamakawa_seira.png',
            'event/scevent/scev_07/boss/sunohara_miki.png',
            'event/scevent/scev_07/boss/matsumoto_mei.png',
            'event/scevent/scev_07/boss/amami_tsubasa.png',
            'event/scevent/scev_07/boss/mizutani_kokone.png',
            'event/scevent/scev_07/boss/kasumi_kaho.png',
        ]
        stagemaster.bustuprate_0 = 0
        stagemaster.bustuprate_1 = 0
        stagemaster.bustuprate_2 = 100
        obj = Objects.scoutevent(self, player, stagemaster.id, stagemaster, 0, 'hogehoge')
        return obj
    
    def makeDummyScoutEventFever(self):
        """スカウトイベントフィーバー情報.
        """
        eventplaydata = ScoutEventPlayData.makeInstance(0)
        eventplaydata.feveretime = OSAUtil.get_now() + datetime.timedelta(seconds=86399)
        eventplaydata.lovetime_etime = eventplaydata.feveretime
        eventplaydata.star = 4
        return Objects.scoutevent_fever(eventplaydata)
    
    def makeDummyScoutEvent(self):
        """スカウトイベント本体.
        """
        config = CurrentScoutEventConfig.makeInstance(0)
        eventmaster = ScoutEventMaster.makeInstance(1)
        eventmaster.name = u'スカウトイベント名'
        eventmaster.htmlname = 'scev_09'
        eventmaster.img_appeal = [
            'event/scevent/scev_09/scev_09_reward_ranking_ssr.png',
            'event/scevent/scev_09/scev_09_reward_ranking_sr.png',
            'event/scevent/scev_09/scev_09_reward_area.png',
            'event/scevent/scev_09/scev_09_reward_item.png',
        ]
        eventmaster.img_produce = 'card/hatsune_minori/H1/Card_thumb_320_400.png'
        
        eventmaster.lovetime_star = 7
        eventmaster.lovetime_timelimit = 3600
        eventmaster.lovetime_tanzakuup = 100
        eventmaster.tanzaku_name = u'短冊'
        eventmaster.lovetime_starname = u'星'
        eventmaster.lovetime_pointname = u'チップ'
        
        config.mid = eventmaster.id
        config.starttime = OSAUtil.get_datetime_min()
        config.endtime = OSAUtil.get_datetime_max()
        return Objects.scouteventmaster(self, eventmaster, config)
    
    def makeDummyScoutEventData(self):
        """スカウトイベントのイベントデータ欄のパラメータ.
        """
        scorerecord = ScoutEventScore.makeInstance(0)
        return Objects.scoutevent_data(scorerecord, 999, 999, 99999)
    
    def makeDummyRankingPrizeInfo(self):
        """討伐ポイント.
        """
        return {
            'rank_min' : 99999,
            'rank_max' : 999999,
            'prizeinfo' : self.makeDummyPrizeInfo(),
        }
    
    def makeDummyDestroyPrizeInfo(self):
        """討伐ポイント.
        """
        return {
            'point' : 99999999,
            'destroy' : 99999999,
            'received' : True,
            'prizeinfo' : self.makeDummyPrizeInfo(),
        }
    
    def makeDummyDestroyPointInfo(self):
        """討伐ポイント.
        """
        points = {
            'owner' : 10000,
            'help' : 20000,
            'mvp' : 30000,
            'total' : 60000
        }
        return points
    
    def makeDummySpecialCardInfo(self):
        """特攻カード.
        """
        model_mgr = self.getModelMgr()
        midlist = [model.id for model in model_mgr.get_mastermodel_all(CardMaster)[:4]]
        return {
            'cardlist' : [{'deck':False,'master':Objects.cardmaster(self, cardmaster),'hasnum':1} for cardmaster in BackendApi.get_cardmasters(midlist, model_mgr).values()],
            'need_edit' : True,
        }
    
    def makeDummySpecialCardList(self):
        """特攻カード.
        """
        model_mgr = self.getModelMgr()
        midlist = [model.id for model in model_mgr.get_mastermodel_all(CardMaster)[:4]]
        arr = []
        for cardmaster in BackendApi.get_cardmasters(midlist, model_mgr).values():
            obj = Objects.cardmaster(self, cardmaster)
            obj['specialpowup'] = 10
            arr.append(obj)
        return arr
    
    def makeDummyRaidEvent(self, timebonus=True):
        """レイドイベント.
        """
        master = RaidEventMaster.makeInstance(1)
        master.name = u'レイドイベント１２３４５６７８'
        master.htmlname = 'rdev_16'
        master.img_appeal = [
            'event/scevent/scev_09/scev_09_reward_ranking_ssr.png',
            'event/scevent/scev_09/scev_09_reward_ranking_sr.png',
            'event/scevent/scev_09/scev_09_reward_area.png',
            'event/scevent/scev_09/scev_09_reward_item.png',
        ]
        
        config = CurrentRaidEventConfig.makeInstance(0)
        config.mid = master.id
        config.starttime = OSAUtil.get_now()
        config.endtime = config.starttime + datetime.timedelta(days=1)
        if timebonus:
            config.timebonus_time = [{
                'stime' : OSAUtil.get_now(),
                'etime' : OSAUtil.get_now() + datetime.timedelta(seconds=1440),
            }]
        return Objects.raidevent(self, master, config)
    
    def makeDummyRaidEventScore(self):
        """レイドイベントのスコア.
        """
        master = RaidEventMaster.makeInstance(1)
        master.name = u'レイドイベント１２３４５６７８'
        scorerecord = RaidEventScore.makeInstance(1)
        scorerecord.destroy = 99999
        scorerecord.destroy_big = 99999
        scorerecord.point = 99999999
        scorerecord.point_total = 9999999999
        return Objects.raidevent_score(master, scorerecord, 1000000)
    
    def makeDummyInfomation(self):
        """インフォメーション.
        """
        
        infomation = InfomationMasterIdListCache()
        infomation.id = 1
        infomation.title = u'タイトル'
        infomation.body = u'本文'
        infomation.stime = OSAUtil.get_now()
        infomation.etime = OSAUtil.get_now()
        return Objects.infomation(self, infomation)
    
    def makeDummyEventBanner(self):
        """イベントバナー.
        """
        banner = EventBannerMaster.makeInstance(0)
        banner.jumpto = '/gacha/'
        banner.imageurl = 'banner/gacha/NewYear_Chargegacha_banner00.png'
        banner.comment = u'バナー下コメント'
        return Objects.eventbanner(self, banner)
    
    def makeDummyBattleRank(self):
        """バトルのランク.
        """
        model_mgr = self.getModelMgr()
        master = BackendApi.get_battlerank(model_mgr, 1)
        return Objects.battlerank(self, master)
    
    def makeDummyBattlePlayer(self):
        """バトルのランク.
        """
        model_mgr = self.getModelMgr()
        player = self.makeDummyPlayer(obj=False)
        battleplayer = BackendApi.get_battleplayer(model_mgr, player.id, get_instance=True)
        master = BackendApi.get_battlerank(model_mgr, 1)
        return Objects.battleplayer(self, battleplayer, master)
    
    def makeDummyMemoriy(self):
        """思い出アルバム.
        """
        memoriesmaster = MemoriesMaster()
        memoriesmaster.id = 1
        memoriesmaster.name = u'ダミーの思い出'
        memoriesmaster.text = u'テキストテキストテキストテキストテキストテキストテキストテキスト'
        memoriesmaster.thumb = '00/id_00_02/main_photo.png'
        card_acquisition = CardAcquisition()
        return Objects.memoriesmaster(self, memoriesmaster, card_acquisition)
    
    def makeDummyListAlbum(self):
        """一覧用アルバム.
        """
        card = self.makeDummyCard(False)
        return Objects.listalbum(self, card.master, is_open=True)
    
    def makeDummyPrizeInfo(self):
        """報酬.
        """
        cardid = CardMaster.getValues().id
        prize = PrizeData.create(100, 10, Defines.ItemEffect.ACTION_ALL_RECOVERY, 2, cardid, 1, 5, 1, 1)
        return BackendApi.make_prizeinfo(self, [prize])
    
    def makeDummyLevelupInfo(self):
        """レベルアップ情報.
        """
        player = self.makeDummyPlayer(obj=False)
        player.level = 2
        return BackendApi.make_playerlevelup_info(self.getModelMgr(), player)
    
    def makeDummyHappeningData(self):
        """ハプニング.
        """
        master = HappeningMaster.getValues()
        raidmaster = RaidMaster.getByKey(master.boss)
        happening = Happening.makeInstance(1)
        raid = Raid.makeInstance(happening.id)
        raid.mid = raidmaster.id
        happeningraidset = HappeningRaidSet(HappeningSet(happening, master), RaidBoss(raid, raidmaster))
        prizeinfo = BackendApi.make_prizeinfo(self, [PrizeData.create(100)])
        obj_happening = Objects.happening(self, happeningraidset, prizeinfo)
        obj_happening['raid'] = self.makeDummyRaidData()
        return obj_happening
    
    def makeDummyRaidData(self):
        """レイド.
        """
        master = HappeningMaster.getValues()
        raidmaster = copy(RaidMaster.getByKey(master.boss))
        raidmaster.ctype = Defines.CharacterType.TYPE_001
        happening = Happening.makeInstance(1)
        raid = Raid.makeInstance(happening.id)
        raid.mid = raidmaster.id
        obj_raid = Objects.raid(self, RaidBoss(raid, raidmaster))
        obj_raid['timelimit'] = Objects.timelimit(OSAUtil.get_now() + datetime.timedelta(seconds=86399))
        obj_raid['fever'] = {
            'timelimit' : Objects.timelimit(OSAUtil.get_now() + datetime.timedelta(seconds=3599))
        }
        obj_raid['combobonus'] = {
            'cnt' : 99,
            'powup' : 999,
            'powup_next' : 999,
            'timelimit' : Objects.timelimit(OSAUtil.get_now() + datetime.timedelta(seconds=3599)),
        }
        return obj_raid
    
    def makeDummyRaidLogData(self):
        """レイド履歴.
        """
        player = self.makeDummyPlayer(obj=False)
        cardset = self.makeDummyCard(obj=False)
        friend = self.makeDummyPlayer(obj=False)
        friend.id = player.id + 1
        
        master = HappeningMaster.getValues()
        raidmaster = RaidMaster.getByKey(master.boss)
        happening = Happening.makeInstance(1)
        raid = Raid.makeInstance(happening.id)
        raid.mid = raidmaster.id
        raid.oid = player.id
        raid.hp = 0
        raidboss = RaidBoss(raid, raidmaster)
        raidboss.addDamageRecord(player.id, 1)
        raidboss.addDamageRecord(friend.id, 1)
        
        raidlog = RaidLog()
        raidlog.id = 1
        raidlog.uid = player.id
        raidlog.raidid = raid.id
        
        return Objects.raidlog(self, raidlog, raidboss, dict([(player.id, player), (friend.id, friend)]), {}, dict([(player.id, cardset)]))
    
    def makeDummyRaidDamageRecord(self):
        """レイドのダメージ履歴.
        """
        player = self.makeDummyPlayer(obj=False)
        person = People.makeNotFound()
        leader = self.makeDummyCard(obj=False)
        damage = 9999
        attack_cnt = 99
        return Objects.raid_damage_record(self, player, person, leader, damage, attack_cnt, damage)
    
    def makeDummyAreaData(self):
        """エリア.
        """
        areamaster = AreaMaster.getValues()
        return Objects.area(self, areamaster, None)
    
    def makeDummyBossData(self):
        """ボス.
        """
        master = BossMaster.getValues()
        master.hp = 1000
        return Objects.boss(self, master)
    
    def makeDummyScoutData(self, area=None):
        """スカウト.
        """
        dropitems = [{
            'thumbUrl' : self.makeAppLinkUrlImg(u'common/item.png'),
            'drop' : True,
        }] * 3
        player = self.makeDummyPlayer(obj=False)
        if area:
            scoutmaster = ScoutMaster.getValues(filters={'area':area})
        else:
            scoutmaster = ScoutMaster.getValues()
        obj_scout = Objects.scout(self, player, scoutmaster, 0, dropitems, scoutkey='hogehoge')
        obj_scout['areaname'] = u'エリア名'
        return obj_scout
    
    def makeDummyRankingGachaMaster(self, boxid=0):
        """ランキングガチャ.
        """
        master = RankingGachaMaster.makeInstance(boxid)
        master.name = u'ランキング名'
        master.img_rule = u'banner/gacha/rank_01/ranking_gacha01_setumei.png'
        master.img_appeal = ["gacha/ranking/rank_01/ranking_gacha01_hr.png", "gacha/ranking/rank_01/ranking_gacha01_sr.png", "gacha/ranking/rank_01/ranking_gacha01_ssr.png"]
        return Objects.rankinggacha(self, master, wholepoint=1234567890)
    
    def makeDummyRankingGachaData(self, boxid, obj_master):
        """ランキングガチャ情報.
        """
        return {
            'single':{
                'data':[self.makeDummyPlayer()]*3
            },
            'total':{
                'data':[self.makeDummyPlayer()]*3
            },
            'master':obj_master,
            'wholeprizelist' : [{'point':9999999,'received':i%2==0,'prizeinfo':self.makeDummyPrizeInfo()} for i in xrange(5)],
            'wholewinprizeinfo' : self.makeDummyPrizeInfo(),
        }
    
    def makeDummyGachaData(self, name, is_first, continuity, price, price_first, firsttype, consumetype):
        """ガチャ.
        """
        model_mgr = self.getModelMgr()
        mid = GachaMaster.getValues().id
        master = BackendApi.get_gachamaster(model_mgr, mid)
        
        grouplist = []
        
        groupmaster = GachaGroupMaster.makeInstance(0)
        groupmaster.name = u'DummyGroup'
        card = self.makeDummyCard()
        
        grouplist.extend([Objects.boxGroup(self, groupmaster, 99, 99, card=card) for _ in xrange(3)])
        grouplist.extend([Objects.boxGroup(self, groupmaster, 99, 99, card=None) for _ in xrange(3)])
        
        player = self.makeDummyPlayer(obj=False)
        
        playdata = GachaPlayData.makeInstance(GachaPlayData.makeID(player.id, master.boxid))
        playcount = GachaPlayCount.makeInstance(GachaPlayCount.makeID(player.id, master.boxid))
        gachabox = GachaBox(master, playdata)
        
        data = Objects.gacha(self, master, player, playcount, gachabox, grouplist)
        
        data.update({
            'unique_name':name,
            'is_first' : is_first,
            'first_stock' : 1,
            'continuity' : continuity,
            'price' : price,
            'continuity_first' : 1,
            'price_first' : price_first,
            'url_do' : self.makeAppLinkUrl(UrlMaker.gachado(0, 'Dummy')),
            'url_supinfo' : self.makeAppLinkUrl(UrlMaker.gachasupinfo(0)),
            'url_supcard' : self.makeAppLinkUrl(UrlMaker.gachasupcard(0)),
            'firsttype_text' : firsttype,
            'price_once' : price,
            'step' : 1,
            'stepmax' : 4,
            'lap' : 2,
            'lapdaymax' : 3,
            'timelimitstep' : {'hours': 11, 'seconds': 22, 'minutes': 33},
            'timelimitlap' : {'hours': 44, 'seconds': 55, 'minutes': 00},
            'consumetype' : consumetype,
            'tabengname' : u'template_test',
        })
        return data
    
    def makeDummyGachaCardListInfo(self):
        """ガチャ出現カード一覧.
        """
        model_mgr = self.getModelMgr()
        gachamaster = BackendApi.get_gachamaster(model_mgr, GachaMaster.getValues().id)
        playdata = GachaPlayData.makeInstance(GachaPlayData.makeID(0, gachamaster.boxid))
        return BackendApi.make_gachabox_rateinfo(model_mgr, gachamaster, playdata)
    
    def makeDummyShopItem(self):
        """商品のダミー.
        """
        data = {
            'id' : 0,
            'name' : u'Dummy商品',
            'text' : u'商品説明テキスト商品説明テキスト商品説明テキスト商品説明テキスト商品説明テキスト',
            'thumbUrl' : self.makeAppLinkUrlImg(u'common/item.png'),
            'price' : 105,
            'stock' : 0,
            'url_buy' : self.makeAppLinkUrl(UrlMaker.shopdo(0)),
            'num' : 1,
            'url_use' : self.makeAppLinkUrl(UrlMaker.item_use(Defines.ItemEffect.ACTION_ALL_RECOVERY, 1)),
            'unit' : u'個',
            'consumetype' : Defines.ShopConsumeType.PAYMENT,
        }
        return data

    
    def makeDummyItem(self, effect=Defines.ItemEffect.ACTION_ALL_RECOVERY):
        """アイテムのダミー.
        """
        master = BackendApi.get_itemmaster(self.getModelMgr(), effect)
        return Objects.item(self, master, 1)
    
    def makeDummyGachaNews(self):
        """ガチャ速報のダミー.
        """
        return {
            'player' : self.makeDummyPlayer(),
            'card' : self.makeDummyCard()['master'],
            'time' : OSAUtil.get_now().strftime(u"%Y/%m/%d"),
        }
        mid = CardMaster.getValues().id
        master = BackendApi.get_cardmasters([mid], self.getModelMgr()).get(mid)
        return Objects.rarelog(self, master, OSAUtil.get_now())
    
    def makeDummyRareLog(self):
        """レアキャバ嬢獲得履歴のダミー.
        """
        mid = CardMaster.getValues().id
        master = BackendApi.get_cardmasters([mid], self.getModelMgr()).get(mid)
        return Objects.rarelog(self, master, OSAUtil.get_now())
    
    def makeDummyPresent(self):
        """ダミーのプレゼント.
        """
        model_mgr = self.getModelMgr()
        presentlist = BackendApi.create_present(model_mgr, 0, 0, Defines.ItemType.GOLD, 0, 100, do_set_save=False)
        presentset = PresentSet.presentToPresentSet(model_mgr, presentlist)[0]
        return Objects.present(self, presentset)
    
    def makeDummyPlayerLog(self, logtype=Defines.PlayerLogType.BATTLE_WIN):
        """ダミーの行動履歴.
        """
        logclass = getPlayerLogCls(logtype)
        ins = logclass()
        ins.logtype = logtype
        ins.params = {
            'area' : 'スカウトエリアA',
            'username' : 'DummyUser',
            'dmmid':'****',
            'url' : '',
        }
        return Objects.gamelog(ins)
    
    def makeDummyFriendLog(self, logtype=Defines.FriendLogType.BOSS_WIN):
        """ダミーの仲間の近況.
        """
        logclass = getFriendLogCls(logtype)
        ins = logclass()
        ins.logtype = logtype
        ins.params = {
            'area' : 'スカウトエリアA',
            'scout' : 'スカウトA',
            'username' : 'DummyUser',
            'dmmid':'****',
            'url' : '',
        }
        return Objects.gamelog(ins)
    
    def makeDummyGreetLog(self):
        """ダミーのあいさつ履歴.
        """
        ins = GreetLogData()
        mid = CardMaster.getValues().id
        master = BackendApi.get_cardmasters([mid], self.getModelMgr()).get(mid)
        ins.params = {
            'username' : 'DummyUser',
            'dmmid':'****',
            'url' : '',
            'thumbUrl' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(master)),
            'comment' : u'a' * Defines.GREET_COMMENT_TEXT_MAX,
        }
        return Objects.greetlog(ins)
    
    def makeDummyCard(self, obj=True):
        """ダミーのカードを作成
        """
        mid = CardMaster.getValues().id
        master = BackendApi.get_cardmasters([mid], self.getModelMgr()).get(mid)
        card = BackendApi.create_card_by_master(master)
        card.id = 1
        cardset = CardSet(card, master)
        if obj:
            obj_card = Objects.card(self, cardset)
            obj_card['level_add'] = 1
            obj_card['autosell'] = True
            obj_card['sellprice'] = 99999
            return obj_card
        else:
            return cardset
    
    
    def makeDummyCardMaster(self, has_skill=None):
        """ダミーのカードを作成.
        """
        if has_skill is None:
            mid = CardMaster.getValues().id
        elif has_skill:
            mid = CardMaster.getValues(filters={'skill__gt':0}).id
        else:
            mid = CardMaster.getValues(filters={'skill':0}).id
        
        master = BackendApi.get_cardmasters([mid], self.getModelMgr()).get(mid)
        return Objects.cardmaster(self, master)
    
    def makeDummyTreasure(self, ttype):
        """ダミーの宝箱を作成.
        """
        model_cls = TreasureUtil.get_model_cls(ttype)
        ins = model_cls()
        ins.id = 1
        ins.ctime = OSAUtil.get_now()
        ins.etime = OSAUtil.get_now()
        return Objects.treasure(self, ins, ttype)
    
    def makeDummyTreasureItem(self):
        """ダミーの宝箱を作成.
        """
        model_mgr = self.getModelMgr()
        presentlist = BackendApi.create_present(model_mgr, 0, 0, Defines.ItemType.GOLD, 0, 100, do_set_save=False)
        presentset = PresentSet.presentToPresentSet(model_mgr, presentlist)[0]
        return Objects.treasureitem(self, presentset, 1)
    
    def makeDummyTradeData(self):
        """秘宝交換レートを作成.
        """
        model_mgr = self.getModelMgr()
        ins = TradeMaster()
        ins.id = 1
        ins.itype = Defines.ItemType.TRYLUCKTICKET
        ins.itemid = 0
        ins.itemnum = 1
        ins.rate_cabaretking = 999
        ins.rate_demiworld = 999
        presentlist = BackendApi.create_present(model_mgr, 0, 0, Defines.ItemType.GOLD, 0, 100, do_set_save=False)
        presentset = PresentSet.presentToPresentSet(model_mgr, presentlist)[0]
        return Objects.trade(self, ins, presentset)
    
    def makeDummyPlayer(self, obj=True):
        """ダミーのプレイヤーを作成.
        """
        player = ModelPlayer([Player.makeInstance(0)])
        for model_cls in ModelPlayer.Meta.MODELS:
            player.setModel(model_cls.makeInstance(player.id))
        player.dmmid = self.osa_util.viewer_id
        player.ptype = Defines.CharacterType.TYPE_001
        player.tutorialstate = Defines.TutorialStatus.COMPLETED
        player.hp = 100
        player.set_ap(player.get_ap_max())
        player.set_bp(player.get_bp_max())
        player.goldkey = 99
        player.silverkey = 99
        player.cabaretking = 999
        player.demiworld = 999
        
        if obj:
            obj_player = Objects.player(self, player, People.makeNotFound("0000"), self.makeDummyCard(False))
            obj_player['bp'] = 50
            obj_player['cost_total'] = 100
            obj_player['receive'] = True
            obj_player['btime'] = OSAUtil.get_now().strftime("%Y/%m/%d %H:%M:%S")
            obj_player['deckmember'] = [self.makeDummyCard()] * (Defines.DECK_CARD_NUM_MAX - 2)
            obj_player['battlekos'] = {
                'win_total' : 31,
                'lose_total' : 30,
            }
            obj_player['power_total'] = 10000
            obj_player['skilllist'] = self.makeDummySkillInfoList()
            obj_player['event_score'] = 9999999999
            obj_player['event_rank'] = 1000000
            obj_player['is_battle_ok'] = True
            obj_player['event_rankname'] = u'キャバ王'
            return obj_player
        else:
            return player
    def makeDummySkillInfoList(self):
        return [{
                'color' : Defines.CharacterType.Effect.TEXT_COLOR.get(Defines.CharacterType.Effect.KOAKUMA),
                'name' : 'スキル1ああああああああ',
            },
            {
                'color' : Defines.CharacterType.Effect.TEXT_COLOR.get(Defines.CharacterType.Effect.IYASHI),
                'name' : 'スキル2ああああああああ',
            },
            {
                'color' : Defines.CharacterType.Effect.TEXT_COLOR.get(Defines.CharacterType.Effect.CHISEI),
                'name' : 'スキル3ああああああああ',
            },
            {
                'color' : Defines.CharacterType.Effect.TEXT_COLOR.get(Defines.CharacterType.Effect.NORMAL),
                'name' : 'スキル4ああああああああ',
            },
        ] * 2
    
    def makeDummySkillMaster(self):
        skillmaster = SkillMaster.makeInstance(1)
        skillmaster.name = 'スキル３４５６７８９０１２'
        skillmaster.text = '説明２３４５６７８９０１２３４５６７８９'
        return Objects.skillmaster(skillmaster)
    
    def makeDummyEventMovie(self, is_open):
        """イベント動画のダミー.
        """
        eventmoviemaster = EventMovieMaster.makeInstance(0)
        eventmoviemaster.cast = u'動画女優名'
        eventmoviemaster.title = u'動画タイトル'
        eventmoviemaster.text = u'動画説明012345678901234567890123456789'
        
        moviemaster = MoviePlayList.makeInstance(0)
        viewdata = EventMovieViewData.makeInstance(0)
        
        obj = Objects.eventmovie(self, eventmoviemaster, moviemaster, viewdata, is_open)
        obj['name'] = u'動画名'
        return obj
    
def main(request):
    return Handler.run(request)
