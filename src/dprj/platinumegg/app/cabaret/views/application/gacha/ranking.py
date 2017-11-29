# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
from defines import Defines
from platinumegg.app.cabaret.util.url_maker import UrlMaker


class Handler(GachaHandler):
    """ランキングガチャランキングページ.
    """
    CONTENT_NUM_PER_PAGE = 10
    
    def process(self):
        args = self.getUrlArgs('/gacharanking/')
        try:
            mid = int(args.get(0))
            is_single = args.get(1) == '1'
            is_view_myrank = args.get(2) == '1'
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        
        # マスターデータを確認.
        gachamaster = BackendApi.get_gachamaster(model_mgr, mid, using=settings.DB_READONLY)
        gacharankingmaster = None
        if gachamaster and gachamaster.consumetype == Defines.GachaConsumeType.RANKING:
            gacharankingmaster = BackendApi.get_rankinggacha_master(model_mgr, gachamaster.boxid, using=settings.DB_READONLY)
        
        if gacharankingmaster is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return
        elif not gacharankingmaster.is_support_totalranking:
            is_single = True
        
        # ランキングガチャ情報.
        self.html_param['rankinggacha'] = Objects.rankinggacha(self, gacharankingmaster)
        
        # 開催中か.
        self.html_param['is_opened'] = BackendApi.check_schedule(model_mgr, gachamaster.schedule, using=settings.DB_READONLY)
        
        # ランキング.
        offset = 0
        if not is_view_myrank:
            page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
            offset = page * Handler.CONTENT_NUM_PER_PAGE
        obj_playerlist = self.makeRankingGachaRanking(gachamaster, is_view_myrank, Handler.CONTENT_NUM_PER_PAGE, offset, True, is_single)
        self.html_param['playerlist'] = obj_playerlist
        
        # 選択中の情報.
        self.html_param['is_view_myrank'] = is_view_myrank
        self.html_param['is_single'] = is_single
        
        # 切り替えリンク.
        self.html_param['url_ranking_single'] = self.makeAppLinkUrl(UrlMaker.gacharanking(mid, True, False))
        self.html_param['url_ranking_total'] = self.makeAppLinkUrl(UrlMaker.gacharanking(mid, False, False))
        self.html_param['url_ranking_all'] = self.makeAppLinkUrl(UrlMaker.gacharanking(mid, is_single, False))
        self.html_param['url_ranking_myrank'] = self.makeAppLinkUrl(UrlMaker.gacharanking(mid, is_single, True))
        self.html_param['url_prize'] = self.makeAppLinkUrl(UrlMaker.gacharankingprize(mid, is_single))
        
        # ページング.
        if not is_view_myrank:
            if is_single:
                contentnum = BackendApi.get_rankinggacha_single_rankernum(gachamaster.boxid)
            else:
                contentnum = BackendApi.get_rankinggacha_total_rankernum(gachamaster.boxid)
            urlbase = UrlMaker.gacharanking(mid, is_single, is_view_myrank)
            self.putPagenation(urlbase, page, contentnum, Handler.CONTENT_NUM_PER_PAGE)
        
        linklist = self.getRankingGachaLinkDataList(gachamaster, gacharankingmaster, lambda x:UrlMaker.gacharanking(x, is_single, is_view_myrank))
        self.html_param['same_rankingmaster_linklist'] = linklist
        
        self.writeAppHtml('gacha/ranking')
    

def main(request):
    return Handler.run(request)
