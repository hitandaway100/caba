# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import settings
from defines import Defines
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.Player import PlayerFriend, PlayerAp,\
    PlayerRequest
import urllib
from platinumegg.app.cabaret.models.Happening import Happening, RaidHelp
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventSpecialBonusScore, RaidEventHelpSpecialBonusScore
from platinumegg.app.cabaret.util.happening import HappeningRaidSet,\
    HappeningUtil, RaidBoss
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.card import CardSet
from platinumegg.app.cabaret.util.present import PrizeData


class Handler(HappeningHandler):
    """ハプニングボス戦(レイド).
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerFriend, PlayerRequest]
    
    def process(self):
        args = self.getUrlArgs('/raid/')
        procname = args.get(0)
        table = {
            'do' : self.procDo,
            'anim' : self.procAnim,
            'resultanim' : self.procResultAnim,
            'result' : self.procResult,
            'end' : self.procEnd,
        }
        func = table.get(procname)
        if func:
            func(args)
        else:
            url = UrlMaker.happening()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def procDo(self, args):
        """書き込み.
        """
        self.addloginfo('procDo')
        
        if settings_sub.IS_BENCH:
            v_player = self.getViewerPlayer()
            raidid = str(Happening.makeID(v_player.id, 101))
            confirmkey = ''
        else:
            raidid = str(args.get(1, ''))
            confirmkey = urllib.unquote(args.get(2, ''))
        is_strong = self.request.get(Defines.URLQUERY_STRONG) == '1'
        
        model_mgr = self.getModelMgr()
        self.addloginfo('get args')
        
        # レイド情報を取得.
        raidboss = None
        if raidid.isdigit():
            happeningraidset = BackendApi.get_happeningraidset(model_mgr, int(raidid))
            if happeningraidset:
                raidboss = happeningraidset.raidboss
        self.addloginfo('get raidboss')
        
        if raidboss is None:
            raise CabaretError(u'超太客にを接客できません', CabaretError.Code.ILLEGAL_ARGS)
        
        # プレイヤー.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        self.addloginfo('getViewerPlayer')
        
        # デッキ.
        deckcardlist = self.getDeckCardList()
        self.addloginfo('getDeckCardList')
        
        # 助っ人.
        friendcard = self.getSelectedFriendCard(raidboss.id, do_set_default=False)
        self.addloginfo('getSelectedFriendCard')
        
        # SHOWTIME.
        champagne = False
        eventvalue = happeningraidset.happening.happening.event
        
        raideventid = HappeningUtil.get_raideventid(eventvalue)
        score = 0

        if raideventid:
            raideventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
            raidmaster = raidboss.raideventraidmaster
            #raidhelp = RaidHelp.getValues(filters={'toid':uid, 'raidid':raidboss.id})
            if uid == raidboss.raid.oid:
                score = BackendApi.get_raidevent_specialbonusscore(model_mgr, uid, raidmaster.specialcard, raidmaster.specialcard_treasure, deckcardlist, using=settings.DB_DEFAULT)
            else:
                score = BackendApi.get_raidevent_specialbonusscore(model_mgr, uid, raidmaster.specialcard, raidmaster.specialcard_treasure, deckcardlist, raidid=raidboss.raid.id, using=settings.DB_DEFAULT)
            
            if raideventmaster and raideventmaster.id == raideventid:
                champagnedata = BackendApi.get_raidevent_champagne(model_mgr, uid, using=settings.DB_READONLY)
                if champagnedata and champagnedata.isChampagneCall(raideventid):
                    champagne = True
        
        scouteventid = HappeningUtil.get_scouteventid(eventvalue)
        if scouteventid:
            scouteventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY)
            if scouteventmaster and scouteventmaster.id == scouteventid:
                playdata = BackendApi.get_event_playdata(model_mgr, scouteventid, uid, using=settings.DB_READONLY)
                if playdata and playdata.is_lovetime():
                    champagne = True
        
        # 書き込み.
        try:
            model_mgr = db_util.run_in_transaction(self.tr_write, uid, raidboss.id, confirmkey, raidboss.master, deckcardlist, friendcard, is_strong, champagne, score)
            model_mgr.write_end()
        except CabaretError, err:
            if settings_sub.IS_LOCAL:
                raise
            elif err.code == CabaretError.Code.ALREADY_RECEIVED:
                # アニメーションにいけるはず.
                model_mgr = ModelRequestMgr()
                battleresult = BackendApi.get_raid_battleresult(model_mgr, v_player.id, using=settings.DB_DEFAULT)
                if battleresult.is_strong != is_strong:
                    # 戻す.
                    if raidboss.raid.oid == v_player.id:
                        # 発見者.
                        url = UrlMaker.happening()
                    else:
                        # 救援者.
                        url = UrlMaker.raidhelpdetail(raidboss.raid.id)
                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
                    return
            elif err.code == CabaretError.Code.OVER_LIMIT:
                # 撃破済みか終了済み.結果に飛ばすか.
                if raidboss.raid.oid == v_player.id:
                    # 発見者.
                    url = UrlMaker.raidend(raidboss.id)
                else:
                    # 救援者.終了しましたを出せるようになったので飛ばす.
                    url = UrlMaker.raidhelpdetail(raidboss.raid.id)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
            else:
                raise
        
        if settings_sub.IS_BENCH:
            self.response.end()
        url = UrlMaker.raidanim()
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def procAnim(self, args):
        """ボス戦アニメーション.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        raidbattle = BackendApi.get_raid_battleresult(model_mgr, v_player.id, using=settings.DB_READONLY)
        if raidbattle is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'想定外の遷移です')
            url = UrlMaker.happening()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # レイド情報を取得.
        raidboss = None
        happeningraidset = BackendApi.get_happeningraidset(model_mgr, raidbattle.raidid, using=settings.DB_READONLY)
        if happeningraidset:
            raidboss = happeningraidset.raidboss
        if raidboss is None:
            raise CabaretError(u'超太客が存在しません', CabaretError.Code.NOT_DATA)
        
        
        animdata = raidbattle.process
        is_win = animdata.winFlag
        
        # 演出用パラメータ.
        params = BackendApi.make_bossbattle_animation_params(self, animdata, HappeningUtil.makeThumbnailUrl(raidboss.master))
        
        # 結果へのURL.
        cur_eventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
        happeningset = BackendApi.get_happening(model_mgr, raidbattle.raidid, using=settings.DB_READONLY)
        eventid = HappeningUtil.get_raideventid(happeningset.happening.event)
        if cur_eventmaster and cur_eventmaster.id == eventid:
            url = UrlMaker.raidresultanim()
        elif is_win:
            url = UrlMaker.raidend(raidbattle.raidid)
        else:
            url = UrlMaker.raidresult()
        params['backUrl'] = self.makeAppLinkUrl(url)
        
        self.appRedirectToEffect('bossbattle2/effect.html', params)
    
    def procResultAnim(self, args):
        """結果演出(イベント限定).
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        # ハプニングとレイド情報を取得.
        raidid = str(args.get(1, ''))
        happeningraidset = None
        if raidid:
            if raidid.isdigit():
                happeningraidset = BackendApi.get_happeningraidset(model_mgr, int(raidid), using=settings.DB_READONLY)
            if happeningraidset is None or happeningraidset.raidboss is None:
                raise CabaretError(u'接客できない超太客です', CabaretError.Code.ILLEGAL_ARGS)
            elif happeningraidset.happening.happening.oid != v_player.id:
                raise CabaretError(u'接客できない超太客です', CabaretError.Code.ILLEGAL_ARGS)
            elif happeningraidset.happening.happening.is_active():
                raise CabaretError(u'この超太客はまだ終了していません', CabaretError.Code.ILLEGAL_ARGS)
            
            if happeningraidset.happening.happening.is_missed_and_not_end():
                self.writeHappeningMissed(happeningraidset.happening.id)
            url = UrlMaker.raidend(raidid)
        else:
            # 未指定なので直前のバトルから.
            raidbattle = BackendApi.get_raid_battleresult(model_mgr, v_player.id, using=settings.DB_READONLY)
            if raidbattle is None:
                if settings_sub.IS_LOCAL:
                    raise CabaretError(u'想定外の遷移です')
                url = UrlMaker.mypage()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
            raidid = raidbattle.raidid
            
            animdata = raidbattle.process
            # 演出用パラメータ.
            is_win = animdata.winFlag
            happeningraidset = BackendApi.get_happeningraidset(model_mgr, raidid, using=settings.DB_READONLY)
            if is_win:
                url = UrlMaker.raidend(raidid)
            else:
                url = UrlMaker.raidresult()
        # 演出はカット.
#        cur_eventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
#        if cur_eventmaster:
#            params = {
#                'backUrl' : self.makeAppLinkUrl(url),
#            }
#            self.appRedirectToEffect('levelup/effect.html', params)
#        else:
#            self.appRedirect(self.makeAppLinkUrlRedirect(url))
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def procResult(self, args):
        """ボス戦結果.
        """
        model_mgr = self.getModelMgr()
        
        v_player = self.getViewerPlayer()
        
        raidbattle = BackendApi.get_raid_battleresult(model_mgr, v_player.id, using=settings.DB_READONLY)
        if raidbattle is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'想定外の遷移です')
            url = UrlMaker.happening()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # レイド情報を取得.
        raidboss = BackendApi.get_raid(model_mgr, raidbattle.raidid, using=settings.DB_READONLY)
        if raidboss is None:
            raise CabaretError(u'超太客が存在しません', CabaretError.Code.NOT_DATA)
        
        animdata = raidbattle.process
        
        raidboss.raid.hp = animdata.bossHpPost
        if raidboss.raid.hp < 1:
            url = UrlMaker.raidend(raidbattle.raidid)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # 借りたカード.
        func_put_playerlist = None
        helpleadercard = raidbattle.getHelpCard()
        if helpleadercard:
            cardmaster = BackendApi.get_cardmasters([helpleadercard.mid], model_mgr, using=settings.DB_READONLY).get(helpleadercard.mid)
            helpleader = CardSet(helpleadercard, cardmaster)
            func_put_playerlist = self.putPlayerListByLeaderList(raidbattle.raidid, [helpleader])
        
        # 与えたダメージ.
        self.html_param['damage'] = animdata.bossDamage
        specialcard_powup = getattr(animdata, 'specialcard_powup', 0)
        str_specialcard_powup = None
        if 0 < specialcard_powup:
            str_specialcard_powup = '+%s' % specialcard_powup
        elif specialcard_powup < 0:
            str_specialcard_powup = '%s' % specialcard_powup
        self.html_param['specialcard_powup'] = str_specialcard_powup
        
        # 属性ボーナス.
        weak_powup = getattr(animdata, 'weak_powup', 0)
        str_weak_powup = None
        if 0 < weak_powup:
            str_weak_powup = '+%s' % weak_powup
        elif weak_powup < 0:
            str_weak_powup = '%s' % weak_powup
        self.html_param['weak_powup'] = str_weak_powup
        
        # 発動したスキル.
        self.html_param['skilllist'] = animdata.make_html_skilllist()
        
        # プレイヤー情報.
        self.html_param['player'] = Objects.player(self, v_player)
        
        # 救援のUrl(フレンド).
        url = UrlMaker.raidhelpsend()
        self.html_param['url_helpsend'] = self.makeAppLinkUrl(url)
        self.html_param['url_helpsend_other'] = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_FLAG, "1"))
        
        # ハプニング情報.
        happeningset = BackendApi.get_happening(model_mgr, raidboss.id, using=settings.DB_READONLY)
        func_happeninginfo_callback = self.putHappeningInfo(happeningset, raidboss, do_execute=False)
        
        func_put_attacklog = None
        
        is_event = False
        raideventmaster = None
        eventid = HappeningUtil.get_raideventid(happeningset.happening.event)
        if eventid:
            raideventmaster = BackendApi.get_raideventmaster(model_mgr, eventid, using=settings.DB_READONLY)
        
        if raideventmaster:
            # イベント情報.
            config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
            self.html_param['raidevent'] = Objects.raidevent(self, raideventmaster, config)
            
            # ダメージ履歴.
            func_put_attacklog = self.putRaidAttackLog(raidboss)
            
            # イベント用の設定.
            eventraidmaster = BackendApi.get_raidevent_raidmaster(model_mgr, raideventmaster.id, raidboss.raid.mid, using=settings.DB_READONLY)
            BackendApi.put_raidevent_specialcard_info(self, v_player.id, eventraidmaster, using=settings.DB_READONLY)
            
            url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.TICKET)
            self.html_param['url_gacha_event'] = self.makeAppLinkUrl(url)
            
            self.html_param['url_raidevent_top'] = self.makeAppLinkUrl(UrlMaker.raidevent_top(raideventmaster.id))
            
            is_event = True
        
        # 戻るUrl.
        if raidboss.raid.oid == v_player.id:
            # 発見者.
            if is_event:
                url = UrlMaker.raidevent_battlepre()
            else:
                url = UrlMaker.happening()
        else:
            # 救援者.
            url = UrlMaker.raidhelpdetail(raidboss.raid.id)
        self.html_param['url_return'] = self.makeAppLinkUrl(url, add_frompage=False)
        
        # デッキ情報.
        deckcardlist = self.getDeckCardList()
        self.__putDeckParams(deckcardlist)
        
        self.execute_api()
        func_happeninginfo_callback()
        
        if func_put_playerlist:
            func_put_playerlist()
        
        if func_put_attacklog:
            func_put_attacklog()
        
        eventid = HappeningUtil.get_raideventid(happeningset.happening.event)
        self.writeHtmlSwitchEvent('bosslose', eventid, eventmaster=raideventmaster)
    
    def procEnd(self, args):
        """レイド終了.
        """
        model_mgr = self.getModelMgr()
        
        # ハプニングとレイド情報を取得.
        raidid = str(args.get(1, ''))
        
        happeningraidset = None
        if raidid.isdigit():
            raidid = int(raidid)
            happeningraidset = BackendApi.get_happeningraidset(model_mgr, raidid, using=settings.DB_READONLY)
        if happeningraidset is None or happeningraidset.raidboss is None:
            raise CabaretError(u'超太客が存在しません', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        
        happeningset = happeningraidset.happening
        raidboss = happeningraidset.raidboss
        if 0 < raidboss.raid.hp:
            url = UrlMaker.happeningend(happeningset.id)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        elif happeningset.happening.is_cleared() and happeningset.happening.oid == v_player.id:
            try:
                model_mgr = db_util.run_in_transaction(self.tr_write_happeningend, happeningset.id, v_player.id)
                model_mgr.write_end()
            except CabaretError, err:
                if settings_sub.IS_LOCAL:
                    raise
                elif err.code == CabaretError.Code.ALREADY_RECEIVED:
                    pass
                else:
                    raise
        elif not v_player.id in raidboss.getDamageRecordUserIdList():
            raise CabaretError(u'接客できない超太客です', CabaretError.Code.ILLEGAL_ARGS)
        else:
            damagerecord = raidboss.getDamageRecord(v_player.id)
            if damagerecord.damage_cnt == 0:
                # 依頼をもらったけど参加する前に終わった.
                url = UrlMaker.raidhelpdetail(raidboss.id)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        
        # 与えたダメージ.
        damage = None
        skilllist = None
        func_put_playerlist = None
        raidbattle = BackendApi.get_raid_battleresult(model_mgr, v_player.id, using=settings.DB_READONLY)
        specialcard_powup = None
        
        if raidbattle is not None and raidbattle.raidid == raidid:
            animdata = raidbattle.process
            if animdata and animdata.winFlag:
                damage = animdata.bossDamage
                skilllist = animdata.make_html_skilllist()
                # 借りたカード.
                helpleadercard = raidbattle.getHelpCard()
                if helpleadercard:
                    cardmaster = BackendApi.get_cardmasters([helpleadercard.mid], model_mgr, using=settings.DB_READONLY).get(helpleadercard.mid)
                    helpleader = CardSet(helpleadercard, cardmaster)
                    func_put_playerlist = self.putPlayerListByLeaderList(raidbattle.raidid, [helpleader])
                # デッキ情報.
                deckcardlist = self.getDeckCardList()
                self.__putDeckParams(deckcardlist)
                
                specialcard_powup = getattr(animdata, 'specialcard_powup', None)
        
        self.html_param['skilllist'] = skilllist
        self.html_param['damage'] = damage
        str_specialcard_powup = None
        if specialcard_powup is not None:
            if 0 < specialcard_powup:
                str_specialcard_powup = '+%s' % specialcard_powup
            elif specialcard_powup < 0:
                str_specialcard_powup = '%s' % specialcard_powup
        self.html_param['specialcard_powup'] = str_specialcard_powup
        
        # ハプニング情報.
        callback = self.putHappeningInfo(happeningset, raidboss, do_execute=False)
        
        # 報酬ページ.
        url = UrlMaker.happeningend(happeningset.id)
        self.html_param['url_happeningend'] = self.makeAppLinkUrl(url)
        
        func_raidattacklog_callback = None
        
        url_scout_top = None
        raideventid = 0
        if raidboss.raideventraidmaster:
            raideventid = raidboss.raideventraidmaster.eventid
            raideventmaster = BackendApi.get_raideventmaster(model_mgr, raideventid, using=settings.DB_READONLY)
            
            # レイドイベント.
            config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
            self.html_param['raidevent'] = Objects.raidevent(self, raideventmaster, config)

            specialbonusscore = 0
            if  v_player.id == happeningset.happening.oid:
                specialbonusscore_model = model_mgr.get_model(RaidEventSpecialBonusScore, v_player.id)
                if isinstance(specialbonusscore_model, RaidEventSpecialBonusScore):
                    specialbonusscore = specialbonusscore_model.last_happening_score
            else:
                # 救援かつ撃破者に特効ボーナスポイント付与する.
                specialbonusscore_model =  BackendApi.get_raidevent_helpspecialbonusscore(raidboss.raid.id, v_player.id, using=settings.DB_DEFAULT)
                if isinstance(specialbonusscore_model, RaidEventHelpSpecialBonusScore):
                    specialbonusscore = specialbonusscore_model.bonusscore
            self.html_param['destroypoint_info'] = BackendApi.make_raidevent_destroypoint_info(model_mgr, v_player.id, raideventmaster, happeningraidset, specialbonusscore, using=settings.DB_READONLY)
            
            # MVP.
            mvp_uidlist = raidboss.getMVPList()
            self.html_param['mvp_uidlist'] = mvp_uidlist
            
            # それ以外の協力したユーザー.
            func_raidattacklog_callback = self.putRaidAttackLog(raidboss)

            # 秘宝所持数.
            scorerecord = BackendApi.get_raidevent_scorerecord(model_mgr, raideventid, v_player.id, using=settings.DB_READONLY)
            rank = BackendApi.get_raidevent_rank(raideventid, v_player.id)
            self.html_param['raideventscore'] = Objects.raidevent_score(raideventmaster, scorerecord, rank)
            # 報酬受取り判定.
            flag = False
            flagrecord = BackendApi.get_raidevent_flagrecord(model_mgr, raideventid, v_player.id, using=settings.DB_READONLY)
            if scorerecord:
                if scorerecord.destroy and BackendApi.choice_raidevent_notfixed_destroy_prizeids(raideventmaster, scorerecord.destroy, flagrecord, False):
                    flag = True
                elif scorerecord.destroy_big and BackendApi.choice_raidevent_notfixed_destroy_prizeids(raideventmaster, scorerecord.destroy_big, flagrecord, True):
                    flag = True
            if flag:
                self.html_param['url_raidevent_prizereceive'] = self.makeAppLinkUrl(UrlMaker.raidevent_prizereceive_do(raideventid, v_player.req_confirmkey))
            
            # 次の報酬.
            next_prizedata = BackendApi.get_raidevent_next_destroyprizedata(model_mgr, raideventmaster, scorerecord, raidboss.is_big(), using=settings.DB_READONLY)
            if next_prizedata:
                self.html_param['next_prizeinfo'] = {
                    'info' : BackendApi.make_prizeinfo(self, next_prizedata['prizelist'], using=settings.DB_READONLY),
                    'rest' : next_prizedata['rest'],
                }
            
            # シャンパン.
            damagerecord = raidboss.getDamageRecord(v_player.id)
            if 0 < damagerecord.champagne_num_add:
                self.html_param['champagne_num_pre'] = damagerecord.champagne_num_pre
                self.html_param['champagne_num_post'] = damagerecord.champagne_num_post
                self.html_param['champagne_num_add'] = damagerecord.champagne_num_add
            
            # 素材.
            if 0 < damagerecord.material_num:
                materials = raideventmaster.getMaterialDict()
                material_id = materials.get(raidboss.raideventraidmaster.material)
                if material_id:
                    materialmaster = BackendApi.get_raidevent_materialmaster(model_mgr, material_id, using=settings.DB_READONLY)
                    materialnumdata = BackendApi.get_raidevent_materialdata(model_mgr, v_player.id, using=settings.DB_READONLY)
                    obj = Objects.raidevent_material(self, materialmaster, materialnumdata.getMaterialNum(raideventid, raidboss.raideventraidmaster.material))
                    obj['num_add'] = damagerecord.material_num
                    self.html_param['material'] = obj
            
            self.html_param['url_raidevent_top'] = self.makeAppLinkUrl(UrlMaker.raidevent_top(raideventid))
            
            if raideventmaster.flag_dedicated_stage:
                url_scout_top = UrlMaker.raidevent_scouttop()
        elif raidboss.scouteventraidmaster:
            scouteventid = raidboss.scouteventraidmaster.eventid
            tanzaku_number = raidboss.get_tanzaku_number(v_player.id)
            tanzakumaster = BackendApi.get_scoutevent_tanzakumaster(model_mgr, scouteventid, tanzaku_number, using=settings.DB_READONLY) if tanzaku_number is not None else None
            
            if tanzakumaster is not None:
                # 短冊.
                self.html_param['scoutevent_tanzaku'] = Objects.scoutevent_tanzaku(self, tanzakumaster)
                self.html_param['tanzaku_num_pre'] = damagerecord.tanzaku_num_pre
                self.html_param['tanzaku_num_post'] = damagerecord.tanzaku_num_post
                self.html_param['tanzaku_num_add'] = damagerecord.tanzaku_num
        
        self.execute_api()
        callback()
        
        if func_put_playerlist:
            func_put_playerlist()
        
        if func_raidattacklog_callback:
            func_raidattacklog_callback()
        
        backinfo = None
        if happeningset.happening.oid == v_player.id:
            flag_model = BackendApi.get_playerlasthappeningtype(v_player.id, get_instance=True)
            url = None
            if flag_model.is_scout:
                url = self.makeAppLinkUrl(UrlMaker.scout())
            elif flag_model.is_scoutevent:
                url = self.makeAppLinkUrl(UrlMaker.scoutevent())
            if url:
                htype = flag_model.htype
                backinfo = {
                    'url' : url,
                    'type' : htype,
                }
        self.html_param['happening_backinfo'] = backinfo
        
        self.html_param['url_scout_top'] = self.makeAppLinkUrl(url_scout_top or UrlMaker.scout())
        
        self.writeHtmlSwitchEvent('bosswin', raideventid)
    
    def tr_write(self, uid, raidid, key, raidmaster, deckcardlist, friendcard, is_strong, champagne, score):
        """書き込み.
        """
        self.addloginfo('tr_write')
        model_mgr = ModelRequestMgr(loginfo=self.addloginfo)
        player = BackendApi.get_players(self, [uid], [PlayerFriend], model_mgr=model_mgr)[0]
        BackendApi.tr_raidbattle(model_mgr, raidid, key, player, raidmaster, deckcardlist, friendcard, is_strong, self.is_pc, champagne=champagne, addloginfo=self.addloginfo, score=score)
        model_mgr.write_all()
        return model_mgr
    
    def tr_write_happeningend(self, happeningid, viewer_uid):
        """ハプニング終了書き込み.
        """
        self.addloginfo('tr_write_happeningend')
        model_mgr = ModelRequestMgr(loginfo=self.addloginfo)
        happening = model_mgr.get_model_forupdate(Happening, happeningid)
        raidboss = BackendApi.get_raid(model_mgr, happening.id, happening_eventvalue=happening.event)
        BackendApi.tr_happening_end(model_mgr, happening, raidboss, viewer_uid)
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
    
    def getPowerTotal(self):
        """デッキの総接客力.
        """
        cardlist = self.getDeckCardList()
        power_total = 0
        for card in cardlist:
            power_total += card.power
        return power_total
    
    def putHappeningInfo(self, happeningset, raidboss, do_execute=True):
        """ハプニング情報作成.
        """
        model_mgr = self.getModelMgr()
        
        v_player = self.getViewerPlayer()
        o_player = None
        is_owner = v_player.id == happeningset.happening.oid
        
        prizelist = []
        if 0 < happeningset.happening.event:
            if not raidboss.raideventraidmaster:
                eventraidmaster = BackendApi.get_eventraidmaster_by_modeleventvalue(model_mgr, happeningset.happening.event, raidboss.raid.mid, using=settings.DB_READONLY)
                raidboss.setEventRaidMaster(eventraidmaster)
            
            if raidboss.raid.hp < 1 and RaidBoss.RAIDEVENT_PRIZE_UPDATETIME <= happeningset.happening.ctime:
                damagerecord = raidboss.getDamageRecord(v_player.id)
                # 報酬.
                if is_owner:
                    # 発見者.
                    cabaretking = raidboss.get_cabaretking()
                    if 0 < cabaretking:
                        prizelist.append(PrizeData.create(cabaretking=cabaretking))
                    prizelist.extend(BackendApi.get_prizelist(model_mgr, raidboss.master.prizes, using=settings.DB_READONLY))
                    prizelist.extend(BackendApi.aggregate_happeningprize(happeningset.happening))

                    # ドロップアイテム報酬
                    if happeningset.happening.items:
                        dropitems = [happening.id for happening in happeningset.happening.items['dropitems']]
                        prizelist.extend(BackendApi.get_prizelist(model_mgr, dropitems, using=settings.DB_READONLY))
                elif 0 < damagerecord.damage_cnt:
                    # 救援者.
                    demiworld = raidboss.get_demiworld()
                    if 0 < demiworld:
                        prizelist.append(PrizeData.create(demiworld=demiworld))
                    prizelist.extend(BackendApi.get_prizelist(model_mgr, raidboss.master.helpprizes, using=settings.DB_READONLY))
        
        # 獲得した報酬.
        if is_owner:
            prizelist.extend(self.getPooledPrizeList(happeningset.happening.is_canceled()))
            o_player = v_player
        else:
            o_player = BackendApi.get_players(self, [happeningset.happening.oid], [], using=settings.DB_READONLY)[0]
        
        prizeinfo = None
        if prizelist:
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
        
        persons = BackendApi.get_dmmplayers(self, [o_player], using=settings.DB_READONLY, do_execute=do_execute)
        
        def cb():
            # ハプニング情報.
            obj_happening = Objects.happening(self, HappeningRaidSet(happeningset, raidboss), prizeinfo, persons.get(o_player.dmmid))
            self.html_param['happening'] = obj_happening
            return obj_happening
        if do_execute:
            self.execute_api()
            return cb()
        else:
            return cb
    
    def __putDeckParams(self, deckcardlist):
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
    

def main(request):
    return Handler.run(request)
