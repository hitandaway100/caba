# -*- coding: utf-8 -*-
import random, time
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerRegist
from defines import Defines


class Handler(BattleEventBaseHandler):
    """バトルイベント対戦相手一覧.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerExp, PlayerRegist]
    
    def process(self):
        
        eventmaster = self.getCurrentBattleEvent()

        if not self.checkBattleEventUser():
            return
        
        args = self.getUrlArgs('/battleeventopplist/')
        target = args.get(0)
        
        table = {
            'revenge' : self.procRevenge,
        }
        func = table.get(target, None)
        if func is None:
            func = self.procLevel
            target = 'lv'

        func(eventmaster, args)
        if self.response.isEnd:
            return

        v_player = self.getViewerPlayer()
        
        # バトルイベント.
        self.html_param['battleevent'] = Objects.battleevent(self, eventmaster)
        
        # 選択中の項目.
        self.html_param['cur_topic'] = target

        # 連勝数の表示.
        model_mgr = self.getModelMgr()
        user_cvictory_count = BackendApi.get_battleevent_continue_victory(model_mgr, v_player.id, eventmaster.id, using=settings.DB_READONLY).count
        self.put_user_continue_victory_data(user_cvictory_count)
        
        # リンク.
        self.html_param['url_battleevent_opplist_lv'] = self.makeAppLinkUrl(UrlMaker.battleevent_opplist('lv'))
        self.html_param['url_battleevent_opplist_revenge'] = self.makeAppLinkUrl(UrlMaker.battleevent_opplist('revenge'))
        self.html_param['url_battleevent_opplist_update'] = self.makeAppLinkUrl(UrlMaker.battleevent_opplist(target, True))
        
        if eventmaster.is_goukon:
            self.writeAppHtml('gcevent/battletop')
        else:
            self.writeAppHtml('btevent/battletop')
    
    def procLevel(self, eventmaster, args):
        """近いレベル.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        eventid = eventmaster.id
        
        do_update = args.get(1) == '1'
        if do_update:
            # 更新.
            rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
            BackendApi.update_battleevent_opponent(model_mgr, rankrecord, v_player.level, using=settings.DB_READONLY)
            url = UrlMaker.battleevent_opplist('lv')
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        uidlist = BackendApi.get_battleevent_opponentidlist(model_mgr, eventid, uid, using=settings.DB_READONLY)
        func = self.putPlayerList(eventid, uidlist)
        
        self.execute_api()
        
        if func:
            func()
    
    def procRevenge(self, eventmaster, args):
        """仕返し.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        eventid = eventmaster.id
        
        revengelist = BackendApi.get_battleevent_revenge_list(model_mgr, uid, Defines.BATTLEEVENT_OPPONENT_NUM, using=settings.DB_READONLY)
        revengedict = dict([(revenge.oid, revenge) for revenge in revengelist if revenge.uid == uid])
        func = self.putPlayerList(eventid, revengedict.keys(), revengedict)
        
        self.execute_api()
        
        if func:
            func()
    
    def putPlayerList(self, eventid, uidlist, revengedict=None):
        """プレイヤー一覧作成.
        """
        v_player = self.getViewerPlayer()
        vid = v_player.id
        is_rival = None
        if uidlist and not revengedict:
            # ライバルの差し込み
            rival_id = self.random_rival_select(v_player.id)
            if rival_id in uidlist:
                uidlist.remove(rival_id)
                uidlist.insert(0, rival_id)
                is_rival = True
            elif rival_id:
                uidlist[0] = rival_id
                is_rival = True

        revengedict = revengedict or {}
        
        model_mgr = self.getModelMgr()
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        
        rankrecord_dict = BackendApi.get_battleevent_rankrecord_dict(model_mgr, eventid, uidlist, using=settings.DB_READONLY)
        playerlist = BackendApi.get_players(self, uidlist, [PlayerExp], using=settings.DB_READONLY)
        persons = BackendApi.get_dmmplayers(self, playerlist, using=settings.DB_READONLY, do_execute=False)
        
        decks = BackendApi.get_decks(uidlist, model_mgr, using=settings.DB_READONLY)
        leaders = {}
        deck_powers = {}
        for uid in uidlist:
            deck = decks[uid]
            cardidlist = deck.to_array()
            cardlist = BackendApi.get_cards(cardidlist, model_mgr, using=settings.DB_READONLY)
            power_total = 0
            for card in cardlist:
                if card.id == deck.leader:
                    leaders[uid] = card
                power_total += card.power
            deck_powers[uid] = power_total
        
        filtered_oidlist = BackendApi.filter_battleevent_opplist_by_battletime(model_mgr, vid, uidlist, using=settings.DB_READONLY)
        
        def apiend():
            obj_playerlist = []
            
            for i, player in enumerate(playerlist):
                obj_player = Objects.player(self, player, persons.get(player.dmmid), leaders.get(player.id))
                rankrecord = rankrecord_dict.get(player.id)
                rankname = None
                if rankrecord:
                    rankmaster = BackendApi.get_battleevent_rankmaster(model_mgr, eventid, rankrecord.getRank(config), using=settings.DB_READONLY)
                    if rankmaster:
                        rankname = rankmaster.name
                obj_player['event_rankname'] = rankname or u'----'

                # ライバルかどうかをフラグで持たせる。一応ライバルは [0] の位置に入ってる筈だけど、すり変わってるとバグがでそうなので。
                if is_rival and i == 0:
                    rival_key = BackendApi.make_is_rival_strings(player.id, eventid)
                    obj_player['is_rival'] = True
                else:
                    rival_key = None
                    obj_player['is_rival'] = False

                is_battle_ok = True
                revenge = revengedict.get(player.id)
                if revenge:
                    url = UrlMaker.battleevent_battlepre(player.id, revenge.id)
                else:
                    url = UrlMaker.battleevent_battlepre(player.id, rival_key=rival_key)
                    is_battle_ok = player.id in filtered_oidlist

                obj_player['url_eventbattle'] = self.makeAppLinkUrl(url)
                obj_player['is_battle_ok'] = is_battle_ok
                obj_player['power_total'] = deck_powers.get(player.id, 0)
                
                obj_playerlist.append(obj_player)

            # self.html_param['playerlist'] で勝負相手を決定している
            self.html_param['playerlist'] = obj_playerlist
        return apiend

    def put_user_continue_victory_data(self, cvictory_count):
        self.html_param['continue_victory_count'] = cvictory_count

    def random_rival_select(self, uid):
        """ライバルをランダムで選出 (IDを返す)"""
        rival_list = BackendApi.get_battleevent_rival(self.getModelMgr(), uid)
        rival_count = len(rival_list)-1
        random.seed(time.time())
        if rival_count < 0:
            return None
        rand = random.randint(0, rival_count)
        return rival_list[rand]

def main(request):
    return Handler.run(request)
