# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.basehandler import BaseHandler
from defines import Defines
import settings_sub
import socket
import os
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.alert import AlertCode
import urllib
from platinumegg.lib.strutil import StrUtil
from platinumegg.lib.compression import intDecompress
import binascii
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.lib.opensocial.util import OSAUtil

#-------------------------------------------------------------------------------
# BaseHandler継承.
class AdminHandler(BaseHandler):
    
    @classmethod
    def get_timeout_time(cls):
        return 0
    
    def get_templates_folder(self):
        # 使用するテンプレートフォルダ.
        return Defines.ADMIN_PREFIX + '/'
    
    def setDefaultParam(self):
        BaseHandler.setDefaultParam(self)
        
        # html_paramの初期値.
        self.html_param['content_name'] = self.getUrlArgs('/').get(0)
        
        model_mgr = self.getModelMgr()
        self.html_param['is_maintenance'] = BackendApi.get_appconfig(model_mgr).is_maintenance()
#        self.html_param['is_before_publication'] = BackendApi.get_preregistconfig(model_mgr).is_before_publication()
        self.html_param['is_before_publication'] = False
        
        self.html_param['pid'] = os.getpid()
        self.html_param['host'] = socket.gethostname()
        
        def putAccordionContentsList(name, cntents, urlmaker):
            data = {
                'content_name':self.getUrlArgs('/%s/' % name).get(0),
                'contents':[],
            }
            for content_name, content_label in cntents:
                content = {
                    'url':self.makeAppLinkUrlAdmin(urlmaker(content_name)),
                    'label':content_label,
                    'name':content_name,
                }
                data['contents'].append(content)
            self.html_param[name] = data
        
        # モデル編集のパッケージ周り.
        model_edit_contents = (
            (u'schedule', u'スケジュール'),
            (u'infomation', u'お知らせ'),
            (u'top_banner', u'トップページバナー'),
            (u'event_banner', u'イベントバナー'),
            (u'popup', u'ポップアップ'),
            (u'player_level_exp', u'プレイヤー経験値テーブル'),
            (u'card_level_exp', u'カード経験値テーブル'),
            (u'item', u'アイテム'),
            (u'skill', u'サービス(スキル)'),
            (u'card', u'カード'),
            (u'prize', u'報酬'),
            (u'access_bonus', u'アクセスボーナス'),
            (u'login_bonus', u'連続ログインボーナス'),
            (u'loginbonustimelimited', u'ロングログインボーナス'),
            (u'loginbonustimelimiteddays', u'ロングログインボーナス報酬'),
            (u'sugorokumap', u'双六LBマップ'),
            (u'sugorokumapsquares', u'双六LBマス'),
            (u'sugoroku', u'双六ログインボーナス'),
            (u'boss', u'ボス'),
            (u'raid', u'レイドボス'),
            (u'happening', u'ハプニング'),
            (u'area', u'スカウトエリア'),
            (u'scout', u'スカウト'),
            (u'battlerank', u'ランク'),
            (u'default_card', u'登録時の所持カード'),
            (u'memories', u'思い出アルバム'),
            (u'eventmovie', u'イベント動画'),
            (u'gacha_explain_text', u'ガチャの説明テキスト設定'),
            (u'gacha_group', u'引き抜きのカードグループ'),
            (u'gacha_slide_cast', u'引抜のスライドキャスト設定'),
            (u'gacha_header', u'引抜のヘッダー画像設定'),
            (u'gacha_box', u'引き抜きのBOX情報'),
            (u'gacha_ranking', u'ランキングガチャ'),
            (u'gacha_step', u'引き抜き（ステップアップ）'),
            (u'gacha_seat_table', u'引抜シートテーブル'),
            (u'gacha_seat', u'引抜シート'),
            (u'gacha', u'引き抜き(ガチャ)'),
            (u'gacha_boxgachadetail', u'BOXガチャ詳細設定'),
            (u'shop_item', u'ショップの商品'),
            (u'treasure_gold', u'宝箱(金)'),
            (u'treasure_gold_table', u'宝箱テーブル(金)'),
            (u'treasure_silver', u'宝箱(銀)'),
            (u'treasure_silver_table', u'宝箱テーブル(銀)'),
            (u'treasure_bronze', u'宝箱(銅)'),
            (u'treasure_bronze_table', u'宝箱テーブル(銅)'),
            (u'trade', u'秘宝交換'),
            (u'trade_shop', u'トレードショップ'),
            (u'trade_shop_item', u'トレードショップアイテム'),
            (u'reprintticket_tradeshop', u'復刻チケット交換所'),
            (u'present_everyone', u'全プレ(LB)'),
            (u'present_everyone_mypage', u'全プレ(マイページ)'),
            (u'present_everyone_record', u'予約済みの全プレ'),
            (u'text', u'テキスト文言'),
            (u'panelmissionpanel', u'パネル'),
            (u'panelmissionmission', u'パネルミッション'),
            (u'tutorialconfig', u'チュートリアルの設定'),
            (u'levelup_bonus', u'レベルアップ達成ボーナスの設定'),
            (u'invite', u'招待'),
            (u'promotion_config', u'プロモーション設定'),
            (u'promotion_prize', u'プロモーション報酬'),
            (u'promotion_requirement', u'プロモーション条件'),
            (u'raidevent', u'レイドイベント'),
            (u'raideventraid', u'[ﾚｲﾄﾞ]レイド'),
            (u'raideventrecipe', u'[ﾚｲﾄﾞ]交換アイテム'),
            (u'raideventmaterial', u'[ﾚｲﾄﾞ]交換素材'),
            (u'raideventscoutstage', u'[ﾚｲﾄﾞ]専用ステージ'),
            (u'scoutevent', u'スカウトイベント'),
            (u'scouteventstage', u'[ｽｶｳﾄ]専用ステージ'),
            (u'scouteventpresentprize', u'[ｽｶｳﾄ]ハートプレゼント報酬'),
            (u'scouteventtanzakucast', u'[ｽｶｳﾄ]短冊キャスト･チップ'),
            (u'scouteventhappeningtable', u'[ｽｶｳﾄ]曜日別レイド設定'),
            (u'scouteventraid', u'[ｽｶｳﾄ]レイド'),
            (u'battleevent', u'バトルイベント'),
            (u'battleeventpiece', u'[ﾊﾞﾄﾙ]ピース'),
            (u'battleeventrank', u'[ﾊﾞﾄﾙ]イベントランク'),
            (u'battleeventpresent', u'[ﾊﾞﾄﾙ]贈り物'),
            (u'battleeventpresentcontent', u'[ﾊﾞﾄﾙ]贈り物の中身'),
            (u'scenario', u'シナリオ'),
            (u'serial_campaign', u'シリアルコードキャンペーン'),
            (u'comebackcampaign', u'カムバックキャンペーン'),
            (u'cabaretclub', u'キャバクラシステム'),
            (u'cabaretclubevent', u'キャバクラの発生イベント'),
            (u'cabaretclubstore', u'キャバクラ店舗'),
            (u'cabaretclub_ranking_event', u'経営ランキング(イベント)'),
            (u'produce_event', u'プロデュースイベント'),
            (u'produceeventscoutstage', u'[ﾌﾟﾛﾃﾞｭｰｽ]専用ステージ'),
            (u'produceeventraid', u'[ﾌﾟﾛﾃﾞｭｰｽ]レイド'),
            (u'produce_cast', u'[ﾌﾟﾛﾃﾞｭｰｽ]キャスト'),
            (u'title', u'称号'),
        )
        putAccordionContentsList('model_edit', model_edit_contents, UrlMaker.model_edit)
        
        # 各種情報.
        infomations_contents = (
            (u'view_player', u'プレイヤー情報'),
            (u'view_userlog', u'行動履歴'),
            (u'view_raid', u'レイド情報'),
            (u'view_raidlog', u'レイド履歴'),
            (u'view_battleevent_battlelog', u'バトルイベントバトル履歴'),
            (u'view_battleevent_group', u'バトルイベントグループ情報'),
            (u'view_eventranking', u'イベントランキング'),
            (u'view_paymentlog', u'課金履歴'),
            (u'view_dmmpayment', u'DMM側課金情報'),
            (u'view_itempaymentlog', u'アイテム毎課金履歴'),
            (u'view_gacha_payment_proceeds', u'ガチャ売上'),
            (u'view_movieview', u'動画閲覧数'),
            (u'view_pcmovieview', u'動画閲覧数(PC)'),
            (u'view_serialcode', u'シリアルコード'),
            (u'view_rankinggacha_log', u'同伴ガチャ履歴'),
        )
        putAccordionContentsList('infomations', infomations_contents, UrlMaker.mgr_infomations)
        
        # KPI.
        kpi_contents = (
            (u'playerlevel', u'プレイヤーレベル分布'),
            (u'card', u'カード流通量'),
            (u'item', u'アイテム流通量'),
            (u'tutorial', u'チュートリアル分布'),
            (u'scoutcomplete', u'スカウト達成数'),
            (u'battlecount', u'バトル対戦回数'),
            (u'rankup', u'バトルランク達成数'),
            (u'raiddestroy', u'レイド討伐数'),
            (u'raidmiss', u'レイド失敗数'),
            (u'invitecount', u'招待数'),
            (u'movieview', u'動画再生数'),
            (u'pcmovieview', u'動画再生数(PC)'),
            (u'raideventpoint', u'[ﾚｲﾄﾞ]秘宝獲得数'),
            (u'raideventconsumepoint', u'[ﾚｲﾄﾞ]消費秘宝数'),
            (u'raideventticket', u'[ﾚｲﾄﾞ]日別チケット交換数'),
            (u'raideventconsumeticket', u'[ﾚｲﾄﾞ]日別チケット消費数'),
            (u'raideventdestroy', u'[ﾚｲﾄﾞ]太客討伐回数分布'),
            (u'raideventdestroybig', u'[ﾚｲﾄﾞ]大ボス討伐回数分布'),
            (u'raideventdestroylevel', u'[ﾚｲﾄﾞ]Lv別討伐回数'),
            (u'raideventstage', u'[ﾚｲﾄﾞ]ステージ分布'),
            (u'scouteventstage', u'[ｽｶｳﾄ]ステージ分布'),
            (u'scouteventpoint', u'[ｽｶｳﾄ]獲得ポイント'),
            (u'scouteventgachapointconsume', u'[ｽｶｳﾄ]消費ガチャPt'),
            (u'scouteventtipconsume', u'[ｽｶｳﾄ]チップ消費数'),
            (u'scouteventtanzaku', u'[ｽｶｳﾄ]短冊獲得数'),
            (u'battleeventjoindaily', u'[ﾊﾞﾄﾙ]日別参加数'),
            (u'battleeventjoin', u'[ﾊﾞﾄﾙ]参加率'),
            (u'battleeventresult', u'[ﾊﾞﾄﾙ]ランク別バトルPT'),
            (u'battleeventfamepoint', u'[ﾊﾞﾄﾙ]名声PT'),
            (u'battleeventbattlecount', u'[ﾊﾞﾄﾙ]バトル回数'),
            (u'battleeventpoint', u'[ﾊﾞﾄﾙ]バトルPT'),
            (u'battleeventpiececollect', u'[ﾊﾞﾄﾙ]ピース獲得数'),
            (u'produceeventstage', u'[ﾌﾟﾛﾃﾞｭｰｽ]ステージ分布'),
            (u'produceeventeducation', u'[ﾌﾟﾛﾃﾞｭｰｽ]レベル/ハート分布'),
            (u'paymententry', u'課金レコード'),
            (u'platform_uu', u'プラットフォーム別DAU'),
            (u'gacha_fq5', u'課金ガチャFQ5'),
            (u'gacha_userdata', u'ガチャユーザデータ'),
            (u'eventreport_daily', u'日別イベントレポート'),
            (u'eventreport_monthly', u'月別イベントレポート'),
            (u'eventreport_range', u'期間別イベントレポート'),
            (u'paymentgacha_leaderdata', u'課金ユーザーのリーダー'),
        )
        putAccordionContentsList('kpi_contents', kpi_contents, UrlMaker.mgr_kpi)

        # Simulator
        simulator_contents = (
            (u'gacha_simulator', u'ガチャシミュレータ'),
            (u'omake_simulator', u'おまけシミュレータ'),
        )
        putAccordionContentsList('simulator_contents', simulator_contents, UrlMaker.mgr_simulator)

        # その他のページたち.
        html_list = [
            'manage_menu',
            'master_data',
            'movie',
            'voice',
            'battle_simulator',
            'battle_panel_simulator',
            'scout_silhouette_simulator',
            'raidevent_simulator',
            'raidboss_drop_simulator',
            'ban_edit',
            'debug_tool',
            'logout',
            'view_images',
            'ng_cast',
        ]
        for name in html_list:
            self.html_param['url_%s' % name.replace('/', '_')] = self.makeAppLinkUrl(('/%s/' % name))
        
        self.html_param['Defines'] = Defines
        
        now = OSAUtil.get_now()
        self.html_param['server_nowtime'] = now
        self.html_param['datetime_weekly'] = BackendApi.to_cabaretclub_section_starttime(now)
        
        self.putAlertToHtmlParam() # アラートをセット.
        
    def checkUser(self):
        self.osa_util.checkUser()
        # 認証.
        if settings_sub.IS_LOCAL:
            return
        elif self.request.host.startswith('10.116.41.'):
            return
        elif self.request.remote_addr.startswith('10.132.67.5'):
            return
        elif self.request.remote_addr in self.appparam.developer_ip:
            return
        elif not self.request.django_request.user.is_authenticated():
            raise CabaretError(code=CabaretError.Code.NOT_AUTH)
        
    
    def makeAppLinkUrl(self, src_url):
        """アプリケーション内のページ遷移URLの作成.
        """
        return self.makeAppLinkUrlAdmin(src_url)
    
    def processError(self, error_message):
        # なんかｴﾗｰ.
        self.html_param['error_message'] = error_message
        try:
            self.writeAppHtml('error')
        except:
            if not self.response.isEnd:
                self.response.set_status(500)
                self.response.send(error_message)
    
    def processAppError(self, err):
        if err.code == CabaretError.Code.NOT_AUTH:
            # ログインして下さい.
            url = self.makeAppLinkUrlAdmin(UrlMaker.login())
            self.appRedirect(url)
        elif err.code == CabaretError.Code.NOT_ALLOWED_IP:
            # 許可されていないIP.
            self.html_param['permission_error_text'] = err.value
            self.writeAppHtml('permission_error')
        else:
            self.processError(StrUtil.to_s(err.getHtml(self.osa_util.is_dbg_user)))
    
    #===========================================================================
    # ページの上に出るお知らせ.
    # 遷移先で表示させたい場合はURLにsetAlertで追加.
    # 現在ページで表示させたい場合はputAlertToHtmlParamを使う.
    #===========================================================================
    def setAlert(self, url, message=u'', alert_code=AlertCode.INFO):
        message = urllib.quote_plus(message.encode('utf8'))
        value = '%s:%s' % (alert_code, message)
        return self.osa_util.addQuery(url, Defines.URLQUERY_ALERT, value)
    def putAlertToHtmlParam(self, message=u'', alert_code=AlertCode.INFO):
        if not message:
            strdata = self.request.get(Defines.URLQUERY_ALERT, '')
            if strdata:
                data = strdata.split(':',1)
                alert_code = int(data[0])
                message = data[1]
        if message:
            self.html_param['alert'] = {
                'code_name':AlertCode.NAMES[alert_code],
                'message':message,
            }
    
    @staticmethod
    def key_to_pass(key):
        base = 'x0}PNpAEK!*+GZ<e&UhR|i,r{l8nB6(mL]j1=zbW#qyHX3;7$M?fk@)5SOgtY%c.v/>w[I~aJ:d^DoQ4su`FT92_CV'
        arr = []
        for i in xrange(len(key)/2):
            idx = i * 2
            arr.append('%02x' % intDecompress(key[idx:idx+2], base))
        return binascii.a2b_hex(''.join(arr))
    
    def putPagenation(self, urlbase, page, contentnum, page_contentnum, urlhash=None, func_add_pagenumber=None):
        if func_add_pagenumber is None:
            func_add_pagenumber = lambda url,p:OSAUtil.addQuery(url, Defines.URLQUERY_PAGE, p)
        
        def __makePage(p):
            return {
                'num':p+1,
                'url':self.makeAppLinkUrlAdmin(func_add_pagenumber(urlbase, p)),
            }
        
        page_contentnum = max(1, page_contentnum)
        page_max = max(1, int((contentnum + page_contentnum - 1) / page_contentnum))
        
        page_view_num_max = 99
        page_range_min = max(page - int(page_view_num_max / 2), 0)
        page_range_max = max(1, min(page_range_min + page_view_num_max, page_max)) - 1
        
        pagination_data = {
            'page_list':[__makePage(p) for p in xrange(page_range_min, page_range_max + 1)],
            'now_page':__makePage(page),
            'has_next':False,
            'has_prev':False,
        }
        if page < (page_max - 1):
            pagination_data['next_page'] = __makePage(page + 1)
            pagination_data['has_next'] = True
            pagination_data['last_page'] = __makePage(page_max - 1)
        if 0 < page:
            pagination_data['prev_page'] = __makePage(page - 1)
            pagination_data['has_prev'] = True
            pagination_data['first_page'] = __makePage(0)
        if 0 < page_range_min:
            pagination_data['prev_block'] = __makePage(page_range_min - 1)
        if page_range_max < (page_max - 1):
            pagination_data['next_block'] = __makePage(page_range_max + 1)
        self.html_param['pagination'] = pagination_data
    
