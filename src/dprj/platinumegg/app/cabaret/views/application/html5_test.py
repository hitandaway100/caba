# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from defines import Defines
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.app.cabaret.util.item import ItemUtil
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.pljson import Json
from platinumegg.lib.opensocial.util import OSAUtil
import random
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from random import randint



class Handler(AppHandler):
    """HTML5を閲覧するだけ.
    """
    
    def checkUser(self):
        if not self.osa_util.is_dbg_user:
            raise CabaretError(u'認証エラー', CabaretError.Code.NOT_AUTH)
    
    def process(self):
        
        args = self.getUrlArgs('/html5_test/')

        model_mgr = self.getModelMgr()
        mid = CardMaster.getValues().id
        self.__dummycard = BackendApi.get_cardmasters([mid], model_mgr).get(mid)
        
        TABLE = (
#            ('IfTest', (u'IF試験用', self.procIfTest)),
#            ('LevelupSample',(u'レベルアップ(サンプル)', self.procLevelupSample)),
#            ('EvolutionSample',(u'ハメ管理(サンプル)', self.procEvolutionSample)),
            ('Levelup',(u'レベルアップ', self.procLevelup)),
            ('Evolution',(u'ハメ管理', self.procEvolution)),
            ('Composition',(u'教育', self.procComposition)),
            ('Battle',(u'バトル', self.procBattle)),
            ('Win2',(u'勝利(You Win)', self.procWin2)),
            ('Win1',(u'勝利(ノルマクリア)', self.procWin1)),
            ('Win3',(u'勝利(出店完了)', self.procWin3)),
            ('Lose',(u'敗北', self.procLose)),
            ('ScoutNone',(u'スカウト(なにもなかった)',self.procScout)),
            ('ScoutComplete',(u'スカウト(完了)',self.procScout)),
            ('ScoutApNone',(u'スカウト(行動力が足りない)',self.procScout)),
            ('ScoutLevelup',(u'スカウト(レベルアップ)',self.procScout)),
            ('ScoutTreasureGet',(u'スカウト(宝箱獲得)',self.procScout)),
            ('ScoutCardGet',(u'スカウト(カード獲得)',self.procScout)),
            ('ScoutItemGet',(u'スカウト(アイテム獲得)',self.procScout)),
            ('ScoutHappening',(u'スカウト(ハプニング発生)',self.procScout)),
            ('ScoutResultHappening',(u'超太客来店',self.procScoutResultHappening)),
            ('ScoutResultComplete',(u'スカウト完了',self.procScoutResultComplete)),
            ('Opening',(u'オープニング', self.procOpening)),
            ('LoginBonus',(u'ログインボーナス', self.procLoginBonus)),
            ('LongLoginBonus',(u'ロングログインボーナス', self.procLongLoginBonus)),
            ('LoginStamp',(u'ログインスタンプ', self.procLoginStamp)),
            ('MonthlyLoginEnd',(u'月末ログインボーナス(次無し)', self.procMonthlyLoginEnd)),
            ('MonthlyLogin',(u'月末ログインボーナス(次有り)', self.procMonthlyLogin)),
            ('CountDownLogin',(u'CDログインボーナス', self.procCountDownLogin)),
            ('CountdownLogin2ndAnniversary',(u'2周年CDログインボーナス', self.procCountdownLogin2ndAnniversary)),
            ('CountdownLogin3rdAnniversary',(u'3周年CDログインボーナス', self.procCountdownLogin3rdAnniversary)),
            ('EndOfYearCountdown',(u'年末CDLB 2015->2016', self.procEndOfYearCountdown)),
            ('Login2ndAnniversary',(u'2周年ログインボーナス', self.procLogin2ndAnniversary)),
            ('Login3rdAnniversary',(u'3周年ログインボーナス', self.procLogin3rdAnniversary)),
            ('NewYearLogin',(u'年始ログインボーナス', self.procNewYearLogin)),
            ('HinamatsuriLogin',(u'雛祭りログインボーナス', self.procHinamatsuriLogin)),
            ('NewbieLogin',(u'初心者ログインボーナス', self.procNewbieLogin)),
            ('Valentine2016Login',(u'バレンタインログイン', self.procValentine2016Login)),
            ('BossEncount',(u'ボス戦出現', self.procBossEncount)),
            ('BossBattleWin',(u'ボス戦(勝利)', self.procBossBattleWin)),
            ('BossBattleLose',(u'ボス戦(敗北)', self.procBossBattleLose)),
            ('GachaNormal',(u'ガチャ(通常)', self.procGachaNormal)),
            ('GachaGold',(u'ガチャ(金)', self.procGachaGold)),
            ('GachaRank',(u'ガチャ(ランキング)', self.procGachaRank)),
            ('GachaSheet',(u'シートガチャ', self.procGachaSheet)),
            ('GachaChristmas',(u'クリスマスガチャ', self.procGachaChristmas)),
            ('GachaXmas2015',(u'Xmasガチャ2015', self.procGachaXmas2015)),
            ('GachaFukubukuro',(u'福袋ガチャ', self.procGachaFukubukuro)),
            ('GachaFukubukuro2016',(u'福袋ガチャ2016', self.procGachaFukubukuro2016)),
            ('GachaFukubukuro201604',(u'福袋ガチャ201604', self.procGachaFukubukuro201604)),
            ('GachaFukubukuro201605',(u'福袋ガチャ201605', self.procGachaFukubukuro201605)),
            ('GachaFukubukuro201605r',(u'福袋ガチャ201605r', self.procGachaFukubukuro201605r)),
            ('GachaFukubukuro201607',(u'福袋ガチャ201607', self.procGachaFukubukuro201607)),
            ('GachaFukubukuro201608',(u'福袋ガチャ201608', self.procGachaFukubukuro201608)),
            ('GachaFukubukuro201701',(u'福袋ガチャ201701', self.procGachaFukubukuro201701)),
            ('GachaScev',(u'スカウトイベントガチャ', self.procGachaScev)),
            ('GachaCastMedal',(u'キャストメダルガチャ', self.procGachaCastMedal)),
            ('GachaMoreCast',(u'追加キャスト', self.procGachaMoreCast)),
            ('EventHappening',(u'レイドイベント超太客来店', self.procEventHappening)),
            ('BigBoss',(u'レイドイベント大ボス', self.procBigBoss)),
            ('BigBoss2',(u'レイドイベント大ボス2', self.procBigBoss2)),
            ('ChampagneCall',(u'SHOWTIME', self.procChampagneCall)),
            ('ScoutEventNone',(u'ｽｶｳﾄ[ｲﾍﾞ](なにもなかった)',self.procScoutEvent)),
            ('ScoutEventComplete',(u'ｽｶｳﾄ[ｲﾍﾞ](完了)',self.procScoutEvent)),
            ('ScoutEventApNone',(u'ｽｶｳﾄ[ｲﾍﾞ](行動力が足りない)',self.procScoutEvent)),
            ('ScoutEventLevelup',(u'ｽｶｳﾄ[ｲﾍﾞ](レベルアップ)',self.procScoutEvent)),
            ('ScoutEventTreasureGet',(u'ｽｶｳﾄ[ｲﾍﾞ](宝箱獲得)',self.procScoutEvent)),
            ('ScoutEventCardGet',(u'ｽｶｳﾄ[ｲﾍﾞ](カード獲得)',self.procScoutEvent)),
            ('ScoutEventItemGet',(u'ｽｶｳﾄ[ｲﾍﾞ](アイテム獲得)',self.procScoutEvent)),
            ('ScoutEventHappening',(u'ｽｶｳﾄ[ｲﾍﾞ](ハプニング発生)',self.procScoutEvent)),
            ('ScoutEventFever',(u'ｽｶｳﾄ[ｲﾍﾞ]フィーバー発生',self.procScoutEventFever)),
            ('ScoutEventLoveTime',(u'ｽｶｳﾄ[ｲﾍﾞ]逢引ラブタイム七夕',self.procScoutEventLoveTime)),
            ('ScoutEventLoveTime2',(u'ｽｶｳﾄ[ｲﾍﾞ]逢引ラブタイム通常',self.procScoutEventLoveTime2)),
            ('BattleEventResult',(u'ﾊﾞﾄﾙ[ｲﾍﾞ]結果報告', self.procBattleEventResult)),
            ('BattleEventTree',(u'ﾊﾞﾄﾙ[ｲﾍﾞ]お酒', self.procBattleEventTree)),
            ('BattleEventPieceComplete',(u'ﾊﾞﾄﾙ[ｲﾍﾞ]ピースコンプ', self.procBattleEventPieceComplete)),
            ('ComeBackCampaign',(u'カムバックキャンペーン', self.procComeBackCampaign)),
            ('GoukonEventNakaoshi',(u'合ｺﾝ[ｲﾍﾞ]中押し', self.procGoukonEventNakaoshi)),
            ('PanelMission',(u'パネルミッション', self.procPanelMission)),
            ('EventScenario',(u'イベントシナリオ',self.procEventScenario)),
            ('CabaClubEventAnim',(u'経営イベント発生',self.procCabaClubEventAnim)),
            ('CabaClubResultAnim',(u'経営結果',self.procCabaClubResultAnim)),
            ('SugorokuLogin',(u'双六ログイン',self.procSugorokuLogin)),
            ('SugorokuLoginLoop',(u'双六ログイン(ゴール無し)',self.procSugorokuLoginLoop)),
            ('ProduceEventHappening', (u'ﾌﾟﾛﾃﾞｭｰｽ[ｲﾍﾞ]太客来店', self.procProduceEventHappening)),
            ('ProduceEventHappeningBigBoss', (u'ﾌﾟﾛﾃﾞｭｰｽ[ｲﾍﾞ]超太客来店', self.procProduceEventHappeningBigBoss)),
            ('ProduceEventRarityUp', (u'ﾌﾟﾛﾃﾞｭｰｽ[ｲﾍﾞ]レア度上昇', self.procProduceEventRarityUp)),
            ('ProduceEventLastCastGet', (u'ﾌﾟﾛﾃﾞｭｰｽ[ｲﾍﾞ]Last card get', self.procProduceEventLastCastGet)),
            ('ProduceEventBossBattleWin', (u'ﾌﾟﾛﾃﾞｭｰｽ[ｲﾍﾞ]ボス戦(勝利)', self.procProduceEventBossBattleWin)),
            ('ProduceEventBossBattleLose', (u'ﾌﾟﾛﾃﾞｭｰｽ[ｲﾍﾞ]ボス戦(敗北)', self.procProduceEventBossBattleLose)),
            ('ProduceEventBossBattleBigWin', (u'ﾌﾟﾛﾃﾞｭｰｽ[ｲﾍﾞ]ボス戦(大成功)', self.procProduceEventBossBattleBigWin)),
            
            ('GachaNormalParam',(u'ガチャ(通常)', self.procGachaNormalParam)),
            ('GachaGoldParam',(u'ガチャ(金)', self.procGachaGoldParam)),
            ('GachaRankParam',(u'ガチャ(ランキング)', self.procGachaRankParam)),
            ('GachaChristmasParam',(u'クリスマスガチャ', self.procGachaChristmasParam)),
            ('GachaXmas2015Param',(u'Xmasガチャ2015', self.procGachaXmas2015Param)),
            ('GachaFukubukuro2016Param',(u'福袋ガチャ', self.procGachaFukubukuro2016Param)),
            ('GachaFukubukuro201604Param',(u'福袋ガチャ201604', self.procGachaFukubukuro201604Param)),
            ('GachaFukubukuro201605Param',(u'福袋ガチャ201605', self.procGachaFukubukuro201605Param)),
            ('GachaFukubukuro201605rParam',(u'福袋ガチャ201605r', self.procGachaFukubukuro201605rParam)),
            ('GachaFukubukuro201607Param',(u'福袋ガチャ201607', self.procGachaFukubukuro201607Param)),
            ('GachaFukubukuro201608Param',(u'福袋ガチャ201608', self.procGachaFukubukuro201608Param)),
            ('GachaFukubukuro201701Param',(u'福袋ガチャ201701', self.procGachaFukubukuro201701Param)),
            ('GachaScevParam',(u'スカウトイベントガチャ', self.procGachaScevParam)),
            ('GachaCastMedalParam',(u'キャストメダルガチャ', self.procGachaCastMedalParam)),
            ('GachaMoreCastParam',(u'追加キャスト', self.procGachaMoreCastParam)),
            ('BattleParam',(u'バトルパラメータ取得', self.procBattleParam)),
            ('ScoutNoneParam',(u'スカウト(なにもなかった)',self.procScoutNone)),
            ('ScoutCompleteParam',(u'スカウト(完了)',self.procScoutComplete)),
            ('ScoutApNoneParam',(u'スカウト(行動力が足りない)',self.procScoutApNone)),
            ('ScoutLevelupParam',(u'スカウト(レベルアップ)',self.procScoutLevelup)),
            ('ScoutTreasureGetParam',(u'スカウト(宝箱獲得)',self.procScoutTreasureGet)),
            ('ScoutCardGetParam',(u'スカウト(カード獲得)',self.procScoutCardGet)),
            ('ScoutItemGetParam',(u'スカウト(アイテム獲得)',self.procScoutItemGet)),
            ('ScoutHappeningParam',(u'スカウト(ハプニング発生)',self.procScoutHappening)),
            ('PanelMissionParam',(u'パネルミッション', self.procPanelMissionParam)),
            ('ScoutEventNoneParam',(u'ｽｶｳﾄ[ｲﾍﾞ](なにもなかった)',self.procScoutEventNone)),
            ('ScoutEventCompleteParam',(u'ｽｶｳﾄ[ｲﾍﾞ](完了)',self.procScoutEventComplete)),
            ('ScoutEventApNoneParam',(u'ｽｶｳﾄ[ｲﾍﾞ](行動力が足りない)',self.procScoutEventApNone)),
            ('ScoutEventLevelupParam',(u'ｽｶｳﾄ[ｲﾍﾞ](レベルアップ)',self.procScoutEventLevelup)),
            ('ScoutEventTreasureGetParam',(u'ｽｶｳﾄ[ｲﾍﾞ](宝箱獲得)',self.procScoutEventTreasureGet)),
            ('ScoutEventCardGetParam',(u'ｽｶｳﾄ[ｲﾍﾞ](カード獲得)',self.procScoutEventCardGet)),
            ('ScoutEventItemGetParam',(u'ｽｶｳﾄ[ｲﾍﾞ](アイテム獲得)',self.procScoutEventItemGet)),
            ('ScoutEventHappeningParam',(u'ｽｶｳﾄ[ｲﾍﾞ](ハプニング発生)',self.procScoutEventHappening)),
            ('CountDownLoginParam',(u'CDログインボーナス', self.procCountDownLoginParam)),
            ('CountdownLogin2ndAnniversaryParam',(u'CD2ログインボーナス', self.procCountdownLogin2ndAnniversaryParam)),
            ('CountdownLogin3rdAnniversaryParam',(u'CD3ログインボーナス', self.procCountdownLogin3rdAnniversaryParam)),
            ('EndOfYearCountdownParam',(u'CD2ログインボーナス', self.procEndOfYearCountdownParam)),
            ('Login2ndAnniversaryParam',(u'2周年ログインボーナス', self.procLogin2ndAnniversaryParam)),
            ('Login3rdAnniversaryParam',(u'3周年ログインボーナス', self.procLogin3rdAnniversaryParam)),
            ('NewYearLoginParam',(u'年始ログインボーナス', self.procNewYearLoginParam)),
            ('EventScenarioParam',(u'イベントシナリオ',self.procEventScenarioParam)),
            ('HinamatsuriLoginParam',(u'雛祭りログインボーナス', self.procHinamatsuriLoginParam)),
            ('NewbieLoginParam',(u'初心者ログインボーナス', self.procNewbieLoginParam)),
            ('Valentine2016LoginParam',(u'バレンタインボーナス', self.procValentine2016LoginParam)),
            ('SugorokuLoginParam',(u'双六ログイン',self.procSugorokuLoginParam)),
            ('SugorokuLoginLoopParam',(u'双六ログイン',self.procSugorokuLoginLoopParam)),
        )
        TABLE_DICT = dict(TABLE)
        html5name = args.get(0, None)

        if html5name:
            v = TABLE_DICT.get(html5name)
            if v:
                v[1]()
                return
        
        url_format = '/html5_test/%s'
        
        FORMS = {
#            'ScoutEventScenario' : (
#                {'name':'_scn', 'value':1, 'choice':range(1, 6+1)},
#            ),
            'MonthlyLogin' : (
                {'name':'_cnt', 'value':1, 'choice':range(3)},
                {'name':'_idxnext', 'value':1, 'choice':range(3)},
            ),
            'MonthlyLoginEnd' : (
                {'name':'_cnt', 'value':1, 'choice':range(3)},
            ),
            'PanelMission' : (
                {'name':'_p0', 'value':'open', 'choice':['none','open','opened']},
                {'name':'_p1', 'value':'open', 'choice':['none','open','opened']},
                {'name':'_p2', 'value':'open', 'choice':['none','open','opened'], 'br':True},
                {'name':'_p3', 'value':'open', 'choice':['none','open','opened']},
                {'name':'_p4', 'value':'open', 'choice':['none','open','opened']},
                {'name':'_p5', 'value':'open', 'choice':['none','open','opened'], 'br':True},
                {'name':'_p6', 'value':'open', 'choice':['none','open','opened']},
                {'name':'_p7', 'value':'open', 'choice':['none','open','opened']},
                {'name':'_p8', 'value':'open', 'choice':['none','open','opened'], 'br':True},
                {'name':'_next', 'value':'last', 'choice':['last',' ']},
            ),
            'CountDownLogin' : (
                {'name':'_f0', 'value':0, 'choice':range(2)},
                {'name':'_f1', 'value':0, 'choice':range(2)},
                {'name':'_f2', 'value':0, 'choice':range(2), 'br':True},
                {'name':'_f3', 'value':0, 'choice':range(2)},
                {'name':'_f4', 'value':0, 'choice':range(2)},
                {'name':'_f5', 'value':0, 'choice':range(2), 'br':True},
                {'name':'_day', 'value':1, 'choice':range(1, 7)},
            ),
            'CountdownLogin2ndAnniversary' : (
                {'name':'_f0', 'value':0, 'choice':range(2)},
                {'name':'_f1', 'value':0, 'choice':range(2)},
                {'name':'_f2', 'value':0, 'choice':range(2)},
                {'name':'_f3', 'value':0, 'choice':range(2), 'br':True},
                {'name':'_day', 'value':11, 'choice':range(11, 26)},
            ),
            'CountdownLogin3rdAnniversary': (
                {'name': '_f0', 'value': 0, 'choice': range(2)},
                {'name': '_f1', 'value': 0, 'choice': range(2)},
                {'name': '_f2', 'value': 0, 'choice': range(2)},
                {'name': '_f3', 'value': 0, 'choice': range(2), 'br': True},
                {'name': '_day', 'value': 19, 'choice': range(19, 26)},
            ),
            'EndOfYearCountdown' : (
                {'name':'_f0', 'value':0, 'choice':range(2)},
                {'name':'_f1', 'value':0, 'choice':range(2)},
                {'name':'_f2', 'value':0, 'choice':range(2), 'br':True},
                {'name':'_day', 'value':29, 'choice':range(29, 32)},
            ),
            'Login2ndAnniversary' : (
                {'name':'_f0', 'value':0, 'choice':range(2)},
                {'name':'_f1', 'value':0, 'choice':range(2)},
                {'name':'_f2', 'value':0, 'choice':range(2)},
                {'name':'_f3', 'value':0, 'choice':range(2), 'br':True},
                {'name':'_day', 'value':26, 'choice':range(26, 32)},
            ),
            'Login3rdAnniversary' : (
                {'name': '_f0', 'value': 0, 'choice': range(2)},
                {'name': '_f1', 'value': 0, 'choice': range(2)},
                {'name': '_f2', 'value': 0, 'choice': range(2)},
                {'name': '_f3', 'value': 0, 'choice': range(2), 'br': True},
                {'name': '_day', 'value': 26, 'choice': range(26, 32)},
            ),
            'NewYearLogin' : (
                {'name':'_idx', 'value':1, 'choice':range(1, 8)},
            ),
            'HinamatsuriLogin' : (
                {'name':'_f0', 'value':0, 'choice':range(2)},
                {'name':'_f1', 'value':0, 'choice':range(2)},
                {'name':'_f2', 'value':0, 'choice':range(2)},
                {'name':'_f3', 'value':0, 'choice':range(2), 'br':True},
                {'name':'_idx', 'value':1, 'choice':range(1, 5)},
            ),
            'NewbieLogin' : (
                {'name':'_bg', 'choice':['syosinsya_lb_182_01', 'syosinsya_lb_182_02', 'syosinsya_lb_182_03', 'syosinsya_lb_182_04'], 'br':True},
                {'name':'_ix', 'value':80},
                {'name':'_iy', 'value':200, 'br':True},
                {'name':'_idx', 'value':1, 'choice':range(1, 8)},
            ),
            'Valentine2016Login' : (
                {'name':'_f0', 'value':0, 'choice':range(2)},
                {'name':'_f1', 'value':0, 'choice':range(2)},
                {'name':'_f2', 'value':0, 'choice':range(2), 'br':True},
                {'name':'_f3', 'value':0, 'choice':range(2)},
                {'name':'_f4', 'value':0, 'choice':range(2)},
                {'name':'_f5', 'value':0, 'choice':range(2), 'br':True},
                {'name':'_day', 'value':1, 'choice':range(1, 7)},
            ),
            'GachaXmas2015' : (
                {'name':'_cnt', 'value':5, 'choice':[5, 10]},
            ),
            'GachaFukubukuro' : (
                {'name':'_cnt', 'value':10, 'choice':[5, 10, 20, 40]},
            ),
            'GachaFukubukuro2016' : (
                {'name':'_cnt', 'value':10, 'choice':[5, 10, 20, 40]},
            ),
            'GachaFukubukuro201604' : (
                {'name':'_cnt', 'value':10, 'choice':[10, 15, 30]},
            ),
            'GachaFukubukuro201605' : (
                {'name':'_cnt', 'value':10, 'choice':[10, 15, 30]},
            ),
            'GachaFukubukuro201605r' : (
                {'name':'_cnt', 'value':10, 'choice':[10, 15, 30]},
            ),
            'GachaFukubukuro201607' : (
                {'name':'_cnt', 'value':10, 'choice':[10, 15, 30]},
            ),
            'GachaFukubukuro201608': (
                {'name': '_cnt', 'value': 10, 'choice': [10, 15, 30]},
            ),
            'GachaFukubukuro201701': (
                {'name': '_cnt', 'value': 10, 'choice': [10, 15, 30]},
            ),
            'GachaScev' : (
                {'name':'_rare', 'value':Defines.Rarity.NORMAL, 'choice':Defines.Rarity.LIST},
            ),
            'GachaCastMedal' : (
                {'name':'_num', 'value':1, 'choice':range(1, 11)},
            ),
            'EventScenario' : (
                {'name':'_scn', 'value':0},
                {'name':'_last', 'value':'', 'choice':['normal', 'last']},
            ),
            'BattleEventTree' : (
                {'name':'_item', 'value':'beer', 'choice':['beer', 'red_wine', 'dom_perignon']},
            ),
            'EventHappening' : (
                {'name':'_boss', 'value':'beer', 'choice':['boss%d' % (i+1) for i in xrange(6)]},
            ),
            'CabaClubResultAnim' : (
                {'name':'_cast', 'value':1, 'choice':range(1, 4)},
            ),
            'SugorokuLogin' : (
                {'name':'_ope', 'value':'none', 'choice':['none','item','go_1','go_2','back_1','back_2','lose_turn','back_to_start','rest','completed']},
            ),
            'SugorokuLoginLoop' : (
                {'name':'_ope', 'value':'none', 'choice':['none','item','go_1','go_2','back_1','back_2','lose_turn','back_to_start','rest','completed']},
            ),
        }
        
        IGNORES = [
            'BattleParam',
            'ScoutNoneParam',
            'ScoutCompleteParam',
            'ScoutApNoneParam',
            'ScoutLevelupParam',
            'ScoutTreasureGetParam',
            'ScoutCardGetParam',
            'ScoutItemGetParam',
            'ScoutHappeningParam',
            'PanelMissionParam',
            'ScoutEventNoneParam',
            'ScoutEventCompleteParam',
            'ScoutEventApNoneParam',
            'ScoutEventLevelupParam',
            'ScoutEventTreasureGetParam',
            'ScoutEventCardGetParam',
            'ScoutEventHappeningParam',
            'GachaNormalParam',
            'GachaGoldParam',
            'GachaRankParam',
            'GachaChristmasParam',
            'GachaXmas2015Param',
            'CountDownLoginParam',
            'CountdownLogin2ndAnniversaryParam',
            'EndOfYearCountdownParam',
            'Login2ndAnniversaryParam',
            'NewYearLoginParam',
            'ValentineLoginParam',
            'GachaXmas2015Param',
            'GachaFukubukuroParam',
            'GachaFukubukuro2016Param',
            'GachaFukubukuro201604Param',
            'GachaFukubukuro201605Param',
            'GachaFukubukuro201605rParam',
            'GachaFukubukuro201607Param',
            'GachaFukubukuro201608Param',
            'GachaScevParam',
            'GachaCastMedalParam',
            'EventScenarioParam',
            'HinamatsuriLoginParam',
            'NewbieLoginParam',
            'SugorokuLoginParam',
            'SugorokuLoginLoopParam',
        ]
        
        html5list = []
        for key, value in TABLE:
            if key in IGNORES:
                continue
            name = value[0]
            
            html5list.append({
                'name' : name,
                'url' : self.makeAppLinkUrl(url_format % key),
                'form' : FORMS.get(key),
            })
        self.html_param['html5list'] = html5list
        self.osa_util.write_html('test/html5_test.html', self.html_param)
    
    def writeDataResponseBody(self, params):
        if self.isUsePCEffect():
            body = Json.encode({
                'flashVars' : self.makeFlashVars(params)
            })
        else:
            body = Json.encode(params)
        self.response.set_header('Content-Type', 'plain/text')
        self.response.set_status(200)
        self.response.send(body)
    
    def procIfTest(self):
        """IF試験用.
        """
        effectpath = 'test/effectPage.html'
        params = {
            'img2':self.makeAppLinkUrlImg('01/scout_main_photo.png'),
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procLevelup(self):
        """レベルアップ演出.
        """
        effectpath = 'levelup/effect.html'
        params = {
            'statusText':u"レベルが2にあがった\n体力が10にあがった",
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procEvolution(self):
        """ハメ管理演出.
        """
        effectpath = 'gousei/effect.html'
        params = {
            'card1':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'card2':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'mixCard':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'startText':u'あいうえお\nかきくけこ',
            'endText':u'さしすせそたちつてとなにぬねのはひふへほ\nさしすせそたちつてとなにぬねのはひふへほ',
            'endText2':u'まみむめもやゆよ\nらりるれろわをん',
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'miniCard1':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'miniCard2':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procComposition(self):
        """教育演出.
        """
        effectpath = 'education/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'baseText' : Defines.EffectTextFormat.EDUCATION_BASETEXT % self.__dummycard.name,
            'trainerText' : Defines.EffectTextFormat.EDUCATION_TRAINERTEXT,
            'lastText1' : Defines.EffectTextFormat.EDUCATION_LASTTEXT1 % self.__dummycard.name,
            'lastText2' : Defines.EffectTextFormat.EDUCATION_LASTTEXT2 % (self.__dummycard.name, 1000),
            'levelupCount' : 1,
            'serviceFlag' : 1,
            'serviceText' : Defines.EffectTextFormat.EDUCATION_SERVICETEXT % u'上目使い',
            'greatFlag' : 0,
            'levelGauge' : Defines.ANIMATION_SEPARATE_STRING.join(['50', '75']),
            'baseImage':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'subImage1':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'subImage2':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'subImage3':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'subImage4':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'subImage5':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'subImage6':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'subImage7':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'subImage8':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'subImage9':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procBattle(self):
        """バトル演出.
        """
        effectpath = 'battle2/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/BattleParam/')
        self.appRedirectToEffect2(effectpath, dataUrl)
    
    def procBattleParam(self):
        """バトル演出パラメータ.
        """
        params = {
            'feverFlag' : 1,
            'eSale' : 1000,
            'pSale' : 1000,
            'pCard1' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'pCard2' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'pCard3' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'pCard4' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'pCard5' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'pCard6' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'pCard7' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'pCard8' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'pCard9' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'pCard10' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'eCard1' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'eCard2' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'eCard3' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'eCard4' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'eCard5' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'eCard6' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'eCard7' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'eCard8' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'eCard9' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'eCard10' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'pSkillCount' : 3,
            'eSkillCount' : 3,
            'pSkillUseChara' : u"1:2:3:4:5:6:7:8:9:10",
            'pPlayerFlag' : u"0:1:0:1:0:1:0:1:0:1",
            'pDownFlag' : u"0:1:0:1:0:1:0:1:0:1",
            'pSkillKind' : u"0:1:2:3:4:5:6:7:8:9",
            'pSkillNum' : u"10:10:10:10:10:10:10:10:10:10",
            'pSkillIndex' : u"1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10",
            'pSkillName' : u"スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ",
            'pSkillText' : u"相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!",
            'pSkillValue' : u'100:200:300:400:500:600:700:800:900:1000',
            'eSkillUseChara' : u"1:2:3:4:5:6:7:8:9:10",
            'ePlayerFlag' : u"0:1:0:1:0:1:0:1:0:1",
            'eDownFlag' : u"0:1:0:1:0:1:0:1:0:1",
            'eSkillKind' : u"0:1:2:3:4:5:6:7:8:9",
            'eSkillNum' : u"10:10:10:10:10:10:10:10:10:10",
            'eSkillIndex' : u"1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10:1,2,3,4,5,6,7,8,9,10",
            'eSkillName' : u"スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ:スーパーゴーストカミカゼアタック__COLON__ギャラクティカドーナツ",
            'eSkillText' : u"相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!:相手の攻撃力を大幅DOWNッッッ!!",
            'eSkillValue' : u'100:200:300:400:500:600:700:800:900:1000',
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.writeDataResponseBody(params)
    
    def procWin1(self):
        """勝利(ノルマクリア)演出.
        """
        effectpath = 'normaclear/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procWin2(self):
        """勝利(You Win)演出.
        """
        effectpath = 'youwin/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procWin3(self):
        """勝利(出店完了)演出.
        """
        effectpath = 'shuttenkanryou/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procLose(self):
        """敗北演出.
        """
        effectpath = 'youlose/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procLevelupSample(self):
        """レベルアップ演出(サンプル).
        """
        effectpath = 'sample/levelup.html'
        self.appRedirectToEffect(effectpath)
    
    def procEvolutionSample(self):
        """ハメ管理演出(サンプル).
        """
        effectpath = 'sample/gousei.html'
        self.appRedirectToEffect(effectpath)
    
    def __procScoutParam(self, eventKind=Defines.ScoutEventType.DEFAULT_ANIMATION_EVENT_TEXT_NONE, eventText=None, **kwargs):
        """スカウト.
        """
        if eventKind == Defines.ScoutEventType.DEFAULT_ANIMATION_EVENT_TEXT_NONE and eventText:
            eventKind = Defines.ScoutEventType.DEFAULT_ANIMATION_EVENT_WITH_TEXT
        elif eventKind == Defines.ScoutEventType.DEFAULT_ANIMATION_EVENT_WITH_TEXT and not eventText:
            eventKind = Defines.ScoutEventType.DEFAULT_ANIMATION_EVENT_TEXT_NONE
        
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'backImage' : self.makeAppLinkUrlImg('area/Area03.png'),
            'eventKind' : eventKind,
            'scoutNum' : 3,
            'charText' : u'続ける1:続ける2:続ける3',
            'cgText' : u'0:1:2',
            'expText' : u'exp10↑:exp9↑:exp8↑',
            'progressGauge' : u'0:33:67:100',
            'hpGauge' : u'100:90:80:70',
            'expGauge' : u'0:10:20:30',
        }
        if eventText:
            params['eventText'] = eventText
        params.update(kwargs)
        self.writeDataResponseBody(params)
    
    def __procScoutStart(self, effectname=None):
        """スカウト.
        """
        args = self.getUrlArgs('/html5_test/')
        effectpath = '%s/effect2.html' % (effectname or 'scout')
        dataUrl = self.makeAppLinkUrl('/html5_test/%sParam/' % args.get(0))
        self.appRedirectToEffect2(effectpath, dataUrl)
    
    def procScout(self):
        """スカウト.
        """
        self.__procScoutStart()
    
    def procScoutNone(self):
        """スカウト(なにもなかった).
        """
        self.__procScoutParam()
    
    def procScoutComplete(self):
        """スカウト(完了).
        """
        params = {
            'hpGauge' : u'30:20:10:0',
            'eventText' : u'なにか起こりそう',
        }
        self.__procScoutParam(**params)
    
    def procScoutApNone(self):
        """スカウト(行動力が足りない).
        """
        params = {
            'hpGauge' : u'30:20:10:0',
            'eventText' : u'体力がなくなった',
        }
        self.__procScoutParam(**params)
    
    def procScoutLevelup(self):
        """スカウト(レベルアップ).
        """
        params = {
            'expGauge' : u'70:80:90:100',
            'eventText' : u'経験値が満タンになった',
        }
        self.__procScoutParam(Defines.ScoutEventType.LEVELUP, **params)
    
    def procScoutTreasureGet(self):
        """スカウト(宝箱獲得).
        """
        params = {
            'eventImage' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlMiddleByTreasureType(Defines.TreasureType.GOLD)),
            'eventText' : u'なにか見つけた',
        }
        self.__procScoutParam(Defines.ScoutEventType.GET_TREASURE, **params)
    
    def procScoutCardGet(self):
        """スカウト(カード獲得).
        """
        params = {
            'eventText' : u'誰かいる',
        }
        self.__procScoutParam(Defines.ScoutEventType.GET_CARD, **params)
    
    def procScoutItemGet(self):
        """スカウト(アイテム獲得).
        """
        params = {
            'eventText' : u'なにか見つけた',
        }
        self.__procScoutParam(Defines.ScoutEventType.GET_ITEM, **params)
    
    def procScoutHappening(self):
        """スカウト(ハプニング発生).
        """
        params = {
            'eventText' : u'電話だ',
        }
        self.__procScoutParam(Defines.ScoutEventType.HAPPENING, **params)
    
    
    def procScoutResultHappening(self):
        """スカウト(ハプニング発生).
        """
        effectpath = 'chohutokyaku/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procScoutResultComplete(self):
        """スカウト完了.
        """
        effectpath = 'scoutclear/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'text' : Defines.EffectTextFormat.SCOUTRESULT_COMPLETE_TEXT,
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procOpening(self):
        """オープニング.
        """
        effectpath = 'op/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procLoginBonus(self):
        """ログインボーナス.
        """
        effectpath = 'login/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'stampNum' : 3,
            'itemPosition' : Defines.ANIMATION_SEPARATE_STRING.join([str(i+1) for i in xrange(12)]),
            'text1' : u'連続ログイン10日達成だよ♪',
            'text2' : u'1000PM受け取ってね',
            'text3' : u'明日もログインすると○○がもらえるよ',
            'itemImage1' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD)),
            'itemImage2' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT)),
            'itemImage3' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET)),
            'itemImage4' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHATICKET)),
            'itemImage5' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLDKEY)),
            'itemImage6' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.SILVERKEY)),
            'itemImage7' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.CABARETKING_TREASURE)),
            'itemImage8' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.TRYLUCKTICKET)),
            'itemImage9' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD)),
            'itemImage10' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT)),
            'itemImage11' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET)),
            'itemImage12' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHATICKET)),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procLoginStamp(self):
        """ログインスタンプ.
        """
        effectpath = 'loginstamp2/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'stampNum' : 14,
            'itemPosition' : Defines.ANIMATION_SEPARATE_STRING.join([str(i+1) for i in xrange(15)]),
            'text1' : u'累計ログイン12日達成だよ♪',
            'text2' : u'1000PM受け取ってね',
            'text3' : u'明日もログインすると○○がもらえるよ',
            'pre' : self.url_static_img,
            'itemImage1' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
            'itemImage2' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
            'itemImage3' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET),
            'itemImage4' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHATICKET),
            'itemImage5' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLDKEY),
            'itemImage6' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.SILVERKEY),
            'itemImage7' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.CABARETKING_TREASURE),
            'itemImage8' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.TRYLUCKTICKET),
            'itemImage9' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
            'itemImage10' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
            'itemImage11' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET),
            'itemImage12' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHATICKET),
            'itemImage13' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET),
            'itemImage14' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
            'itemImage15' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procMonthlyLogin(self):
        """月末ログインボーナス.
        """
        effectpath = 'monthly_login/effect.html'
        idx = int(self.request.get('_cnt') or 0)
        idxnext = int(self.request.get('_idxnext') or 0)
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img,
            'i0' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
            'i1' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
            'i2' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
            'idx' : idx,
            'idxnext' : idxnext,
            'td' : OSAUtil.get_now().day,
            'tt' : u'本日のアイテム名',
            'nt' : u'明日のアイテム名',
            'logoPre' : self.url_static + 'effect/sp/v2/monthly_login/data/default/',
            'rouletteCnt' : 9 + idx,
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procCountDownLogin(self):
        """カウントダウンログイン.
        """
        arr = [str(self.request.get('_day')) or '1']
        arr.extend([(self.request.get('_f%d' % i) or '0') for i in xrange(6)])
        effectpath = 'countdown_login/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/CountDownLoginParam/%s' % ('/'.join(arr)))
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procCountdownLogin2ndAnniversary(self):
        """2周年記念カウントダウンログイン
        """
        arr = [str(self.request.get('_day')) or '11']
        arr.extend([(self.request.get('_f%d' % i) or '0') for i in xrange(6)])
        effectpath = 'countdown_login_2ndanniversary/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/CountdownLogin2ndAnniversaryParam/%s' % ('/'.join(arr)))
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procCountdownLogin3rdAnniversary(self):
        """2周年記念カウントダウンログイン
        """
        arr = [str(self.request.get('_day')) or '19']
        arr.extend([(self.request.get('_f%d' % i) or '0') for i in xrange(6)])
        effectpath = 'countdown_login_3rdanniversary/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/CountdownLogin3rdAnniversaryParam/%s' % ('/'.join(arr)))
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procEndOfYearCountdown(self):
        """年末カウントダウンログイン 2015->2016ver.
        """
        arr = [str(self.request.get('_day')) or '29']
        arr.extend([(self.request.get('_f%d' % i) or '0') for i in xrange(3)])
        effectpath = 'end_of_year_countdown/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/EndOfYearCountdownParam/%s' % ('/'.join(arr)))
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procLogin2ndAnniversary(self):
        """2周年記念ログインボーナス
        """
        arr = [str(self.request.get('_day')) or '1']
        arr.extend([(self.request.get('_f%d' % i) or '0') for i in xrange(6)])
        effectpath = '2nd_anniversary_login/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/Login2ndAnniversaryParam/%s' % ('/'.join(arr)))
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procLogin3rdAnniversary(self):
        """2周年記念ログインボーナス
        """
        arr = [str(self.request.get('_day')) or '1']
        arr.extend([(self.request.get('_f%d' % i) or '0') for i in xrange(6)])
        effectpath = '3rd_anniversary_login/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/Login3rdAnniversaryParam/%s' % ('/'.join(arr)))
        self.appRedirectToEffect2(effectpath, dataUrl)
    
    def procNewYearLogin(self):
        """年始ログイン.
        """
        idx = self.request.get('_idx') or 1
        effectpath = 'newyear_login/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/NewYearLoginParam/%s' % idx)
        self.appRedirectToEffect2(effectpath, dataUrl)
    
    def procHinamatsuriLogin(self):
        """雛祭りログイン.
        """
        arr = [(self.request.get('_f%d' % i) or '0') for i in xrange(4)]
        idx = self.request.get('_idx') or 0
        effectpath = 'hinamatsuri_login/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/HinamatsuriLoginParam/%s/%s' % (idx, '/'.join(arr)))
        self.appRedirectToEffect2(effectpath, dataUrl)
    
    def procNewbieLogin(self):
        """初心者限定ログインボーナス.
        """
        idx = self.request.get('_idx') or 1
        ix = self.request.get('_ix') or -1
        iy = self.request.get('_iy') or -1
        bg = self.request.get('_bg') or 'bg'
        effectpath = 'newbie_login/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/NewbieLoginParam/%s/%s/%s/%s' % (idx, ix, iy, bg))
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procValentine2016Login(self):
        """バレンタインログイン.
        """
        arr = [str(self.request.get('_day')) or '1']
        arr.extend([(self.request.get('_f%d' % i) or '0') for i in xrange(6)])
        effectpath = 'valentine2016/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/Valentine2016LoginParam/%s' % ('/'.join(arr)))
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procValentine2016LoginParam(self):
        """カウントダウンログインのパラメータ.
        """
        args = self.getUrlArgs('/html5_test/Valentine2016LoginParam/')
        idx = (args.getInt(0) or 1) - 1
        day = 6 - (idx + 1)

        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img,
            "i0": "item/ticket_koakuma/Item_thumb_60_60.png", 
            "i1": "item/ticket_chiteki/Item_thumb_60_60.png", 
            "i2": "item/ticket_iyashi/Item_thumb_60_60.png", 
            "i3": "gacha/ticket/gachaticket_hr_1.png", 
            "i4": "gacha/ticket/gachaticket_sr_1.png", 
            "i5": "item/ring_diamond/Item_thumb_60_60.png", 
            "t0": "オーナー！バレンタインですね！なんかワクワクしませんか？",
            "t1": "チョコばかりだと飽きちゃいません？変わった物も欲しいですよね〜？",
            "t2": "だから今日は「__ITEM__」あげます！",
            "t3": "次も来てくれたら「__NEXT__」あげちゃいますからね♪",
            "t4": "はい！バレンタインプレゼントも終わりです！来年もバレンタインしましょうね❸(仮でラスト用を混ぜてます)",
            'idx' : idx,
            'tt' : u'本日のアイテム名',
            'nt' : u'明日のアイテム名',
            'logoPre' : self.url_static + 'effect/sp/v2/valentine2016/data/',
            'day' : day,
        }
        
        for i in xrange(6):
            params['f%d' % i] = args.get(i+1) or '0'
        
        if idx < 5:
            params['idxnext'] = idx + 1
        
        self.writeDataResponseBody(params)
    
    def procCountDownLoginParam(self):
        """カウントダウンログインのパラメータ.
        """
        args = self.getUrlArgs('/html5_test/CountDownLoginParam/')
        idx = (args.getInt(0) or 1) - 1
        day = 6 - (idx + 1)

        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img,
            "i0": "item/ticket_koakuma/Item_thumb_60_60.png", 
            "i1": "item/ticket_chiteki/Item_thumb_60_60.png", 
            "i2": "item/ticket_iyashi/Item_thumb_60_60.png", 
            "i3": "gacha/ticket/gachaticket_hr_1.png", 
            "i4": "gacha/ticket/gachaticket_sr_1.png", 
            "i5": "item/ring_diamond/Item_thumb_60_60.png", 
            'idx' : idx,
            'tt' : u'本日のアイテム名',
            'logoPre' : self.url_static + 'effect/sp/v2/countdown_login/data/',
            'day' : day,
        }
        
        for i in xrange(6):
            params['f%d' % i] = args.get(i+1) or '0'
        
        if idx < 5:
            params['idxnext'] = idx + 1
        
        self.writeDataResponseBody(params)

    def procCountdownLogin2ndAnniversaryParam(self):
        """2周年記念カウントダウンログインのパラメータ.
        """
        args = self.getUrlArgs('/html5_test/CountdownLogin2ndAnniversaryParam/')
        now_day = args.getInt(0)
        first_day = 11
        last_day = 25
        remaining_day = last_day - now_day
        max_idx = 3
        
        if now_day == first_day:
            idx = 0
        elif (max_idx-1) > remaining_day:
            idx = max_idx - remaining_day
        else:
            idx = 1
        
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'tt' : u'本日のアイテム名',
            'nt' : u'明日のアイテム名',
            'pre' : self.url_static_img,
            'idx' : idx,
            'day': remaining_day,
            'month': 12,
            'ten_digit': remaining_day / 10,
            'one_digit': remaining_day % 10,
            "i0": "item/ticket_koakuma/Item_thumb_60_60.png",
            "i1": "item/ticket_chiteki/Item_thumb_60_60.png",
            "i2": "item/ticket_iyashi/Item_thumb_60_60.png",
            "i3": "gacha/ticket/gachaticket_hr_1.png",
            "t0": "あ、オーナー2周年記念までの間プレゼントを配布してます！",
            "t1": "えっと、今日のプレゼントはこれです",
            "t2": "[ITEM]をプレゼントします",
            "t3": "次は[NEXTITEM]をプレゼントします。忘れずに来てくださいね",
            "t4": "ついに記念すべき2周年ですね！明日も豪華なプレゼントを用意して待ってます！",
            'td' : now_day,
            "getitem": "item/ticket_iyashi/Item_thumb_60_60.png",
            "nextitem": "gacha/ticket/gachaticket_hr_1.png",
            'next_name': u'明日のアイテム名',
        }
        for i in xrange(4):
            params['f%d' % i] = args.getInt(i+1) or 0
        
        date0 = now_day - idx
        for i in xrange(max_idx+1):
            params['date%d' % i] = "12月%d日" % (date0+i)

        if idx < 4:
            params['idxnext'] = idx + 1
        
        self.writeDataResponseBody(params)

    def procCountdownLogin3rdAnniversaryParam(self):
        """3周年記念カウントダウンログインのパラメータ.
        """
        args = self.getUrlArgs('/html5_test/CountdownLogin3rdAnniversaryParam/')
        now_day = args.getInt(0)
        first_day = 19
        last_day = 25
        remaining_day = last_day - now_day
        max_idx = 3

        if now_day == first_day:
            idx = 0
        elif (max_idx - 1) > remaining_day:
            idx = max_idx - remaining_day
        else:
            idx = 1

        params = {
            'backUrl': self.makeAppLinkUrl('/html5_test/'),
            'tt': u'本日のアイテム名',
            'nt': u'明日のアイテム名',
            'pre': self.url_static_img,
            'predata': self.url_static + 'effect/sp/v2/countdown_login_3rdanniversary/data/',
            'idx': idx,
            'day': remaining_day,
            'month': 12,
            'one_digit': remaining_day % 10,
            "i0": "item/ticket_koakuma/Item_thumb_60_60.png",
            "i1": "item/ticket_chiteki/Item_thumb_60_60.png",
            "i2": "item/ticket_iyashi/Item_thumb_60_60.png",
            "i3": "gacha/ticket/gachaticket_hr_1.png",
            "t0": "あ、オーナー3周年記念までの間プレゼントを配布してます！",
            "t1": "えっと、今日のプレゼントはこれです",
            "t2": "[ITEM]をプレゼントします",
            "t3": "次は[NEXTITEM]をプレゼントします。忘れずに来てくださいね",
            "t4": "ついに記念すべき3周年ですね！明日も豪華なプレゼントを用意して待ってます！",
            'td': now_day,
            "getitem": "item/ticket_iyashi/Item_thumb_60_60.png",
            "nextitem": "gacha/ticket/gachaticket_hr_1.png",
            'next_name': u'明日のアイテム名',
        }
        for i in xrange(4):
            params['f%d' % i] = args.getInt(i + 1) or 0

        date0 = now_day - idx
        for i in xrange(max_idx + 1):
            params['date%d' % i] = "12月%d日" % (date0 + i)

        if idx < 4:
            params['idxnext'] = idx + 1

        self.writeDataResponseBody(params)

    def procEndOfYearCountdownParam(self):
        """年末カウントダウンログイン 2015->2016ver パラメータ.
        """
        args = self.getUrlArgs('/html5_test/EndOfYearCountdownParam/')
        now_day = args.getInt(0)
        first_day = 29
        last_day = 31
        remaining_day = last_day - now_day
        max_idx = 2

        if now_day == first_day:
            idx = 0
        elif (max_idx-1) > remaining_day:
            idx = max_idx - remaining_day
        else:
            idx = 1

        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'tt' : u'本日のアイテム名',
            'nt' : u'明日のアイテム名',
            'pre' : self.url_static_img,
            'logoPre' : self.url_static + 'effect/sp/v2/end_of_year_countdown/data/',
            'idx' : idx,
            'day': remaining_day,
            "i0": "item/ticket_koakuma/Item_thumb_60_60.png",
            "i1": "item/ticket_chiteki/Item_thumb_60_60.png",
            "i2": "item/ticket_iyashi/Item_thumb_60_60.png",
            "t0": "オーナー今年もお疲れ様でした！プレゼントあげちゃいます♩",
            "t1": "う〜ん、今日のプレゼントは〜…これ！！",
            "t2": "「__ITEM__」をあげちゃいます♩",
            "t3": "次は「__NEXT__」をプレゼントします！明日も待ってますからね！！",
            "t4": "年末カウントダウンプレゼントはこれでお終しまいです！来年もよろしくお願いしますね♩",
            'td' : now_day,
            "getitem": "item/ticket_iyashi/Item_thumb_60_60.png",
            "nextitem": "gacha/ticket/gachaticket_hr_1.png",
            'next_name': u'明日のアイテム名',
        }
        for i in xrange(4):
            params['f%d' % i] = args.getInt(i+1) or 0

        date0 = now_day - idx
        for i in xrange(max_idx+1):
            params['date%d' % i] = "12月%d日" % (date0+i)

        if idx < 4:
            params['idxnext'] = idx + 1
        self.writeDataResponseBody(params)


    def procLogin2ndAnniversaryParam(self):
        """2周年記念ログインのパラメータ.
        """
        args = self.getUrlArgs('/html5_test/Login2ndAnniversaryParam/')
        now_day = args.getInt(0)
        
        first_day = 26
        last_day = 31
        remaining_day = last_day - now_day
        max_idx = 3
        
        if now_day == first_day:
            idx = 0
        elif (max_idx-1) > remaining_day:
            idx = max_idx - remaining_day
        else:
            idx = 1
        
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'tt' : u'本日のアイテム名',
            'nt' : u'明日のアイテム名',
            'pre' : self.url_static_img,
            'logoPre' : self.url_static + 'effect/sp/v2/2nd_anniversary_login/data/',
            'idx' : idx,
            'day': remaining_day,
            'month': 12,
            'i0': 'item/ticket_koakuma/Item_thumb_60_60.png',
            'i1': 'item/ticket_chiteki/Item_thumb_60_60.png',
            'i2': 'item/ticket_iyashi/Item_thumb_60_60.png',
            'i3': 'gacha/ticket/gachaticket_hr_1.png',
            't0':'2周年記念！これもオーナーのおかげです！プレゼント配布しちゃいます！',
            't1':'今日のプレゼントは…これかなぁ？',
            't2':'「__ITEM__」をプレゼントしちゃいます！',
            't3':'次は「__NEXT__」をプレゼントしちゃいますよ！明日も待ってます！',
            't4':'2周年記念のプレゼントはおしまい！これからも宜しくお願いしますね！',
            'td' : now_day,
            'getitem': 'item/ticket_iyashi/Item_thumb_60_60.png',
            'nextitem': 'gacha/ticket/gachaticket_hr_1.png',
            'next_name': u'明日のアイテム名',
        }
        for i in xrange(4):
            params['f%d' % i] = args.getInt(i+1) or 0
        
        date0 = now_day - idx
        for i in xrange(max_idx+1):
            params['date%d' % i] = "12月%d日" % (date0+i)

        if idx < 4:
            params['idxnext'] = idx + 1

        self.writeDataResponseBody(params)

    def procLogin3rdAnniversaryParam(self):
        """3周年記念ログインのパラメータ.
        """
        args = self.getUrlArgs('/html5_test/Login3rdAnniversaryParam/')
        now_day = args.getInt(0)

        first_day = 26
        last_day = 31
        remaining_day = last_day - now_day
        max_idx = 3

        if now_day == first_day:
            idx = 0
        elif (max_idx - 1) > remaining_day:
            idx = max_idx - remaining_day
        else:
            idx = 1

        params = {
            'backUrl': self.makeAppLinkUrl('/html5_test/'),
            'tt': u'本日のアイテム名',
            'nt': u'明日のアイテム名',
            'pre': self.url_static_img,
            'logoPre': self.url_static + 'effect/sp/v2/3rd_anniversary_login/data/',
            'idx': idx,
            'day': remaining_day,
            'month': 12,
            'i0': 'item/ticket_koakuma/Item_thumb_60_60.png',
            'i1': 'item/ticket_chiteki/Item_thumb_60_60.png',
            'i2': 'item/ticket_iyashi/Item_thumb_60_60.png',
            'i3': 'gacha/ticket/gachaticket_hr_1.png',
            't0': '3周年記念！これもオーナーのおかげです！プレゼント配布しちゃいます！',
            't1': '今日のプレゼントは…これかなぁ？',
            't2': '「__ITEM__」をプレゼントしちゃいます！',
            't3': '次は「__NEXT__」をプレゼントしちゃいますよ！明日も待ってます！',
            't4': '3周年記念のプレゼントはおしまい！これからも宜しくお願いしますね！',
            'td': now_day,
            'getitem': 'item/ticket_iyashi/Item_thumb_60_60.png',
            'nextitem': 'gacha/ticket/gachaticket_hr_1.png',
            'next_name': u'明日のアイテム名',
        }
        for i in xrange(4):
            params['f%d' % i] = args.getInt(i + 1) or 0

        date0 = now_day - idx
        for i in xrange(max_idx + 1):
            params['date%d' % i] = "12月%d日" % (date0 + i)

        if idx < 4:
            params['idxnext'] = idx + 1

        self.writeDataResponseBody(params)

    def procNewYearLoginParam(self):
        """年始ログインのパラメータ.
        """
        args = self.getUrlArgs('/html5_test/NewYearLoginParam/')
        idx = (args.getInt(0) or 1) - 1
        
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img,
            'i0' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
            'i1' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
            'i2' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHATICKET),
            'i3' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET),
            'i4' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.SILVERKEY),
            'i5' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLDKEY),
            'i6' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.MEMORIESTICKET),
            'idx' : idx,
            'tt' : u'本日のアイテム名',
            'logoPre' : self.url_static + 'effect/sp/v2/newyear_login/data/',
        }
        for i in xrange(idx):
            params['f%d' % i] = 1
        if idx < 6:
            params.update({
                'nt' : u'明日のアイテム名',
                'idxnext' : idx+1,
            })
        
        self.writeDataResponseBody(params)
    
    def procHinamatsuriLoginParam(self):
        """雛祭りログインのパラメータ.
        """
        args = self.getUrlArgs('/html5_test/HinamatsuriLoginParam/')
        idx = (args.getInt(0) or 1) - 1
        
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img,
            "i0": "item/ticket_koakuma/Item_thumb_60_60.png", 
            "i1": "item/ticket_chiteki/Item_thumb_60_60.png",
            "i2": "item/ticket_iyashi/Item_thumb_60_60.png", 
            "i3": "gacha/ticket/gachaticket_hr_1.png", 
            'idx' : idx,
            'tt' : u'本日のアイテム名',
            'nt' : u'次のアイテム名',
            'logo' : True,
            'preEffect' : self.url_static_img + 'event/loginbonus/hinamatsuri/',
            'date0' : u'3月3日',
            'date1' : u'3月4日',
            'date2' : u'3月5日',
            'date3' : u'3月6日',
            't0' : u'オーナーお疲れ様です♪',
            't1' : u'「雛祭り」って元々は「雛遊び」から来てるって知ってました?これでもっと私たちと遊んで下さい♪',
            't2' : u'「__ITEM__」を雛祭りの記念にプレゼントです！',
            't3' : u'明日はこちらをプレゼントです！受け取りに来てくれるのを、ずっと待ってますからね♪',
            't4' : u'じゃあ、今日も1日頑張りましょう♪',
        }
        
        for i in xrange(4):
            params['f%d' % i] = args.get(i+1) or '0'
        
        if idx < 5:
            params['idxnext'] = idx + 1
        
        self.writeDataResponseBody(params)
    
    def procNewbieLoginParam(self):
        """初心者限定ログインのパラメータ.
        """
        args = self.getUrlArgs('/html5_test/NewbieLoginParam/')
        idx = (args.getInt(0) or 1) - 1
        ix = (args.getInt(1) or -1)
        iy = (args.getInt(2) or -1)
        bg = u'%s.png' % args.get(3)
        
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img,
            "i0": "item/ticket_koakuma/Item_thumb_60_60.png", 
            "i1": "item/ticket_chiteki/Item_thumb_60_60.png",
            "i2": "item/ticket_iyashi/Item_thumb_60_60.png", 
            "i3": "gacha/ticket/gachaticket_hr_1.png", 
            "i4": "gacha/ticket/gachaticket_hr_1.png", 
            "i5": "gacha/ticket/gachaticket_hr_1.png", 
            "i6": "gacha/ticket/gachaticket_hr_1.png", 
            'idx' : idx,
            'ix' : ix,
            'iy' : iy,
            'tt' : u'本日のアイテム名',
            'logo' : True,
            'preEffect' : self.url_static_img + 'event/loginbonus/newbie/',
            'bg' : bg,
            'tlogo' : u'あ、オーナー！\n来てくれたんですね♪',
            't0' : u'オーナーが来てくれて嬉しい！\n良いものあげちゃいますね♪',
            't1' : u'今日は…これ！！',
            't2' : u'「__ITEM__」をあげちゃいますっ！',
            't3' : u'明日は「__NEXT__」をあげるね！次は違う格好でオーナーを迎えようかな？',
            't4' : u'こうしてオーナーと会えるのも今日で最後です!でもまだまだ構ってもらいますからね!約束♪',
        }
        
        for i in xrange(idx):
            params['f%d' % i] = '1'
        
        if idx < 6:
            params.update({
                'nt' : u'明日のアイテム名',
                'idxnext' : idx+1,
            })
        
        self.writeDataResponseBody(params)
    
    def procMonthlyLoginEnd(self):
        """月末ログインボーナス.
        """
        effectpath = 'monthly_login/effect.html'
        idx = int(self.request.get('_cnt') or 0)
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img,
            'i0' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
            'i1' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
            'i2' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
            'idx' : idx,
            'td' : OSAUtil.get_now().day,
            'tt' : u'本日のアイテム名',
            'logoPre' : self.url_static + 'effect/sp/v2/monthly_login/data/default/',
            'rouletteCnt' : 9 + idx,
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procLongLoginBonus(self):
        """ロングログインボーナス.
        """
        effectpath = 'dl_100thou/long_login/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img,
            'i0' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
            'd0' : 3,
            'i1' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
            'd1' : 5,
            'i2' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHATICKET),
            'd2' : 7,
            'i3' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET),
            'd3' : 9,
            'td' : 5,
            'tt' : u'引抜チケットx50枚',
            'nt' : u'レア以上確定ガチャチケットx50枚',
            'has_next' : True,
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procBossEncount(self):
        """ボスエンカウント.
        """
        effectpath = 'bossencount/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def __procBossBattle(self, winFlag):
        """ボス戦.
        """
        effectpath = 'bossbattle2/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'winFlag' : int(winFlag),
            'playerMax' : 10,
            'activePlayer' : '1:2:3:4:5:6:7:8:9:10',
            'bossGauge' : '0:85',
            'bossImage' : self.makeAppLinkUrlImg('event/raidevent/rdev_09/boss1/Raid_boss.png'),
            'image1' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'image2' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image3' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image4' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image5' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image6' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image7' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image8' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image9' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image10' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'helpFlag' : 0,
            'bossDamage' : 99999999999,
            'helpPlayer' : '1:2:3:4:5:6:7:8:9:10',
        }
        self.appRedirectToEffect(effectpath, params)
        
    def procBossBattleWin(self):
        """ボス戦(勝利).
        """
        self.__procBossBattle(True)
    
    def procBossBattleLose(self):
        """ボス戦(敗北).
        """
        self.__procBossBattle(False)
    
    def procGachaNormal(self):
        """通常ガチャ.
        """
        effectpath = 'gachanormal/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/GachaNormalParam/')
        self.appRedirectToEffect2(effectpath, dataUrl)
    
    def procGachaNormalParam(self):
        """通常ガチャの演出パラメータ.
        """
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'newFlag':"1",
            'cardText' : Defines.EffectTextFormat.GACHA_CARDTEXT % u'<<カード>>',
            'image' : self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
        }
        self.writeDataResponseBody(params)
    
    def procGachaGold(self):
        """課金ガチャ.
        """
        effectpath = 'gachagold/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/GachaGoldParam/')
        self.appRedirectToEffect2(effectpath, dataUrl)
    
    def procGachaRank(self):
        """ランキングガチャ.
        """
        effectpath = 'gacharank/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/GachaRankParam/')
        self.appRedirectToEffect2(effectpath, dataUrl)
    
    def procGachaChristmas(self):
        """クリスマスガチャ.
        """
        effectpath = 'gachaxmas/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/GachaChristmasParam/')
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procGachaXmas2015(self):
        """Xmas2015ガチャ.
        """
        effectpath = 'gachaxmas2015/effect2.html'
        cnt = int(self.request.get('_cnt'))
        url = '/html5_test/GachaXmas2015Param/'
        url = OSAUtil.addQuery(url, '_cnt', cnt)
        dataUrl = self.makeAppLinkUrl(url)
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procGachaFukubukuro(self):
        """福袋ガチャ.
        """
        effectpath = 'gachahappybag2/effect2.html'
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        url = '/html5_test/GachaFukubukuroParam/'
        url = OSAUtil.addQuery(url, '_cnt', cnt)
        url = OSAUtil.addQuery(url, '_page', page)
        dataUrl = self.makeAppLinkUrl(url)
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procGachaFukubukuro2016(self):
        """福袋ガチャ2016年.
        """
        effectpath = 'gachahappybag2016/effect2.html'
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        url = '/html5_test/GachaFukubukuro2016Param/'
        url = OSAUtil.addQuery(url, '_cnt', cnt)
        url = OSAUtil.addQuery(url, '_page', page)
        dataUrl = self.makeAppLinkUrl(url)
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procGachaFukubukuro201604(self):
        """福袋ガチャ2016年4月新年度ver.
        """
        effectpath = 'gachahappybag201604/effect2.html'
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        url = '/html5_test/GachaFukubukuro201604Param/'
        url = OSAUtil.addQuery(url, '_cnt', cnt)
        url = OSAUtil.addQuery(url, '_page', page)
        dataUrl = self.makeAppLinkUrl(url)
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procGachaFukubukuro201605(self):
        """福袋ガチャ2016年5月GWver.
        """
        effectpath = 'gachahappybag201605/effect2.html'
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        url = '/html5_test/GachaFukubukuro201605Param/'
        url = OSAUtil.addQuery(url, '_cnt', cnt)
        url = OSAUtil.addQuery(url, '_page', page)
        dataUrl = self.makeAppLinkUrl(url)
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procGachaFukubukuro201605r(self):
        """福袋ガチャ2016年5月GWリセットver.
        """
        effectpath = 'gachahappybag201605r/effect2.html'
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        url = '/html5_test/GachaFukubukuro201605rParam/'
        url = OSAUtil.addQuery(url, '_cnt', cnt)
        url = OSAUtil.addQuery(url, '_page', page)
        dataUrl = self.makeAppLinkUrl(url)
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procGachaFukubukuro201607(self):
        """福袋ガチャ2016年7月ver.
        """
        effectpath = 'gachahappybag201607/effect2.html'
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        url = '/html5_test/GachaFukubukuro201607Param/'
        url = OSAUtil.addQuery(url, '_cnt', cnt)
        url = OSAUtil.addQuery(url, '_page', page)
        dataUrl = self.makeAppLinkUrl(url)
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procGachaFukubukuro201608(self):
            """福袋ガチャ2016年7月ver.
            """
            effectpath = 'gachahappybag201608/effect2.html'
            page = int(self.request.get('_page') or 0)
            cnt = int(self.request.get('_cnt'))
            url = '/html5_test/GachaFukubukuro201608Param/'
            url = OSAUtil.addQuery(url, '_cnt', cnt)
            url = OSAUtil.addQuery(url, '_page', page)
            dataUrl = self.makeAppLinkUrl(url)
            self.appRedirectToEffect2(effectpath, dataUrl)

    def procGachaFukubukuro201701(self):
        """福袋ガチャ2016年7月ver.
        """
        effectpath = 'gachahappybag201701/effect2.html'
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        url = '/html5_test/GachaFukubukuro201701Param/'
        url = OSAUtil.addQuery(url, '_cnt', cnt)
        url = OSAUtil.addQuery(url, '_page', page)
        dataUrl = self.makeAppLinkUrl(url)
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procGachaGoldParam(self):
        """課金ガチャの演出パラメータ.
        """
        model_mgr = self.getModelMgr()
        masterlist = []
        for i in xrange(41):
            mid = CardMaster.getValues(offset=i).id
            masterlist.append(BackendApi.get_cardmasters([mid], model_mgr).get(mid))
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'newFlag':':'.join(['1:0'] * (len(masterlist)/2)),
            'cardText' : ':'.join([Defines.EffectTextFormat.GACHA_CARDTEXT % master.name for master in masterlist]),
            'image' : u','.join([self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(master)) for master in masterlist])
        }
        self.writeDataResponseBody(params)
    
    def procGachaRankParam(self):
        """ランキングガチャの演出パラメータ.
        """
        model_mgr = self.getModelMgr()
        masterlist = []
        for i in xrange(10):
            mid = CardMaster.getValues(offset=i).id
            masterlist.append(BackendApi.get_cardmasters([mid], model_mgr).get(mid))
        
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'newFlag':':'.join(['1:0'] * (len(masterlist)/2)),
            'cardText' : ':'.join([Defines.EffectTextFormat.GACHA_CARDTEXT % master.name for master in masterlist]),
            'image' : u','.join([self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(master)) for master in masterlist]),
            'point' : ':'.join([str(i*1000) for i in xrange(1, 11)]),
            'expectation' : ':'.join([str(i%3) for i in xrange(1, 11)]),
            'pre' : self.url_static + 'img/sp/large/gacha/ranking/rank_01/',
            'logo_img' : 'event_logo.png',
            'logo_w_img' : 'event_logo_w.png',
        }
        print Json.encode(params)
        self.writeDataResponseBody(params)
    
    def procGachaChristmasParam(self):
        """クリスマスガチャの演出パラメータ.
        """
        model_mgr = self.getModelMgr()
        masterlist = []
        for i in xrange(10):
            mid = CardMaster.getValues(offset=i+1).id
            masterlist.append(BackendApi.get_cardmasters([mid], model_mgr).get(mid))
        
        cardimglist = [CardUtil.makeThumbnailUrlIcon(master) for master in masterlist[:-1]]
        cardimglist.append(CardUtil.makeThumbnailUrlMiddle(masterlist[-1]))
        
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'newFlag':':'.join(['0:1'] * (len(masterlist)/2)),
            'cardText' : masterlist[-1].name,
            'image' : u','.join(cardimglist),
            'pre' : self.url_static_img,
            'logoPre' : self.url_static + 'effect/sp/v2/gachaxmas/data/',
        }
        print Json.encode(params)
        self.writeDataResponseBody(params)

    def procGachaXmas2015Param(self):
        """Xmas2015ガチャの演出パラメータ.
        """
        masterlist = []
        model_mgr = self.getModelMgr()
        cardnum = int(self.request.get('_cnt'))
        for i in xrange(cardnum):
            mid = CardMaster.getValues(offset=i+1).id
            masterlist.append(BackendApi.get_cardmasters([mid], model_mgr).get(mid))

        cardimglist = [CardUtil.makeThumbnailUrlIcon(master) for master in masterlist]
        if cardnum == 5:
            newFlag = ['0','1','0','0','0']
        else:
            newFlag = ['1','0','0','0','0','1','0','0','1','1']

        params = {
            'backUrl': self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img,
            'logoPre' : self.url_static + 'effect/sp/v2/gachaxmas2015/data/',
            'image' : u','.join(cardimglist),
            'newFlag' : u':'.join(newFlag)
        }
        print Json.encode(params)
        self.writeDataResponseBody(params)

    def procGachaFukubukuroParam(self):
        """福袋ガチャの演出パラメータ.
        """
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        page_max = int((cnt + 9) / 10)
        
        skipUrl = self.makeAppLinkUrl('/html5_test/')
        isLast = page == (page_max - 1)
        if isLast:
            backUrl = skipUrl
        else:
            url = '/html5_test/GachaFukubukuro/'
            url = OSAUtil.addQuery(url, '_cnt', cnt)
            url = OSAUtil.addQuery(url, '_page', page + 1)
            backUrl = self.makeAppLinkUrl(url)
        
        cardnum = min(10, cnt - page * 10)
        model_mgr = self.getModelMgr()
        masterlist = []
        for i in xrange(cardnum):
            mid = CardMaster.getValues(offset=i+1).id
            masterlist.append(BackendApi.get_cardmasters([mid], model_mgr).get(mid))
        
        cardimglist = [CardUtil.makeThumbnailUrlIcon(master) for master in masterlist]
        
        params = {
            'backUrl':backUrl,
            'skipUrl' : skipUrl,
            'pre' : self.url_static_img,
            'logoPre' : self.url_static + 'effect/sp/v2/gachahappybag2/data/',
            'newFlag':':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'rarityFlag':':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'isFirst' : 1 if page == 0 else 0,
            'isLast' : 1 if isLast else 0,
            'image' : u','.join(cardimglist),
        }
        
        if isLast:
            itemimg = [
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHATICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLDKEY),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.SILVERKEY),
            ]
            params.update({
                'itemImage' : u','.join(itemimg),
                'itemImageIdx' : ':'.join([str(random.randint(0, len(itemimg)-1)) for _ in xrange(30)]),
            })
        
        print Json.encode(params)
        self.writeDataResponseBody(params)

    def procGachaFukubukuro2016Param(self):
        """福袋ガチャ2016年の演出パラメータ.
        """
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        page_max = int((cnt + 9) / 10)
        
        skipUrl = self.makeAppLinkUrl('/html5_test/')
        isLast = page == (page_max - 1)
        if isLast:
            backUrl = skipUrl
        else:
            url = '/html5_test/GachaFukubukuro2016/'
            url = OSAUtil.addQuery(url, '_cnt', cnt)
            url = OSAUtil.addQuery(url, '_page', page + 1)
            backUrl = self.makeAppLinkUrl(url)
        
        cardnum = min(10, cnt - page * 10)
        model_mgr = self.getModelMgr()
        masterlist = []
        for i in xrange(cardnum):
            mid = CardMaster.getValues(offset=i+1).id
            masterlist.append(BackendApi.get_cardmasters([mid], model_mgr).get(mid))
        
        cardimglist = [CardUtil.makeThumbnailUrlIcon(master) for master in masterlist]
        
        params = {
            'backUrl':backUrl,
            'skipUrl' : skipUrl,
            'pre' : self.url_static_img,
            'logoPre' : self.url_static + 'effect/sp/v2/gachahappybag2016/data/',
            'newFlag':':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'rarityFlag':':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'isFirst' : 1 if page == 0 else 0,
            'isLast' : 1 if isLast else 0,
            'image' : u','.join(cardimglist),
        }
        
        if isLast:
            itemimg = [
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHATICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLDKEY),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.SILVERKEY),
            ]
            params.update({
                'itemImage' : u','.join(itemimg),
                'itemImageIdx' : ':'.join([str(random.randint(0, len(itemimg)-1)) for _ in xrange(30)]),
            })
        
        print Json.encode(params)
        self.writeDataResponseBody(params)

    def procGachaFukubukuro201604Param(self):
        """福袋ガチャ2016年4月新年度verの演出パラメータ.
        """
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        page_max = int((cnt + 9) / 10)
        
        skipUrl = self.makeAppLinkUrl('/html5_test/')
        isLast = page == (page_max - 1)
        if isLast:
            backUrl = skipUrl
        else:
            url = '/html5_test/GachaFukubukuro201604/'
            url = OSAUtil.addQuery(url, '_cnt', cnt)
            url = OSAUtil.addQuery(url, '_page', page + 1)
            backUrl = self.makeAppLinkUrl(url)
        
        cardnum = min(10, cnt - page * 10)
        model_mgr = self.getModelMgr()
        masterlist = []
        for i in xrange(cardnum):
            mid = CardMaster.getValues(offset=i+1).id
            masterlist.append(BackendApi.get_cardmasters([mid], model_mgr).get(mid))
        
        cardimglist = [CardUtil.makeThumbnailUrlIcon(master) for master in masterlist]
        
        params = {
            'backUrl':backUrl,
            'skipUrl' : skipUrl,
            'pre' : self.url_static_img,
            'logoPre' : self.url_static + 'effect/sp/v2/gachahappybag201604/data/',
            'newFlag':':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'rarityFlag':':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'isFirst' : 1 if page == 0 else 0,
            'isLast' : 1 if isLast else 0,
            'image' : u','.join(cardimglist),
        }
        
        if isLast:
            itemimg = [
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHATICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLDKEY),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.SILVERKEY),
            ]
            params.update({
                'itemImage' : u','.join(itemimg),
                'itemImageIdx' : ':'.join([str(random.randint(0, len(itemimg)-1)) for _ in xrange(30)]),
            })
        
        print Json.encode(params)
        self.writeDataResponseBody(params)

    def procGachaFukubukuro201605Param(self):
        """福袋ガチャ2016年5月GWrverの演出パラメータ.
        """
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        page_max = int((cnt + 9) / 10)
        
        skipUrl = self.makeAppLinkUrl('/html5_test/')
        isLast = page == (page_max - 1)
        if isLast:
            backUrl = skipUrl
        else:
            url = '/html5_test/GachaFukubukuro201605/'
            url = OSAUtil.addQuery(url, '_cnt', cnt)
            url = OSAUtil.addQuery(url, '_page', page + 1)
            backUrl = self.makeAppLinkUrl(url)
        
        cardnum = min(10, cnt - page * 10)
        model_mgr = self.getModelMgr()
        masterlist = []
        for i in xrange(cardnum):
            mid = CardMaster.getValues(offset=i+1).id
            masterlist.append(BackendApi.get_cardmasters([mid], model_mgr).get(mid))
        
        cardimglist = [CardUtil.makeThumbnailUrlIcon(master) for master in masterlist]
        
        params = {
            'backUrl':backUrl,
            'skipUrl' : skipUrl,
            'pre' : self.url_static_img,
            'logoPre' : self.url_static + 'effect/sp/v2/gachahappybag201605/data/',
            'newFlag':':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'rarityFlag':':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'isFirst' : 1 if page == 0 else 0,
            'isLast' : 1 if isLast else 0,
            'image' : u','.join(cardimglist),
        }
        
        if isLast:
            itemimg = [
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHATICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLDKEY),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.SILVERKEY),
            ]
            params.update({
                'itemImage' : u','.join(itemimg),
                'itemImageIdx' : ':'.join([str(random.randint(0, len(itemimg)-1)) for _ in xrange(30)]),
            })
        
        print Json.encode(params)
        self.writeDataResponseBody(params)

    def procGachaFukubukuro201605rParam(self):
        """福袋ガチャ2016年5月GWrverの演出パラメータ.
        """
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        page_max = int((cnt + 9) / 10)
        
        skipUrl = self.makeAppLinkUrl('/html5_test/')
        isLast = page == (page_max - 1)
        if isLast:
            backUrl = skipUrl
        else:
            url = '/html5_test/GachaFukubukuro201605r/'
            url = OSAUtil.addQuery(url, '_cnt', cnt)
            url = OSAUtil.addQuery(url, '_page', page + 1)
            backUrl = self.makeAppLinkUrl(url)
        
        cardnum = min(10, cnt - page * 10)
        model_mgr = self.getModelMgr()
        masterlist = []
        for i in xrange(cardnum):
            mid = CardMaster.getValues(offset=i+1).id
            masterlist.append(BackendApi.get_cardmasters([mid], model_mgr).get(mid))
        
        cardimglist = [CardUtil.makeThumbnailUrlIcon(master) for master in masterlist]
        
        params = {
            'backUrl':backUrl,
            'skipUrl' : skipUrl,
            'pre' : self.url_static_img,
            'logoPre' : self.url_static + 'effect/sp/v2/gachahappybag201605r/data/',
            'newFlag':':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'rarityFlag':':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'isFirst' : 1 if page == 0 else 0,
            'isLast' : 1 if isLast else 0,
            'image' : u','.join(cardimglist),
        }
        
        if isLast:
            itemimg = [
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHATICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLDKEY),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.SILVERKEY),
            ]
            params.update({
                'itemImage' : u','.join(itemimg),
                'itemImageIdx' : ':'.join([str(random.randint(0, len(itemimg)-1)) for _ in xrange(30)]),
            })
        
        print Json.encode(params)
        self.writeDataResponseBody(params)

    def procGachaFukubukuro201607Param(self):
        """福袋ガチャ2016年7月GWrverの演出パラメータ.
        """
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        page_max = int((cnt + 9) / 10)
        
        skipUrl = self.makeAppLinkUrl('/html5_test/')
        isLast = page == (page_max - 1)
        if isLast:
            backUrl = skipUrl
        else:
            url = '/html5_test/GachaFukubukuro201607/'
            url = OSAUtil.addQuery(url, '_cnt', cnt)
            url = OSAUtil.addQuery(url, '_page', page + 1)
            backUrl = self.makeAppLinkUrl(url)
        
        cardnum = min(10, cnt - page * 10)
        model_mgr = self.getModelMgr()
        masterlist = []
        for i in xrange(cardnum):
            mid = CardMaster.getValues(offset=i+1).id
            masterlist.append(BackendApi.get_cardmasters([mid], model_mgr).get(mid))
        
        cardimglist = [CardUtil.makeThumbnailUrlIcon(master) for master in masterlist]
        
        params = {
            'backUrl':backUrl,
            'skipUrl' : skipUrl,
            'pre' : self.url_static_img,
            'logoPre' : self.url_static + 'effect/sp/v2/gachahappybag201607/data/',
            'newFlag':':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'rarityFlag':':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'isFirst' : 1 if page == 0 else 0,
            'isLast' : 1 if isLast else 0,
            'image' : u','.join(cardimglist),
        }
        
        if isLast:
            itemimg = [
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHATICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLDKEY),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.SILVERKEY),
            ]
            params.update({
                'itemImage' : u','.join(itemimg),
                'itemImageIdx' : ':'.join([str(random.randint(0, len(itemimg)-1)) for _ in xrange(30)]),
            })
        
        print Json.encode(params)
        self.writeDataResponseBody(params)

    def procGachaFukubukuro201608Param(self):
        """福袋ガチャ2016年7月GWrverの演出パラメータ.
        """
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        page_max = int((cnt + 9) / 10)

        skipUrl = self.makeAppLinkUrl('/html5_test/')
        isLast = page == (page_max - 1)
        if isLast:
            backUrl = skipUrl
        else:
            url = '/html5_test/GachaFukubukuro201608/'
            url = OSAUtil.addQuery(url, '_cnt', cnt)
            url = OSAUtil.addQuery(url, '_page', page + 1)
            backUrl = self.makeAppLinkUrl(url)

        cardnum = min(10, cnt - page * 10)
        model_mgr = self.getModelMgr()
        masterlist = []
        for i in xrange(cardnum):
            mid = CardMaster.getValues(offset=i + 1).id
            masterlist.append(BackendApi.get_cardmasters([mid], model_mgr).get(mid))

        cardimglist = [CardUtil.makeThumbnailUrlIcon(master) for master in masterlist]

        params = {
            'backUrl': backUrl,
            'skipUrl': skipUrl,
            'pre': self.url_static_img,
            'logoPre': self.url_static + 'effect/sp/v2/gachahappybag201608/data/',
            'newFlag': ':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'rarityFlag': ':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'isFirst': 1 if page == 0 else 0,
            'isLast': 1 if isLast else 0,
            'image': u','.join(cardimglist),
        }

        if isLast:
            itemimg = [
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHATICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLDKEY),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.SILVERKEY),
            ]
            params.update({
                'itemImage': u','.join(itemimg),
                'itemImageIdx': ':'.join([str(random.randint(0, len(itemimg) - 1)) for _ in xrange(30)]),
            })

        print Json.encode(params)
        self.writeDataResponseBody(params)

    def procGachaFukubukuro201701Param(self):
        """福袋ガチャ2017年1月GWrverの演出パラメータ.
        """
        page = int(self.request.get('_page') or 0)
        cnt = int(self.request.get('_cnt'))
        page_max = int((cnt + 9) / 10)

        skipUrl = self.makeAppLinkUrl('/html5_test/')
        isLast = page == (page_max - 1)
        if isLast:
            backUrl = skipUrl
        else:
            url = '/html5_test/GachaFukubukuro201701/'
            url = OSAUtil.addQuery(url, '_cnt', cnt)
            url = OSAUtil.addQuery(url, '_page', page + 1)
            backUrl = self.makeAppLinkUrl(url)

        cardnum = min(10, cnt - page * 10)
        model_mgr = self.getModelMgr()
        masterlist = []
        for i in xrange(cardnum):
            mid = CardMaster.getValues(offset=i + 1).id
            masterlist.append(BackendApi.get_cardmasters([mid], model_mgr).get(mid))

        cardimglist = [CardUtil.makeThumbnailUrlIcon(master) for master in masterlist]

        params = {
            'backUrl': backUrl,
            'skipUrl': skipUrl,
            'pre': self.url_static_img,
            'logoPre': self.url_static + 'effect/sp/v2/gachahappybag201701/data/',
            'newFlag': ':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'rarityFlag': ':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
            'isFirst': 1 if page == 0 else 0,
            'isLast': 1 if isLast else 0,
            'image': u','.join(cardimglist),
        }

        if isLast:
            itemimg = [
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHATICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.RAREOVERTICKET),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLDKEY),
                ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.SILVERKEY),
            ]
            params.update({
                'itemImage': u','.join(itemimg),
                'itemImageIdx': ':'.join([str(random.randint(0, len(itemimg) - 1)) for _ in xrange(30)]),
            })

        print Json.encode(params)
        self.writeDataResponseBody(params)

    def procGachaSheet(self):
        """シートガチャ.
        """
        effectpath = 'sheet_gacha/logofree/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        
        arr = (
            Defines.ItemType.GOLD,                   # お金.
            Defines.ItemType.GACHA_PT,               # 引きぬきポイント.
            Defines.ItemType.RAREOVERTICKET,         # レア以上チケット
            Defines.ItemType.TRYLUCKTICKET,          # 運試しチケット.
            Defines.ItemType.GACHATICKET,            # 引き抜きチケット.
            Defines.ItemType.GOLDKEY,                # 金の鍵.
            Defines.ItemType.SILVERKEY,              # 銀の鍵.
            Defines.ItemType.CABARETKING_TREASURE,   # キャバ王の秘宝.
        )
        for i in xrange(9):
            params['i%02d' % i] = ItemUtil.makeThumbnailUrlMiddleByType(arr[i % len(arr)])
            params['f%02d' % i] = i % 2
        params['idx'] = 8
        params['prefix'] = self.url_static_img
        params['logoPre'] = self.makeAppLinkUrlImg('event/loginbonus/dl_300thou/')
        
        self.appRedirectToEffect(effectpath, params)
    
    def procGachaScev(self):
        """スカウトイベントガチャ.
        """
        effectpath = 'gachascev/effect2.html'
        rare = int(self.request.get('_rare') or Defines.Rarity.NORMAL)
        url = '/html5_test/GachaScevParam/'
        url = OSAUtil.addQuery(url, '_rare', rare)
        dataUrl = self.makeAppLinkUrl(url)
        self.appRedirectToEffect2(effectpath, dataUrl)
    
    def procGachaScevParam(self):
        """スカウトイベントガチャのパラメータ.
        """
        rare = int(self.request.get('_rare') or Defines.Rarity.NORMAL)
        
        model_mgr = self.getModelMgr()
        masterlist = []
        for i in xrange(10):
            mid = CardMaster.getValues(offset=i).id
            masterlist.append(BackendApi.get_cardmasters([mid], model_mgr).get(mid))
        
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'newFlag':':'.join(['1:0'] * (len(masterlist)/2)),
            'cardText' : ':'.join([master.name for master in masterlist]),
            'image' : u','.join([CardUtil.makeThumbnailUrlMiddle(master) for master in masterlist]),
            'effectPre' : self.url_static + 'effect/sp/v2/gachascev/data/scev_10/',
            'pre' : self.url_static_img,
            'maxrare' : rare,
        }
        self.writeDataResponseBody(params)
    
    def procGachaCastMedal(self):
        """スカウトイベントガチャ.
        """
        effectpath = 'gachacastmedal/effect2.html'
        url = '/html5_test/GachaCastMedalParam/'
        url = OSAUtil.addQuery(url, '_num', int(self.request.get('_num') or 10))
        dataUrl = self.makeAppLinkUrl(url)
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procGachaCastMedalParam(self):
        """スカウトイベントガチャのパラメータ.
        """
        model_mgr = self.getModelMgr()
        masterlist = []
        for i in xrange(int(self.request.get('_num') or 10)):
            mid = CardMaster.getValues(offset=i).id
            masterlist.append(BackendApi.get_cardmasters([mid], model_mgr).get(mid))
        
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'newFlag':':'.join(['1:0'] * (len(masterlist)/2)),
            'cardText' : ':'.join([u'%sが入店しました'% master.name for master in masterlist]),
            'image' : u','.join([CardUtil.makeThumbnailUrlMiddle(master) for master in masterlist]),
            'logoPre' : self.makeAppLinkUrlImg('event/scevent/scev_17/gacha/'),
            'imagePre' : self.url_static_img,
            'rarityFlag':':'.join([str(random.randint(0, 1)) for _ in xrange(len(masterlist))]),
        }
        self.writeDataResponseBody(params)

    def procGachaMoreCast(self):
        """ガチャ追加キャスト.
        """
        effectpath = 'gachamorecast/effect2.html'
        url = '/html5_test/GachaMoreCastParam/'
        dataUrl = self.makeAppLinkUrl(url)
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procGachaMoreCastParam(self):
        """ガチャ追加キャストの演出パラメータ.
        """
        card = self.getModelMgr().get_model(CardMaster, 12020)
        params = {
            'backUrl': self.makeAppLinkUrl('/html5_test/'),
            'cardText': Defines.EffectTextFormat.GACHA_CARDTEXT % card.name,
            'image': self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(card)),
            'pre': 'img/',
        }
        self.writeDataResponseBody(params)

    
    def procPanelMission(self):
        """パネルミッション.
        """
        params = [str(int(self.request.get('_next') != 'last'))]
        params.extend([str(self.request.get('_p%d' % i)) for i in xrange(9)])
        
        effectpath = 'panel_mission/effect2.html'
        dataUrl = self.makeAppLinkUrl('/html5_test/PanelMissionParam/%s' % '/'.join(params))
        self.appRedirectToEffect2(effectpath, dataUrl)
    
    def procPanelMissionParam(self):
        """パネルミッション演出パラメータ.
        """
        MISSION_NUM = 9
        
        panel_idx = 0
        
        def makePanelImgPath(panel, number):
            return 'mission/test/%02d/mission_%02d_%02d.png' % (panel, panel, number+1)
        def makePanelBgPath(panel):
            return 'mission/test/%02d/photo%d.png' % (panel, panel+1)
        
        args = self.getUrlArgs('/html5_test/PanelMissionParam/')
        
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'logoPre' : self.url_static + 'effect/sp/v2/panel_mission/data/201702/',
            'pre' : self.url_static_img,
            'panel' : panel_idx + 1,
            'bg' : makePanelBgPath(panel_idx),
        }
        
        # 現在のパネル.
        clear = []
        cleared_cnt = 0
        for i in xrange(MISSION_NUM):
            v = args.get(i + 1)
            if v == 'opened':
                cleared_cnt += 1
                continue
            elif v == 'open':
                clear.append(str(i))
            params['m%d' % i] = makePanelImgPath(panel_idx, i)
            params['mtext%d' % i] = u'ミッション%d' % (i+1)
        
        # 今回クリアしたミッション.
        params['clear'] = ','.join(clear)
        
        # オールクリアで獲得するカード.
        if (cleared_cnt+len(clear)) == MISSION_NUM:
            params['card'] = CardUtil.makeThumbnailUrlMiddle(self.__dummycard)
            params['cname'] = u'カード名012345'
            
            # 次のパネル.
            has_next = args.getInt(0)
            if has_next:
                for i in xrange(MISSION_NUM):
                    params['next%d' % i] = makePanelImgPath(panel_idx + 1, i)
        
        self.writeDataResponseBody(params)
    
    def procEventOpening(self):
        """イベントオープニング.
        """
        effectpath = 'raidevent/rdev_14/event_opening/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static + 'effect/sp/v2/raidevent/rdev_14/data/',
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procEventHappening(self):
        """レイドイベント ハプニング発生.
        """
        effectpath = 'raidevent/chohutokyaku/effect.html'
        boss = self.request.get('_boss')
        eventmaster = BackendApi.get_current_raideventmaster(self.getModelMgr(), using=settings.DB_READONLY, do_check_schedule=False)
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img + 'event/raidevent/%s/%s/' % (eventmaster.codename, boss)
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procBigBoss(self):
        """レイドイベント 大ボス.
        """
        effectpath = 'raidevent/event_boss_ec/effect.html'
        eventmaster = BackendApi.get_current_raideventmaster(self.getModelMgr(), using=settings.DB_READONLY, do_check_schedule=False)
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img + 'event/raidevent/%s/effect/' % eventmaster.codename
        }
        self.appRedirectToEffect(effectpath, params)

    def procBigBoss2(self):
        """レイドイベント 大ボス.
        """
        effectpath = 'raidevent/event_boss_ec2/effect.html'
        eventmaster = BackendApi.get_current_raideventmaster(self.getModelMgr(), using=settings.DB_READONLY, do_check_schedule=False)
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img + 'event/raidevent/%s/effect/' % eventmaster.codename
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procEventEnding(self):
        """レイドイベント エンディング.
        """
        effectpath = 'raidevent/rdev_14/event_epilogue/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static + 'effect/sp/v2/raidevent/rdev_14/data/',
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procChampagneCall(self):
        """SHOWTIME.
        """
        effectpath = 'raidevent/showtime/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img + 'event/raidevent/showtime/',
            'cast0' : 'rdev_Cast_01c.png',
            'cast1' : 'rdev_Cast_02c.png',
            'cast2' : 'rdev_Cast_03c.png',
            'cast3' : 'rdev_Cast_04c.png',
        }
        self.appRedirectToEffect(effectpath, params)

    def procProduceEventHappening(self):
        """プロデュースイベント太客発生.
        """
        effectpath = 'produce_event/produce_hutokyaku/effect.html'
        params = {
            'backUrl': self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)

    def procProduceEventHappeningBigBoss(self):
        """プロデュースイベント超太客発生.
                """
        effectpath = 'produce_event/produce_chohutokyaku/effect.html'
        params = {
            'backUrl': self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)

    def procProduceEventRarityUp(self):
        """プロデュースイベント超太客発生.
        """
        effectpath = 'produce_event/produce_rareup/effect.html'
        params = {
            'backUrl': self.makeAppLinkUrl('/html5_test/'),
            'old_rarity': self.makeAppLinkUrlImg('event/raidevent/rdev_32/boss1/Raid_boss.png'),
            'new_rarity': self.makeAppLinkUrlImg('card/aina_rina/H1/Card_thumb_320_400.png'),
        }
        self.appRedirectToEffect(effectpath, params)

    def procProduceEventLastCastGet(self):
        """プロデュースイベント超太客発生.
        """
        effectpath = 'produce_event/produce_lastcastget/effect.html'
        params = {
            'backUrl': self.makeAppLinkUrl('/html5_test/'),
            'cast': self.makeAppLinkUrlImg('event/raidevent/rdev_37/boss2/chohutokyaku_cast.png'),
        }
        self.appRedirectToEffect(effectpath, params)

    def __procProduceEventBossBattle(self, winFlag, bigwinFlag):
        """ボス戦.
        """
        effectpath = 'produce_event/produce_bossbattle/effect.html'
        params = {
            'backUrl': self.makeAppLinkUrl('/html5_test/'),
            'logoPre': self.url_static + 'effect/sp/v2/produce_event/produce_bossbattle/data/',
            'winFlag': int(winFlag),
            'bigwinFlag': int(bigwinFlag),
            'playerMax': 10,
            'activePlayer': '1:2:3:4:5:6:7:8:9:10',
            'bossGauge': '0:85',
            'bossImage': self.makeAppLinkUrlImg('boss/area/Area_boss01.png'),
            'bossCastImage': self.makeAppLinkUrlImg('event/raidevent/rdev_22/boss1/Raid_boss.png'),
            'image1': self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(self.__dummycard)),
            'image2': self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image3': self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image4': self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image5': self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image6': self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image7': self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image8': self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image9': self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'image10': self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(self.__dummycard)),
            'helpFlag': 0,
            'bossDamage': 99999999999,
            'heartBefore': 2,
            'heartGotten': 55,
            'level_min': 17,
            'level_max': 20,
            'after_level':20,
            'levels': "",
            'education_levelup': 1,
            'helpPlayer': '1:2:3:4:5:6:7:8:9:10',
        }
        self.appRedirectToEffect(effectpath, params)

    def procProduceEventBossBattleWin(self):
        """ボス戦(勝利).
        """
        self.__procProduceEventBossBattle(True, False)

    def procProduceEventBossBattleLose(self):
        """ボス戦(敗北).
        """
        self.__procProduceEventBossBattle(False, False)

    def procProduceEventBossBattleBigWin(self):
        """ボス戦(大成功)
        """
        self.__procProduceEventBossBattle(True, True)
    
    def procScoutEventOpening(self):
        """スカウトイベントオープニング.
        """
        effectpath = 'scoutevent/scev_10/event_opening/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static+'effect/sp/v2/scoutevent/scev_10/event_scenario/data/',
            'logo_img' : 'event_logo.png',
            'logo_w_img' : 'event_logo_w.png',
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procScoutEventScenario(self):
        """スカウトイベントシナリオ.
        """
        scenario = self.request.get('_scn') or 1
        effectpath = 'scoutevent/scev_10/event_scenario/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static+'effect/sp/v2/scoutevent/scev_10/event_scenario/data/',
        }
        if self.isUsePCEffect():
            params.update(scn=scenario, sp_location=self.url_static+"effect/sp/v2/scoutevent/scev_10/event_scenario/data/")
        query_params = {
            'scn' : scenario,
        }
        self.appRedirectToEffect(effectpath, params, query_params=query_params)
    
    def procScoutEvent(self):
        """イベントスカウト.
        """
        self.__procScoutStart(effectname='scoutevent/scout')
    
    def procScoutEventFever(self):
        """スカウトイベントフィーバー発生.
        """
        effectpath = 'scoutevent/fever2/effect.html'
        params = {
            'endText' : u"フィーバー発生！！です！！よ！！",
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procScoutEventEnding(self):
        """スカウトイベントエンディング.
        """
        effectpath = 'scoutevent/scev_10/event_epilogue/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static+'effect/sp/v2/scoutevent/scev_10/event_scenario/data/',
            'logo_img' : 'event_logo.png',
            'logo_w_img' : 'event_logo_w.png',
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procScoutEventNone(self):
        """スカウト(なにもなかった).
        """
        self.__procScoutParam()
    
    def procScoutEventComplete(self):
        """スカウト(完了).
        """
        params = {
            'hpGauge' : u'30:20:10:0',
            'eventText' : u'なにか起こりそう',
        }
        self.__procScoutParam(**params)
    
    def procScoutEventApNone(self):
        """スカウト(行動力が足りない).
        """
        params = {
            'hpGauge' : u'30:20:10:0',
            'eventText' : u'体力がなくなった',
        }
        self.__procScoutParam(**params)
    
    def procScoutEventLevelup(self):
        """スカウト(レベルアップ).
        """
        params = {
            'expGauge' : u'70:80:90:100',
            'eventText' : u'経験値が満タンになった',
        }
        self.__procScoutParam(Defines.ScoutEventType.LEVELUP, **params)
    
    def procScoutEventTreasureGet(self):
        """スカウト(宝箱獲得).
        """
        params = {
            'eventImage' : self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlMiddleByTreasureType(Defines.TreasureType.GOLD)),
            'eventText' : u'なにか見つけた',
        }
        self.__procScoutParam(Defines.ScoutEventType.GET_TREASURE, **params)
    
    def procScoutEventCardGet(self):
        """スカウト(カード獲得).
        """
        params = {
            'eventText' : u'誰かいる',
        }
        self.__procScoutParam(Defines.ScoutEventType.GET_CARD, **params)
    
    def procScoutEventItemGet(self):
        """スカウト(アイテム獲得).
        """
        params = {
            'eventText' : u'アイテム出てきた',
        }
        self.__procScoutParam(Defines.ScoutEventType.GET_ITEM, **params)
    
    def procScoutEventHappening(self):
        """スカウト(ハプニング発生).
        """
        params = {
            'eventText' : u'電話だ',
        }
        self.__procScoutParam(Defines.ScoutEventType.HAPPENING, **params)
    
    def procScoutEventLoveTime(self):
        """逢引ラブタイム. 七夕用.
        """
        effectpath = 'scoutevent/lovetime/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)

    def procScoutEventLoveTime2(self):
        """逢引ラブタイム. 通常用.
        """
        effectpath = 'scoutevent/lovetime2/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procBattleEventOpening(self):
        """バトルイベントオープニング.
        """
        effectpath = 'btevent/btev_11/event_opening/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static + 'effect/sp/v2/btevent/btev_21/data/',
            'logo_img' : 'event_logo.png',
            'logo_w_img' : 'event_logo_w.png',
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procBattleEventResult(self):
        """バトルイベント結果報告.
        """
        effectpath = 'btevent/event_result/effect.html'
        params = {
            'effectText0' : Defines.EffectTextFormat.BATTLEEVENT_LOGINBONUS_UP % (u'キャバ王', 1, u'キャバ王'),
            'effectText1' : Defines.EffectTextFormat.BATTLEEVENT_LOGINBONUS_2,
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static + 'img/sp/large/event/btevent/btev_18/scenario/',
            'logo_img' : 'event_logo.png',
            'logo_w_img' : 'event_logo_w.png',
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procBattleEventEpilogue(self):
        """バトルイベントエピローグ.
        """
        effectpath = 'btevent/btev_11/event_epilogue/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static + 'effect/sp/v2/btevent/btev_11/data/',
            'logo_img' : 'event_logo.png',
            'logo_w_img' : 'event_logo_w.png',
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procBattleEventTree(self):
        """バトルイベントお酒演出.
        """
        effectpath = 'btevent/event_extra_alcohol/effect.html'
        item = self.request.get('_item') or 'beer'
        
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'logoPre' : self.url_static_img + 'event/btevent/btev_14/',
            'pre' : self.url_static_img,
            'item' : 'event/btevent/btev_11/btev_11_%s.png' % item,
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procBattleEventPieceComplete(self):
        """バトルイベントピースコンプリート演出.
        """
        effectpath = 'btevent/piece_complete/effect.html'
        
        mid = CardMaster.getValues(offset=1).id
        master = BackendApi.get_cardmasters([mid]).get(mid)
        
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img,
            'card' : CardUtil.makeThumbnailUrlLarge(master),
            'piece' : 'event/btevent/btev_16/piece_hr/piece_complete.png',
            'bg' : 'event/btevent/btev_16/bg_piececomplete.png',
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procComeBackCampaign(self):
        """カムバックキャンペーン.
        """
        effectpath = 'comeback_cp/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static_img,
            'i0' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GOLD),
            'i1' : ItemUtil.makeThumbnailUrlSmallByType(Defines.ItemType.GACHA_PT),
            'has_next' : True,
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procGoukonEventOpening(self):
        """合コンイベントオープニング.
        """
        effectpath = 'gcevent/gcev_02/event_opening/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static + 'effect/sp/v2/gcevent/gcev_02/data/',
            'logo_img' : 'event_logo.png',
            'logo_w_img' : 'event_logo_w.png',
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procGoukonEventNakaoshi(self):
        """合コンイベント結果報告.
        """
        effectpath = 'gcevent/gcev_02/event_nakaoshi/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static + 'effect/sp/v2/gcevent/gcev_02/data/',
            'logo_img' : 'event_logo.png',
            'logo_w_img' : 'event_logo_w.png',
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procGoukonEventEpilogue(self):
        """合コンイベントエピローグ.
        """
        effectpath = 'gcevent/gcev_02/event_epilogue/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'pre' : self.url_static + 'effect/sp/v2/gcevent/gcev_02/data/',
            'logo_img' : 'event_logo.png',
            'logo_w_img' : 'event_logo_w.png',
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procEventScenario(self):
        """イベントシナリオ.
        """
        effectpath = UrlMaker.event_scenario()
