# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.pljson import Json
import settings_sub
from urlparse import urlparse
import urllib
from defines import Defines
from platinumegg.app.cabaret.util.scout import ScoutEventNone
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.present import PresentSet
import datetime
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.util.rediscache import LoginBonusTimeLimitedAnimationSet
from platinumegg.app.cabaret.views.application.loginbonus.base import LoginBonusHandler


class Handler(AppHandler):
    """演出のパラメータを取得.
    """
    
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 500
    
    def processError(self, error_message):
        self.response.set_status(500)
        self.response.end()
    
    def __sendErrorResponse(self, status):
        self.response.set_status(status)
        self.response.end()
    
    def checkUser(self):
        pass
    
    def check_process_pre(self):
        if settings_sub.IS_LOCAL:
            return True
        elif self.osa_util.is_dbg_user:
            pass
        elif not settings_sub.IS_DEV and self.osa_util.viewer_id in ('10814964', '11404810', '39121', '12852359', '1412759', '11830507', '11467913', '10128761', '11868885', '434009', '23427632', '10918839', '21655464', '17279084', '24500573', '28774432', '11739356','2588824','28978730','20174324'):
            pass
        elif not self.checkMaintenance():
            return False
        return True
    
    def process(self):
        args = self.getUrlArgs('/effect/')
        ope = args.get(0)

        f = getattr(self, 'proc_%s' % ope, None)
        if f is None:
            self.__sendErrorResponse(404)
            return
        f(args)
    
    def writeResponseBody(self, params):
        if self.isUsePCEffect():
            body = Json.encode({
                'flashVars' : self.makeFlashVars(params)
            })
        else:
            body = Json.encode(params)
        self.response.set_header('Content-Type', 'plain/text')
        self.response.set_status(200)
        self.response.send(body)
    
    def proc_battle(self, args):
        """バトル演出.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer(True)
        if v_player is None:
            # 結果が存在しない.
            self.osa_util.logger.error('Player is None. opensocial_viewer_id=%s' % self.osa_util.viewer_id)
            self.__sendErrorResponse(404)
            return
        
        # 結果データ.
        battleresult = BackendApi.get_battleresult(model_mgr, v_player.id, using=settings.DB_READONLY)
        if battleresult is None or not battleresult.anim:
            # 結果が存在しない.
            self.osa_util.logger.error('result is None')
            self.__sendErrorResponse(404)
            return
        
        # 演出用パラメータ.
        animationdata = battleresult.anim
        params = animationdata.to_animation_data(self)
        if BackendApi.get_current_battleevent_master(model_mgr, using=settings.DB_READONLY):
            params['feverFlag'] = 0     # イベントでは表示しない.
        
        urldata = urlparse(self.url_cgi)
        url = '%s://%s%s' % (urldata.scheme, settings_sub.WEB_GLOBAL_HOST, urldata.path)
        url = url + UrlMaker.battleresultanim()
        url = self.osa_util.makeLinkUrl(self.addTimeStamp(url))
        params['backUrl'] = url
        
        self.writeResponseBody(params)
    
    def proc_battleevent(self, args):
        """イベントバトル演出.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer(True)
        if v_player is None:
            # 結果が存在しない.
            self.osa_util.logger.error('Player is None. opensocial_viewer_id=%s' % self.osa_util.viewer_id)
            self.__sendErrorResponse(404)
            return
        uid = v_player.id
        
        try:
            eventid = int(args.get(1))
        except:
            # 引数がおかしい.
            self.osa_util.logger.error('Invalid arguments')
            self.__sendErrorResponse(400)
            return
        
        # 結果データ.
        battleresult = BackendApi.get_battleevent_battleresult(model_mgr, eventid, uid, using=settings.DB_READONLY)
        if battleresult is None or not battleresult.anim:
            # 結果が存在しない.
            self.osa_util.logger.error('result is None')
            self.__sendErrorResponse(404)
            return
        
        # 演出用パラメータ.
        animationdata = battleresult.anim
        params = animationdata.to_animation_data(self)
        params['feverFlag'] = 0     # イベントでは表示しない.

        rarity = args.getInt(2)
        piecenumber = args.getInt(3)
        is_complete = args.getInt(4)
        
        urldata = urlparse(self.url_cgi)
        url = '%s://%s%s' % (urldata.scheme, settings_sub.WEB_GLOBAL_HOST, urldata.path)
        url = url + UrlMaker.battleevent_battleresultanim(eventid, rarity, piecenumber, is_complete)
        url = self.osa_util.makeLinkUrl(self.addTimeStamp(url))
        params['backUrl'] = url
        
        self.writeResponseBody(params)
    
    def proc_scout(self, args):
        """スカウト演出.
        """
        try:
            scoutid = int(args.get(1))
            scoutkey = urllib.unquote(args.get(2))
        except:
            # 引数がおかしい.
            self.osa_util.logger.error('Invalid arguments')
            self.__sendErrorResponse(400)
            return
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        uid = v_player.id
        
        using = settings.DB_READONLY
        
        # 進行情報.
        playdata = BackendApi.get_scoutprogress(model_mgr, uid, [scoutid], using=using).get(scoutid, None)
        if playdata is None or playdata.alreadykey != scoutkey:
            # DBからとり直すべき.
            playdata = BackendApi.get_scoutprogress(model_mgr, uid, [scoutid], using=settings.DB_DEFAULT, reflesh=True).get(scoutid, None)
            if playdata is None or playdata.alreadykey != scoutkey:
                self.osa_util.logger.error('Not Found')
                self.__sendErrorResponse(404)
                return
        
        eventlist = playdata.result.get('event', [])
        if eventlist:
            # ここで必要なのははじめの１件.
            event = eventlist[0]
        else:
            # なにも起きなかった.
            event = ScoutEventNone.create()
        
        eventKind = event.get_type()
        backUrl = None
        
        # イベント毎の設定.
        if eventKind == Defines.ScoutEventType.NONE:
            # そのままもう一回.
            backUrl = UrlMaker.scoutdo(scoutid, playdata.confirmkey)
        elif eventKind in (Defines.ScoutEventType.LEVELUP, Defines.ScoutEventType.COMPLETE, Defines.ScoutEventType.HAPPENING):
            # 結果表示へ.
            backUrl = UrlMaker.scoutresultanim(scoutid, scoutkey, 0)
        
        # 結果表示へ.
        backUrl = backUrl or UrlMaker.scoutresult(scoutid, scoutkey)
        
        # 演出のパラメータ.
        scoutmaster = BackendApi.get_scouts(model_mgr, [scoutid], using=using)[0]
        resultlist = playdata.result.get('result', [])
        params = BackendApi.make_scoutanim_params(self, scoutmaster, eventlist, resultlist)
        if params is None:
            self.osa_util.logger.error('Not Found')
            self.__sendErrorResponse(404)
            return
        
        urldata = urlparse(self.url_cgi)
        url = '%s://%s%s' % (urldata.scheme, settings_sub.WEB_GLOBAL_HOST, urldata.path)
        url = self.osa_util.makeLinkUrl(self.addTimeStamp(url + backUrl))
        params['backUrl'] = url
        
        self.writeResponseBody(params)
    
    def __make_eventscoutanim_params(self, stagemaster, playdata, backUrl):
        """スカウトイベント演出.
        """
        eventlist = playdata.result.get('event', [])
        
        # 演出のパラメータ.
        resultlist = playdata.result.get('result', [])
        params = BackendApi.make_scoutanim_params(self, stagemaster, eventlist, resultlist, feveretime=getattr(playdata, 'feveretime', None))
        if params is None:
            self.osa_util.logger.error('Not Found')
            self.__sendErrorResponse(404)
            return
        
        urldata = urlparse(self.url_cgi)
        url = '%s://%s%s' % (urldata.scheme, settings_sub.WEB_GLOBAL_HOST, urldata.path)
        url = self.osa_util.makeLinkUrl(self.addTimeStamp(url + backUrl))
        params['backUrl'] = url
        
        return params
    
    def proc_scoutevent(self, args):
        """スカウトイベント演出.
        """
        try:
            stageid = int(args.get(1))
            scoutkey = urllib.unquote(args.get(2))
        except:
            # 引数がおかしい.
            self.osa_util.logger.error('Invalid arguments')
            self.__sendErrorResponse(400)
            return
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=using)
        if eventmaster is None:
            # 引数がおかしい.
            self.osa_util.logger.error('Event Not Found')
            self.__sendErrorResponse(404)
            return
        mid = eventmaster.id
        
        # 進行情報.
        playdata = BackendApi.get_event_playdata(model_mgr, mid, v_player.id, using)
        if playdata is None or playdata.alreadykey != scoutkey:
            self.osa_util.logger.error('Not Found')
            self.__sendErrorResponse(404)
            return
        
        eventlist = playdata.result.get('event', [])
        if eventlist:
            # ここで必要なのははじめの１件.
            event = eventlist[0]
        else:
            # なにも起きなかった.
            event = ScoutEventNone.create()
        
        eventKind = event.get_type()
        backUrl = None
        
        # イベント毎の設定.
        if eventKind == Defines.ScoutEventType.NONE:
            # そのままもう一回.
            backUrl = UrlMaker.scouteventdo(stageid, playdata.confirmkey)
        else:
            if playdata.result.get('feverstart'):
                # フィーバー演出
                backUrl = UrlMaker.scouteventfever(stageid, scoutkey)
            elif playdata.result.get('lovetime_start'):
                # 逢引タイム演出.
                backUrl = UrlMaker.scouteventlovetime(stageid, scoutkey)
            elif eventKind in (Defines.ScoutEventType.LEVELUP, Defines.ScoutEventType.COMPLETE, Defines.ScoutEventType.HAPPENING):
                # 結果表示へ.
                backUrl = UrlMaker.scouteventresultanim(stageid, scoutkey, 0)
        
        # 結果表示へ.
        backUrl = backUrl or UrlMaker.scouteventresult(stageid, scoutkey)
        
        stagemaster = BackendApi.get_event_stage(model_mgr, stageid, using=using)
        params = self.__make_eventscoutanim_params(stagemaster, playdata, backUrl)
        if self.response.isEnd:
            return
        
        self.writeResponseBody(params)
    
    def proc_raideventscout(self, args):
        """スカウトイベント演出.
        """
        try:
            stageid = int(args.get(1))
            scoutkey = urllib.unquote(args.get(2))
        except:
            # 引数がおかしい.
            self.osa_util.logger.error('Invalid arguments')
            self.__sendErrorResponse(400)
            return
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        eventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=using)
        if eventmaster is None:
            # 引数がおかしい.
            self.osa_util.logger.error('Event Not Found')
            self.__sendErrorResponse(404)
            return
        mid = eventmaster.id
        
        # 進行情報.
        playdata = BackendApi.get_raideventstage_playdata(model_mgr, mid, uid, using)
        if playdata is None or playdata.alreadykey != scoutkey:
            self.osa_util.logger.error('Not Found')
            self.__sendErrorResponse(404)
            return
        
        eventlist = playdata.result.get('event', [])
        if eventlist:
            # ここで必要なのははじめの１件.
            event = eventlist[0]
        else:
            # なにも起きなかった.
            event = ScoutEventNone.create()
        
        eventKind = event.get_type()
        backUrl = None
        
        # イベント毎の設定.
        if eventKind == Defines.ScoutEventType.NONE:
            # そのままもう一回.
            backUrl = UrlMaker.raidevent_scoutdo(stageid, playdata.confirmkey)
        elif eventKind in (Defines.ScoutEventType.LEVELUP, Defines.ScoutEventType.COMPLETE, Defines.ScoutEventType.HAPPENING):
            # 結果表示へ.
            backUrl = UrlMaker.raidevent_scoutresultanim(stageid, scoutkey, 0)
        
        # 結果表示へ.
        backUrl = backUrl or UrlMaker.raidevent_scoutresult(stageid, scoutkey)
        
        stagemaster = BackendApi.get_raidevent_stagemaster(model_mgr, stageid, using=using)
        params = self.__make_eventscoutanim_params(stagemaster, playdata, backUrl)
        if self.response.isEnd:
            return
        
        self.writeResponseBody(params)

    def proc_produceeventscout(self, args):
        """プロデュースイベントのスカウトイベント演出.
        """
        try:
            stageid = int(args.get(1))
            scoutkey = urllib.unquote(args.get(2))
        except:
            # 引数がおかしい.
            self.osa_util.logger.error('Invalid arguments')
            self.__sendErrorResponse(400)
            return

        v_player = self.getViewerPlayer()
        uid = v_player.id

        model_mgr = self.getModelMgr()

        using = settings.DB_READONLY

        eventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=using)
        if eventmaster is None:
            # 引数がおかしい.
            self.osa_util.logger.error('Event Not Found')
            self.__sendErrorResponse(404)
            return
        mid = eventmaster.id

        # 進行情報.
        playdata = BackendApi.get_raideventstage_playdata(model_mgr, mid, uid, using)
        playdata = BackendApi.get_produceeventstage_playdata(model_mgr, mid, uid, using)
        if playdata is None or playdata.alreadykey != scoutkey:
            self.osa_util.logger.error('Not Found')
            self.__sendErrorResponse(404)
            return

        eventlist = playdata.result.get('event', [])
        if eventlist:
            # ここで必要なのははじめの１件.
            event = eventlist[0]
        else:
            # なにも起きなかった.
            event = ScoutEventNone.create()

        eventKind = event.get_type()
        backUrl = None

        # イベント毎の設定.
        if eventKind == Defines.ScoutEventType.NONE:
            # そのままもう一回.
            backUrl = UrlMaker.produceevent_scoutdo(stageid, playdata.confirmkey)
        elif eventKind in (Defines.ScoutEventType.LEVELUP, Defines.ScoutEventType.COMPLETE, Defines.ScoutEventType.HAPPENING):
            # 結果表示へ.
            backUrl = UrlMaker.produceevent_scoutresultanim(stageid, scoutkey, 0)

        # 結果表示へ.
        backUrl = backUrl or UrlMaker.produceevent_scoutresult(stageid, scoutkey)

        stagemaster = BackendApi.get_produceevent_stagemaster(model_mgr, stageid, using=using)
        params = self.__make_eventscoutanim_params(stagemaster, playdata, backUrl)
        if self.response.isEnd:
            return

        self.writeResponseBody(params)
    
    def proc_gacha(self, args):
        """ガチャ演出.
        """
        CONTENT_NUM_PER_PAGE = 10
        
        try:
            mid = int(args.get(1))
            reqkey = urllib.unquote(args.get(2))
            page = int(args.get(3) or 0)
        except:
            # 引数がおかしい.
            self.osa_util.logger.error('Invalid arguments')
            self.__sendErrorResponse(400)
            return
        
        model_mgr = self.getModelMgr()
        using = settings.DB_READONLY
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        gachamaster = BackendApi.get_gachamaster(model_mgr, mid, using)
        
        playdata = None
        gachamasterstep = None
        if gachamaster:
            if gachamaster.stepsid > 0:
                if gachamaster.stepsid != gachamaster.id:
                    gachamasterstep = BackendApi.get_gachamaster(model_mgr, gachamaster.stepsid, using=using)
                    if gachamasterstep is None:
                        self.osa_util.logger.error('Not Found')
                        self.__sendErrorResponse(404)
                        return
                else:
                    gachamasterstep = gachamaster
            
            playdata = BackendApi.get_gachaplaydata(model_mgr, uid, [gachamaster.boxid], using=using).get(gachamaster.boxid)
        if playdata is None or not playdata.result:
            # 結果がない.
            self.osa_util.logger.error('Not Found')
            self.__sendErrorResponse(404)
            return
        
        if gachamaster.consumetype == Defines.GachaConsumeType.RANKING:
            cardtextformat_getter = lambda master : Defines.EffectTextFormat.RANKINGGACHA_CARDTEXT
        else:
            cardtextformat_getter = lambda master : Defines.EffectTextFormat.GACHA_CARDTEXT if master.ckind == Defines.CardKind.NORMAL else Defines.EffectTextFormat.GACHA_ITEMTEXT
        
        sep = Defines.ANIMATION_SEPARATE_STRING
        urlsep = Defines.ANIMATION_URLSEPARATE_STRING
        newFlag = []
        rarityFlag = []
        cardText = []
        image = []
        pointlist = []
        expectation = []
        is_first = page == 0
        is_last = True
        
        # 獲得したカード.
        resultlist = playdata.result['result'] if isinstance(playdata.result, dict) else playdata.result
        if gachamaster.consumetype in (Defines.GachaConsumeType.FUKUBUKURO, Defines.GachaConsumeType.FUKUBUKURO2016, Defines.GachaConsumeType.FUKUBUKURO2017):
            page_last = int((len(resultlist) + CONTENT_NUM_PER_PAGE - 1) / CONTENT_NUM_PER_PAGE) - 1
            page = min(page, page_last)
            offset = page * CONTENT_NUM_PER_PAGE
            resultlist = resultlist[offset:(offset+CONTENT_NUM_PER_PAGE)]
            is_last = page == page_last

        if gachamaster.consumetype == Defines.GachaConsumeType.FIXEDSR:
            try:
                gachamorecast = int(args.get(5))
            except:
                self.osa_util.logger.error('Invalid arguments')
                self.__sendErrorResponse(400)
                return
            if gachamorecast == 0:
                resultlist = resultlist[gachamaster.rarity_fixed_num:]
        
        cardidlist = [data['id'] for data in resultlist]
        cardmasters = BackendApi.get_cardmasters(cardidlist, model_mgr, using=settings.DB_READONLY)
        groupidlist = [data['group'] for data in resultlist]
        groupmaster_dict = BackendApi.get_gachagroupmaster_dict(model_mgr, groupidlist, using=settings.DB_READONLY)
        
        rarityFlag_getter = None
        
        if gachamaster.consumetype == Defines.GachaConsumeType.CHRISTMAS:
            image_getter = lambda idx,master:(CardUtil.makeThumbnailUrlIcon(master) if idx < gachamaster.continuity-1 else CardUtil.makeThumbnailUrlMiddle(master))
            cardtext_getter = lambda idx,master:master.name
        elif gachamaster.consumetype in (Defines.GachaConsumeType.FUKUBUKURO, Defines.GachaConsumeType.FUKUBUKURO2016, Defines.GachaConsumeType.FUKUBUKURO2017):
            image_getter = lambda idx,master:CardUtil.makeThumbnailUrlMiddle(master)
            cardtext_getter = lambda idx,master:master.name
        elif gachamaster.consumetype == Defines.GachaConsumeType.XMAS_OMAKE:
            image_getter = lambda idx,master:CardUtil.makeThumbnailUrlIcon(master)
            cardtext_getter = lambda idx,master:master.name
        elif gachamaster.consumetype == Defines.GachaConsumeType.SCOUTEVENT and Defines.SCOUTEVENTGACHA_USE_EXCLUSIVE_USE_EFFECT:
            image_getter = lambda idx,master:CardUtil.makeThumbnailUrlMiddle(master)
            cardtext_getter = lambda idx,master:(cardtextformat_getter(master) % master.name)
        else:
            image_getter = lambda idx,master:self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(master))
            cardtext_getter = lambda idx,master:(cardtextformat_getter(master) % master.name)
        rarityFlag_getter = rarityFlag_getter or (lambda master:'1' if Defines.Rarity.SUPERRARE <= master.rare else '0')
        
        max_rare = Defines.Rarity.NORMAL
        for idx,data in enumerate(resultlist):
            master = cardmasters[data['id']]
            groupmaster = groupmaster_dict.get(data['group'])
            newFlag.append(str(int(bool(data['is_new']))))
            cardText.append(cardtext_getter(idx, master))
            image.append(image_getter(idx, master))
            pointlist.append(str(data['point']))
            expectation.append(str(groupmaster.expectation) if groupmaster else str(Defines.RankingGachaExpect.LOW))
            rarityFlag.append(rarityFlag_getter(master))
            
            if max_rare < master.rare:
                max_rare = master.rare
        
        v_player = self.getViewerPlayer()
        
        # シートガチャ情報.
        seatmodels = BackendApi.get_gachaseatmodels_by_gachamaster(model_mgr, uid, gachamasterstep or gachamaster, do_get_result=False, using=settings.DB_READONLY)
        
        urldata = urlparse(self.url_cgi)
        urlhead = '%s://%s%s' % (urldata.scheme, settings_sub.WEB_GLOBAL_HOST, urldata.path)
        if seatmodels.get('playdata'):
            # シート演出へ.
            url = urlhead + UrlMaker.gachaseatanim(gachamaster.id, reqkey)
        else:
            url = urlhead + UrlMaker.gacharesult(gachamaster.id, reqkey)
        backUrl = self.osa_util.makeLinkUrl(self.addTimeStamp(url))
        
        params = {
            'newFlag': sep.join(newFlag),
            'cardText' : sep.join(cardText),
            'image' : urlsep.join(image),
        }
        
        if gachamaster.consumetype == Defines.GachaConsumeType.CHRISTMAS:
            params['logoPre'] = self.url_static + 'effect/sp/v2/gachaxmas/data/'
            params['pre'] = self.url_static_img
            params['cardText'] = cardText[-1]
        elif gachamaster.consumetype == Defines.GachaConsumeType.RANKING:
            params.update({
                'point' : sep.join(pointlist),
                'expectation' : sep.join(expectation),
                'pre' : self.url_static + 'img/sp/large/gacha/ranking/rank_01/',    # TODO:DBを見るように修正が必要.
                'logo_img' : 'event_logo.png',
                'logo_w_img' : 'event_logo_w.png',
            })
        elif gachamaster.consumetype == Defines.GachaConsumeType.SCOUTEVENT and Defines.SCOUTEVENTGACHA_USE_EXCLUSIVE_USE_EFFECT:
            eventmaster = BackendApi.get_current_present_scouteventmaster(model_mgr, using=settings.DB_READONLY)
            if Defines.SCOUTEVENTGACHA_FOR_VALENTINE:
                params.update({
                    'pre' : self.url_static_img,
                    'effectPre' : self.url_static + 'effect/sp/v2/gachascev/data/scev_25/',
                    'cardText' : params['cardText'].replace('が入店しました', ''), # js, flash の修正をすると作業が大きくなるのでquick hack.
                })
            else:
                params.update({
                    'imagePre' : self.url_static_img,
                    'rarityFlag' : sep.join(rarityFlag),
                    'logoPre' : self.makeAppLinkUrlImg('event/scevent/%s/gacha/' % eventmaster.codename),
                })
        elif gachamaster.consumetype in (Defines.GachaConsumeType.FUKUBUKURO, Defines.GachaConsumeType.FUKUBUKURO2016, Defines.GachaConsumeType.FUKUBUKURO2017):
            url = None
            if is_last:
                if isinstance(playdata.result, dict) and playdata.result.get('omake'):
                    prizelist = BackendApi.get_prizelist(model_mgr, playdata.result['omake'], using=settings.DB_READONLY)
                    presentlist = BackendApi.create_present_by_prize(model_mgr, v_player.id, prizelist, 0, using=settings.DB_READONLY, do_set_save=False)
                    presentsetlist = PresentSet.presentToPresentSet(model_mgr, presentlist, using=settings.DB_READONLY)
                    
                    thumblist = []
                    omakeindexes = []
                    for presentset in presentsetlist:
                        if presentset.present.itype in (Defines.ItemType.GOLD, Defines.ItemType.GACHA_PT):
                            num = 1
                        else:
                            num = presentset.num
                        
                        if presentset.itemthumbnail in thumblist:
                            idx = thumblist.index(presentset.itemthumbnail)
                        else:
                            idx = len(thumblist)
                            thumblist.append(presentset.itemthumbnail)
                        
                        omakeindexes.extend([str(idx)] * num)
                    
                    if thumblist:
                        params.update({
                            'itemImage' : urlsep.join(thumblist),
                            'itemImageIdx' : sep.join(omakeindexes),
                        })
            else:
                url = urlhead + UrlMaker.gachaanimsub(gachamaster.id)
                url = OSAUtil.addQuery(url, Defines.URLQUERY_PAGE, page + 1)
                url = self.osa_util.makeLinkUrl(self.addTimeStamp(url))
            
            params.update({
                'skipUrl': backUrl,
                'pre' : self.url_static_img,
                # 4月ver
                #'logoPre' : self.url_static + 'effect/sp/v2/gachahappybag201604/data/',
                #'logoPre' : self.url_static + 'effect/sp/v2/gachahappybag201605/data/',
                # 'logoPre' : self.url_static + 'effect/sp/v2/gachahappybag201607/data/',
                # 'logoPre' : self.url_static + 'effect/sp/v2/gachahappybag201608/data/',
                'logoPre' : self.url_static + 'effect/sp/v2/gachahappybag201701/data/',
                'isFirst' : is_first,
                'isLast' : is_last,
                'n' : gachamaster.continuity,
                'rarityFlag' : sep.join(rarityFlag),
            })
            del params['cardText']
            
            backUrl = url or backUrl
        elif gachamaster.consumetype == Defines.GachaConsumeType.SR_SSR_PROBABILITY_UP or gachamaster.consumetype == Defines.GachaConsumeType.PTCHANGE:
            #トレードショップが開いていたら
            if gachamaster.trade_shop_master_id is not None and 0 < gachamaster.trade_shop_master_id:
                try:
                    lottery_point = int(args.get(4))
                    url = urlhead + UrlMaker.gacharesult(gachamaster.id, reqkey, lottery_point=lottery_point)
                except:
                    # 引数がおかしい.
                    self.osa_util.logger.error('Invalid arguments')
                    self.__sendErrorResponse(400)
                    return
            else:
                url = urlhead + UrlMaker.gacharesult(gachamaster.id, reqkey)
            # URL作り直し
            backUrl = self.osa_util.makeLinkUrl(self.addTimeStamp(url))
        elif gachamaster.consumetype == Defines.GachaConsumeType.FIXEDSR:
            try:
                gachamorecast = int(args.get(5))
            except:
                self.osa_util.logger.error('Invalid arguments')
                self.__sendErrorResponse(400)
                return

            if gachamorecast == 0:
                url = urlhead + UrlMaker.gachamorecast(gachamaster.id, reqkey)
                backUrl = self.osa_util.makeLinkUrl(self.addTimeStamp(url))
            else:
                if 0 < gachamaster.rarity_fixed_num:
                    fixed_card_id = cardidlist[0]
                    card = BackendApi.get_cardmasters([fixed_card_id], model_mgr).get(fixed_card_id)
                    backUrl = self.makeAppLinkUrl(UrlMaker.gacharesult(gachamaster.id, reqkey))
                    params = {
                        'cardText': Defines.EffectTextFormat.GACHA_CARDTEXT % card.name,
                        'image': self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(card)),
                        'pre': 'img/',
                    }
                else:
                    self.osa_util.logger.error('Not set Gachamaster.rarity_fixed_num')
                    self.__sendErrorResponse(400)
                    return
        elif gachamaster.consumetype == Defines.GachaConsumeType.XMAS_OMAKE:
            params = {
                'pre' : self.url_static_img,
                'logoPre' : self.url_static + 'effect/sp/v2/gachaxmas2015/',
                'image' : urlsep.join(image),
                'newFlag': sep.join(newFlag)
            }

        params['backUrl'] = backUrl
        self.writeResponseBody(params)
    
    def proc_panelmission(self, args):
        """パネルミッション.
        """
        try:
            panel = int(args.get(1))
        except:
            # 引数がおかしい.
            self.osa_util.logger.error('Invalid arguments')
            self.__sendErrorResponse(400)
            return
        
        model_mgr = self.getModelMgr()
        using = settings.DB_READONLY
        
        # パネルのマスターデータ.
        panelmaster = None
        if panel:
            panelmaster = BackendApi.get_panelmission_panelmaster(model_mgr, panel, using=using)
        if panelmaster is None:
            self.osa_util.logger.error('Illigal panel number')
            self.__sendErrorResponse(400)
            return
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        now = OSAUtil.get_now()
        
        # 進行情報.
        panelplaydata = BackendApi.get_panelmission_data(model_mgr, uid, panel, using=using, get_instance=False)
        if panelplaydata is None:
            self.osa_util.logger.error('Illigal panel number')
            self.__sendErrorResponse(400)
            return
        
        # 演出パラメータ.
        params = {
#            'logoPre' : self.url_static + 'effect/sp/v2/panel_mission/data/201412/',
#            'logoPre' : self.url_static + 'effect/sp/v2/panel_mission/data/201505/',
#            'logoPre' : self.url_static + 'effect/sp/v2/panel_mission/data/201508/',
#            'logoPre' : self.url_static + 'effect/sp/v2/panel_mission/data/201512/',
#            'logoPre' : self.url_static + 'effect/sp/v2/panel_mission/data/201602/',
#            'logoPre' : self.url_static + 'effect/sp/v2/panel_mission/data/201604/',
#            'logoPre' : self.url_static + 'effect/sp/v2/panel_mission/data/201606/',
#            'logoPre' : self.url_static + 'effect/sp/v2/panel_mission/data/201607/',
#             'logoPre' : self.url_static + 'effect/sp/v2/panel_mission/data/201610/',
#             'logoPre' : self.url_static + 'effect/sp/v2/panel_mission/data/201612/',
            'logoPre' : self.url_static + 'effect/sp/v2/panel_mission/data/201702/',
            'pre' : self.url_static_img,
            'panel' : panel,
            'bg' : panelmaster.image,
        }
        
        # ミッションのマスター.
        missionmaster_list = BackendApi.get_panelmission_missionmaster_by_panelid(model_mgr, panel, using=using)
        
        # 全クリフラグ.
        is_allend = True
        
        # 今回クリアしたミッション.
        max_time = None
        clearlist = []
        missionmaster_dict = {}
        for missionmaster in missionmaster_list:
            number = missionmaster.number
            missionmaster_dict[number] = missionmaster
            
            idx = number - 1
            data = panelplaydata.get_data(number)
            rtime = data['rtime']
            if now < rtime:
                # 未達成のミッション画像と名前.
                params['m%d' % idx] = missionmaster.image_pre
                params['mtext%d' % idx] = missionmaster.name
                is_allend = False
                continue
            elif max_time and rtime < max_time:
                continue
            elif max_time is None or max_time < rtime:
                max_time = rtime
                clearlist = []
            clearlist.append(str(idx))
        if not clearlist:
            self.osa_util.logger.error('You can not view the effect.')
            self.__sendErrorResponse(400)
            return
        params['clear'] = ','.join(clearlist)
        
        # 今回達成したミッションの画像と名前.
        for idx in clearlist:
            missionmaster = missionmaster_dict[int(idx) + 1]
            params['m%s' % idx] = missionmaster.image_pre
            params['mtext%s' % idx] = missionmaster.name
        
        if is_allend:
            # 獲得したカード画像と名前.
            prizelist = BackendApi.get_prizelist(model_mgr, panelmaster.prizes, using=using)
            if not prizelist:
                self.osa_util.logger.error('prize none.')
                self.__sendErrorResponse(400)
                return
            presentlist = BackendApi.create_present_by_prize(model_mgr, uid, prizelist, 0, using=using, do_set_save=False)
            presentset = PresentSet.presentToPresentSet(model_mgr, presentlist[:1], using=using)[0]
            params['card'] = presentset.itemthumbnail_middle
            params['cname'] = presentset.itemname
            
            # 次のパネル.
            next_panelmaster = BackendApi.get_panelmission_panelmaster(model_mgr, panel + 1, using=using)
            if next_panelmaster:
                next_panelmissionmaster_list = BackendApi.get_panelmission_missionmaster_by_panelid(model_mgr, next_panelmaster.id, using=using)
                for next_panelmissionmaster in next_panelmissionmaster_list:
                    idx = next_panelmissionmaster.number - 1
                    params['next%s' % idx] = next_panelmissionmaster.image_pre
        
        urldata = urlparse(self.url_cgi)
        url = '%s://%s%s' % (urldata.scheme, settings_sub.WEB_GLOBAL_HOST, urldata.path)
        url = url + UrlMaker.panelmissiontop()
        url = self.osa_util.makeLinkUrl(self.addTimeStamp(url))
        params['backUrl'] = url
        
        self.writeResponseBody(params)
    
    def proc_loginbonustimelimited(self, args):
        """期限付きログインボーナス.
        """
        mid = args.getInt(1)
        loginbonus = args.getInt(2)

        str_midlist = self.request.get(Defines.URLQUERY_ID) or ''
        midlist = [int(str_mid) for str_mid in str_midlist.split(',') if str_mid.isdigit()]
        
        model_mgr = self.getModelMgr()
        now = OSAUtil.get_now()
        
        master = BackendApi.get_loginbonustimelimitedmaster(model_mgr, mid, using=settings.DB_READONLY)
        if master is None:
            self.osa_util.logger.error('masterdata is not found.')
            self.__sendErrorResponse(400)
            return
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        if BackendApi.check_lead_loginbonustimelimited(model_mgr, v_player.id, now):
            # まだ受け取っていない.
            self.osa_util.logger.error('not received.')
            self.__sendErrorResponse(400)
            return
        
        logindata = BackendApi.get_logintimelimited_data(model_mgr, v_player.id, mid, using=settings.DB_READONLY)
        if logindata is None:
            self.osa_util.logger.error('logindata is None.')
            self.__sendErrorResponse(400)
            return
        
        # 表示するログインボーナスを選別(現在の日数のボーナスの前のボーナスから4つ表示したい).
        table = BackendApi.get_loginbonustimelimiteddaysmaster_day_table_by_timelimitedmid(model_mgr, mid, using=settings.DB_READONLY)
        
        params = {
            'pre' : self.url_static_img,
        }
        # 設定情報.
        config = BackendApi.get_current_loginbonustimelimitedconfig(model_mgr, using=settings.DB_READONLY)
        config_data = dict(config.getDataList()).get(master.id)
        
        making_functions = {
            'monthly_login' : self.__makeMonthlyLoginBonusParams,
        }
        func = making_functions.get(master.effectname, self.__makeCommonLoginBonusParams)
        tmp, cur_bonusmaster, next_bonusmaster = func(master, logindata, table, config_data)
        params.update(**tmp)
        
        #取得したアイテム(名前,日数).
        if cur_bonusmaster:
            params['td'] = cur_bonusmaster.day
            params['tt'] = self.getBonusItemText(cur_bonusmaster)
        else:
            # 演出いらない.
            self.osa_util.logger.error('can not view the effect.')
            self.__sendErrorResponse(400)
            return
        
        if next_bonusmaster:
            params['nt'] = self.getBonusItemText(next_bonusmaster)

        # 遷移先.
        url = None
        if mid in midlist:
            next_idx = midlist.index(mid)+1
            if next_idx < len(midlist):
                # 次がある.
                url = UrlMaker.loginbonustimelimitedanim(midlist[next_idx], loginbonus)
                url = OSAUtil.addQuery(url, Defines.URLQUERY_ID, str_midlist)
        if url is None:
            if loginbonus:
                # ログインボーナス.
                url = UrlMaker.loginbonusanim()
            else:
                url = LoginBonusHandler.getEffectBackUrl(self)

        anniversary_data = {}
        if master.effectname == 'countdown_login_2ndanniversary':
            anniversary_data = {
                'ten_digit': params['day'] / 10,
                'one_digit': params['day'] % 10,
            }
        elif master.effectname == 'countdown_login_3rdanniversary':
            anniversary_data = {
                'one_digit': params['day'] % 10,
                'predata': self.url_static + 'effect/sp/v2/countdown_login_3rdanniversary/data/'
            }
        params.update(anniversary_data)

        urldata = urlparse(self.url_cgi)
        urlhead = '%s://%s%s' % (urldata.scheme, settings_sub.WEB_GLOBAL_HOST, urldata.path)
        url = urlhead + url
        url = self.osa_util.makeLinkUrl(self.addTimeStamp(url))
        params['backUrl'] = url

        self.writeResponseBody(params)
    
    def __makeCommonLoginBonusParams(self, master, logindata, day_table, config_data):
        """共通のログインボーナス演出パラメータ.
        """
        VIEW_ITEM_NUM_MAX_TABLE = {
            Defines.LoginBonusTimeLimitedType.TOTAL : 4,
            Defines.LoginBonusTimeLimitedType.FIXATION : 6,
            Defines.LoginBonusTimeLimitedType.MONTHLY : 3,
        }
        VIEW_ITEM_NUM_MAX_TABLE_BY_EFFECTNAME = {
            'hinamatsuri_login' : 4,
            'countdown_login_2ndanniversary' : 4,
            'countdown_login_3rdanniversary' : 4,
            '2nd_anniversary_login' : 4,
            '3rd_anniversary_login' : 4,
            'valentine2016' : 6,
            'end_of_year_countdown' : 3,
            'newyear_login' : 7,
            'newbie_login' : 7,
        }
        item_num_max = VIEW_ITEM_NUM_MAX_TABLE_BY_EFFECTNAME.get(master.effectname, VIEW_ITEM_NUM_MAX_TABLE[master.lbtype])
        
        model_mgr = self.getModelMgr()
        
        cur_day = logindata.days
        params = {}
        cur_bonusmaster = None
        next_bonusmaster = None
        mid = master.id
        
        days = day_table.keys()
        days.sort()
        
        tmp_days = list(set(days + [cur_day]))
        tmp_days.sort()
        start = max(0, min(tmp_days.index(cur_day) - 1, len(days) - item_num_max))
        
        bonusmidlist = []
        has_next = False
        for day in days[start:]:
            if not day_table.has_key(day):
                continue
            elif len(bonusmidlist) == item_num_max:
                has_next = True
                break
            bonusmidlist.append(day_table[day])
        
        bonusmaster_list = BackendApi.get_loginbonustimelimiteddaysmaster_by_idlist(model_mgr, bonusmidlist, using=settings.DB_READONLY)
        
        params.update(has_next=has_next)
        
        if master.lbtype == Defines.LoginBonusTimeLimitedType.FIXATION:
            min_time = DateTimeUtil.strToDateTime(logindata.lbtltime.strftime("%Y%m01"), "%Y%m%d") - datetime.timedelta(seconds=1)
            min_time = DateTimeUtil.toLoginTime(min_time)
            receive_flags = BackendApi.get_loginbonustimelimited_fixation_received_dates(logindata.uid, mid, min_time).keys()
            
            params['logoPre'] = self.url_static + 'effect/sp/v2/%s/data/' % master.effectname
        else:
            params['logoPre'] = self.url_static + 'effect/sp/v2/%s/data/' % master.effectname
            receive_flags = None
        
        make_date_string = {
            Defines.LoginBonusTimeLimitedType.FIXATION : lambda x:u'%s月%s日' % (logindata.lbtltime.month, x),
            Defines.LoginBonusTimeLimitedType.MONTHLY : lambda x:u'%s日' % (logindata.lbtltime.month, x),
        }.get(master.lbtype, lambda x:'%d日目' % x)
        
        #アイテム一覧(日数と画像URL).
        bonusmaster_list.sort(key=lambda x:x.day)
        for idx, bonusmaster in enumerate(bonusmaster_list):
            params['i%d' % idx] = bonusmaster.thumb
            params['d%d' % idx] = bonusmaster.day
            params['date%d' % idx] = make_date_string(bonusmaster.day)
            if cur_day == bonusmaster.day:
                cur_bonusmaster = bonusmaster
                params['idx'] = idx
            elif cur_bonusmaster and not next_bonusmaster:
                next_bonusmaster = bonusmaster
            if receive_flags is not None:
                params['f%d' % idx] = 1 if bonusmaster.day in receive_flags else 0
        
        # 最終日までの日数.
        td = config_data['etime'] - logindata.lbtltime
        params['day'] = td.days
        
        if next_bonusmaster and 0 < td.days:
            params['idxnext'] = params['idx'] + 1
        if master.lbtype == Defines.LoginBonusTimeLimitedType.TOTAL:
            for i in xrange(params['idx']):
                params['f%d' % i] = 1
        
        def getEffectDBValue(attname, default):
            v = getattr(cur_bonusmaster, attname, '') if cur_bonusmaster else ''
            return v or default
        
        # 演出用文言.
        params['logo'] = master.logo
        params['preEffect'] = self.url_static_img + master.img_effect
        params['bg'] = getEffectDBValue(u'bg', u'bg.png')
        params['tlogo'] = getEffectDBValue(u'text_logo', master.text_logo)
        params['t0'] = getEffectDBValue(u'text_start', master.text_start)
        params['t1'] = getEffectDBValue(u'text_itemlist', master.text_itemlist)
        params['t2'] = getEffectDBValue(u'text_itemget', master.text_itemget)
        params['t3'] = getEffectDBValue(u'text_itemnext', master.text_itemnext)
        params['t4'] = getEffectDBValue(u'text_end', master.text_end)
        
        if cur_bonusmaster:
            params['ix'] = cur_bonusmaster.item_x
            params['iy'] = cur_bonusmaster.item_y
            params['gx'] = cur_bonusmaster.item_x
            params['gy'] = cur_bonusmaster.item_y
        
        return params, cur_bonusmaster, next_bonusmaster
    
    def __makeMonthlyLoginBonusParams(self, master, logindata, day_table, config_data):
        """月末ログインボーナス演出用パラメータ.
        """
        LOOP_CNT = 3
        ITEM_NUM_MAX = 3
        
        model_mgr = self.getModelMgr()
        
        mid = master.id
        cur_day = logindata.days
        params = {}
        
        params['logoPre'] = self.url_static + 'effect/sp/v2/monthly_login/data/default/'   # TODO: これをマスターデータで設定しないと.
        
        # 次の日.
        tomorrow = logindata.lbtltime + datetime.timedelta(days=1)
        
        # 月末はなんか特殊.
        bonusmaster_list = BackendApi.get_loginbonustimelimiteddaysmaster_by_idlist(model_mgr, day_table.values(), using=settings.DB_READONLY)
        bonusmaster_list.sort(key=lambda x:x.id)
        
        cur_bonusmaster = BackendApi.get_loginbonustimelimiteddaysmaster(model_mgr, mid, cur_day, using=settings.DB_READONLY)
        next_bonusmaster = None
        if config_data['stime'] <= tomorrow < config_data['etime']:
            # 次の日が期間内.
            next_bonusmaster = BackendApi.get_loginbonustimelimiteddaysmaster(model_mgr, mid, tomorrow.day, using=settings.DB_READONLY)
        
        cur_prizeid = cur_bonusmaster.prizes[0] if cur_bonusmaster and cur_bonusmaster.prizes else 0
        next_prizeid = next_bonusmaster.prizes[0] if next_bonusmaster and next_bonusmaster.prizes else 0
        
        prizeidlist = []
        for bonusmaster in bonusmaster_list:
            if not bonusmaster.prizes:
                continue
            prizeid = bonusmaster.prizes[0]
            if prizeid in prizeidlist:
                continue
            idx = len(prizeidlist)
            params['i%d' % idx] = bonusmaster.thumb
            prizeidlist.append(prizeid)
            if ITEM_NUM_MAX <= len(prizeidlist):
                break
        idx = prizeidlist.index(cur_prizeid)
        params['idx'] = idx
        if next_prizeid:
            params['idxnext'] = prizeidlist.index(next_prizeid)
        
        params['rouletteCnt'] = LOOP_CNT * ITEM_NUM_MAX + idx
        
        return params, cur_bonusmaster, next_bonusmaster
    
    def getBonusItemText(self, master):
        """ログインボーナスのテキストを作成
        """
        if LoginBonusTimeLimitedAnimationSet.exists(master.mid, master.day):
            items = LoginBonusTimeLimitedAnimationSet.get(master.mid, master.day)
        else:
            model_mgr = self.getModelMgr()
            prizelist = BackendApi.get_prizelist(model_mgr, master.prizes, using=settings.DB_READONLY)
            prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
            items = [listitem['text'] for listitem in prizeinfo['listitem_list']]
            LoginBonusTimeLimitedAnimationSet.save(master.mid, master.day, items)
        return Defines.STR_AND.join(items)
    
    #==============================================================
    # イベントシナリオ.
    def proc_eventscenario(self, args):
        """イベントシナリオ.
        """
        number = args.getInt(1)
        edt = args.get(2) or ''
        backUrl = '/'.join(args.args[3:])
        
        model_mgr = self.getModelMgr()
        data = BackendApi.get_eventscenario_by_number(model_mgr, number, using=settings.DB_READONLY)
        if not data:
            self.osa_util.logger.error('the scenario is not found...%s' % number)
            self.__sendErrorResponse(404)
            return
        
        urldata = urlparse(self.url_cgi)
        urlhead = '%s://%s%s' % (urldata.scheme, settings_sub.WEB_GLOBAL_HOST, urldata.path)
        url = '%s/%s' % (urlhead, backUrl)
        url = self.osa_util.makeLinkUrl(self.addTimeStamp(url))
        
        img_pre = self.url_static_img + (data.get('thumb') or 'event/scenario/%d/' % number)
        params = {
            'backUrl' : url,
            'pre' : img_pre,
            'edt' : edt,
        }
        params.update(data)
        self.writeResponseBody(params)
    
    #==============================================================
    # 双六.
    def proc_sugoroku(self, args):
        """双六ログイン.
        """
        mid = args.getInt(1)
        if mid is None:
            self.__sendErrorResponse(404)
            return
        page = args.getInt(2) or 0
        
        model_mgr = self.getModelMgr()
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        viewer_id = v_player.id
        # 結果情報を取得.
        logindata = BackendApi.get_loginbonus_sugoroku_playerdata(model_mgr, viewer_id, mid, using=settings.DB_DEFAULT)
        if logindata is None:
            self.__sendErrorResponse(404)
            return
        # 停まったマス.
        squares_id_list = logindata.result.get('square_id_list')
        squares_master_list = BackendApi.get_loginbonus_sugoroku_map_squares_master_list_by_id(model_mgr, squares_id_list, using=settings.DB_READONLY)
        squares_master_dict = dict([(squares_master.id, squares_master) for squares_master in squares_master_list])
        page_cnt = 0
        arr = []
        mapid = None
        for squares_id in squares_id_list:
            squares_master = squares_master_dict[squares_id]
            if mapid is None:
                mapid = squares_master.mid
            elif mapid != squares_master.mid:
                page_cnt += 1
                if page < page_cnt:
                    # 次のマップの分も入れておく.
                    arr.append(squares_master)
                    break
                mapid = squares_master.mid
            if page_cnt == page:
                arr.append(squares_master)
        squares_master_list = arr
        # マップ.
        mapmaster = BackendApi.get_loginbonus_sugoroku_map_master(model_mgr, mapid, using=settings.DB_READONLY)
        # 演出パラメータ.
        params = dict(
            backUrl = self.request.get('backUrl'),
            logoPre = self.url_static_img + 'sugo6/{}/'.format(mapmaster.effectname),
            pre = self.url_static_img,
            lt = 0,
        )
        # 報酬.
        prizeidlist_list = []
        message_items = []
        def get_prize_number(prizeidlist):
            if prizeidlist in prizeidlist_list:
                return prizeidlist_list.index(prizeidlist)
            else:
                prizeidlist_list.append(prizeidlist)
                return len(prizeidlist_list) - 1
        # 現在地.
        if 0 < page:
            params['continue'] = '1'
            params['cp'] = 0
        else:
            squares_master = squares_master_list.pop(0)
            params['cp'] = squares_master.number
            if len(squares_id_list) == 1:
                # 動いていない.
                if squares_master.last:
                    # 最終マス.
                    params['completeitem'] = get_prize_number(mapmaster.prize)
                    message_items.append(params['completeitem'])
                else:
                    # 休み.
                    params['lt'] = logindata.lose_turns + 1
        # マップ情報.
        map_squares_master_list = BackendApi.get_loginbonus_sugoroku_map_squares_master_by_mapid(model_mgr, mapid, using=settings.DB_READONLY)
        for squares_master in map_squares_master_list:
            number = squares_master.number
            params['et{}'.format(number)] = squares_master.event_type
            params['ev{}'.format(number)] = squares_master.event_value
            if squares_master.prize:
                params['ei{}'.format(number)] = get_prize_number(squares_master.prize)
        # 停まったマス.
        params['pn'] = len(squares_master_list)
        pre_event_type = Defines.SugorokuMapEventType.NONE
        for i,squares_master in enumerate(squares_master_list):
            if squares_master.mid == mapid:
                params['p{}'.format(i)] = squares_master.number
                if squares_master.prize:
                    message_items.append(get_prize_number(squares_master.prize))
            elif pre_event_type == Defines.SugorokuMapEventType.BACK:
                # 戻って前のマップへ.
                pre_map_squares_master_list = BackendApi.get_loginbonus_sugoroku_map_squares_master_by_mapid(model_mgr, squares_master.mid, using=settings.DB_READONLY)
                params['p{}'.format(i)] = squares_master.number - len(pre_map_squares_master_list)
            else:
                # 進んで次のマップへ.
                params['p{}'.format(i)] = len(map_squares_master_list) + squares_master.number
            pre_event_type = squares_master.event_type
        # アイテム.
        params['in'] = len(prizeidlist_list)
        for i,prizeidlist in enumerate(prizeidlist_list):
            # アイテム画像.
            if i in message_items:
                prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY)
                prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
                # アイテム名.
                params['in{}'.format(i)] = Defines.STR_AND.join([listitem['text'] for listitem in prizeinfo['listitem_list']])
            else:
                prizelist = BackendApi.get_prizelist(model_mgr, [prizeidlist[0]], using=settings.DB_READONLY)
                prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
            # アイテム画像.
            params['i{}'.format(i)] = prizeinfo['listitem_list'][0]['thumbUrl'].replace(params['pre'], '')
        self.writeResponseBody(params)

def main(request):
    return Handler.run(request)
