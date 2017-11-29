# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerAp,\
    PlayerFriend
import math
from platinumegg.app.cabaret.models.battleevent import BattleEvent

class Handler(BattleEventBaseHandler):
    """バトルイベントバトル結果.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerFriend, PlayerExp]
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        
        args = self.getUrlArgs('/battleeventbattleresult/')
        eventid = args.getInt(0)
        
        eventmaster = None
        if eventid:
            eventmaster = BackendApi.get_battleevent_master(model_mgr, eventid, using=settings.DB_READONLY)
        
        if eventmaster is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'引数がおかしい')
            self.redirectToTop()
            return

        v_player = self.getViewerPlayer()
        uid = v_player.id

        # 結果データ.
        battleresult = BackendApi.get_battleevent_battleresult(model_mgr, eventid, uid, using=settings.DB_READONLY)
        if battleresult is None:
            # 結果が存在しない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'結果がない')
            url = UrlMaker.battleevent_top(eventid)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        self.setFromPage(Defines.FromPages.BATTLEEVENTPRE)

        data = battleresult.data
        
        # 対戦相手.
        oid = battleresult.oid
        arr = BackendApi.get_players(self, [oid], [PlayerExp], using=settings.DB_READONLY)
        o_player = arr[0] if arr else None
        if o_player is None:
            # 相手が存在しない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'相手が存在しない')
            url = UrlMaker.battleevent_top(eventid)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        obj_v_player, obj_o_player = self.getObjPlayerList([v_player, o_player])

        rival_key = BackendApi.get_rival_key(oid, eventid, args)
        self.html_param['resultdata'] = data

        obj_v_player['power_total'] = data['v_power']
        obj_o_player['power_total'] = data['o_power']
        obj_v_player['sp_powup'] = (data.get('v_sp_powup') or 0) * data['fever_powerup_rate'] / 100
        obj_o_player['sp_powup'] = data.get('o_sp_powup') or 0
        obj_v_player['spt_powup'] = (data.get('v_spt_powup') or 0) * data['fever_powerup_rate'] / 100
        obj_o_player['spt_powup'] = data.get('o_spt_powup') or 0
        
        obj_v_player['skilllist'] = battleresult.anim.make_html_skilllist(True)
        obj_o_player['skilllist'] = battleresult.anim.make_html_skilllist(False)
        
        self.html_param['player'] = obj_v_player
        self.html_param['o_player'] = obj_o_player
        
        if BackendApi.check_friend(uid, oid, arg_model_mgr=model_mgr, using=settings.DB_READONLY):
            pass
        elif BackendApi.check_friendrequest_receive(uid, oid, arg_model_mgr=model_mgr, using=settings.DB_READONLY):
            pass
        elif BackendApi.check_friendrequest_send(uid, oid, arg_model_mgr=model_mgr, using=settings.DB_READONLY):
            pass
        else:
            self.html_param['is_friendrequest_ok'] = True

        # 獲得したアイテム.
        prizes = data.get('prizes')
        if prizes:
            prizelist = BackendApi.get_prizelist(model_mgr, prizes, using=settings.DB_READONLY)
            self.html_param['prize'] = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)

        battle_ticket_num = self.get_base_battle_ticket_num(data)
        self.html_param['battle_ticket_num'] = battle_ticket_num
        self.html_param['battle_ticket_bonus'] = self.get_player_battle_ticket_bonus(model_mgr, uid, battle_ticket_num, eventmaster)

        # レベルアップしたカード.
        obj_lebelupcardlist = []
        levelupcardlist = BackendApi.get_cards(battleresult.levelupcard.keys(), model_mgr, using=settings.DB_READONLY)
        for levelupcard in levelupcardlist:
            obj_card = Objects.card(self, levelupcard)
            obj_card['level_add'] = battleresult.levelupcard.get(levelupcard.id, 0)
            obj_lebelupcardlist.append(obj_card)
        self.html_param['levelupcardlist'] = obj_lebelupcardlist
        
        # 回復アイテム.
        BackendApi.put_bprecover_uselead_info(self)
        
        # 獲得したポイント.
        scorerecord = BackendApi.get_battleevent_scorerecord(model_mgr, eventid, uid, using=settings.DB_READONLY)
        self.html_param['battleevent_score'] = self.makeScoreRecordObj(scorerecord, battleresult)
        
        # 特効キャスト分のポイント.
        effect_percent = data.get('effp', 0)
        if 0 < effect_percent:
            point_add = data['eventpoint']
            point_base = int(point_add * 100 / (effect_percent + 100))
            self.html_param['effect_point'] = point_add - point_base
        
        # 現在の贈り物情報を確認.
        presentdata = BackendApi.get_battleeventpresent_pointdata(model_mgr, uid, eventid, using=settings.DB_READONLY)
        if presentdata:
            cur_data = presentdata.getData()
            presentmaster = BackendApi.get_battleeventpresent_master(model_mgr, eventid, cur_data['number'], using=settings.DB_READONLY)
            self.html_param['is_present_open'] = presentmaster.point <= presentdata.point
        else:
            self.html_param['is_present_open'] = False
        
        # トピック.
        self.putEventTopic(eventid)
        
        # 続けて競う.
        target = 'revenge' if data.get('revenge') else 'lv'
        self.html_param['url_battlecontinue'] = self.makeAppLinkUrl(UrlMaker.battleevent_opplist(target, do_update=True))
        
        # グループ詳細.
        self.html_param['url_battleevent_group'] = self.makeAppLinkUrl(UrlMaker.battleevent_group())
        self.html_param["battleevent"] =  Objects.battleevent(self, eventmaster);
        if data['is_win']:
            piecedata = battleresult.data.get('piecedata')
            if piecedata:
                if piecedata.get('is_item'):
                    # キャスト名.
                    _, cardmaster = self.get_dirname_and_castname(eventid, piecedata['rarity'])
                    
                    # アイテム獲得.
                    prizelist = BackendApi.get_prizelist(model_mgr, piecedata.get('item_prizeids') or [], using=settings.DB_READONLY)
                    self.html_param['piece_dropiteminfo'] = dict(cardmaster=Objects.cardmaster(self, cardmaster)
                                                                 , prize=BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY))
                else:
                    self.put_drop_castname(model_mgr, eventid, piecedata['rarity'], piecedata['piece'])
            self.writeAppHtml('%s/battlewin' % ('gcevent' if eventmaster.is_goukon else 'btevent'))
        else:
            self.writeAppHtml('%s/battlelose' % ('gcevent' if eventmaster.is_goukon else 'btevent'))

    def get_dirname_and_castname(self, eventid, rarity):
        model_mgr = ModelRequestMgr()

        piecemaster_list = BackendApi.get_battleevent_piecemaster(model_mgr, eventid, using=settings.DB_READONLY)
        piecemaster = BackendApi.get_battleevent_piecemaster_instance(rarity, piecemaster_list)
        return (piecemaster, BackendApi.get_cardmasters([piecemaster.complete_prize], model_mgr)[piecemaster.complete_prize])

    def change_piecenumber_style(self, piecenumber):
        return '0%s' % str(piecenumber+1)

    def put_drop_castname(self, model_mgr, eventid, rarity, piecenumber):
        piecemaster_list = BackendApi.get_battleevent_piecemaster(model_mgr, eventid, using=settings.DB_READONLY)
        rarity_list = [piecemaster.number for piecemaster in piecemaster_list]
        if rarity in rarity_list:
            piece, castname = self.get_dirname_and_castname(eventid, rarity)
            data = { 'is_drop': True, 'castname': castname.name, 'dirname': piece.name, 'number':  self.change_piecenumber_style(piecenumber)}
            self.html_param['dropcast'] = data
        else:
            self.html_param['dropcast'] = { 'is_drop': False }

def main(request):
    return Handler.run(request)