#        dataUrl = self.makeAppLinkUrl('/html5_test/EventScenarioParam/')
        number = self.request.get('_scn') or 0
        last = self.request.get('_last') or ''
        dataUrl = self.makeAppLinkUrl('/effect/eventscenario/%s/%s/html5_test' % (number, last))
        self.appRedirectToEffect2(effectpath, dataUrl)
    
    def procEventScenarioParam(self):
        """イベントシナリオのパラメータ.
            windowOpen    0
            windowClose    1
            setText    2
            setPos    3
            wait    4
            moveCast    5
            fadeCast    6
            changeBg    7
            setBgVisible    8
        """
        castdata = {
            'cast_0' : ["482_1sho_nishino.png", 0, 0, 320, 514],
            'cast_1' : ["482_2sho_nishino.png", 0, 0, 320, 514],
        }
        bgdata = {
            'bg_0' : ["bg_town.png", 0, 0, 262, 232],
            'bg_1' : ["bg_club.png", 0, 0, 262, 232],
        }
        scenario = [
            [0, 0],
            [1, 4, 4],
            [0, 6, "cast_0", 0, 100, 12],
            [2, 2,u"西野翔",u"間に合った……。"],
            [2, 2,u"",u"翔はおしゃれな紙袋に収まっている包装紙に包まれた箱を見る。"],
            [2, 2,u"西野翔",u"あとはこれを……渡すだけ……"],
            [2, 2,u"",u"翔は心臓の高鳴りを感じつつ、手作りチョコレートの入った紙袋をそっと抱きしめた。"],
            [2, 2,u"西野翔",u"…………よし！"],
            [2, 2,u"",u"数秒、自分の意志を確かめるように沈黙した後、翔は精一杯作ったチョコを渡すべく街へと飛び出した。"],
            [1, 1],
        ]
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'cast' : Json.encode(castdata),
            'bg' : Json.encode(bgdata),
            'scenario' : Json.encode(scenario),
            'pre' : self.url_static+'effect/sp/v2/event_scenario/data/test/',
        }
        self.writeDataResponseBody(params)
    
    def procCabaClubEventAnim(self):
        """経営イベント発生.
        """
        effectpath = 'cb_system/warning/effect.html'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procCabaClubResultAnim(self):
        """経営結果.
        """
        effectpath = 'cb_system/result/effect.html'
        params = {
            'proceeds' : 9999999,
            'customer' : 8888888,
            'cast':int(self.request.get('_cast') or 1) - 1,
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procSugorokuLogin(self):
        """双六ログイン.
        """
        effectpath = 'sugo6_login/effect2.html'
        ope = self.request.get('_ope') or 'none'
        dataUrl = self.makeAppLinkUrl(OSAUtil.addQuery('/html5_test/SugorokuLoginParam/', '_ope', ope))
        self.appRedirectToEffect2(effectpath, dataUrl)

    def procSugorokuLoginLoop(self):
        """双六ログイン(ゴール無し).
        """
        effectpath = 'sugo6_login_loop/effect2.html'
        ope = self.request.get('_ope') or 'none'
        dataUrl = self.makeAppLinkUrl(OSAUtil.addQuery('/html5_test/SugorokuLoginLoopParam/', '_ope', ope))
        self.appRedirectToEffect2(effectpath, dataUrl)
    
    def procSugorokuLoginParam(self):
        """双六ログインのパラメータ.
        """
        ope = self.request.get('_ope') or 'none'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'logoPre' : self.url_static_img + 'sugo6/sugo6_login/',
            'pre' : self.url_static_img,
            'lt' : 0,
            'cp' : 4,
#             'continue' : "1",
        }
        events = (
            (Defines.SugorokuMapEventType.NONE, 0),
            (Defines.SugorokuMapEventType.GO, 1),
            (Defines.SugorokuMapEventType.GO, 2),
            (Defines.SugorokuMapEventType.BACK, 1),
            (Defines.SugorokuMapEventType.BACK, 2),
            (Defines.SugorokuMapEventType.LOSE_TURN, 1),
            (Defines.SugorokuMapEventType.JUMP, 1),
        )
        items = (
            ("item/ticket_koakuma/Item_thumb_60_60.png",u'小悪魔チケット'),
            ("item/ticket_chiteki/Item_thumb_60_60.png",u'知的チケット'),
            ("item/ticket_iyashi/Item_thumb_60_60.png",u'癒しチケット'),
            ("gacha/ticket/gachaticket_hr_1.png",u'HR確定チケット'),
            ("gacha/ticket/gachaticket_sr_1.png",u'SR確定チケット'),
            ("item/ring_diamond/Item_thumb_60_60.png",u'ダイヤの指輪'),
        )
        def setMapEvent(mass, event_idx, item=None):
            event = events[event_idx]
            params['et{}'.format(mass)] = event[0]
            params['ev{}'.format(mass)] = event[1]
            ei = 'ei{}'.format(mass)
            if item is not None:
                params[ei] = item
            elif params.has_key(ei):
                del params[ei]
        
        # マップ.
        for i in xrange(27):
            idx = randint(0, len(events) - 1)
            item = None
            if randint(0, 1) == 0:
                item = randint(0, len(items) - 1)
            setMapEvent(i+1, idx, item)
        
        class MapPosition:
            def __init__(self):
                self.cp = params['cp']
                self.positions = []
            def move(self, diff):
                self.cp += diff
                self.positions.append(self.cp)
        if ope == 'completed':
            params['cp'] = 27
            params['completeitem'] = randint(0, len(items) - 1)
            params['pn'] = 0
        elif ope == 'rest':
            params['pn'] = 0
            params['lt'] = 1
        else:
            map_position = MapPosition()
            map_position.move(randint(1, 6))
