# -*- coding: utf-8 -*-
import settings_sub
import datetime
from platinumegg.lib import timezone
import os

class Defines:
    """アプリ定数.
    """
    ADMIN_PREFIX = 'mgr'    # 管理ページのURLの接頭語.
    MEDIA_DIR = '%s_media' % settings_sub.APP_NAME    # 静的ファイルの配置場所.
    STATIC_DIR = '%s_static' % settings_sub.APP_NAME    # 静的ファイルの配置場所.
    EFFECT_VERSION = 'v2'
    
    PROJECT_DIR = os.path.dirname(__file__)
    
    IOS_VERSION = '4.0.0'
    ANDROID_VERSION = '2.3.0'
    
    GAME_PROFILE_TAG_FORMAT = u'<game type="profile" app_id="%s" href="%s">%s</game>'
    
    # レイドの報酬配布を外部でやるフラグ.
    RAID_PRIZE_DISTRIBUTION_OUTSIDE = True
    
    #レベルアップボーナスを配布する際にどのMIDの物をみるか
    LEVELUP_BONUS_VERSION = 1

    # URLクエリ.
    URLQUERY_TIMESTAMP = u'_tm'       # タイムスタンプ.
    URLQUERY_USERID = u'_uid'       # ユーザID.
    URLQUERY_CARD = u'_card'        # カードのID.
    URLQUERY_CARD_NUM = u'_card_num'    # カードの枚数.
    URLQUERY_CTYPE = u'_ctype'      # タイプ.
    URLQUERY_CKIND = u'_ckind'      # 種類.
    URLQUERY_SKILL = u'_skill'      # スキル.
    URLQUERY_GTYPE = u'_gtype'      # ガチャタイプ.
    URLQUERY_GTAB = u'_gtab'        # ガチャのタブ.
    URLQUERY_RARE = u'_rare'        # レア度.
    URLQUERY_SORTBY = u'_sortby'    # ソート方法.
    URLQUERY_PAGE = u'_page'        # ページ番号.
    URLQUERY_GOLD = u'_gold'        # 所持金.
    URLQUERY_GOLDADD = u'_gold_add'     # 所持金加算分.
    URLQUERY_GOLDPRE = u'_gold_pre'     # 所持金変化前.
    URLQUERY_INDEX = u'_idx'        # インデクス.
    URLQUERY_STATE = u'_state'      # 状態.
    URLQUERY_STRONG = u'_strong'    # 強攻撃.
    URLQUERY_LEVELGROUP = u'_lvgrp' # レベル帯.
    URLQUERY_ALERT = u'_alert'      # アラート.
    URLQUERY_AREA = u'_area'        # エリア.
    URLQUERY_SCOUT = u'_scout'      # スカウト.
    URLQUERY_NUMBER = u'_num'       # 数.
    URLQUERY_CURRENT = u'_cur'      # 現在値.
    URLQUERY_ID = u'_id'            # 汎用ID.
    URLQUERY_ID1 = u'_id1'           # 汎用ID.
    URLQUERY_ID2 = u'_id2'           # 汎用ID.
    URLQUERY_ITEM = u'_item'        # アイテム.
    URLQUERY_CHECK_GOLD = u'_check_gold'    # お金をチェック.
    URLQUERY_CHECK_CARD = u'_check_card'    # カードをチェック.
    URLQUERY_ADD = u'_ad'           # 追加するもの.
    URLQUERY_REM = u'_rm'           # 除外するもの.
    URLQUERY_TUTO = u'_tuto'        # チュートリアルの状態.
    URLQUERY_FROM = u'_from'        # 遷移元ページ識別用.
    URLQUERY_ACCEPT = u'_accept'    # 承認.
    URLQUERY_BATTLE = u'_battlekey'   # バトルのキー.
    URLQUERY_SKIP = u'_skip'        # スキップフラグ.
    URLQUERY_SEARCH = u'_search'    # 全力探索フラグ.
    URLQUERY_ERROR = u'_er'           # エラー.
    URLQUERY_FLAG = u'_flg'           # フラグ.
    URLQUERY_SERIALCODE = u'_scode'   # シリアルコード.
    URLQUERY_HKEVEL = u'_hk'        # ハメ管理度.
    URLQUERY_BEGINER = u'_beginer'    # 初心者フラグ.
    URLQUERY_CABAKING = u'_ckt'    # キャバ王の秘宝.
    URLQUERY_CABAKINGPRE = u'_cktpre'    # キャバ王の秘宝.
    URLQUERY_DAYS = u'_days'        # 日数.
    
    STATUS_KEY_NAME = 'status'
    
    URL_COMUNITY_SP = ''    # スマホ版公式コミュニティのURL.
    URL_COMUNITY_PC = ''    # PC版公式コミュニティのURL.
    
    AP_RECOVE_TIME = 3 * 60
    BP_RECOVE_TIME = 1 * 60
    
    # アクティブな日数.
    ACTIVE_DAYS = 3
    
    PUBLISH_STATUS_COLUMN = 'pubstatus'
    MASTER_EDITTIME_COLUMN = 'edittime'
    
    # 日付変更時間.
    DATE_CHANGE_TIME = 4

    # 経営イベントの日付変更時間.
    CABARETCLUB_EVENT_DATE_CHANGE_TIME = 12
    
    # マイページで表示するデッキメンバー数.
    MYPAGE_DECK_MEMBER_NUM = 1
    
    # あいさつでもらえる引きぬきポイント.
    GREET_GACHA_PT = 5
    # あいさつでもらえる引きぬきポイント.
    GREET_GACHA_PT_FRIEND = 10
    # 一日に出来るあいさつ回数.
    GREET_COUNT_MAX_PER_DAY = 300
    # 同じ人にあいさつできる間隔.
    GREET_INTERVAL = datetime.timedelta(seconds=2*60*60)
    # あいさつコメントでもらえる引きぬきポイント.
    GREET_COMMENT_GACHA_PT = 5
    # あいさつコメントでもらえる引きぬきポイント.
    GREET_COMMENT_GACHA_PT_FRIEND = 10
    # あいさつコメント最大文字数.
    GREET_COMMENT_TEXT_MAX = 50
    
    # 思い出ガチャで持ってるカードが出る確率.
    GACHA_MEMORIES_MYCARD_RATE = 60
    
    # Boxの一覧表示数.
    BOX_PAGE_CONTENT_NUM = 9
    
    # いろいろ値の最大値.
    VALUE_MAX = 999999999
    VALUE_MAX_GACHA_PT = 999999999
    VALUE_MAX_BIG = 9999999999999999999
    
    # small int型の最大値
    UNSIGNED_SMALL_INT_MAX = 65535
    
    # デッキのカード枚数.
    DECK_CARD_NUM_MAX = 10
    
    # アイテムで増やせるカード所持数の上限.
    CARDLIMITITEM_MAX = 100
    
    # お知らせの一覧表示数.
    INFORMATION_PAGE_CONTENT_NUM = 4
    
    # Boxの一覧表示数.
    FRIEND_PAGE_CONTENT_NUM = 5
    
    # キャスト名鑑の一覧表示数.
    ALBUM_PAGE_CONTENT_NUM = 20
    
    # キャスト名鑑の一覧列数.
    ALBUM_COLUMN_CONTENT_NUM = 5
    ALBUM_LINE_CONTENT_NUM = int((ALBUM_PAGE_CONTENT_NUM + ALBUM_COLUMN_CONTENT_NUM - 1) / ALBUM_COLUMN_CONTENT_NUM)
    
    # 図鑑にストックできるカード枚数.
    ALBUM_STOCK_NUM_MAX = 100
    
    # 思い出アルバムの1列あたりのコンテンツ数.
    MEMORIES_COLUMN_CONTENT_NUM = 4
    
    # プレゼントの有効期限.
    PRESENT_RECEIVE_TIMELIMIT = datetime.timedelta(days=30)
    
    # プレゼントBOXの一覧表示数.
    PRESENT_PAGE_CONTENT_NUM = 10
    
    # ハメ管理最大レベル.
    HKLEVEL_MAX = 4
    
    # スキル最大レベル.
    SKILLLEVEL_MAX = 10
    
    # 初心者判定時間.
    BEGINER_TIME = datetime.timedelta(days=3)
    # 購入数の最大.
    BUY_NUM_MAX = 10
    
    # 合成大成功の確率(％).
    COMPOSITION_GREAT_SUCCESS_RATE = 5
    # 合成大成功時の経験値の倍率(％).
    COMPOSITION_GREAT_SUCCESS_EXP_RATE = 150
    # 同属性合成時の経験値の倍率(％).
    COMPOSITION_SAME_TYPE_EXP_RATE = 110
    
    # 進化時の引き継ぎ率.
    EVOLUTION_TAKEOVER_RATE = 5
    # レベル最大での進化時の引き継ぎ率.
    EVOLUTION_TAKEOVER_RATE_LVMAX = 10
    
    # バトル対戦相手のデッキ表示の行数.
    BATTLE_OPPONENTDECK_ROW_NUM = 2
    # バトル対戦相手のデッキ表示の列数.
    BATTLE_OPPONENTDECK_COL_NUM = int(((DECK_CARD_NUM_MAX-1) + BATTLE_OPPONENTDECK_ROW_NUM - 1) / BATTLE_OPPONENTDECK_ROW_NUM)
    
    # バトル対戦相手一覧で表示する数.
    BATTLE_OPPONENTLIST_NUMMAX = 5
    
    BATTLE_RESULT_LINE_CARD_NUM = 5
    
    # バトルの対戦相手変更可能数.
    BATTLE_OPPONENT_CHANGE_COUNT_MAX = 5
    # バトルの対戦相手の保存件数.
    BATTLE_OPPONENT_SAVE_NUM_MAX = 50
    
    # クリティカルで上昇する攻撃力(%).
    CRITICAL_POWERUP_RATE = 150
    
    # PC版の行動履歴の数.
    PC_GAMELOG_CONTENT_NUM = 50
    
    # 行動履歴の一覧表示数.
    GAMELOG_PAGE_CONTENT_NUM = 8
    
    # 初心者のレベル.
    BIGINNER_PLAYERLEVEL = 10
    
    # スカウトのエリア一覧の1ページあたりの表示数.
    SCOUTAREAMAP_CONTENTNUM_PER_PAGE = 5
    
    # スカウトでイベントが発生する頻度.
    SCOUT_EVENT_RATE = 3
    
    # 宝箱の開封期限.
    TREASURE_TIMELIMIT = 3 * 86400
    
    # レイドの救援依頼数.
    RAIDHELP_LIST_MAXLENGTH = 10
    
    # レイドでフレンドの助けを借りれる時間間隔.
    RAIDHELP_TIME_INTERVAL = 7200
    
    # レイドの救援依頼数.
    RAIDFRIEND_LIST_CONTENT_NUM_PER_PAGE = 4
    
    # 送信できるレイドの救援依頼最小数.
    RAIDFRIEND_NUM_MIN = 20
    RAIDFRIEND_NUM_MAX = 40
    
    # レイド攻撃倍率.
    RAIDATTACK_RATE_NORMAL = 100
    RAIDATTACK_RATE_STRONG = 300
    
    # レイドのコンボの制限時間のデフォルト.
    RAIDCOMBO_TIMELIMIT_DEFAULT = 300
    
    # レイド履歴一覧のページ内の表示数.
    RAIDLOG_CONTENT_NUM_PER_PAGE = 5
    PC_RAIDLOG_CONTENT_NUM_PER_PAGE = 20
    
    # バトルイベントの対戦相手数.
    BATTLEEVENT_OPPONENT_NUM = 3
    
    # バトルイベントの同じ対戦相手へ攻撃するときの時間間隔[秒].
    BATTLEEVENT_BATTLE_INTERVAL_SAME_OPPONENT = datetime.timedelta(seconds=600)
    
    # バトルイベントの対戦相手検索幅の拡張サイズ.
    BATTLEEVENT_OPPONENT_SEACH_RANGE_SPREAD_SIZE = 10
    
    # バトルイベントのポイントプレゼントのストック数.
    BATTLEEVENT_PRESENT_STOCK_NUM_MAX = 10

    # バトルチケットの勝利時の枚数
    BATTLE_TICKET_WIN = 10

    # バトルチケットの敗北時の枚数
    BATTLE_TICKET_LOSE = 1
    
    # 引き抜きガチャチケット消費数.
    GACHA_TICKET_COST_NUM = 1
    
    # スカウトイベント使用可能名刺最大数
    SCOUTEVENT_USENUM_CARD_NORMAL = 20              # 普通名刺.
    SCOUTEVENT_USENUM_CARD_HIGHGRADE = 10           # 上質名刺.
    
    # スカウトイベントガチャ専用演出を使用するか.
    SCOUTEVENTGACHA_USE_EXCLUSIVE_USE_EFFECT = True

    # スカウトイベントガチャをバレンタインにするか
    SCOUTEVENTGACHA_FOR_VALENTINE = True
    
    ANIMATION_SEPARATE_STRING = u':'
    ANIMATION_URLSEPARATE_STRING = u','
    ANIMATION_REPLACE_STRINGS = (
        (':', '__COLON__'),
    )
    
    # ○○とってテキストの区切り文字.
    STR_AND = u'と'
    
    CLOSE_EVENT_PRODUCE_NAME = 'close_produceevent'
    CLOSE_EVENT_PROCESS_NAME = 'close_raidevent'
    CLOSE_SCOUTEVENT_PROCESS_NAME = 'close_scoutevent'
    
    # プレイヤーログとフレンドログの保存件数の最大.
    if settings_sub.IS_LOCAL:
        PLAYERLOG_NUM_MAX = 10
    else:
        PLAYERLOG_NUM_MAX = 25
    
    # 全プレ時に作成するマスターデータの最小値.
    PRESENTEVERYONE_AUTO_CREATION_ID_MIN = 10000000
    
    # パネルミッションの1パネルあたりのミッション数.
    PANELMISSION_MISSIN_NUM_PER_PANEL = 9
    
    # お知らせを自動作成するマスターデータのIDの最小値.
    INFOMATION_AUTO_CREATION_ID_MIN = 10000000
    
    # レイドイベントの材料の種類の最大.
    RAIDEVENT_MATERIAL_KIND_MAX = 3
    
    # キャバクラ店舗でイベント発生間隔.
    CABARETCLUB_STORE_EVENT_INTERVAL = 1800
    
    # クロスプロモーションの開始時間と終了時間
    CROSS_PROMO_START_TIME = datetime.datetime.strptime('2017-1-23 18:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.TZ_DB)
    CROSS_PROMO_END_TIME = datetime.datetime.strptime('2017-1-30 17:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.TZ_DB)

    # 経験値 X 倍キャンペーン開始時間と終了時間.
    EXP_RATE_OVER = 1.5 # 1.5倍
    EXP_START_TIME =  datetime.datetime.strptime('2016-4-28 17:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.TZ_DB)
    EXP_END_TIME = datetime.datetime.strptime('2016-5-12 15:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.TZ_DB)
    
    class MasterData:
        TIARA_ID = 40004
    class MaintenanceType:
        """メンテナンスの種類.
        """
        (
            NONE,               # メンテ状態じゃない.
            EMERGENCY,          # 緊急.
            REGULAR,            # 定期.
            EMERGENCY_PLATFORM, # 緊急(プラットフォームメンテ).
            REGULAR_PLATFORM,   # 定期(プラットフォームメンテ).
        ) = range(5)
        NAMES = {
            NONE:u'メンテ状態じゃない',
            EMERGENCY:u'緊急',
            REGULAR:u'定期',
            EMERGENCY_PLATFORM:u'緊急(プラットフォームメンテ)',
            REGULAR_PLATFORM:u'定期(プラットフォームメンテ)',
        }
    
    class PublishStatus:
        """公開状態.
        """
        (
            PUBLIC,
            PUBLIC_DEV,
            SECRET,
         ) = range(3)
        NAMES = {
            PUBLIC:u'公開',
            PUBLIC_DEV:u'開発環境のみ公開',
            SECRET:u'非公開',
        }
        OPEN_STATAS_LIST = (PUBLIC,)
        CLOSED_STATAS_LIST = list(set(NAMES.keys()) - set(OPEN_STATAS_LIST))
    
    class WeekDay:
        """曜日.
        """
        (
            MONDAY,
            TUESDAY,
            WEDNESDAY,
            THURSDAY,
            FRIDAY,
            SATURDAY,
            SUNDAY,
        ) = range(7)
        (
            EVERYDAY,   # 毎日.
            ALL         # 全て.
        ) = range(0xff, 0xff+2)
        NAMES = {
            MONDAY:u'月曜',
            TUESDAY:u'火曜',
            WEDNESDAY:u'水曜',
            THURSDAY:u'木曜',
            FRIDAY:u'金曜',
            SATURDAY:u'土曜',
            SUNDAY:u'日曜',
            EVERYDAY:u'毎日',
            ALL:u'全て',
        }
        LIST = (
            MONDAY,
            TUESDAY,
            WEDNESDAY,
            THURSDAY,
            FRIDAY,
            SATURDAY,
            SUNDAY,
        )
    
    class TutorialStatus:
        """チュートリアルの状態.
        """
        CHAPTER_REGIST = 0x0000     # 登録.
#        CHAPTER_SCOUT00 = 0x0100    # スカウト(キャスト発見).
        CHAPTER_EVOL00 = 0x0100     # ハメ管理.
        CHAPTER_SCOUT01 = 0x0200    # スカウト(キャスト発見).
#        CHAPTER_SCOUT02 = 0x0300    # スカウト(宝箱発見).
        CHAPTER_SCOUT03 = 0x0300    # スカウト(完了).
        CHAPTER_BOSS00 = 0x0400     # ボス戦1回目.
        CHAPTER_COMPOSITION00 = 0x0500  # 教育.
        CHAPTER_BOSS01 = 0x600     # ボス戦2回目.
        CHAPTER_COMPLETE = 0x0700   # チュートリアル完了.
        
        (
            REGIST_SELECT,      # タイプ選択.
            REGIST_YESNO,       # タイプ選択確認.
            REGIST_COMPLETE,    # 登録完了.
        ) = range(CHAPTER_REGIST, CHAPTER_REGIST+3)
#        (
#            SCOUT00_TOP,        #スカウトTOP.
#            SCOUT00_ANIM,       #スカウトアニメーション.
#            SCOUT00_CARDGET,    #スカウト成功.
#        ) = range(CHAPTER_SCOUT00, CHAPTER_SCOUT00+3)
        (
#            EVOL00_BASESELECT,  #ハメ管理ベース選択.
#            EVOL00_MATERIAL,    #ハメ管理素材選択.
            EVOL00_YESNO,       #ハメ管理合成確認.
            EVOL00_ANIM,        #ハメ管理アニメーション.
            EVOL00_COMPLETE,    #ハメ管理合成結果.
            EVOL00_ALBUM,       #思い出アルバム.
        ) = range(CHAPTER_EVOL00, CHAPTER_EVOL00+4)
        (
            SCOUT01_TOP,        #スカウトTOP.
            SCOUT01_ANIM,       #スカウトアニメーション.
            SCOUT01_CARDGET,    #スカウト成功.
        ) = range(CHAPTER_SCOUT01, CHAPTER_SCOUT01+3)
#        (
#            SCOUT02_ANIM,       #スカウトアニメーション.
#            SCOUT02_RESULT,     #宝箱発見.
#        ) = range(CHAPTER_SCOUT02, CHAPTER_SCOUT02+2)
        (
            SCOUT03_ANIM,       #スカウトアニメーション.
            SCOUT03_RESULTANIM, #スカウト完了アニメーション.
            SCOUT03_BOSS,       #ボス出現アニメーション.
        ) = range(CHAPTER_SCOUT03, CHAPTER_SCOUT03+3)
        (
            BOSS00_PRE,         #ボス登場.
            BOSS00_ANIM,        #ボス戦アニメーション.
            BOSS00_RESULT,      #ボス敗北(カードの付与).
        ) = range(CHAPTER_BOSS00, CHAPTER_BOSS00+3)
        (
#            COMPOSITION00_BASESELECT,   #教育ベース選択.
#            COMPOSITION00_MATERIAL,     #教育素材選択.
            COMPOSITION00_YESNO,        #教育合成確認.
            COMPOSITION00_ANIM,         #教育アニメーション.
            COMPOSITION00_COMPLETE,     #教育合成結果画面.
        ) = range(CHAPTER_COMPOSITION00, CHAPTER_COMPOSITION00+3)
        (
            BOSS01_PRE,         # ボス登場.
            BOSS01_ANIM,        # ボス戦アニメーション.
            BOSS01_RESULT,      # ボス勝利.
        ) = range(CHAPTER_BOSS01, CHAPTER_BOSS01+3)
        (
            COMPLETE_HOWTOCABA,    # How To キャバ王.
            COMPLETE_MATOME,    # まとめ.
        ) = range(CHAPTER_COMPLETE, CHAPTER_COMPLETE+2)
        
        COMPLETED = 0xffff      # チュートリアル完了.
        
        NAMES = {
            REGIST_SELECT : u'タイプ選択',
            REGIST_YESNO : u'タイプ確認',
            REGIST_COMPLETE : u'タイプ決定',
            
#            SCOUT00_TOP : u'スカウト',
#            SCOUT00_ANIM : u'スカウトアニメーション',
#            SCOUT00_CARDGET : u'キャスト獲得',
            
#            EVOL00_BASESELECT : u'ハメ管理 ベースカード選択',
#            EVOL00_MATERIAL : u'ハメ管理 素材カード選択',
            EVOL00_YESNO : u'ハメ管理 合成確認',
            EVOL00_ANIM : u'ハメ管理アニメーション',
            EVOL00_COMPLETE : u'ハメ管理 結果',
            EVOL00_ALBUM : u'思い出アルバム',
            
            SCOUT01_TOP : u'スカウト',
            SCOUT01_ANIM : u'スカウトアニメーション',
            SCOUT01_CARDGET : u'キャスト獲得',
            
#            SCOUT02_ANIM : u'スカウトアニメーション',
#            SCOUT02_RESULT : u'宝箱発見',
            
            SCOUT03_ANIM : u'スカウトアニメーション',
            SCOUT03_RESULTANIM : u'スカウト完了アニメーション',
            SCOUT03_BOSS : u'ボス出現アニメーション',
            
            BOSS00_PRE : u'ボス出現',
            BOSS00_ANIM : u'ボス戦アニメーション',
            BOSS00_RESULT : u'教育をしよう',
            
#            COMPOSITION00_BASESELECT : u'教育 ベースカード選択',
#            COMPOSITION00_MATERIAL : u'教育 素材カード選択',
            COMPOSITION00_YESNO : u'教育 合成確認',
            COMPOSITION00_ANIM : u'教育アニメーション',
            COMPOSITION00_COMPLETE : u'教育 結果',
            
            BOSS01_PRE : u'ボスに再挑戦',
            BOSS01_ANIM : u'ボス戦アニメーション',
            BOSS01_RESULT : u'ボスに勝利',
            
            COMPLETE_HOWTOCABA : u'How to キャバ王',
            COMPLETE_MATOME : u'チュートリアルのまとめ',
            COMPLETED : u'チュートリアル完了',
        }
        FLOW = (
            REGIST_SELECT,      # タイプ選択.
#            REGIST_YESNO,       # タイプ選択確認.
            REGIST_COMPLETE,    # 登録完了.
            
#            SCOUT00_TOP,        #スカウトTOP.
#            SCOUT00_ANIM,       #スカウトアニメーション.
#            SCOUT00_CARDGET,    #スカウト成功.
            
#            EVOL00_BASESELECT,  #ハメ管理ベース選択.
#            EVOL00_MATERIAL,    #ハメ管理素材選択.
            EVOL00_YESNO,       #ハメ管理合成確認.
            EVOL00_ANIM,        #ハメ管理アニメーション.
            EVOL00_COMPLETE,    #ハメ管理合成結果.
            EVOL00_ALBUM,       #思い出アルバム.
            
            SCOUT01_TOP,        #スカウトTOP.
            SCOUT01_ANIM,       #スカウトアニメーション.
            SCOUT01_CARDGET,    #スカウト成功.
            
#            SCOUT02_ANIM,       #スカウトアニメーション.
#            SCOUT02_RESULT,     #スカウト宝箱獲得完了.
            
            SCOUT03_ANIM,       #スカウトアニメーション.
            SCOUT03_RESULTANIM, #スカウト完了アニメーション.
            SCOUT03_BOSS,       #ボス出現アニメーション.
            
            BOSS00_PRE,         #ボス登場.
            BOSS00_ANIM,        #ボス戦アニメーション.
            BOSS00_RESULT,      #ボス敗北(カードの付与).
            
#            COMPOSITION00_BASESELECT,   #教育ベース選択.
#            COMPOSITION00_MATERIAL,     #教育素材選択.
            COMPOSITION00_YESNO,        #教育合成確認.
            COMPOSITION00_ANIM,         #教育アニメーション.
            COMPOSITION00_COMPLETE,     #教育合成結果画面.
            
            BOSS01_PRE,         #ボス登場.
            BOSS01_ANIM,        #ボス戦アニメーション.
            BOSS01_RESULT,      #ボス勝利.
            
            COMPLETE_HOWTOCABA,    # How To キャバ王.
            COMPLETE_MATOME,    # まとめ.
            COMPLETED,          # チュートリアル完了報酬.
        )
        ANIMATIONS = (
            EVOL00_ANIM,        #ハメ管理アニメーション.
#            SCOUT00_ANIM,       #スカウトアニメーション.
            SCOUT01_ANIM,       #スカウトアニメーション.
#            SCOUT02_ANIM,       #スカウトアニメーション.
            SCOUT03_ANIM,       #スカウトアニメーション.
            SCOUT03_RESULTANIM, #スカウト完了アニメーション.
            SCOUT03_BOSS,       #ボス出現アニメーション.
            BOSS00_ANIM,        #ボス戦アニメーション.
            COMPOSITION00_ANIM,         #教育アニメーション.
            BOSS01_ANIM,        #ボス戦アニメーション.
        )
        FLOW_EXCLUDE_ANIMATIONS = tuple([st for st in FLOW if not st in ANIMATIONS])
        
        # スカウトのチャプター.
        SCOUT_CHAPTERS = (
#              CHAPTER_SCOUT00,
              CHAPTER_SCOUT01,
#              CHAPTER_SCOUT02,
              CHAPTER_SCOUT03
        )
        SCOUT_CHAPTER_NUM = len(SCOUT_CHAPTERS)
    
    class CharacterType:
        """プレイヤー,カードのタイプ.
        """
        NUM_MAX = 3
        NONE = 0
        ALL = 255
        (
            TYPE_001,
            TYPE_002,
            TYPE_003,
        ) = range(1, NUM_MAX+1)
        
        LIST = (
            TYPE_001,
            TYPE_002,
            TYPE_003,
        )
        
        NAMES = {
            TYPE_001 : u'魔',
            TYPE_002 : u'知',
            TYPE_003 : u'癒',
        }
        SKILL_TARGET_NAMES = {
            ALL : u'全て',
            TYPE_001 : u'魔',
            TYPE_002 : u'知',
            TYPE_003 : u'癒',
        }
        SKILL_TARGET_NAMES_SUB = {
            NONE : u'無',
            ALL : u'全て',
            TYPE_001 : u'魔',
            TYPE_002 : u'知',
            TYPE_003 : u'癒',
        }
        BOSS_NAMES = {
            NONE : u'無',
            TYPE_001 : u'魔',
            TYPE_002 : u'知',
            TYPE_003 : u'癒',
        }
        ICONS = {
            TYPE_001 : 'common/zokusei_1.png',
            TYPE_002 : 'common/zokusei_2.png',
            TYPE_003 : 'common/zokusei_3.png',
        }
        COLORS = {
            TYPE_001 : '#ff3030',
            TYPE_002 : '#30ff30',
            TYPE_003 : '#3030ff',
        }
        LONG_NAMES = {  # 仕様書にないのにいつの間にか定着している名前..
            TYPE_001 : u'小悪魔',
            TYPE_002 : u'知的',
            TYPE_003 : u'癒し',
        }
        
        class Effect:
            """演出で定義されてるタイプがちょっと違う..
            """
            (
                NORMAL,
                KOAKUMA,
                IYASHI,
                CHISEI,
            ) = range(4)
            TEXT_COLOR = {
                NORMAL : None,
                KOAKUMA : u'#f02020',
                IYASHI : u'#5050ff',
                CHISEI : u'#20f020',
            }
        
        SKILL_TARGET_TO_EFFECT = {
            ALL : Effect.NORMAL,
            TYPE_001 : Effect.KOAKUMA,
            TYPE_002 : Effect.CHISEI,
            TYPE_003 : Effect.IYASHI,
        }
    
    class CardKind:
        """カードの種類.
        """
        NUM_MAX = 4
        (
            NORMAL,
            TRAINING,
            EVOLUTION,
            SKILL,
        ) = range(1, NUM_MAX+1)
        
        SPECIAL_LIST = (
            TRAINING,
            EVOLUTION,
            SKILL,
        )
        
        NAMES = {
            NORMAL : u'通常',
            TRAINING : u'教育',
            EVOLUTION : u'進化',
            SKILL : u'スキルLvup',
        }
        UNIT = {
            NORMAL : u'人',
            TRAINING : u'個',
            EVOLUTION : u'個',
            SKILL : u'個',
        }
        COMPOSITION_MATERIAL = (
            NORMAL,
            TRAINING,
#            EVOLUTION,
            SKILL,
        )
        COMPOSITION_MATERIAL_NOSKILL = (
            NORMAL,
            TRAINING,
#            EVOLUTION,
#            SKILL,
        )
        class ListFilterType():
            (
                CAST_ONLY,         # キャストのみ.
                ACCESSORIES_ONLY,  # アクセサリのみ.
                RING_ONLY,         # 指輪のみ.
                ALL_KIND,          # 全て.
            ) = range(4)
            
            NAMES = {
                CAST_ONLY : u'キャストのみ',
                ACCESSORIES_ONLY : u'アクセサリのみ',
                RING_ONLY : u'指輪のみ',
                ALL_KIND : u'全て',
            }
        
        LIST_FILTER_TABLE = {
            ListFilterType.CAST_ONLY : (NORMAL,),
            ListFilterType.ACCESSORIES_ONLY : (TRAINING,SKILL),
            ListFilterType.RING_ONLY : (EVOLUTION,),
            ListFilterType.ALL_KIND : (NORMAL, TRAINING, EVOLUTION, SKILL),
        }
    
    class CardGrowthType:
        """カードの成長タイプ.
        """
        NUM_MAX = 3
        (
            PRECOCIOUS,
            BALANCE,
            BANSEI,
        ) = range(1, NUM_MAX+1)
        
        NAMES = {
            PRECOCIOUS : u'早熟',
            BALANCE : u'バランス',
            BANSEI : u'晩成',
        }
    class ItemEffect:
        """アイテムの効果.
        """
        NUM_MAX = 19
        (
            ACTION_SMALL_RECOVERY,          # 行動力小回復.
            ACTION_MIDDLE_RECOVERY,         # 行動力中回復.
            ACTION_ALL_RECOVERY,            # 行動力全回復.
        ) = range(0x01, 0x01+3)
        (
            TENSION_SMALL_RECOVERY,         # テンション小回復.
            TENSION_MIDDLE_RECOVERY,        # テンション中回復.
            TENSION_ALL_RECOVERY,           # テンション全回復.
        ) = range(0x11, 0x11+3)
        (
            GACHA_PT_ACQUISITION_0,         # 引抜Pt.
            GACHA_PT_ACQUISITION_1,         # 引抜Pt.
            GACHA_PT_ACQUISITION_2,         # 引抜Pt.
            GACHA_PT_ACQUISITION_3,         # 引抜Pt.
            GACHA_PT_ACQUISITION_4,         # 引抜Pt.
        ) = range(0x21, 0x21+5)
        (
            GOLD_ACQUISITION_0,             # キャバゴールド.
            GOLD_ACQUISITION_1,             # キャバゴールド.
            GOLD_ACQUISITION_2,             # キャバゴールド.
            GOLD_ACQUISITION_3,             # キャバゴールド.
            GOLD_ACQUISITION_4,             # キャバゴールド.
        ) = range(0x31, 0x31+5)
        (
            CARD_BOX_EXPANSION,             # カードBOX拡張.
        ) = range(0x41, 0x41+1)
        (
            SCOUT_CARD_NORMAL,              # 普通名刺.
            SCOUT_CARD_HIGHGRADE,           # 上質名刺.
        ) = range(0x51, 0x51+2)
        (
            SCOUT_GUM,                      # ガム.
        ) = range(0x61, 0x61+1)
        (
            CABACLUB_SCOUTMAN,              # スカウトマン.
            CABACLUB_PREFERENTIAL,          # 優待券.
            CABACLUB_BARRIER,               # バリアアイテム.
        ) = range(0x71, 0x71+3)
        (
            # 超接客
            CHRISTMAS_CAKE,
            KIMONO,
            CHOCO,
        ) = range(0x81, 0x81+3)
        
        NAMES = {
            ACTION_SMALL_RECOVERY : u'赤ハブドリンク[小]',
            ACTION_MIDDLE_RECOVERY : u'赤ハブドリンク[中]',
            ACTION_ALL_RECOVERY : u'赤ハブドリンク[大]',
            TENSION_SMALL_RECOVERY : u'気力回復剤[小]',
            TENSION_MIDDLE_RECOVERY : u'気力回復剤[中]',
            TENSION_ALL_RECOVERY : u'気力回復剤[大]',
            GACHA_PT_ACQUISITION_0 : u'引抜Pt0',
            GACHA_PT_ACQUISITION_1 : u'引抜Pt1',
            GACHA_PT_ACQUISITION_2 : u'引抜Pt2',
            GACHA_PT_ACQUISITION_3 : u'引抜Pt3',
            GACHA_PT_ACQUISITION_4 : u'引抜Pt4',
            GOLD_ACQUISITION_0 : u'キャバゴールド0',
            GOLD_ACQUISITION_1 : u'キャバゴールド1',
            GOLD_ACQUISITION_2 : u'キャバゴールド2',
            GOLD_ACQUISITION_3 : u'キャバゴールド3',
            GOLD_ACQUISITION_4 : u'キャバゴールド4',
            CARD_BOX_EXPANSION : u'カードBOX拡張',
            SCOUT_CARD_NORMAL : u'普通名刺',
            SCOUT_CARD_HIGHGRADE : u'上質名刺',
            SCOUT_GUM : u'ガム',
            CABACLUB_SCOUTMAN : u'スカウトマン増員',
            CABACLUB_PREFERENTIAL : u'優待券配布',
            CABACLUB_BARRIER : u'バリア的なアイテム',
            CHRISTMAS_CAKE : u'クリスマスケーキ',           # (超接客)
            KIMONO : u'着物', # (超接客)
            CHOCO : u'チョコ', # (超接客)
        }
        USE_ABLE = (
            ACTION_SMALL_RECOVERY,          # 行動力小回復
            ACTION_MIDDLE_RECOVERY,         # 行動力中回復
            ACTION_ALL_RECOVERY,            # 行動力全回復
            TENSION_SMALL_RECOVERY,         # テンション小回復
            TENSION_MIDDLE_RECOVERY,        # テンション中回復
            TENSION_ALL_RECOVERY,           # テンション全回復
            GACHA_PT_ACQUISITION_0,         # 引抜Pt.
            GACHA_PT_ACQUISITION_1,         # 引抜Pt.
            GACHA_PT_ACQUISITION_2,         # 引抜Pt.
            GACHA_PT_ACQUISITION_3,         # 引抜Pt.
            GACHA_PT_ACQUISITION_4,         # 引抜Pt.
            GOLD_ACQUISITION_0,             # キャバゴールド.
            GOLD_ACQUISITION_1,             # キャバゴールド.
            GOLD_ACQUISITION_2,             # キャバゴールド.
            GOLD_ACQUISITION_3,             # キャバゴールド.
            GOLD_ACQUISITION_4,             # キャバゴールド.
            CARD_BOX_EXPANSION,             # カードBOX拡張.
            SCOUT_GUM,                      # ガム.
            CABACLUB_PREFERENTIAL,          # 優待券.
            CABACLUB_BARRIER,               # バリアアイテム.
        )
        # 一度に使用できる上限(未指定は無制限).
        USE_NUM_MAX = {
            ACTION_ALL_RECOVERY : 1,            # 行動力全回復.
            TENSION_ALL_RECOVERY : 1,           # テンション全回復.
            CARD_BOX_EXPANSION : 1,             # カードBOX拡張.
            SCOUT_GUM : 1,                      # ガム.
            CABACLUB_PREFERENTIAL : 1,          # 優待券.
            CABACLUB_BARRIER : 1,               # バリアアイテム.
            CHRISTMAS_CAKE : 1,                 # クリスマスケーキ. (超接客)
            KIMONO : 1,                         # 着物. (超接客)
            CHOCO : 1,                          # チョコ. (超接客)
        }
        # 体力回復アイテム.
        ACTION_RECOVERY_ITEMS = (
            ACTION_ALL_RECOVERY,   # 体力全回復
            ACTION_MIDDLE_RECOVERY,         # 行動力中回復
            ACTION_SMALL_RECOVERY,          # 行動力小回復
        )
        # 気力回復アイテム.
        TENSION_RECOVERY_ITEMS = (
            TENSION_ALL_RECOVERY,  # 気力全回復
            TENSION_MIDDLE_RECOVERY,        # テンション中回復
            TENSION_SMALL_RECOVERY,         # テンション小回復
        )
        SCOUT_CARD_ITEMS = (
            SCOUT_CARD_NORMAL,              # 普通名刺.
            SCOUT_CARD_HIGHGRADE,           # 上質名刺.
        )
        GACHA_PT_ACQUISITION_ITEMS = (
            GACHA_PT_ACQUISITION_0,         # 引抜Pt.
            GACHA_PT_ACQUISITION_1,         # 引抜Pt.
            GACHA_PT_ACQUISITION_2,         # 引抜Pt.
            GACHA_PT_ACQUISITION_3,         # 引抜Pt.
            GACHA_PT_ACQUISITION_4,         # 引抜Pt.
        )
        GOLD_ACQUISITION_ITEMS = (
            GOLD_ACQUISITION_0,             # キャバゴールド.
            GOLD_ACQUISITION_1,             # キャバゴールド.
            GOLD_ACQUISITION_2,             # キャバゴールド.
            GOLD_ACQUISITION_3,             # キャバゴールド.
            GOLD_ACQUISITION_4,             # キャバゴールド.
        )
        SCOUT_GUM_ITEMS = (
            SCOUT_GUM,                      # ガム.
        )
        CABACLUB_STORE_ITEMS = (
            CABACLUB_SCOUTMAN,              # スカウトマン.
            CABACLUB_PREFERENTIAL,          # 優待券.
            CABACLUB_BARRIER,               # バリアアイテム.
        )
        # 全力探索
        PRODUCE_ONLY_ITEMS = (
            CHRISTMAS_CAKE,                    # クリスマスケーキ
            KIMONO,
            CHOCO,
        )
    
    class PresentTopic:
        """プレゼントのトピック.
        """
        NUM_MAX = 4
        RANGE = range(1, NUM_MAX+1)
        (
            ALL,
            CARD,
            ITEM,
            ETC,
        ) = RANGE
    
    class ItemType:
        """アイテムの種類.
        """
        NUM_MAX = 20
        (
            GOLD,                   # お金.
            GACHA_PT,               # 引きぬきポイント.
            ITEM,                   # アイテム.
            CARD,                   # カード.
            _TROPHY_,               # トロフィ(欠番).
            RAREOVERTICKET,         # レア以上チケット
            TRYLUCKTICKET,          # 運試しチケット.
            MEMORIESTICKET,         # 思い出チケット.
            GACHATICKET,            # 引き抜きチケット.
            GOLDKEY,                # 金の鍵.
            SILVERKEY,              # 銀の鍵.
            CABARETKING_TREASURE,   # キャバ王の秘宝.
            DEMIWORLD_TREASURE,     # 裏社会の秘宝.
            EVENT_GACHATICKET,      # イベントガチャチケット.
            ADDITIONAL_GACHATICKET,      # 追加分ガチャチケット.
            SCOUTEVENT_TANZAKU,     # スカウトイベントの短冊.
            CABARETCLUB_SPECIAL_MONEY,   # キャバクラシステムの特別なマネー.
            CABARETCLUB_HONOR_POINT,     # 名声ポイント.
            PLATINUM_PIECE,         # ピースのかけら.
            CRYSTAL_PIECE,          # クリスタルの欠片
        ) = range(1, NUM_MAX+1)
        NAMES = {
            GOLD : u'キャバゴールド',
            GACHA_PT:u'引抜Pt',
            ITEM:u'アイテム',
            CARD:u'キャスト',
            RAREOVERTICKET : u'レア以上チケット',
            TRYLUCKTICKET : u'運試しチケット',
            MEMORIESTICKET : u'思い出チケット',
            GACHATICKET : u'引抜チケット',
            GOLDKEY : u'金のカギ',
            SILVERKEY : u'銀のカギ',
            CABARETKING_TREASURE : u'キャバ王の秘宝',
            DEMIWORLD_TREASURE : u'キャバ王の秘宝',    # 裏社会の秘宝.
            PLATINUM_PIECE : u'プラチナのかけら',
            CRYSTAL_PIECE : u'クリスタルのかけら',
            EVENT_GACHATICKET : u'イベントガチャチケット',
            ADDITIONAL_GACHATICKET : u'追加分ガチャチケット',
            SCOUTEVENT_TANZAKU : u'スカウトイベントの短冊',
            CABARETCLUB_SPECIAL_MONEY : u'経営マネー',
            CABARETCLUB_HONOR_POINT : u'名誉pt',
        }
        SMALL_NAMES = {
            GOLD : u'CG',
        }
        UNIT = {
            GOLD:u'CG',
            GACHA_PT:u'',
            RAREOVERTICKET : u'枚',
            TRYLUCKTICKET : u'枚',
            MEMORIESTICKET : u'枚',
            GACHATICKET : u'枚',
            ITEM : u'',
            CARD : u'',
            GOLDKEY : u'個',
            SILVERKEY : u'個',
            CABARETKING_TREASURE : u'個',
            DEMIWORLD_TREASURE : u'個',
            PLATINUM_PIECE : u'個',
            CRYSTAL_PIECE : u'個',
            EVENT_GACHATICKET : u'枚',
            ADDITIONAL_GACHATICKET : u'枚',
            SCOUTEVENT_TANZAKU : u'',
            CABARETCLUB_SPECIAL_MONEY : u'',
            CABARETCLUB_HONOR_POINT : u'',
        }
        THUMBNAIL = {
            GOLD:u'item/cabagold_1000',
            GACHA_PT:u'item/hikinukipt_250',
            RAREOVERTICKET : u'item/ticket_rare',
            TRYLUCKTICKET:u'item/ticket_lucky',
            MEMORIESTICKET:u'item/ticket_memory',
            GACHATICKET:u'item/ticket_hikinuki',
            GOLDKEY : u'item/key_gold',
            SILVERKEY : u'item/key_silver',
            CABARETKING_TREASURE : u'item/cabarettreasure',
            DEMIWORLD_TREASURE : u'item/cabarettreasure',
            PLATINUM_PIECE : u'item/piece_platinum',
            CRYSTAL_PIECE : u'item/piece_crystal',
            CABARETCLUB_SPECIAL_MONEY : u'item/cb_money',
            CABARETCLUB_HONOR_POINT : u'item/honor_pt',
        }
        PRESENT_TYPES = dict([(itype, NAMES[itype])
            for itype in (
                GOLD,           # お金.
                GACHA_PT,       # 引きぬきポイント.
                ITEM,           # アイテム.
                CARD,           # カード.
                RAREOVERTICKET, # レア以上チケット
                TRYLUCKTICKET,  # 運試しチケット.
                MEMORIESTICKET, # 思い出チケット.
                GACHATICKET,    # 引き抜きチケット.
                GOLDKEY,        # 金の鍵.
                SILVERKEY,      # 銀の鍵.
                EVENT_GACHATICKET,  #イベントガチャチケット.
                ADDITIONAL_GACHATICKET,      # 追加分ガチャチケット.
                SCOUTEVENT_TANZAKU,     # スカウトイベントの短冊.
                CABARETCLUB_SPECIAL_MONEY,   # キャバクラシステムの特別なマネー.
                CABARETCLUB_HONOR_POINT,     # 名声ポイント.
                PLATINUM_PIECE, #プラチナのかけら.
                CRYSTAL_PIECE, # クリスタルの欠片
            )
        ])
        BUY_ABLE_TYPES = dict([(itype, NAMES[itype])
            for itype in (
                ITEM,           # アイテム.
                CARD,           # カード.
                GACHATICKET,    # 引抜チケット.
                TRYLUCKTICKET,  # 運試しチケット.
                MEMORIESTICKET, # 思い出チケット.
                GOLDKEY,        # 金の鍵.
                SILVERKEY,      # 銀の鍵.
                CABARETCLUB_SPECIAL_MONEY,   # キャバクラシステムの特別なマネー.
                CABARETCLUB_HONOR_POINT,     # 名声ポイント.
            )
        ])
        TREASURE_ITEM_TYPES = dict([(itype, NAMES[itype])
            for itype in (
                GOLD,           # お金.
                GACHA_PT,       # 引きぬきポイント.
                ITEM,           # アイテム.
                CARD,           # カード.
                RAREOVERTICKET, # レア以上チケット
                GACHATICKET,    # 引抜チケット.
                TRYLUCKTICKET,  # 運試しチケット.
                MEMORIESTICKET, # 思い出チケット.
                ADDITIONAL_GACHATICKET,      # 追加分ガチャチケット.
                CABARETCLUB_SPECIAL_MONEY,   # キャバクラシステムの特別なマネー.
                CABARETCLUB_HONOR_POINT,     # 名声ポイント.
            )
        ])
        TRADE_TYPES = dict([(itype, NAMES[itype])
            for itype in (
                ITEM,           # アイテム.
                CARD,           # カード.
                RAREOVERTICKET, # レア以上チケット
                TRYLUCKTICKET,  # 運試しチケット.
                MEMORIESTICKET, # 思い出チケット.
                GACHATICKET,    # 引き抜きチケット.
                ADDITIONAL_GACHATICKET,      # 追加分ガチャチケット.
                CABARETCLUB_SPECIAL_MONEY,   # キャバクラシステムの特別なマネー.
                CABARETCLUB_HONOR_POINT,     # 名声ポイント.
            )
        ])
        TRADE_NUM_MAX = {   # 最大交換可能数.
            CARD : 10,           # カード.
        }
        TICKET_ITEM_TYPES = dict([(itype, NAMES[itype])
            for itype in (
                RAREOVERTICKET, # レア以上チケット
                TRYLUCKTICKET,  # 運試しチケット.
                MEMORIESTICKET, # 思い出チケット.
                GACHATICKET,    # 引き抜きチケット.
            )
        ])
        AUTO_RECEIVE_TYPES = (
            GOLD,                   # お金.
            GACHA_PT,               # 引きぬきポイント.
        )
    
    PRESENT_TOPIC_TABLE = {
        ItemType.GOLD : PresentTopic.ETC,
        ItemType.GACHA_PT:PresentTopic.ETC,
        ItemType.ITEM : PresentTopic.ITEM,
        ItemType.CARD : PresentTopic.CARD,
        ItemType.RAREOVERTICKET : PresentTopic.ITEM,
        ItemType.TRYLUCKTICKET : PresentTopic.ITEM,
        ItemType.MEMORIESTICKET : PresentTopic.ITEM,
        ItemType.GACHATICKET : PresentTopic.ITEM,
        ItemType.GOLDKEY : PresentTopic.ITEM,
        ItemType.SILVERKEY : PresentTopic.ITEM,
        ItemType.EVENT_GACHATICKET : PresentTopic.ITEM,
        ItemType.ADDITIONAL_GACHATICKET : PresentTopic.ITEM,
        ItemType.CABARETCLUB_SPECIAL_MONEY : PresentTopic.ETC,
        ItemType.CABARETCLUB_HONOR_POINT : PresentTopic.ETC,
        ItemType.PLATINUM_PIECE : PresentTopic.ETC,
    }
    
    class PlayerLogType:
        """行動履歴のタイプ.
        """
        NUM_MAX = 4
        (
            BATTLE_RECEIVE_WIN,         # バトルで挑まれて勝った.
            BATTLE_RECEIVE_LOSE,        # バトルで挑まれて負けた.
            BATTLE_WIN,                 # バトルを挑んで勝った.
            BATTLE_LOSE,                # バトルを挑んで負けた.
        ) = range(1, NUM_MAX+1)
    
    class FriendLogType:
        """仲間の近況のタイプ.
        """
        NUM_MAX = 6
        (
            BOSS_WIN,           # ボスに勝った.
            SCOUT_CLEAR,        # スカウトクリア.
            EVENTBOSS_WIN,      # ボスに勝った(イベントスカウト).
            EVENTSTAGE_CLEAR,   # スカウトクリア(イベントスカウト).
            RAIDEVENTBOSS_WIN,      # ボスに勝った(レイドイベントスカウト).
            RAIDEVENTSTAGE_CLEAR,   # スカウトクリア(レイドイベントスカウト).
        ) = range(1, NUM_MAX+1)
    
    class CardSortType:
        CTIME_REV = '-ctime'    #新着順.
        CTIME = 'ctime'         #古い順.
        RARE_REV = '-rare'      #レアリティが高い順.
        RARE = 'rare'           #レアリティが低い順.
        LEVEL_REV = '-level'    #レベルが高い順.
        LEVEL = 'level'         #レベルが低い順.
        COST_REV = '-cost'      #コストが高い順.
        COST = 'cost'           #コストが低い順.
        POWER_REV = '-power'    #接客力が高い順.
        POWER = 'power'         #接客力が低い順.
        HKLEVEL_REV = '-hklevel'#ハメ管理度が高い順.
        HKLEVEL = 'hklevel'     #ハメ管理度が低い順.
        EVO_MATERIAL = 'evomaterial'     #進化素材用.
        
        SORTEDLIST = (
            CTIME_REV,
            CTIME,
            RARE_REV,
            RARE,
            LEVEL_REV,
            LEVEL,
            COST_REV,
            COST,
            POWER_REV,
            POWER,
            HKLEVEL_REV,
            HKLEVEL,
        )
        
        NAMES = {
            CTIME_REV : u'新着順',
            CTIME : u'古い順',
            RARE_REV : u'レアリティが高い順',
            RARE : u'レアリティが低い順',
            LEVEL_REV : u'レベルが高い順',
            LEVEL : u'レベルが低い順',
            COST_REV : u'人件費が高い順',
            COST : u'人件費が低い順',
            POWER_REV : u'接客力が高い順',
            POWER : u'接客力が低い順',
            HKLEVEL_REV : u'ハメ管理度が高い順',
            HKLEVEL : u'ハメ管理度が低い順',
        }
        
        GROUP = (
            CTIME,
            RARE,
            LEVEL,
            COST,
            POWER,
            HKLEVEL
        )
    
    class CardGetWayType:
        """取得方法.
        """
        (
            OTHER,
            REGIST,
            SCOUT,
            AREA,
            GACHA,
            LOGINBONUS,
            PRIZE,
            TREASURE,
            SHOP,
            INVITE,
            TRADE,
            STOCK,
            RAIDEVENT_MIX,
        ) = range(13)
        NAMES = {
            OTHER : u'その他',
            REGIST : u'登録時',
            SCOUT : u'スカウト',
            AREA : u'エリアクリア',
            GACHA : u'ガチャ',
            LOGINBONUS : u'ログインボーナス',
            PRIZE : u'報酬',
            TREASURE : u'宝箱',
            SHOP : u'ショップ',
            INVITE : u'招待',
            TRADE : u'秘宝交換',
            STOCK : u'図鑑から再生',
            RAIDEVENT_MIX : u'レイドイベントの配合',
        }
    
    class Rarity:
        """レア度.
        """
        (
            NORMAL,
            HIGH_NORMAL,
            RARE,
            HIGH_RARE,
            SUPERRARE,
            SPECIALSUPERRARE,
            LEGEND_CAST,
        ) = range(7)
        ALL = 255
        
        LIST = (
            NORMAL,
            HIGH_NORMAL,
            RARE,
            HIGH_RARE,
            SUPERRARE,
            SPECIALSUPERRARE,
            LEGEND_CAST,
        )
        
        RARITY_MAX = LIST[-1]
        
        AUTO_SELL = (
            NORMAL,
            HIGH_NORMAL,
            RARE,
        )
        
        TRANSFER = (
            RARE,
            HIGH_RARE,
            SUPERRARE,
            SPECIALSUPERRARE,
            LEGEND_CAST,
        )
        
        NAMES = {
            NORMAL : u'N',
            HIGH_NORMAL : u'HN',
            RARE : u'R',
            HIGH_RARE : u'HR',
            SUPERRARE : u'SR',
            SPECIALSUPERRARE : u'SSR',
            LEGEND_CAST : u'LC',
        }
        NAMES_INCLUDE_ALL = dict(NAMES)
        NAMES_INCLUDE_ALL.update({ALL:u'全て'})
        
        EVOLUTION_ABLES = (
            RARE,
            HIGH_RARE,
            SUPERRARE,
            SPECIALSUPERRARE,
            LEGEND_CAST,
        )
        FEVER_RATE = {
            NORMAL : 2,
            HIGH_NORMAL : 8,
            RARE : 20,
            HIGH_RARE : 40,
            SUPERRARE : 100,
            SPECIALSUPERRARE : 200,
            LEGEND_CAST : 200,
        }
        FEVER_POWERUP_RATE = {
            NORMAL : 110,
            HIGH_NORMAL : 130,
            RARE : 150,
            HIGH_RARE : 170,
            SUPERRARE : 200,
            SPECIALSUPERRARE : 250,
            LEGEND_CAST : 250,
        }
        
        SCOUT_DETERMINE_RATE = {
            NORMAL : 100,
            HIGH_NORMAL : 80,
            RARE : 5,
            HIGH_RARE : 3,
            SUPERRARE : 1,
            SPECIALSUPERRARE : 0,
            LEGEND_CAST : 0,
        }
        
        COLORS = {
            RARE : u'#ff2020',
            HIGH_RARE : u'#ff8020',
            SUPERRARE : u'#2080ff',
            SPECIALSUPERRARE : u'#20ff80',
            LEGEND_CAST : u'#ff80ee',
        }
        
        TREASURE_WHEN_SELL = {
            RARE : 5,
            HIGH_RARE : 50,
            SUPERRARE : 200,
            SPECIALSUPERRARE : 1000,
            LEGEND_CAST : 2000,
        }
    
    class FriendState:
        """仲間申請の状態.
        """
        (
            SEND,       # 申請中.
            RECEIVE,    # 承認待ち.
            ACCEPT,     # 承認済み.
        ) = range(3)
        NAMES = {
            SEND : u'申請中',
            RECEIVE : u'承認待ち',
            ACCEPT : u'仲間',
        }
        TOPICS = {
            ACCEPT : 1,
            SEND : 2,
            RECEIVE : 3,
        }
    
    class LevelGroup:
        """レベル帯.
        """
        (
            LV01_09,
            LV10_19,
            LV20_39,
            LV40_59,
            LV60_OVER,
        ) = range(5)
        NAMES = {
            LV01_09 : u'Lv10未満',
            LV10_19 : u'Lv10〜Lv19',
            LV20_39 : u'Lv20〜Lv39',
            LV40_59 : u'Lv40〜Lv59',
            LV60_OVER : u'Lv60以上',
        }
    
    class TextMasterID:
        """テキスト.
        """
        NUM_MAX = 18
        (
            AREA_CLEAR,
            LOGIN_BONUS,
            ACCESS_BONUS,
            HAPPENING_DROP,
            GACHA_CARD,
            GACHA_CARD_OVER,
            GACHA_BONUS,
            TUTORIAL_END,
            BATTLE_WIN,
            BATTLE_LOSE,
            BATTLE_RANKUP,
            RAID_CLEAR,
            RAID_JOIN,
            TREASURE_BOX,
            SCOUT,
            PREREGIST,
            INVITE,
            CABARETCLUB_WEEKLY_PRIZE,
        ) = range(1, NUM_MAX+1)
        NAMES = {
            AREA_CLEAR : u'エリアクリア',
            LOGIN_BONUS : u'連続ログインボーナス',
            ACCESS_BONUS : u'アクセスボーナス',
            HAPPENING_DROP : u'ハプニングでのドロップ',
            GACHA_CARD : u'課金引抜で手に入れたカード',
            GACHA_CARD_OVER : u'引抜でBOXに入りきらなかったカード',
            GACHA_BONUS : u'引抜のおまけ',
            TUTORIAL_END : u'チュートリアル完了',
            BATTLE_WIN : u'バトル:勝利報酬',
            BATTLE_LOSE : u'バトル:敗北時のプレゼント',
            BATTLE_RANKUP : u'バトル:ランクアップ報酬',
            RAID_CLEAR : u'レイド:クリア報酬',
            RAID_JOIN : u'レイド:参加報酬',
            TREASURE_BOX : u'宝箱:開封',
            SCOUT : u'スカウト',
            PREREGIST : u'事前登録報酬',
            INVITE : u'招待報酬',
            CABARETCLUB_WEEKLY_PRIZE : u'キャバクラ店舗の毎週の報酬(名誉ポイント)',
        }
        AUTO_CREATION_ID_MIN = 1000000
    
    class ScoutEventType:
        """スカウトで発生するイベント.
        """
        NUM_MAX = 10
        (
            NONE,       # なにもなかった.
            LEVELUP,    # レベルアップ(テキスト表示ありのイベントなし).
            GET_CARD,   # カード獲得.
            HAPPENING,  # ハプニング.
            GET_ITEM,   # アイテム獲得.
            GET_TREASURE, # 宝箱獲得.
            COMPLETE,   # 完了.
            AP_NONE,    # 行動力が足りない.
            EVENTGACHA, # スカウトイベントガチャポイント.
            LOVETIME_STAR,      # 逢引ラブタイムの星.
        ) = range(0, NUM_MAX)
        
        NAMES = {
            NONE : u'なにもなかった',
            LEVELUP : u'レベルアップ',
            GET_CARD : u'カード獲得',
            HAPPENING : u'ハプニング',
            GET_ITEM : u'アイテム獲得',
            GET_TREASURE : u'宝箱獲得',
            COMPLETE : u'完了',
            AP_NONE : u'行動力不足',
            EVENTGACHA : u'スカウトイベントガチャポイント',
            LOVETIME_STAR : u'逢引ラブタイムの星',
        }
        ENG_NAMES = {
            NONE : u'none',
            LEVELUP : u'levelup',
            GET_CARD : u'card',
            HAPPENING : u'happening',
            GET_ITEM : u'item',
            GET_TREASURE : u'treasure',
            COMPLETE : u'complete',
            AP_NONE : u'apnone',
            EVENTGACHA : u'eventgacha',
            LOVETIME_STAR : u'lovetime_star',
        }
        
        DEFAULT_ANIMATION_EVENT_TEXT_NONE = 0
        DEFAULT_ANIMATION_EVENT_WITH_TEXT = LEVELUP
        
        ANIMATION_EVENTS = {
            NONE : NONE,       # なにもなかった.
            LEVELUP : LEVELUP,    # レベルアップ.
            GET_CARD : GET_CARD,   # カード獲得.
            HAPPENING : HAPPENING,  # ハプニング.
            GET_ITEM : GET_ITEM,   # アイテム獲得.
            GET_TREASURE : GET_TREASURE, # 宝箱獲得.
            EVENTGACHA : GET_ITEM, # スカウトイベントガチャポイント.
            LOVETIME_STAR : GET_ITEM,      # 逢引ラブタイムの星.
        }
        EVENT_TEXTS = {
            LEVELUP : (u'経験値が100%に達しました', ),
            GET_CARD : (u'！？あの子は有望だぞ！', ),
            HAPPENING : (u'お店から電話だ！なにがあったんだ･･･！？', ),
            GET_ITEM : (u'プレゼントの中身は･･･！？', ),
            GET_TREASURE : (u'%s発見！バトルに勝利してカギをGetして中身を獲得しよう', u'%s発見！'),
            COMPLETE : (u'進捗が100%に達しました', ),
            AP_NONE : (u'体力が無くなった', ),
            EVENTGACHA : (u'プレゼントの中身は･･･！？', ),
            LOVETIME_STAR : (u'プレゼントの中身は･･･！？', ),
        }
    
    class MemoryContentType:
        """思い出アルバムのコンテンツの種類.
        """
        NUM_MAX = 4
        (
            IMAGE,
            MOVIE,
            VOICE,
            MOVIE_PC,
        ) = range(1, NUM_MAX+1)
        NAMES = {
            IMAGE : u'画像',
            MOVIE : u'動画',
            VOICE : u'音声',
            MOVIE_PC : u'動画(PC)',
        }
    
    class SkillTarget:
        """スキルのターゲット.
        """
        (
            PLAYER,
            OPPONENT,
        ) = range(2)
        NAMES = {
            PLAYER : u'自分のデッキ',
            OPPONENT : u'相手のデッキ',
        }

    class SkillEffect:
        """スキル効果
        """
        (
            NONE,
            CAST_COUNT,
            CABACLUB,
        ) = range(3)
        NAMES = {
            NONE : u'無',
            CAST_COUNT : u'数が多いほど',
            CABACLUB: u'経営',
        }

    class GachaFirsttimeType:
        """ガチャ初回タイプ.
        """
        (
            NONE,
            EVERYDAY,
            ONETIME,
            SEAT,
        ) = range(4)
        NAMES = {
            NONE : u'初回サービスなし',
            EVERYDAY : u'毎日初回',
            ONETIME : u'1度きり',
            SEAT : u'シート初回時',
        }
    
    class GachaConsumeType:
        """ガチャ消費タイプ.といいつつ実はガチャの種類.
        """
        (
            GACHAPT,
            PAYMENT,
            RAREOVERTICKET,
            TRYLUCKTICKET,
            MEMORIESTICKET,
            EVENTTICKET,
            PREMIUM,
            MINI_BOX,
            SEAT,
            STEPUP,
            SSR_20PERCENT_TICKET,
            MINI_SEAT,
            ONE_TWO_THREE,
            CONTINUITY_20,
            RANKING,
            HR_OVER_TICKET,
            SR_OVER_TICKET,
            KOAKUMA_TICKET,
            CHITEKI_TICKET,
            IYASHI_TICKET,
            OMAKE,
            CHRISTMAS,
            FUKUBUKURO,
            SCOUTEVENT,
            DAILY_DISCOUNT,
            SR_SSR_PROBABILITY_UP,
            NEWCARD_SSR_20PERCENT,
            NEWCARD_SR_ORVER_SSR_50PERCENT,
            FIXEDSR,
            FIXEDSR_SSR_20PERCENT,
            FIXEDSR_SSR_50PERCENT,
            REPRINT_TICKET, # 現状, ガチャでは使わない. スカウトイベントでの交換用チケット.
            LIMIT_SHEET,
            XMAS_OMAKE,
            CASTTRADE_TICKET, # 現状, ガチャでは使わない. スカウトイベントでの交換用チケット.
            FIXEDHR_SR_20PERCENT,
            FIXEDHR_SR_50PERCENT,
            FIXEDSSR_LC_10PERCENT,
            FIXEDSSR_LC_20PERCENT,
            FUKUBUKURO2016,
            NEW_FIXEDSR_SSR_20PERCENT,
            NEW_FIXEDSR_SSR_50PERCENT,
            FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_20PERCENT,
            FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_50PERCENT,
            PTCHANGE,
            FIXEDSR_SP_SSR_20PERCENT,
            FIXEDSR_SP_SSR_50PERCENT,
            NEWSTORE_SUPPORT_PREMIUM,
            LIMITED_RESET_BOX,
            BATTLE_TICKET, # 現状, ガチャでは使わない. バトルイベントでの交換用チケット.
            SEAT2, # シーテガチャを二つ出したい.
            FIXEDSSR,
            STEPUP2,
            OMAKE2,
            LIMITED_FIXEDSSR_LC_10PERCENT,
            SP_SSR_20PERCENT_LC_10PERCENT,
            MINI_BOX2,
            FIXEDSSR_LC_30PERCENT,
            LC_20PERCENT,
            NEW_FIXEDSSR_LC_30PERCENT,
            FUKUBUKURO2017,
            MANAGEMENT_REPRINT,
        ) = range(62)
        
        NAMES = {
            GACHAPT : u'引抜チケットor引抜Pt',
            PAYMENT : u'常設プレミアム',
            RAREOVERTICKET : u'レア以上確定チケットガチャ',
            TRYLUCKTICKET : u'運試しチケットガチャ',
            MEMORIESTICKET : u'思い出チケットガチャ',
            EVENTTICKET : u'イベント限定チケットガチャ',
            PREMIUM : u'限定BOX',
            MINI_BOX : u'ミニBOX',
            SEAT : u'シート',
            STEPUP : u'STEP UP',
            SSR_20PERCENT_TICKET : u'SSR30%チケット',
            MINI_SEAT : u'ミニシート',
            ONE_TWO_THREE : u'1,2,3',
            CONTINUITY_20 : u'20連ガチャ',
            RANKING : u'ランキング',
            HR_OVER_TICKET : u'HR以上確定チケットガチャ',
            SR_OVER_TICKET : u'SR以上確定チケットガチャ',
            KOAKUMA_TICKET : u'小悪魔確定チケットガチャ',
            CHITEKI_TICKET : u'知的確定チケットガチャ',
            IYASHI_TICKET : u'癒し確定チケットガチャ',
            OMAKE : u'おまけ',
            CHRISTMAS : u'クリスマス',
            FUKUBUKURO : u'福袋',
            SCOUTEVENT : u'スカウトイベント限定ガチャ',
            DAILY_DISCOUNT : u'1日1回',
            SR_SSR_PROBABILITY_UP : u'出現率UP',
            NEWCARD_SSR_20PERCENT : u'新SSR20%ガチャチケット',
            NEWCARD_SR_ORVER_SSR_50PERCENT : u'新SR以上確定新SSR50%ガチャチケット',
            FIXEDSR : u'SR確定ガチャ',
            FIXEDSR_SSR_20PERCENT : u'SR確定SSR20%ガチャ',
            FIXEDSR_SSR_50PERCENT : u'SR確定SSR50%ガチャ',
            REPRINT_TICKET : u'復刻チケット',
            CASTTRADE_TICKET : u'キャスト指定チケット',
            XMAS_OMAKE : u'クリスマス限定コスプレおまけガチャ',
            LIMIT_SHEET : u'限定シートガチャ',
            FIXEDHR_SR_20PERCENT : u'HR確定SR20%ガチャ',
            FIXEDHR_SR_50PERCENT : u'HR確定SR50%ガチャ',
            FIXEDSSR_LC_10PERCENT : u'新SSR確定LC10%ガチャ',
            FIXEDSSR_LC_20PERCENT : u'新SSR確定LC20%ガチャ',
            FUKUBUKURO2016 : u'福袋2016',
            NEW_FIXEDSR_SSR_20PERCENT : u'新SR確定SSR20%ガチャ',
            NEW_FIXEDSR_SSR_50PERCENT : u'新SR確定SSR50%ガチャ',
            FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_20PERCENT : u'40万人突破記念SR確定SSR20%ガチャ',
            FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_50PERCENT : u'40万人突破記念SR確定SSR50%ガチャ',
            PTCHANGE : u'PtChangeガチャ',
            FIXEDSR_SP_SSR_20PERCENT : u'SR確定特効SSR20%ガチャチケット',
            FIXEDSR_SP_SSR_50PERCENT : u'SR確定特効SSR50%ガチャチケット',
            NEWSTORE_SUPPORT_PREMIUM : u'新店舗応援プレミアムガチャ',
            LIMITED_RESET_BOX : u'条件付きリセット可能BOXガチャ',
            BATTLE_TICKET : u'バトルチケット',
            SEAT2 : u'シートガチャ',
            FIXEDSSR : u'SSR確定ガチャチケット',
            STEPUP2 : u'コラボ',
            OMAKE2 : u'確率UPおまけ',
            LIMITED_FIXEDSSR_LC_10PERCENT: u'SSR確定LC10%ガチャ',
            SP_SSR_20PERCENT_LC_10PERCENT: u'特効SSR20%LC10%ガチャ',
            MINI_BOX2: u'ミニBOX2',
            FIXEDSSR_LC_30PERCENT: u'SSR確定LC30%ガチャ',
            LC_20PERCENT: u'SSR確定LC20%ガチャ',
            NEW_FIXEDSSR_LC_30PERCENT: "新SSR確定LC30%ガチャ",
            FUKUBUKURO2017: u'福袋2017',
            MANAGEMENT_REPRINT: u'復刻経営キャストガチャ',
        }
        GTYPE_NAMES = {
            GACHAPT : u'free',
            PAYMENT : u'usually',
            RAREOVERTICKET : u'ticket',
            TRYLUCKTICKET : u'ticket',
            MEMORIESTICKET : u'ticket',
            EVENTTICKET : u'ticket',
            PREMIUM : u'premium',
            MINI_BOX : u'minibox',
            SEAT : u'seat',
            STEPUP : u'stepup',
            SSR_20PERCENT_TICKET : u'ticket',
            MINI_SEAT : u'miniseat',
            ONE_TWO_THREE : u'onetwothree',
            CONTINUITY_20 : u'cnt20',
            RANKING : u'ranking',
            HR_OVER_TICKET : u'ticket',
            SR_OVER_TICKET : u'ticket',
            KOAKUMA_TICKET : u'ticket',
            CHITEKI_TICKET : u'ticket',
            IYASHI_TICKET : u'ticket',
            OMAKE : u'omake',
            CHRISTMAS : u'christmas',
            FUKUBUKURO : u'fukubukuro',
            SCOUTEVENT : u'scev',
            DAILY_DISCOUNT : u'discount',
            SR_SSR_PROBABILITY_UP : u'probability',
            NEWCARD_SSR_20PERCENT : u'ticket',
            NEWCARD_SR_ORVER_SSR_50PERCENT : u'ticket',
            FIXEDSR : u'fixedsr',
            FIXEDSR_SSR_20PERCENT : u'fixedsr_ssr_20',
            FIXEDSR_SSR_50PERCENT : u'fixedsr_ssr_50',
            XMAS_OMAKE : u'xmas_omake',
            LIMIT_SHEET : u'limit_sheet',
            FIXEDHR_SR_20PERCENT : u'fixedhr_sr_20',
            FIXEDHR_SR_50PERCENT : u'fixedhr_sr_50',
            FIXEDSSR_LC_10PERCENT : u'fixedssr_lc_10',
            FIXEDSSR_LC_20PERCENT : u'fixedssr_lc_20',
            FUKUBUKURO2016 : u'fukubukuro2016',
            NEW_FIXEDSR_SSR_20PERCENT : u'ticket',
            NEW_FIXEDSR_SSR_50PERCENT : u'ticket',
            FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_20PERCENT : u'ticket',
            FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_50PERCENT : u'ticket',
            PTCHANGE : u'ptchange',
            FIXEDSR_SP_SSR_20PERCENT : u'fixedsr_sp_ssr_20',
            FIXEDSR_SP_SSR_50PERCENT : u'fixedsr_sp_ssr_50',
            NEWSTORE_SUPPORT_PREMIUM : u'newstore_support_premium',
            LIMITED_RESET_BOX : u'limited_reset_box',
            SEAT2 : u'seat2',
            FIXEDSSR : u'fixedssr',
            STEPUP2 : u'stepup2',
            OMAKE2 : u'omake2',
            LIMITED_FIXEDSSR_LC_10PERCENT: u'limited_fixedssr_lc_10',
            SP_SSR_20PERCENT_LC_10PERCENT: u'sp_ssr_20_lc_10',
            MINI_BOX2: u'minibox2',
            FIXEDSSR_LC_30PERCENT: u'fixedssr_lc_30',
            LC_20PERCENT: u'lc_20',
            NEW_FIXEDSSR_LC_30PERCENT: u'new_fixedssr_lc_30',
            FUKUBUKURO2017: u'fukubukuro2017',
            MANAGEMENT_REPRINT: u'management_reprint'
        }
        
        class GachaTicketType:
            """ガチャチケットタイプ.
            """
            (
                SSR_20PERCENT,
                HR_OVER,
                SR_OVER,
                KOAKUMA,
                CHITEKI,
                IYASHI,
                NEWCARD_SSR_20PERCENT,
                NEWCARD_SR_ORVER_SSR_50PERCENT,
                FIXEDSR_SSR_20PERCENT,
                FIXEDSR_SSR_50PERCENT,
                REPRINT_TICKET,  # 現状, ガチャでは使わない. スカウトイベントでの交換用チケット.
                CASTTRADE_TICKET, # 現状, ガチャでは使わない. スカウトイベントでの交換用チケット.
                FIXEDHR_SR_20PERCENT,
                FIXEDHR_SR_50PERCENT,
                FIXEDSSR_LC_10PERCENT,
                FIXEDSSR_LC_20PERCENT,
                NEW_FIXEDSR_SSR_20PERCENT,
                NEW_FIXEDSR_SSR_50PERCENT,
                FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_20PERCENT,
                FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_50PERCENT,
                FIXEDSR_SP_SSR_20PERCENT,
                FIXEDSR_SP_SSR_50PERCENT,
                BATTLE_TICKET,  # 現状, ガチャでは使わない. バトルイベントでの交換用チケット.
                FIXEDSSR,
                LIMITED_FIXEDSSR_LC_10PERCENT,
                SP_SSR_20PERCENT_LC_10PERCENT,
                FIXEDSSR_LC_30PERCENT,
                LC_20PERCENT,
                NEW_FIXEDSSR_LC_30PERCENT,
                MANAGEMENT_REPRINT,
            ) = range(1, 31)
            NAMES = {
                SSR_20PERCENT : u'SSR30%チケット',
                HR_OVER : u'HR以上確定ガチャチケット',
                SR_OVER : u'SR以上確定ガチャチケット',
                KOAKUMA : u'小悪魔確定ガチャチケット',
                CHITEKI : u'知的確定ガチャチケット',
                IYASHI : u'癒し確定ガチャチケット',
                NEWCARD_SSR_20PERCENT : u'新SSR20%ガチャチケット',
                NEWCARD_SR_ORVER_SSR_50PERCENT : u'新SR以上確定新SSR50%ガチャチケット',
                FIXEDSR_SSR_20PERCENT : u'SR確定SSR20%ガチャチケット',
                FIXEDSR_SSR_50PERCENT : u'SR確定SSR50%ガチャチケット',
                REPRINT_TICKET : u'復刻チケット',
                CASTTRADE_TICKET : u'キャスト指定チケット',
                FIXEDHR_SR_20PERCENT : u'HR確定SR20%ガチャチケット',
                FIXEDHR_SR_50PERCENT : u'HR確定SR50%ガチャチケット',
                FIXEDSSR_LC_10PERCENT : u'新SSR確定LC10%ガチャチケット',
                FIXEDSSR_LC_20PERCENT : u'新SSR確定LC20%ガチャチケット',
                NEW_FIXEDSR_SSR_20PERCENT : u'新SR確定SSR20%ガチャチケット',
                NEW_FIXEDSR_SSR_50PERCENT : u'新SR確定SSR50%ガチャチケット',
                FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_20PERCENT : '40万人突破記念SR確定SSR20%ガチャ',
                FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_50PERCENT : '40万人突破記念SR確定SSR50%ガチャ',
                FIXEDSR_SP_SSR_20PERCENT : u'SR確定特効SSR20%ガチャチケット',
                FIXEDSR_SP_SSR_50PERCENT : u'SR確定特効SSR50%ガチャチケット',
                BATTLE_TICKET : u'バトルチケット',
                FIXEDSSR : u'SSR確定ガチャチケット',
                LIMITED_FIXEDSSR_LC_10PERCENT: u'SSR確定LC10%ガチャチケット',
                SP_SSR_20PERCENT_LC_10PERCENT: u'特効SSR20%LC10%ガチャ',
                FIXEDSSR_LC_30PERCENT: u'SSR確定LC30%ガチャチケット',
                LC_20PERCENT: u'SSR確定LC20%ガチャチケット',
                NEW_FIXEDSSR_LC_30PERCENT: "新SSR確定LC30%ガチャチケット",
                MANAGEMENT_REPRINT: "復刻経営キャストガチャチケット"
            }
            THUMBNAIL = {
                SSR_20PERCENT : u'item/ticket_ssrare',
                HR_OVER : u'item/ticket_hrover',
                SR_OVER : u'item/ticket_srover',
                KOAKUMA : u'item/ticket_koakuma',
                CHITEKI : u'item/ticket_chiteki',
                IYASHI : u'item/ticket_iyashi',
                NEWCARD_SSR_20PERCENT : u'item/newcard_ssr20',
                NEWCARD_SR_ORVER_SSR_50PERCENT : u'item/newcard_srover_ssr50',
                FIXEDSR_SSR_20PERCENT : u'item/ticket_srover_ssr20',
                FIXEDSR_SSR_50PERCENT : u'item/ticket_srover_ssr50',
                REPRINT_TICKET : u'item/ticket_reprint',
                CASTTRADE_TICKET : u'item/ticket_call_cast',
                FIXEDHR_SR_20PERCENT : u'item/ticket_hrsr20',
                FIXEDHR_SR_50PERCENT : u'item/ticket_hrsr50',
                FIXEDSSR_LC_10PERCENT : u'item/ticket_ssrlc10',
                FIXEDSSR_LC_20PERCENT : u'item/ticket_ssrlc20',
                NEW_FIXEDSR_SSR_20PERCENT : u'item/ticket_srssr20',
                NEW_FIXEDSR_SSR_50PERCENT : u'item/ticket_srssr50',
                FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_20PERCENT : 'item/400thou_ssr20',
                FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_50PERCENT : 'item/400thou_ssr50',
                FIXEDSR_SP_SSR_20PERCENT : u'item/ticket_sp20',
                FIXEDSR_SP_SSR_50PERCENT : u'item/ticket_sp50',
                BATTLE_TICKET : u'item/battle_ticket',
                FIXEDSSR : u'item/ticket_ssr100',
                LIMITED_FIXEDSSR_LC_10PERCENT: u'item/ticket_ssrlc10_special',
                SP_SSR_20PERCENT_LC_10PERCENT: u'item/ticket_ssrlc10_effective',
                FIXEDSSR_LC_30PERCENT: u'item/ticket_ssrlc30_special',
                LC_20PERCENT: u'item/ticket_ssrlc20_special',
                NEW_FIXEDSSR_LC_30PERCENT : u'item/ticket_ssrlc30',
                MANAGEMENT_REPRINT: u'item/ticket_management_reprint',
            }
            CHOICES = dict([[0, u'------']] + list(NAMES.items()))
        ADDITIONAL_TICKETS = {
            SSR_20PERCENT_TICKET : GachaTicketType.SSR_20PERCENT,
            HR_OVER_TICKET : GachaTicketType.HR_OVER,
            SR_OVER_TICKET : GachaTicketType.SR_OVER,
            KOAKUMA_TICKET : GachaTicketType.KOAKUMA,
            CHITEKI_TICKET : GachaTicketType.CHITEKI,
            IYASHI_TICKET : GachaTicketType.IYASHI,
            NEWCARD_SSR_20PERCENT : GachaTicketType.NEWCARD_SSR_20PERCENT,
            NEWCARD_SR_ORVER_SSR_50PERCENT : GachaTicketType.NEWCARD_SR_ORVER_SSR_50PERCENT,
            FIXEDSR_SSR_20PERCENT : GachaTicketType.FIXEDSR_SSR_20PERCENT,
            FIXEDSR_SSR_50PERCENT : GachaTicketType.FIXEDSR_SSR_50PERCENT,
            REPRINT_TICKET : GachaTicketType.REPRINT_TICKET,
            CASTTRADE_TICKET : GachaTicketType.CASTTRADE_TICKET,
            FIXEDHR_SR_20PERCENT : GachaTicketType.FIXEDHR_SR_20PERCENT,
            FIXEDHR_SR_50PERCENT : GachaTicketType.FIXEDHR_SR_50PERCENT,
            FIXEDSSR_LC_10PERCENT : GachaTicketType.FIXEDSSR_LC_10PERCENT,
            FIXEDSSR_LC_20PERCENT : GachaTicketType.FIXEDSSR_LC_20PERCENT,
            NEW_FIXEDSR_SSR_20PERCENT : GachaTicketType.NEW_FIXEDSR_SSR_20PERCENT,
            NEW_FIXEDSR_SSR_50PERCENT : GachaTicketType.NEW_FIXEDSR_SSR_50PERCENT,
            FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_20PERCENT : GachaTicketType.FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_20PERCENT,
            FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_50PERCENT : GachaTicketType.FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_50PERCENT,
            FIXEDSR_SP_SSR_20PERCENT : GachaTicketType.FIXEDSR_SP_SSR_20PERCENT,
            FIXEDSR_SP_SSR_50PERCENT :GachaTicketType.FIXEDSR_SP_SSR_50PERCENT,
            BATTLE_TICKET : GachaTicketType.BATTLE_TICKET,
            FIXEDSSR : GachaTicketType.FIXEDSSR,
            LIMITED_FIXEDSSR_LC_10PERCENT: GachaTicketType.LIMITED_FIXEDSSR_LC_10PERCENT,
            SP_SSR_20PERCENT_LC_10PERCENT: GachaTicketType.SP_SSR_20PERCENT_LC_10PERCENT,
            FIXEDSSR_LC_30PERCENT: GachaTicketType.FIXEDSSR_LC_30PERCENT,
            LC_20PERCENT: GachaTicketType.LC_20PERCENT,
            NEW_FIXEDSSR_LC_30PERCENT: GachaTicketType.NEW_FIXEDSSR_LC_30PERCENT,
            MANAGEMENT_REPRINT: GachaTicketType.MANAGEMENT_REPRINT,
        }
        
        class GachaTopTopic:
            (
                PREMIUM,    # 課金.
                PAYMENT,    # BOX.
                TICKET,     # チケット.
                FREE,       # 無料.
                SCOUTEVENT  # スカウトイベント.
            ) = range(1, 6)
            
            PAYMENT_TOPICS = (
                PAYMENT,
                PREMIUM
            )
        
        TO_TOPIC = {
            GACHAPT : GachaTopTopic.FREE,
            PAYMENT : GachaTopTopic.PAYMENT,
            RAREOVERTICKET : GachaTopTopic.TICKET,
            TRYLUCKTICKET : GachaTopTopic.FREE,
            MEMORIESTICKET : GachaTopTopic.TICKET,
            EVENTTICKET : GachaTopTopic.TICKET,
            PREMIUM : GachaTopTopic.PREMIUM,
            MINI_BOX : GachaTopTopic.PREMIUM,
            SEAT : GachaTopTopic.PREMIUM,
            STEPUP : GachaTopTopic.PREMIUM,
            SSR_20PERCENT_TICKET : GachaTopTopic.TICKET,
            MINI_SEAT : GachaTopTopic.PREMIUM,
            ONE_TWO_THREE : GachaTopTopic.PREMIUM,
            CONTINUITY_20 : GachaTopTopic.PREMIUM,
            RANKING : GachaTopTopic.PREMIUM,
            HR_OVER_TICKET : GachaTopTopic.TICKET,
            SR_OVER_TICKET : GachaTopTopic.TICKET,
            KOAKUMA_TICKET : GachaTopTopic.TICKET,
            CHITEKI_TICKET : GachaTopTopic.TICKET,
            IYASHI_TICKET : GachaTopTopic.TICKET,
            OMAKE : GachaTopTopic.PREMIUM,
            CHRISTMAS : GachaTopTopic.PREMIUM,
            FUKUBUKURO : GachaTopTopic.PREMIUM,
            SCOUTEVENT : GachaTopTopic.SCOUTEVENT,
            DAILY_DISCOUNT : GachaTopTopic.PREMIUM,
            SR_SSR_PROBABILITY_UP : GachaTopTopic.PREMIUM,
            NEWCARD_SSR_20PERCENT : GachaTopTopic.TICKET,
            NEWCARD_SR_ORVER_SSR_50PERCENT : GachaTopTopic.TICKET,
            FIXEDSR : GachaTopTopic.PREMIUM,
            FIXEDSR_SSR_20PERCENT : GachaTopTopic.TICKET,
            FIXEDSR_SSR_50PERCENT : GachaTopTopic.TICKET,
            XMAS_OMAKE : GachaTopTopic.PREMIUM,
            LIMIT_SHEET : GachaTopTopic.PREMIUM,
            FIXEDHR_SR_20PERCENT : GachaTopTopic.TICKET,
            FIXEDHR_SR_50PERCENT : GachaTopTopic.TICKET,
            FIXEDSSR_LC_10PERCENT : GachaTopTopic.TICKET,
            FIXEDSSR_LC_20PERCENT : GachaTopTopic.TICKET,
            FUKUBUKURO2016 : GachaTopTopic.PREMIUM,
            NEW_FIXEDSR_SSR_20PERCENT : GachaTopTopic.TICKET,
            NEW_FIXEDSR_SSR_50PERCENT : GachaTopTopic.TICKET,
            FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_20PERCENT : GachaTopTopic.TICKET,
            FOUR_HUNDRED_THOUSAND_OVER_FIXEDSR_SSR_50PERCENT : GachaTopTopic.TICKET,
            PTCHANGE : GachaTopTopic.PREMIUM,
            FIXEDSR_SP_SSR_20PERCENT : GachaTopTopic.TICKET,
            FIXEDSR_SP_SSR_50PERCENT : GachaTopTopic.TICKET,
            NEWSTORE_SUPPORT_PREMIUM : GachaTopTopic.PREMIUM,
            LIMITED_RESET_BOX : GachaTopTopic.PREMIUM,
            SEAT2 : GachaTopTopic.PREMIUM,
            FIXEDSSR : GachaTopTopic.TICKET,
            STEPUP2 : GachaTopTopic.PREMIUM,
            OMAKE2 : GachaTopTopic.PREMIUM,
            LIMITED_FIXEDSSR_LC_10PERCENT: GachaTopTopic.TICKET,
            SP_SSR_20PERCENT_LC_10PERCENT: GachaTopTopic.TICKET,
            MINI_BOX2 : GachaTopTopic.PREMIUM,
            FIXEDSSR_LC_30PERCENT: GachaTopTopic.TICKET,
            LC_20PERCENT: GachaTopTopic.TICKET,
            NEW_FIXEDSSR_LC_30PERCENT: GachaTopTopic.TICKET,
            FUKUBUKURO2017: GachaTopTopic.PREMIUM,
            MANAGEMENT_REPRINT: GachaTopTopic.TICKET,
        }
        # 課金タイプ.
        PAYMENT_TYPES = (
            STEPUP,
            SEAT,
            MINI_BOX,
            PREMIUM,
            PAYMENT,
            MINI_SEAT,
            ONE_TWO_THREE,
            CONTINUITY_20,
            RANKING,
            OMAKE,
            CHRISTMAS,
            FUKUBUKURO,
            DAILY_DISCOUNT,
            SR_SSR_PROBABILITY_UP,
            FIXEDSR,
            XMAS_OMAKE,
            LIMIT_SHEET,
            FUKUBUKURO2016,
            PTCHANGE,
            NEWSTORE_SUPPORT_PREMIUM,
            LIMITED_RESET_BOX,
            SEAT2,
            STEPUP2,
            OMAKE2,
            MINI_BOX2,
            FUKUBUKURO2017,
        )
        PREMIUM_TYPES = (
            STEPUP,
            SEAT,
            MINI_BOX,
            PREMIUM,
            MINI_SEAT,
            ONE_TWO_THREE,
            CONTINUITY_20,
            RANKING,
            OMAKE,
            CHRISTMAS,
            FUKUBUKURO,
            DAILY_DISCOUNT,
            SR_SSR_PROBABILITY_UP,
            FIXEDSR,
            XMAS_OMAKE,
            LIMIT_SHEET,
            FUKUBUKURO2016,
            PTCHANGE,
            NEWSTORE_SUPPORT_PREMIUM,
            LIMITED_RESET_BOX,
            SEAT2,
            STEPUP2,
            OMAKE2,
            MINI_BOX2,
            FUKUBUKURO2017,
        )
        BOX_TYPES = (
            PREMIUM,
            MINI_BOX,
            MINI_BOX2,
        )
    
    class TreasureType:
        """宝箱の種類.
        """
        NUM_MAX = 3
        (
            GOLD,
            SILVER,
            BRONZE,
        ) = range(1, NUM_MAX+1)
        
        NAMES = {
            GOLD : u'金の宝箱',
            SILVER : u'銀の宝箱',
            BRONZE : u'銅の宝箱',
        }
        THUMBNAIL = {
            GOLD : u'item/chest_gold',
            SILVER : u'item/chest_silver',
            BRONZE : u'item/chest_copper',
        }
        STRING = {
            GOLD : u'gold',
            SILVER : u'silver',
            BRONZE : u'bronze',
        }
        # 宝箱最大所持数
        POOL_LIMIT = {
            GOLD : 10,
            SILVER : 10,
            BRONZE : 10,
        }
        
        TUTORIAL_TREASURETYPE = SILVER
    
    class HappeningState:
        """ハプニングの状態.
        """
        (
            ACTIVE,
            BOSS,
            CLEAR,
            END,
            CANCEL,
            MISS,
        ) = range(6)
        NAMES = {
            ACTIVE : u'プレイ可能',
            BOSS : u'ボス出現中',
            CLEAR : u'クリア済み未完了',
            END : u'終了済み',
            CANCEL : u'キャンセル済み',
            MISS : u'失敗処理済み',
        }
        MGR_NAMES = {
            BOSS : u'レイド出現中(タイムアウト未処理も含む)',
            CLEAR : u'クリアして未完了',
            END : u'クリアして終了済み',
            CANCEL : u'キャンセル済み',
            MISS : u'失敗処理済み',
        }
    
    class BattleResultCode:
        """対戦結果コード.
        """
        (
            WIN,
            LOSE,
        ) = range(2)
    
    class InviteState:
        """招待の状態.
        """
        (
            SEND,       # 招待中.
            RECEIVE,    # ゲーム開始.
            ACCEPT,     # チュートリアル完了.
        ) = range(3)
        NAMES = {
            SEND : u'招待中',
            RECEIVE : u'ゲーム開始',
            ACCEPT : u'完了',
        }
    
    class FromPages:
        SCOUT = 'scout'
        HAPPENING = 'happening'
        RAID = 'raid'
        RAIDLOG = 'raidlog'
        BATTLE = 'battle'
        BATTLEPRE = 'battlepre'
        FRIENDLIST = 'frlist'
        FRIENDREQUEST = 'frrequest'
        FRIENDRECEIVE = 'frreceive'
        BOSS = 'boss'
        SCOUTEVENT = 'scoutevent'
        SCOUTEVENTBOSS = 'scouteventboss'
        BATTLEEVENTPRE = 'battleeventpre'
        RAIDEVENT = 'raidevent'
        RAIDEVENTSCOUT = 'raideventscout'
        RAIDEVENTSCOUTBOSS = 'raideventscoutboss'
        PRODUCEEVENT = "produceevent"
        PRODUCEEVENTSCOUT = "produceeventscout"
        PRODUCEEVENTSCOUTBOSS = "produceeventscoutboss"
        BATTLEEVENT = 'battleevent'
        CARDBOX = 'cardbox'
        CABACLUB_STORE = 'cc_store'
        DECK_RAID = 'deck_raid'
        DECK_NORMAL = 'deck_normal'
    
    class EffectTextFormat:
        """演出で使うテキストのフォーマット.
        """
        LEVELUP_STATUSTEXT = u'レベルが%dにあがりました！'
        EVOLUTION_STARTTEXT = u'ハメ管理を開始します'
        EVOLUTION_ENDTEXT = u'%sのハメ管理度が%dになりました！\n接客力を%d引き継ぎました！'
        EVOLUTION_ENDTEXT2 = u'レベル上限が%dに上がったよ'
        EVOLUTION_ENDTEXT3_MEMORIES = u'思い出部屋の画像が開放されました！'
        EVOLUTION_ENDTEXT3_MOVIE = u'思い出部屋の画像と動画が開放されました！'
        SCOUTRESULT_COMPLETE_TEXT = u'スカウト完了！！'
        GACHA_CARDTEXT = u'%sが入店しました'
        GACHA_ITEMTEXT = u'%sを獲得しました'
        RANKINGGACHA_CARDTEXT = u'%sがお客様を連れて入店しました'
        LOGINBONUS_TEXT1 = u'連続ログイン%d日達成だよ♪'
        LOGINBONUS_TEXT2 = u'%sを受け取ってね'
        LOGINBONUS_TEXT3 = u'明日もログインすると%sがもらえるよ'
        TOTALLOGINBONUS_TEXT1 = u'累計ログイン%d日達成だよ♪'
        TOTALLOGINBONUS_TEXT2 = u'%sを受け取ってね'
        TOTALLOGINBONUS_TEXT3 = u'明日もログインすると%sがもらえるよ'
        EDUCATION_BASETEXT = u'%sを'
        EDUCATION_TRAINERTEXT = u'このキャストたちで教育します'
        EDUCATION_LASTTEXT1 = u'%sの教育に成功しました！'
        EDUCATION_LASTTEXT1_GREAT = u'%sの教育に大成功しました！'
        EDUCATION_LASTTEXT2 = u'%sのLvが上がった\n接客力が%d上がった'
        EDUCATION_SERVICETEXT = u'%sのテクニックレベルが上がった'
        BATTLEEVENT_LOGINBONUS_UP = u'オーナーお疲れ様です♪\n昨日は「%s」ランクで%s位でした！\n「%s」ランクにアップしちゃいました♪'
        BATTLEEVENT_LOGINBONUS_STAY = u'オーナーお疲れ様です♪\n昨日は「%s」ランクで%s位でした！\n今日も「%s」ランクですね♪'
        BATTLEEVENT_LOGINBONUS_DOWN = u'オーナーお疲れ様です♪\n昨日は「%s」ランクで%s位でした！\n今日は「%s」ランクに下がるけどめげませんよ♪'
        BATTLEEVENT_LOGINBONUS_2 = u'キャバ王を目指して今日も１日がんばりましょう♪'
        BATTLEEVENT_LOGINBONUS_2_RANKMAX = u'今日も１日がんばりましょう♪'
    
    class EffectIndexTables:
        BATTLE = {
            2 : (4, 5),
            4 : (4, 5, 6, 7),
            6 : (1, 2, 3, 4, 5, 8),
            8 : (1, 2, 3, 4, 5, 8, 9, 10),
            9 : (1, 2, 3, 4, 5, 6, 7, 9, 10),
        }
        EDUCATION = {
            1 : (5, ),
            2 : (4, 6),
            3 : (4, 5, 6),
            4 : (1, 3, 7, 9),
            5 : (1, 3, 5, 7, 9),
            6 : (1, 2, 3, 7, 8, 9),
            7 : (1, 2, 3, 5, 7, 8, 9),
            8 : (1, 2, 3, 4, 6, 7, 8, 9),
            9 : (1, 2, 3, 4, 5, 6, 7, 8, 9),
        }
    
    class UserLogType:
        """ユーザログ種別.
        """
        NUM_MAX = 28
        (
            LOGINBONUS,
            CARD_GET,
            CARD_SELL,
            COMPOSITION,
            EVOLUTION,
            GACHA,
            AREA_COMPLETE,
            SCOUT_COMPLETE,
            PRESENT_RECEIVE,
            PRESENT_SEND,
            ITEM_GET,
            ITEM_USE,
            TREASURE_GET,
            TREASURE_OPEN,
            TRADE,
            ADDITIONAL_TICKET,
            LOGINBONUS_TIMELIMITED,
            COMEBACK,
            CARDSTOCK,
            BATTLEEVENT_PRESENT,
            SCOUTEVENT_GACHAPT,
            RANKINGGACHA_WHOLEPRIZE,
            SCOUTEVENT_TIPGET,
            LOGINBONUS_SUGOROKU,
            LEVELUP_BONUS,
            CABACLUB_STORE,
            POINTCHANGE_TRADESHOP,
            TICKET_TRADESHOP,
        ) = range(NUM_MAX)
        
        NAMES = {
            LOGINBONUS : u'ログインボーナス受取',
            CARD_GET : u'カード獲得',
            CARD_SELL : u'カード売却',
            COMPOSITION : u'教育',
            EVOLUTION : u'ハメ管理',
            GACHA : u'ガチャ',
            AREA_COMPLETE : u'エリア達成',
            SCOUT_COMPLETE : u'スカウト達成',
            PRESENT_RECEIVE : u'プレゼント受取',
            PRESENT_SEND : u'プレゼント送信',
            ITEM_GET : u'アイテム獲得',
            ITEM_USE : u'アイテム使用',
            TREASURE_GET : u'宝箱獲得',
            TREASURE_OPEN : u'宝箱開封',
            TRADE : u'秘宝交換',
            ADDITIONAL_TICKET : u'新規追加分ガチャチケット増減',
            LOGINBONUS_TIMELIMITED : u'ロングログインボーナス',
            COMEBACK : u'カムバックキャンペーン',
            CARDSTOCK : u'キャストの異動',
            BATTLEEVENT_PRESENT : u'バトルイベント贈り物',
            SCOUTEVENT_GACHAPT : u'カカオの変動',
            RANKINGGACHA_WHOLEPRIZE : u'同伴ガチャ総計Pt達成報酬',
            SCOUTEVENT_TIPGET : u'チップ獲得',
            LOGINBONUS_SUGOROKU : u'双六ログインボーナス',
            LEVELUP_BONUS : u'レベルアップボーナス配布',
            CABACLUB_STORE : u'キャバクラ経営店舗',
            POINTCHANGE_TRADESHOP : u'PtChange交換所',
            TICKET_TRADESHOP : u'チケット交換所',
        }
    
    class LoginBonusTimeLimitedType:
        """ロングログインのタイプ.
        """
        (
            TOTAL,
            FIXATION,
            MONTHLY,
        ) = range(3)
        
        NAMES = {
            TOTAL : u'ログイン日数別',
            FIXATION : u'日付別',
            MONTHLY : u'月末',
        }
        
        FIXATION_TYPES = (
            FIXATION,
            MONTHLY,
        )
    
    class PromotionRequirementType():
        """クロスプロモーション条件タイプ.
        """
        NUM_MAX = 1
        (
            LEVEL,
        ) = range(NUM_MAX)
        
        NAMES = {
            LEVEL : u'レベル達成',
        }
    
    class PromotionStatus():
        """クロスプロモーション達成状態.
        """
        NUM_MAX = 3
        (
            NONE,
            ACHIEVED,
            RECEIVED,
        ) = range(NUM_MAX)
        
        NAMES = {
            NONE : u'未達成',
            ACHIEVED : u'達成済み',
            RECEIVED : u'受取済み',
        }
    
    class BattleEventPointCalculationType:
        """バトルイベントのポイント計算式の種別を設定.
        """
        NUM_MAX = 3
        (
            LEVEL,
            COST,
            OPPONENT_POWER,
        ) = range(NUM_MAX)
        
        NAMES = {
            LEVEL : u'レベル差',
            COST : u'コスト差',
            OPPONENT_POWER : u'対戦相手の接客力',
        }
    
    class TradeNumChoices:
        """交換数テーブル.
        """
        ALL = 0
        TABLE = (1, 5, 10, 100)
    
    class RankingGachaExpect:
        """ランキングガチャ演出の種類.
        """
        NUM_MAX = 4
        (
            LOW,
            MEDIUM,
            HIGH,
            SUPER_HIGH,
        ) = range(NUM_MAX)
        
        NAMES = {
            LOW : u'期待度低',
            MEDIUM : u'期待度中',
            HIGH : u'期待度高',
            SUPER_HIGH : u'期待度激高',
        }
    
    class PanelMissionCondition:
        """パネルミッションの達成条件種別.
        """
        NUM_MAX = 29
        (
            BATTLE_RANK_UP,         # バトルでランクアップ.
            AREA_COMPLETE,          # エリア達成.
            PLAYER_LEVEL,           # プレイヤーのレベル.
            DO_BATTLE,              # バトルをする.
            DO_SCOUT,               # スカウトをする.
            DO_COMPOSITION,         # 教育をする.
            PLAY_GACHA_FIRST,       # 初回ガチャ実行.
            PLAY_GACHA,             # ガチャ実行.
            RAID_WIN,               # 超太客成功.
            EDIT_DECK,              # デッキ編集.
            SERVICE_LEVEL,          # サービスレベル.
            EVOLUTION,              # ハメ管理.
            EVOLUTION_RING,         # 指輪でハメ管理.
            LOGINBONUS,             # ログイン日数.
            OPEN_TREASURE_GOLD,     # 金の宝箱開封.
            OPEN_TREASURE_SILVER,   # 銀の宝箱開封.
            OPEN_TREASURE_BRONZE,   # 銅の宝箱開封.
            SEND_FRIEND_REQUEST,    # フレンド申請.
            USE_ITEM,               # アイテム使用.
            RECEIVE_PRESENT,        # プレゼントを受け取る.
            VIEW_EVENT_OPENING,     # イベントOP閲覧.
            VIEW_MEMORIES_IMAGE,    # 思い出アルバム画像閲覧.
            VIEW_MEMORIES_MOVIE,    # 思い出アルバム動画閲覧.
            TRADE,                  # 秘宝交換.
            PLAY_CABACLUB,          # 店舗を開店する.
            HONOR_POINT,            # 名誉pt.
            CUSTOMER_TOTAL,         # 総来客数.
            PROCEEDS,               # 売上.
            REPRINT_TICKET,         # 復刻チケット交換所で交換.
        ) = range(NUM_MAX)
        
        NAMES = {
            BATTLE_RANK_UP:u'バトルでランクアップ',
            AREA_COMPLETE:u'エリア達成',
            PLAYER_LEVEL:u'プレイヤーのレベル',
            DO_BATTLE:u'バトルをする',
            DO_SCOUT:u'スカウトをする',
            DO_COMPOSITION:u'教育をする',
            PLAY_GACHA_FIRST:u'ガチャ実行(初回)',
            PLAY_GACHA:u'ガチャ実行',
            RAID_WIN:u'超太客成功',
            EDIT_DECK:u'デッキ編集',
            SERVICE_LEVEL:u'サービスレベル',
            EVOLUTION:u'ハメ管理',
            EVOLUTION_RING:u'指輪でハメ管理',
            LOGINBONUS:u'ログイン日数',
            OPEN_TREASURE_GOLD:u'金の宝箱開封',
            OPEN_TREASURE_SILVER:u'銀の宝箱開封',
            OPEN_TREASURE_BRONZE:u'銅の宝箱開封',
            SEND_FRIEND_REQUEST:u'フレンド申請',
            USE_ITEM:u'アイテム使用',
            RECEIVE_PRESENT:u'プレゼントを受け取る',
            VIEW_EVENT_OPENING:u'イベントOP閲覧',
            VIEW_MEMORIES_IMAGE:u'思い出アルバム画像閲覧',
            VIEW_MEMORIES_MOVIE:u'思い出アルバム動画閲覧',
            TRADE:u'秘宝交換',
            PLAY_CABACLUB:u'経営をプレイする',
            HONOR_POINT:u'名誉pt',
            CUSTOMER_TOTAL:u'総来客数',
            PROCEEDS:u'売上',
            REPRINT_TICKET:u'復刻チケット交換所で交換',
        }
        
        ENG_NAMES = {
            BATTLE_RANK_UP:'BattleRankUp',
            AREA_COMPLETE:'AreaComplete',
            PLAYER_LEVEL:'PlayerLevel',
            DO_BATTLE:'DoBattle',
            DO_SCOUT:'DoScout',
            DO_COMPOSITION:'DoComposition',
            PLAY_GACHA_FIRST:'PlayGachaFirst',
            PLAY_GACHA:'PlayGacha',
            RAID_WIN:'RaidWin',
            EDIT_DECK:'EditDeck',
            SERVICE_LEVEL:u'ServiceLevel',
            EVOLUTION:'Evolution',
            EVOLUTION_RING:'EvolutionRing',
            LOGINBONUS:'LoginBonus',
            OPEN_TREASURE_GOLD:'OpenTreasureGold',
            OPEN_TREASURE_SILVER:'OpenTreasureSilver',
            OPEN_TREASURE_BRONZE:'OpenTreasureBronze',
            SEND_FRIEND_REQUEST:'SendFriendRequest',
            USE_ITEM:'UseItem',
            RECEIVE_PRESENT:'ReceivePresent',
            VIEW_EVENT_OPENING:'ViewEventOpening',
            VIEW_MEMORIES_IMAGE:'ViewMemoriesImage',
            VIEW_MEMORIES_MOVIE:'ViewMemoriesMovie',
            TRADE:'Trade',
            PLAY_CABACLUB:'PlayCabaclub',
            HONOR_POINT:'HonorPoint',
            CUSTOMER_TOTAL:'CustomerTotal',
            PROCEEDS:'Proceeds',
            REPRINT_TICKET:'ReprintTicket',
        }
    
    class EventScenarioCommand:
        """イベントシナリオ演出のコマンド.
        """
        (
            WINDOW_OPEN,        # テキストウィンドウを開く.
            WINDOW_CLOSE,       # テキストウィンドウを閉じる.
            SET_TEXT,           # テキストを設定.
            SET_CAST_POSITION,  # キャストの位置を指定.
            WAIT,               # 指定フレーム待つ.
            MOVE_CAST,          # キャスト移動.
            FADE_CAST,          # キャストのアルファ操作.
            CHANGE_BG,          # 背景を変更.
            SET_BG_VISIBLE,     # 背景の表示非表示を設定.
            FADE_BLACK,         # 画面全体のフェード.
        ) = range(10)
    
    class SugorokuMapEventType:
        """すごろくログインのマップで発生するイベント.
        """
        (
            NONE,
            GO,
            BACK,
            LOSE_TURN,
            JUMP,
        ) = range(5)
        NAMES = {
            NONE : u'無し',
            GO : u'◯マス進む',
            BACK : u'◯マス戻る',
            LOSE_TURN : u'◯回休み',
            JUMP : u'他のマスへ飛ぶ',
        }
    
    class ShopConsumeType:
        """ショップで消費するもの.
        """
        (
            PAYMENT,    # 課金.
            GOLD,       # CG.
            CABAKING,   # 秘宝.
        ) = range(3)
        NAMES = {
            PAYMENT : u'課金',
            GOLD : u'キャバゴールド',
            CABAKING : u'キャバ王の秘宝',
        }
    
    class CabaClubEventUAType:
        """キャバクラシステムのユーザアクション.
        """
        (
            NONE,           # 無し.
            LIVEN_UP,       # 盛り上げる.
            TAKE_MEASURES,  # 対策する.
        ) = range(3)
        NAMES = {
            NONE : u'無し',
            LIVEN_UP : u'盛り上げる',
            TAKE_MEASURES : u'対策する',
        }

    class DXP:
        """Dmm x Promotion.
        """
        ow_is_release = True
        ow_is_release_staging = True
        get_incentive_level = 20
        insentive_prize_masterid = 1500
        textid = 239

        class ErrorCode:
            incentive_acquired = '905005'
