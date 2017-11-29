# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerTutorial, PlayerGold,\
    PlayerExp, PlayerAp, PlayerFriend
from defines import Defines
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.lib.opensocial.util import OSAUtil
import settings
from copy import copy
from platinumegg.app.cabaret.models.Card import CardAcquisition
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.app.cabaret.util.scout import ScoutEventGetCard, ScoutExec,\
    ScoutEventGetTreasure, ScoutEventComplete
from platinumegg.app.cabaret.util.item import ItemUtil
from platinumegg.app.cabaret.util.redisdb import MemoriesSession
from platinumegg.app.cabaret.util.battle import BossBattleAnimParam

class Handler(AppHandler):
    """チュートリアル.
    """
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold, PlayerExp, PlayerAp, PlayerFriend]
    
    def process(self):
        args = self.getUrlArgs('/tutorial/')
        if args.get(0) == '1':
            # skip.
            self.procSkip()
            return
        
        self.__cur_state = self.getCurrentTutoState()
        if self.__cur_state is None:
            self.redirectToTop()
            return
        chapter = Handler.tutoStateToChapterState(self.__cur_state)
        
        table = {
            Defines.TutorialStatus.CHAPTER_EVOL00 : self.procEvolution,
#            Defines.TutorialStatus.CHAPTER_SCOUT00 : self.procScout,
            Defines.TutorialStatus.CHAPTER_SCOUT01 : self.procScout,
#            Defines.TutorialStatus.CHAPTER_SCOUT02 : self.procScout,
            Defines.TutorialStatus.CHAPTER_SCOUT03 : self.procScout,
            Defines.TutorialStatus.CHAPTER_BOSS00 : self.procBoss,
            Defines.TutorialStatus.CHAPTER_COMPOSITION00 : self.procComposition,
            Defines.TutorialStatus.CHAPTER_BOSS01 : self.procBoss,
            Defines.TutorialStatus.CHAPTER_COMPLETE : self.procComplete,
        }
        func = table.get(chapter, None)
        if func is None:
            self.redirectToTop()
            return
        
        self.updateTutoState(self.__cur_state)
        
        if not self.__cur_state in Defines.TutorialStatus.ANIMATIONS:
            self.html_param['is_tutorial'] = True
            self.html_param['tutorial_title'] = Defines.TutorialStatus.NAMES[self.__cur_state]
            self.html_param['tutorial_page'] = Defines.TutorialStatus.FLOW_EXCLUDE_ANIMATIONS.index(self.__cur_state) + 1
            self.html_param['tutorial_page_max'] = len(Defines.TutorialStatus.FLOW_EXCLUDE_ANIMATIONS)
            self.html_param['tutorial_state'] = self.__cur_state
            if not self.html_param.get('is_staging'):
                self.html_param['url_tutorial_skip'] = self.makeAppLinkUrl(UrlMaker.tutorial(True))
        func()
    
    #=================================================================
    # ハメ管理合成.
    def procEvolution(self):
        if not self.checkPlayer():
            return
        table = {
#            Defines.TutorialStatus.EVOL00_BASESELECT : self.proc_EVOL00_BASESELECT, #ハメ管理ベース選択.
#            Defines.TutorialStatus.EVOL00_MATERIAL : self.proc_EVOL00_MATERIAL,     #ハメ管理素材選択.
            Defines.TutorialStatus.EVOL00_YESNO : self.proc_EVOL00_YESNO,           #ハメ管理合成確認.
            Defines.TutorialStatus.EVOL00_ANIM : self.proc_EVOL00_ANIM,             #ハメ管理アニメーション.
            Defines.TutorialStatus.EVOL00_COMPLETE : self.proc_EVOL00_COMPLETE,     #ハメ管理合成結果.
            Defines.TutorialStatus.EVOL00_ALBUM : self.proc_EVOL00_ALBUM,           #思い出アルバム.
        }
        
        # ベースカード.
        basecard = self.getLeaderCard()
        # 素材カード.
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer(True)
        materialcard = BackendApi.get_tutorialevolution_material(model_mgr, v_player.id, using=settings.DB_READONLY)
        
        table.get(self.__cur_state, self.proc_EVOL00_YESNO)(basecard, materialcard)
    
    def makeCompositionObjCardList(self, basecard, materialcard):
        obj_cardlist = []
        url_next = self.makeAppLinkUrl(self.makeUrlNext())
        for cardset in (basecard, materialcard):
            obj_card = Objects.card(self, cardset)
            obj_card['url_composition'] = url_next
            obj_card['url_evolution'] = url_next
            obj_cardlist.append(obj_card)
        return obj_cardlist
    
    def proc_EVOL00_BASESELECT(self, basecard, materialcard):
        """ベースカード選択.
        """
        obj_cardlist = self.makeCompositionObjCardList(basecard, materialcard)
        obj_basecard, obj_materialcard = obj_cardlist
        self.html_param['cardlist'] = [obj_basecard] + [obj_materialcard] * (Defines.HKLEVEL_MAX - 1)
        self.html_param['cardnum'] = len(self.html_param['cardlist'])
        
        self.html_param['cur_page'] = 1
        self.html_param['page_max'] = 1
        
        self.putPlayerInfo()
        
        self.writeAppHtml('evolution/baseselect')
    
    def proc_EVOL00_MATERIAL(self, basecard, materialcard):
        """素材カード選択.
        """
        obj_cardlist = self.makeCompositionObjCardList(basecard, materialcard)
        self.html_param['basecard'] = obj_cardlist[0]
        self.html_param['cardlist'] = obj_cardlist[1:]
        self.html_param['cardnum'] = len(obj_cardlist)
        
        self.html_param['cur_page'] = 1
        self.html_param['page_max'] = 1
        
        self.putPlayerInfo()
        self.writeAppHtml('evolution/materialselect')
    
    def proc_EVOL00_YESNO(self, basecard, materialcard):
        """ハメ管理確認.
        """
        obj_cardlist = self.makeCompositionObjCardList(basecard, materialcard)
        self.html_param['basecard'] = obj_cardlist[0]
        self.html_param['materialcardlist'] = [obj_cardlist[1]] * (Defines.HKLEVEL_MAX - 1)
        self.html_param['cardnum'] = len(obj_cardlist)
        
        self.html_param['url_do'] = self.makeAppLinkUrl(self.makeUrlNext())
        
        self.putPlayerInfo()
        self.writeAppHtml('evolution/yesno')
    
    def proc_EVOL00_ANIM(self, basecard, materialcard):
        """ハメ管理合成アニメーション.
        """
        model_mgr = self.getModelMgr()
        params = {
            'card1':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(basecard.master)),
            'card2':self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(materialcard.master)),
            'startText':Defines.EffectTextFormat.EVOLUTION_STARTTEXT,
            'backUrl':self.makeAppLinkUrl(self.makeUrlNext()),
        }
        basecard_post, _ = BackendApi.tutorial_evolution(model_mgr, basecard, materialcard, using=settings.DB_READONLY)
        params['mixCard'] = self.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlMiddle(basecard_post.master))
        params['endText'] = Defines.EffectTextFormat.EVOLUTION_ENDTEXT % (basecard_post.master.name, basecard_post.master.hklevel - 1, basecard_post.card.takeover)
        params['endText2'] = Defines.EffectTextFormat.EVOLUTION_ENDTEXT2 % basecard_post.master.maxlevel
        params['endText3'] = Defines.EffectTextFormat.EVOLUTION_ENDTEXT3_MOVIE
        
        v_player = self.getViewerPlayer(True)
        mid = basecard_post.master.id
        if self.is_pc:
            memoriesmaster = BackendApi.get_tutorial_pcmemories(model_mgr, v_player.ptype, using=settings.DB_READONLY)
        else:
            memoriesmaster = BackendApi.get_tutorial_memories(model_mgr, v_player.ptype, using=settings.DB_READONLY)
        card_acquisition = CardAcquisition.makeInstance(CardAcquisition.makeID(basecard_post.card.uid, mid))
        
        obj_memories = Objects.memoriesmaster(self, memoriesmaster, card_acquisition)
        params['miniCard1'] = obj_memories['thumbUrl']
        
        self.appRedirectToEffect('gousei/effect.html', params)
    
    def proc_EVOL00_COMPLETE(self, basecard, materialcard):
        """ハメ管理完了.
        """
        model_mgr = self.getModelMgr()
        basecard_post, _ = BackendApi.tutorial_evolution(model_mgr, basecard, materialcard, using=settings.DB_READONLY)
        obj_basecard_post = Objects.card(self, basecard_post)
        obj_basecard_post['master']['url_album'] = self.makeAppLinkUrl(self.makeUrlNext())
        self.html_param['basecard_post'] = obj_basecard_post
        
        self.writeAppHtml('evolution/complete')
    
    def proc_EVOL00_ALBUM(self, basecard, materialcard):
        """思い出アルバム.
        """
        model_mgr = self.getModelMgr()
        
        basecard_post, _ = BackendApi.tutorial_evolution(model_mgr, basecard, materialcard, using=settings.DB_READONLY)
        
        v_player = self.getViewerPlayer(True)
        mid = basecard_post.master.id
        memoriesmaster = None
        if self.is_pc:
            memoriesmaster = BackendApi.get_tutorial_pcmemories(model_mgr, v_player.ptype, using=settings.DB_READONLY)
        else:
            memoriesmaster = BackendApi.get_tutorial_memories(model_mgr, v_player.ptype, using=settings.DB_READONLY)
        card_acquisition = CardAcquisition.makeInstance(CardAcquisition.makeID(basecard_post.card.uid, mid))
        
        self.html_param['cardmaster'] = Objects.cardmaster(self, basecard_post.master)
        self.html_param['album'] = Objects.memoriesmaster(self, memoriesmaster, card_acquisition)
        
        memories_list = []
        movie_list = []
        pcmovie_list = []
        for obj_memories in BackendApi.get_album_memories_list(self, basecard_post.card.uid, basecard_post.master.album, using=settings.DB_READONLY):
            if obj_memories['contenttype'] == Defines.MemoryContentType.MOVIE:
                movie_list.append(obj_memories)
            elif obj_memories['contenttype'] == Defines.MemoryContentType.MOVIE_PC:
                pcmovie_list.append(obj_memories)
            else:
                memories_list.append(obj_memories)
        self.html_param['memories_list'] = memories_list
        self.html_param['movie_list'] = movie_list
        self.html_param['pcmovie_list'] = pcmovie_list
        
        self.html_param['url_next'] = self.makeAppLinkUrl(self.makeUrlNext())
        
        # 動画閲覧用のキーを保存.
        remote_addr = self.request.remote_addr
        if remote_addr:
            key = '%s##%s' % (remote_addr, self.osa_util.useragent.browser)
            MemoriesSession.create(v_player.id, memoriesmaster.id, key).save()
        
        self.writeAppHtml('album/memories')
    
    #=================================================================
    # スカウト.
    def procScout(self):
        """スカウト.
        """
        if not self.checkPlayer():
            return
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer(True)
        # エリア.
        area = BackendApi.get_tutorial_area(model_mgr, v_player.ptype, using=settings.DB_READONLY)
        # スカウト.
        scout = BackendApi.get_tutorial_scout(model_mgr, v_player.ptype, using=settings.DB_READONLY)
        scout = copy(scout)
        scout.execution = Defines.TutorialStatus.SCOUT_CHAPTER_NUM
        
        table = {
#            Defines.TutorialStatus.SCOUT00_TOP : (self.proc_SCOUT00_TOP, 0),
#            Defines.TutorialStatus.SCOUT00_ANIM : (self.proc_SCOUT00_ANIM, 1),
#            Defines.TutorialStatus.SCOUT00_CARDGET : (self.proc_SCOUT00_CARDGET, 1),
            Defines.TutorialStatus.SCOUT01_TOP : (self.proc_SCOUT00_TOP, 0),
            Defines.TutorialStatus.SCOUT01_ANIM : (self.proc_SCOUT01_ANIM, 0),
            Defines.TutorialStatus.SCOUT01_CARDGET : (self.proc_SCOUT01_CARDGET, 0),
#            Defines.TutorialStatus.SCOUT02_ANIM : (self.proc_SCOUT02_ANIM, 2),
#            Defines.TutorialStatus.SCOUT02_RESULT : (self.proc_SCOUT02_RESULT, 2),
            Defines.TutorialStatus.SCOUT03_ANIM : (self.proc_SCOUT03_ANIM, scout.execution),
            Defines.TutorialStatus.SCOUT03_RESULTANIM : (self.proc_SCOUT03_RESULTANIM, scout.execution),
            Defines.TutorialStatus.SCOUT03_BOSS : (self.proc_SCOUT03_BOSS, scout.execution),
        }
        
        func, cnt = table[self.__cur_state]
        
        func(area, scout, cnt)
    
    def proc_SCOUT00_TOP(self, area, scout, scout_cnt):
        """スカウトTop.
        """
        v_player = self.getViewerPlayer(True)
        
        self.html_param['area'] = Objects.area(self, area, None)
        
        obj_scout = Objects.scout(self, v_player, scout, scout_cnt, [])
        obj_scout['url_exec'] = self.makeAppLinkUrl(self.makeUrlNext())
        self.html_param['scoutlist'] = [obj_scout]
        
        self.putPlayerInfo(scout_cnt=scout_cnt)
        self.writeAppHtml('scout/scout')
    
    def __putScoutAnimation(self, scout, eventlist, scout_cnt, **kwargs):
        """スカウト演出を出力.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer(True)
        
        if 1 < scout_cnt:
            self.reflectScoutResult(scout_cnt-1)
        gold_add, exp_add = BackendApi.get_tutorial_scoutresult(model_mgr, v_player.ptype, using=settings.DB_READONLY)
        apmax = v_player.get_ap_max()
        
        result_obj = ScoutExec.makeResultObject(v_player.level,
                                         v_player.exp, v_player.exp + exp_add, exp_add,
                                         gold_add,
                                         apmax, apmax, apmax, 0,
                                         scout_cnt - 1, scout_cnt, scout.execution)
        params = BackendApi.make_scoutanim_params(self, scout, eventlist, [result_obj])
        
        params['backUrl'] = self.makeAppLinkUrl(self.makeUrlNext())
        
        params.update(kwargs)
        
        self.appRedirectToEffect('scout/effect.html', params)
    
    def proc_SCOUT00_ANIM(self, area, scout, scout_cnt):
        """スカウト実行アニメーション(カード獲得).
        """
        eventlist = [
            ScoutEventGetCard.create(0),
        ]
        self.__putScoutAnimation(scout, eventlist, scout_cnt)
    
    def proc_SCOUT00_CARDGET(self, area, scout, scout_cnt):
        """スカウト実行アニメーション(スカウト成功).
        """
        v_player = self.getViewerPlayer(True)
        card = self.getLeaderCard()
        
        obj_scout = Objects.scout(self, v_player, scout, scout_cnt, [])
        obj_scout['url_exec'] = self.makeAppLinkUrl(self.makeUrlNext())
        self.html_param['scout'] = obj_scout
        self.html_param['card'] = Objects.card(self, card, is_new=True)
        
        self.putPlayerInfo(scout_cnt=scout_cnt)
        
        self.writeAppHtml('scout/cardgetresult_success')
    
    def proc_SCOUT01_ANIM(self, area, scout, scout_cnt):
        """スカウト実行アニメーション(カード獲得).
        """
        eventlist = [
            ScoutEventGetCard.create(0),
        ]
        self.__putScoutAnimation(scout, eventlist, scout_cnt)
    
    def proc_SCOUT01_CARDGET(self, area, scout, scout_cnt):
        """スカウト実行アニメーション(スカウト成功).
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer(True)
        card = BackendApi.get_tutorial_scoutdropcard(model_mgr, v_player.ptype, using=settings.DB_READONLY)
        
        obj_scout = Objects.scout(self, v_player, scout, scout_cnt, [])
        obj_scout['url_exec'] = self.makeAppLinkUrl(self.makeUrlNext())
        self.html_param['scout'] = obj_scout
        self.html_param['card'] = Objects.card(self, card, is_new=True)
        
        self.putPlayerInfo(scout_cnt=scout_cnt)
        
        self.writeAppHtml('scout/cardgetresult_success')
    
    def proc_SCOUT02_ANIM(self, area, scout, scout_cnt):
        """スカウト実行アニメーション(宝箱獲得).
        """
        treasure_type = Defines.TreasureType.TUTORIAL_TREASURETYPE
        eventlist = [
            ScoutEventGetTreasure.create(treasure_type),
        ]
        eventImage = self.makeAppLinkUrlImg(ItemUtil.makeThumbnailUrlMiddleByTreasureType(treasure_type))
        self.__putScoutAnimation(scout, eventlist, scout_cnt, eventImage=eventImage)
    
    def proc_SCOUT02_RESULT(self, area, scout, scout_cnt):
        """宝箱獲得結果.
        """
        v_player = self.getViewerPlayer(True)
        
        self.html_param['area'] = Objects.area(self, area, None)
        self.html_param['scout'] = Objects.scout(self, v_player, scout, scout_cnt, [])
        self.html_param['url_next'] = self.makeAppLinkUrl(self.makeUrlNext())
        self.html_param['treasure_view'] = Objects.treasure_view(self, Defines.TreasureType.SILVER)
        
        self.putPlayerInfo(scout_cnt=scout_cnt)
        
        self.writeAppHtml('scout/treasureget')
    
    def proc_SCOUT03_ANIM(self, area, scout, scout_cnt):
        """スカウト実行アニメーション(スカウト完了).
        """
        eventlist = [
            ScoutEventComplete.create(scout.id),
        ]
        self.__putScoutAnimation(scout, eventlist, scout_cnt)
    
    def proc_SCOUT03_RESULTANIM(self, area, scout, scout_cnt):
        """スカウト完了.
        """
        params = {
            'backUrl':self.makeAppLinkUrl(self.makeUrlNext()),
            'text' : Defines.EffectTextFormat.SCOUTRESULT_COMPLETE_TEXT,
        }
        self.appRedirectToEffect('scoutclear/effect.html', params)
    
    def proc_SCOUT03_BOSS(self, area, scout, scout_cnt):
        """ボス出現.
        """
        params = {
            'backUrl' : self.makeAppLinkUrl(self.makeUrlNext()),
        }
        self.appRedirectToEffect('bossencount/effect.html', params)
    
    #=================================================================
    # ボス戦.
    def procBoss(self):
        """ボス戦.
        """
        if not self.checkPlayer():
            return
        
        table = {
            Defines.TutorialStatus.BOSS00_PRE : self.proc_BOSS00_PRE,
            Defines.TutorialStatus.BOSS00_ANIM : self.proc_BOSS00_ANIM,
            Defines.TutorialStatus.BOSS00_RESULT : self.proc_BOSS00_RESULT,
            Defines.TutorialStatus.BOSS01_PRE : self.proc_BOSS01_PRE,
            Defines.TutorialStatus.BOSS01_ANIM : self.proc_BOSS01_ANIM,
            Defines.TutorialStatus.BOSS01_RESULT : self.proc_BOSS01_RESULT,
        }
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer(True)
        
        # エリア.
        area = BackendApi.get_tutorial_area(model_mgr, v_player.ptype, using=settings.DB_READONLY)
        # ボス.
        boss = BackendApi.get_boss(model_mgr, area.boss, using=settings.DB_READONLY)
        # デッキ.
        deck = BackendApi.get_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
        cardlist = BackendApi.get_cards(deck.to_array(), model_mgr, using=settings.DB_READONLY)
        leader = cardlist[0]
        members = cardlist[1:]
        evol_materialcard = BackendApi.get_tutorialevolution_material(model_mgr, v_player.id, using=settings.DB_READONLY)
        leader, _ = BackendApi.tutorial_evolution(model_mgr, leader, evol_materialcard, using=settings.DB_READONLY)
        if Handler.tutoStateToChapterState(self.__cur_state) ==  Defines.TutorialStatus.CHAPTER_BOSS01:
            # 教育も済.
            materialcard = BackendApi.get_tutorialcomposition_material(model_mgr, v_player.ptype, using=settings.DB_READONLY)
            BackendApi.composition(model_mgr, leader, [materialcard], False, using=settings.DB_READONLY)
        deckcardlist = [leader] + members
        
        table[self.__cur_state](area, boss, deckcardlist)
    
    def __getBossHp(self, boss, is_win):
        """BOSSの残りHP.
        """
        if is_win:
            hp_post = 0
        else:
            hp_post = int(boss.hp * 16 / 100)   # 適当..
        return hp_post
    
    def __putBossResultDeck(self, deckcardlist):
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
    
    def __putBossBattleAnimation(self, is_win, boss, cardlist):
        """ボス戦演出を出力.
        """
        hp_pre = boss.hp
        hp_post = self.__getBossHp(boss, is_win)
        damage = hp_pre - hp_post
        
        power = 0
        for cardset in cardlist:
            power += cardset.power
        
        animdata = BossBattleAnimParam.create(power, power, cardlist, [], damage, hp_pre, hp_post, hp_pre, critical=False)
        params = BackendApi.make_bossbattle_animation_params(self, animdata, boss.thumb)
        params['backUrl'] = self.makeAppLinkUrl(self.makeUrlNext())
        
        self.appRedirectToEffect('bossbattle2/effect.html', params)
    
    def proc_BOSS00_PRE(self, area, boss, deckcardlist):
        """ボス戦確認.
        """
        self.html_param['area'] = Objects.area(self, area, None)
        self.html_param['boss'] = Objects.boss(self, boss)
        self.__putBossResultDeck(deckcardlist)
        self.html_param['url_bossbattle'] = self.makeAppLinkUrl(self.makeUrlNext())
        
        self.writeAppHtml('boss/bosspre')
    
    def proc_BOSS00_ANIM(self, area, boss, deckcardlist):
        """ボス戦アニメーション.
        """
        self.__putBossBattleAnimation(False, boss, deckcardlist)
    
    def proc_BOSS00_RESULT(self, area, boss, deckcardlist):
        """ボス戦結果 敗北.
        """
        self.html_param['area'] = Objects.area(self, area, None)
        self.html_param['boss'] = Objects.boss(self, boss, self.__getBossHp(boss, False))
        self.__putBossResultDeck(deckcardlist)
        self.html_param['url_composition_material'] = self.makeAppLinkUrl(self.makeUrlNext())
        
        self.writeAppHtml('boss/bosslose')
    
    def proc_BOSS01_PRE(self, area, boss, deckcardlist):
        """ボス戦確認.
        """
        self.html_param['area'] = Objects.area(self, area, None)
        self.html_param['boss'] = Objects.boss(self, boss)
        self.__putBossResultDeck(deckcardlist)
        self.html_param['url_bossbattle'] = self.makeAppLinkUrl(self.makeUrlNext())
        
        self.writeAppHtml('tutorial/boss_tuto2')
    
    def proc_BOSS01_ANIM(self, area, boss, deckcardlist):
        """ボス戦アニメーション.
        """
        self.__putBossBattleAnimation(True, boss, deckcardlist)
    
    def proc_BOSS01_RESULT(self, area, boss, deckcardlist):
        """ボス戦結果 勝利.
        """
        
        model_mgr = self.getModelMgr()
        prizelist = BackendApi.get_prizelist(model_mgr, area.prizes, using=settings.DB_READONLY)
        
        self.html_param['area'] = Objects.area(self, area, None)
        self.html_param['boss'] = Objects.boss(self, boss, self.__getBossHp(boss, True))
        self.__putBossResultDeck(deckcardlist)
        self.html_param['prize'] = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
        self.html_param['url_next'] = self.makeAppLinkUrl(self.makeUrlNext())
        
        self.writeAppHtml('boss/bosswin')
    
    #=================================================================
    # 教育.
    def procComposition(self):
        """教育.
        """
        if not self.checkPlayer():
            return
        
        table = {
#            Defines.TutorialStatus.COMPOSITION00_BASESELECT : self.proc_COMPOSITION00_BASESELECT,
#            Defines.TutorialStatus.COMPOSITION00_MATERIAL : self.proc_COMPOSITION00_MATERIAL,
            Defines.TutorialStatus.COMPOSITION00_YESNO : self.proc_COMPOSITION00_YESNO,
            Defines.TutorialStatus.COMPOSITION00_ANIM : self.proc_COMPOSITION00_ANIM,
            Defines.TutorialStatus.COMPOSITION00_COMPLETE : self.proc_COMPOSITION00_COMPLETE,
        }
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer(True)
        
        # リーダーカード.
        leader = BackendApi.get_leaders([v_player.id], model_mgr, using=settings.DB_READONLY).get(v_player.id)
        evol_materialcard = BackendApi.get_tutorialevolution_material(model_mgr, v_player.id, using=settings.DB_READONLY)
        leader, _ = BackendApi.tutorial_evolution(model_mgr, leader, evol_materialcard, using=settings.DB_READONLY)
        
        # 素材カード.
        materialcard = BackendApi.get_tutorialcomposition_material(model_mgr, v_player.ptype, using=settings.DB_READONLY)
        
        table[self.__cur_state](leader, materialcard)
    
    def proc_COMPOSITION00_BASESELECT(self, basecard, materialcard):
        """ベースカード選択.
        """
        obj_cardlist = self.makeCompositionObjCardList(basecard, materialcard)
        self.html_param['cardlist'] = obj_cardlist
        self.html_param['cardnum'] = len(obj_cardlist)
        
        self.html_param['cur_page'] = 1
        self.html_param['page_max'] = 1
        
        self.putPlayerInfo(scout_cnt=Defines.TutorialStatus.SCOUT_CHAPTER_NUM)
        self.writeAppHtml('composition/baseselect')
    
    def proc_COMPOSITION00_MATERIAL(self, basecard, materialcard):
        """素材カード選択.
        """
        obj_cardlist = self.makeCompositionObjCardList(basecard, materialcard)
        self.html_param['basecard'] = obj_cardlist[0]
        self.html_param['cardlist'] = obj_cardlist[1:]
        self.html_param['cardnum'] = len(obj_cardlist)
        
        self.html_param['cur_page'] = 1
        self.html_param['page_max'] = 1
        
        self.html_param['url_yesno'] = self.makeAppLinkUrl(self.makeUrlNext())
        
        self.putPlayerInfo(scout_cnt=Defines.TutorialStatus.SCOUT_CHAPTER_NUM)
        
        self.writeAppHtml('composition/materialselect')
    
    def proc_COMPOSITION00_YESNO(self, basecard, materialcard):
        """確認.
        """
        obj_cardlist = self.makeCompositionObjCardList(basecard, materialcard)
        self.html_param['basecard'] = obj_cardlist[0]
        self.html_param['cardlist'] = obj_cardlist[1:]
        self.html_param['cardnum'] = len(obj_cardlist)
        
        self.html_param['url_do'] = self.makeAppLinkUrl(self.makeUrlNext())
        
        self.putPlayerInfo(scout_cnt=Defines.TutorialStatus.SCOUT_CHAPTER_NUM)
        self.writeAppHtml('composition/yesno')
    
    def proc_COMPOSITION00_ANIM(self, basecard, materialcard):
        """教育演出.
        """
        model_mgr = self.getModelMgr()
        exp_pre = 0
        level_pre = basecard.card.level
        exp_add, _, level_add = BackendApi.composition(model_mgr, basecard, [materialcard], False, using=settings.DB_READONLY)
        
        params = BackendApi.make_composition_effectparams(self, basecard, [materialcard], exp_pre, exp_add, level_pre, level_add, 0, False)
        params['backUrl'] = self.makeAppLinkUrl(self.makeUrlNext())
        
        self.appRedirectToEffect('education/effect.html', params)
    
    def proc_COMPOSITION00_COMPLETE(self, basecard, materialcard):
        """教育結果.
        """
        model_mgr = self.getModelMgr()
        pre_level = basecard.card.level
        pre_power = basecard.power
        BackendApi.composition(model_mgr, basecard, [materialcard], False, using=settings.DB_READONLY)
        obj_card = Objects.card(self, basecard)
        self.html_param['basecard_post'] = obj_card
        self.html_param['url_next'] = self.makeAppLinkUrl(self.makeUrlNext())
        self.html_param['power_add'] = obj_card['power'] - pre_power
        self.html_param['level_add'] = obj_card['level'] - pre_level
        self.html_param['skilllevel_add'] = 0
        
        self.writeAppHtml('composition/complete')
    
    #=================================================================
    # 完了.
    def procComplete(self):
        """まとめと報酬受取.
        """
        table = {
            Defines.TutorialStatus.COMPLETE_HOWTOCABA : self.proc_COMPLETE_HOWTOCABA,
            Defines.TutorialStatus.COMPLETE_MATOME : self.proc_COMPLETE_MATOME,
            Defines.TutorialStatus.COMPLETED : self.proc_COMPLETED,
        }
        table[self.__cur_state]()

    def proc_COMPLETE_HOWTOCABA(self):
        """まとめ.
        """
        self.html_param['url_next'] = self.makeAppLinkUrl(self.makeUrlNext())
        self.writeAppHtml('tutorial/howtocaba')
    
    def proc_COMPLETE_MATOME(self):
        """まとめ.
        """
        self.html_param['url_next'] = self.makeAppLinkUrl(self.makeUrlNext())
        self.writeAppHtml('tutorial/matome')
    
    def proc_COMPLETED(self):
        """完了報酬.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer(True)
        prizelist = BackendApi.get_tutorial_prizelist(model_mgr, v_player.ptype, using=settings.DB_READONLY)
        self.html_param['prize'] = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
        self.writeAppHtml('tutorial/complete')
    
    #=================================================================
    # スキップ.
    def procSkip(self):
        """チュートリアルをスキップ.
        """
        # チュートリアル完了にする.
        self.updateTutoState(Defines.TutorialStatus.COMPLETED)
        
        # 報酬受取へ.
        url = OSAUtil.addQuery(UrlMaker.tutorial(), Defines.URLQUERY_TUTO, Defines.TutorialStatus.COMPLETED)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    #=================================================================
    def checkPlayer(self, end=False):
        v_player = self.getViewerPlayer(True)
        if v_player.getModel(PlayerTutorial) is None:
            pass
        elif end and not (v_player.tutorialstate in (Defines.TutorialStatus.COMPLETED, Defines.TutorialStatus.COMPLETE_MATOME)):
            pass
        elif not end and v_player.tutorialstate == Defines.TutorialStatus.COMPLETED:
            pass
        else:
            return True
        
        self.redirectToTop()
        return False
    
    def reflectScoutResult(self, scout_cnt):
        v_player = self.getViewerPlayer(True)
        
        if 0 < scout_cnt:
            model_mgr = self.getModelMgr()
            # 実行回数分のステータスを加算.
            gold, exp = BackendApi.get_tutorial_scoutresult(model_mgr, v_player.ptype, scout_cnt, using=settings.DB_READONLY)
            v_player.gold = gold
            BackendApi.set_exp(model_mgr, v_player, exp, using=settings.DB_READONLY)
        return v_player
    
    def putPlayerInfo(self, person=None, leader=None, scout_cnt=0):
        
        self.reflectScoutResult(scout_cnt)
        
        v_player = self.getViewerPlayer(True)
        
        self.html_param['player'] = Objects.player(self, v_player, person, leader)
    
    def getLeaderCard(self, evolution=False, composition=False):
        """リーダーカード.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer(True)
        leader = BackendApi.get_leaders([v_player.id], model_mgr, using=settings.DB_READONLY).get(v_player.id)
        if evolution:
            evol_materialcard = BackendApi.get_tutorialevolution_material(model_mgr, v_player.id, using=settings.DB_READONLY)
            leader, _ = BackendApi.tutorial_evolution(model_mgr, leader, evol_materialcard, using=settings.DB_READONLY)
            if composition:
                material = BackendApi.get_tutorialcomposition_material(model_mgr, v_player.ptype, using=settings.DB_READONLY)
                BackendApi.composition(model_mgr, leader, [material], False, using=settings.DB_READONLY)
        return leader
    
    @staticmethod
    def tutoStateToChapterState(tutostate):
        if tutostate == Defines.TutorialStatus.COMPLETED:
            return Defines.TutorialStatus.CHAPTER_COMPLETE
        return tutostate & 0xff00
    
    def getCurrentTutoState(self):
        v_player = self.getViewerPlayer(True)
        if v_player is None:
            return None
        playertutorial = v_player.getModel(PlayerTutorial)
        if playertutorial is None:
            return None
        
        chapter = Handler.tutoStateToChapterState(playertutorial.tutorialstate)
        tutostate = self.request.get(Defines.URLQUERY_TUTO, '')
        if tutostate.isdigit():
            tutostate = int(tutostate)
            if not tutostate in (playertutorial.tutorialstate, self.toNextState(playertutorial.tutorialstate)):
                tutostate = playertutorial.tutorialstate
        elif playertutorial.tutorialstate == Defines.TutorialStatus.COMPLETED:
            # すでに終わっている.
            return None
        else:
            tutostate = chapter
        if Handler.tutoStateToChapterState(tutostate) == Defines.TutorialStatus.CHAPTER_REGIST:
            tutostate = self.toNextState(Defines.TutorialStatus.REGIST_COMPLETE)
        return tutostate
    
    def toNextState(self, state):
        if state in (Defines.TutorialStatus.COMPLETED, Defines.TutorialStatus.COMPLETE_MATOME):
            return Defines.TutorialStatus.COMPLETED
        
        next_state = state + 1
        if not Defines.TutorialStatus.NAMES.has_key(next_state):
            chapter = Handler.tutoStateToChapterState(state)
            next_state = chapter + 0x0100
        return next_state
    
    def makeUrlNext(self):
        tutostate = self.toNextState(self.__cur_state)
        return OSAUtil.addQuery(UrlMaker.tutorial(), Defines.URLQUERY_TUTO, tutostate)
    
    def updateTutoState(self, tutostate):
        v_player = self.getViewerPlayer(True)
        if v_player.tutorialstate != tutostate:
            try:
                if tutostate == Defines.TutorialStatus.COMPLETED:
                    model_mgr = db_util.run_in_transaction(self.tr_write_tutoend, v_player.id)
                else:
                    model_mgr = db_util.run_in_transaction(self.tr_update_tutostate, v_player.id, tutostate)
                model_mgr.write_end()
            except CabaretError, err:
                if err.code == CabaretError.Code.ALREADY_RECEIVED:
                    pass
                else:
                    raise
    
    def tr_update_tutostate(self, uid, tutostate):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_update_tutorialstate(model_mgr, uid, tutostate)
        model_mgr.write_all()
        return model_mgr
    
    def tr_write_tutoend(self, uid):
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_players(self, [uid], [], model_mgr=model_mgr)[0]
        BackendApi.tr_tutorialend(model_mgr, player, self.is_pc)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