#             map_position.move(6)
            if ope == 'none':
                setMapEvent(map_position.cp, 0)
            elif ope == 'item':
                setMapEvent(map_position.cp, 0, randint(0, len(items) - 1))
            elif ope == 'go_1':
                setMapEvent(map_position.cp, 1)
                map_position.move(1)
                setMapEvent(map_position.cp, 0)
            elif ope == 'go_2':
                setMapEvent(map_position.cp, 2)
                map_position.move(2)
                setMapEvent(map_position.cp, 0, randint(0, len(items) - 1))
            elif ope == 'back_1':
                setMapEvent(map_position.cp, 3)
                map_position.move(-1)
                setMapEvent(map_position.cp, 0, randint(0, len(items) - 1))
            elif ope == 'back_2':
                setMapEvent(map_position.cp, 4)
                map_position.move(-2)
                setMapEvent(map_position.cp, 0)
            elif ope == 'lose_turn':
                setMapEvent(map_position.cp, 5)
            elif ope == 'back_to_start':
                setMapEvent(map_position.cp, 6)
            params['pn'] = len(map_position.positions)
            for i,pos in enumerate(map_position.positions):
                params['p{}'.format(i)] = pos
        # アイテム.
        params['in'] = len(items)
        for i,data in enumerate(items):
            params['i{}'.format(i)] = data[0]
            params['in{}'.format(i)] = data[1]
        
        self.writeDataResponseBody(params)

    def procSugorokuLoginLoopParam(self):
        """双六ログイン(ゴール無し)のパラメータ.
        """
        ope = self.request.get('_ope') or 'none'
        params = {
            'backUrl':self.makeAppLinkUrl('/html5_test/'),
            'logoPre' : self.url_static_img + 'sugo6/sugo6_login_loop/',
            'pre' : self.url_static_img,
            'lt' : 0,
            'cp' : 4,
#             'continue' : "1",
        }
        events = (
            (Defines.SugorokuMapEventType.NONE, 0),
            (Defines.SugorokuMapEventType.GO, 1),
            (Defines.SugorokuMapEventType.GO, 2),
            (Defines.SugorokuMapEventType.BACK, 1),
            (Defines.SugorokuMapEventType.BACK, 2),
            (Defines.SugorokuMapEventType.LOSE_TURN, 1),
            (Defines.SugorokuMapEventType.JUMP, 1),
        )
        items = (
            ("item/ticket_koakuma/Item_thumb_60_60.png",u'小悪魔チケット'),
            ("item/ticket_chiteki/Item_thumb_60_60.png",u'知的チケット'),
            ("item/ticket_iyashi/Item_thumb_60_60.png",u'癒しチケット'),
            ("gacha/ticket/gachaticket_hr_1.png",u'HR確定チケット'),
            ("gacha/ticket/gachaticket_sr_1.png",u'SR確定チケット'),
            ("item/ring_diamond/Item_thumb_60_60.png",u'ダイヤの指輪'),
        )
        def setMapEvent(mass, event_idx, item=None):
            event = events[event_idx]
            params['et{}'.format(mass)] = event[0]
            params['ev{}'.format(mass)] = event[1]
            ei = 'ei{}'.format(mass)
            if item is not None:
                params[ei] = item
            elif params.has_key(ei):
                del params[ei]
        
        # マップ.
        for i in xrange(28):
            idx = randint(0, len(events) - 1)
            item = None
            if randint(0, 1) == 0:
                item = randint(0, len(items) - 1)
            setMapEvent(i+1, idx, item)
        
        class MapPosition:
            def __init__(self):
                self.cp = params['cp']
                self.positions = []
            def move(self, diff):
                self.cp += diff
                self.positions.append(self.cp)
        if ope == 'completed':
            params['cp'] = 28
            params['completeitem'] = randint(0, len(items) - 1)
            params['pn'] = 0
        elif ope == 'rest':
            params['pn'] = 0
            params['lt'] = 1
        else:
            map_position = MapPosition()
            map_position.move(randint(1, 6))
