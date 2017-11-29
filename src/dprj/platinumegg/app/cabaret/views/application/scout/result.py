# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.scout.base import ScoutHandler
import urllib
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerExp,\
    PlayerGold, PlayerDeck, PlayerFriend
from defines import Defines
from platinumegg.app.cabaret.util.card import CardSet
import settings_sub
from platinumegg.app.cabaret.util.happening import HappeningRaidSet


class Handler(ScoutHandler):
    """スカウト結果.
    引数:
        実行したスカウトのID.
        確認キー.
    共通で埋め込むもの:
        スカウト情報.
        プレイヤー情報.
        スカウトを続けるURL.
    結果のパターン:
        レベルアップ.
            スカウト達成があるかも.
        スカウト達成.
        アイテム獲得.
        トロフィ獲得.
        カード獲得.
        行動力が足りない.
        なにも起きなかった.
            scoutdoへリダイレクト.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerFriend, PlayerExp, PlayerGold, PlayerDeck]
    
    def process(self):
        args = self.getUrlArgs('/scoutresult/')
        try:
            scoutid = int(args.get(0))
            scoutkey = urllib.unquote(args.get(1))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        # 進行情報.
        playdata = BackendApi.get_scoutprogress(model_mgr, v_player.id, [scoutid], using=using).get(scoutid, None)
        if playdata and playdata.confirmkey == scoutkey:
            # DBからとり直すべき.
            playdata = BackendApi.get_scoutprogress(model_mgr, v_player.id, [scoutid], using=settings.DB_DEFAULT, reflesh=True).get(scoutid, None)
        
        if playdata is None or playdata.alreadykey != scoutkey:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'キーが正しくありません %s vs %s' % (playdata.alreadykey if playdata else 'None', scoutkey))
            url = self.makeAppLinkUrlRedirect(UrlMaker.scout())
            self.appRedirect(url)
            return
        
        # プレイヤー.
        self.html_param['player'] = Objects.player(self, v_player)
        
        # スカウト.
        arr = BackendApi.get_scouts(model_mgr, [scoutid], using=using)
        scoutmaster = arr[0] if arr else None
        self.html_param['scout'] = self.makeScoutObj(scoutmaster, playdata)
        
        # エリアマスターデータ.
        areamaster = BackendApi.get_area(model_mgr, scoutmaster.area, using)
        if areamaster is None:
            url = self.makeAppLinkUrlRedirect(UrlMaker.scout())
            self.appRedirect(url)
            return
        
        # エリアクリア情報.
        areaplaydata = BackendApi.get_areaplaydata(model_mgr, v_player.id, [areamaster.id], using).get(areamaster.id)
        self.html_param['area'] = Objects.area(self, areamaster, areaplaydata)
        
        # 続ける.
        url = UrlMaker.scoutdo(scoutmaster.id, playdata.confirmkey)
        self.html_param['url_scoutdo'] = self.makeAppLinkUrl(url)
        
        eventlist = playdata.result.get('event', [])
        if not eventlist:
            raise CabaretError(u'スカウト実行の実装に問題があります')
        
        # レイドイベント.
        BackendApi.put_raidevent_champagnedata(self, v_player.id)
        
        table = (
            (Defines.ScoutEventType.LEVELUP, self.procLevelup),
            (Defines.ScoutEventType.GET_CARD, self.procGetCard),
            (Defines.ScoutEventType.GET_TREASURE, self.procGetTreasure),
            (Defines.ScoutEventType.COMPLETE, self.procComplete),
            (Defines.ScoutEventType.HAPPENING, self.procHappening),
            (Defines.ScoutEventType.AP_NONE, self.procApNone),
            (Defines.ScoutEventType.NONE, self.procNone),
        )
        
        eventdict = {}
        for event in eventlist:
            eventdict[event.get_type()] = event
        self.__eventdict = eventdict
        
        # スカウト結果.
        resultlist = playdata.result.get('result', [])
        self.html_param['scoutresultinfo'] = BackendApi.make_scoutresult_info(resultlist)
        
        for eventtype, func in table:
            event = eventdict.get(eventtype)
            if event:
                func(scoutmaster, playdata, event)
                return
        raise CabaretError(u'実行可能なスカウト内イベントがありません')
    
    def procLevelup(self, scoutmaster, playdata, event):
        """レベルアップ.
        """
        model_mgr = self.getModelMgr()
        
        v_player = self.getViewerPlayer()
        if event.level != v_player.level:
            url = UrlMaker.scoutdo(scoutmaster.id, playdata.confirmkey)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        self.html_param['levelup_info'] = BackendApi.make_playerlevelup_info(model_mgr, v_player, using=settings.DB_READONLY)
        
        if self.__eventdict.has_key(Defines.ScoutEventType.COMPLETE):
            self.__putCompleteData(model_mgr, scoutmaster)
        
        self.writeAppHtml('scout/levelup')
    
    def __putCompleteData(self, model_mgr, scoutmaster):
        nextscoutid = BackendApi.get_next_scoutid(model_mgr, scoutmaster.id, using=settings.DB_READONLY)
        flag_boss = False
        if nextscoutid == scoutmaster.id:
            flag_boss = True
        else:
            arr = BackendApi.get_scouts(model_mgr, [nextscoutid], using=settings.DB_READONLY)
            nextscoutmaster = arr[0] if arr else None
            if nextscoutmaster:
                if nextscoutmaster.area == scoutmaster.area:
                    self.html_param['next_scout'] = self.makeScoutObj(nextscoutmaster, None)
                else:
                    flag_boss = True
        
        if flag_boss:
            # ボス出現.
            areamaster = BackendApi.get_area(model_mgr, scoutmaster.area, using=settings.DB_READONLY)
            if areamaster.boss:
                boss = BackendApi.get_boss(model_mgr, areamaster.boss, using=settings.DB_READONLY)
                if boss:
                    self.html_param['boss'] = Objects.boss(self, boss)
                    self.html_param['url_bossbattle'] = self.makeAppLinkUrl(UrlMaker.bosspre(areamaster.id))
    
    def procComplete(self, scoutmaster, playdata, event):
        """スカウト完了.
        """
        model_mgr = self.getModelMgr()
        self.__putCompleteData(model_mgr, scoutmaster)
        self.writeAppHtml('scout/complete')
    
    def procGetCard(self, scoutmaster, playdata, event):
        """カード獲得.
        """
        if event.is_received:
            # 終了済み.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'判定済みです', CabaretError.Code.ALREADY_RECEIVED)
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.scoutcardgetresult(playdata.mid)))
            return
        
        model_mgr = self.getModelMgr()
        
        # 獲得したカード.
        cardid = event.card
        cardmaster = BackendApi.get_cardmasters([cardid], model_mgr, using=settings.DB_READONLY).get(cardid)
        if cardmaster is None:
            raise CabaretError(u'一度公開されたキャストが非公開にされました.危険です.', CabaretError.Code.INVALID_MASTERDATA)
        card = BackendApi.create_card_by_master(cardmaster)
        self.html_param['card'] = Objects.card(self, CardSet(card, cardmaster), is_new=event.is_new)
        
        # 獲得判定へ飛ぶ.
        url = UrlMaker.scoutcardget(playdata.mid)
        self.html_param['url_exec'] = self.makeAppLinkUrl(url)
        
        # アイテム.
        BackendApi.put_scoutcard_uselead_info(self, UrlMaker.scoutcardget(playdata.mid))
        
        self.writeAppHtml('scout/cardget')
    
    def procGetTreasure(self, scoutmaster, playdata, event):
        """宝箱発見.
        """
        self.html_param['treasure_view'] = Objects.treasure_view(self, event.treasuretype)
        self.writeAppHtml('scout/treasureget')
    
    def procApNone(self, scoutmaster, playdata, event):
        """行動力が足りない.
        """
        v_player = self.getViewerPlayer()
        
        apcost = BackendApi.get_apcost(scoutmaster, v_player)
        if apcost <= v_player.get_ap():
            # 行動力が回復している.
            url = UrlMaker.scoutdo(scoutmaster.id, playdata.confirmkey)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        self.setFromPage(Defines.FromPages.SCOUT, scoutmaster.id)
        
        # 回復アイテム.
        BackendApi.put_aprecover_uselead_info(self)
        
        self.writeAppHtml('scout/apnone')
    
    def procNone(self, scoutmaster, playdata, event):
        """なにも起きなかった.
        """
        flag_skip = BackendApi.get_scoutskip_flag(playdata.uid)
        if flag_skip:
            self.writeAppHtml('scout/none')
        else:
            url = UrlMaker.scoutdo(scoutmaster.id, playdata.confirmkey)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def procHappening(self, scoutmaster, playdata, event):
        """ハプニング発生.
        """
        using = playdata.current_db
        
        model_mgr = self.getModelMgr()
        happeningid = BackendApi.get_current_happeningid(model_mgr, playdata.uid, using=using, reflesh=True)
        happeningset = BackendApi.get_happening(model_mgr, happeningid, using=using)
        if happeningset is None or happeningset.happening.is_end():
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'ハプニングが発生していません')
            url = UrlMaker.scout()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        raidboss = BackendApi.get_raid(model_mgr, happeningset.id, using=using, happening_eventvalue=happeningset.happening.event)
        happeningraidset = HappeningRaidSet(happeningset, raidboss)
        self.html_param['happening'] = Objects.happening(self, happeningraidset)
        
        # レイドボス.
        raidmaster = BackendApi.get_raid_master(model_mgr, happeningset.master.boss, using=settings.DB_READONLY)
        self.html_param['boss'] = Objects.raidmaster(self, raidmaster)
        
        self.writeAppHtml('scout/happening')
    

def main(request):
    return Handler.run(request)
