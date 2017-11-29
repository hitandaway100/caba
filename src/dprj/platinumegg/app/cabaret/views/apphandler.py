# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.basehandler import BaseHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerRegist, PlayerTutorial,\
    Player, PlayerLogin, PlayerDeck, PlayerRequest, PlayerGachaPt, PlayerGold,\
    PlayerTreasure
from platinumegg.lib.opensocial.util import OSAUtil
import settings_sub
from platinumegg.app.cabaret.util.item import ItemUtil
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.player import ModelPlayer
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.Gacha import GachaPlayData
import urllib
from platinumegg.app.cabaret.util.promotion import PromotionSettings
from platinumegg.lib.opensocial.useragent import BrowserType


class AppHandler(BaseHandler):
    """アプリのハンドラ.
    """
    
    def __init__(self):
        BaseHandler.__init__(self)
        self.__viewer_player = None
    
    @classmethod
    def get_timeout_time(cls):
        return 12
    
    def setDefaultParam(self):
        # クライアントに渡す値のデフォルトを定義.
        BaseHandler.setDefaultParam(self)
        
        self.html_param['is_tutorial'] = False
        
        # 定数.
        self.html_param['GREET_GACHA_PT'] = Defines.GREET_GACHA_PT
        self.html_param['GREET_COUNT_MAX_PER_DAY'] = Defines.GREET_COUNT_MAX_PER_DAY
        
        # デフォルトで埋め込んでおくUrl.
        pagelist = (
            'top',
            'mypage',
            'scout',
            'areamap',
            'battle',
            'gacha',
            'deck',
            'deck_raid',
            'infomation',
            'playerlog',
            'friendlog',
            'composition',
            'evolution',
            'album',
            'memories',
            'friendlist',
            'shop',
            'greetlog',
            'apitest',
            'present',
            'itemlist',
            'treasurelist',
            'friendsearch',
            'happening',
            'raidloglist',
            'trade',
            'support_paymentlist',
            'help',
            'warnpage',
            'invite',
            'myframe',
            'getstatus',
            'transfer',
            'config',
            'cabaclubtop',
            'raidevent_top',
        )
        for pagename in pagelist:
            self.html_param['url_%s' % pagename] = self.makeAppLinkUrl(getattr(UrlMaker, pagename)(), add_frompage=False)
        
        for pagename in ('cardbox', 'sell'):
            url = getattr(UrlMaker, pagename)()
            self.html_param['url_%s' % pagename] = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_PAGE, 0), add_frompage=False)
        
        gachatypes = list(set(Defines.GachaConsumeType.GTYPE_NAMES.values()))
        urlbase = UrlMaker.gacha()
        for gachatype in gachatypes:
            self.html_param['url_gacha_%s' % gachatype] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_GTYPE, gachatype))

        self.html_param['url_gacha_ctype_ticket'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.TICKET))
        
        urlbase = UrlMaker.friendlist()
        # 申請中一覧.
        self.html_param['url_friendlist_send'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_STATE, Defines.FriendState.SEND), add_frompage=False)
        # 承認待ち一覧.
        self.html_param['url_friendlist_receive'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_STATE, Defines.FriendState.RECEIVE), add_frompage=False)
        
        if self.is_pc:
            self.html_param['url_community'] = Defines.URL_COMUNITY_PC
        else:
            self.html_param['url_community'] = Defines.URL_COMUNITY_SP
        
        if self.osa_util.session:
            self.html_param['cookie'] = 'session=%s; path=/;' % self.osa_util.session
        
        self.html_param['gold_name'] = Defines.ItemType.NAMES[Defines.ItemType.GOLD]
        self.html_param['gold_unit'] = Defines.ItemType.UNIT[Defines.ItemType.GOLD]
        self.html_param['gachapt_name'] = Defines.ItemType.NAMES[Defines.ItemType.GACHA_PT]
        self.html_param['rareover_ticket_name'] = Defines.ItemType.NAMES[Defines.ItemType.RAREOVERTICKET]
        self.html_param['tryluck_ticket_name'] = Defines.ItemType.NAMES[Defines.ItemType.TRYLUCKTICKET]
        self.html_param['memories_ticket_name'] = Defines.ItemType.NAMES[Defines.ItemType.MEMORIESTICKET]
        self.html_param['gacha_ticket_name'] = Defines.ItemType.NAMES[Defines.ItemType.GACHATICKET]
        
        if settings_sub.IS_DEV:
            self.html_param['url_template_test'] = self.makeAppLinkUrl('/template_test/sp/top/top.html')
            self.html_param['url_template_test_old'] = self.makeAppLinkUrl('/template_test/sp_old/top/top.html')
            self.html_param['url_html5_test'] = self.makeAppLinkUrl('/html5_test/')
            self.html_param['url_cookie_test'] = self.makeAppLinkUrl('/cookie_test/')
            self.html_param['url_promotion_debug'] = self.makeAppLinkUrl('/promotiondebug/%s/' % PromotionSettings.Apps.CSC)
        
        self.html_param['is_admin_access'] = self.osa_util.is_admin_access
        self.html_param['is_dbg_user'] = self.osa_util.is_dbg_user
        
        self.html_param['is_new_session'] = self.osa_util.is_new_session
        
        url = '/session_set'
        url = OSAUtil.addQuery(url, OSAUtil.KEY_VIEWER_ID, self.osa_util.viewer_id)
        url = OSAUtil.addQuery(url, OSAUtil.KEY_OWNER_ID, self.osa_util.viewer_id)
        self.html_param['url_session_set'] = self.url_cgi + url
        
        if self.request.method == 'POST':
            url_self = self.url_cgi + UrlMaker.top()
        else:
            url_self = self.request.url
            for k in self.request.body.keys():
                if k.find('auth') != -1:
                    continue
                elif k in (OSAUtil.KEY_VIEWER_ID, OSAUtil.KEY_OWNER_ID, OSAUtil.KEY_APP_ID):
                    continue
                url_self = OSAUtil.addQuery(url_self, k, self.request.body[k])
        self.html_param['url_session_callback'] = url_self
        
        self.html_param['url_session_error'] = self.makeAppLinkUrl(UrlMaker.session_error())
        
        self.html_param['is_pc'] = self.is_pc
        self.html_param['is_ios'] = self.osa_util.useragent.is_ios()
        self.html_param['is_android'] = self.osa_util.useragent.is_android()
        self.html_param['os_version'] = self.osa_util.useragent.version or '0'
        
        self.html_param['is_ie'] = self.osa_util.useragent.browser in (BrowserType.INTERNETEXPROLER, BrowserType.INTERNETEXPROLER_11_OVER)
        self.html_param['is_safari'] = self.osa_util.useragent.browser == BrowserType.SAFARI
        self.html_param['is_firefox'] = self.osa_util.useragent.browser == BrowserType.FIREFOX
        self.html_param['is_chrome'] = self.osa_util.useragent.browser == BrowserType.CHROME
        self.html_param['is_windows'] = self.osa_util.useragent.is_windows
        
        self.html_param['cur_session'] = self.osa_util.session or ''
        
        menu_banner = BackendApi.get_menu_eventbanner(self, using=settings.DB_READONLY)
        self.html_param['menu_banner'] = Objects.eventbanner(self, menu_banner) if menu_banner else None
        
        self.html_param['Defines'] = Defines
        self.html_param['ItemUtil'] = ItemUtil
    
    def get_templates_folder(self):
        # 使用するテンプレートフォルダ.
        if self.is_pc:
            return [u'pc/', u'sp/']
        else:
            return u'sp/'
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return None
    
    def getViewerPlayer(self, quiet=False):
        """Viewer情報.
        """
        if self.__viewer_player is not None:
            return self.__viewer_player
        
        dmmid = self.osa_util.viewer_id
        uid = BackendApi.dmmid_to_appuid(self, [dmmid], using=settings.DB_READONLY).get(dmmid, None)
        self.addloginfo('dmmid_to_appuid')
        if uid is not None:
            classlist = [PlayerRegist, PlayerTutorial]
            classlist.extend(self.__class__.getViewerPlayerClassList() or [])
            players = BackendApi.get_players(self, [uid], classlist, using=settings.DB_READONLY)
            if 0 < len(players):
                self.__viewer_player = players[0]
        self.addloginfo('get player')
        
        if (self.__viewer_player is None or self.__viewer_player.getModel(PlayerRegist) is None) and not quiet:
            # 未登録.
            raise CabaretError(u'未登録です', CabaretError.Code.NOT_REGISTERD)
        elif self.__class__.doUpdateLoginTime() and self.__viewer_player.is_tutorialend():
            seconds = None
            if self.__viewer_player.getModel(PlayerLogin):
                timediff = OSAUtil.get_now() - self.__viewer_player.ltime
                seconds = timediff.days * 86400 + timediff.seconds
            
            if seconds is None or self.__class__.getUpdateLoginTimeInterval() < seconds:
                try:
                    model_mgr = db_util.run_in_transaction(self.__class__.tr_updatelogintime, self.__viewer_player.getModel(Player), self.is_pc)
                    model_mgr.write_end()
                except:
                    pass
            else:
                BackendApi.save_weeklylogin(uid, self.is_pc)
        self.addloginfo('save login')
        
        return self.__viewer_player
    
    @classmethod
    def doUpdateLoginTime(cls):
        return False
    
    @classmethod
    def getUpdateLoginTimeInterval(cls):
        return 21600
    
    @staticmethod
    def tr_updatelogintime(player, is_pc):
        model_mgr = ModelRequestMgr()
        modelplayer = ModelPlayer([player])
        BackendApi.tr_updatelogintime(model_mgr, modelplayer, is_pc)
        model_mgr.write_all()
        return model_mgr
    
    def checkUser(self):
        if self.osa_util.is_admin_access and not self.osa_util.is_dbg_user:
            raise CabaretError(u'セッションが切れました.', CabaretError.Code.INVALID_SESSION)
        # overrideして必要な作業だけおこなう.
        self.osa_util.checkUser()
        self.osa_util.checkOAuth()
    
    def processError(self, error_message):
        if settings_sub.IS_BENCH:
            # 負荷テスト時は何かあった時にわかりやすくするため500返す.
            self.response.set_status(500)
        if self.is_pc:
            self.__processErrorForPc(error_message)
        else:
            self.__processErrorForSp(error_message)
    
    def __processErrorForSp(self, error_message):
        # なんかｴﾗｰ.
        self.html_param['error_message'] = error_message
        self.writeAppHtml('error')
    
    def __processErrorForPc(self, error_message):
        self.html_param['error_message'] = error_message
        self.writeAppHtml('error')
