# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.app.cabaret.models.Player import PlayerRegist, PlayerHappening
from defines import Defines
from platinumegg.app.cabaret.models.Item import ItemMaster, Item
from platinumegg.app.cabaret.models.Friend import Friend
from platinumegg.app.cabaret.models.Invite import InviteData, Invite,\
    InviteMaster
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventScorePerRank
from platinumegg.app.cabaret.models.battleevent.BattleEventPresent import BattleEventPresentData
from platinumegg.app.cabaret.models.Gacha import RankingGachaScore
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventTanzakuCastData
from platinumegg.app.cabaret.util.cabaclub_store import CabaclubStoreSet

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Handler(AdminHandler):
    """ユーザー情報確認.
    """
    def process(self):
        args = self.getUrlArgs('/infomations/view_player/')
        uid = str(args.get(0))
        if uid.isdigit():
            self.__procView(int(uid))
        else:
            self.__procSearch()
    
    def __procSearch(self):
        """ユーザー検索.
        """
        serchtype = self.request.get('_serchtype')
        value = self.request.get('_value') or ''
        
        uidlist = None
        if serchtype == 'uid':
            uidlist = [int(str_uid) for str_uid in value.split(',') if str_uid.isdigit()]
        elif serchtype == 'dmmid':
            dmmidlist = [str_dmmid for str_dmmid in value.split(',') if str_dmmid]
            uidlist = BackendApi.dmmid_to_appuid(self, dmmidlist, using=backup_db).values()
        elif serchtype == 'invitedmmid':
            inviter_uid = BackendApi.dmmid_to_appuid(self, [value], using=backup_db).get(value)
            if inviter_uid:
                dmmidlist = [record.id for record in InviteData.fetchValues(['id'], filters={'fid':inviter_uid}, using=backup_db)]
                uidlist = BackendApi.dmmid_to_appuid(self, dmmidlist, using=backup_db).values()
            else:
                uidlist = []
        elif serchtype == 'inviteuid':
            inviter_uid = int(value) if value.isdigit() else None
            if inviter_uid:
                dmmidlist = [record.id for record in InviteData.fetchValues(['id'], filters={'fid':inviter_uid}, using=backup_db)]
                uidlist = BackendApi.dmmid_to_appuid(self, dmmidlist, using=backup_db).values()
            else:
                uidlist = []
        
        if uidlist is not None:
            playerlist = None
            if uidlist:
                playerlist = BackendApi.get_players(self, uidlist, clslist=[], using=backup_db)
            if playerlist:
                self.html_param['playerlist'] = [self.makeListPlayer(player) for player in playerlist]
            else:
                self.putAlertToHtmlParam(u'見つかりませんでした', AlertCode.WARNING)
        
        self.html_param['url_view_player'] = self.makeAppLinkUrlAdmin(UrlMaker.view_player())
        
        self.writeAppHtml('infomations/view_player/search')
    
    def __procView(self, uid):
        """詳細表示.
        """
        model_mgr = self.getModelMgr()
        now = OSAUtil.get_now()
        
        playerlist = BackendApi.get_players(self, [uid], using=backup_db)
        if not playerlist:
            self.putAlertToHtmlParam(u'見つかりませんでした', AlertCode.ERROR)
            self.__procSearch()
            return
        player = playerlist[0]
        person = BackendApi.get_dmmplayers(self, [player], using=backup_db, do_execute=True).get(player.dmmid)
        obj_player = Objects.player(self, player, person)
        obj_player['userType'] = person.userType or u'一般'
        self.html_param['player'] = obj_player
        
        # 招待してくれた人.
        invitedata = BackendApi.get_model(model_mgr, InviteData, player.dmmid, using=backup_db)
        if invitedata and invitedata.fid:
            playerlist = BackendApi.get_players(self, [invitedata.fid], [], using=backup_db, model_mgr=model_mgr)
            invite_from_player = playerlist[0] if playerlist else None
            if invite_from_player:
                invite_from_person = BackendApi.get_dmmplayers(self, [invite_from_player], using=backup_db, do_execute=True).get(invite_from_player.dmmid)
                self.html_param['invitedata'] = {
                    'url' : self.makeAppLinkUrlAdmin(UrlMaker.view_player(invite_from_player.id)),
                    'player' : Objects.player(self, invite_from_player, invite_from_person),
                    'ctime' : invitedata.ctime,
                    'state' : Defines.InviteState.NAMES[invitedata.state],
                }
        
        # 招待した人数.
        inviterecordlist = Invite.fetchValues(filters={'uid':player.id}, order_by='mid', using=backup_db)
        if inviterecordlist:
            midlist = [inviterecord.mid for inviterecord in inviterecordlist]
            invitemasterdict = BackendApi.get_model_dict(model_mgr, InviteMaster, midlist, get_instance=True, using=backup_db)
            
            obj_inviterecordlist = []
            for inviterecord in inviterecordlist:
                invitemaster = invitemasterdict.get(inviterecord.mid)
                obj_inviterecordlist.append({
                    'id' : invitemaster.id,
                    'name' : invitemaster.name,
                    'cnt' : inviterecord.cnt,
                })
            self.html_param['inviterecordlist'] = obj_inviterecordlist
        
        regist = False
        if player.getModel(PlayerRegist) is not None:
            regist = True
            
            # アイテム.
            itemidlist = Defines.ItemEffect.NAMES.keys()
            itemmasterdict = BackendApi.get_model_dict(model_mgr, ItemMaster, itemidlist, using=backup_db)
            itemnums = BackendApi.get_model_list(model_mgr, Item, [Item.makeID(uid, iid) for iid in Defines.ItemEffect.NAMES.keys()], using=backup_db)
            iteminfolist = []
            for item in itemnums:
                master = itemmasterdict.get(item.mid)
                if master:
                    iteminfolist.append({
                        'master' : master,
                        'nums' : item,
                    })
            self.html_param['itemlist'] = iteminfolist
            
            # 所持カード.
            deck = BackendApi.get_deck(uid, arg_model_mgr=model_mgr, using=backup_db)
            raiddeck = BackendApi.get_raid_deck(uid, arg_model_mgr=model_mgr, using=backup_db)
            
            cardlist = BackendApi.get_card_list(uid, arg_model_mgr=model_mgr, using=backup_db)
            obj_cardlist = []
            obj_deckcards = {}
            obj_raiddeckcards = {}
            cardcounts = {}
            for cardset in cardlist:
                obj_card = Objects.card(self, cardset, deck)
                obj_card['way'] = Defines.CardGetWayType.NAMES.get(cardset.card.way, u'不明')
                obj_card['raiddeckmember'] = raiddeck.is_member(cardset.id)
                if obj_card['deckmember']:
                    obj_deckcards[cardset.id] = obj_card
                elif obj_card['raiddeckmember']:
                    obj_card['raiddeckmember'] = True
                    obj_raiddeckcards[cardset.id] = obj_card
                else:
                    obj_cardlist.append(obj_card)
                mid = cardset.master.id
                data = cardcounts[mid] = cardcounts.get(mid) or {'name':cardset.master.name, 'cnt':0}
                data['cnt'] += 1
            self.html_param['deckcardlist'] = [obj_deckcards[cardid] for cardid in deck.to_array()]
            self.html_param['raiddeckcardlist'] = [obj_raiddeckcards[cardid] for cardid in raiddeck.to_array() if obj_raiddeckcards.get(cardid)]
            self.html_param['cardlist'] = obj_cardlist
            self.html_param['cardcounts'] = cardcounts
            
            # フレンド.
            table = {
                'friendlist' : BackendApi.get_friend_idlist,
                'friendrequestlist' : BackendApi.get_friendrequest_send_idlist,
                'friendreceivelist' : BackendApi.get_friendrequest_receive_idlist,
            }
            for k,func in table.items():
                uidlist = func(uid, arg_model_mgr=model_mgr, using=backup_db)
                friendlist = BackendApi.get_players(self, uidlist, [], using=backup_db)
                friendmodels = BackendApi.get_model_dict(model_mgr, Friend, [Friend.makeID(uid, fid) for fid in uidlist], using=backup_db)
                obj_friendlist = []
                for friend in friendlist:
                    obj_friend = self.makeListPlayer(friend)
                    friendmodel = friendmodels.get(Friend.makeID(uid, friend.id))
                    if friendmodel:
                        obj_friend['f_time'] = friendmodel.ctime.strftime("%Y/%m/%d %H:%M:%S")
                    obj_friendlist.append(obj_friend)
                self.html_param[k] = obj_friendlist
            
            # バトル情報.
            self.html_param['battleKOs'] = BackendApi.get_battleKOs(uid, arg_model_mgr=model_mgr, using=backup_db)
            battleplayer = BackendApi.get_battleplayer(model_mgr, uid, using=backup_db)
            if battleplayer:
                # 最大ランク.
                self.html_param['max_rank'] = BackendApi.get_battlerank_max(model_mgr, using=backup_db)
                
                rankmaster = BackendApi.get_battlerank(model_mgr, battleplayer.rank, using=backup_db)
                self.html_param['battleplayer'] = Objects.battleplayer(self, battleplayer, rankmaster)
            
            # ハプニング.
            if player.getModel(PlayerHappening):
                happeningraidset = BackendApi.get_happeningraidset(model_mgr, player.happening, using=backup_db)
                if happeningraidset:
                    model_happening = happeningraidset.happening.happening
                    prize = BackendApi.aggregate_happeningprize(model_happening, model_happening.is_canceled())
                    self.html_param['happening'] = Objects.happening(self, happeningraidset, prize)
            
            self.html_param['is_ban'] = not BackendApi.check_player_ban(model_mgr, uid, using=backup_db)
            
            # スカウトイベント.
            scevent = []
            config = BackendApi.get_current_scouteventconfig(model_mgr, using=backup_db)
            if config:
                eventmaster = BackendApi.get_scouteventmaster(model_mgr, config.mid, using=backup_db)
                if eventmaster:
                    playdata = BackendApi.get_event_playdata(model_mgr, eventmaster.id, uid, using=backup_db)
                    arr = BackendApi.get_event_stages(model_mgr, [playdata.stage], using=backup_db)
                    stage = arr[0] if arr else None
                    arr = BackendApi.get_event_stages(model_mgr, [playdata.cleared], using=backup_db)
                    cleared = arr[0] if arr else None
                    scorerecord = BackendApi.get_scoutevent_scorerecord(model_mgr, eventmaster.id, uid, using=backup_db)
                    produce_list = BackendApi.get_scoutevent_presentprizemaster_by_eventid(model_mgr, eventmaster.id, using=backup_db)
                    produce_data = BackendApi.get_scoutevent_presentnums_record(model_mgr, eventmaster.id, uid, using=backup_db)
                    if produce_data:
                        nums = produce_data.nums
                    else:
                        nums = {}
                    obj_produce_list = [(produce.name, nums.get(produce.number, 0)) for produce in produce_list]
                    
                    tanzaku_list = BackendApi.get_scoutevent_tanzakumaster_by_eventid(model_mgr, eventmaster.id, using=backup_db)
                    obj_tanzaku_list = None
                    current_cast_number = -1
                    if tanzaku_list:
                        tanzakudata = ScoutEventTanzakuCastData.getByKey(ScoutEventTanzakuCastData.makeID(uid, eventmaster.id), using=backup_db)
                        current_cast_number = tanzakudata.current_cast if tanzakudata else -1
                        obj_tanzaku_list = [dict(Objects.scoutevent_tanzaku(self, tanzakumaster, tanzakudata), current=current_cast_number==tanzakumaster.number) for tanzakumaster in tanzaku_list]
                    
                    event = {'name': eventmaster.name,
                             'stage': stage,
                             'cleared': cleared,
                             'scorerecord': scorerecord,
                             'produce_list' : obj_produce_list,
                             'tanzaku_list' : obj_tanzaku_list,
                            }
                    scevent.insert(0, event)
            self.html_param['scevent'] = scevent
            
            # バトルイベント.
            battleevent_config = BackendApi.get_current_battleeventconfig(model_mgr, using=backup_db)
            if battleevent_config.mid:
                eventmaster = BackendApi.get_battleevent_master(model_mgr, battleevent_config.mid, using=backup_db)
                if eventmaster:
                    eventid = eventmaster.id
                    obj_battleevent = {
                        'id' : eventmaster.id,
                        'name' : eventmaster.name,
                        'point' : 0,
                        'point_total' : 0,
                        'rank' : 0,
                        'rankname' : u'未参加',
                        'fame' : 0,
                        'fame_next' : 0,
                    }
                    scorerecord = BackendApi.get_battleevent_scorerecord(model_mgr, eventid, uid, using=backup_db)
                    if scorerecord:
                        obj_battleevent.update({
                            'point' : scorerecord.getPointToday(),
                            'point_total' : scorerecord.point_total,
                        })
                    rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventid, uid, using=backup_db)
                    if rankrecord:
                        rank = rankrecord.getRank(battleevent_config)
                        rankmaster = BackendApi.get_battleevent_rankmaster(model_mgr, eventid, rank, using=backup_db)
                        
                        obj_battleevent.update({
                            'rank' : rank,
                            'rankname' : rankmaster.name if rankmaster else u'不明',
                            'fame' : rankrecord.fame,
                            'fame_next' : rankrecord.fame_next,
                        })
                    # ランク別バトルポイント.
                    rankmasterlist = BackendApi.get_battleevent_rankmaster_by_eventid(model_mgr, eventid, using=backup_db, do_check_open=False)
                    idlist = [BattleEventScorePerRank.makeID(uid, BattleEventScorePerRank.makeMid(eventid, rankmaster.rank)) for rankmaster in rankmasterlist]
                    scoredata_dict = BackendApi.get_model_dict(model_mgr, BattleEventScorePerRank, idlist, using=backup_db, key=lambda x:x.rank)
                    obj_rankscorelist = []
                    rankmasterlist.sort(key=lambda x:x.rank, reverse=True)
                    for rankmaster in rankmasterlist:
                        obj_rankscorelist.append({
                            'rank' : rankmaster.rank,
                            'rankname' : rankmaster.name if rankmaster else u'不明',
                            'score' : scoredata_dict[rankmaster.rank].point if scoredata_dict.get(rankmaster.rank) else 0,
                        })
                    obj_battleevent['rankscorelist'] = obj_rankscorelist
                    
                    # 現在の贈り物.
                    presentdata = BackendApi.get_model(model_mgr, BattleEventPresentData, BattleEventPresentData.makeID(uid, eventid), using=backup_db)
                    obj_presentdata = None
                    if presentdata and presentdata.getData():
                        data = presentdata.getData()
                        presentmaster = BackendApi.get_battleeventpresent_master(model_mgr, eventid, data['number'], using=backup_db)
                        contentmaster = BackendApi.get_battleeventpresent_content_master(model_mgr, data['content'], using=backup_db)
                        obj_presentdata = {
                            'present' : presentmaster,
                            'content' : contentmaster,
                            'point' : presentdata.point,
                        }
                    obj_battleevent['presentdata'] = obj_presentdata
                    
                    self.html_param['battleevent'] = obj_battleevent
        
        obj_player['regist'] = regist
        
        # ガチャチケット.
        tickettypes = Defines.GachaConsumeType.GachaTicketType.NAMES.keys()
        ticket_num_models = BackendApi.get_additional_gachaticket_nums(model_mgr, uid, tickettypes, using=backup_db)
        ticket_list = []
        for tickettype in tickettypes:
            num_model = ticket_num_models.get(tickettype)
            ticket_list.append({
                'name' : Defines.GachaConsumeType.GachaTicketType.NAMES[tickettype],
                'num' : num_model.num if num_model else 0,
            })
        self.html_param['ticket_list'] = ticket_list
        
        # ランキングガチャ.
        rankinggachascore_list = RankingGachaScore.fetchByOwner(uid, using=backup_db)
        rankinggacha_master_dict = BackendApi.get_rankinggacha_master_dict(model_mgr, [rankinggachascore.mid for rankinggachascore in rankinggachascore_list], using=backup_db)
        obj_rankinggacha_list = []
        for rankinggachascore in rankinggachascore_list:
            rankinggacha_master = rankinggacha_master_dict.get(rankinggachascore.mid)
            obj_rankinggacha_list.append({
                'id' : rankinggachascore.mid,
                'name' : rankinggacha_master.name if rankinggacha_master else u'不明',
                'single' : rankinggachascore.single,
                'total' : rankinggachascore.total,
                'firstpoint' : rankinggachascore.firstpoint,
                'firsttime' : (rankinggachascore.firsttime or OSAUtil.get_datetime_min()).strftime("%Y-%m-%d %H:%M:%S"),
            })
        self.html_param['rankinggacha_list'] = obj_rankinggacha_list
        
        # 店舗.
        cabaclubstoremaster_all = BackendApi.get_cabaretclub_store_master_all(model_mgr, using=backup_db)
        midlist = [cabaclubstoremaster.id for cabaclubstoremaster in cabaclubstoremaster_all]
        store_set_dict = BackendApi.get_cabaretclub_storeset_dict(model_mgr, uid, midlist, using=backup_db)
        obj_store_list = []
        for cabaclubstoremaster in cabaclubstoremaster_all:
            store_set = store_set_dict.get(cabaclubstoremaster.id) or CabaclubStoreSet(cabaclubstoremaster, None)
            obj = Objects.cabaclubstore(self, store_set, now)
            obj['utime'] = store_set.playerdata.utime
            obj['rtime'] = store_set.playerdata.rtime
            obj['etime'] = store_set.playerdata.etime
            obj_store_list.append(obj)
        self.html_param['cabaclubstore_list'] = obj_store_list
        
        # 称号.
        title_set = BackendApi.get_current_title_set(model_mgr, uid, now, using=backup_db)
        if title_set:
            self.html_param['title'] = Objects.title(self, title_set.master, title_set.playerdata, now)
        
        self.writeAppHtml('infomations/view_player/detail')
    
    def makeListPlayer(self, player):
        return {
            'id' : player.id,
            'dmmid' : player.dmmid,
            'url' : self.makeAppLinkUrlAdmin(UrlMaker.view_player(player.id)),
            'url_promotion' : self.makeAppLinkUrlAdmin(UrlMaker.view_promotion(player.dmmid)),
            'url_panelmission' : self.makeAppLinkUrlAdmin(UrlMaker.view_panelmission(player.id)),
        }

def main(request):
    return Handler.run(request)
