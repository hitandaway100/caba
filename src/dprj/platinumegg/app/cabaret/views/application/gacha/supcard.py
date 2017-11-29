# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines


class Handler(GachaHandler):
    """ステップアップガチャキャスト一覧.
    """
    
    def process(self):
        args = self.getUrlArgs('/gachasupcard/')
        try:
            mid = int(args.get(0))
            subbox = int(args.get(1))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        
        self.html_param['player'] = Objects.player(self, v_player)
        
        model_mgr = self.getModelMgr()
        
        # マスターデータ.
        gachamaster = BackendApi.get_gachamaster(model_mgr, mid, using=settings.DB_READONLY)
        if gachamaster is None:
            raise CabaretError(u'表示できない引抜です', CabaretError.Code.ILLEGAL_ARGS)
        self.html_param['gacha_name'] = gachamaster.name
        
        # カード情報.
        if subbox == 0:
            info = BackendApi.make_stepup_rateinfo(self, gachamaster, using=settings.DB_READONLY)
            self.html_param['gachacardlistinfo'] = info
        elif 0 < gachamaster.rarity_fixed_boxid and subbox == 1:
            subboxinfo = BackendApi.make_stepup_rateinfo(self, gachamaster, subbox=True, using=settings.DB_READONLY)
            self.html_param['gachacardlistinfo'] = subboxinfo
        
        # スライド情報.
        BackendApi.put_gachaslidecarddata(self, [gachamaster])
        
        # ガチャページに戻る.
        consumetype, tabengname = gachamaster.consumetype, gachamaster.tabengname
        url = UrlMaker.gacha()
        if consumetype in Defines.GachaConsumeType.PAYMENT_TYPES:
            url = OSAUtil.addQuery(url, Defines.URLQUERY_GTYPE, Defines.GachaConsumeType.GTYPE_NAMES[consumetype])
            if tabengname:
                url = OSAUtil.addQuery(url, Defines.URLQUERY_GTAB, tabengname)
        else:
            url = OSAUtil.addQuery(url, Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.TO_TOPIC[consumetype])
        
        self.html_param['url_back'] = self.makeAppLinkUrl(url)
        
        self.writeAppHtml('gacha/supcard')
    

def main(request):
    return Handler.run(request)
