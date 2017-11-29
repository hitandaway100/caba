# -*- coding: utf-8 -*-
from django.conf.urls import patterns

import settings_sub
from defines import Defines

def __get_app_patterns():
    """アプリ側のマッピング.
    """
    def __app_pattern(url_pattern, view):
        return (r'^%s' % url_pattern, 'platinumegg.app.%s.views.%s.main' % (settings_sub.APP_NAME, view))
    urllist = []
    if settings_sub.IS_DEV:
        urllist.extend([
                __app_pattern(r'sp/apitest', 'application.apitest'),
                __app_pattern(r'pc/apitest', 'application.pc.payment_test'),
                __app_pattern(r'sp/template_test/*', 'application.template_test'),
                __app_pattern(r'pc/template_test/*', 'application.template_test'),
                __app_pattern(r'pc/testtop', 'application.pc.testtop'),
                __app_pattern(r'sp/html5_test/*', 'application.html5_test'),
                __app_pattern(r'pc/html5_test/*', 'application.html5_test'),
                __app_pattern(r'sp/cookie_test/*', 'application.cookie_test'),
                __app_pattern(r'sp/mediatest', 'application.movie.test'),
                __app_pattern(r'sp/promotiondebug/', 'application.promotion.debug'),
        ])
    urllist.extend([
        
        # 警告ページ.
        __app_pattern(r'sp/warnpage/', 'application.warnpage'),
        
        # ヘルプ.
        __app_pattern(r'sp/help/', 'application.help'),
        
        # 仲間の近況.
        __app_pattern(r'sp/friendlog', 'application.friendlog'),
        
        # 行動履歴.
#        __app_pattern(r'sp/playerlog', 'application.playerlog'),
        
        # お知らせ.
        __app_pattern(r'sp/infomation', 'application.infomation'),
        
        # ログインボーナス.
        __app_pattern(r'sp/loginbonusanim', 'application.loginbonus.anim'),
        __app_pattern(r'sp/loginbonus', 'application.loginbonus.do'),
        __app_pattern(r'sp/lbtlexplain/', 'application.loginbonus.explain'),
        __app_pattern(r'sp/lbtldo/', 'application.loginbonus.timelimiteddo'),
        __app_pattern(r'sp/lbtlanim/', 'application.loginbonus.timelimitedanim'),
        __app_pattern(r'sp/lbsugorokudo/', 'application.loginbonus.sugorokudo'),
        __app_pattern(r'sp/lbsugorokuanim/', 'application.loginbonus.sugorokuanim'),
        __app_pattern(r'sp/comebackanim/', 'application.loginbonus.comebackanim'),
        
        # バトル.
        __app_pattern(r'sp/battleresultanim/', 'application.battle.resultanim'),
        __app_pattern(r'sp/battleresult/', 'application.battle.result'),
        __app_pattern(r'sp/battleanim/', 'application.battle.anim'),
        __app_pattern(r'sp/battledo/', 'application.battle.do'),
        __app_pattern(r'sp/battlepre/', 'application.battle.pre'),
        __app_pattern(r'sp/battleoppselect/', 'application.battle.oppselect'),
        __app_pattern(r'sp/bprecover/', 'application.battle.bprecover'),
        __app_pattern(r'sp/battlelp/', 'application.battle.landing'),
        __app_pattern(r'sp/battle/', 'application.battle.top'),
        
        # 進化合成.
        __app_pattern(r'sp/evolutionresult', 'application.evolution.result'),
        __app_pattern(r'sp/evolutionanim', 'application.evolution.anim'),
        __app_pattern(r'sp/evolutiondo', 'application.evolution.do'),
        __app_pattern(r'sp/evolutionyesno', 'application.evolution.yesno'),
        __app_pattern(r'sp/evolutionmaterial', 'application.evolution.materialselect'),
        __app_pattern(r'sp/evolution', 'application.evolution.baseselect'),
        
        # 強化合成.
        __app_pattern(r'sp/compositionresult', 'application.composition.result'),
        __app_pattern(r'sp/compositionanim', 'application.composition.anim'),
        __app_pattern(r'sp/compositiondo', 'application.composition.do'),
        __app_pattern(r'sp/compositionyesno', 'application.composition.yesno'),
        __app_pattern(r'sp/compositionmaterial', 'application.composition.materialselect'),
        __app_pattern(r'sp/composition', 'application.composition.baseselect'),
        
        # プレゼントBox
        __app_pattern(r'sp/present', 'application.present'),
        
        # ショップ.
        __app_pattern(r'sp/shopresult', 'application.shop.result'),
        __app_pattern(r'sp/shoppay', 'application.shop.pay'),
        __app_pattern(r'sp/shopdo', 'application.shop.do'),
        __app_pattern(r'sp/shopyesno', 'application.shop.yesno'),
        __app_pattern(r'sp/shop', 'application.shop.top'),
        
        # 引抜.

        __app_pattern(r'sp/gacharankingtop/', 'application.gacha.rankingtop'),
        __app_pattern(r'sp/gacharanking/', 'application.gacha.ranking'),
        __app_pattern(r'sp/gacharankingprize/', 'application.gacha.rankingprize'),
        
        __app_pattern(r'sp/gachamorecast', 'application.gacha.morecastanim'),
        __app_pattern(r'sp/gachaboxreset', 'application.gacha.boxreset'),
        __app_pattern(r'sp/gachaseatreset', 'application.gacha.seatreset'),
        __app_pattern(r'sp/gachacardlist', 'application.gacha.cardlist'),
        __app_pattern(r'sp/gachapay', 'application.gacha.pay'),
        __app_pattern(r'sp/gacharesult', 'application.gacha.result'),
        __app_pattern(r'sp/gachaanimsub', 'application.gacha.animsub'),
        __app_pattern(r'sp/gachaanim', 'application.gacha.anim'),
        __app_pattern(r'sp/gachado', 'application.gacha.do'),
        __app_pattern(r'sp/gachasupinfo', 'application.gacha.supinfo'),
        __app_pattern(r'sp/gachasupcard', 'application.gacha.supcard'),
        __app_pattern(r'sp/gachaseatanim', 'application.gacha.seatanim'),
        __app_pattern(r'sp/gachaomakelist', 'application.gacha.omakelist'),
        __app_pattern(r'sp/gacha', 'application.gacha.top'),
        
        # ハプニング.
        __app_pattern(r'sp/happeningend', 'application.happening.end'),
        __app_pattern(r'sp/happeningcancel', 'application.happening.cancel'),
        __app_pattern(r'sp/happeningboss', 'application.happening.boss'),
        __app_pattern(r'sp/happeningresultanim/', 'application.happening.resultanim'),
        __app_pattern(r'sp/happeningresult/', 'application.happening.result'),
        __app_pattern(r'sp/happeninganim/', 'application.happening.anim'),
        __app_pattern(r'sp/happeningdo', 'application.happening.do'),
        __app_pattern(r'sp/happening', 'application.happening.top'),
        
        # レイド.
        __app_pattern(r'sp/raidfriendselect', 'application.happening.friendselect'),
        __app_pattern(r'sp/raidhelpsend', 'application.happening.raidhelpsend'),
        __app_pattern(r'sp/raidhelpdetail', 'application.happening.raidhelpdetail'),
        __app_pattern(r'sp/raidlog/', 'application.happening.raidlog'),
        __app_pattern(r'sp/raid/', 'application.happening.raid'),
        
        # ボス.
        __app_pattern(r'sp/bossresult', 'application.boss.result'),
        __app_pattern(r'sp/bossbattleanim', 'application.boss.battleanim'),
        __app_pattern(r'sp/bossbattle', 'application.boss.battle'),
        __app_pattern(r'sp/bosspre', 'application.boss.pre'),
        __app_pattern(r'sp/bossscenarioanim', 'application.boss.scenarioanim'),
        
        # スカウト.
        __app_pattern(r'sp/scoutcardgetresult', 'application.scout.cardgetresult'),
        __app_pattern(r'sp/scoutcardget', 'application.scout.cardget'),
        __app_pattern(r'sp/scoutresultanim', 'application.scout.resultanim'),
        __app_pattern(r'sp/scoutresult', 'application.scout.result'),
        __app_pattern(r'sp/scoutanim', 'application.scout.scoutanim'),
        __app_pattern(r'sp/scoutdo', 'application.scout.do'),
        __app_pattern(r'sp/scout', 'application.scout.top'),
        __app_pattern(r'sp/areamap', 'application.scout.areamap'),
        # 仲間.
        __app_pattern(r'sp/friendremove', 'application.friend.friendremove'),
        __app_pattern(r'sp/friendreceive', 'application.friend.friendreceive'),
        __app_pattern(r'sp/friendcancel', 'application.friend.friendcancel'),
        __app_pattern(r'sp/friendrequest', 'application.friend.friendrequest'),
        __app_pattern(r'sp/friendsearch', 'application.friend.friendsearch'),
        __app_pattern(r'sp/friendlist', 'application.friend.friendlist'),
        # デッキ.
        __app_pattern(r'sp/deckset', 'application.card.deckset'),
        __app_pattern(r'sp/deckmember', 'application.card.deckmember'),
        __app_pattern(r'sp/deck', 'application.card.deck'),
        # 売却.
        __app_pattern(r'sp/sellcomplete', 'application.card.sellcomplete'),
        __app_pattern(r'sp/selldo', 'application.card.selldo'),
        __app_pattern(r'sp/sellyesno', 'application.card.sellyesno'),
        __app_pattern(r'sp/sell', 'application.card.sell'),
        # 異動.
        __app_pattern(r'sp/transfercomplete/', 'application.card.transfercomplete'),
        __app_pattern(r'sp/transferdo/', 'application.card.transferdo'),
        __app_pattern(r'sp/transferyesno/', 'application.card.transferyesno'),
        __app_pattern(r'sp/transfer/', 'application.card.transfer'),
        __app_pattern(r'sp/transferreturn/', 'application.card.transferreturn'),
        __app_pattern(r'sp/transferreturncomplete/', 'application.card.transferreturncomplete'),
        # カードBOX.
        __app_pattern(r'sp/cardbox', 'application.card.box'),
        __app_pattern(r'sp/carddetail', 'application.card.detail'),
        __app_pattern(r'sp/cardprotect', 'application.card.protect'),
        # あいさつ.
        __app_pattern(r'sp/greet_complete', 'application.greet.complete'),
        __app_pattern(r'sp/greet_comment_comp', 'application.greet.commentcomp'),
        __app_pattern(r'sp/greetlog', 'application.greet.log'),
        __app_pattern(r'sp/greet', 'application.greet.do'),
        
        __app_pattern(r'sp/profile', 'application.profile'),
        
        __app_pattern(r'sp/mypage', 'application.mypage'),
        
        __app_pattern(r'sp/regist/', 'application.regist'),
        
        # アイテム
        __app_pattern(r'sp/item_itemlist', 'application.item.itemlist'),
        __app_pattern(r'sp/item_useyesno', 'application.item.useyesno'),
        __app_pattern(r'sp/item_usecomplete', 'application.item.usecomplete'),
        __app_pattern(r'sp/item_use/', 'application.item.use'),
        __app_pattern(r'sp/item_use2/', 'application.item.use2'),
        
        # アルバム
        __app_pattern(r'sp/albumdetail', 'application.album.detail'),
        __app_pattern(r'sp/albummemories', 'application.album.memories'),
        __app_pattern(r'sp/album', 'application.album.album'),
        
        # 動画.
        __app_pattern(r'sp/movie/keyget/', 'application.movie.keyget'),

        # 交換所.
        __app_pattern(r'sp/tradeshopresult', 'application.tradeshop.result'),
        __app_pattern(r'sp/tradeshopyesno', 'application.tradeshop.yesno'),
        __app_pattern(r'sp/tradeshopdo', 'application.tradeshop.do'),
        __app_pattern(r'sp/tradeshop', 'application.tradeshop.top'),
        
        # 復刻チケット交換所.
        __app_pattern(r'sp/reprintticket_tradeshopresult', 'application.reprintticket_tradeshop.result'),
        __app_pattern(r'sp/reprintticket_tradeshopyesno', 'application.reprintticket_tradeshop.yesno'),
        __app_pattern(r'sp/reprintticket_tradeshopdo', 'application.reprintticket_tradeshop.do'),
        __app_pattern(r'sp/reprintticket_tradeshop', 'application.reprintticket_tradeshop.top'),

        # 宝箱
        __app_pattern(r'sp/treasurelist', 'application.treasure.treasurelist'),
        __app_pattern(r'sp/treasuregetcomplete', 'application.treasure.getcomplete'),
        __app_pattern(r'sp/treasureget', 'application.treasure.get'),
        
        # 秘宝
        __app_pattern(r'sp/tradeyesno', 'application.trade.tradeyesno'),
        __app_pattern(r'sp/tradecomplete', 'application.trade.tradecomplete'),
        __app_pattern(r'sp/tradedo', 'application.trade.do'),
        __app_pattern(r'sp/trade', 'application.trade.trade'),

        # 招待.
        __app_pattern(r'sp/invite', 'application.invite'),
        
        # 設定.
        __app_pattern(r'sp/config', 'application.config'),
        
        # クロスプロモーション.
        __app_pattern(r'sp/promotiontop/', 'application.promotion.top'),
        __app_pattern(r'sp/promotionprize/', 'application.promotion.prize'),
        __app_pattern(r'sp/promotionconditionget/', 'application.promotion.conditionget'),
        __app_pattern(r'sp/promotioncheck/', 'application.promotion.check'),

        # n周年記念
        __app_pattern(r'sp/anniv/', 'application.anniv.top'),
        
        # イベント.
        __app_pattern(r'sp/raideventtop/', 'application.raidevent.top'),
        __app_pattern(r'sp/raideventstart/', 'application.raidevent.start'),
        __app_pattern(r'sp/raideventopening/', 'application.raidevent.opening'),
        __app_pattern(r'sp/raideventepilogue/', 'application.raidevent.epilogue'),
        __app_pattern(r'sp/raideventbigboss/', 'application.raidevent.bigboss'),
        __app_pattern(r'sp/raideventtimebonus/', 'application.raidevent.timebonus'),
        __app_pattern(r'sp/raideventexplain/', 'application.raidevent.explain'),
        __app_pattern(r'sp/raideventranking/', 'application.raidevent.ranking'),
        __app_pattern(r'sp/raideventhelplist/', 'application.raidevent.helplist'),
        __app_pattern(r'sp/raideventprizereceive/', 'application.raidevent.prizereceive'),
        __app_pattern(r'sp/raideventbattlepre/', 'application.raidevent.battlepre'),
        __app_pattern(r'sp/raideventgachacast/', 'application.raidevent.gacha_cast'),
        __app_pattern(r'sp/raideventteaser/', 'application.raidevent.teaser'),
        __app_pattern(r'sp/raideventrecipelist/', 'application.raidevent.recipelist'),
        __app_pattern(r'sp/raideventrecipeyesno/', 'application.raidevent.recipeyesno'),
        __app_pattern(r'sp/raideventrecipedo/', 'application.raidevent.recipedo'),
        __app_pattern(r'sp/raideventrecipecomplete/', 'application.raidevent.recipecomplete'),
        __app_pattern(r'sp/raideventscoutcardgetresult/', 'application.raidevent.scout.cardgetresult'),
        __app_pattern(r'sp/raideventscoutcardget/', 'application.raidevent.scout.cardget'),
        __app_pattern(r'sp/raideventscoutresultanim/', 'application.raidevent.scout.resultanim'),
        __app_pattern(r'sp/raideventscoutresult/', 'application.raidevent.scout.result'),
        __app_pattern(r'sp/raideventscoutanim/', 'application.raidevent.scout.scoutanim'),
        __app_pattern(r'sp/raideventscoutdo/', 'application.raidevent.scout.do'),
        __app_pattern(r'sp/raideventscouttop/', 'application.raidevent.scout.top'),

        # プロデュースイベント
        __app_pattern(r'sp/produceeventtop/', 'application.produce_event.top'),
        __app_pattern(r'sp/produceeventexplain/', 'application.produce_event.explain'),
        __app_pattern(r'sp/produceeventscouttop/', 'application.produce_event.scout.top'),
        __app_pattern(r'sp/produceeventscoutdo/', 'application.produce_event.scout.do'),
        __app_pattern(r'sp/produceeventscoutresult/', 'application.produce_event.scout.result'),
        __app_pattern(r'sp/produceeventbattlepre/', 'application.produce_event.battlepre'),
        __app_pattern(r'sp/produceeventscoutcardgetresult/', 'application.produce_event.scout.cardgetresult'),
        __app_pattern(r'sp/produceeventscoutcardget/', 'application.produce_event.scout.cardget'),

        __app_pattern(r'sp/producehappeningend', 'application.produce_happening.end'),
        __app_pattern(r'sp/producehappeningcancel', 'application.produce_happening.cancel'),
        __app_pattern(r'sp/producehappeningboss', 'application.produce_happening.boss'),
        __app_pattern(r'sp/producehappeningresultanim/', 'application.produce_happening.resultanim'),
        __app_pattern(r'sp/producehappeningresult/', 'application.produce_happening.result'),
        __app_pattern(r'sp/producehappeninganim/', 'application.produce_happening.anim'),
        __app_pattern(r'sp/producehappeningdo', 'application.produce_happening.do'),
        __app_pattern(r'sp/producehappening', 'application.produce_happening.top'),
        __app_pattern(r'sp/produceraid/', 'application.produce_happening.raid'),

        __app_pattern(r'sp/produceeventscoutanim/', 'application.produce_event.scout.scoutanim'),
        __app_pattern(r'sp/produceeventscoutresultanim/', 'application.produce_event.scout.resultanim'),
        __app_pattern(r'sp/produceeventopening/', 'application.produce_event.opening'),
        __app_pattern(r'sp/produceeventepilogue/', 'application.produce_event.epilogue'),
        
        # スカウトイベント.
        __app_pattern(r'sp/sceventstart/', 'application.scoutevent.start'),
        __app_pattern(r'sp/sceventtop/', 'application.scoutevent.eventtop'),
        __app_pattern(r'sp/sceventopening/', 'application.scoutevent.opening'),
        __app_pattern(r'sp/sceventepilogue/', 'application.scoutevent.epilogue'),
        __app_pattern(r'sp/sceventexplain/', 'application.scoutevent.explain'),
        __app_pattern(r'sp/sceventranking/', 'application.scoutevent.ranking'),
        __app_pattern(r'sp/sceventareamap/', 'application.scoutevent.areamap'),
        __app_pattern(r'sp/sceventcardgetresult/', 'application.scoutevent.cardgetresult'),
        __app_pattern(r'sp/sceventcardget/', 'application.scoutevent.cardget'),
        __app_pattern(r'sp/sceventresultanim/', 'application.scoutevent.resultanim'),
        __app_pattern(r'sp/sceventresult/', 'application.scoutevent.result'),
        __app_pattern(r'sp/sceventanim/', 'application.scoutevent.scoutanim'),
        __app_pattern(r'sp/sceventfever/', 'application.scoutevent.fever'),
        __app_pattern(r'sp/sceventlovetime/', 'application.scoutevent.lovetime'),
        __app_pattern(r'sp/sceventdo/', 'application.scoutevent.do'),
        __app_pattern(r'sp/scevent/', 'application.scoutevent.top'),
        __app_pattern(r'sp/sceventteaser/', 'application.scoutevent.teaser'),
        __app_pattern(r'sp/sceventmovie/', 'application.scoutevent.movie'),
        __app_pattern(r'sp/sceventproduce/', 'application.scoutevent.produce'),
        __app_pattern(r'sp/sceventcastnomination/', 'application.scoutevent.castnomination'),
        __app_pattern(r'sp/sceventtippopulatecomplete/', 'application.scoutevent.tippopulatecomplete'),
        __app_pattern(r'sp/sceventtiptrade/', 'application.scoutevent.tiptrade'),
        __app_pattern(r'sp/sceventtiptradedo/', 'application.scoutevent.tiptradedo'),
        __app_pattern(r'sp/sceventtiptraderesult/', 'application.scoutevent.tiptraderesult'),
        
        # バトルイベント.
        __app_pattern(r'sp/battleeventopening/', 'application.battleevent.opening'),
        __app_pattern(r'sp/battleeventepilogue/', 'application.battleevent.epilogue'),
        __app_pattern(r'sp/battleeventscenario/', 'application.battleevent.scenario'),
        __app_pattern(r'sp/battleeventregist/', 'application.battleevent.regist'),
        __app_pattern(r'sp/battleeventtop/', 'application.battleevent.top'),
        __app_pattern(r'sp/battleeventopplist/', 'application.battleevent.opplist'),
        __app_pattern(r'sp/battleeventbattlepre/', 'application.battleevent.pre'),
        __app_pattern(r'sp/battleeventbattledo/', 'application.battleevent.do'),
        __app_pattern(r'sp/battleeventbattleanim/', 'application.battleevent.anim'),
        __app_pattern(r'sp/battleeventbattlepiecepresent/', 'application.battleevent.piecepresent'),
        __app_pattern(r'sp/battleeventresultanim/', 'application.battleevent.resultanim'),
        __app_pattern(r'sp/battleeventbattleresult/', 'application.battleevent.result'),
        __app_pattern(r'sp/battleeventranking/', 'application.battleevent.ranking'),
        __app_pattern(r'sp/battleeventloglist/', 'application.battleevent.loglist'),
        __app_pattern(r'sp/battleeventgrouplog/list/', 'application.battleevent.grouploglist'),
        __app_pattern(r'sp/battleeventgrouplog/detail/', 'application.battleevent.grouplogdetail'),
        __app_pattern(r'sp/battleeventgroup/', 'application.battleevent.group'),
        __app_pattern(r'sp/battleeventexplain/', 'application.battleevent.explain'),
        __app_pattern(r'sp/battleeventloginbonus/', 'application.battleevent.loginbonus'),
        __app_pattern(r'sp/battleeventloginbonusanim/', 'application.battleevent.loginbonusanim'),
        __app_pattern(r'sp/battleeventteaser/', 'application.battleevent.teaser'),
        
        __app_pattern(r'sp/battleeventpresent/', 'application.battleevent.eventpresent'),
        __app_pattern(r'sp/battleeventpresentreceive/', 'application.battleevent.eventpresentreceive'),
        __app_pattern(r'sp/battleeventpresentanim/', 'application.battleevent.eventpresentanim'),
        __app_pattern(r'sp/battleeventpresentlist/', 'application.battleevent.eventpresentlist'),
        
        __app_pattern(r'sp/serial_top', 'application.serial.top'),
        __app_pattern(r'sp/serial_input', 'application.serial.input'),
        
        # パネルミッション.
        __app_pattern(r'sp/panelmissiontop/', 'application.panelmission.top'),
        __app_pattern(r'sp/panelmissionanim/', 'application.panelmission.anim'),
        
        # 経営.
        __app_pattern(r'sp/cabaclubtop/', 'application.cabaclub.top'),
        __app_pattern(r'sp/cabaclubresultanim/', 'application.cabaclub.resultanim'),
        __app_pattern(r'sp/cabaclubeventanim/', 'application.cabaclub.eventanim'),
        __app_pattern(r'sp/cabaclubstore/', 'application.cabaclub.store'),
        __app_pattern(r'sp/cabaclubrentyesno/', 'application.cabaclub.rentyesno'),
        __app_pattern(r'sp/cabaclubrentdo/', 'application.cabaclub.rentdo'),
        __app_pattern(r'sp/cabaclubrentend/', 'application.cabaclub.rentend'),
        __app_pattern(r'sp/cabaclubopen/', 'application.cabaclub.open'),
        __app_pattern(r'sp/cabaclubclose/', 'application.cabaclub.close'),
        __app_pattern(r'sp/cabaclubuayesno/', 'application.cabaclub.uayesno'),
        __app_pattern(r'sp/cabaclubuado/', 'application.cabaclub.uado'),
        __app_pattern(r'sp/cabaclubuaend/', 'application.cabaclub.uaend'),
        __app_pattern(r'sp/cabaclubcancelyesno/', 'application.cabaclub.cancelyesno'),
        __app_pattern(r'sp/cabaclubcanceldo/', 'application.cabaclub.canceldo'),
        __app_pattern(r'sp/cabaclubcancelend/', 'application.cabaclub.cancelend'),
        __app_pattern(r'sp/cabaclubcastselect/', 'application.cabaclub.castselect'),
        __app_pattern(r'sp/cabaclubcastselectdo/', 'application.cabaclub.castselectdo'),
        __app_pattern(r'sp/cabaclubcastremove/', 'application.cabaclub.castremove'),
        __app_pattern(r'sp/cabaclubrank/', 'application.cabaclub.rank'),
        __app_pattern(r'sp/cabaclubdeckselect/', 'application.cabaclub.deckselect'),

        # 称号.
        __app_pattern(r'sp/titletop/', 'application.title.top'),
        __app_pattern(r'sp/titleyesno/', 'application.title.yesno'),
        __app_pattern(r'sp/titledo/', 'application.title.do'),
        __app_pattern(r'sp/titleend/', 'application.title.end'),
        
        __app_pattern(r'sp/teaser/', 'application.teaser'),
        
        __app_pattern(r'sp/session_error', 'application.session_error'),
        
        __app_pattern(r'sp/tutorial', 'application.tutorial'),
        
        __app_pattern(r'sp/effect/', 'application.effect'),
        
        __app_pattern(r'sp/popupview/', 'application.popupview'),
        
        __app_pattern(r'sp/session_set', 'application.session_set'),
        
        __app_pattern(r'sp/support_paymentlist', 'application.support.paymentlist'),
        
        __app_pattern(r'sp/no_support', 'application.no_support'),
        
        __app_pattern(r'sp/lifecycle/', 'application.lifecycle'),
        
        __app_pattern(r'sp/ban/', 'application.ban'),
        
        __app_pattern(r'sp/simple/', 'application.simple'),

        __app_pattern(r'sp/levelupbonus', 'application.levelupbonus'),
        
        __app_pattern(r'sp/', 'application.top'),
        
        # PC版.
        # 警告ページ.
        __app_pattern(r'pc/warnpage/', 'application.warnpage'),
        
        # ヘルプ.
        __app_pattern(r'pc/help/', 'application.help'),
        
        # 仲間の近況.
        __app_pattern(r'pc/friendlog', 'application.friendlog'),
        
        # 行動履歴.
#        __app_pattern(r'pc/playerlog', 'application.playerlog'),
        
        # お知らせ.
        __app_pattern(r'pc/infomation', 'application.infomation'),
        
        # ログインボーナス.
        __app_pattern(r'pc/loginbonusanim', 'application.loginbonus.anim'),
        __app_pattern(r'pc/loginbonus', 'application.loginbonus.do'),
        __app_pattern(r'pc/lbtlexplain/', 'application.loginbonus.explain'),
        __app_pattern(r'pc/lbtldo/', 'application.loginbonus.timelimiteddo'),
        __app_pattern(r'pc/lbtlanim/', 'application.loginbonus.timelimitedanim'),
        __app_pattern(r'pc/lbsugorokudo/', 'application.loginbonus.sugorokudo'),
        __app_pattern(r'pc/lbsugorokuanim/', 'application.loginbonus.sugorokuanim'),
        __app_pattern(r'pc/comebackanim/', 'application.loginbonus.comebackanim'),
        
        # バトル.
        __app_pattern(r'pc/battleresultanim/', 'application.battle.resultanim'),
        __app_pattern(r'pc/battleresult/', 'application.battle.result'),
        __app_pattern(r'pc/battleanim/', 'application.battle.anim'),
        __app_pattern(r'pc/battledo/', 'application.battle.do'),
        __app_pattern(r'pc/battlepre/', 'application.battle.pre'),
        __app_pattern(r'pc/battleoppselect/', 'application.battle.oppselect'),
        __app_pattern(r'pc/bprecover/', 'application.battle.bprecover'),
        __app_pattern(r'pc/battlelp/', 'application.battle.landing'),
        __app_pattern(r'pc/battle/', 'application.battle.top'),
        
        # 進化合成.
        __app_pattern(r'pc/evolutionresult', 'application.evolution.result'),
        __app_pattern(r'pc/evolutionanim', 'application.evolution.anim'),
        __app_pattern(r'pc/evolutiondo', 'application.evolution.do'),
        __app_pattern(r'pc/evolutionyesno', 'application.evolution.yesno'),
        __app_pattern(r'pc/evolutionmaterial', 'application.evolution.materialselect'),
        __app_pattern(r'pc/evolution', 'application.evolution.baseselect'),
        
        # 強化合成.
        __app_pattern(r'pc/compositionresult', 'application.composition.result'),
        __app_pattern(r'pc/compositionanim', 'application.composition.anim'),
        __app_pattern(r'pc/compositiondo', 'application.composition.do'),
        __app_pattern(r'pc/compositionyesno', 'application.composition.yesno'),
        __app_pattern(r'pc/compositionmaterial', 'application.composition.materialselect'),
        __app_pattern(r'pc/composition', 'application.composition.baseselect'),
        
        # プレゼントBox
        __app_pattern(r'pc/present', 'application.present'),
        
        # ショップ.
        __app_pattern(r'pc/shopresult', 'application.shop.result'),
#        __app_pattern(r'pc/shoppay', 'application.shop.pay'),
        __app_pattern(r'pc/shopdo', 'application.shop.do'),
        __app_pattern(r'pc/shopyesno', 'application.shop.yesno'),
        __app_pattern(r'pc/shop', 'application.shop.top'),
        
        # 引抜.
        __app_pattern(r'pc/gacharankingtop/', 'application.gacha.rankingtop'),
        __app_pattern(r'pc/gacharanking/', 'application.gacha.ranking'),
        __app_pattern(r'pc/gacharankingprize/', 'application.gacha.rankingprize'),
        
        __app_pattern(r'pc/gachamorecast', 'application.gacha.morecastanim'),
        __app_pattern(r'pc/gachaboxreset', 'application.gacha.boxreset'),
        __app_pattern(r'pc/gachaseatreset', 'application.gacha.seatreset'),
        __app_pattern(r'pc/gachacardlist', 'application.gacha.cardlist'),
#        __app_pattern(r'pc/gachapay', 'application.gacha.pay'),
        __app_pattern(r'pc/gacharesult', 'application.gacha.result'),
        __app_pattern(r'pc/gachaanimsub', 'application.gacha.animsub'),
        __app_pattern(r'pc/gachaanim', 'application.gacha.anim'),
        __app_pattern(r'pc/gachado', 'application.gacha.do'),
        __app_pattern(r'pc/gachasupinfo', 'application.gacha.supinfo'),
        __app_pattern(r'pc/gachasupcard', 'application.gacha.supcard'),
        __app_pattern(r'pc/gachaseatanim', 'application.gacha.seatanim'),
        __app_pattern(r'pc/gachaomakelist', 'application.gacha.omakelist'),
        __app_pattern(r'pc/gacha', 'application.gacha.top'),
        
        # ハプニング.
        __app_pattern(r'pc/happeningend', 'application.happening.end'),
        __app_pattern(r'pc/happeningcancel', 'application.happening.cancel'),
        __app_pattern(r'pc/happeningboss', 'application.happening.boss'),
        __app_pattern(r'pc/happeningresultanim/', 'application.happening.resultanim'),
        __app_pattern(r'pc/happeningresult/', 'application.happening.result'),
        __app_pattern(r'pc/happeninganim/', 'application.happening.anim'),
        __app_pattern(r'pc/happeningdo', 'application.happening.do'),
        __app_pattern(r'pc/happening', 'application.happening.top'),
        
        # レイド.
        __app_pattern(r'pc/raidfriendselect', 'application.happening.friendselect'),
        __app_pattern(r'pc/raidhelpsend', 'application.happening.raidhelpsend'),
        __app_pattern(r'pc/raidhelpdetail', 'application.happening.raidhelpdetail'),
        __app_pattern(r'pc/raidlog/', 'application.happening.raidlog'),
        __app_pattern(r'pc/raid/', 'application.happening.raid'),
        
        # ボス.
        __app_pattern(r'pc/bossresult', 'application.boss.result'),
        __app_pattern(r'pc/bossbattleanim', 'application.boss.battleanim'),
        __app_pattern(r'pc/bossbattle', 'application.boss.battle'),
        __app_pattern(r'pc/bosspre', 'application.boss.pre'),
        __app_pattern(r'pc/bossscenarioanim', 'application.boss.scenarioanim'),
        
        # スカウト.
        __app_pattern(r'pc/scoutcardgetresult', 'application.scout.cardgetresult'),
        __app_pattern(r'pc/scoutcardget', 'application.scout.cardget'),
        __app_pattern(r'pc/scoutresultanim', 'application.scout.resultanim'),
        __app_pattern(r'pc/scoutresult', 'application.scout.result'),
        __app_pattern(r'pc/scoutanim', 'application.scout.scoutanim'),
        __app_pattern(r'pc/scoutdo', 'application.scout.do'),
        __app_pattern(r'pc/scout', 'application.scout.top'),
        __app_pattern(r'pc/areamap', 'application.scout.areamap'),
        # 仲間.
        __app_pattern(r'pc/friendremove', 'application.friend.friendremove'),
        __app_pattern(r'pc/friendreceive', 'application.friend.friendreceive'),
        __app_pattern(r'pc/friendcancel', 'application.friend.friendcancel'),
        __app_pattern(r'pc/friendrequest', 'application.friend.friendrequest'),
        __app_pattern(r'pc/friendsearch', 'application.friend.friendsearch'),
        __app_pattern(r'pc/friendlist', 'application.friend.friendlist'),
        # デッキ.
        __app_pattern(r'pc/deckset', 'application.card.deckset'),
        __app_pattern(r'pc/deckmember', 'application.card.deckmember'),
        __app_pattern(r'pc/deck', 'application.card.deck'),
        # 売却.
        __app_pattern(r'pc/sellcomplete', 'application.card.sellcomplete'),
        __app_pattern(r'pc/selldo', 'application.card.selldo'),
        __app_pattern(r'pc/sellyesno', 'application.card.sellyesno'),
        __app_pattern(r'pc/sell', 'application.card.sell'),
        # 異動.
        __app_pattern(r'pc/transfercomplete/', 'application.card.transfercomplete'),
        __app_pattern(r'pc/transferdo/', 'application.card.transferdo'),
        __app_pattern(r'pc/transferyesno/', 'application.card.transferyesno'),
        __app_pattern(r'pc/transfer/', 'application.card.transfer'),
        __app_pattern(r'pc/transferreturn/', 'application.card.transferreturn'),
        __app_pattern(r'pc/transferreturncomplete/', 'application.card.transferreturncomplete'),
        # カードBOX.
        __app_pattern(r'pc/cardbox', 'application.card.box'),
        __app_pattern(r'pc/carddetail', 'application.card.detail'),
        __app_pattern(r'pc/cardprotect', 'application.card.protect'),
        # あいさつ.
        __app_pattern(r'pc/greet_complete', 'application.greet.complete'),
        __app_pattern(r'pc/greet_comment_comp', 'application.greet.commentcomp'),
        __app_pattern(r'pc/greetlog', 'application.greet.log'),
        __app_pattern(r'pc/greet', 'application.greet.do'),
        
        __app_pattern(r'pc/profile', 'application.profile'),
        
        __app_pattern(r'pc/mypage', 'application.mypage'),
        
        __app_pattern(r'pc/regist/', 'application.regist'),
        
        # アイテム
        __app_pattern(r'pc/item_itemlist', 'application.item.itemlist'),
        __app_pattern(r'pc/item_useyesno', 'application.item.useyesno'),
        __app_pattern(r'pc/item_usecomplete', 'application.item.usecomplete'),
        __app_pattern(r'pc/item_use/', 'application.item.use'),
        __app_pattern(r'pc/item_use2/', 'application.item.use2'),
        
        # アルバム
        __app_pattern(r'pc/albumdetail', 'application.album.detail'),
        __app_pattern(r'pc/albummemories', 'application.album.memories'),
        __app_pattern(r'pc/album', 'application.album.album'),
        
        # 交換所.
        __app_pattern(r'pc/tradeshopresult', 'application.tradeshop.result'),
        __app_pattern(r'pc/tradeshopyesno', 'application.tradeshop.yesno'),
        __app_pattern(r'pc/tradeshopdo', 'application.tradeshop.do'),
        __app_pattern(r'pc/tradeshop', 'application.tradeshop.top'),

        # 復刻チケット交換所
        __app_pattern(r'pc/reprintticket_tradeshopresult', 'application.reprintticket_tradeshop.result'),
        __app_pattern(r'pc/reprintticket_tradeshopyesno', 'application.reprintticket_tradeshop.yesno'),
        __app_pattern(r'pc/reprintticket_tradeshopdo', 'application.reprintticket_tradeshop.do'),
        __app_pattern(r'pc/reprintticket_tradeshop', 'application.reprintticket_tradeshop.top'),

        # 宝箱
        __app_pattern(r'pc/treasurelist', 'application.treasure.treasurelist'),
        __app_pattern(r'pc/treasuregetcomplete', 'application.treasure.getcomplete'),
        __app_pattern(r'pc/treasureget', 'application.treasure.get'),
        
        # 秘宝
        __app_pattern(r'pc/tradeyesno', 'application.trade.tradeyesno'),
        __app_pattern(r'pc/tradecomplete', 'application.trade.tradecomplete'),
        __app_pattern(r'pc/tradedo', 'application.trade.do'),
        __app_pattern(r'pc/trade', 'application.trade.trade'),

        # 招待.
        __app_pattern(r'pc/invite', 'application.invite'),
        
        # 設定.
        __app_pattern(r'pc/config', 'application.config'),
        
        # クロスプロモーション.
        __app_pattern(r'pc/promotiontop/', 'application.promotion.top'),
        __app_pattern(r'pc/promotionprize/', 'application.promotion.prize'),
        __app_pattern(r'pc/promotionconditionget/', 'application.promotion.conditionget'),
        __app_pattern(r'pc/promotioncheck/', 'application.promotion.check'),

        # n周年記念
        __app_pattern(r'pc/anniv/', 'application.anniv.top'),

        # イベント.
        __app_pattern(r'pc/raideventtop/', 'application.raidevent.top'),
        __app_pattern(r'pc/raideventstart/', 'application.raidevent.start'),
        __app_pattern(r'pc/raideventopening/', 'application.raidevent.opening'),
        __app_pattern(r'pc/raideventepilogue/', 'application.raidevent.epilogue'),
        __app_pattern(r'pc/raideventbigboss/', 'application.raidevent.bigboss'),
        __app_pattern(r'pc/raideventtimebonus/', 'application.raidevent.timebonus'),
        __app_pattern(r'pc/raideventexplain/', 'application.raidevent.explain'),
        __app_pattern(r'pc/raideventranking/', 'application.raidevent.ranking'),
        __app_pattern(r'pc/raideventhelplist/', 'application.raidevent.helplist'),
        __app_pattern(r'pc/raideventprizereceive/', 'application.raidevent.prizereceive'),
        __app_pattern(r'pc/raideventbattlepre/', 'application.raidevent.battlepre'),
        __app_pattern(r'pc/raideventgachacast/', 'application.raidevent.gacha_cast'),
        __app_pattern(r'pc/raideventteaser/', 'application.raidevent.teaser'),
        __app_pattern(r'pc/raideventrecipelist/', 'application.raidevent.recipelist'),
        __app_pattern(r'pc/raideventrecipeyesno/', 'application.raidevent.recipeyesno'),
        __app_pattern(r'pc/raideventrecipedo/', 'application.raidevent.recipedo'),
        __app_pattern(r'pc/raideventrecipecomplete/', 'application.raidevent.recipecomplete'),
        __app_pattern(r'pc/raideventscoutcardgetresult/', 'application.raidevent.scout.cardgetresult'),
        __app_pattern(r'pc/raideventscoutcardget/', 'application.raidevent.scout.cardget'),
        __app_pattern(r'pc/raideventscoutresultanim/', 'application.raidevent.scout.resultanim'),
        __app_pattern(r'pc/raideventscoutresult/', 'application.raidevent.scout.result'),
        __app_pattern(r'pc/raideventscoutanim/', 'application.raidevent.scout.scoutanim'),
        __app_pattern(r'pc/raideventscoutdo/', 'application.raidevent.scout.do'),
        __app_pattern(r'pc/raideventscouttop/', 'application.raidevent.scout.top'),
        
        # プロデュースイベント
        __app_pattern(r'pc/produceeventtop/', 'application.produce_event.top'),
        __app_pattern(r'pc/produceeventexplain/', 'application.produce_event.explain'),
        __app_pattern(r'pc/produceeventscouttop/', 'application.produce_event.scout.top'),
        __app_pattern(r'pc/produceeventscoutdo/', 'application.produce_event.scout.do'),
        __app_pattern(r'pc/produceeventscoutresult/', 'application.produce_event.scout.result'),
        __app_pattern(r'pc/produceeventbattlepre/', 'application.produce_event.battlepre'),
        __app_pattern(r'pc/produceeventscoutcardgetresult/', 'application.produce_event.scout.cardgetresult'),
        __app_pattern(r'pc/produceeventscoutcardget/', 'application.produce_event.scout.cardget'),

        __app_pattern(r'pc/producehappeningend', 'application.produce_happening.end'),
        __app_pattern(r'pc/producehappeningcancel', 'application.produce_happening.cancel'),
        __app_pattern(r'pc/producehappeningboss', 'application.produce_happening.boss'),
        __app_pattern(r'pc/producehappeningresultanim/', 'application.produce_happening.resultanim'),
        __app_pattern(r'pc/producehappeningresult/', 'application.produce_happening.result'),
        __app_pattern(r'pc/producehappeninganim/', 'application.produce_happening.anim'),
        __app_pattern(r'pc/producehappeningdo', 'application.produce_happening.do'),
        __app_pattern(r'pc/producehappening', 'application.produce_happening.top'),
        __app_pattern(r'pc/produceraid/', 'application.produce_happening.raid'),

        __app_pattern(r'pc/produceeventscoutanim/', 'application.produce_event.scout.scoutanim'),
        __app_pattern(r'pc/produceeventscoutresultanim/', 'application.produce_event.scout.resultanim'),
        __app_pattern(r'pc/produceeventopening/', 'application.produce_event.opening'),
        __app_pattern(r'pc/produceeventepilogue/', 'application.produce_event.epilogue'),

        # スカウトイベント.
        __app_pattern(r'pc/sceventstart/', 'application.scoutevent.start'),
        __app_pattern(r'pc/sceventtop/', 'application.scoutevent.eventtop'),
        __app_pattern(r'pc/sceventopening/', 'application.scoutevent.opening'),
        __app_pattern(r'pc/sceventepilogue/', 'application.scoutevent.epilogue'),
        __app_pattern(r'pc/sceventexplain/', 'application.scoutevent.explain'),
        __app_pattern(r'pc/sceventranking/', 'application.scoutevent.ranking'),
        __app_pattern(r'pc/sceventareamap/', 'application.scoutevent.areamap'),
        __app_pattern(r'pc/sceventcardgetresult/', 'application.scoutevent.cardgetresult'),
        __app_pattern(r'pc/sceventcardget/', 'application.scoutevent.cardget'),
        __app_pattern(r'pc/sceventresultanim/', 'application.scoutevent.resultanim'),
        __app_pattern(r'pc/sceventresult/', 'application.scoutevent.result'),
        __app_pattern(r'pc/sceventanim/', 'application.scoutevent.scoutanim'),
        __app_pattern(r'pc/sceventfever/', 'application.scoutevent.fever'),
        __app_pattern(r'pc/sceventlovetime/', 'application.scoutevent.lovetime'),
        __app_pattern(r'pc/sceventdo/', 'application.scoutevent.do'),
        __app_pattern(r'pc/scevent/', 'application.scoutevent.top'),
        __app_pattern(r'pc/sceventteaser/', 'application.scoutevent.teaser'),
        __app_pattern(r'pc/sceventmovie/', 'application.scoutevent.movie'),
        __app_pattern(r'pc/sceventproduce/', 'application.scoutevent.produce'),
        __app_pattern(r'pc/sceventcastnomination/', 'application.scoutevent.castnomination'),
        __app_pattern(r'pc/sceventtippopulatecomplete/', 'application.scoutevent.tippopulatecomplete'),
        __app_pattern(r'pc/sceventtiptrade/', 'application.scoutevent.tiptrade'),
        __app_pattern(r'pc/sceventtiptradedo/', 'application.scoutevent.tiptradedo'),
        __app_pattern(r'pc/sceventtiptraderesult/', 'application.scoutevent.tiptraderesult'),
        
        # バトルイベント.
        __app_pattern(r'pc/battleeventopening/', 'application.battleevent.opening'),
        __app_pattern(r'pc/battleeventepilogue/', 'application.battleevent.epilogue'),
        __app_pattern(r'pc/battleeventscenario/', 'application.battleevent.scenario'),
        __app_pattern(r'pc/battleeventregist/', 'application.battleevent.regist'),
        __app_pattern(r'pc/battleeventtop/', 'application.battleevent.top'),
        __app_pattern(r'pc/battleeventopplist/', 'application.battleevent.opplist'),
        __app_pattern(r'pc/battleeventbattlepre/', 'application.battleevent.pre'),
        __app_pattern(r'pc/battleeventbattledo/', 'application.battleevent.do'),
        __app_pattern(r'pc/battleeventbattleanim/', 'application.battleevent.anim'),
        __app_pattern(r'pc/battleeventbattlepiecepresent/', 'application.battleevent.piecepresent'),
        __app_pattern(r'pc/battleeventresultanim/', 'application.battleevent.resultanim'),
        __app_pattern(r'pc/battleeventbattleresult/', 'application.battleevent.result'),
        __app_pattern(r'pc/battleeventranking/', 'application.battleevent.ranking'),
        __app_pattern(r'pc/battleeventloglist/', 'application.battleevent.loglist'),
        __app_pattern(r'pc/battleeventgrouplog/list/', 'application.battleevent.grouploglist'),
        __app_pattern(r'pc/battleeventgrouplog/detail/', 'application.battleevent.grouplogdetail'),
        __app_pattern(r'pc/battleeventgroup/', 'application.battleevent.group'),
        __app_pattern(r'pc/battleeventexplain/', 'application.battleevent.explain'),
        __app_pattern(r'pc/battleeventloginbonus/', 'application.battleevent.loginbonus'),
        __app_pattern(r'pc/battleeventloginbonusanim/', 'application.battleevent.loginbonusanim'),
        __app_pattern(r'pc/battleeventteaser/', 'application.battleevent.teaser'),
        
        __app_pattern(r'pc/battleeventpresent/', 'application.battleevent.eventpresent'),
        __app_pattern(r'pc/battleeventpresentreceive/', 'application.battleevent.eventpresentreceive'),
        __app_pattern(r'pc/battleeventpresentanim/', 'application.battleevent.eventpresentanim'),
        __app_pattern(r'pc/battleeventpresentlist/', 'application.battleevent.eventpresentlist'),
        
        __app_pattern(r'pc/serial_top', 'application.serial.top'),
        __app_pattern(r'pc/serial_input', 'application.serial.input'),
        
        # パネルミッション.
        __app_pattern(r'pc/panelmissiontop/', 'application.panelmission.top'),
        __app_pattern(r'pc/panelmissionanim/', 'application.panelmission.anim'),
        
        # 経営.
        __app_pattern(r'pc/cabaclubtop/', 'application.cabaclub.top'),
        __app_pattern(r'pc/cabaclubresultanim/', 'application.cabaclub.resultanim'),
        __app_pattern(r'pc/cabaclubeventanim/', 'application.cabaclub.eventanim'),
        __app_pattern(r'pc/cabaclubstore/', 'application.cabaclub.store'),
        __app_pattern(r'pc/cabaclubrentyesno/', 'application.cabaclub.rentyesno'),
        __app_pattern(r'pc/cabaclubrentdo/', 'application.cabaclub.rentdo'),
        __app_pattern(r'pc/cabaclubrentend/', 'application.cabaclub.rentend'),
        __app_pattern(r'pc/cabaclubopen/', 'application.cabaclub.open'),
        __app_pattern(r'pc/cabaclubclose/', 'application.cabaclub.close'),
        __app_pattern(r'pc/cabaclubuayesno/', 'application.cabaclub.uayesno'),
        __app_pattern(r'pc/cabaclubuado/', 'application.cabaclub.uado'),
        __app_pattern(r'pc/cabaclubuaend/', 'application.cabaclub.uaend'),
        __app_pattern(r'pc/cabaclubcancelyesno/', 'application.cabaclub.cancelyesno'),
        __app_pattern(r'pc/cabaclubcanceldo/', 'application.cabaclub.canceldo'),
        __app_pattern(r'pc/cabaclubcancelend/', 'application.cabaclub.cancelend'),
        __app_pattern(r'pc/cabaclubcastselect/', 'application.cabaclub.castselect'),
        __app_pattern(r'pc/cabaclubcastselectdo/', 'application.cabaclub.castselectdo'),
        __app_pattern(r'pc/cabaclubcastremove/', 'application.cabaclub.castremove'),
        __app_pattern(r'pc/cabaclubrank/', 'application.cabaclub.rank'),
        __app_pattern(r'pc/cabaclubdeckselect/', 'application.cabaclub.deckselect'),

        # 称号.
        __app_pattern(r'pc/titletop/', 'application.title.top'),
        __app_pattern(r'pc/titleyesno/', 'application.title.yesno'),
        __app_pattern(r'pc/titledo/', 'application.title.do'),
        __app_pattern(r'pc/titleend/', 'application.title.end'),
        
        __app_pattern(r'pc/teaser/', 'application.teaser'),
        
        __app_pattern(r'pc/session_error', 'application.session_error'),
        
        __app_pattern(r'pc/tutorial', 'application.tutorial'),
        
        __app_pattern(r'pc/effect/', 'application.effect'),
        
        __app_pattern(r'pc/popupview/', 'application.popupview'),
        
#        __app_pattern(r'pc/session_set', 'application.session_set'),
        
        __app_pattern(r'pc/support_paymentlist', 'application.support.paymentlist'),
        
        __app_pattern(r'pc/no_support', 'application.no_support'),
        
#        __app_pattern(r'pc/lifecycle/', 'application.lifecycle'),
        
        __app_pattern(r'pc/ban/', 'application.ban'),
        
        __app_pattern(r'pc/simple/', 'application.simple'),

        __app_pattern(r'pc/levelupbonus', 'application.levelupbonus'),
        
        # pc版のみ.
        __app_pattern(r'pc/myframe', 'application.pc.myframe'),
        __app_pattern(r'pc/getstatus', 'application.pc.getstatus'),
        __app_pattern(r'pc/payment_handler', 'application.pc.api.payment'),
        __app_pattern(r'pc/login/', 'application.pc.login'),
        __app_pattern(r'pc/movie/keyget/', 'application.pc.stream'),
        __app_pattern(r'pc/maintenance/', 'application.pc.maintenance'),
        
        __app_pattern(r'pc/', 'application.top'),
        
        #__app_pattern(r'pc/playerGet', 'application.pc.api.playerGet'),
        #__app_pattern(r'pc/playerRegist/', 'application.regist'),
        #__app_pattern(r'pc/playerLogListGet/', 'application.playerlog'),
        #__app_pattern(r'pc/infomationGet/', 'application.pc.api.infomationGet'),
        #__app_pattern(r'pc/eventbannerGet/', 'application.pc.api.eventbannerGet'),
        #__app_pattern(r'pc/friendLogListGet/', 'application.friendlog'),
        #__app_pattern(r'pc/cardListGet/', 'application.pc.api.cardListGet'),
        #__app_pattern(r'pc/deckGet/', 'application.pc.api.deckGet'),
        #__app_pattern(r'pc/deckSet/', 'application.card.deckset'),
        #__app_pattern(r'pc/cardSell/', 'application.card.selldo'),
        #__app_pattern(r'pc/frindListGet/', 'application.friend.friendlist'),
        #__app_pattern(r'pc/friendRequestSend/', 'application.friend.friendrequest'),
        #__app_pattern(r'pc/friendReceiveAccept/', 'application.friend.friendreceive'),
        #__app_pattern(r'pc/friendReceiveAccept/', 'application.friend.friendreceive'),
        #__app_pattern(r'pc/friendRemove/', 'application.friend.friendremove'),
        #__app_pattern(r'pc/friendSearch/', 'application.friend.friendsearch'),
        #__app_pattern(r'pc/greetDo/', 'application.greet.do'),
        #__app_pattern(r'pc/greetLogGet/', 'application.greet.log'),
        #__app_pattern(r'pc/areaListGet/', 'application.pc.api.areaListGet'),
        #__app_pattern(r'pc/scoutListGet/', 'application.scout.top'),
        #__app_pattern(r'pc/scoutDo/', 'application.scout.do'),
        #__app_pattern(r'pc/bossDo/', 'application.boss.battle'),
        #__app_pattern(r'pc/battleInfoGet/', 'application.pc.api.battleInfoGet'),
        #__app_pattern(r'pc/battleOpponentGet/', 'application.pc.api.battleOpponentGet'),
        #__app_pattern(r'pc/battleOpponentChange/', 'application.battle.oppselect'),
        #__app_pattern(r'pc/battleDo/', 'application.battle.do'),
        #__app_pattern(r'pc/happeningGet/', 'application.pc.api.happeningGet'),
        #__app_pattern(r'pc/happeningDo/', 'application.happening.do'),
        #__app_pattern(r'pc/raidGet/', 'application.pc.api.raidGet'),
        #__app_pattern(r'pc/raidFriendSet', 'application.happening.friendselect'),
        #__app_pattern(r'pc/raidHelpListGet', 'application.pc.api.raidHelpListGet'),
        #__app_pattern(r'pc/raidDo/', 'application.happening.raid'),
        #__app_pattern(r'pc/raidHelpSend', 'application.happening.raidhelpsend'),
        #__app_pattern(r'pc/raidLogListGet', 'application.happening.raidlog'),
        #__app_pattern(r'pc/itemListGet', 'application.item.itemlist'),
        #__app_pattern(r'pc/itemUse', 'application.item.use'),
        #__app_pattern(r'pc/treasureListGet', 'application.treasure.treasurelist'),
        #__app_pattern(r'pc/treasureOpen', 'application.treasure.get'),
        #__app_pattern(r'pc/compositionDo', 'application.composition.do'),
        #__app_pattern(r'pc/evolutionDo', 'application.evolution.do'),
        
#        __app_pattern(r'sp/top', 'application.top'),
#        __app_pattern(r'pc/top', 'application.top'),
#        __app_pattern(r'sp/', 'application.template_test'),
#        __app_pattern(r'pc/', 'application.pc.testtop'),
    ])
    if settings_sub.IS_LOCAL:
        __app_pattern(r'sp/cabaclubtestpage/', 'application.cabaclub.testpage'),    # キャバクラシステムの操作確認用.
    
    return urllist

