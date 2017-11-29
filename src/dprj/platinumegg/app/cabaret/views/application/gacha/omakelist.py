# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
from defines import Defines
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(GachaHandler):
    """おまけ一覧.
    """
    
    def process(self):
        try:
            str_midlist = self.request.get(Defines.URLQUERY_ID).split(',')
            midlist = list(set([int(str_mid) for str_mid in str_midlist]))
            if not midlist:
                raise
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        
        # マスターデータ.
        gachamaster_list = BackendApi.get_gachamaster_list(model_mgr, midlist, using=settings.DB_READONLY)
        gachamaster_list.sort(key=lambda x:x.id)
        
        obj_omakeinfo_list = []
        backurlargs = None
        for gachamaster in gachamaster_list:
            prizeidlist_list = gachamaster.get_bonus_all()
            name_list = gachamaster.get_bonus_name()
            prizeinfo_list = []
            for idx, prizeidlist in enumerate(prizeidlist_list):
                name = name_list[idx]
                prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY)
                prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
                prizeinfo['name'] = name
                prizeinfo_list.append(prizeinfo)
            obj_omakeinfo_list.append(Objects.gachaomakeinfo(self, gachamaster, prizeinfo_list))
            backurlargs = backurlargs or (gachamaster.consumetype, gachamaster.tabengname)
        self.html_param['omakeinfo_list'] = obj_omakeinfo_list
        
        # ガチャページに戻る.
        consumetype, tabengname = backurlargs
        url = UrlMaker.gacha()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_GTYPE, Defines.GachaConsumeType.GTYPE_NAMES[consumetype])
        if tabengname:
            url = OSAUtil.addQuery(url, Defines.URLQUERY_GTAB, tabengname)
        self.html_param['url_back'] = self.makeAppLinkUrl(url)
        
        self.writeAppHtml('gacha/omakelist')
    

def main(request):
    return Handler.run(request)