#             map_position.move(6)
            if ope == 'none':
                setMapEvent(map_position.cp, 0)
            elif ope == 'item':
                setMapEvent(map_position.cp, 0, randint(0, len(items) - 1))
            elif ope == 'go_1':
                setMapEvent(map_position.cp, 1)
                map_position.move(1)
                setMapEvent(map_position.cp, 0)
            elif ope == 'go_2':
                setMapEvent(map_position.cp, 2)
                map_position.move(2)
                setMapEvent(map_position.cp, 0, randint(0, len(items) - 1))
            elif ope == 'back_1':
                setMapEvent(map_position.cp, 3)
                map_position.move(-1)
                setMapEvent(map_position.cp, 0, randint(0, len(items) - 1))
            elif ope == 'back_2':
                setMapEvent(map_position.cp, 4)
                map_position.move(-2)
                setMapEvent(map_position.cp, 0)
            elif ope == 'lose_turn':
                setMapEvent(map_position.cp, 5)
            elif ope == 'back_to_start':
                setMapEvent(map_position.cp, 6)
            params['pn'] = len(map_position.positions)
            for i,pos in enumerate(map_position.positions):
                params['p{}'.format(i)] = pos
        # アイテム.
        params['in'] = len(items)
        for i,data in enumerate(items):
            params['i{}'.format(i)] = data[0]
            params['in{}'.format(i)] = data[1]
        
        self.writeDataResponseBody(params)

def main(request):
    return Handler.run(request)