def __get_mgr_patterns():
    """管理ツール側のマッピング.
    """
    def __app_pattern(url_pattern, view):
        return (r'^%s%s' % (Defines.ADMIN_PREFIX, url_pattern), 'platinumegg.app.%s.views.%s.%s.main' % (settings_sub.APP_NAME, Defines.ADMIN_PREFIX, view))
    urllist = []
    if settings_sub.IS_DEV:
        pass
    urllist.extend([
        __app_pattern(r'/model_edit/access_bonus', 'model_edit.access_bonus'),
        __app_pattern(r'/model_edit/area', 'model_edit.area'),
        __app_pattern(r'/model_edit/boss', 'model_edit.boss'),
        __app_pattern(r'/model_edit/default_card', 'model_edit.default_card'),
        __app_pattern(r'/model_edit/cabaretclubevent', 'model_edit.cabaretclubevent'),
        __app_pattern(r'/model_edit/cabaretclubstore', 'model_edit.cabaretclubstore'),
        __app_pattern(r'/model_edit/cabaretclub_ranking_event', 'model_edit.cabaretclub_ranking_event'),
        __app_pattern(r'/model_edit/cabaretclub', 'model_edit.cabaretclub'),
        __app_pattern(r'/model_edit/card_level_exp', 'model_edit.card_level_exp'),
        __app_pattern(r'/model_edit/card', 'model_edit.card'),
        __app_pattern(r'/model_edit/event_banner', 'model_edit.event_banner'),
        __app_pattern(r'/model_edit/gacha_explain_text', 'model_edit.gacha_explain_text'),
        __app_pattern(r'/model_edit/gacha_boxgachadetail', 'model_edit.gacha_boxgachadetail'),
        __app_pattern(r'/model_edit/gacha_box', 'model_edit.gacha_box'),
        __app_pattern(r'/model_edit/gacha_group', 'model_edit.gacha_group'),
        __app_pattern(r'/model_edit/gacha_step', 'model_edit.gacha_step'),
        __app_pattern(r'/model_edit/gacha_slide_cast', 'model_edit.gacha_slide_cast'),
        __app_pattern(r'/model_edit/gacha_header', 'model_edit.gacha_header'),
        __app_pattern(r'/model_edit/gacha_seat_table', 'model_edit.gacha_seat_table'),
        __app_pattern(r'/model_edit/gacha_seat', 'model_edit.gacha_seat'),
        __app_pattern(r'/model_edit/gacha_ranking', 'model_edit.gacha_ranking'),
        __app_pattern(r'/model_edit/gacha', 'model_edit.gacha'),
        __app_pattern(r'/model_edit/happening', 'model_edit.happening'),
        __app_pattern(r'/model_edit/raideventscoutstage', 'model_edit.raideventscoutstage'),
        __app_pattern(r'/model_edit/raideventmaterial', 'model_edit.raideventmaterial'),
        __app_pattern(r'/model_edit/raideventrecipe', 'model_edit.raideventrecipe'),
        __app_pattern(r'/model_edit/raideventraid', 'model_edit.raideventraid'),
        __app_pattern(r'/model_edit/raidevent', 'model_edit.raidevent'),
        __app_pattern(r'/model_edit/raid', 'model_edit.raid'),
        __app_pattern(r'/model_edit/reprintticket_tradeshop', 'model_edit.reprintticket_tradeshop'),
        __app_pattern(r'/model_edit/infomation', 'model_edit.infomation'),
        __app_pattern(r'/model_edit/item', 'model_edit.item'),
        __app_pattern(r'/model_edit/login_bonus', 'model_edit.login_bonus'),
        __app_pattern(r'/model_edit/loginbonustimelimiteddays', 'model_edit.loginbonustimelimiteddays'),
        __app_pattern(r'/model_edit/loginbonustimelimited', 'model_edit.loginbonustimelimited'),
        __app_pattern(r'/model_edit/sugorokumapsquares', 'model_edit.sugorokumapsquares'),
        __app_pattern(r'/model_edit/sugorokumap', 'model_edit.sugorokumap'),
        __app_pattern(r'/model_edit/sugoroku', 'model_edit.sugoroku'),
        __app_pattern(r'/model_edit/memories', 'model_edit.memories'),
        __app_pattern(r'/model_edit/player_level_exp', 'model_edit.player_level_exp'),
        __app_pattern(r'/model_edit/popup', 'model_edit.popup'),
        __app_pattern(r'/model_edit/present_everyone_record', 'model_edit.present_everyone_record'),
        __app_pattern(r'/model_edit/present_everyone_mypage', 'model_edit.present_everyone_mypage'),
        __app_pattern(r'/model_edit/present_everyone', 'model_edit.present_everyone'),
        __app_pattern(r'/model_edit/prize', 'model_edit.prize'),
        __app_pattern(r'/model_edit/schedule', 'model_edit.schedule'),
        __app_pattern(r'/model_edit/scouteventtanzakucast', 'model_edit.scouteventtanzakucast'),
        __app_pattern(r'/model_edit/scouteventhappeningtable', 'model_edit.scouteventhappeningtable'),
        __app_pattern(r'/model_edit/scouteventraid', 'model_edit.scouteventraid'),
        __app_pattern(r'/model_edit/scouteventpresentprize', 'model_edit.scouteventpresentprize'),
        __app_pattern(r'/model_edit/scouteventstage', 'model_edit.scouteventstage'),
        __app_pattern(r'/model_edit/scoutevent', 'model_edit.scoutevent'),
        __app_pattern(r'/model_edit/scout', 'model_edit.scout'),
        __app_pattern(r'/model_edit/shop_item', 'model_edit.shop_item'),
        __app_pattern(r'/model_edit/title', 'model_edit.title'),
        __app_pattern(r'/model_edit/treasure_gold_table', 'model_edit.treasure_gold_table'),
        __app_pattern(r'/model_edit/treasure_gold', 'model_edit.treasure_gold'),
        __app_pattern(r'/model_edit/treasure_silver_table', 'model_edit.treasure_silver_table'),
        __app_pattern(r'/model_edit/treasure_silver', 'model_edit.treasure_silver'),
        __app_pattern(r'/model_edit/treasure_bronze_table', 'model_edit.treasure_bronze_table'),
        __app_pattern(r'/model_edit/treasure_bronze', 'model_edit.treasure_bronze'),
        __app_pattern(r'/model_edit/trade_shop_item', 'model_edit.trade_shop_item'),
        __app_pattern(r'/model_edit/trade_shop', 'model_edit.trade_shop'),
        __app_pattern(r'/model_edit/trade', 'model_edit.trade'),
        __app_pattern(r'/model_edit/skill', 'model_edit.skill'),
        __app_pattern(r'/model_edit/text', 'model_edit.text'),
        __app_pattern(r'/model_edit/top_banner', 'model_edit.top_banner'),
        __app_pattern(r'/model_edit/battlerank', 'model_edit.battlerank'),
        __app_pattern(r'/model_edit/tutorialconfig', 'model_edit.tutorial_config'),
        __app_pattern(r'/model_edit/invite', 'model_edit.invite'),
        __app_pattern(r'/model_edit/battleeventpiece', 'model_edit.battleeventpiece'),
        __app_pattern(r'/model_edit/battleeventpresentcontent', 'model_edit.battleeventpresentcontent'),
        __app_pattern(r'/model_edit/battleeventpresent', 'model_edit.battleeventpresent'),
        __app_pattern(r'/model_edit/battleeventrank', 'model_edit.battleeventrank'),
        __app_pattern(r'/model_edit/battleevent', 'model_edit.battleevent'),
        __app_pattern(r'/model_edit/promotion_prize', 'model_edit.promotion_prize'),
        __app_pattern(r'/model_edit/promotion_requirement', 'model_edit.promotion_requirement'),
        __app_pattern(r'/model_edit/promotion_config', 'model_edit.promotion_config'),
        __app_pattern(r'/model_edit/serial_campaign', 'model_edit.serial_campaign'),
        __app_pattern(r'/model_edit/comebackcampaign', 'model_edit.comebackcampaign'),
        __app_pattern(r'/model_edit/eventmovie', 'model_edit.eventmovie'),
        __app_pattern(r'/model_edit/panelmissionpanel', 'model_edit.panelmissionpanel'),
        __app_pattern(r'/model_edit/panelmissionmission', 'model_edit.panelmissionmission'),
        __app_pattern(r'/model_edit/scenario', 'model_edit.scenario'),
        __app_pattern(r'/model_edit/levelup_bonus', 'model_edit.levelup_bonus'),
        __app_pattern(r'/model_edit/produce_event', 'model_edit.produce_event'),
        __app_pattern(r'/model_edit/produceeventscoutstage', 'model_edit.produceeventscoutstage'),
        __app_pattern(r'/model_edit/produceeventraid', 'model_edit.produceeventraid'),
        __app_pattern(r'/model_edit/produce_cast', 'model_edit.produce_cast'),
        
        __app_pattern(r'/manage_menu', 'manage_menu'),
        __app_pattern(r'/movie', 'movie'),
        __app_pattern(r'/voice', 'voice'),
        __app_pattern(r'/battle_simulator', 'battle_simulator'),
        __app_pattern(r'/battle_panel_simulator', 'battle_panel_simulator'),
        __app_pattern(r'/scout_silhouette_simulator', 'scout_silhouette_simulator'),
        __app_pattern(r'/raidevent_simulator', 'raidevent_simulator'),
        __app_pattern(r'/raidboss_drop_simulator', 'raidboss_drop_simulator'),
        __app_pattern(r'/ban_edit/', 'ban_edit'),
        __app_pattern(r'/view_images/', 'view_images'),
        __app_pattern(r'/ng_cast/', 'ng_cast'),
        
        __app_pattern(r'/infomations/view_player/', 'view_player'),
        __app_pattern(r'/infomations/view_userlog/', 'view_userlog'),
        __app_pattern(r'/infomations/view_paymentlog/', 'view_paymentlog'),
        __app_pattern(r'/infomations/view_dmmpayment/', 'view_dmmpayment'),
        __app_pattern(r'/infomations/view_itempaymentlog/', 'view_itempaymentlog'),
        __app_pattern(r'/infomations/view_raidlog/', 'view_raidlog'),
        __app_pattern(r'/infomations/view_raid/', 'view_raid'),
        __app_pattern(r'/infomations/view_battleevent_group/', 'view_battleevent_group'),
        __app_pattern(r'/infomations/view_battleevent_battlelog/', 'view_battleevent_battlelog'),
        __app_pattern(r'/infomations/view_movieview/', 'view_movieview'),
        __app_pattern(r'/infomations/view_pcmovieview/', 'view_pcmovieview'),
        __app_pattern(r'/infomations/view_promotion/', 'view_promotion'),
        __app_pattern(r'/infomations/view_gacha_payment_proceeds/', 'view_gacha_payment_proceeds'),
        __app_pattern(r'/infomations/view_serialcode/', 'view_serialcode'),
        __app_pattern(r'/infomations/view_eventranking/', 'view_eventranking'),
        __app_pattern(r'/infomations/view_panelmission/', 'view_panelmission'),
        __app_pattern(r'/infomations/view_rankinggacha_log/', 'view_rankinggacha_log'),
        
        __app_pattern(r'/kpi/playerlevel/', 'kpi.playerlevel'),
        __app_pattern(r'/kpi/card/', 'kpi.card'),
        __app_pattern(r'/kpi/item/', 'kpi.item'),
        __app_pattern(r'/kpi/tutorial/', 'kpi.tutorial'),
        __app_pattern(r'/kpi/scoutcomplete/', 'kpi.scoutcomplete'),
        __app_pattern(r'/kpi/battlecount/', 'kpi.battlecount'),
        __app_pattern(r'/kpi/rankup/', 'kpi.rankup'),
        __app_pattern(r'/kpi/raiddestroy/', 'kpi.raiddestroy'),
        __app_pattern(r'/kpi/raidmiss/', 'kpi.raidmiss'),
        __app_pattern(r'/kpi/raideventpoint/', 'kpi.raideventpoint'),
        __app_pattern(r'/kpi/raideventconsumepoint/', 'kpi.raideventconsumepoint'),
        __app_pattern(r'/kpi/raideventticket/', 'kpi.raideventticket'),
        __app_pattern(r'/kpi/raideventconsumeticket/', 'kpi.raideventconsumeticket'),
        __app_pattern(r'/kpi/raideventdestroy/', 'kpi.raideventdestroy'),
        __app_pattern(r'/kpi/raideventdestroybig/', 'kpi.raideventdestroybig'),
        __app_pattern(r'/kpi/raideventdestroylevel/', 'kpi.raideventdestroylevel'),
        __app_pattern(r'/kpi/raideventstage/', 'kpi.raideventstage'),
        __app_pattern(r'/kpi/scouteventstage/', 'kpi.scouteventstage'),
        __app_pattern(r'/kpi/scouteventpoint/', 'kpi.scouteventpoint'),
        __app_pattern(r'/kpi/scouteventgachapointconsume/', 'kpi.scouteventgachapointconsume'),
        __app_pattern(r'/kpi/scouteventtipconsume/', 'kpi.scouteventtipconsume'),
        __app_pattern(r'/kpi/scouteventtanzaku/', 'kpi.scouteventtanzaku'),
        __app_pattern(r'/kpi/battleeventjoindaily/', 'kpi.battleeventjoindaily'),
        __app_pattern(r'/kpi/battleeventjoin/', 'kpi.battleeventjoin'),
        __app_pattern(r'/kpi/battleeventresult/', 'kpi.battleeventresult'),
        __app_pattern(r'/kpi/battleeventfamepoint/', 'kpi.battleeventfamepoint'),
        __app_pattern(r'/kpi/battleeventbattlecount/', 'kpi.battleeventbattlecount'),
        __app_pattern(r'/kpi/battleeventpoint/', 'kpi.battleeventpoint'),
        __app_pattern(r'/kpi/battleeventpiececollect/', 'kpi.battleeventpiececollect'),
        __app_pattern(r'/kpi/produceeventstage/', 'kpi.produceeventstage'),
        __app_pattern(r'/kpi/produceeventeducation/', 'kpi.produceeventeducation'),
        __app_pattern(r'/kpi/invitecount/', 'kpi.invitecount'),
        __app_pattern(r'/kpi/movieview/', 'kpi.movieview'),
        __app_pattern(r'/kpi/pcmovieview/', 'kpi.pcmovieview'),
        __app_pattern(r'/kpi/paymententry/', 'kpi.paymententry'),
        __app_pattern(r'/kpi/platform_uu/', 'kpi.platform_uu'),
        __app_pattern(r'/kpi/gacha_fq5/', 'kpi.gacha_fq5'),
        __app_pattern(r'/kpi/gacha_userdata/', 'kpi.gacha_userdata'),
        __app_pattern(r'/kpi/eventreport_daily/', 'kpi.eventreport_daily'),
        __app_pattern(r'/kpi/eventreport_monthly/', 'kpi.eventreport_monthly'),
        __app_pattern(r'/kpi/eventreport_range/', 'kpi.eventreport_range'),
        __app_pattern(r'/kpi/paymentgacha_leaderdata/', 'kpi.paymentgacha_leaderdata'),

        # Simulator
        __app_pattern(r'/simulator/gacha_simulator/', 'gacha_simulator'),
        __app_pattern(r'/simulator/omake_simulator/', 'omake_simulator'),

        __app_pattern(r'/master_data', 'master_data'),
        
        __app_pattern(r'/debug_tool', 'debug_tool'),
        
        __app_pattern(r'/paymentlog_post/', 'paymentlog_post'),
        __app_pattern(r'/aggregate_paymententry/', 'aggregate_paymententry'),
        
        __app_pattern(r'/logout', 'logout'),
        __app_pattern(r'/login', 'login'),
        __app_pattern(r'/', 'index'),
    ])
    return urllist

