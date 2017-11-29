# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.promotion import PromotionUtil
from platinumegg.app.cabaret.models.Player import PlayerCrossPromotion
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines


class Handler(AppHandler):
    """クロスプロモーションTOPページ.
    """
    
    def process(self):
        args = self.getUrlArgs('/promotiontop/')
        appname = args.get(0)
        is_recipient = bool(int(self.request.get(Defines.URLQUERY_FLAG, '0')))
        self.html_param['is_recipient'] = is_recipient
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        if PlayerCrossPromotion.is_session():
            self.html_param['is_pc'] = self.is_pc
            if self.is_pc:
                # self.html_param['url_goh'] = 'http://rcv.ixd.dmm.com/api/surl?urid=NmcO0Hxz'
                # self.html_param['url_harepai'] = 'http://rcv.ixd.dmm.com/api/surl?urid=XzIUBerr'
                # self.html_param['url_sengoku'] = 'http://www.dmm.co.jp/netgame/feature/sengokuaibu.html'
                self.html_param['url_avst'] = 'http://www.dmm.co.jp/netgame/social/-/gadgets/=/app_id=445699/'
                self.html_param['url_noahs_gate'] = 'http://www.dmm.co.jp/netgame/social/-/gadgets/=/app_id=223705/'
            else:
                # self.html_param['url_goh'] = 'http://rcv.ixd.dmm.com/api/surl?urid=t6vJmS4X'
                # self.html_param['url_harepai'] = 'http://rcv.ixd.dmm.com/api/surl?urid=j9mnDsZP'
                # self.html_param['url_sengoku'] = 'http://www.dmm.co.jp/netgame/feature/sengokuaibu.html'
                self.html_param['url_avst'] = 'http://www.dmm.co.jp/netgame_s/avstrikers/'
                self.html_param['url_noahs_gate'] = 'http://sp.dmm.co.jp/netgame/gadgets/index/app_id/223705/'
            url_base = UrlMaker.promotion_top(appname)
            if is_recipient:
                self.html_param['url_cabaret'] = self.makeAppLinkUrl(url_base)
            else:
                self.html_param['url_recipient'] = self.makeAppLinkUrl(
                    OSAUtil.addQuery(url_base, Defines.URLQUERY_FLAG, '1'))

            # set display information for start time and end time of cross promotion
            start_date = '{d.month}/{d.day} {d.hour}:{d.minute:02}'.format(d=Defines.CROSS_PROMO_START_TIME)
            end_date = '{d.month}/{d.day} {d.hour}:{d.minute:02}'.format(d=Defines.CROSS_PROMO_END_TIME)
            self.html_param['cross_promo_time_limit'] = start_date + '〜' + end_date

            self.html_param['url_treasurelist'] = self.makeAppLinkUrl(UrlMaker.treasurelist())
            self.html_param['url_cabaclubtop'] = self.makeAppLinkUrl(UrlMaker.cabaclubtop())
            self.html_param['url_trade'] = self.makeAppLinkUrl(UrlMaker.trade())
            self.html_param['url_scout'] = self.makeAppLinkUrl(UrlMaker.scout())
            self.html_param['url_battle'] = self.makeAppLinkUrl(UrlMaker.battle())
            self.html_param['url_gacha'] = self.makeAppLinkUrl(
                OSAUtil.addQuery(
                    UrlMaker.gacha(),
                    Defines.URLQUERY_GTYPE,
                    Defines.GachaConsumeType.GTYPE_NAMES[Defines.GachaConsumeType.STEPUP2]
                )
            )

            player_cross_promotion = model_mgr.get_model(PlayerCrossPromotion, v_player.id)
            if player_cross_promotion:
                self.html_param['total_login_count'] = player_cross_promotion.total_login_count
            else:
                self.html_param['total_login_count'] = 0
            self.writeAppHtml('promotion/{0}/top'.format(appname))
            return
        else:
            # 開催期間外ならTopに飛ばす
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return


def main(request):
    return Handler.run(request)
