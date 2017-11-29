# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerRegist, PlayerExp
import operator
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.happening import HappeningUtil


class HappeningHandler(AppHandler):
    """ハプニングのハンドラ.
    """
    
    class HappeningRaidSetLocal():
        def __init__(self, happeningraidset):
            self.happeningraidset = happeningraidset
    
    def preprocess(self):
        AppHandler.preprocess(self)
        self.__happeningraidset = None
        self.__prizelist = None
        self.__leaderlist = None
    
    def getHappeningRaidSet(self):
        """進行情報.
        """
        if self.__happeningraidset is None:
            v_player = self.getViewerPlayer()
            model_mgr = self.getModelMgr()
            
            happeningraidset = None
            happeningid = BackendApi.get_current_producehappeningid(model_mgr, v_player.id, using=settings.DB_READONLY, reflesh=True)
            if happeningid:
                happeningraidset = BackendApi.get_producehappeningraidset(model_mgr, happeningid, using=settings.DB_READONLY)
            self.__happeningraidset = HappeningHandler.HappeningRaidSetLocal(happeningraidset)
        return self.__happeningraidset.happeningraidset
    
    def getHappening(self):
        """ハプニング.
        """
        happeningraidset = self.getHappeningRaidSet()
        happening = None
        if happeningraidset:
            happening = happeningraidset.happening
        return happening
    
    def getHappeningMaster(self):
        happeningset = self.getHappening()
        if happeningset:
            return happeningset.master
        return None

    def getRaidBoss(self):
        """レイドボス.
        """
        happeningraidset = self.getHappeningRaidSet()
        raidboss = None
        if happeningraidset:
            raidboss = happeningraidset.raidboss
        return raidboss
    
    def getPooledPrizeList(self, cancel=False):
        """プールされている報酬一覧.
        """
        if self.__prizelist is None:
            happening = self.getHappening()
            prizelist = []
            if happening:
                prizelist = BackendApi.aggregate_happeningprize(happening.happening, cancel)
            self.__prizelist = prizelist
        return self.__prizelist
    
    def putHappeningInfo(self, do_get_end=False):
        """ハプニング情報作成.
        """
        happeningraidset = self.getHappeningRaidSet()
        if not happeningraidset:
            return
        
        happeningset = happeningraidset.happening
        if not do_get_end and happeningset.happening.is_end():
            return
        
        # 獲得した報酬.
        prizelist = self.getPooledPrizeList(happeningset.happening.is_canceled())
        prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
        
        # ハプニング情報.
        obj_happening = Objects.producehappening(self, happeningraidset, prizeinfo)
        self.html_param['happening'] = obj_happening
        
        return obj_happening
    
    def putRaidHelpList(self, do_execute=True, limit=None, offset=0):
        """救援依頼一覧を埋め込む.
        """
        limit = limit or Defines.RAIDHELP_LIST_MAXLENGTH
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        raidhelpidlist = BackendApi.get_raidhelpidlist(model_mgr, v_player.id, limit=limit, offset=offset, using=settings.DB_READONLY)
        raidhelplist = BackendApi.get_raidhelplist(model_mgr, raidhelpidlist, using=settings.DB_READONLY)
        if len(raidhelplist) == 0:
            self.html_param['raidhelplist'] = []
            return None
        
        raididlist = []
        oid_set = set()
        for raidhelp in raidhelplist:
            raididlist.append(raidhelp.raidid)
            oid_set.add(raidhelp.fromid)
        
        o_playerlist = BackendApi.get_players(self, oid_set, [], using=settings.DB_READONLY, model_mgr=model_mgr)
        o_playerdict = dict([(o_player.id, o_player) for o_player in o_playerlist])
        persons = BackendApi.get_dmmplayers(self, o_playerlist, using=settings.DB_READONLY, do_execute=do_execute)
        
        raidid_items = dict([(raidhelp.raidid, raidhelp) for raidhelp in raidhelplist])
        raididlist = raidid_items.keys()
        happeningraidset_dict = dict([(model.id, model) for model in  BackendApi.get_happeningraidset_list(model_mgr, raididlist, using=settings.DB_READONLY) if model.happening.happening.is_active()])
        leaders = BackendApi.get_leaders(oid_set, model_mgr, using=settings.DB_READONLY)
        
        endidlist = list(set(raididlist) - set(happeningraidset_dict.keys()))
        if endidlist:
            BackendApi.remove_raidhelpid_list([raidid_items[endid] for endid in endidlist])
            self.addlog(u'remove_raidhelpid_list:%s' % endidlist)
        
        def cb():
            now = OSAUtil.get_now()
            
            obj_raidlist = []
            for raidhelp in raidhelplist:
                if happeningraidset_dict.has_key(raidhelp.raidid):
                    happeningraidset = happeningraidset_dict[raidhelp.raidid]
                    happeningset = happeningraidset.happening
                    raidboss = happeningraidset.raidboss
                    
                    if happeningset.happening.event:
                        eventraidmaster = BackendApi.get_eventraidmaster_by_modeleventvalue(model_mgr, happeningset.happening.event, raidboss.master.id, using=settings.DB_READONLY)
                        raidboss.setEventRaidMaster(eventraidmaster)
                    
                    o_person = None
                    o_player = o_playerdict.get(raidhelp.fromid)
                    if o_player:
                        o_person = persons.get(o_player.dmmid)
                    obj_raid = Objects.raid(self, raidboss, o_person, leaders.get(raidhelp.fromid))
                    obj_raid['timelimit'] = Objects.timelimit(happeningset.happening.etime, now)
                    obj_raidlist.append(obj_raid)
            
            self.html_param['raidhelplist'] = obj_raidlist
        
        if do_execute:
            cb()
            return None
        else:
            return cb
    
    def putRaidAttackLog(self, raidboss, excludes=None):
        """レイドの攻撃履歴を埋め込む.
        """
        params = {}
        
        if raidboss is None:
            return None
        
        excludes = excludes or []
        
        model_mgr = self.getModelMgr()
        recordlist = raidboss.getDamageRecordList()
        
        damagerecordnum = 0
        uidlist = []
        for record in recordlist:
            if record.damage_cnt == 0:
                continue
            
            damagerecordnum += 1
            if not record.uid in excludes:
                uidlist.append(record.uid)
        
        playerlist = BackendApi.get_players(self, uidlist, [PlayerRegist, PlayerExp], using=settings.DB_READONLY, model_mgr=model_mgr)
        playerdict = dict([(player.id, player) for player in playerlist])
        persons = BackendApi.get_dmmplayers(self, playerlist, using=settings.DB_READONLY, do_execute=False)
        leaders = BackendApi.get_leaders(uidlist, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
        
        border_damage = raidboss.getBorderDamageForPrizeGet()
        
        params['damagerecordnum'] = damagerecordnum
        
        def execute_end():
            obj_recordlist = []
            for record in recordlist:
                player = playerdict.get(record.uid)
                if not player:
                    continue
                person = persons[player.dmmid]
                leader = leaders[player.id]
                obj_recordlist.append(Objects.raid_damage_record(self, player, person, leader, record.damage, record.damage_cnt, border_damage))
            
            params['damagerecordlist'] = obj_recordlist
            
            self.html_param.update(**params)
        return execute_end
    
    def __getFriendLeaderCardList(self):
        """フレンドのリーダーカードを取得.
        """
        if self.__leaderlist is None:
            v_player = self.getViewerPlayer()
            model_mgr = self.getModelMgr()
            uidlist = BackendApi.get_friend_idlist(v_player.id, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
            
            leaderlist = BackendApi.get_raid_leaders(uidlist, arg_model_mgr=model_mgr, using=settings.DB_READONLY).values()
            leaderlist.sort(key=operator.attrgetter('power'), reverse=True)
            self.__leaderlist = leaderlist
        return self.__leaderlist
    
    def getFriendLeaderCardList(self, limit=None, offset=0):
        """フレンドのリーダーカードを取得.
        """
        leaderlist = self.__getFriendLeaderCardList()
        if limit:
            return leaderlist[offset:(offset + limit)]
        else:
            return leaderlist[offset:]
    
    def getFriendLeaderCardNum(self):
        """フレンドのリーダーカード数を取得.
        """
        return len(self.__getFriendLeaderCardList())
    
    def getSelectedFriendCard(self, raidid, do_set_default=True):
        """選択済みのリーダーカード.
        """
        v_player = self.getViewerPlayer()
        if not BackendApi.raid_is_can_callfriend(v_player.id):
            BackendApi.delete_raidhelpcard(v_player.id)
            return None
        
        model_mgr = self.getModelMgr()
        cardset = BackendApi.get_raidhelpcard(model_mgr, v_player.id, raidid, using=settings.DB_READONLY)
        
        if cardset:
            if not BackendApi.check_friend(v_player.id, cardset.card.uid, model_mgr, using=settings.DB_READONLY):
                BackendApi.delete_raidhelpcard(v_player.id)
                cardset = None
        
        if cardset is None and do_set_default and not BackendApi.check_raidhelpcard_canceled(model_mgr, v_player.id, raidid, using=settings.DB_READONLY):
            cardlist = self.getFriendLeaderCardList(1)
            if cardlist:
                cardset = cardlist[0]
                BackendApi.save_raidhelpcard(model_mgr, v_player.id, raidid, cardset, using=settings.DB_READONLY)
        return cardset
    
    def putPlayerListByLeaderList(self, raidid, leaderlist):
        """リーダーカードからプレイヤーリストを作成して埋め込む.
        """
        model_mgr = self.getModelMgr()
        
        uidlist = [leader.card.uid for leader in leaderlist]
        playerlist = BackendApi.get_players(self, uidlist, [PlayerRegist, PlayerExp], using=settings.DB_READONLY, model_mgr=model_mgr)
        playerdict = dict([(player.id, player) for player in playerlist])
        persons = BackendApi.get_dmmplayers(self, playerlist, using=settings.DB_READONLY, do_execute=False)
        
        obj_playerlist = []
        self.html_param['playerlist'] = obj_playerlist
        
        def execute_end():
            for leader in leaderlist:
                player = playerdict.get(leader.card.uid)
                if not player:
                    continue
                person = persons[player.dmmid]
                obj_player = Objects.player(self, player, person, leader)
                obj_player['url_friendselect'] = self.makeAppLinkUrl(UrlMaker.raidfriendset(raidid, leader.card.uid), False)
                obj_playerlist.append(obj_player)
        return execute_end
    
    def putHelpFriend(self, raidboss):
        """助けを借りるフレンド.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        params = {}
        
        func_put_playerlist = None
        if self.request.get(Defines.URLQUERY_REM) == '1':
            # フレンドを外す.
            BackendApi.cancel_raidhelpcard(v_player.id, raidboss.id)
        else:
            helpleader = self.getSelectedFriendCard(raidboss.id)
            if helpleader:
                func_put_playerlist = self.putPlayerListByLeaderList(raidboss.id, [helpleader])
        
        friend_callopentime = BackendApi.get_raid_callfriend_opentime(v_player.id)
        if friend_callopentime:
            params['friend_call_opentime'] = Objects.timelimit(friend_callopentime)
        else:
            friend_num = BackendApi.get_friend_num(v_player.id, model_mgr, using=settings.DB_READONLY)
            if 0 < friend_num:
                url = UrlMaker.raidfriendselect(raidboss.id)
                params['url_friendselect'] = self.makeAppLinkUrl(url)
        
        # フレンドを外すリンク.
        url = self.request.url.replace(self.url_cgi, '')
        url = OSAUtil.addQuery(url, Defines.URLQUERY_REM, 1)
        params['url_helpfriend_cancel'] = self.makeAppLinkUrl(url)
        
        self.html_param.update(**params)
        
        return func_put_playerlist
    
    def writeHtmlSwitchEvent(self, name, eventid=None, eventmaster=None, basedir_normal='producehappening'):
        """イベントと通常のHTMLを切り替えて書き込む.
        """
        model_mgr = self.getModelMgr()
        if eventmaster is None:
            eventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=settings.DB_READONLY)
        if eventmaster and (eventid is None or eventmaster.id == eventid):
            if not self.html_param.has_key('url_produceevent_top'):
                self.html_param['url_produceevent_top'] = self.makeAppLinkUrl(UrlMaker.produceevent_top(eventmaster.id))
            if not self.html_param.has_key('produceevent'):
                config = BackendApi.get_current_produce_event_config(model_mgr, using=settings.DB_READONLY)
                self.html_param['produceevent'] = Objects.produceevent(self, eventmaster, config)
            self.writeAppHtml('produce_event/%s' % name)
        else:
            self.writeAppHtml('%s/%s' % (basedir_normal, name))
    
    def makeLinkRaidBattlePre(self, happeningraidset):
        """レイド挑戦ページのURL.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        happeningset = happeningraidset.happening
        raidboss = happeningraidset.raidboss
        
        if happeningraidset is None or happeningset is None or raidboss is None:
            return UrlMaker.happening()
            
        elif v_player.id != happeningset.happening.oid:
            return UrlMaker.raidhelpdetail(happeningset.id)
            
        else:
            model_mgr = self.getModelMgr()
            cur_eventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
            eventid = HappeningUtil.get_raideventid(happeningset.happening.event)
            if cur_eventmaster and cur_eventmaster.id == eventid:
                return UrlMaker.raidevent_battlepre()
            else:
                return UrlMaker.happening()
    
    def writeHappeningMissed(self, happeningid):
        """ハプニング失敗書き込み.
        """
        try:
            model_mgr = db_util.run_in_transaction(self.tr_write_missed, happeningid)
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
    
    def tr_write_missed(self, happeningid):
        """ハプニング失敗書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_happening_missed(model_mgr, happeningid)
        model_mgr.write_all()
        return model_mgr
    
    def getDeck(self):
        """デッキ取得.
        """
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        deck = BackendApi.get_raid_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
        return deck
    
    def getDeckCardList(self):
        """デッキのカード取得.
        """
        model_mgr = self.getModelMgr()
        deck = self.getDeck()
        cardidlist = deck.to_array()
        cardlist = BackendApi.get_cards(cardidlist, model_mgr, using=settings.DB_READONLY)
        return cardlist
    
    def putDeckParams(self, deckcardlist):
        obj_cardlist = []
        cost_total = 0
        power_total = 0
        for card in deckcardlist:
            obj_card = Objects.card(self, card)
            power_total += obj_card['power']
            cost_total += card.master.cost
            obj_cardlist.append(obj_card)
        self.html_param['cardlist'] = obj_cardlist
        self.html_param['cost_total'] = cost_total
        self.html_param['power_total'] = power_total