def __get_url_patterns():
    urllist = [
        (r'^nagios/', 'platinumegg.app.%s.views.application.nagios.main' % settings_sub.APP_NAME),
        (r'^everyminutes', 'platinumegg.app.%s.views.application.everyminutes.main' % settings_sub.APP_NAME),
        (r'^check_dmmapi/', 'platinumegg.app.%s.views.mgr.check_dmmapi.main' % settings_sub.APP_NAME),
        (r'^check_battleeventgroup/', 'platinumegg.app.%s.views.mgr.check_battleeventgroup.main' % settings_sub.APP_NAME),
    ]
    if settings_sub.LAUNCH_MODE == 0:
        # 全て閲覧できる.
        urllist.extend(__get_app_patterns())
        urllist.extend(__get_mgr_patterns())
    elif settings_sub.LAUNCH_MODE == 1:
        # アプリ側のみ閲覧できる.
        urllist.extend(__get_app_patterns())
    elif settings_sub.LAUNCH_MODE == 2:
        # 管理ツール側のみ閲覧できる.
        urllist.extend(__get_mgr_patterns())
    
    if settings_sub.IS_LOCAL:
        urllist.append((r'^%s/(?P<path>.*)$' % Defines.MEDIA_DIR, 'django.views.static.serve', {'document_root': settings_sub.MEDIA_DOC_ROOT}))
        urllist.append((r'^%s/(?P<path>.*)$' % Defines.STATIC_DIR, 'django.views.static.serve', {'document_root': settings_sub.STATIC_DOC_ROOT, 'show_indexes': True}))
    
    return patterns('', *urllist)

urlpatterns = __get_url_patterns()
