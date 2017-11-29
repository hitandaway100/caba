# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.views.application.produce_happening.base import HappeningHandler
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import settings
from defines import Defines
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.Player import PlayerFriend, PlayerAp, \
    PlayerRequest
import urllib
from platinumegg.app.cabaret.models.Happening import Happening
from platinumegg.app.cabaret.util.happening import HappeningRaidSet, \
    HappeningUtil, RaidBoss
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.card import CardSet
from platinumegg.app.cabaret.util.present import PrizeData
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import ProduceEventHappeningResult, ProduceCastMaster,\
    PlayerEducation
from platinumegg.app.cabaret.models.View import CardMasterView
from platinumegg.app.cabaret.util.card import CardUtil


class Handler(HappeningHandler):
    """ハプニングボス戦(レイド).
    """

    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerFriend, PlayerRequest]

    def process(self):
        args = self.getUrlArgs('/produceraid/')
        procname = args.get(0)
        table = {
            'do': self.procDo,
            'anim': self.procAnim,
            'rarityanim': self.procRarityAnim,
            'lastcastgetanim': self.procLastCardGetAnim,
            'resultanim': self.procResultAnim,
            'result': self.procResult,
            'end': self.procEnd,
        }
        func = table.get(procname)
        if func:
            func(args)
        else:
            url = UrlMaker.producehappening()
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
            happeningraidset = BackendApi.get_producehappeningraidset(model_mgr, int(raidid))
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
        eventvalue = happeningraidset.happening.happening.event

        produceeventid = HappeningUtil.get_produceeventid(eventvalue)
        score = 0

        champagne = None
        if produceeventid:
            produceeventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=settings.DB_READONLY)
            raidmaster = raidboss.produceeventraidmaster
            champagne = None

        # 書き込み.
        try:
            model_mgr = db_util.run_in_transaction(self.tr_write, uid, raidboss.id, confirmkey, raidboss.master,
                                                   deckcardlist, friendcard, is_strong, champagne, score)
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
                        url = UrlMaker.producehappening()
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
        url = UrlMaker.produceraidanim()
        self.appRedirect(self.makeAppLinkUrlRedirect(url))

    def procAnim(self, args):
        """ボス戦アニメーション.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        cur_eventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=settings.DB_READONLY)

        if not cur_eventmaster:
            raise CabaretError(u'イベントは終了しました', CabaretError.Code.EVENT_CLOSED)

        raidbattle = BackendApi.get_raid_battleresult(model_mgr, v_player.id, using=settings.DB_READONLY)
        if raidbattle is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'想定外の遷移です')
            url = UrlMaker.producehappening()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return

        # レイド情報を取得.
        raidboss = None
        happeningraidset = BackendApi.get_producehappeningraidset(model_mgr, raidbattle.raidid, using=settings.DB_READONLY)
        if happeningraidset:
            raidboss = happeningraidset.raidboss
        if raidboss is None:
            raise CabaretError(u'超太客が存在しません', CabaretError.Code.NOT_DATA)

        animdata = raidbattle.process
        is_win = animdata.winFlag

        player_result = model_mgr.get_model(ProduceEventHappeningResult, ProduceEventHappeningResult.makeID(uid, cur_eventmaster.id), using=settings.DB_DEFAULT)
        player_education = model_mgr.get_model(PlayerEducation, PlayerEducation.makeID(uid, cur_eventmaster.id), using=settings.DB_DEFAULT)
        cur_event_castmasters = cur_eventmaster.get_produce_castmasters(order_by='order', using=settings.DB_READONLY)
        produce_castmaster = player_education.get_produce_castmaster_for_array(cur_event_castmasters)
        max_order = ProduceCastMaster.get_maxorder(cur_event_castmasters)

        # 演出用パラメータ.
        params = {}

        rarityup = False
        new_order = 0
        old_order = 0
        if player_result and player_education and produce_castmaster:
            new_order = player_education.cast_order
            order_rate = player_result.order

            if order_rate != 0:
                old_order = new_order - order_rate
                rarityup = bool(old_order)

            # get the correct remaining cast masters that the player hasn't gotten yet
            # NOTE: at this point new_order == player_education.cast_order == produce_castmaster.order
            # (they have the same value)
            if rarityup:
                remaining_castmaster = [castmaster for castmaster in cur_event_castmasters if castmaster.order >= new_order]
            else:
                remaining_castmaster = [castmaster for castmaster in cur_event_castmasters if castmaster.order > new_order]

            params['bigwinFlag'] = player_result.is_perfect_win
            params['heartBefore'] = player_result.before_heart
            params['heartGotten'] = player_result.education_point
            params['after_level'] = player_result.after_level
            params['level_min'] = player_result.before_level
            params['level_max'] = produce_castmaster.max_education_level
            params['education_levelup'] = (player_result.after_level - player_result.before_level) > 0
            params['levels'] = ":".join([str(castmaster.max_education_level) for castmaster in remaining_castmaster])

        # ボスとボスキャストの画像パラメータ
        castorder = old_order if rarityup else player_education.cast_order
        eventboss_thumbnail = HappeningUtil.makeProduceEventBossThumbnailUrl(raidboss.master)
        eventcast_thumbnail = HappeningUtil.makeProduceEventCastThumbnailUrl(cur_eventmaster, castorder)
        boss_parameters = BackendApi.make_bossbattle_animation_params(self, animdata, eventboss_thumbnail, eventcast_thumbnail)
        params.update(boss_parameters)

        # 結果へのURL.
        happeningset = BackendApi.get_producehappening(model_mgr, raidbattle.raidid, using=settings.DB_READONLY)
        eventid = HappeningUtil.get_produceeventid(happeningset.happening.event)
        max_education_level = ProduceCastMaster.get_max_maxeducationlevel(cur_event_castmasters)
        # 最後のレア度のキャスト獲得??
        last_card = player_education.is_education_limit(max_education_level, max_order) and player_result.education_point > 0
        if rarityup:
            url = UrlMaker.produceraidrarityanim(new_order, old_order)
            old_produce_castmaster = ProduceCastMaster.getValues(filters={'order': old_order})
            params['level_max'] = old_produce_castmaster.max_education_level
        elif last_card:
            url = UrlMaker.produceraidlastcastgetanim(produce_castmaster.produce_cast)
        elif cur_eventmaster and cur_eventmaster.id == eventid:
            url = UrlMaker.produceraidresultanim()
        elif is_win:
            url = UrlMaker.produceraidend(raidbattle.raidid)
        else:
            url = UrlMaker.produceraidresult()
        params['backUrl'] = self.makeAppLinkUrl(url)

        self.appRedirectToEffect('produce_event/produce_bossbattle/effect.html', params)

    def procRarityAnim(self, args):
        """レア度上昇演出
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()

        # カードのorder情報を取得する
        new_order = args.getInt(1)
        old_order = args.getInt(2)

        cur_eventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=settings.DB_READONLY)

        if not cur_eventmaster:
            raise CabaretError(u'イベントは終了しました', CabaretError.Code.EVENT_CLOSED)

        raidbattle = BackendApi.get_raid_battleresult(model_mgr, v_player.id, using=settings.DB_READONLY)
        if raidbattle is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'想定外の遷移です')
            url = UrlMaker.producehappening()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return

        # レイド情報を取得.
        raidboss = None
        happeningraidset = BackendApi.get_producehappeningraidset(model_mgr, raidbattle.raidid, using=settings.DB_READONLY)
        if happeningraidset:
            raidboss = happeningraidset.raidboss
        if raidboss is None:
            raise CabaretError(u'超太客が存在しません', CabaretError.Code.NOT_DATA)

        animdata = raidbattle.process
        is_win = animdata.winFlag

        # 結果へのURL.
        happeningset = BackendApi.get_producehappening(model_mgr, raidbattle.raidid, using=settings.DB_READONLY)
        eventid = HappeningUtil.get_produceeventid(happeningset.happening.event)
        if cur_eventmaster and cur_eventmaster.id == eventid:
            url = UrlMaker.produceraidresultanim()
        elif is_win:
            url = UrlMaker.produceraidend(raidbattle.raidid)
        else:
            url = UrlMaker.produceraidresult()

        params = {}
        castmasters = cur_eventmaster.get_produce_castmasters(filters={'order__in': [old_order, new_order]},
                                                              order_by='order', using=settings.DB_READONLY)

        old_rarity_card = BackendApi.get_model(model_mgr, CardMasterView, castmasters[0].produce_cast)
        new_rarity_card = BackendApi.get_model(model_mgr, CardMasterView, castmasters[1].produce_cast)

        params['backUrl'] = self.makeAppLinkUrl(url)
        params['old_rarity'] = self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(old_rarity_card))
        params['new_rarity'] = self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(new_rarity_card))

        self.appRedirectToEffect('produce_event/produce_rareup/effect.html', params)

    def procLastCardGetAnim(self, args):
        """最後のレア度のキャスト獲得演出
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()

        # get the card id form url
        cardid = args.getInt(1)

        cur_eventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=settings.DB_READONLY)

        if not cur_eventmaster:
            raise CabaretError(u'イベントは終了しました', CabaretError.Code.EVENT_CLOSED)

        raidbattle = BackendApi.get_raid_battleresult(model_mgr, v_player.id, using=settings.DB_READONLY)
        if raidbattle is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'想定外の遷移です')
            url = UrlMaker.producehappening()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return

        # レイド情報を取得.
        raidboss = None
        happeningraidset = BackendApi.get_producehappeningraidset(model_mgr, raidbattle.raidid, using=settings.DB_READONLY)
        if happeningraidset:
            raidboss = happeningraidset.raidboss
        if raidboss is None:
            raise CabaretError(u'超太客が存在しません', CabaretError.Code.NOT_DATA)

        animdata = raidbattle.process
        is_win = animdata.winFlag

        # 結果へのURL.
        happeningset = BackendApi.get_producehappening(model_mgr, raidbattle.raidid, using=settings.DB_READONLY)
        eventid = HappeningUtil.get_produceeventid(happeningset.happening.event)
        if cur_eventmaster and cur_eventmaster.id == eventid:
            url = UrlMaker.produceraidresultanim()
        elif is_win:
            url = UrlMaker.produceraidend(raidbattle.raidid)
        else:
            url = UrlMaker.produceraidresult()

        cardmaster = BackendApi.get_model(model_mgr, CardMasterView, cardid, using=settings.DB_READONLY)
        params = {}
        params['backUrl'] = self.makeAppLinkUrl(url)
        params['cast'] = self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(cardmaster))

        self.appRedirectToEffect('produce_event/produce_lastcastget/effect.html', params)

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
                happeningraidset = BackendApi.get_producehappeningraidset(model_mgr, int(raidid), using=settings.DB_READONLY)
            if happeningraidset is None or happeningraidset.raidboss is None:
                raise CabaretError(u'接客できない超太客です', CabaretError.Code.ILLEGAL_ARGS)
            elif happeningraidset.happening.happening.oid != v_player.id:
                raise CabaretError(u'接客できない超太客です', CabaretError.Code.ILLEGAL_ARGS)
            elif happeningraidset.happening.happening.is_active():
                raise CabaretError(u'この超太客はまだ終了していません', CabaretError.Code.ILLEGAL_ARGS)

            url = UrlMaker.produceraidend(raidid)
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
            if is_win:
                # it should always be win
                url = UrlMaker.produceraidend(raidid)
            else:
                # for debug purposes
                # this should never happen
                url = UrlMaker.produceraidresult()

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
            url = UrlMaker.producehappening()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return

        # レイド情報を取得.
        raidboss = BackendApi.get_raid(model_mgr, raidbattle.raidid, using=settings.DB_READONLY)
        if raidboss is None:
            raise CabaretError(u'超太客が存在しません', CabaretError.Code.NOT_DATA)

        animdata = raidbattle.process

        raidboss.raid.hp = animdata.bossHpPost
        if raidboss.raid.hp < 1:
            url = UrlMaker.produceraidend(raidbattle.raidid)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return

        # 借りたカード.
        func_put_playerlist = None
        helpleadercard = raidbattle.getHelpCard()
        if helpleadercard:
            cardmaster = BackendApi.get_cardmasters([helpleadercard.mid], model_mgr, using=settings.DB_READONLY).get(
                helpleadercard.mid)
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
        happeningset = BackendApi.get_producehappening(model_mgr, raidboss.id, using=settings.DB_READONLY)
        func_happeninginfo_callback = self.putHappeningInfo(happeningset, raidboss, do_execute=False)

        func_put_attacklog = None

        is_event = False
        produceeventmaster = None
        eventid = HappeningUtil.get_produceeventid(happeningset.happening.event)
        if eventid:
            produceeventmaster = BackendApi.get_produce_event_master(model_mgr, eventid, using=settings.DB_READONLY)

        if produceeventmaster:
            # イベント情報.
            config = BackendApi.get_current_produce_event_config(model_mgr, using=settings.DB_READONLY)
            self.html_param['raidevent'] = Objects.produceevent(self, produceeventmaster, config)

            # ダメージ履歴.
            func_put_attacklog = self.putRaidAttackLog(raidboss)

            # イベント用の設定.
            eventraidmaster = BackendApi.get_produceevent_raidmaster(model_mgr, produceeventmaster.id, raidboss.raid.mid, using=settings.DB_READONLY)
            BackendApi.put_raidevent_specialcard_info(self, v_player.id, eventraidmaster, using=settings.DB_READONLY)

            self.html_param['url_produceevent_top'] = self.makeAppLinkUrl(UrlMaker.produceevent_top(produceeventmaster.id))

            is_event = True

        # 戻るUrl.
        if raidboss.raid.oid == v_player.id:
            # 発見者.
            if is_event:
                url = UrlMaker.produceevent_battlepre()
            else:
                url = UrlMaker.producehappening()
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

        eventid = HappeningUtil.get_produceeventid(happeningset.happening.event)
        self.writeHtmlSwitchEvent('bosslose', eventid, eventmaster=produceeventmaster)

    def procEnd(self, args):
        """レイド終了.
        """
        model_mgr = self.getModelMgr()

        # ハプニングとレイド情報を取得.
        raidid = str(args.get(1, ''))

        happeningraidset = None
        if raidid.isdigit():
            raidid = int(raidid)
            happeningraidset = BackendApi.get_producehappeningraidset(model_mgr, raidid, using=settings.DB_READONLY)
        if happeningraidset is None or happeningraidset.raidboss is None:
            raise CabaretError(u'超太客が存在しません', CabaretError.Code.ILLEGAL_ARGS)

        v_player = self.getViewerPlayer()

        happeningset = happeningraidset.happening
        raidboss = happeningraidset.raidboss
        if 0 < raidboss.raid.hp:
            url = UrlMaker.producehappeningend(happeningset.id)
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
                    cardmaster = BackendApi.get_cardmasters([helpleadercard.mid], model_mgr,
                                                            using=settings.DB_READONLY).get(helpleadercard.mid)
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
        url = UrlMaker.producehappeningend(happeningset.id)
        self.html_param['url_happeningend'] = self.makeAppLinkUrl(url)
        
        produce_event_config = BackendApi.get_current_produce_event_config(model_mgr, using=settings.DB_READONLY)
        if not produce_event_config:
            raise CabaretError(u'ProduceEventConfigに設定がありません', CabaretError.Code.EVENT_CLOSED)
        self.html_param['produce_card'] = BackendApi.create_produce_cardinfo(self, model_mgr, v_player.id, produce_event_config.mid)
        produce_happening_result = ProduceEventHappeningResult.get_instance(model_mgr, v_player.id, produce_event_config.mid, using=settings.DB_READONLY)
        self.html_param['produce_happening_result'] = produce_happening_result.to_dict()
        player_education = BackendApi.get_player_education(model_mgr, v_player.id, produce_event_config.mid, using=settings.DB_READONLY)
        self.html_param['produce_cast_master'] = player_education.get_produce_castmaster().to_dict()
        
        func_raidattacklog_callback = None

        raideventid = 0
        produceeventid = 0
        if raidboss.produceeventraidmaster:
            produceeventid = raidboss.produceeventraidmaster.eventid

        self.execute_api()
        callback()

        if func_put_playerlist:
            func_put_playerlist()

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
                    'url': url,
                    'type': htype,
                }
        self.html_param['happening_backinfo'] = backinfo

        self.html_param['url_scout_top'] = self.makeAppLinkUrl(UrlMaker.produceevent_scouttop())
        self.writeHtmlSwitchEvent('bosswin', produceeventid)

    def tr_write(self, uid, raidid, key, raidmaster, deckcardlist, friendcard, is_strong, champagne, score):
        """書き込み.
        """
        self.addloginfo('tr_write')
        model_mgr = ModelRequestMgr(loginfo=self.addloginfo)
        player = BackendApi.get_players(self, [uid], [PlayerFriend], model_mgr=model_mgr)[0]
        BackendApi.tr_raidbattle(model_mgr, raidid, key, player, raidmaster, deckcardlist, friendcard, is_strong,
                                 self.is_pc, champagne=champagne, addloginfo=self.addloginfo, score=score,
                                 is_produceevent=True)
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
            if not raidboss.produceeventraidmaster:
                eventraidmaster = BackendApi.get_eventraidmaster_by_modeleventvalue(model_mgr,
                                                                                    happeningset.happening.event,
                                                                                    raidboss.raid.mid,
                                                                                    using=settings.DB_READONLY)
                raidboss.setEventRaidMaster(eventraidmaster)

            if raidboss.raid.hp < 1 and RaidBoss.RAIDEVENT_PRIZE_UPDATETIME <= happeningset.happening.ctime:
                damagerecord = raidboss.getDamageRecord(v_player.id)
                # 報酬.
                if is_owner:
                    # 発見者.
                    cabaretking = raidboss.get_cabaretking()
                    if 0 < cabaretking:
                        prizelist.append(PrizeData.create(cabaretking=cabaretking))
                    prizelist.extend(
                        BackendApi.get_prizelist(model_mgr, raidboss.master.prizes, using=settings.DB_READONLY))
                    prizelist.extend(BackendApi.aggregate_happeningprize(happeningset.happening))

                    # ドロップアイテム報酬
                    if happeningset.happening.items:
                        dropitems = [happening.id for happening in happeningset.happening.items['dropitems']]
                        prizelist.extend(BackendApi.get_prizelist(model_mgr, dropitems, using=settings.DB_READONLY))
                        # elif 0 < damagerecord.damage_cnt:
                        #     # 救援者.
                        #     demiworld = raidboss.get_demiworld()
                        #     if 0 < demiworld:
                        #         prizelist.append(PrizeData.create(demiworld=demiworld))
                        #     prizelist.extend(BackendApi.get_prizelist(model_mgr, raidboss.master.helpprizes, using=settings.DB_READONLY))

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
            obj_happening = Objects.producehappening(self, HappeningRaidSet(happeningset, raidboss), prizeinfo,
                                                     persons.get(o_player.dmmid))
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
