# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerFriend,\
    PlayerExp, PlayerRequest
from defines import Defines
import settings

class Handler(BattleEventBaseHandler):
    """バトルイベントにらみ合い.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerFriend, PlayerExp, PlayerRequest]
    
    def process(self):
        
        eventmaster = self.getCurrentBattleEvent()
        if not self.checkBattleEventUser():
            return
        
        args = self.getUrlArgs('/battleeventbattlepre/')
        oid = args.getInt(0)

        rival_index = BackendApi._check_is_rival_strings(oid, eventmaster.id, args)
        rival_key = BackendApi.get_rival_key(oid, eventmaster.id, args)

        if rival_key and rival_index == 2:
            revengeid = args.getInt(1)
        elif not rival_key:
            revengeid = args.getInt(1)
        else:
            revengeid = None

        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        obj_v_player = None
        obj_o_player = None
        if oid:
            o_player = BackendApi.get_player(self, oid, [PlayerFriend, PlayerExp], using=settings.DB_READONLY)
            if o_player:
                tmp = self.getObjPlayerList([o_player, v_player])
                
                for obj_player in tmp:
                    if obj_player['id'] == oid:
                        obj_o_player = obj_player
                    elif obj_player['id'] == uid:
                        obj_v_player = obj_player
                if tmp:
                    obj_o_player = tmp[0]
        is_battle_ok = True
        if not obj_o_player:
            url = UrlMaker.battleevent_opplist()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        elif not self.checkOpponentId(oid, revengeid, do_redirect=revengeid, args=args):
            # 対戦できない相手.
            if revengeid:
                return
            is_battle_ok = False
        obj_o_player['is_battle_ok'] = is_battle_ok
        
        self.setFromPage(Defines.FromPages.BATTLEEVENTPRE, [oid, revengeid, rival_key])
        
        # バトルイベント.
        self.html_param['battleevent'] = Objects.battleevent(self, eventmaster)
        
        # 各プレイヤーの情報.
        self.html_param['player'] = obj_v_player
        self.html_param['o_player'] = obj_o_player
        
        # ランク情報.
        rankrecord = self.getCurrentBattleRankRecord()
        obj_rankrecord = self.makeRankRecordObj(rankrecord)
        self.html_param['battleevent_rank'] = obj_rankrecord
        
        # 回復への導線.
        BackendApi.put_bprecover_uselead_info(self)
        
        # バトル開始URL.
        url = UrlMaker.battleevent_battledo(v_player.req_confirmkey, oid, revengeid, rival_key=rival_key)
        self.html_param['url_battle_do'] = self.makeAppLinkUrl(url)
        
        # 相手変更URL.
        target = 'revenge' if revengeid else 'lv'
        url = UrlMaker.battleevent_opplist(target)
        self.html_param['url_battle_oppselect'] = self.makeAppLinkUrl(url)
        
        # 書き込み.
        if eventmaster.is_goukon:
            self.writeAppHtml('gcevent/battleselect')
        else:
            self.writeAppHtml('btevent/battleselect')

def main(request):
    return Handler.run(request)
