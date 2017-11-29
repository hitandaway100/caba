# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Battle import BattleRankMaster
from platinumegg.app.cabaret.models.Area import AreaMaster
from platinumegg.app.cabaret.models.PlayerLevelExp import PlayerLevelExpMaster
from platinumegg.app.cabaret.models.Item import ItemMaster
from platinumegg.app.cabaret.models.Trade import TradeMaster
from platinumegg.app.cabaret.models.CabaretClub import CabaClubStorePlayerData


class PanelMissionConditionExecuter():
    """パネルミッションの達成度進行.
    """
    
    def __init__(self):
        self.__check_targets = {}
    
    def __add_check_target(self, condition_type, *args):
        """確認対象を追加.
        """
        arr = self.__check_targets[condition_type] = self.__check_targets.get(condition_type) or []
        arr.append(args)
    
    def getTargetNum(self, condition_type):
        return len(self.__check_targets.get(condition_type) or [])
    
    def isNeedCheck(self):
        return bool(self.__check_targets)
    
    def execute(self, missionmaster, missionpaneldata, now=None):
        """ミッション進行と達成確認.
        """
        now = now or OSAUtil.get_now()

        # 現在の進行情報.
        missiondata = missionpaneldata.get_data(missionmaster.number)
        if missiondata['etime'] <= now:
            # 達成済み.
            return False
        
        # チェック項目.
        arr = self.__check_targets.get(missionmaster.condition_type)
        if not arr:
            return False
        
        # 確認用メソッド.
        engname = Defines.PanelMissionCondition.ENG_NAMES.get(missionmaster.condition_type)
        func = getattr(self, '_updateCount%s' % engname, None)
        if func is None:
            raise CabaretError(u'未実装のパネルミッションです.%d' % missionmaster.condition_type)
        
        # 確認項目を順番に処理.
        flag = False
        for args in arr:
            is_clear = func(missiondata, missionmaster.condition_value1, missionmaster.condition_value2, now, *args)
            if is_clear:
                # 達成した.
                missiondata['etime'] = now
                flag = True
                break
        # ミッション情報を更新.
        missionpaneldata.set_data(missionmaster.number, **missiondata)
        
        return flag
    
    def __execFunction(self, condition_type, raise_on_notfound, prefix, *args, **kwargs):
        """各項目ごとの関数を実行.
        """
        # 取得用メソッド.
        engname = Defines.PanelMissionCondition.ENG_NAMES.get(condition_type)
        func = getattr(self, '%s%s' % (prefix, engname), None)
        if func is None:
            if raise_on_notfound:
                raise CabaretError(u'未実装のパネルミッションです.%d' % condition_type)
            return None
        return func(*args, **kwargs)
    
    def getConditionValue(self, missionmaster):
        """達成条件の値を取得.
        """
        return self.__execFunction(missionmaster.condition_type, True, '_getConditionValue', missionmaster)
    
    def getJumpUrl(self, missionmaster):
        """ミッションの遷移先.
        """
        return self.__execFunction(missionmaster.condition_type, False, '_getJumpUrl', missionmaster)
    
    def validateMission(self, missionmaster):
        """ミッションのマスターの確認.
        """
        if not Defines.PanelMissionCondition.ENG_NAMES.get(missionmaster.condition_type):
            raise CabaretError(u'未実装のミッションです.%d' % missionmaster.condition_type)
        self.__execFunction(missionmaster.condition_type, False, '_validateMission', missionmaster)
    
    #================================
    # バトルでランクアップ.
    def addTargetBattleRankUp(self, rank):
        self.__add_check_target(Defines.PanelMissionCondition.BATTLE_RANK_UP, rank)
    
    def _updateCountBattleRankUp(self, missiondata, v1, v2, now, rank):
        target_rank = v1
        missiondata['cnt'] = max(missiondata['cnt'], rank)
        if rank < target_rank:
            return False
        
        missiondata['cnt'] = min(missiondata['cnt'], target_rank)
        return True
    
    def _getConditionValueBattleRankUp(self, missionmaster):
        # 達成したかどうかなので1.
        return 1
    
    def _getJumpUrlBattleRankUp(self, missionmaster):
        return UrlMaker.battle()
    
    def _validateMissionBattleRankUp(self, missionmaster):
        if BattleRankMaster.getByKey(missionmaster.condition_value1) is None:
            raise CabaretError(u'存在しないランクが設定されています')
    
    #================================
    # プレイヤーレベル.
    def addTargetPlayerLevel(self, level):
        self.__add_check_target(Defines.PanelMissionCondition.PLAYER_LEVEL, level)
    
    def _updateCountPlayerLevel(self, missiondata, v1, v2, now, level):
        return v1 <= level
    
    def _getConditionValuePlayerLevel(self, missionmaster):
        return missionmaster.condition_value1
    
    def _getJumpUrlPlayerLevel(self, missionmaster):
        return UrlMaker.scout()
    
    def _validateMissionPlayerLevel(self, missionmaster):
        if PlayerLevelExpMaster.getByKey(missionmaster.condition_value1) is None:
            raise CabaretError(u'存在しないプレイヤーレベルが設定されています')
    
    #================================
    # バトルをする.
    def addTargetDoBattle(self):
        self.__add_check_target(Defines.PanelMissionCondition.DO_BATTLE)
    
    def _updateCountDoBattle(self, missiondata, v1, v2, now):
        missiondata['cnt'] = min(missiondata['cnt']+1, v1)
        return v1 <= missiondata['cnt']
    
    def _getConditionValueDoBattle(self, missionmaster):
        return missionmaster.condition_value1
    
    def _getJumpUrlDoBattle(self, missionmaster):
        return UrlMaker.battle()
    
    def _validateMissionDoBattle(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # スカウトをする.
    def addTargetDoScout(self, cnt):
        self.__add_check_target(Defines.PanelMissionCondition.DO_SCOUT, cnt)
    
    def _updateCountDoScout(self, missiondata, v1, v2, now, cnt):
        missiondata['cnt'] = min(missiondata['cnt']+cnt, v1)
        return v1 <= missiondata['cnt']
    
    def _getConditionValueDoScout(self, missionmaster):
        return missionmaster.condition_value1
    
    def _getJumpUrlDoScout(self, missionmaster):
        return UrlMaker.scout()
    
    def _validateMissionDoScout(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # 教育をする.
    def addTargetDoComposition(self):
        self.__add_check_target(Defines.PanelMissionCondition.DO_COMPOSITION)
    
    def _updateCountDoComposition(self, missiondata, v1, v2, now):
        missiondata['cnt'] = min(missiondata['cnt']+1, v1)
        return v1 <= missiondata['cnt']
    
    def _getConditionValueDoComposition(self, missionmaster):
        return missionmaster.condition_value1
    
    def _getJumpUrlDoComposition(self, missionmaster):
        return UrlMaker.composition()
    
    def _validateMissionDoComposition(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # エリア達成.
    def addTargetAreaComplete(self, area):
        self.__add_check_target(Defines.PanelMissionCondition.AREA_COMPLETE, area)
    
    def _updateCountAreaComplete(self, missiondata, v1, v2, now, area):
        target_area = v1
        missiondata['cnt'] = max(missiondata['cnt'], area)
        if area < target_area:
            return False
        
        missiondata['cnt'] = min(missiondata['cnt'], target_area)
        return True
    
    def _getConditionValueAreaComplete(self, missionmaster):
        # 達成したかどうかなので1.
        return 1
    
    def _getJumpUrlAreaComplete(self, missionmaster):
        return UrlMaker.scout()
    
    def _validateMissionAreaComplete(self, missionmaster):
        if AreaMaster.getByKey(missionmaster.condition_value1) is None:
            raise CabaretError(u'存在しないエリアが設定されています')
    
    #================================
    # 初回ガチャ実行.
    def addTargetPlayGachaFirst(self, consumetype, cnt):
        self.__add_check_target(Defines.PanelMissionCondition.PLAY_GACHA_FIRST, consumetype, cnt)
    
    def _updateCountPlayGachaFirst(self, missiondata, v1, v2, now, consumetype, cnt):
        if consumetype != v1:
            return False
        
        missiondata['cnt'] = min(missiondata['cnt']+cnt, v2)
        return v2 <= missiondata['cnt']
    
    def _getConditionValuePlayGachaFirst(self, missionmaster):
        return missionmaster.condition_value2
    
    def _getJumpUrlPlayGachaFirst(self, missionmaster):
        consumetype = missionmaster.condition_value1
        url = UrlMaker.gacha()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.TO_TOPIC[consumetype])
        url = OSAUtil.addQuery(url, Defines.URLQUERY_GTYPE, Defines.GachaConsumeType.GTYPE_NAMES[consumetype])
        return url
    
    def _validateMissionPlayGachaFirst(self, missionmaster):
        if not Defines.GachaConsumeType.NAMES.has_key(missionmaster.condition_value1):
            raise CabaretError(u'存在しないガチャが指定されています')
        elif missionmaster.condition_value2 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # ガチャ実行.
    def addTargetPlayGacha(self, consumetype, cnt):
        self.__add_check_target(Defines.PanelMissionCondition.PLAY_GACHA, consumetype, cnt)
    
    def _updateCountPlayGacha(self, missiondata, v1, v2, now, consumetype, cnt):
        if consumetype != v1:
            return False
        
        missiondata['cnt'] = min(missiondata['cnt']+cnt, v2)
        return v2 <= missiondata['cnt']
    
    def _getConditionValuePlayGacha(self, missionmaster):
        return missionmaster.condition_value2
    
    def _getJumpUrlPlayGacha(self, missionmaster):
        consumetype = missionmaster.condition_value1
        url = UrlMaker.gacha()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.TO_TOPIC[consumetype])
        url = OSAUtil.addQuery(url, Defines.URLQUERY_GTYPE, Defines.GachaConsumeType.GTYPE_NAMES[consumetype])
        return url
    
    def _validateMissionPlayGacha(self, missionmaster):
        if not Defines.GachaConsumeType.NAMES.has_key(missionmaster.condition_value1):
            raise CabaretError(u'存在しないガチャが指定されています')
        elif missionmaster.condition_value2 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # 超太客成功.
    def addTargetRaidWin(self, level):
        self.__add_check_target(Defines.PanelMissionCondition.RAID_WIN, level)
    
    def _updateCountRaidWin(self, missiondata, v1, v2, now, level):
        if level < v1:
            return False
        
        missiondata['cnt'] = min(missiondata['cnt']+1, v2)
        return v2 <= missiondata['cnt']
    
    def _getConditionValueRaidWin(self, missionmaster):
        return missionmaster.condition_value2
    
    def _getJumpUrlRaidWin(self, missionmaster):
        return UrlMaker.happening()
    
    def _validateMissionRaidWin(self, missionmaster):
        if missionmaster.condition_value2 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # デッキ編集.
    def addTargetEditDeck(self, no1_change):
        self.__add_check_target(Defines.PanelMissionCondition.EDIT_DECK, no1_change)
    
    def _updateCountEditDeck(self, missiondata, v1, v2, now, no1_change):
        if v1:
            return no1_change
        return True
    
    def _getConditionValueEditDeck(self, missionmaster):
        return 1
    
    def _getJumpUrlEditDeck(self, missionmaster):
        return UrlMaker.deck()
    
    #================================
    # キャストのサービスレベル.
    def addTargetServiceLevel(self, skilllevel):
        self.__add_check_target(Defines.PanelMissionCondition.SERVICE_LEVEL, skilllevel)
    
    def _updateCountServiceLevel(self, missiondata, v1, v2, now, skilllevel):
        return v1 <= skilllevel
    
    def _getConditionValueServiceLevel(self, missionmaster):
        return missionmaster.condition_value1
    
    def _getJumpUrlServiceLevel(self, missionmaster):
        return UrlMaker.composition()
    
    def _validateMissionServiceLevel(self, missionmaster):
        if not (1 <= missionmaster.condition_value1 <= Defines.SKILLLEVEL_MAX):
            raise CabaretError(u'サービスレベルは1〜%dで設定してください' % Defines.SKILLLEVEL_MAX)
    
    #================================
    # ハメ管理.
    def addTargetEvolution(self, hklevel):
        self.__add_check_target(Defines.PanelMissionCondition.EVOLUTION, hklevel)
    
    def _updateCountEvolution(self, missiondata, v1, v2, now, hklevel):
        if v1 <= hklevel:
            missiondata['cnt'] = min(missiondata['cnt']+1, v2)
        return v2 <= missiondata['cnt']
    
    def _getConditionValueEvolution(self, missionmaster):
        return missionmaster.condition_value2
    
    def _getJumpUrlEvolution(self, missionmaster):
        return UrlMaker.evolution()
    
    def _validateMissionEvolution(self, missionmaster):
        if not (1 <= missionmaster.condition_value1 <= Defines.HKLEVEL_MAX):
            raise CabaretError(u'ハメ管理度は1〜%dで設定してください' % Defines.HKLEVEL_MAX)
        elif missionmaster.condition_value2 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # 指輪でハメ管理.
    def addTargetEvolutionRing(self, hklevel):
        self.__add_check_target(Defines.PanelMissionCondition.EVOLUTION_RING, hklevel)
    
    def _updateCountEvolutionRing(self, missiondata, v1, v2, now, hklevel):
        if v1 <= hklevel:
            missiondata['cnt'] = min(missiondata['cnt']+1, v2)
        return v2 <= missiondata['cnt']
    
    def _getConditionValueEvolutionRing(self, missionmaster):
        return missionmaster.condition_value2
    
    def _getJumpUrlEvolutionRing(self, missionmaster):
        return UrlMaker.evolution()
    
    def _validateMissionEvolutionRing(self, missionmaster):
        if not (1 <= missionmaster.condition_value1 <= Defines.HKLEVEL_MAX):
            raise CabaretError(u'ハメ管理度は1〜%dで設定してください' % Defines.HKLEVEL_MAX)
        elif missionmaster.condition_value2 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # ログイン日数.
    def addTargetLoginBonus(self):
        self.__add_check_target(Defines.PanelMissionCondition.LOGINBONUS)
    
    def _updateCountLoginBonus(self, missiondata, v1, v2, now):
        missiondata['cnt'] = min(missiondata['cnt']+1, v1)
        return v1 <= missiondata['cnt']
    
    def _getConditionValueLoginBonus(self, missionmaster):
        return missionmaster.condition_value1
    
    def _getJumpUrlLoginBonus(self, missionmaster):
        return None
    
    def _validateMissionLoginBonus(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'ログイン日数は自然数で設定してください')
    
    #================================
    # 金の宝箱開封.
    def addTargetOpenTreasureGold(self, cnt):
        self.__add_check_target(Defines.PanelMissionCondition.OPEN_TREASURE_GOLD, cnt)
    
    def _updateCountOpenTreasureGold(self, missiondata, v1, v2, now, cnt):
        missiondata['cnt'] = min(missiondata['cnt']+cnt, v1)
        return v1 <= missiondata['cnt']
    
    def _getConditionValueOpenTreasureGold(self, missionmaster):
        return missionmaster.condition_value1
    
    def _getJumpUrlOpenTreasureGold(self, missionmaster):
        return UrlMaker.treasurelist(Defines.TreasureType.GOLD)
    
    def _validateMissionOpenTreasureGold(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # 銀の宝箱開封.
    def addTargetOpenTreasureSilver(self, cnt):
        self.__add_check_target(Defines.PanelMissionCondition.OPEN_TREASURE_SILVER, cnt)
    
    def _updateCountOpenTreasureSilver(self, missiondata, v1, v2, now, cnt):
        missiondata['cnt'] = min(missiondata['cnt']+cnt, v1)
        return v1 <= missiondata['cnt']
    
    def _getConditionValueOpenTreasureSilver(self, missionmaster):
        return missionmaster.condition_value1
    
    def _getJumpUrlOpenTreasureSilver(self, missionmaster):
        return UrlMaker.treasurelist(Defines.TreasureType.SILVER)
    
    def _validateMissionOpenTreasureSilver(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # 銅の宝箱開封.
    def addTargetOpenTreasureBronze(self, cnt):
        self.__add_check_target(Defines.PanelMissionCondition.OPEN_TREASURE_BRONZE, cnt)
    
    def _updateCountOpenTreasureBronze(self, missiondata, v1, v2, now, cnt):
        missiondata['cnt'] = min(missiondata['cnt']+cnt, v1)
        return v1 <= missiondata['cnt']
    
    def _getConditionValueOpenTreasureBronze(self, missionmaster):
        return missionmaster.condition_value1
    
    def _getJumpUrlOpenTreasureBronze(self, missionmaster):
        return UrlMaker.treasurelist(Defines.TreasureType.BRONZE)
    
    def _validateMissionOpenTreasureBronze(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # フレンド申請.
    def addTargetSendFriendRequest(self, cnt):
        self.__add_check_target(Defines.PanelMissionCondition.SEND_FRIEND_REQUEST, cnt)
    
    def _updateCountSendFriendRequest(self, missiondata, v1, v2, now, cnt):
        missiondata['cnt'] = min(missiondata['cnt']+cnt, v1)
        return v1 <= missiondata['cnt']
    
    def _getConditionValueSendFriendRequest(self, missionmaster):
        return missionmaster.condition_value1
    
    def _getJumpUrlSendFriendRequest(self, missionmaster):
        return UrlMaker.friendlist()
    
    def _validateMissionSendFriendRequest(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # アイテム使用.
    def addTargetUseItem(self, mid, cnt):
        self.__add_check_target(Defines.PanelMissionCondition.USE_ITEM, mid, cnt)
    
    def _updateCountUseItem(self, missiondata, v1, v2, now, mid, cnt):
        if v1 == mid:
            missiondata['cnt'] = min(missiondata['cnt']+cnt, v2)
        return v2 <= missiondata['cnt']
    
    def _getConditionValueUseItem(self, missionmaster):
        return missionmaster.condition_value2
    
    def _getJumpUrlUseItem(self, missionmaster):
        return UrlMaker.itemlist()
    
    def _validateMissionUseItem(self, missionmaster):
        if ItemMaster.getByKey(missionmaster.condition_value1) is None:
            raise CabaretError(u'存在しないアイテムが設定されています')
        elif missionmaster.condition_value2 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # プレゼントを受け取る.
    def addTargetReceivePresent(self, cnt):
        self.__add_check_target(Defines.PanelMissionCondition.RECEIVE_PRESENT, cnt)
    
    def _updateCountReceivePresent(self, missiondata, v1, v2, now, cnt):
        missiondata['cnt'] = min(missiondata['cnt']+cnt, v1)
        return v1 <= missiondata['cnt']
    
    def _getConditionValueReceivePresent(self, missionmaster):
        return missionmaster.condition_value1
    
    def _getJumpUrlReceivePresent(self, missionmaster):
        return UrlMaker.present()
    
    def _validateMissionReceivePresent(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # イベントOP閲覧.
    def addTargetViewEventOpening(self):
        self.__add_check_target(Defines.PanelMissionCondition.VIEW_EVENT_OPENING)
    
    def _updateCountViewEventOpening(self, missiondata, v1, v2, now):
        missiondata['cnt'] = min(missiondata['cnt']+1, v1)
        return v1 <= missiondata['cnt']
    
    def _getConditionValueViewEventOpening(self, missionmaster):
        return missionmaster.condition_value1
    
    def _getJumpUrlViewEventOpening(self, missionmaster):
        return None
    
    def _validateMissionViewEventOpening(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # 思い出アルバム画像閲覧.
    def addTargetViewMemoriesImage(self):
        self.__add_check_target(Defines.PanelMissionCondition.VIEW_MEMORIES_IMAGE)
    
    def _updateCountViewMemoriesImage(self, missiondata, v1, v2, now):
        missiondata['cnt'] = min(missiondata['cnt']+1, v1)
        return v1 <= missiondata['cnt']
    
    def _getConditionValueViewMemoriesImage(self, missionmaster):
        return missionmaster.condition_value1
    
    def _getJumpUrlViewMemoriesImage(self, missionmaster):
        return UrlMaker.album()
    
    def _validateMissionViewMemoriesImage(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # 思い出アルバム動画閲覧.
    def addTargetViewMemoriesMovie(self):
        self.__add_check_target(Defines.PanelMissionCondition.VIEW_MEMORIES_MOVIE)
    
    def _updateCountViewMemoriesMovie(self, missiondata, v1, v2, now):
        missiondata['cnt'] = min(missiondata['cnt']+1, v1)
        return v1 <= missiondata['cnt']
    
    def _getConditionValueViewMemoriesMovie(self, missionmaster):
        return missionmaster.condition_value1
    
    def _getJumpUrlViewMemoriesMovie(self, missionmaster):
        return UrlMaker.album()
    
    def _validateMissionViewMemoriesMovie(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'回数は自然数で設定してください')
    
    #================================
    # 秘宝交換.
    def addTargetTrade(self, trademaster):
        self.__add_check_target(Defines.PanelMissionCondition.TRADE, trademaster)
    
    def _updateCountTrade(self, missiondata, v1, v2, now, trademaster):
        if v1 == 0 and v2 == 0:
            return True
        return v1 == trademaster.itype and v2 == trademaster.itemid
    
    def _getConditionValueTrade(self, missionmaster):
        return 1
    
    def _getJumpUrlTrade(self, missionmaster):
        return UrlMaker.trade()
    
    def _validateMissionTrade(self, missionmaster):
        if missionmaster.condition_value1 == 0 and missionmaster.condition_value2 == 0:
            return
        
        filters = {
            'itype' : missionmaster.condition_value1,
            'itemid' : missionmaster.condition_value2,
        }
        if not TradeMaster.fetchValues(fields=['id'], filters=filters, limit=1):
            raise CabaretError(u'存在しない秘宝交換が設定されています')

    #================================
    # 店舗を開店する.
    def addTargetPlayCabaclub(self):
        self.__add_check_target(Defines.PanelMissionCondition.PLAY_CABACLUB)

    def _updateCountPlayCabaclub(self, missiondata, v1, v2, now):
        border_play_cnt = v1
        # 今回のプレイ分を加算
        current_play_cnt = missiondata['cnt'] + 1

        # カウントがしきい値より越えないように念の為
        missiondata['cnt'] = min(current_play_cnt, border_play_cnt)

        return border_play_cnt <= current_play_cnt

    def _getConditionValuePlayCabaclub(self, missionmaster):
        return missionmaster.condition_value1

    def _getJumpUrlPlayCabaclub(self, missionmaster):
        return UrlMaker.cabaclubtop()

    def _validateMissionPlayCabaclub(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'回数は自然数で設定してください')

    #================================
    # 名誉pt.
    def addTargetHonorPoint(self, point):
        self.__add_check_target(Defines.PanelMissionCondition.HONOR_POINT, point)

    def _updateCountHonorPoint(self, missiondata, v1, v2, now, point):
        cur_point = max(point, missiondata['cnt'])
        missiondata['cnt'] = min(cur_point, v1)
        return v1 <= missiondata['cnt']

    def _getConditionValueHonorPoint(self, missionmaster):
        return missionmaster.condition_value1

    def _getJumpUrlHonorPoint(self, missionmaster):
        return UrlMaker.cabaclubtop()

    def _validateMissionHonorPoint(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'名誉ptは自然数で設定してください')

    #================================
    # 総来客数.
    def addTargetCustomerTotal(self, customer):
        self.__add_check_target(Defines.PanelMissionCondition.CUSTOMER_TOTAL, customer)

    def _updateCountCustomerTotal(self, missiondata, v1, v2, now, customer):
        cur_customer = max(customer, missiondata['cnt'])
        missiondata['cnt'] = min(cur_customer, v1)
        return v1 <= missiondata['cnt']

    def _getConditionValueCustomerTotal(self, missionmaster):
        return missionmaster.condition_value1

    def _getJumpUrlCustomerTotal(self, missionmaster):
        return UrlMaker.cabaclubtop()

    def _validateMissionCustomerTotal(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'総来客数は自然数で設定してください')

    #================================
    # 売上.
    def addTargetProceeds(self, proceeds):
        self.__add_check_target(Defines.PanelMissionCondition.PROCEEDS, proceeds)

    def _updateCountProceeds(self, missiondata, v1, v2, now, proceeds):
        try:
            cur_proceeds = int(proceeds / 1000)
        except ZeroDivisionError as error:
            cur_proceeds = 0
        cur_proceeds = max(cur_proceeds, missiondata['cnt'])
        missiondata['cnt'] = min(cur_proceeds, v1)
        return v1 <= missiondata['cnt']

    def _getConditionValueProceeds(self, missionmaster):
        return missionmaster.condition_value1 * 1000

    def _getJumpUrlProceeds(self, missionmaster):
        return UrlMaker.cabaclubtop()

    def _validateMissionProceeds(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'売上は自然数で設定してください')

    #================================
    # 復刻チケット交換所で交換.
    def addTargetReprintTicket(self):
        self.__add_check_target(Defines.PanelMissionCondition.REPRINT_TICKET)

    def _updateCountReprintTicket(self, missiondata, v1, v2, now):
        border_trade_cnt = v1
        # 今回の交換分を加算
        current_trade_cnt = missiondata['cnt'] + 1

        # カウントがしきい値より越えないように念の為
        missiondata['cnt'] = min(current_trade_cnt, border_trade_cnt)

        return border_trade_cnt <= current_trade_cnt

    def _getConditionValueReprintTicket(self, missionmaster):
        return missionmaster.condition_value1

    def _getJumpUrlReprintTicket(self, missionmaster):
        return UrlMaker.reprintticket_tradeshop(ticket_id=Defines.GachaConsumeType.GachaTicketType.REPRINT_TICKET)

    def _validateMissionReprintTicket(self, missionmaster):
        if missionmaster.condition_value1 < 1:
            raise CabaretError(u'交換回数は自然数で設定してください')