#         self.json_param['error_message'] = unicode(error_message)
#         if settings_sub.USE_LOG:
#             self.json_param['log'] = self.osa_util.logger.to_string()
#         try:
#             self.writeAppJson()
#         except:
#             aaa = {}
#             aaa[Defines.STATUS_KEY_NAME] = CabaretError.Code.UNKNOWN
#             aaa['error_message'] = u'json convert error.\r\n'
#             aaa['error_message'] += unicode(self.json_param)
#             aaa['result'] = {}
#             if getattr(self, 'osa_util', None) is None:
#                 # __setStaticParamあたりで死ぬとosa_utilがセットされてない.
#                 self.__write_json_obj(aaa)
#             else:
#                 self.osa_util.write_json_obj(aaa)
    
    def processAppError(self, err):
        if self.is_pc:
            self.__processAppErrorForPc(err)
        else:
            self.__processAppErrorForSp(err)
    
    def __processAppErrorForSp(self, err):
        if err.code == CabaretError.Code.INVALID_SESSION:
            url = UrlMaker.session_error()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        elif err.code == CabaretError.Code.NOT_REGISTERD:
            self.redirectToTop()
            return
        BaseHandler.processAppError(self, err)
    
    def __processAppErrorForPc(self, err):
        if err.code in (CabaretError.Code.INVALID_SESSION, CabaretError.Code.NOT_REGISTERD):
            url = UrlMaker.session_error()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        else:
