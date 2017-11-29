# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerDeck,\
    PlayerRequest
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
import settings
from platinumegg.app.cabaret.util.redistradeshop import RedisPlayerTradeShopPoint
from platinumegg.app.cabaret.models.Player import PlayerTradeShop
from platinumegg.app.cabaret.util.redisdb import RedisModel
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class Handler(GachaHandler):
    """引抜Topページ.
    表示するもの:
        プレイヤー情報.
        開催中のガチャ情報.
        ガチャ速報.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGachaPt, PlayerDeck, PlayerRequest]
    
    def process(self):
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        self.html_param['player'] = Objects.player(self, v_player)
        
        model_mgr = self.getModelMgr()
        
        # カード所持数.
        cardnum = BackendApi.get_cardnum(v_player.id, model_mgr, using=settings.DB_READONLY)
        self.html_param['cardnum'] = cardnum
        
        # 初期タブ指定
        topic = int(self.request.get(Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.PREMIUM))
        
        # 初期タブ指定(プレミアム用).
        current_tab = self.request.get(Defines.URLQUERY_GTAB) or None
        
        # 開催中のガチャ情報.
        self.putOpenGachaList(topic)

        # Gacha consumetype
        gacha_consumetype = None

        # 引き抜きガチャチケット消費数.
        self.html_param['gacha_ticket_cost'] = Defines.GACHA_TICKET_COST_NUM
        
        # 絞り込み用のURL.
        url_base = UrlMaker.gacha()
        self.html_param['url_gacha_premium_top'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.PREMIUM))
        self.html_param['url_gacha_usually'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.PAYMENT))
        self.html_param['url_gacha_ticket'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.TICKET))
        self.html_param['url_gacha_pt'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.FREE))
        self.html_param['url_gacha_scoutevent'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.SCOUTEVENT))
        self.html_param['url_tradeshop'] = self.makeAppLinkUrl(UrlMaker.tradeshop())
        defines_consumetype = Defines.GachaConsumeType
        gtypenames = defines_consumetype.GTYPE_NAMES
        htmltable = {
            defines_consumetype.GachaTopTopic.PREMIUM : (
                'gacha/gacha_usually',
                (
                    (gtypenames[defines_consumetype.DAILY_DISCOUNT], ('gacha/gacha_discount', defines_consumetype.DAILY_DISCOUNT)),
                    (gtypenames[defines_consumetype.FUKUBUKURO], ('gacha/gacha_fukubukuro', defines_consumetype.FUKUBUKURO)),
                    (gtypenames[defines_consumetype.OMAKE], ('gacha/gacha_omake', defines_consumetype.OMAKE)),
                    (gtypenames[defines_consumetype.OMAKE2], ('gacha/gacha_omake2', defines_consumetype.OMAKE2)),
                    (gtypenames[defines_consumetype.CHRISTMAS], ('gacha/gacha_christmas', defines_consumetype.CHRISTMAS)),
                    (gtypenames[defines_consumetype.RANKING], ('gacha/gacha_ranking', defines_consumetype.RANKING)),
                    (gtypenames[defines_consumetype.CONTINUITY_20], ('gacha/gacha_cnt20', defines_consumetype.CONTINUITY_20)),
                    (gtypenames[defines_consumetype.SEAT], ('gacha/gacha_seat', defines_consumetype.SEAT)),
                    (gtypenames[defines_consumetype.SEAT2], ('gacha/gacha_seat2', defines_consumetype.SEAT2)),
                    (gtypenames[defines_consumetype.MINI_SEAT], ('gacha/gacha_miniseat', defines_consumetype.MINI_SEAT)),
                    (gtypenames[defines_consumetype.MINI_BOX], ('gacha/gacha_minibox', defines_consumetype.MINI_BOX)),
                    (gtypenames[defines_consumetype.MINI_BOX2], ('gacha/gacha_minibox2', defines_consumetype.MINI_BOX2)),
                    (gtypenames[defines_consumetype.STEPUP], ('gacha/gacha_stepup', defines_consumetype.STEPUP)),
                    (gtypenames[defines_consumetype.STEPUP2], ('gacha/gacha_stepup2', defines_consumetype.STEPUP2)),
                    (gtypenames[defines_consumetype.ONE_TWO_THREE], ('gacha/gacha_onetwothree', defines_consumetype.ONE_TWO_THREE)),
                    (gtypenames[defines_consumetype.PREMIUM], ('gacha/gacha_payment', defines_consumetype.PREMIUM)),
                    (gtypenames[defines_consumetype.PAYMENT], ('gacha/gacha_usually', None)),
                    (gtypenames[defines_consumetype.SR_SSR_PROBABILITY_UP], ('gacha/gacha_probability', defines_consumetype.SR_SSR_PROBABILITY_UP)),
                    (gtypenames[defines_consumetype.FIXEDSR], ('gacha/gacha_fixedsr', defines_consumetype.FIXEDSR)),
                    (gtypenames[defines_consumetype.XMAS_OMAKE], ('gacha/gacha_xmasomake', defines_consumetype.XMAS_OMAKE)),
                    (gtypenames[defines_consumetype.LIMIT_SHEET], ('gacha/gacha_limitsheet', defines_consumetype.LIMIT_SHEET)),
                    (gtypenames[defines_consumetype.FUKUBUKURO2016], ('gacha/gacha_fukubukuro2016', defines_consumetype.FUKUBUKURO2016)),
                    (gtypenames[defines_consumetype.PTCHANGE], ('gacha/gacha_ptchange', defines_consumetype.PTCHANGE)),
                    (gtypenames[defines_consumetype.NEWSTORE_SUPPORT_PREMIUM], ('gacha/gacha_newstore_support_premium', defines_consumetype.NEWSTORE_SUPPORT_PREMIUM)),
                    (gtypenames[defines_consumetype.LIMITED_RESET_BOX], ('gacha/gacha_limitedreset_boxgacha', defines_consumetype.LIMITED_RESET_BOX)),
                    (gtypenames[defines_consumetype.FUKUBUKURO2017], ('gacha/gacha_fukubukuro2017', defines_consumetype.FUKUBUKURO2017)),
                )
            ),
            defines_consumetype.GachaTopTopic.TICKET : 'gacha/gacha_ticket',
            defines_consumetype.GachaTopTopic.FREE : 'gacha/gacha_free',
            defines_consumetype.GachaTopTopic.PAYMENT : 'gacha/gacha_usually',
            defines_consumetype.GachaTopTopic.SCOUTEVENT : 'gacha/gacha_scev',
        }
        default_htmlname = 'gacha/gacha_payment'
        
        data = htmltable.get(topic, default_htmlname)

        if isinstance(data, tuple):
            def gtypedata_htmlname_get(gtypedata, default=None):
                if isinstance(gtypedata, tuple):
                    gacha_type_counts = self.html_param.get('gacha_type_counts') or {}
                    if gacha_type_counts.get(gtypedata[1]):
                        return gtypedata[0]
                    return default
                else:
                    return gtypedata
            
            default_htmlname, gtypes = data
            gtypes_dict = dict(gtypes)
            gtype = self.request.get(Defines.URLQUERY_GTYPE) or ''
            gtypedata = gtypes_dict.get(gtype)

            tabname_to_consumetype = self.html_param['tabname_to_consumetype']
            
            if gtypedata is None:
                htmlname = None
                for tab in self.html_param.get('gacha_premium_priority') or []:
                    k = tabname_to_consumetype.get(tab, tab)
                    v = gtypes_dict.get(gtypenames[k])
                    htmlname = gtypedata_htmlname_get(v, None)
                    if htmlname is not None:
                        gtype = k
                        gtypedata = v
                        current_tab = tab if tab != k else None
                        break
                if htmlname is None:
                    htmlname = default_htmlname
            else:
                htmlname = gtypedata_htmlname_get(gtypedata, default_htmlname)

            if gtypedata is not None and gtypedata[1] is not None and (defines_consumetype.SR_SSR_PROBABILITY_UP == gtypedata[1] or defines_consumetype.PTCHANGE == gtypedata[1]):
                userpoint = BackendApi.get_tradeshop_userpoint(model_mgr, v_player.id)
                if userpoint is None:
                    userdata = PlayerTradeShop.createInstance(v_player.id)
                    userpoint = userdata.point
                    model_mgr = db_util.run_in_transaction(self.tr_write, v_player.id, userdata)
                    model_mgr.write_end()
                self.html_param['user_point'] = userpoint
            _, gacha_consumetype = gtypedata
        else:
            htmlname = data

        for gachavalues in self.html_param["gachadata"].values():
            if gachavalues['consumetype'] == gacha_consumetype:
                self.html_param['explain_text'] = gachavalues['explain_text']

        self.html_param['current_tab'] = current_tab or ''
        self.writeAppHtml(htmlname)

    def tr_write(self, uid, userdata):
        model_mgr = ModelRequestMgr()
        model_mgr.set_save(userdata)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
