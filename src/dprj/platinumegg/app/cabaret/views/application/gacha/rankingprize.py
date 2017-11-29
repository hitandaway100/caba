# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
from defines import Defines
from platinumegg.app.cabaret.util.url_maker import UrlMaker


class Handler(GachaHandler):
    """ランキングガチャ報酬ページ.
    """
    CONTENT_NUM_PER_PAGE = 10
    
    def process(self):
        args = self.getUrlArgs('/gacharankingprize/')
        try:
            mid = int(args.get(0))
            is_single = args.get(1) == '1'
            is_whole = args.get(2) == '1'
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
        
        self.__putTabs(gachamaster, gacharankingmaster, is_whole)
        
        # ランキングガチャ情報.
        obj_rankinggacha = Objects.rankinggacha(self, gacharankingmaster)
        obj_rankinggacha.update({
            'url_wholeprize' : self.makeAppLinkUrl(UrlMaker.gacharankingprize(mid, is_single, True)),
            'url_rankprize' : self.makeAppLinkUrl(UrlMaker.gacharankingprize(mid, is_single, False)),
        })
        self.html_param['rankinggacha'] = obj_rankinggacha
        
        # 開催中か.
        self.html_param['is_opened'] = BackendApi.check_schedule(model_mgr, gachamaster.schedule, using=settings.DB_READONLY)
        
        # 選択中の情報.
        self.html_param['is_single'] = is_single
        
        # 切り替えリンク.
        self.html_param['url_ranking'] = self.makeAppLinkUrl(UrlMaker.gacharanking(mid, is_single, False))
        self.html_param['url_prize_total'] = self.makeAppLinkUrl(UrlMaker.gacharankingprize(mid, False))
        self.html_param['url_prize_single'] = self.makeAppLinkUrl(UrlMaker.gacharankingprize(mid, True))
        
        if is_whole:
            self.__procWholePointBonus(gacharankingmaster)
        else:
            self.__procRankBonus(gacharankingmaster, is_single)
    
    def __procRankBonus(self, gacharankingmaster, is_single):
        """ランキング報酬一覧.
        """
        # 報酬.
        if is_single:
            prizes = gacharankingmaster.singleprizes
        else:
            prizes = gacharankingmaster.totalprizes
        prizedatalist = self.make_rankingprizelist(prizes)
        self.html_param['rankingprizelist'] = prizedatalist
        
        self.writeAppHtml('gacha/rankbonus')
    
    def __procWholePointBonus(self, gacharankingmaster):
        """総計Pt報酬一覧.
        """
        model_mgr = self.getModelMgr()
        
        # 現在の総計Pt.
        boxid = gacharankingmaster.id
        cur_point = BackendApi.get_rankinggacha_wholepoint_dict(model_mgr, [boxid], using=settings.DB_READONLY).get(boxid, 0)
        
        # 報酬一覧.
        self.html_param['pointprizelist'] = self.make_pointprizelist(gacharankingmaster.wholeprizes, cur_point)
        
        self.writeAppHtml('gacha/pointbonus')
    
    def __putTabs(self, gachamaster, rankinggachamaster, is_whole):
        """タブ切り替え用のリンクを埋め込む.
        """
        linklist = self.getRankingGachaLinkDataList(gachamaster, rankinggachamaster, lambda x:UrlMaker.gacharankingprize(x, True, is_whole))
        self.html_param['same_rankingmaster_linklist'] = linklist
        
        self.html_param['url_wholeprize'] = self.makeAppLinkUrl(UrlMaker.gacharankingprize(gachamaster.id, True, True))

def main(request):
    return Handler.run(request)