#            self.json_param['viewer_id'] = self.osa_util.viewer_id
#            self.json_param['app_id'] = self.osa_util.appparam.app_id
#            self.json_param['code'] = err.code
#            self.json_param['str_code'] = CabaretError.getCodeString(err.code)
#            self.json_param['message'] = err.value
#            self.json_param[Defines.STATUS_KEY_NAME] = err.code
#            self.processError(err.value)
            BaseHandler.processAppError(self, err)
    
    def __makeBackLinkUrlBattle(self, args):
        return {
            'url' : self.makeAppLinkUrl(UrlMaker.battle(), add_frompage=False),
            'text' : u'キャバ王への道へ戻る'
        }
    def __makeBackLinkUrlBattlePre(self, args):
        return {
            'url' : self.makeAppLinkUrl(UrlMaker.battlepre(), add_frompage=False),
            'text' : u'キャバ王への道へ戻る'
        }
    def __makeBackLinkUrlScout(self, args):
        if args and 0 < len(args) and str(args[0]).isdigit():
            model_mgr = self.getModelMgr()
            uid = self.getViewerPlayer().id
            mid = int(args[0])
            scoutkey = BackendApi.get_scoutkey(model_mgr, uid, mid, using=settings.DB_READONLY)
            url = UrlMaker.scoutdo(mid, scoutkey)
        else:
            url = UrlMaker.scout()
        return {
            'url' : self.makeAppLinkUrl(url, add_frompage=False),
            'text' : u'スカウトへ戻る'
        }
    def __makeBackLinkUrlScoutEvent(self, args):
        if args and 1 < len(args) and str(args[0]).isdigit():
            url = UrlMaker.scouteventdo(int(args[0]), urllib.unquote(args[1]))
        else:
            url = UrlMaker.scoutevent()
        return {
            'url' : self.makeAppLinkUrl(url, add_frompage=False),
            'text' : u'イベントスカウトへ戻る'
        }
    def __makeBackLinkUrlProduceEvent(self, args):
        if args and 1 < len(args) and str(args[0]).isdigit():
            url = UrlMaker.produceevent_scoutdo(int(args[0]), urllib.unquote(args[1]))
        else:
            url = UrlMaker.produceevent_top()
        return {
            'url' : self.makeAppLinkUrl(url, add_frompage=False),
            'text' : u'イベントスカウトへ戻る'
        }
    def __makeBackLinkUrlScoutEventBoss(self, args):
        if args and 0 < len(args) and str(args[0]).isdigit():
            self.setFromPage(Defines.FromPages.SCOUTEVENT, int(args[0]))
            url = UrlMaker.bosspre(int(args[0]))
            return {
                'url' : self.makeAppLinkUrl(url, add_frompage=True),
                'text' : u'太客接客へ戻る'
            }
        return None
    def __makeBackLinkUrlHappening(self, args):
        url = UrlMaker.happening()
        return {
            'url' : self.makeAppLinkUrl(url, add_frompage=False),
            'text' : u'超太客へ戻る'
        }
    def __makeBackLinkUrlRaid(self, args):
        if args and 0 < len(args) and str(args[0]).isdigit():
            url = UrlMaker.raidhelpdetail(int(args[0]))
            return {
                'url' : self.makeAppLinkUrl(url, add_frompage=False),
                'text' : u'超太客へ戻る'
            }
        return None
    def __makeBackLinkUrlRaidLog(self, args):
        if args and 0 < len(args) and str(args[0]).isdigit():
            url = UrlMaker.raidlogdetail(int(args[0]))
        else:
            url = UrlMaker.raidloglist()
        return {
            'url' : self.makeAppLinkUrl(url, add_frompage=False),
            'text' : u'超太客来店履歴へ戻る'
        }
    def __makeBackLinkUrlBoss(self, args):
        if args and 0 < len(args) and str(args[0]).isdigit():
            url = UrlMaker.bosspre(int(args[0]))
            return {
                'url' : self.makeAppLinkUrl(url, add_frompage=False),
                'text' : u'太客接客へ戻る'
            }
        return None
    
    def __makeBackLinkUrlBattleEvent(self, args):
        if args and 0 < len(args) and str(args[0]).isdigit():
            revengeid = None
            if 1 < len(args) and str(args[1]).isdigit():
                revengeid = args[1]
            rival_key = None
            if 2 < len(args):
                rival_key = args[2]

            url = UrlMaker.battleevent_battlepre(args[0], revengeid, rival_key=rival_key)
        else:
            url = UrlMaker.battleevent_opplist()
        return {
            'url' : self.makeAppLinkUrl(url, add_frompage=False),
            'text' : u'イベントへ戻る'
        }
    
    def __makeBackLinkUrlRaidEvent(self, args):
        if args and 0 < len(args) and str(args[0]).isdigit():
            url = UrlMaker.raidevent_top(args[0])
        else:
            url = UrlMaker.raidevent_top()
        return {
            'url' : self.makeAppLinkUrl(url, add_frompage=False),
            'text' : u'イベントへ戻る'
        }
    
    def __makeBackLinkUrlRaidEventScout(self, args):
        if args and 1 < len(args) and str(args[0]).isdigit():
            url = UrlMaker.raidevent_scoutdo(int(args[0]), urllib.unquote(args[1]))
        else:
            url = UrlMaker.raidevent_scouttop()
        return {
            'url' : self.makeAppLinkUrl(url, add_frompage=False),
            'text' : u'イベントスカウトへ戻る'
        }
    def __makeBackLinkUrlRaidEventScoutBoss(self, args):
        if args and 0 < len(args) and str(args[0]).isdigit():
            self.setFromPage(Defines.FromPages.RAIDEVENTSCOUT, int(args[0]))
            url = UrlMaker.bosspre(int(args[0]))
            return {
                'url' : self.makeAppLinkUrl(url, add_frompage=True),
                'text' : u'太客接客へ戻る'
            }
        return None
    def __makeBackLinkUrlCabaClubStore(self, args):
        if args and 0 < len(args) and str(args[0]).isdigit():
            url = UrlMaker.cabaclubstore(int(args[0]))
        else:
            url = UrlMaker.cabaclubtop()
        return {
            'url' : self.makeAppLinkUrl(url, add_frompage=False),
            'text' : u'店舗へ戻る'
        }
    
    def putFromBackPageLinkUrl(self):
        """遷移元ページヘのリンクを埋め込む.
        """
        frompage_name = self.getFromPageName()
        if frompage_name:
            table = {
                Defines.FromPages.BATTLE : self.__makeBackLinkUrlBattle,
                Defines.FromPages.BATTLEPRE : self.__makeBackLinkUrlBattlePre,
                Defines.FromPages.SCOUT : self.__makeBackLinkUrlScout,
                Defines.FromPages.HAPPENING : self.__makeBackLinkUrlHappening,
                Defines.FromPages.RAID : self.__makeBackLinkUrlRaid,
                Defines.FromPages.RAIDLOG : self.__makeBackLinkUrlRaidLog,
                Defines.FromPages.BOSS : self.__makeBackLinkUrlBoss,
                Defines.FromPages.SCOUTEVENT : self.__makeBackLinkUrlScoutEvent,
                Defines.FromPages.SCOUTEVENTBOSS : self.__makeBackLinkUrlScoutEventBoss,
                Defines.FromPages.BATTLEEVENTPRE : self.__makeBackLinkUrlBattleEvent,
                Defines.FromPages.RAIDEVENT : self.__makeBackLinkUrlRaidEvent,
                Defines.FromPages.RAIDEVENTSCOUT : self.__makeBackLinkUrlRaidEventScout,
                Defines.FromPages.RAIDEVENTSCOUTBOSS : self.__makeBackLinkUrlRaidEventScoutBoss,
                Defines.FromPages.CABACLUB_STORE : self.__makeBackLinkUrlCabaClubStore,
                Defines.FromPages.PRODUCEEVENTSCOUT : self.__makeBackLinkUrlProduceEvent
            }
            func = table.get(frompage_name)
            if func:
                obj = func(self.getFromPageArgs())
                self.html_param['backpage_param'] = obj
    
    def makeProfileTag(self, uid):
        # プロフィールページのリンクタグ.
        url = UrlMaker.profile(uid)
        return Defines.GAME_PROFILE_TAG_FORMAT % (self.appparam.app_id, self.makeAppLinkUrl(url, add_frompage=False), 'プロフィール')
    
    def check_process_pre(self):
        if settings_sub.IS_LOCAL:
            pass
        elif not (self.osa_util.is_dbg_user or self.checkMaintenance()):
            return False
        elif not (self.osa_util.is_dbg_user or self.checkBeforePublication()):
            return False
        elif not self.checkUserAgent():
            return False
        elif not self.checkBan():
            return False
        return True
    
    def checkMaintenance(self):
        """メンテナンスチェック.
        """
        model_mgr = self.getModelMgr()
        app_config = BackendApi.get_appconfig(model_mgr, using=settings.DB_READONLY)
        if app_config.is_maintenance():
            self.procMaintenance()
            return False
        return True
    
    def procMaintenance(self):
        """メンテナンス状態の操作.
        """
        model_mgr = self.getModelMgr()
        app_config = BackendApi.get_appconfig(model_mgr, using=settings.DB_READONLY)
        # person.
        self.html_param['is_platform_maintenance'] = app_config.is_platform_maintenance()
        self.html_param['is_emergency'] = app_config.is_emergency()
        self.html_param['stime'] = app_config.stime
        self.html_param['etime'] = app_config.etime
        self.writeAppHtml('maintenance')
    
    def checkBeforePublication(self):
        """公開チェック.
        """
