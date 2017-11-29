# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerFriend,\
    PlayerExp, PlayerRequest, PlayerGold
import settings
import urllib
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.apprandom import AppRandom
from platinumegg.app.cabaret.util import db_util
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub

class Handler(BattleEventBaseHandler):
    """バトルイベントバトル書き込み.
    """

    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerFriend, PlayerExp, PlayerRequest]

    def process(self):
        
        eventmaster = self.getCurrentBattleEvent()
        if not self.checkBattleEventUser():
            return
        
        args = self.getUrlArgs('/battleeventbattledo/')
        confirmkey = urllib.unquote(args.get(0) or '')
        oid = args.getInt(1)

        rival_index = BackendApi._check_is_rival_strings(oid, eventmaster.id, args)
        rival_key = BackendApi.get_rival_key(oid, eventmaster.id, args)

        if rival_key and rival_index == 3:
            revengeid = args.getInt(2)
        elif not rival_key:
            revengeid = args.getInt(2)
        else:
            revengeid = None

        rival_key = BackendApi.get_rival_key(oid, eventmaster.id, args)

        now = OSAUtil.get_now()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        o_player = None
        if oid:
            o_player = BackendApi.get_player(self, oid, [PlayerFriend, PlayerExp], using=settings.DB_READONLY)
        
        if not o_player:
            url = UrlMaker.battleevent_opplist()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        elif not self.checkOpponentId(oid, revengeid, args=args):
            # 対戦できない相手.
            return
        
        model_mgr = self.getModelMgr()
        #piecedata = None
        if v_player.req_confirmkey == confirmkey:
            self.addloginfo(u'req_confirmkey==confirmkey')
            
            # 正しいリクエスト.
            
            # お互いのカード.
            v_deck = BackendApi.get_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
            o_deck = BackendApi.get_deck(o_player.id, model_mgr, using=settings.DB_READONLY)
            v_deck_cardlist = BackendApi.get_cards(v_deck.to_array(), model_mgr, using=settings.DB_READONLY)
            o_deck_cardlist = BackendApi.get_cards(o_deck.to_array(), model_mgr, using=settings.DB_READONLY)
            self.addloginfo(u'get deck')
            
            # 現在の称号.
            titlemaster = BackendApi.get_current_title_master(model_mgr, v_player.id, now, using=settings.DB_READONLY)
            battleevent_power_up = titlemaster.battleevent_power_up if titlemaster else 0
            
            # 計算.
            rand = AppRandom()
            data = BackendApi.battle(v_player, v_deck_cardlist, o_player, o_deck_cardlist, rand, eventmaster=eventmaster, title_effect=battleevent_power_up)
            self.addloginfo(u'battle')

            v_deck_cardidlist = v_deck.to_array()
            o_deck_cardidlist = o_deck.to_array()
            
            eventrankmaster = self.getCurrentBattleRankMaster()
            v_rankrecord = self.getCurrentBattleRankRecord()
            
            o_rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventmaster.id, oid, using=settings.DB_READONLY)
            o_eventrankmaster = None
            if o_rankrecord:
                config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
                o_eventrankmaster = BackendApi.get_battleevent_rankmaster(model_mgr, eventmaster.id, o_rankrecord.getRank(config), using=settings.DB_READONLY)
            self.addloginfo(u'get rankrecord')
            
            # グループ内順位.
            group = self.getCurrentBattleGroup()
            grouprankdata = BackendApi.make_battleevent_grouprankingdata(self, group, v_rankrecord.uid, now, using=settings.DB_READONLY, do_get_name=False)
            grouprank = grouprankdata['rank'] if grouprankdata else -1
            is_worst = grouprankdata['worst'] if grouprankdata else False
            self.addloginfo(u'make rankdata')

#             piecedata = self.present_piece(model_mgr, uid, eventmaster.id, data[0]['is_win'], rival_key)
            try:
                model_mgr = db_util.run_in_transaction(self.tr_write, eventmaster, eventrankmaster, o_eventrankmaster, uid, oid, v_deck_cardidlist, o_deck_cardidlist, data, grouprank, is_worst, revengeid, confirmkey, now, rival_key)
                self.addloginfo(u'write')
                model_mgr.write_end()
                self.addloginfo(u'write end')
            except CabaretError, err:
                if err.code == CabaretError.Code.ALREADY_RECEIVED:
                    pass
                elif settings_sub.IS_LOCAL:
                    raise err
                else:
                    url = self.makeAppLinkUrlRedirect(UrlMaker.battleevent_opplist())
                    self.appRedirect(url)
                    return
        elif v_player.req_alreadykey == confirmkey:
            # 処理済みのリクエスト.
            pass
        else:
            # おかしなリクエスト.
            model_mgr.delete_models_from_cache(PlayerRequest, [uid])
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.battleevent_top(eventmaster.id)))
            return
        
        url = UrlMaker.battleevent_battleanim(eventmaster.id)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def tr_write(self, eventmaster, eventrankmaster, o_eventrankmaster, uid, oid, v_deck_cardidlist, o_deck_cardidlist, data, grouprank, is_worst, revengeid, confirmkey, now, rival_key):
        model_mgr = ModelRequestMgr()
        players = BackendApi.get_players(self, [uid, oid], [PlayerGold, PlayerExp, PlayerFriend], model_mgr=model_mgr)
        v_player = None
        o_player = None
        for player in players:
            if player.id == uid:
                v_player = player
            else:
                o_player = player

        battle_data, _ = data
        battle_ticket_base = self.get_base_battle_ticket_num(battle_data)
        battle_ticket_num = battle_ticket_base + self.get_player_battle_ticket_bonus(model_mgr, uid, battle_ticket_base, eventmaster)
        BackendApi.tr_battleevent_battle(model_mgr, eventmaster, eventrankmaster, o_eventrankmaster, v_player, o_player,
                                         v_deck_cardidlist, o_deck_cardidlist, data, grouprank, is_worst, revengeid,
                                         confirmkey, now, rival_key, battle_ticket_num, self.is_pc)
        model_mgr.write_all()
        return model_mgr

    # BackendApi.tr_battleevent_set_result_for_pieceへ移動.
#     def is_present_piece(self, model_mgr, uid, is_win, rival_key):
#         """ピース (アイテム) ドロップするかどうかチェック。True の場合はそのままレアリティの抽選に進む。"""
#         eventid = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY).mid
#         # 勝敗のカウント処理を実行。負けたらリセットされる。
#         victory_count = BackendApi.do_battleevent_continue_victory_count(uid, eventid, is_win)
# 
#         # 負けたら配布処理は無し
#         if not is_win:
#             return False
# 
#         rank_master = BackendApi.get_rank_master_from_user_rank(model_mgr, uid, eventid)
#         total_point = self.calc_present_percent(victory_count, rank_master, rival_key)
#         return  BackendApi.do_battleevent_drop_lottery(total_point)
# 
#     def present_piece(self, model_mgr, uid, eventid, is_win, rival_key):
#         """ピースのプレゼント処理"""
#         if self.is_present_piece(model_mgr, uid, is_win, rival_key):
#             return BackendApi.tr_do_get_piece_or_items(uid, eventid)
#         return None
# 
#     def calc_present_percent(self, victory_count, rank_master, rival_key):
#         if rank_master.max_rise < victory_count:
#             victory_count = rank_master.max_rise
# 
#         rival_rise = 0
#         if rival_key:
#             rival_rise = rank_master.rival_rise
# 
#         total_point = rank_master.base_drop + rival_rise + (rank_master.rise * victory_count)
#         if 100 < total_point:
#             total_point = 100
#         return total_point

def main(request):
    return Handler.run(request)