#        model_mgr = self.getModelMgr()
#        config = BackendApi.get_preregistconfig(model_mgr, using=settings.DB_READONLY)
#        if config.is_before_publication():
#            v_player = self.getViewerPlayer(True)
#            
#            do_redirect = True
#            if v_player:
#                person = BackendApi.get_dmmplayers(self, [v_player], using=settings.DB_READONLY, do_execute=True).get(self.osa_util.viewer_id)
#                if person.userType in ('developer','Staff') or self.osa_util.is_dbg_user:
#                    do_redirect = False
#            
#            if do_redirect:
#                if self.is_pc:
#                    self.json_result_param['is_before_publication'] = True
#                    self.json_param[Defines.STATUS_KEY_NAME] = CabaretError.Code.OAUTH_ERROR
#                    self.writeAppJson()
#                else:
#                    url = UrlMaker.top()
#                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
#                return False
        return True
    
    def checkBan(self):
        """停止アカウントチェック.
        """
        self.addloginfo('check Ban')
        v_player = self.getViewerPlayer(True)
        self.addloginfo('getViewerPlayer')
        if v_player is None or not v_player.is_tutorialend():
            return True
        model_mgr = self.getModelMgr()
        if BackendApi.check_player_ban(model_mgr, v_player.id, using=settings.DB_READONLY):
            self.addloginfo('check_player_ban')
            return True
        else:
            url = UrlMaker.ban()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return False
    
    def checkUserAgent(self):
        """UserAgentをチェック.
        """
        if self.check_support_terminal():
            return True
        self.appRedirect(self.makeAppLinkUrl(UrlMaker.no_support()))
        return False
    
    def check_support_terminal(self):
        """対応端末か.
        Android2.3
        iOS4以降(iPhoneのみ)
        """
        flag = False
        
        def versionToInt(v):
            if not v:
                return 0
            arr = v.split('.')+[0]*3
            return sum([int(s)<<((2-idx)*8) for idx,s in enumerate(arr[:3])])
        
        def compareVersion(v1, v2):
            return versionToInt(v1) <= versionToInt(v2)
        
        if self.is_pc:
            versions = {
                BrowserType.INTERNETEXPROLER : '11',
                BrowserType.INTERNETEXPROLER_11_OVER : '11',
                BrowserType.FIREFOX : '29',
                BrowserType.CHROME : '35',
                BrowserType.SAFARI : '6.1.2',
            }
            v = versions.get(self.osa_util.useragent.browser, None)
            if v is not None and compareVersion(v, self.osa_util.useragent.version):
                flag = True
        else:
            if not self.osa_util.useragent.is_smartphone():
                pass
            elif self.osa_util.useragent.is_ios():
                flag = compareVersion(Defines.IOS_VERSION, self.osa_util.useragent.version)
            elif self.osa_util.useragent.is_android():
                flag = compareVersion(Defines.ANDROID_VERSION, self.osa_util.useragent.version)
            else:
                flag = self.osa_util.is_dbg
        return flag
    
    def __makePrizeGetLinkParam(self, url, text):
        return {
            'url' : self.makeAppLinkUrl(url),
            'text' : text,
        }
    def __makePrizeGetLinkParamComposition(self, itype, iid):
        return self.__makePrizeGetLinkParam(UrlMaker.composition(), u'教育する')
    def __makePrizeGetLinkParamEvolution(self, itype, iid):
        dress = 40003
        bag = 40002
        necklace = 40001
        if iid in (dress, bag, necklace):
            return self.__makePrizeGetLinkParamComposition(itype, iid)
        else:
            return self.__makePrizeGetLinkParam(UrlMaker.evolution(), u'ハメ管理する')
    def __makePrizeGetLinkParamGachaFree(self, itype, iid):
        url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.FREE)
        return self.__makePrizeGetLinkParam(url, u'引き抜く')
    def __makePrizeGetLinkParamItemList(self, itype, iid):
        return self.__makePrizeGetLinkParam(UrlMaker.itemlist(), u'使用する')
    def __makePrizeGetLinkParamGachaTicket(self, itype, iid):
        url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.TICKET)
        return self.__makePrizeGetLinkParam(url, u'引き抜く')
    def __makePrizeGetLinkParamGoldTreasure(self, itype, iid):
        return self.__makePrizeGetLinkParam(UrlMaker.treasurelist(Defines.TreasureType.GOLD), u'宝箱を開ける')
    def __makePrizeGetLinkParamSilverTreasure(self, itype, iid):
        return self.__makePrizeGetLinkParam(UrlMaker.treasurelist(Defines.TreasureType.SILVER), u'宝箱を開ける')
    def __makePrizeGetLinkParamTrade(self, itype, iid):
        return self.__makePrizeGetLinkParam(UrlMaker.trade(), u'秘宝交換へ')
    
    def makePrizeGetLinkParam(self, itype, iid=0):
        """受け取った報酬ごとにリンクURLと文言を分けたい.
        """
        table = {
            Defines.ItemType.GOLD : self.__makePrizeGetLinkParamComposition,
            Defines.ItemType.GACHA_PT : self.__makePrizeGetLinkParamGachaFree,
            Defines.ItemType.ITEM : self.__makePrizeGetLinkParamItemList,
            Defines.ItemType.CARD : self.__makePrizeGetLinkParamEvolution,
            Defines.ItemType.RAREOVERTICKET : self.__makePrizeGetLinkParamGachaTicket,
            Defines.ItemType.TRYLUCKTICKET : self.__makePrizeGetLinkParamGachaFree,
            Defines.ItemType.MEMORIESTICKET : self.__makePrizeGetLinkParamGachaTicket,
            Defines.ItemType.GACHATICKET : self.__makePrizeGetLinkParamGachaFree,
            Defines.ItemType.GOLDKEY : self.__makePrizeGetLinkParamGoldTreasure,
            Defines.ItemType.SILVERKEY : self.__makePrizeGetLinkParamSilverTreasure,
            Defines.ItemType.CABARETKING_TREASURE : self.__makePrizeGetLinkParamTrade,
            Defines.ItemType.DEMIWORLD_TREASURE : self.__makePrizeGetLinkParamTrade,
            Defines.ItemType.ADDITIONAL_GACHATICKET : self.__makePrizeGetLinkParamGachaTicket,
        }
        f = table.get(itype)
        if f:
            return f(itype, iid)
        else:
            return None
    
    def writePlayPaymentGacha(self, paymentId,player_trade_point=None):
        """課金ガチャプレイ書き込み.
        """
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        try:
            model_mgr, entry, player = db_util.run_in_transaction(self.__tr_write_playgacha_pay, uid, paymentId,player_trade_point=player_trade_point)
            model_mgr.write_end()
            v_player.setModel(player.getModel(PlayerRequest))
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                model_mgr = self.getModelMgr()
                entry = BackendApi.get_gachapaymententry(model_mgr, paymentId)
                v_player.setModel(BackendApi.get_model(ModelRequestMgr(), PlayerRequest, uid))
            else:
                raise
        return entry
    
    def __tr_write_playgacha_pay(self, uid, paymentId,player_trade_point=None):
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_players(self, [uid], [PlayerDeck], model_mgr=model_mgr)[0]
        _, entry = BackendApi.tr_play_gacha_pay(model_mgr, player, paymentId, self.is_pc,player_trade_point=player_trade_point)
        model_mgr.write_all()
        return model_mgr, entry, player
    
    def writeGachaCancel(self, paymentId):
        """課金ガチャキャンセル書き込み.
        """
        v_player = self.getViewerPlayer()
        try:
            model_mgr = db_util.run_in_transaction(self.__tr_write_gacha_cancel, v_player.id, paymentId)
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
    
    def __tr_write_gacha_cancel(self, uid, paymentId):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_gacha_cancel(model_mgr, uid, paymentId)
        model_mgr.write_all()
        return model_mgr
    
    def writeGachaTimeout(self, paymentId):
        """課金ガチャキャンセル書き込み.
        """
        v_player = self.getViewerPlayer()
        try:
            model_mgr = db_util.run_in_transaction(self.__tr_write_gacha_timeout, v_player.id, paymentId)
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
    
    def __tr_write_gacha_timeout(self, uid, paymentId):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_gacha_timeout(model_mgr, uid, paymentId)
        model_mgr.write_all()
        return model_mgr
    
    @staticmethod
    def tr_write_playdata(uid, midlist):
        """プレイ情報がないので用意.
        """
        playdatas = {}
        model_mgr = ModelRequestMgr()
        for mid in midlist:
            ins = GachaPlayData.makeInstance(GachaPlayData.makeID(uid, mid))
            model_mgr.set_save(ins)
            playdatas[mid] = ins
        model_mgr.write_all()
        return model_mgr, playdatas
    
    def writeBuyItem(self, paymentId):
        """購入書き込み.
        """
        v_player = self.getViewerPlayer()
        
        try:
            model_mgr, entry = db_util.run_in_transaction(self.__tr_write_buyitem, v_player.id, paymentId)
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                model_mgr = self.getModelMgr()
                entry = BackendApi.get_shoppaymententry(model_mgr, paymentId)
            else:
                raise
        return entry
    
    def __tr_write_buyitem(self, uid, paymentId):
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_players(self, [uid], [PlayerRegist, PlayerGachaPt, PlayerGold, PlayerTreasure], model_mgr=model_mgr)[0]
        entry = BackendApi.tr_shopbuy(model_mgr, player, paymentId, self.is_pc)
        model_mgr.write_all()
        return model_mgr, entry
    
    def writeBuyCancel(self, paymentId):
        """キャンセル書き込み.
        """
        v_player = self.getViewerPlayer()
        try:
            model_mgr = db_util.run_in_transaction(self.__tr_buy_cancel, v_player.id, paymentId)
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
    
    def __tr_buy_cancel(self, uid, paymentId):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_shopcancel(model_mgr, uid, paymentId)
        model_mgr.write_all()
        return model_mgr
    
    def writeBuyTimeOut(self, paymentId):
        """期限切れ書き込み.
        """
        v_player = self.getViewerPlayer()
        try:
            model_mgr = db_util.run_in_transaction(self.__tr_buy_timeout, v_player.id, paymentId)
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
    
    def __tr_buy_timeout(self, uid, paymentId):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_shoptimeout(model_mgr, uid, paymentId)
        model_mgr.write_all()
        return model_mgr
    
    def make_rankingprizelist(self, prizes):
        """ランキング報酬リスト作成.
        """
        model_mgr = self.getModelMgr()
        
        prizedatalist = []
        for data in prizes:
            prizeidlist = data.get('prize')
            if not prizeidlist:
                continue
            
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY)
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
            
            prizedatalist.append({
                'rank_min' : data['rank_min'],
                'rank_max' : data['rank_max'],
                'prizeinfo' : prizeinfo,
            })
        prizedatalist.sort(key=lambda x:x['rank_min'])
        return prizedatalist
    
    def make_pointprizelist(self, prizes, cur_point=0):
        """ポイント達成報酬.
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
    
    def redirectToTop(self):
        """TOPページヘリダイレクト.
        """
        if self.is_pc:
            # フレームを考慮.javascriptで飛ばす.
            self.writeAppHtml('to_top')
        else:
            url = UrlMaker.top()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))

